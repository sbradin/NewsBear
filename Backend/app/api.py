import os
from xmlrpc.client import boolean
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL missing")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GET_NEXT_SQL = text("""
SELECT a.id, a.uri, a.url, a.title, a.body_preview, a.body, a.lang, a.source_title, a.source_uri, a.published_at, a.sentiment
FROM articles a
LEFT JOIN article_labels l
  ON l.article_id = a.id AND l.labeler = :labeler
WHERE l.id IS NULL
ORDER BY a.published_at DESC NULLS LAST, a.ingested_at DESC
LIMIT 1;
""")

INSERT_LABEL_SQL = text("""
INSERT INTO article_labels (article_id, labeler, good_bad)
VALUES (:article_id, :labeler, :good_bad)
ON CONFLICT (article_id, labeler) DO UPDATE SET
  good_bad = EXCLUDED.good_bad,
  created_at = now();
""")

class LabelIn(BaseModel):
    article_id: int
    good_bad: int  # -1,0,1
    is_political: boolean
    labeler: str = "local"

@app.get("/label/next")
def get_next(labeler: str = "local"):
    with engine.begin() as conn:
        row = conn.execute(GET_NEXT_SQL, {"labeler": labeler}).mappings().first()
        if not row:
            return {"done": True}
        # return only one of body/body_preview depending on your preference
        return {"done": False, "article": dict(row)}

@app.post("/label")
def label_article(payload: LabelIn):
    if payload.good_bad not in (-1, 0, 1):
        raise HTTPException(status_code=400, detail="good_bad must be -1,0,1")

    with engine.begin() as conn:
        conn.execute(INSERT_LABEL_SQL, {
            "article_id": payload.article_id,
            "labeler": payload.labeler,
            "good_bad": payload.good_bad,
            "is_political": payload.is_political
        })
    return {"ok": True}