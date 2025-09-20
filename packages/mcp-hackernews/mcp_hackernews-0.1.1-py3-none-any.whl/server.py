from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Optional
import httpx

mcp = FastMCP("HNews")
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"


@mcp.tool(name="search_hackernews")
def search_hackernews(query: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """Search top Hacker News stories by calling the API directly.

    - query: keyword to match in title (case-insensitive).
    - limit: max number of results.
    """
    results: List[Dict] = []
    try:
        with httpx.Client(timeout=15.0) as client:
            # 1. Get top story IDs
            top_stories_url = f"{HN_API_BASE}/topstories.json"
            id_response = client.get(top_stories_url)
            id_response.raise_for_status()
            story_ids = id_response.json()

            # 2. Fetch story details for each ID
            for story_id in story_ids:
                if len(results) >= limit:
                    break

                item_url = f"{HN_API_BASE}/item/{story_id}.json"
                story_response = client.get(item_url)
                story_data = story_response.json()

                if not story_data:
                    continue

                # Filter by query if provided
                story_title = story_data.get("title", "")
                if query and query.lower() not in story_title.lower():
                    continue

                # Append simplified story object
                results.append(
                    {
                        "id": story_data.get("id"),
                        "title": story_title,
                        "url": story_data.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "author": story_data.get("by"),
                        "score": story_data.get("score"),
                        "comments": story_data.get("descendants"),
                    }
                )

    except httpx.RequestError as e:
        print(f"An error occurred while requesting Hacker News API: {e}")
        # Return an empty list on error
        return []

    return results
