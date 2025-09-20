import logging
import os
import asyncio
import json
from typing import Any, Dict, Optional

import httpx
import bilibili_api
from bilibili_api import Credential, user, search, video, aid2bvid
from bilibili_api.exceptions import ApiException
from async_lru import alru_cache

from .config import (
    DEFAULT_HEADERS, REQUEST_DELAY, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX,
    REQUEST_TIMEOUT, CONNECT_TIMEOUT, READ_TIMEOUT
)

# 配置 bilibili-api 请求设置
bilibili_api.request_settings.set('headers', DEFAULT_HEADERS)
bilibili_api.request_settings.set('timeout', REQUEST_TIMEOUT)

logger = logging.getLogger(__name__)

def get_credential(sessdata: str, bili_jct: str, buvid3: str) -> Optional[Credential]:
    """创建Bilibili API的凭证对象"""
    if not sessdata:
        logger.error("SESSDATA environment variable is not set or empty.")
        return None
    return Credential(sessdata=sessdata, bili_jct=bili_jct, buvid3=buvid3)

def _get_cookies(cred: Credential) -> str:
    """获取用于请求的 Cookie 字符串。"""
    cookie_parts = []
    if getattr(cred, "sessdata", None):
        cookie_parts.append(f"SESSDATA={cred.sessdata}")
    if getattr(cred, "bili_jct", None):
        cookie_parts.append(f"bili_jct={cred.bili_jct}")
    if getattr(cred, "buvid3", None):
        cookie_parts.append(f"buvid3={cred.buvid3}")
    return "; ".join(cookie_parts)

async def _get_video_subtitle_info(bvid: str, cred: Credential) -> Dict[str, Any]:
    """获取视频的详细字幕信息（优化版）"""
    try:
        if not bvid:
            return {"has_subtitle": False, "subtitle_count": 0, "subtitle_list": []}
            
        v = video.Video(bvid=bvid, credential=cred)
        
        subtitle_info = {
            "has_subtitle": False,
            "subtitle_count": 0,
            "subtitle_list": [],
            "subtitle_summary": "无字幕"  # 新增：字幕概要信息
        }
        
        # 方法1：先尝试从视频基本信息获取
        video_info = await v.get_info()
        subtitles_from_info = video_info.get("subtitle", {}).get("list", [])
        
        # 方法2：如果方法1无数据，尝试使用get_subtitle方法
        subtitles_data = None
        if not subtitles_from_info:
            try:
                # 获取页面信息和cid
                pages = await v.get_pages()
                if pages:
                    cid = pages[0].get('cid')
                    if cid:
                        # 使用get_subtitle方法
                        subtitle_response = await v.get_subtitle(cid=cid)
                        subtitles_data = subtitle_response.get("subtitles", [])
                        logger.debug(f"Using get_subtitle method for video {bvid}, found {len(subtitles_data)} subtitles")
            except Exception as e:
                logger.debug(f"get_subtitle method failed for video {bvid}: {e}")
        else:
            subtitles_data = subtitles_from_info
            logger.debug(f"Using video info method for video {bvid}, found {len(subtitles_data)} subtitles")
        
        # 处理字幕数据
        if subtitles_data:
            subtitle_info["has_subtitle"] = True
            subtitle_info["subtitle_count"] = len(subtitles_data)
            
            logger.debug(f"Found {len(subtitles_data)} subtitle tracks for video {bvid}")
            
            # 收集语言信息用于概要
            languages = []
            
            for sub in subtitles_data:
                # 处理AI字幕的特殊情况
                is_ai_generated = False
                lan_code = sub.get("lan", "")
                if lan_code.startswith("ai-") or sub.get("ai_type", 0) > 0 or sub.get("ai_status", 0) > 0:
                    is_ai_generated = True
                
                subtitle_item = {
                    "id": sub.get("id"),
                    "lan": lan_code,
                    "lan_doc": sub.get("lan_doc"),
                    "is_lock": sub.get("is_lock", False),
                    "author_mid": sub.get("author", {}).get("mid") if sub.get("author") else None,
                    "author_name": sub.get("author", {}).get("name") if sub.get("author") else None,
                    "subtitle_url": sub.get("subtitle_url"),
                    "is_ai_generated": is_ai_generated,
                    "ai_type": sub.get("ai_type", 0),
                    "ai_status": sub.get("ai_status", 0)
                }
                subtitle_info["subtitle_list"].append(subtitle_item)
                
                # 收集语言信息
                lang_desc = sub.get("lan_doc", sub.get("lan", "未知"))
                if is_ai_generated:
                    lang_desc += "(AI生成)"
                languages.append(lang_desc)
            
            # 生成简洁的字幕概要
            if languages:
                subtitle_info["subtitle_summary"] = f"有{len(languages)}种字幕: " + ", ".join(languages)
            
            logger.debug(f"Video {bvid} subtitle summary: {subtitle_info['subtitle_summary']}")
        else:
            logger.debug(f"No subtitles found for video {bvid}")
        
        return subtitle_info
        
    except Exception as e:
        logger.warning(f"Failed to get subtitle info for video {bvid}: {e}")
        return {
            "has_subtitle": False, 
            "subtitle_count": 0, 
            "subtitle_list": [], 
            "subtitle_summary": "获取失败",
            "error": str(e)
        }

