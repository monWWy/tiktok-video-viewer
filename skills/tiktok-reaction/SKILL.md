---
name: tiktok-reaction
description: Analyze public TikTok links and give a conversational reaction. Use whenever the user shares a TikTok URL and asks what is in it, what is being said, whether it is funny, or asks for a reaction.
---

# TikTok reaction

## Goal
Give the user a useful, natural reaction to a TikTok video: explain what happens, summarize spoken content, identify the joke or key moment, and then give a brief opinion. Do not pretend to have watched a video when only metadata is available.

## Workflow
1. Detect a TikTok URL in the user's message. Accept public share links such as `vt.tiktok.com`, `vm.tiktok.com`, and canonical `www.tiktok.com` links.
2. If a supported short-form video analysis tool is available in the current assistant environment, use it on the full public URL. For vidIQ's short-form analysis tool, submit the URL and poll its returned job ID until it completes. Respect the tool's credit cost and availability.
3. If video analysis is unavailable, call the MCP tool `inspect_tiktok_link` when the TikTok Link Inspector MCP server is connected. Use its result only for public metadata (title, creator, thumbnail/embed information).
4. Clearly distinguish evidence:
   - If the video-analysis tool returned transcript/scenes, summarize those findings and react to them.
   - If only oEmbed metadata or an embedded player is available, say that the video itself has not been analyzed. Do not infer the video's events or dialogue from its title or thumbnail.
5. Keep the reaction concise and conversational in the user's language. Explain the premise, the punchline or interesting moment, and why it works (or does not), when supported by the analysis.
6. If the link is private, unavailable, unsupported, or cannot be analyzed, say so plainly and offer the next useful step without claiming success.

## Tool limitations
The MCP server in this repository currently exposes `inspect_tiktok_link(url)`. It validates TikTok HTTPS links and retrieves public TikTok oEmbed metadata. It does not download, decode, transcribe, or analyze video/audio. The website's embedded TikTok player is for viewing only; it does not make the media stream available to the server.

Never claim that the MCP server has analyzed video content unless a future, separately integrated video-analysis provider actually returns that content.
