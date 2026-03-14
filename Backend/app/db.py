import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import re

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



_BOILER_PATTERNS = [
    r"by clicking (submit|sign up|continue)\b",
    r"\bprivacy policy\b",
    r"\bcookies?\b",
    r"\bterms of (service|use)\b",
    r"\bmarketing purposes\b",
    r"\bcross-context\b",
    r"\badvertising\b",
    r"\bsubscribe\b",
    r"\bsign up\b",
    r"\bnewsletter\b",
    r"\ball rights reserved\b",
]

_boiler_re = re.compile("|".join(_BOILER_PATTERNS), re.IGNORECASE)

def clean_body(text: str | None) -> str | None:
    if not text:
        return None
    # normalize whitespace but keep paragraph boundaries
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    paras = [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]

    # drop leading boilerplate paragraphs (only at the start)
    out = []
    dropping = True
    for p in paras:
        if dropping and (_boiler_re.search(p) or len(p) < 40):
            continue
        dropping = False
        out.append(p)

    cleaned = "\n\n".join(out).strip()
    return cleaned if cleaned else None

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
        
        raw_body = a.get("body")
        body = clean_body(raw_body)
        rows.append({
            "uri": uri,
            "url": a.get("url"),
            "title": a.get("title"),
            "body": body,
            "body_preview": _preview(body),
            "body_raw": raw_body,
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