def _parse_dynamic_item(item: dict) -> dict:
    """将单个动态的原始字典数据解析为干净的目标格式。"""
    try:
        desc = item.get('desc', {})
        card = item.get('card', {}) # It's a dict now, not a string.

        # Base structure from 'desc'
        parsed = {
            "dynamic_id": desc.get('dynamic_id_str'),
            "type_id": desc.get('type'),
            "author_mid": desc.get('uid'),
            "timestamp": desc.get('timestamp'),
            "stats": {
                "like": desc.get('like'),
                "comment": desc.get('comment'),
                "forward": desc.get('repost'),
            }
        }

        # --- Content Extraction ---
        dynamic_type = desc.get('type')
        
        # Type 1: Repost
        if dynamic_type == 1:
            parsed['type'] = 'REPOST'
            parsed['text_content'] = card.get('item', {}).get('content')
            if 'origin' in card:
                try:
                    # Origin is a JSON string inside the card dict
                    origin_card = json.loads(card['origin'])
                    origin_item = origin_card.get('item', {})
                    parsed['origin_user'] = origin_card.get('user', {}).get('uname')
                    parsed['origin_content'] = origin_item.get('content') or origin_item.get('description')
                except Exception:
                    parsed['origin_content'] = "(转发内容解析失败)"

        # Type 2: Image-text
        elif dynamic_type == 2:
            parsed['type'] = 'IMAGE_TEXT'
            item_data = card.get('item', {})
            parsed['text_content'] = item_data.get('description')
            # 修复: 当 pictures 为 None 时提供默认空列表
            pictures = item_data.get('pictures') or []
            parsed['images'] = [p.get('img_src') for p in pictures if isinstance(p, dict)]

        # Type 4: Text-only
        elif dynamic_type == 4:
            parsed['type'] = 'TEXT'
            parsed['text_content'] = card.get('item', {}).get('content')

        # Type 8: Video
        elif dynamic_type == 8:
            parsed['type'] = 'VIDEO'
            parsed['text_content'] = card.get('dynamic')
            
            # 修复视频bvid字段 - 如果为空则从aid转换生成
            video_bvid = card.get('bvid')
            video_aid = card.get('aid')
            
            if not video_bvid and video_aid:
                try:
                    video_bvid = aid2bvid(video_aid)
                    logger.debug(f"Generated bvid {video_bvid} from aid {video_aid} in dynamic")
                except Exception as e:
                    logger.warning(f"Failed to convert aid {video_aid} to bvid in dynamic: {e}")
                    video_bvid = None
            
            parsed['video'] = {
                "title": card.get('title'),
                "bvid": video_bvid,
                "aid": video_aid,
                "desc": card.get('desc'),
                "pic": card.get('pic')
            }

        # Type 64: Article
        elif dynamic_type == 64:
            parsed['type'] = 'ARTICLE'
            parsed['text_content'] = card.get('summary')
            parsed['article'] = {
                "id": card.get('id'),
                "title": card.get('title'),
                "covers": card.get('image_urls', [])
            }
        
        # Type 2048: Charge/QA post (增强解析)
        elif dynamic_type == 2048:
            parsed['type'] = 'CHARGE_QA'
            vest_content = card.get('vest', {}).get('content', '')
            sketch_title = card.get('sketch', {}).get('title', '')
            parsed['text_content'] = f"{vest_content} {sketch_title}".strip()
            parsed['charge_info'] = {
                "vest": card.get('vest', {}),
                "sketch": card.get('sketch', {})
            }
        
        # Type 512: Activity/番剧
        elif dynamic_type == 512:
            parsed['type'] = 'ACTIVITY'
            parsed['text_content'] = card.get('title', '') or card.get('description', '')
            parsed['activity_info'] = {
                "title": card.get('title'),
                "description": card.get('description'),
                "cover": card.get('cover')
            }
        
        else:
            parsed['type'] = f"UNKNOWN_{dynamic_type}"
            parsed['text_content'] = f'(未支持的动态类型 {dynamic_type})'
            # 保留原始数据用于调试和后续支持
            parsed['raw_card_keys'] = list(card.keys()) if card else []
            parsed['debug_info'] = {
                "type_id": dynamic_type,
                "card_sample": {k: str(v)[:100] for k, v in (card or {}).items()}
            }

        return parsed
    except Exception as e:
        dynamic_id = item.get('desc', {}).get('dynamic_id_str', 'unknown')
        dynamic_type = item.get('desc', {}).get('type', 'unknown')
        logger.error(f"Failed to parse dynamic item {dynamic_id} (type {dynamic_type}): {e}")
        
        # 增强的调试信息
        debug_info = {
            "error": f"Failed to parse dynamic: {str(e)}", 
            "id": dynamic_id,
            "type_id": dynamic_type,
            "error_location": f"Type {dynamic_type} parsing",
            "card_keys": list(item.get('card', {}).keys()) if item.get('card') else [],
            "desc_keys": list(item.get('desc', {}).keys()) if item.get('desc') else [],
            "raw_data_sample": str(item)[:300] + "..." if len(str(item)) > 300 else str(item)
        }
        
        return debug_info

