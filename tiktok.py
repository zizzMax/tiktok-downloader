#!/usr/bin/env python3
"""
TikTok via tiktokio — paste a link, get everything about it.

    pip install requests
    python tiktok.py <link>

Output is one small block, nothing more:

    type      : video / photo
    pengupload: @username
    caption   : ...

    video        : <direct download link>   (best quality, no watermark)
    musik        : <direct download link>
    cover        : <direct download link>
    (photo post: foto 1, foto 2, ... + musik)

To download the best file straight to disk instead:

    python tiktok.py download <link> [output-folder]
    (video post -> the HD no-watermark file; photo post -> all images)

How it works: the link is sent to tiktokio.com's own API
(POST /api/v1/tk/html, the same call its website makes), and the
download links in its HTML answer are parsed out. The files are
served by tiktokio's servers (fr*.tiktokio.com) — including the
original-quality HD stream that TikTok's web page does not offer.
Links carry an expiry token; run again to get fresh ones.
"""
import re
import sys
from pathlib import Path

import requests

API = "https://tiktokio.com/api/v1/tk/html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://tiktokio.com/",
}


def _fetch(url: str) -> dict:
    """Send a TikTok link to tiktokio and parse its HTML answer."""
    url = url.strip()
    m = re.search(r"https?://\S+", url)
    if m:
        url = m.group(0).strip('"<>\'')
    r = requests.post(API, json={"vid": url, "prefix": "tiktokio.com"},
                      headers=HEADERS, timeout=60)
    r.raise_for_status()
    html = r.text
    if "tk-error" in html or "download" not in html:
        raise RuntimeError("tiktokio could not process this link "
                           "(post may be private, deleted, or the link is wrong).")

    title = ""
    h3 = re.search(r"<h3>(.*?)</h3>", html, re.S)
    if h3:
        title = re.sub(r"<[^>]+>", "", h3.group(1)).strip()

    links = []  # (label, url) in page order
    for href, inner in re.findall(
            r'href="([^"]*tiktokio\.com/download[^"]*)"[^>]*>(.*?)</a>',
            html, re.S):
        label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", inner)).strip()
        links.append((label, href.replace("&amp;", "&")))
    if not links:
        raise RuntimeError("No download links in tiktokio's answer.")

    author = None
    final = url
    if re.search(r"v[tm]\.tiktok\.com", url):
        try:
            final = requests.head(url, headers=HEADERS,
                                  allow_redirects=True, timeout=20).url
        except requests.RequestException:
            pass
    am = re.search(r"tiktok\.com/@([^/?#]+)", final)
    if am:
        author = am.group(1)
    im = re.search(r"/(?:video|photo)/(\d+)", final)

    images = [u for lab, u in links if lab.lower().startswith("download image")]

    def pick(prefix):
        return next((u for lab, u in links if lab.lower().startswith(prefix)), None)

    video_link = pick("download without watermark (hd)") or \
        pick("download without watermark")
    music = pick("download mp3")
    cover = None
    if not images:
        cm = re.search(r'<div class="video-info">.*?<img[^>]+src="([^"]+)"',
                       html, re.S)
        if cm:
            cover = cm.group(1).replace("&#38;", "&").replace("&amp;", "&")
    return {
        "video_link": video_link,
        "music": music,
        "cover": cover,
        "id": im.group(1) if im else None,
        "type": "photo" if images else "video",
        "author": author,
        "caption": title,
        "links": links,
        "images": images,
    }


def describe(url: str) -> str:
    """The whole output for a pasted link — only what matters."""
    d = _fetch(url)
    lines = [
        f"type      : {d['type']}",
        f"pengupload: @{d['author']}" if d["author"] else "pengupload: -",
        f"caption   : {d['caption']}",
    ]
    if d["type"] == "photo":
        lines.append(f"jumlah    : {len(d['images'])}")
    lines.append("")
    if d["type"] == "video":
        lines.append(f"{'video':<13}: {d['video_link']}")
    else:
        for i, img in enumerate(d["images"], 1):
            lines.append(f"{'foto ' + str(i):<13}: {img}")
    if d["music"]:
        lines.append(f"{'musik':<13}: {d['music']}")
    if d["cover"]:
        lines.append(f"{'cover':<13}: {d['cover']}")
    return "\n".join(lines)


def _save(media_url: str, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(media_url, headers=HEADERS, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length") or 0)
        done = 0
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if not chunk:
                    continue
                f.write(chunk)
                done += len(chunk)
                if total:
                    print(f"\r{out.name}  {done * 100 // total}% "
                          f"({done}/{total} bytes)", end="", flush=True)
        if total:
            print()
    return out


def download(url: str, outdir: str = ".") -> list:
    """Download the best file(s): HD no-watermark video, or all images."""
    d = _fetch(url)
    post_id = d["id"] or "tiktok"
    author = re.sub(r"[^A-Za-z0-9_.-]", "_", d["author"] or "tiktok")
    base = f"{post_id}_{author}"
    if d["type"] == "photo":
        folder = Path(outdir) / base
        return [_save(u, folder / f"{i:02d}.jpg")
                for i, u in enumerate(d["images"], 1)]
    if not d["video_link"]:
        raise RuntimeError("No no-watermark video link in tiktokio's answer.")
    return [_save(d["video_link"], Path(outdir) / f"{base}.mp4")]


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 1 and (args[0].startswith("http") or "tiktok.com" in args[0]):
        print(describe(args[0]))
    elif len(args) >= 2 and args[0] == "download":
        outdir = args[2] if len(args) > 2 else "."
        for p in download(args[1], outdir):
            print(f"Saved to: {p}")
    else:
        print(__doc__)
        sys.exit(1)
