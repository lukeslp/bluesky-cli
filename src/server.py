#!/usr/bin/env python3
import sys
import json
import logging
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
try:
    from bluesky_cli.api import BlueSkyAPI
except ImportError:
    # Try local import if running from src
    sys.path.append(os.path.dirname(__file__))
    from bluesky_cli.api import BlueSkyAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bluesky-mcp")

api = BlueSkyAPI()

# Auto-authenticate if env vars are present
BSKY_HANDLE = os.getenv("BSKY_HANDLE")
BSKY_PASSWORD = os.getenv("BSKY_PASSWORD")

if BSKY_HANDLE and BSKY_PASSWORD:
    try:
        api.authenticate_bsky(BSKY_HANDLE, BSKY_PASSWORD)
        logger.info(f"Authenticated as {BSKY_HANDLE}")
    except Exception as e:
        logger.error(f"Auth failed: {e}")

def list_tools():
    return [
        {
            "name": "dream_bsky_get_profile",
            "description": "Get a BlueSky user profile.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "handle": {"type": "string", "description": "User handle (e.g. 'jay.bsky.social')"}
                },
                "required": ["handle"]
            }
        },
        {
            "name": "dream_bsky_get_feed",
            "description": "Get recent posts from a user.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "handle": {"type": "string", "description": "User handle"},
                    "limit": {"type": "integer", "description": "Number of posts (default 10)", "default": 20}
                },
                "required": ["handle"]
            }
        },
        {
            "name": "dream_bsky_search",
            "description": "Search for posts or users.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term"},
                    "type": {"type": "string", "enum": ["posts", "users"], "default": "posts"},
                    "limit": {"type": "integer", "default": 20}
                },
                "required": ["query"]
            }
        },
        {
            "name": "dream_bsky_vibe_check",
            "description": "Analyze the 'vibe' and personality of a user based on their posts.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "handle": {"type": "string", "description": "User handle"}
                },
                "required": ["handle"]
            }
        }
    ]

def handle_call_tool(name, arguments):
    if not api.bsky_did and not (BSKY_HANDLE and BSKY_PASSWORD):
         return {"content": [{"type": "text", "text": "Error: BSKY_HANDLE and BSKY_PASSWORD environment variables not set."}], "isError": True}
    
    # Ensure authenticated
    if not api.bsky_did:
        try:
             api.authenticate_bsky(BSKY_HANDLE, BSKY_PASSWORD)
        except Exception as e:
             return {"content": [{"type": "text", "text": f"Authentication failed: {e}"}], "isError": True}

    try:
        if name == "dream_bsky_get_profile":
            profile = api.get_profile(arguments["handle"])
            return {"content": [{"type": "text", "text": json.dumps(profile, indent=2)}]}
            
        elif name == "dream_bsky_get_feed":
            limit = arguments.get("limit", 20)
            feed = api.get_bsky_posts(arguments["handle"], limit=limit)
            # Summarize or extract text to save context
            clean_feed = []
            for item in feed.get('feed', []):
                 post = item.get('post', {})
                 record = post.get('record', {})
                 clean_feed.append({
                     'text': record.get('text'),
                     'created_at': record.get('createdAt'),
                     'likes': post.get('likeCount'),
                     'reposts': post.get('repostCount')
                 })
            return {"content": [{"type": "text", "text": json.dumps(clean_feed, indent=2)}]}
            
        elif name == "dream_bsky_search":
            query = arguments["query"]
            limit = arguments.get("limit", 20)
            search_type = arguments.get("type", "posts")
            
            if search_type == "posts":
                res = api.search_posts(query, limit)
                # Cleaning search results
                clean_res = []
                for post in res.get('posts', []):
                    clean_res.append({
                        'author': post.get('author', {}).get('handle'),
                        'text': post.get('record', {}).get('text'),
                        'created_at': post.get('record', {}).get('createdAt')
                    })
                return {"content": [{"type": "text", "text": json.dumps(clean_res, indent=2)}]}
            else:
                res = api.search_users(query, limit)
                return {"content": [{"type": "text", "text": json.dumps(res.get('actors', []), indent=2)}]}

        elif name == "dream_bsky_vibe_check":
            handle = arguments["handle"]
            # 1. Get posts
            feed = api.get_bsky_posts(handle, limit=50)
            text = api.get_post_content(feed)
            if not text:
                 return {"content": [{"type": "text", "text": f"No text found for {handle} to analyze."}]}
            
            # 2. Vibe Check
            # Note: This relies on api.ai_client which needs OPENAI/ANTHROPIC keys in env too
            try:
                analysis = api.vibe_check(text)
                return {"content": [{"type": "text", "text": analysis}]}
            except Exception as e:
                 return {"content": [{"type": "text", "text": f"AI Analysis failed: {e}. Check API keys."}], "isError": True}

        return {"content": [{"type": "text", "text": f"Tool not found: {name}"}], "isError": True}
        
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error executing {name}: {str(e)}"}], "isError": True}

def run_server():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line)
            req_id = request.get("id")
            
            response = {"jsonrpc": "2.0", "id": req_id}
            
            if request.get("method") == "initialize":
                response["result"] = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "geepers-bluesky", "version": "1.0.0"}
                }
            elif request.get("method") == "tools/list":
                response["result"] = {"tools": list_tools()}
            elif request.get("method") == "tools/call":
                result = handle_call_tool(request["params"]["name"], request["params"]["arguments"])
                if result.get("isError"):
                     response["error"] = {"code": -32603, "message": result["content"][0]["text"]}
                else:
                     response["result"] = result
            else:
                continue
                
            print(json.dumps(response), flush=True)
        except Exception:
            break

if __name__ == "__main__":
    run_server()