@alru_cache(maxsize=128, ttl=3600)
async def get_user_id_by_username(username: str) -> Optional[int]:
    """通过用户名搜索并获取用户ID"""
    if not username:
        return None
    try:
        search_result = await search.search_by_type(
            keyword=username,
            search_type=search.SearchObjectType.USER
        )
        result_list = search_result.get("result") or (search_result.get("data", {}) or {}).get("result")
        if not isinstance(result_list, list) or not result_list:
            logger.warning(f"User '{username}' not found in search results.")
            return None
        return result_list[0]['mid']
    except ApiException as e:
        error_code = getattr(e, 'code', None)
        if error_code == -412:
            logger.error(f"Search request blocked for '{username}': rate limit exceeded")
        elif error_code == -509:
            logger.error(f"Search request rate limited for '{username}': too frequent requests")
        else:
            logger.error(f"Bilibili API error while searching for user '{username}': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while searching for user '{username}': {e}")
        return None

@alru_cache(maxsize=32, ttl=300)
async def fetch_user_info(user_id: int, cred: Credential) -> Dict[str, Any]:
    """获取B站用户的详细资料。返回JSON对象，为保证数据完整，默认返回所有字段。"""
    try:
        u = user.User(uid=user_id, credential=cred)
        info = await u.get_user_info()
        if not info or 'mid' not in info:
            raise ValueError("User info response is invalid")

        user_data = {
            "mid": info.get("mid"),
            "name": info.get("name"),
            "face": info.get("face"),
            "sign": info.get("sign"),
            "level": info.get("level"),
            "birthday": info.get("birthday"),
            "sex": info.get("sex"),
            "top_photo": info.get("top_photo"),
            "live_room": info.get("live_room"),
            "following": None,
            "follower": None
        }

        try:
            stat_url = "https://api.bilibili.com/x/relation/stat"
            params = {'vmid': user_id}
            headers = DEFAULT_HEADERS.copy()
            headers['Cookie'] = _get_cookies(cred)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(stat_url, params=params, headers=headers, timeout=httpx.Timeout(CONNECT_TIMEOUT, read=READ_TIMEOUT))
                response.raise_for_status()
                stat_data = response.json()

            if stat_data.get('code') == 0 and 'data' in stat_data:
                user_data['following'] = stat_data['data'].get('following')
                user_data['follower'] = stat_data['data'].get('follower')
            else:
                logger.warning(f"Failed to get relation stat for UID {user_id}: {stat_data.get('message')}")
        except httpx.RequestError as e:
            logger.warning(f"HTTP request for relation stat failed for UID {user_id}: {e}")
        
        return user_data

    except ApiException as e:
        error_code = getattr(e, 'code', None)
        if error_code == -404:
            return {"error": f"用户 {user_id} 不存在或已注销"}
        elif error_code == -412:
            return {"error": "请求被拦截，可能是访问频率过高，请稍后重试"}
        elif error_code == -509:
            return {"error": "请求过于频繁，被系统限流，请逐渐减少请求频率"}
        logger.error(f"Bilibili API error for UID {user_id}: {e}")
        return {"error": f"Bilibili API 错误（码: {error_code}）: {str(e)}"}
    except httpx.RequestError as e:
        logger.error(f"Network error for UID {user_id}: {e}")
        return {"error": f"网络错误: {str(e)}，请检查网络连接或稍后重试"}
    except Exception as e:
        logger.error(f"Failed to get user info for UID {user_id}: {e}")
        return {"error": f"获取用户信息时发生未知错误: {str(e)}"}

