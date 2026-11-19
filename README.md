# TikTok Link Inspector

A small **Streamable HTTP MCP server** plus a separate web page for inspecting public TikTok link metadata.

## Project structure

- `server.py` — MCP server and web application.
- `/mcp` — Streamable HTTP MCP endpoint.
- `/` — separate browser page with the TikTok link form and official embedded player.
- `/api/inspect` — web page's metadata endpoint.
- `skills/tiktok-reaction/SKILL.md` — Agent Skill instructions for how an assistant should handle TikTok links and react to analyzed videos.

## MCP tool currently available

### `inspect_tiktok_link(url)`

Validates a TikTok HTTPS URL and requests public metadata from TikTok's oEmbed endpoint. When available, it returns the title, creator, profile URL, thumbnail URL, and embed HTML.

**Important:** this tool does not watch, download, transcribe, or analyze the video/audio. An embedded player is only a player; it does not expose the media stream to this server.

## Skill

The Agent Skill in `skills/tiktok-reaction/SKILL.md` describes the assistant workflow:
1. Prefer an available short-form video analysis provider for the actual video.
2. Use this MCP server as a metadata fallback.
3. Never claim to have watched or analyzed a video when only metadata was retrieved.
4. Give the user a concise, natural reaction in their language when actual analysis is available.

A Skill file is guidance for a compatible assistant/agent. Committing it to GitHub does **not** automatically install it into ChatGPT or connect this MCP server to a ChatGPT account. Those are separate setup steps.

## Run locally

Requires Python 3.11+.

```bash
pip install -r requirements.txt
python server.py
```

The server listens on port 8000 by default and exposes the MCP endpoint at `/mcp`.

## Deploy to Render

The included Dockerfile and `render.yaml` define the existing web service. The site and MCP endpoint run in the same process, so keep both routes when changing the app.

## Connect an MCP client

Use the deployed service's MCP URL:

```
https://YOUR-SERVICE.onrender.com/mcp
```

The service currently has no authentication layer or rate limiting. Treat the public endpoint as a prototype; add access controls and rate limiting before exposing it to untrusted traffic. Do not commit secrets or API keys.

## Roadmap

- Add an authorized video-analysis provider behind a separate MCP tool.
- Keep metadata inspection separate from actual video analysis.
- Add tests for URL validation and provider error handling.
