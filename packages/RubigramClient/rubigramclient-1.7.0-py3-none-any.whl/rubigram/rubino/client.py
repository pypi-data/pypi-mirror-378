from typing import Literal, Optional, Union, Any
from aiohttp import ClientSession, FormData
from urllib.parse import urlparse
from random import randint
from pathlib import Path
from json import loads
import os


class Http:
    def __init__(self, auth: str):
        self.auth = auth
        self.session: Optional[ClientSession] = None
        self.api = f"https://rubino{randint(1, 30)}.iranlms.ir"
        self.client = {
            "app_name": "Main",
            "app_version": "3.0.2",
            "lang_code": "fa",
            "package": "app.rbmain.a",
            "platform": "Android"
        }

    async def connect(self):
        if self.session is None:
            self.session = ClientSession()

    async def disconnect(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def request(self, method: str, data: dict[str, Any]):
        await self.connect()
        json = {
            "api_version": "0",
            "auth": self.auth,
            "client": self.client,
            "data": data,
            "method": method
        }
        async with self.session.post(self.api, json=json) as response:
            response.raise_for_status()
            return await response.json()

    async def getBytes(self, url: str) -> bytes:
        await self.connect()
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.read()

    async def getName(self, url: str) -> str:
        parser = urlparse(url)
        return os.path.basename(parser.path)

    async def request_upload_file(
        self,
        file_name: str,
        file_size: str,
        file_type: str,
        profile_id: str,
    ):
        data = {
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_type,
            "profile_id": profile_id,
        }
        return await self.request("requestUploadFile", data)

    async def requestUpload(
        self,
        file: str,
        file_type: str,
        file_name: Optional[str] = None,
        profile_id: Optional[str] = None,
    ):
        path = Path(file)
        if path.is_file():
            data = path.read_bytes()
            file_name = file_name if file_name else path.name
            file_size = path.stat().st_size

        elif file.startswith("http"):
            data = await self.getBytes(file)
            file_name = file_name if file_name else await self.getName(file)
            file_size = len(data)

        else:
            raise Exception(f"Can't find this file : {file}")

        request = await self.request_upload_file(file_name, file_size, file_type, profile_id)
        request: dict[str, str] = request["data"]

        file_id: str = request["file_id"]
        hash_file_request: str = request["hash_file_request"]
        server_url: str = request["server_url"]

        headers = {
            "auth": self.auth,
            "chunk-size": str(file_size),
            "file-id": file_id,
            "hash-file-request": hash_file_request,
            "content-length": str(file_size),
            "part-number": "1",
            "total-part": "1"
        }
        form = FormData()
        form.add_field(
            "file", data, filename=file_name, content_type="application/octet-stream"
        )
        async with self.session.post(server_url, data=form, headers=headers) as response:
            text = await response.text()
            hash_file_receive = loads(text)["data"]["hash_file_receive"]
            return {"file_id": file_id, "hash_file_receive": hash_file_receive}


class Rubino(Http):
    def __init__(self, auth: str):
        super().__init__(auth)
    
    def rnd(self):
        return randint(100000, 999999999)

    async def app_post(
        self,
        file: str,
        caption: Optional[str] = None,
        post_type: Literal["Picture", "Video"] = "Picture",
        profile_id: Optional[str] = None,
        file_name: Optional[str] = None,
        is_multi_file: Optional[str] = None,
    ):
        request = await self.requestUpload(file, post_type, file_name, profile_id)
        file_id, hash_file_receive = request["file_id"], request["hash_file_receive"]
        data = {
            "caption": caption,
            "file_id": file_id,
            "hash_file_receive": hash_file_receive,
            "height": 800,
            "width": 800,
            "is_multi_file": is_multi_file,
            "post_type": post_type,
            "rnd": self.rnd(),
            "thumbnail_file_id": file_id,
            "thumbnail_hash_file_receive": hash_file_receive,
            "profile_id": profile_id
        }
        return await self.request("addPost", data)

    async def get_post_by_share_link(self, post_link: str):
        return await self.request("getPostByShareLink", {"share_string": post_link.split("/")[-1]})

    async def add_post_view_count(self, post_id: str, post_profile_id: str):
        data = {"post_id": post_id, "post_profile_id": post_profile_id}
        return await self.request("addPostViewCount", data)

    async def add_view_story(self, story_profile_id: str, story_ids: Union[str, list[str]], profile_id: Optional[str] = None):
        story_ids = story_ids if isinstance(story_ids, list) else [story_ids]
        data = {
            "story_profile_id": story_profile_id,
            "story_ids": story_ids,
            "profile_id": profile_id
        }
        return await self.request("addViewStory", data)

    async def is_exist_username(self, username: str):
        return await self.request("isExistUsername", {"username": username.replace("@", "")})

    async def create_page(self, username: str, name: str, bio: Optional[str] = None):
        return await self.request("createPage", {"username": username, "name": name, "bio": bio})

    async def add_comment(self, content: str, post_id: str, post_profile_id: str, profile_id: Optional[str] = None):
        data = {
            "content": content,
            "post_id": post_id,
            "post_profile_id": post_profile_id,
            "profile_id": profile_id,
            "rnd": self.rnd()
        }
        return await self.request("addComment", data)

    async def request_follow(self, followee_id: str, f_type: Literal["Follow", "Unfollow"] = "Follow", profile_id: Optional[str] = None):
        data = {
            "f_type": f_type,
            "followee_id": followee_id,
            "profile_id": profile_id
        }
        return self.request("requestFollow", data)
    
    async def follow(self, followee_id: str, profile_id: Optional[str] = None):
        return await self.request_follow(followee_id, "Follow", profile_id)

    async def unfollow(self, followee_id: str, profile_id: Optional[str] = None):
        return await self.request_follow(followee_id, "Unfollow", profile_id)

    async def set_block_profile(self, block_id: str, action: Literal["Block", "Unblock"] = "Block", profile_id: Optional[str] = None):
        data = {
            "block_id": block_id,
            "action": action,
            "profile_id": profile_id
        }
        return self.request("setBlockProfile", data)

    async def block_profile(self, block_id: str, profile_id: Optional[str] = None):
        return await self.set_block_profile(block_id, "Block", profile_id)
    
    async def unblock_profile(self, block_id: str, profile_id: Optional[str] = None):
        return await self.set_block_profile(block_id, "Unblock", profile_id)

    async def get_comments(self, post_id: str, post_profile_id: str, limit: Optional[int] = 100, profile_id: Optional[str] = None):
        data = {
            "post_id": post_id,
            "post_profile_id": post_profile_id,
            "limit": limit,
            "profile_id": profile_id,
            "equal": False,
            "sort": "FromMax"
        }
        return await self.request("getComments", data)

    async def get_my_profile_info(self, profile_id: Optional[str] = None):
        return await self.request("getMyProfileInfo", {"profile_id": profile_id})

    async def get_profile_list(self, limit: Optional[int] = 10):
        data = {
            "limit": limit,
            "equal": False,
            "sort": "FromMax"
        }
        return await self.request("getProfileList", data)

    async def get_profile_stories(self, profile_id: Optional[str] = None, limit: Optional[int] = 10):
        return self.request("getProfileStories", {"limit": limit, "profile_id": profile_id})

    async def get_recent_following_posts(self, profile_id: Optional[str] = None, limit: Optional[int] = 10):
        data = {
            "limit": limit,
            "equal": False,
            "sort": "FromMax",
            "profile_id": profile_id
        }
        return await self.request("getRecentFollowingPosts", data)

    async def get_share_link(self, post_id: str, target_profile_id: str, profile_id: Optional[str] = None):
        return await self.request("getShareLink", {"post_id": post_id, "target_profile_id": target_profile_id, "profile_id": profile_id})

    async def get_story_id(self, post_profile_id: str, profile_id: Optional[str] = None):
        return await self.request("getStoryIds", {"post_profile_id": post_profile_id, "profile_id": profile_id})

    async def save_post(self, post_id: str, target_profile_id: str, profile_id: Optional[str] = None):
        data = {
            "action_type": "Bookmark",
            "post_id": post_id,
            "target_profile_id": target_profile_id,
            "profile_id": profile_id
        }
        return await self.request("postBookmarkAction", data)

    async def unsave_post(self, post_id: str, post_profile_id: str, profile_id: Optional[str] = None):
        data = {
            "action_type": "Unbookmark",
            "post_id": post_id,
            "post_profile_id": post_profile_id,
            "profile_id": profile_id
        }
        return await self.request("postBookmarkAction", data)

    async def update_profile(self, profile_id: Optional[str] = None):
        data = {
            "profile_id": profile_id,
            "profile_status": "Public"
        }
        return await self.request("updateProfile", data)

    async def like_post(self, post_id: str, target_profile_id: str, profile_id: Optional[str] = None):
        data = {
            "action_type": "Like",
            "post_id": post_id,
            "target_profile_id": target_profile_id,
            "profile_id": profile_id
        }
        return await self.request("likePostAction", data)

    async def unlike_post(self, post_id: str, target_profile_id: str, profile_id: Optional[str] = None):
        data = {
            "action_type": "Unlike",
            "post_id": post_id,
            "target_profile_id": target_profile_id,
            "profile_id": profile_id
        }
        return await self.request("likePostAction", data)

    async def like_comment(self, comment_id: str, post_id: str, profile_id: Optional[str] = None):
        data = {
            "action_type": "Like",
            "comment_id": comment_id,
            "post_id": post_id,
            "profile_id": profile_id
        }
        return await self.request("likeCommentAction", data)

    async def unlike_comment(self, comment_id: str, post_id: str, profile_id: Optional[str] = None):
        data = {
            "action_type": "Unlike",
            "comment_id": comment_id,
            "post_id": post_id,
            "profile_id": profile_id
        }
        return await self.request("likeCommentAction", data)

    async def get_saved_posts(self, limit: int = 10, profile_id: Optional[str] = None):
        data = {
            "equal": False,
            "limit": limit,
            "sort": "FromMax",
            "profile_id": profile_id
        }
        return await self.request("getBookmarkedPosts", data)

    async def get_archive_stories(self, limit: int = 10, start_id: Optional[str] = None, profile_id: Optional[str] = None):
        data = {
            "equal": False,
            "limit": limit,
            "start_id": start_id,
            "sort": "FromMax",
            "profile_id": profile_id
        }
        return await self.request("getMyArchiveStories", data)

    async def get_profile_highlights(self, target_profile_id: str, limit: int = 10, profile_id: Optional[str] = None):
        data = {
            "equal": False,
            "limit": limit,
            "sort": "FromMax",
            "target_profile_id": target_profile_id,
            "profile_id": profile_id
        }
        return await self.request("getProfileHighlights", data)

    async def get_blocked_profiles(self, limit: int = 50, max_id: Optional[str] = None, profile_id: Optional[str] = None):
        data = {
            "equal": False,
            "limit": limit,
            "max_id": max_id,
            "sort": "FromMax",
            "profile_id": profile_id
        }
        return await self.request("getBlockedProfiles", data)

    async def get_profile_following(self, target_profile_id: str, limit: int = 50, profile_id: Optional[str] = None):
        data = {
            "equal": False,
            "f_type": "Following",
            "limit": limit,
            "sort": "FromMax",
            "target_profile_id": target_profile_id,
            "profile_id": profile_id
        }
        return await self.request("getProfileFollowers", data)
    
    async def get_profile_followers(self, target_profile_id: str, limit: int = 50, profile_id: Optional[str] = None):
        data = {
            "equal": False,
            "f_type": "Follower",
            "limit": limit,
            "sort": "FromMax",
            "target_profile_id": target_profile_id,
            "profile_id": profile_id
        }
        return await self.request("getProfileFollowers", data)

    async def get_my_stories_list(self, limit: Optional[int] = None, profile_id: Optional[str] = None):
        data = {
            "limit": limit,
            "profile_id": profile_id
        }
        return await self.request("getMyStoriesList", data)

    async def delete_story(self, story_id: str, profile_id: Optional[str] = None):
        data = {
            "profile_id": profile_id,
            "story_id": story_id
        }
        return await self.request("deleteStory", data)

    async def get_explore_posts(self, topic_id: str, limit: int = 50, max_id: Optional[str] = None, profile_id: Optional[str] = None):
        data = {
            "equal": False,
            "limit": limit,
            "max_id": max_id,
            "sort": "FromMax",
            "topic_id": topic_id,
            "profile_id": profile_id
        }
        return await self.request("getExplorePosts", data)

    async def search_profile(self, username: str, limit: int = 50, profile_id: Optional[str] = None):
        data = {
            "equal": False,
            "limit": limit,
            "sort": "FromMax",
            "username": username.replace("@", ""),
            "profile_id": profile_id
        }
        return await self.request("searchProfile", data)

    async def search_in_rubino(self, username: str, limit: int = 50, profile_id: Optional[str] = None):
        data = {
            "equal": False,
            "limit": limit,
            "sort": "FromMax",
            "username": username.startswith("@"),
            "profile_id": profile_id
        }
        return await self.request("searchProfile", data)

    async def get_hashtag_trend(self, limit: int = 50, profile_id: Optional[str] = None):
        data = {
            "equal": False,
            "limit": limit,
            "sort": "FromMax",
            "profile_id": profile_id
        }
        return await self.request("getHashTagTrend", data)

    async def search_hashtag(self, content: str, limit: int = 50, profile_id: Optional[str] = None):
        data = {
            "content": content,
            "equal": False,
            "limit": limit,
            "sort": "FromMax",
            "profile_id": profile_id
        }
        return await self.request("searchHashTag", data)

    async def get_posts_by_hashtag(self, hashtag: str, limit: int = 50, profile_id: Optional[str] = None):
        data = {
            "equal": False,
            "hashtag": hashtag,
            "limit": limit,
            "profile_id": profile_id
        }
        return await self.request("getPostsByHashTag", data)
    
    async def remove_page(self, profile_id: str, record_id: str):
        data = {
            "model": "Profile",
            "record_id": record_id,
            "profile_id": profile_id
        }
        return await self.request("removeRecord", data)
    
    async def get_new_follow_requests(self, profile_id: Optional[str] = None, limit: Optional[int] = 20):
        data = {
            "profile_id": profile_id,
            "limit": limit,
            "sort": "FromMax"
        }
        return await self.request("getNewFollowRequests", data)
        
    async def action_on_request(self, request_id: str, profile_id: Optional[str] = None, action: Literal["Accept", "Decline"] = "Accept"):
        data = {
            "action": action,
            "request_id": request_id,
            "profile_id": profile_id
        }
        return await self.request("actionOnRequest", data)
    
    async def accept_request(self, request_id: str, profile_id: Optional[str] = None):
        return await self.action_on_request(request_id, profile_id)

    async def reject_request(self, request_id: str, profile_id: Optional[str] = None):
        return await self.action_on_request(request_id, profile_id, "Decline")