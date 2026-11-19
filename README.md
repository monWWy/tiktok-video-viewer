# TikTok Link Inspector

A small MCP server for inspecting public TikTok link metadata.

## Current scope

The `inspect_tiktok_link` tool validates a TikTok HTTPS link and requests its public metadata through TikTok's oEmbed endpoint. It can return the title, creator, thumbnail information, and embed HTML when available.

**It does not watch, download, transcribe, or analyze the video/audio.** TikTok may not expose metadata for private, unavailable, region-restricted, or unsupported videos.

## Run locally

Requires Python 3.11+.

```bash
pip install -r requirements.txt
python server.py
```

The MCP server uses Streamable HTTP. By default it listens on port 8000 and exposes the MCP endpoint at `/mcp`.

## Deploy to Render

1. Create a new **Web Service** from this GitHub repository.
2. Choose the Docker runtime (Render can detect the included Dockerfile).
3. Choose the Free plan if available for your account and region.
4. Deploy. The service listens on Render's `PORT` environment variable.

## Connect an MCP client

Use the deployed service's base URL with the `/mcp` path, for example:

`https://YOUR-SERVICE.onrender.com/mcp`

Do not add secrets to this repository. This first version has no authentication layer, so treat the public endpoint as a prototype and do not expose it to untrusted traffic without adding access controls and rate limiting.
