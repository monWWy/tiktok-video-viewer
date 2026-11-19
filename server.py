import os
from urllib.parse import urlparse

import httpx
import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

mcp = FastMCP(
    "TikTok Link Inspector",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
    stateless_http=True,
    json_response=True,
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
        raise ValueError("Вставь корректную ссылку TikTok (до 2048 символов).")

    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or host not in ALLOWED_HOSTS:
        raise ValueError("Поддерживаются только HTTPS-ссылки с доменов TikTok.")
    if parsed.username or parsed.password:
        raise ValueError("Ссылки с данными для входа не поддерживаются.")
    return value


async def get_tiktok_metadata(url: str) -> dict:
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
            "error": "TikTok не отдал данные для этой ссылки.",
            "status_code": exc.response.status_code,
            "hint": "Ролик может быть закрытым, недоступным в регионе или не поддерживаться oEmbed.",
        }
    except (httpx.HTTPError, ValueError) as exc:
        return {"ok": False, "error": "Не удалось получить метаданные TikTok.", "details": str(exc)}

    return {
        "ok": True,
        "source": "TikTok oEmbed",
        "title": data.get("title"),
        "author_name": data.get("author_name"),
        "author_url": data.get("author_url"),
        "thumbnail_url": data.get("thumbnail_url"),
        "embed_html": data.get("html"),
        "note": "Видео показано через официальный плеер TikTok. Сервер не получает видеопоток и не анализирует звук или кадры.",
    }


@mcp.tool()
async def inspect_tiktok_link(url: str) -> dict:
    """Get public metadata for a TikTok video link. Does not watch, download, or analyze video/audio."""
    return await get_tiktok_metadata(url)


PAGE = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TikTok Link Inspector</title>
<style>
:root{color-scheme:dark;font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:#090b12;color:#f4f5f8;display:grid;place-items:center;padding:24px}
main{width:min(100%,620px);background:#131722;border:1px solid #293044;border-radius:22px;padding:clamp(22px,5vw,38px);box-shadow:0 24px 80px #0007}
.tag{color:#8f9bb8;font-size:12px;letter-spacing:.14em;text-transform:uppercase}
h1{font-size:clamp(27px,6vw,38px);margin:12px 0}p{color:#aab3c7;line-height:1.55}
form{display:flex;gap:10px;margin:25px 0 12px;flex-wrap:wrap}
input{flex:1 1 260px;min-width:0;background:#0b0f18;color:#fff;border:1px solid #343d53;border-radius:12px;padding:15px;font-size:15px;outline:none}
input:focus{border-color:#8c79ff}button{border:0;border-radius:12px;padding:0 20px;min-height:49px;background:#8c79ff;color:#fff;font-weight:700;font-size:15px;cursor:pointer}
button:disabled{opacity:.55;cursor:wait}.hint{font-size:12px;color:#77829a}
#result{margin-top:22px}.panel{padding:17px;border-radius:14px;background:#0c111c;border:1px solid #293044;overflow-wrap:anywhere}
.label{color:#8995ae;font-size:12px;text-transform:uppercase;letter-spacing:.08em;margin-top:13px}
.value{font-size:15px;margin-top:5px}.error{color:#ff9a9a}.thumb{display:block;max-width:100%;border-radius:12px;margin-top:14px}
footer{margin-top:25px;color:#707b92;font-size:12px}
</style>
</head>
<body><main>
<div class="tag">A tiny project · public metadata</div>
<h1>TikTok Link Inspector</h1>
<p>Вставь публичную ссылку на TikTok. Сервис попробует получить название ролика, автора и превью.</p>
<form id="form"><input id="url" type="url" placeholder="https://www.tiktok.com/..." required><button id="submit">Проверить</button></form>
<div class="hint">Поддерживаются публичные ссылки TikTok. Некоторые короткие ссылки могут не распознаваться.</div>
<div id="result" aria-live="polite"></div>
<footer>Сейчас это проверка метаданных, а не просмотр или анализ самого видео.</footer>
</main>
<script>
const form=document.querySelector('#form'), input=document.querySelector('#url'), button=document.querySelector('#submit'), result=document.querySelector('#result');
function field(label,value){if(!value)return '';const wrap=document.createElement('div');const l=document.createElement('div');l.className='label';l.textContent=label;const v=document.createElement('div');v.className='value';v.textContent=value;wrap.append(l,v);return wrap}
form.addEventListener('submit',async e=>{
 e.preventDefault();button.disabled=true;button.textContent='Проверяю…';result.replaceChildren();
 const wait=document.createElement('div');wait.className='panel';wait.textContent='Запрашиваю публичные данные TikTok…';result.append(wait);
 try{
  const response=await fetch('/api/inspect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:input.value})});
  const data=await response.json();const panel=document.createElement('div');panel.className='panel';panel.replaceChildren();
  if(!response.ok||!data.ok){const err=document.createElement('div');err.className='error';err.textContent=data.error||'Не получилось проверить ссылку.';panel.append(err);if(data.hint){const hint=document.createElement('p');hint.textContent=data.hint;panel.append(hint)}}
  else{
   panel.append(field('Автор',data.author_name),field('Название',data.title));
   if(data.author_url){const a=document.createElement('a');a.href=data.author_url;a.target='_blank';a.rel='noopener noreferrer';a.textContent='Открыть профиль автора';panel.append(a)}
   if(data.embed_html){
    const match=data.embed_html.match(/src=["']([^"']+)["']/i);
    if(match){try{
     const playerUrl=new URL(match[1]);
     if(playerUrl.protocol==="https:"&&playerUrl.hostname==="www.tiktok.com"&&playerUrl.pathname.startsWith("/player/v1/")){
      const frame=document.createElement("iframe");frame.src=playerUrl.href;frame.title="TikTok video player";
      frame.allow="autoplay; encrypted-media; picture-in-picture; fullscreen";frame.allowFullscreen=true;frame.loading="lazy";
      frame.style.cssText="display:block;width:100%;aspect-ratio:9/16;max-height:620px;border:0;border-radius:12px;margin-top:16px";
      panel.append(frame);
     }
    }catch(_){}}
   }
   if(data.thumbnail_url&&!data.embed_html){const img=document.createElement('img');img.className='thumb';img.src=data.thumbnail_url;img.alt='Превью ролика';panel.append(img)}
   const note=document.createElement('p');note.textContent=data.note;panel.append(note);
  }
  result.replaceChildren(panel);
 }catch(err){const p=document.createElement('div');p.className='panel error';p.textContent='Ошибка соединения: '+err.message;result.replaceChildren(p)}
 finally{button.disabled=false;button.textContent='Проверить'}
});
</script></body></html>"""


async def homepage(request):
    return HTMLResponse(PAGE)


async def inspect_api(request):
    try:
        body = await request.json()
        url = body.get("url", "")
        data = await get_tiktok_metadata(url)
        status = 200 if data.get("ok") else 422
        return JSONResponse(data, status_code=status)
    except ValueError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)
    except Exception:
        return JSONResponse({"ok": False, "error": "Не удалось обработать запрос."}, status_code=500)


app = mcp.streamable_http_app()
app.routes.insert(0, Route("/", homepage, methods=["GET"]))
app.routes.insert(1, Route("/api/inspect", inspect_api, methods=["POST"]))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
