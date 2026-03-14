import { useEffect, useState, useCallback } from "react";

const API = "http://localhost:8000";

export default function App() {
  const [article, setArticle] = useState(null);
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(true);

  const [goodBad, setGoodBad] = useState(null);     // -1 | 0 | 1 | null
  const [political, setPolitical] = useState(false);

  const loadNext = useCallback(async () => {
    setLoading(true);
    const r = await fetch(`${API}/label/next?labeler=local`);
    const j = await r.json();
    setDone(j.done);
    setArticle(j.article || null);
    setLoading(false);

    // reset selections for next article
    setGoodBad(null);
    setPolitical(false);
  }, []);

  const submit = useCallback(async () => {
    if (!article) return;
    if (goodBad === null) return;

    await fetch(`${API}/label`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        article_id: article.id,
        good_bad: goodBad,
        is_political: political,
        labeler: "local",
      }),
    });

    await loadNext();
  }, [article, goodBad, political, loadNext]);

  useEffect(() => { loadNext(); }, [loadNext]);

  useEffect(() => {
    const onKey = (e) => {
      if (done || loading) return;
      if (e.key === "1") setGoodBad(-1);
      if (e.key === "2") setGoodBad(0);
      if (e.key === "3") setGoodBad(1);
      if (e.key.toLowerCase() === "p") setPolitical((v) => !v);
      if (e.key === "Enter") submit();
      if (e.key.toLowerCase() === "s") loadNext();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [submit, loadNext, done, loading]);

  if (loading) return <div style={{ padding: 24 }}>Loading...</div>;
  if (done) return <div style={{ padding: 24 }}>No unlabeled articles left.</div>;
  if (!article) return <div style={{ padding: 24 }}>No article.</div>;

  const text = article.body_preview || article.body || "";

  const btn = (active) => ({
    padding: "10px 14px",
    border: active ? "2px solid black" : "1px solid #ccc",
    fontWeight: active ? 700 : 400,
  });

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 24, fontFamily: "system-ui" }}>
      <h2 style={{ marginBottom: 8 }}>{article.title}</h2>
      <div style={{ opacity: 0.7, marginBottom: 16 }}>
        {article.source_title || article.source_uri || "Unknown source"} • {article.published_at || "No date"} • {article.lang || ""}
      </div>

      <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.5, marginBottom: 16 }}>
        {text}
      </div>

      {article.url && (
        <div style={{ marginBottom: 16 }}>
          <a href={article.url} target="_blank" rel="noreferrer">Open original</a>
        </div>
      )}

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <button onClick={() => setGoodBad(-1)} style={btn(goodBad === -1)}>Bad (-1) [1]</button>
        <button onClick={() => setGoodBad(0)} style={btn(goodBad === 0)}>Neutral (0) [2]</button>
        <button onClick={() => setGoodBad(1)} style={btn(goodBad === 1)}>Good (1) [3]</button>

        <button onClick={() => setPolitical((v) => !v)} style={btn(political)}>
          Political [p]: {political ? "Yes" : "No"}
        </button>

        <button onClick={submit} style={{ padding: "10px 14px" }}>
          Submit [Enter]
        </button>

        <button onClick={loadNext} style={{ padding: "10px 14px" }}>Skip [s]</button>
      </div>
    </div>
  );
}