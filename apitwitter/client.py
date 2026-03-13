"""ApiTwitter SDK main client."""

from __future__ import annotations

from typing import Any

import httpx

from apitwitter.exceptions import (
    ApiTwitterError,
    AuthenticationError,
    InsufficientCreditsError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


class ApiTwitter:
    """Client for the ApiTwitter REST API.

    Usage::

        from apitwitter import ApiTwitter

        client = ApiTwitter("your-api-key")
        user = client.get_user("elonmusk")
        print(user)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.apitwitter.com",
        timeout: float = 30.0,
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            timeout=timeout,
        )

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # -- internal helpers --

    def _request(self, method: str, path: str, **kwargs) -> Any:
        resp = self._client.request(method, path, **kwargs)
        return self._handle_response(resp)

    def _get(self, path: str, params: dict | None = None) -> Any:
        return self._request("GET", path, params=params)

    def _post(self, path: str, body: dict | None = None) -> Any:
        return self._request("POST", path, json=body)

    def _delete(self, path: str, body: dict | None = None) -> Any:
        return self._request("DELETE", path, json=body)

    def _patch(self, path: str, body: dict | None = None) -> Any:
        return self._request("PATCH", path, json=body)

    def _handle_response(self, resp: httpx.Response) -> Any:
        try:
            data = resp.json()
        except Exception:
            data = {"msg": resp.text}

        if resp.status_code == 200:
            return data.get("data", data)

        msg = data.get("msg", data.get("message", str(data)))
        status = resp.status_code

        if status == 401:
            raise AuthenticationError(msg, status_code=status, response=data)
        if status == 402:
            raise InsufficientCreditsError(msg, status_code=status, response=data)
        if status == 404:
            raise NotFoundError(msg, status_code=status, response=data)
        if status == 429:
            retry = float(data.get("retry_after", 0))
            raise RateLimitError(msg, retry_after=retry, status_code=status, response=data)
        if status == 400:
            raise ValidationError(msg, status_code=status, response=data)
        raise ApiTwitterError(msg, status_code=status, response=data)

    # ── Session ───────────────────────────────────────────────

    def verify_session(self, cookie: str, proxy: str, *, user_agent: str | None = None) -> str:
        """Verify Twitter cookies. Returns the authenticated screen name."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post("/twitter/session/verify", body)

    # ── Users (GET — pool) ────────────────────────────────────

    def get_user(self, username: str) -> dict:
        """Get user profile by screen name (uses server pool)."""
        return self._get(f"/twitter/user/{username}")

    def get_user_by_id(self, user_id: str) -> dict:
        """Get user profile by numeric ID (uses server pool)."""
        return self._get(f"/twitter/user/id/{user_id}")

    def get_users_batch(self, user_ids: list[str]) -> list[dict]:
        """Batch get users by IDs (uses server pool)."""
        return self._get("/twitter/users/batch", params={"userIds": ",".join(user_ids)})

    def get_followers(self, username: str, count: int = 200, cursor: str | None = None) -> dict:
        """Get followers of a user (uses server pool)."""
        params: dict[str, Any] = {"count": count}
        if cursor:
            params["cursor"] = cursor
        return self._get(f"/twitter/user/{username}/followers", params=params)

    def get_following(self, username: str, count: int = 200, cursor: str | None = None) -> dict:
        """Get who a user follows (uses server pool)."""
        params: dict[str, Any] = {"count": count}
        if cursor:
            params["cursor"] = cursor
        return self._get(f"/twitter/user/{username}/following", params=params)

    def get_followers_you_know(self, username: str, count: int = 20, cursor: str | None = None) -> dict:
        """Get mutual followers (uses server pool)."""
        params: dict[str, Any] = {"count": count}
        if cursor:
            params["cursor"] = cursor
        return self._get(f"/twitter/user/{username}/followers-you-know", params=params)

    # ── Users (POST — own credentials) ────────────────────────

    def get_user_post(self, username: str, cookie: str, proxy: str) -> dict:
        """Get user profile using your own credentials."""
        return self._post(f"/twitter/user/{username}", {"cookie": cookie, "proxy": proxy})

    def get_user_likes(self, username: str, cookie: str, proxy: str, count: int = 20, cursor: str | None = None) -> dict:
        """Get a user's liked tweets."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post(f"/twitter/user/{username}/likes", body)

    def get_user_media(self, username: str, cookie: str, proxy: str, count: int = 20, cursor: str | None = None) -> dict:
        """Get a user's media tweets."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post(f"/twitter/user/{username}/media", body)

    def get_user_replies(self, username: str, cookie: str, proxy: str, count: int = 20, cursor: str | None = None) -> dict:
        """Get a user's tweets and replies."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post(f"/twitter/user/{username}/replies", body)

    def get_blocked(self, cookie: str, proxy: str, count: int = 200, cursor: str | None = None) -> dict:
        """Get blocked accounts."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post("/twitter/blocked", body)

    def get_muted(self, cookie: str, proxy: str, count: int = 200, cursor: str | None = None) -> dict:
        """Get muted accounts."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post("/twitter/muted", body)

    def remove_follower(self, user_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Remove a follower."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/user/{user_id}/remove-follower", body)

    # ── Tweets (GET — pool) ───────────────────────────────────

    def get_user_tweets(self, username: str, cursor: str | None = None) -> dict:
        """Get a user's tweets (uses server pool)."""
        params: dict[str, Any] = {}
        if cursor:
            params["cursor"] = cursor
        return self._get(f"/twitter/user/{username}/tweets", params=params)

    def get_tweets(self, tweet_ids: list[str]) -> list[dict]:
        """Get tweets by IDs (uses server pool)."""
        return self._get("/twitter/tweets/lookup", params={"tweet_ids": ",".join(tweet_ids)})

    def search(self, query: str, product: str = "Top", count: int = 20, cursor: str | None = None) -> dict:
        """Search tweets (uses server pool)."""
        params: dict[str, Any] = {"query": query, "product": product, "count": count}
        if cursor:
            params["cursor"] = cursor
        return self._get("/twitter/search", params=params)

    # ── Tweets (POST — own credentials) ───────────────────────

    def create_tweet(self, tweet_text: str, cookie: str, proxy: str, *, reply_to: str | None = None, user_agent: str | None = None) -> dict:
        """Post a new tweet."""
        body: dict[str, Any] = {"tweet_text": tweet_text, "cookie": cookie, "proxy": proxy}
        if reply_to:
            body["reply_to_tweet_id"] = reply_to
        if user_agent:
            body["user_agent"] = user_agent
        return self._post("/twitter/tweets", body)

    def delete_tweet(self, tweet_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Delete a tweet."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._delete(f"/twitter/tweets/{tweet_id}", body)

    def retweet(self, tweet_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Retweet a tweet."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/tweets/{tweet_id}/retweet", body)

    def unretweet(self, tweet_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Remove a retweet."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._delete(f"/twitter/tweets/{tweet_id}/retweet", body)

    def pin_tweet(self, tweet_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Pin a tweet to profile."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/tweets/{tweet_id}/pin", body)

    def unpin_tweet(self, tweet_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Unpin a tweet."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._delete(f"/twitter/tweets/{tweet_id}/pin", body)

    # ── Engagement ────────────────────────────────────────────

    def like(self, tweet_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Like a tweet."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/tweets/{tweet_id}/like", body)

    def unlike(self, tweet_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Unlike a tweet."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/tweets/{tweet_id}/unlike", body)

    def follow(self, user_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Follow a user."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/user/{user_id}/follow", body)

    def unfollow(self, user_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Unfollow a user."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/user/{user_id}/unfollow", body)

    # ── DM ────────────────────────────────────────────────────

    def send_dm(self, user_id: str, text: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Send a direct message."""
        body: dict[str, Any] = {"text": text, "cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/dm/{user_id}", body)

    def dm_block(self, user_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Block a user in DMs."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/dm/block/{user_id}", body)

    def dm_unblock(self, user_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Unblock a user in DMs."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._delete(f"/twitter/dm/block/{user_id}", body)

    # ── Bookmarks ─────────────────────────────────────────────

    def add_bookmark(self, tweet_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Bookmark a tweet."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/tweets/{tweet_id}/bookmark", body)

    def remove_bookmark(self, tweet_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Remove a bookmark."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._delete(f"/twitter/tweets/{tweet_id}/bookmark", body)

    def get_bookmarks(self, cookie: str, proxy: str, count: int = 20, cursor: str | None = None) -> dict:
        """Get bookmarked tweets."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post("/twitter/bookmarks", body)

    # ── Timeline ──────────────────────────────────────────────

    def get_timeline_for_you(self, cookie: str, proxy: str, count: int = 20, cursor: str | None = None, *, user_agent: str | None = None) -> dict:
        """Get the For You home timeline."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        if user_agent:
            body["user_agent"] = user_agent
        return self._post("/twitter/timeline/for-you", body)

    def get_timeline_latest(self, cookie: str, proxy: str, count: int = 20, cursor: str | None = None, *, user_agent: str | None = None) -> dict:
        """Get the Latest (Following) home timeline."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        if user_agent:
            body["user_agent"] = user_agent
        return self._post("/twitter/timeline/latest", body)

    # ── Search (POST) ─────────────────────────────────────────

    def search_post(self, query: str, cookie: str, proxy: str, product: str = "Top", count: int = 20, cursor: str | None = None) -> dict:
        """Search tweets with your own credentials."""
        body: dict[str, Any] = {"query": query, "cookie": cookie, "proxy": proxy, "product": product, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post("/twitter/search", body)

    # ── Lists ─────────────────────────────────────────────────

    def create_list(self, name: str, cookie: str, proxy: str, *, description: str | None = None, is_private: bool = False, user_agent: str | None = None) -> dict:
        """Create a new list."""
        body: dict[str, Any] = {"name": name, "cookie": cookie, "proxy": proxy, "is_private": is_private}
        if description:
            body["description"] = description
        if user_agent:
            body["user_agent"] = user_agent
        return self._post("/twitter/lists", body)

    def delete_list(self, list_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Delete a list."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._delete(f"/twitter/lists/{list_id}", body)

    def update_list(self, list_id: str, cookie: str, proxy: str, *, name: str | None = None, description: str | None = None, is_private: bool | None = None, user_agent: str | None = None) -> dict:
        """Update a list."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if name:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if is_private is not None:
            body["is_private"] = is_private
        if user_agent:
            body["user_agent"] = user_agent
        return self._patch(f"/twitter/lists/{list_id}", body)

    def get_list_info(self, list_id: str, cookie: str, proxy: str) -> dict:
        """Get list details."""
        return self._post(f"/twitter/lists/{list_id}/info", {"cookie": cookie, "proxy": proxy})

    def get_list_tweets(self, list_id: str, cookie: str, proxy: str, count: int = 20, cursor: str | None = None) -> dict:
        """Get tweets from a list."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post(f"/twitter/lists/{list_id}/tweets", body)

    def get_list_members(self, list_id: str, cookie: str, proxy: str, count: int = 20, cursor: str | None = None) -> dict:
        """Get list members."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post(f"/twitter/lists/{list_id}/members", body)

    def add_list_member(self, list_id: str, user_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Add a member to a list."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/lists/{list_id}/members/{user_id}/add", body)

    def remove_list_member(self, list_id: str, user_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Remove a member from a list."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/lists/{list_id}/members/{user_id}/remove", body)

    def get_owned_lists(self, user_id: str, cookie: str, proxy: str, count: int = 20, cursor: str | None = None) -> dict:
        """Get lists owned by a user."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "user_id": user_id, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post("/twitter/lists/owned", body)

    def get_list_memberships(self, user_id: str, cookie: str, proxy: str, count: int = 20, cursor: str | None = None) -> dict:
        """Get lists a user is a member of."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "user_id": user_id, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post("/twitter/lists/memberships", body)

    def get_list_subscribers(self, list_id: str, cookie: str, proxy: str, count: int = 20, cursor: str | None = None) -> dict:
        """Get list subscribers."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post(f"/twitter/lists/{list_id}/subscribers", body)

    def subscribe_to_list(self, list_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Subscribe to a list."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/lists/{list_id}/subscribe", body)

    def unsubscribe_from_list(self, list_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Unsubscribe from a list."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._delete(f"/twitter/lists/{list_id}/subscribe", body)

    # ── Communities ───────────────────────────────────────────

    def explore_communities(self, cookie: str, proxy: str, count: int = 20, cursor: str | None = None) -> dict:
        """Explore communities."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post("/twitter/communities/explore", body)

    def get_community(self, community_id: str, cookie: str, proxy: str) -> dict:
        """Get community info."""
        return self._post(f"/twitter/communities/{community_id}", {"cookie": cookie, "proxy": proxy})

    def join_community(self, community_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Join a community."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/communities/{community_id}/join", body)

    def leave_community(self, community_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Leave a community."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._delete(f"/twitter/communities/{community_id}/join", body)

    def get_community_tweets(self, community_id: str, cookie: str, proxy: str, count: int = 20, cursor: str | None = None) -> dict:
        """Get community tweets."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post(f"/twitter/communities/{community_id}/tweets", body)

    def get_community_media(self, community_id: str, cookie: str, proxy: str, count: int = 20, cursor: str | None = None) -> dict:
        """Get community media."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy, "count": count}
        if cursor:
            body["cursor"] = cursor
        return self._post(f"/twitter/communities/{community_id}/media", body)

    # ── Topics ────────────────────────────────────────────────

    def get_topic(self, topic_id: str, cookie: str, proxy: str) -> dict:
        """Get topic info."""
        return self._post(f"/twitter/topics/{topic_id}", {"cookie": cookie, "proxy": proxy})

    def follow_topic(self, topic_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Follow a topic."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._post(f"/twitter/topics/{topic_id}/follow", body)

    def unfollow_topic(self, topic_id: str, cookie: str, proxy: str, *, user_agent: str | None = None) -> dict:
        """Unfollow a topic."""
        body: dict[str, Any] = {"cookie": cookie, "proxy": proxy}
        if user_agent:
            body["user_agent"] = user_agent
        return self._delete(f"/twitter/topics/{topic_id}/follow", body)
