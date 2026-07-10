import httpx
from app.core.config import PEXELS_API_KEY

PEXELS_BASE = "https://api.pexels.com"
HEADERS = {"Authorization": PEXELS_API_KEY}


async def search_image(query: str, per_page: int = 5) -> list[dict]:
    if not PEXELS_API_KEY:
        return []
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{PEXELS_BASE}/v1/search",
            headers=HEADERS,
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            {
                "url": photo["src"]["large"],
                "alt": photo.get("alt", ""),
                "photographer": photo.get("photographer", ""),
            }
            for photo in data.get("photos", [])
        ]


async def search_video(query: str, per_page: int = 5) -> list[dict]:
    if not PEXELS_API_KEY:
        return []
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{PEXELS_BASE}/videos/search",
            headers=HEADERS,
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for video in data.get("videos", []):
            video_files = video.get("video_files", [])
            best = None
            for vf in video_files:
                if vf.get("quality") in ("hd", "sd") and vf.get("link"):
                    if not best or (vf["quality"] == "hd" and best["quality"] != "hd"):
                        best = vf
            if best:
                results.append({
                    "url": best["link"],
                    "quality": best.get("quality", ""),
                    "width": best.get("width", 0),
                    "height": best.get("height", 0),
                    "duration": video.get("duration", 0),
                    "user": video.get("user", {}).get("name", "") if video.get("user") else "",
                })
        return results
