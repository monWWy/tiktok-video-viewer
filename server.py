import os
from urllib.parse import urlparse

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "TikTok Link Inspector",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
)

ALLOWED_HOSTS = {
    "tiktok.com",
    "www.tiktok.com",
    "m.tiktok.com",
    "vm.tiktok.com",
    "vt.tiktok.com",
}


def validate_tiktok_url(value: str) -> str:
    value = value.strip()
    if not value or len(value) > 2048:
        raise ValueError("Provide a valid TikTok URL (maximum 2048 characters).")

    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()

    if parsed.scheme != "https" or host not in ALLOWED_HOSTS:
        raise ValueError("Only HTTPS links from TikTok are supported.")

    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed.")

    return value


@mcp.tool()
async def inspect_tiktok_link(url: str) -> dict:
    """Get public metadata for a TikTok video link using TikTok's oEmbed endpoint.

    Returns metadata such as the creator, title, and embed HTML when TikTok
    makes it available. This does not download or analyze video/audio.
    """
    safe_url = validate_tiktok_url(url)
    endpoint = "https://www.tiktok.com/oembed"

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(15.0),
            follow_redirects=True,
            headers={"User-Agent": "TikTokLinkInspector/1.0"},
        ) as client:
            response = await client.get(endpoint, params={"url": safe_url})
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        return {
            "ok": False,
            "error": "TikTok did not provide metadata for this link.",
            "status_code": exc.response.status_code,
            "hint": "The video may be private, unavailable, region-restricted, or unsupported by oEmbed.",
        }
    except (httpx.HTTPError, ValueError) as exc:
        return {
            "ok": False,
            "error": "Could not retrieve TikTok metadata.",
            "details": str(exc),
        }

    return {
        "ok": True,
        "source": "TikTok oEmbed",
        "title": data.get("title"),
        "author_name": data.get("author_name"),
        "author_url": data.get("author_url"),
        "provider_name": data.get("provider_name"),
        "thumbnail_url": data.get("thumbnail_url"),
        "thumbnail_width": data.get("thumbnail_width"),
        "thumbnail_height": data.get("thumbnail_height"),
        "embed_html": data.get("html"),
        "note": "Metadata only. The video and its audio have not been watched or analyzed.",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
