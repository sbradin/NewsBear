import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL:", os.getenv("DATABASE_URL"))

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL missing in .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

UPSERT_SQL = text("""
INSERT INTO articles (
  uri, url, title, body, body_preview, lang,
  source_title, source_uri, published_at, sentiment
)
VALUES (
  :uri, :url, :title, :body, :body_preview, :lang,
  :source_title, :source_uri, :published_at, :sentiment
)
ON CONFLICT (uri) DO UPDATE SET
  url = EXCLUDED.url,
  title = EXCLUDED.title,
  body = EXCLUDED.body,
  body_preview = EXCLUDED.body_preview,
  lang = EXCLUDED.lang,
  source_title = EXCLUDED.source_title,
  source_uri = EXCLUDED.source_uri,
  published_at = EXCLUDED.published_at,
  sentiment = EXCLUDED.sentiment
""")

def _preview(body: str | None, n: int = 400) -> str | None:
    if not body:
        return None
    body = " ".join(body.split())
    return body[:n]

def store_articles(article_list: list[dict]) -> int:
    """
    Accepts list of Event Registry article dicts (from GetRecentArticles.getUpdates()).
    Stores/upserts them into Postgres keyed by 'uri'.
    """
    rows = []
    for a in article_list:
        uri = a.get("uri")
        if not uri:
            continue
        if(a.get("isDuplicate")):
            continue
        
        body = a.get("body")
        rows.append({
            "uri": uri,
            "url": a.get("url"),
            "title": a.get("title"),
            "body": body,
            "body_preview": _preview(body),
            "lang": a.get("lang"),
            "source_title": (a.get("source") or {}).get("title") if isinstance(a.get("source"), dict) else a.get("sourceTitle"),
            "source_uri": (a.get("source") or {}).get("uri") if isinstance(a.get("source"), dict) else a.get("sourceUri"),
            "published_at": a.get("dateTimePub") or a.get("dateTime") or a.get("date"),
            "sentiment": a.get("sentiment") or a.get("tone"),
        })

    if not rows:
        return 0

    with engine.begin() as conn:
        for row in rows:
            conn.execute(UPSERT_SQL, row)

    return len(rows)
