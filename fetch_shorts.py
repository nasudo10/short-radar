"""
Radar de Shorts Virais - YouTube Data API v3
----------------------------------------------
Busca Shorts (videos <=60s) publicados nas ultimas 48h, em ingles e
espanhol, e ranqueia pela VELOCIDADE de visualizacoes (views / horas
desde a publicacao) -- assim pega o que esta bombando AGORA, e nao
so os canais que ja sao grandes.

Uso:
    export YOUTUBE_API_KEY="sua_chave_aqui"
    python fetch_shorts.py

Gera: data/data.json (consumido pelo dashboard index.html)
"""

import os
import re
import json
import datetime
import requests

API_KEY = os.environ.get("YOUTUBE_API_KEY")
if not API_KEY:
    raise SystemExit("Defina a variavel de ambiente YOUTUBE_API_KEY antes de rodar.")

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

LANGUAGES = ["en", "es"]          # ingles e espanhol
HOURS_WINDOW = 48                 # janela de tempo
MAX_RESULTS_PER_LANG = 50         # maximo permitido por chamada de busca
TOP_N = 30                        # quantos videos entregar no final
MIN_VIEWS = 20000                 # ignora ruido / videos com poucas views


def iso_duration_to_seconds(duration: str) -> int:
    """Converte duracao ISO 8601 (ex: PT45S, PT1M5S) para segundos."""
    match = re.match(
        r"PT(?:(?P<h>\d+)H)?(?:(?P<m>\d+)M)?(?:(?P<s>\d+)S)?", duration
    )
    if not match:
        return 0
    parts = match.groupdict()
    h = int(parts["h"] or 0)
    m = int(parts["m"] or 0)
    s = int(parts["s"] or 0)
    return h * 3600 + m * 60 + s


def search_video_ids(language: str, published_after: str) -> list:
    ids = []
    params = {
        "part": "id",
        "type": "video",
        "order": "viewCount",
        "publishedAfter": published_after,
        "relevanceLanguage": language,
        "videoDuration": "short",   # <4min (filtramos <=60s depois)
        "maxResults": MAX_RESULTS_PER_LANG,
        "key": API_KEY,
    }
    resp = requests.get(SEARCH_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    for item in data.get("items", []):
        vid = item.get("id", {}).get("videoId")
        if vid:
            ids.append(vid)
    return ids


def fetch_video_details(video_ids: list) -> list:
    """Busca estatisticas + duracao em lotes de 50 (limite da API)."""
    details = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(batch),
            "key": API_KEY,
        }
        resp = requests.get(VIDEOS_URL, params=params, timeout=30)
        resp.raise_for_status()
        details.extend(resp.json().get("items", []))
    return details


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    published_after = (now - datetime.timedelta(hours=HOURS_WINDOW)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    all_ids = set()
    for lang in LANGUAGES:
        ids = search_video_ids(lang, published_after)
        all_ids.update(ids)
        print(f"[{lang}] {len(ids)} candidatos encontrados")

    raw_details = fetch_video_details(list(all_ids))
    print(f"Detalhes obtidos para {len(raw_details)} videos")

    results = []
    for item in raw_details:
        duration_s = iso_duration_to_seconds(item["contentDetails"]["duration"])
        if duration_s > 60:
            continue  # nao e um Short de verdade

        stats = item.get("statistics", {})
        views = int(stats.get("viewCount", 0))
        if views < MIN_VIEWS:
            continue

        published_at = item["snippet"]["publishedAt"]
        published_dt = datetime.datetime.strptime(
            published_at, "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=datetime.timezone.utc)
        hours_since_publish = max(
            (now - published_dt).total_seconds() / 3600, 0.5
        )
        velocity = views / hours_since_publish  # views por hora

        results.append({
            "id": item["id"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "publishedAt": published_at,
            "hoursSincePublish": round(hours_since_publish, 1),
            "views": views,
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "durationSeconds": duration_s,
            "velocity": round(velocity),
            "thumbnail": item["snippet"]["thumbnails"].get("high", {}).get(
                "url", item["snippet"]["thumbnails"]["default"]["url"]
            ),
            "url": f"https://www.youtube.com/shorts/{item['id']}",
        })

    results.sort(key=lambda x: x["velocity"], reverse=True)
    top_results = results[:TOP_N]

    output = {
        "generatedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "windowHours": HOURS_WINDOW,
        "count": len(top_results),
        "videos": top_results,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"OK - {len(top_results)} videos salvos em data/data.json")


if __name__ == "__main__":
    main()