async def fetch_user_videos(user_id: int, page: int, limit: int, cred: Credential) -> Dict[str, Any]:
    """获取用户的视频列表。现在包含增强的字幕信息，包括字幕语言、作者和下载URL等详细信息。"""
    try:
        u = user.User(uid=user_id, credential=cred)
        video_list = await u.get_videos(pn=page, ps=limit)
        raw_videos = video_list.get("list", {}).get("vlist", [])
        processed_videos = []
        
        for v_data in raw_videos:
            # 修复 bvid 字段 - 如果为空则从 aid 转换生成
            bvid = v_data.get("bvid")
            aid = v_data.get("aid")
            
            if not bvid and aid:
                try:
                    bvid = aid2bvid(aid)
                    logger.debug(f"Generated bvid {bvid} from aid {aid}")
                except Exception as e:
                    logger.warning(f"Failed to convert aid {aid} to bvid: {e}")
                    bvid = None
            
            # 获取详细的字幕信息（只有当 bvid 存在时才获取）
            if bvid:
                subtitle_info = await _get_video_subtitle_info(bvid, cred)
            else:
                subtitle_info = {"has_subtitle": False, "subtitle_count": 0, "subtitle_list": [], "error": "No bvid available"}
            
            processed_video = {
                "mid": v_data.get("mid"),
                "bvid": bvid,
                "aid": aid,
                "title": v_data.get("title"),
                "description": v_data.get("description"),
                "created": v_data.get("created"),
                "length": v_data.get("length"),
                "play": v_data.get("play"),
                "comment": v_data.get("comment"),
                "favorites": v_data.get("favorites"),
                "like": v_data.get("like"),
                "pic": v_data.get("pic"),
                "subtitle": subtitle_info,  # 增强的字幕信息
                "url": f"https://www.bilibili.com/video/{bvid}" if bvid else f"https://www.bilibili.com/video/av{aid}"
            }
            processed_videos.append(processed_video)

        return {"videos": processed_videos, "total": video_list.get("page", {}).get("count", 0)}
    except ApiException as e:
        logger.error(f"Bilibili API error for videos of UID {user_id}: {e}")
        return {"error": f"Bilibili API 错误: {str(e)}"}
    except Exception as e:
        logger.error(f"Failed to get user videos for UID {user_id}: {e}")
        return {"error": f"获取用户视频时发生未知错误: {str(e)}"}

async def fetch_user_dynamics(user_id: int, offset: int, limit: int, cred: Credential, dynamic_type: str = "ALL") -> Dict[str, Any]:
    """获取用户的动态列表。为保证数据可用性，返回JSON列表。会尝试解析不同类型的动态。"""
    try:
        # 导入DynamicType配置
        from .config import DynamicType
        
        u = user.User(uid=user_id, credential=cred)
        raw_dynamics_data = await u.get_dynamics(offset=offset)
        
        processed_dynamics = []
        if raw_dynamics_data and raw_dynamics_data.get("cards"):
            for card in raw_dynamics_data["cards"]:
                if len(processed_dynamics) >= limit:
                    break
                    
                parsed_item = _parse_dynamic_item(card)
                
                # 实现动态类型筛选
                if dynamic_type != "ALL":
                    # 检查动态类型是否匹配
                    item_type_id = card.get('desc', {}).get('type')
                    
                    # 根据类型映射进行筛选
                    if dynamic_type == "VIDEO" and item_type_id != 8:
                        continue
                    elif dynamic_type == "ARTICLE" and item_type_id != 64:
                        continue
                    elif dynamic_type == "ANIME" and item_type_id != 512:
                        continue
                    elif dynamic_type == "DRAW" and item_type_id != 2:
                        continue
                        
                processed_dynamics.append(parsed_item)

        return {"dynamics": processed_dynamics, "total_fetched": len(processed_dynamics), "filter_type": dynamic_type}
    except ApiException as e:
        logger.error(f"Bilibili API error for dynamics of UID {user_id}: {e}")
        return {"error": f"Bilibili API 错误: {str(e)}"}
    except Exception as e:
        logger.error(f"An unexpected error in fetch_user_dynamics for UID {user_id}: {e}")
        return {"error": f"处理动态数据时发生未知错误: {str(e)}"}

