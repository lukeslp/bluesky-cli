"""
BlueSky API Client with multi-provider AI support
"""
import requests
import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .utils import get_ai_config, get_bsky_credentials, console

# BlueSky API endpoints
BSKY_AUTH_ENDPOINT = "https://bsky.social/xrpc/com.atproto.server.createSession"
BSKY_FEED_ENDPOINT = "https://bsky.social/xrpc/app.bsky.feed.getAuthorFeed"
BSKY_PROFILE_ENDPOINT = "https://bsky.social/xrpc/app.bsky.actor.getProfile"
BSKY_FOLLOWERS_ENDPOINT = "https://bsky.social/xrpc/app.bsky.graph.getFollowers"
BSKY_FOLLOWS_ENDPOINT = "https://bsky.social/xrpc/app.bsky.graph.getFollows"
BSKY_SEARCH_POSTS_ENDPOINT = "https://bsky.social/xrpc/app.bsky.feed.searchPosts"
BSKY_SEARCH_ACTORS_ENDPOINT = "https://bsky.social/xrpc/app.bsky.actor.searchActors"


class BlueSkyAPI:
    def __init__(self):
        self.ai_config = get_ai_config()
        self.ai_client = None
        self._init_ai_client()

        self.bsky_auth_token = None
        self.bsky_headers = None
        self.bsky_did = None

    def _init_ai_client(self):
        """Initialize the AI client based on configured provider."""
        if not self.ai_config["api_key"]:
            return

        # OpenAI SDK works with OpenAI, Anthropic (via proxy), and Ollama
        self.ai_client = OpenAI(
            api_key=self.ai_config["api_key"],
            base_url=self.ai_config["base_url"],
        )

    def authenticate_bsky(self, identifier: str = None, password: str = None) -> bool:
        """Authenticate with BlueSky API."""
        if not identifier or not password:
            conf_id, conf_pass = get_bsky_credentials()
            identifier = identifier or conf_id
            password = password or conf_pass

        if not identifier or not password:
            raise ValueError("BlueSky credentials not found.")

        auth_payload = {"identifier": identifier, "password": password}

        try:
            response = requests.post(BSKY_AUTH_ENDPOINT, json=auth_payload)
            response.raise_for_status()
            auth_data = response.json()
            self.bsky_auth_token = auth_data.get("accessJwt")
            if not self.bsky_auth_token:
                raise ValueError("No access token returned")

            self.bsky_did = auth_data.get("did")
            self.bsky_headers = {
                "Authorization": f"Bearer {self.bsky_auth_token}",
                "Content-Type": "application/json"
            }
            return True
        except Exception as e:
            raise RuntimeError(f"BlueSky authentication failed: {e}")

    def format_handle(self, handle: str) -> str:
        """Format handle for BlueSky API."""
        if handle.startswith("@"):
            handle = handle[1:]
        if "." not in handle:
            handle = f"{handle}.bsky.social"
        return handle

    def get_profile(self, handle: str) -> dict:
        """Get user profile."""
        if not self.bsky_headers:
            raise RuntimeError("Not authenticated. Call authenticate_bsky() first.")
        handle = self.format_handle(handle)
        params = {"actor": handle}
        try:
            response = requests.get(BSKY_PROFILE_ENDPOINT, params=params, headers=self.bsky_headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Error fetching profile: {e}")

    def get_bsky_posts(self, handle: str, limit: int = 50) -> dict:
        """Get user's recent posts."""
        if not self.bsky_headers:
            raise RuntimeError("Not authenticated.")
        handle = self.format_handle(handle)
        params = {"actor": handle, "limit": limit}
        try:
            response = requests.get(BSKY_FEED_ENDPOINT, params=params, headers=self.bsky_headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Error fetching posts: {e}")

    def get_post_content(self, posts_data: dict) -> str:
        """Extract text content from posts."""
        posts = posts_data.get("feed", [])
        combined_text = ""
        for item in posts:
            post_view = item.get("post", {})
            record = post_view.get("record", {})
            text = record.get("text", "")
            if text:
                combined_text += text + "\n"
        if not combined_text.strip():
            raise ValueError("No post texts found.")
        return combined_text.strip()

    def get_followers(self, handle: str, limit: int = 50) -> dict:
        """Get user's followers."""
        if not self.bsky_headers:
            raise RuntimeError("Not authenticated.")
        handle = self.format_handle(handle)
        params = {"actor": handle, "limit": limit}
        try:
            response = requests.get(BSKY_FOLLOWERS_ENDPOINT, params=params, headers=self.bsky_headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Error fetching followers: {e}")

    def get_follows(self, handle: str, limit: int = 50) -> dict:
        """Get users the handle follows."""
        if not self.bsky_headers:
            raise RuntimeError("Not authenticated.")
        handle = self.format_handle(handle)
        params = {"actor": handle, "limit": limit}
        try:
            response = requests.get(BSKY_FOLLOWS_ENDPOINT, params=params, headers=self.bsky_headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Error fetching follows: {e}")

    def search_posts(self, query: str, limit: int = 20) -> dict:
        """Search posts by keyword."""
        if not self.bsky_headers:
            raise RuntimeError("Not authenticated.")
        params = {"q": query, "limit": limit}
        try:
            response = requests.get(BSKY_SEARCH_POSTS_ENDPOINT, params=params, headers=self.bsky_headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Error searching posts: {e}")

    def search_users(self, query: str, limit: int = 20) -> dict:
        """Search users by keyword."""
        if not self.bsky_headers:
            raise RuntimeError("Not authenticated.")
        params = {"q": query, "limit": limit}
        try:
            response = requests.get(BSKY_SEARCH_ACTORS_ENDPOINT, params=params, headers=self.bsky_headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Error searching users: {e}")

    def vibe_check(self, text: str) -> str:
        """Analyze user's posting vibe using AI."""
        if not self.ai_client:
            raise RuntimeError(f"AI not configured. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or use Ollama.")

        system_prompt = """You are an insightful social media analyst. Analyze the provided BlueSky posts and provide a 'vibe check' that includes:
1. Overall tone and personality
2. Key topics and interests
3. Communication style
4. Notable patterns or themes
Be concise but insightful."""

        try:
            completion = self.ai_client.chat.completions.create(
                model=self.ai_config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze these BlueSky posts:\n\n{text}"}
                ],
                temperature=0.3,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Error performing vibe check: {e}")

    def summarize_text(self, text: str) -> str:
        """Summarize posts using AI."""
        if not self.ai_client:
            raise RuntimeError("AI not configured.")
        try:
            prompt = f"Summarize these BlueSky posts concisely, capturing key themes:\n\n{text}"
            completion = self.ai_client.chat.completions.create(
                model=self.ai_config["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Error summarizing: {e}")

    def get_all_followers(self, handle: str, max_results: int = 1000, batch_size: int = 100) -> List[dict]:
        """Get all followers with pagination."""
        if not self.bsky_headers:
            raise RuntimeError("Not authenticated.")
        handle = self.format_handle(handle)
        all_followers = []
        cursor = None

        while max_results == 0 or len(all_followers) < max_results:
            params = {"actor": handle, "limit": batch_size}
            if cursor:
                params["cursor"] = cursor
            try:
                r = requests.get(BSKY_FOLLOWERS_ENDPOINT, params=params, headers=self.bsky_headers)
                r.raise_for_status()
                data = r.json()
                all_followers.extend(data.get("followers", []))
                cursor = data.get("cursor")
                if not cursor:
                    break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                break

        if max_results > 0:
            all_followers = all_followers[:max_results]
        return all_followers

    def get_all_follows(self, handle: str, max_results: int = 1000, batch_size: int = 100) -> List[dict]:
        """Get all follows with pagination."""
        if not self.bsky_headers:
            raise RuntimeError("Not authenticated.")
        handle = self.format_handle(handle)
        all_follows = []
        cursor = None

        while max_results == 0 or len(all_follows) < max_results:
            params = {"actor": handle, "limit": batch_size}
            if cursor:
                params["cursor"] = cursor
            try:
                r = requests.get(BSKY_FOLLOWS_ENDPOINT, params=params, headers=self.bsky_headers)
                r.raise_for_status()
                data = r.json()
                all_follows.extend(data.get("follows", []))
                cursor = data.get("cursor")
                if not cursor:
                    break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                break

        if max_results > 0:
            all_follows = all_follows[:max_results]
        return all_follows

    def save_user_list_to_csv(self, users: List[dict], filename: str) -> bool:
        """Export user list to CSV."""
        import csv
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['handle', 'displayName', 'did', 'description', 'followerCount', 'followingCount']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for user in users:
                    writer.writerow({
                        'handle': user.get('handle', ''),
                        'displayName': user.get('displayName', ''),
                        'did': user.get('did', ''),
                        'description': user.get('description', ''),
                        'followerCount': user.get('followerCount', 0),
                        'followingCount': user.get('followingCount', 0)
                    })
            return True
        except Exception as e:
            console.print(f"[red]Error saving CSV: {e}[/red]")
            return False