async def fetch_user_articles(user_id: int, page: int, limit: int, cred: Credential) -> Dict[str, Any]:
    """获取用户的专栏文章列表。为保证数据完整，默认返回所有字段。"""
    try:
        u = user.User(uid=user_id, credential=cred)
        articles_data = await u.get_articles(pn=page, ps=limit)
        
        raw_articles = articles_data.get("articles", [])
        processed_articles = []
        for article_data in raw_articles:
            if len(processed_articles) >= limit:
                break

            processed_article = {
                "mid": article_data.get("author", {}).get("mid"),
                "id": article_data.get("id"),
                "title": article_data.get("title"),
                "summary": article_data.get("summary"),
                "banner_url": article_data.get("banner_url"),
                "publish_time": article_data.get("publish_time"),
                "stats": article_data.get("stats"),
                "words": article_data.get("words"),
                "url": f"https://www.bilibili.com/read/cv{article_data.get('id')}"
            }
            processed_articles.append(processed_article)
            
        return {"articles": processed_articles}
    except ApiException as e:
        logger.error(f"Bilibili API error for articles of UID {user_id}: {e}")
        return {"error": f"Bilibili API 错误: {str(e)}"}
    except Exception as e:
        logger.error(f"Failed to get user articles for UID {user_id}: {e}")
        return {"error": f"获取用户专栏文章时发生未知错误: {str(e)}"}


async def fetch_user_followings(user_id: int, page: int, limit: int, cred: Credential) -> Dict[str, Any]:
    """获取用户的关注列表。"""
    try:
        api_url = "https://api.bilibili.com/x/relation/followings"
        params = {'vmid': user_id, 'ps': limit, 'pn': page}
        headers = DEFAULT_HEADERS.copy()
        headers['Cookie'] = _get_cookies(cred)
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params, headers=headers, timeout=httpx.Timeout(CONNECT_TIMEOUT, read=READ_TIMEOUT))
            response.raise_for_status()
            followings_data = response.json()
            
            # 增强错误码处理
            if followings_data.get('code') == -412:
                return {"error": "请求被拦截，可能是访问频率过高，请稍后重试"}
            elif followings_data.get('code') == -509:
                return {"error": "请求过于频繁，被系统限流，请逐渐减少请求频率"}
            elif followings_data.get('code') == 2207:
                return {"error": "用户关注列表已设置为隐私，无法查看"}
            elif followings_data.get('code') == -404:
                return {"error": f"用户 {user_id} 不存在或已注销"}
            elif followings_data.get('code') != 0:
                error_msg = followings_data.get('message', 'Failed to fetch followings from raw API.')
                return {"error": f"API返回错误（码: {followings_data.get('code')}）: {error_msg}"}
            followings_data = followings_data.get('data', {})

        raw_followings = followings_data.get("list", [])
        processed_followings = []
        for f_data in raw_followings:
            processed_following = {
                "mid": f_data.get("mid"),
                "uname": f_data.get("uname"),
                "face": f_data.get("face"),
                "sign": f_data.get("sign"),
                "official_verify": f_data.get("official_verify", {}).get("desc"),
                "vip_type": f_data.get("vip", {}).get("vipType")
            }
            processed_followings.append(processed_following)

        return {"followings": processed_followings, "total": followings_data.get("total", 0)}

    except ApiException as e:
        logger.error(f"Bilibili API error for followings of UID {user_id}: {e}")
        return {"error": f"Bilibili API 错误: {str(e)}"}
    except httpx.RequestError as e:
        logger.error(f"Network error for followings of UID {user_id}: {e}")
        return {"error": f"网络错误: {str(e)}"}
    except Exception as e:
        logger.error(f"Failed to get user followings for UID {user_id}: {e}")
        return {"error": f"获取用户关注列表时发生未知错误: {str(e)}"}