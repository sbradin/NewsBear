import { useEffect, useState, useCallback } from "react";

const API = "http://localhost:8000";

export default function App() {
  const [article, setArticle] = useState(null);
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(true);
  const [political, setPolitical] = useState(false);

  const loadNext = useCallback(async () => {
    setLoading(true);
    const r = await fetch(`${API}/label/next?labeler=local`);
    const j = await r.json();
    setDone(j.done);
    setArticle(j.article || null);
    setLoading(false);
  }, []);

  const submitLabel = useCallback(async (good_bad) => {
    if (!article) return;
    await fetch(`${API}/label`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ article_id: article.id, good_bad, labeler: "local", is_political: political })
    });
    await loadNext();
  }, [article, loadNext]);

  useEffect(() => { loadNext(); }, [loadNext]);

  const isPolitical = useCallback(async (political_bool) => {
    setPolitical(political_bool);
  }, []);

  useEffect(() => {
    const onKey = (e) => {
      if (done || loading) return;
      if (e.key === "1") submitLabel(-1);
      if (e.key === "2") submitLabel(0);
      if (e.key === "3") submitLabel(1);
      if (e.key === "s") loadNext(); // skip
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [submitLabel, loadNext, done, loading]);

  if (loading) return <div style={{ padding: 24 }}>Loading...</div>;
  if (done) return <div style={{ padding: 24 }}>No unlabeled articles left.</div>;
  if (!article) return <div style={{ padding: 24 }}>No article.</div>;

  const text = article.body_preview || article.body || "";

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

      <div style={{ display: "flex", gap: 12 }}>
        <button onClick={() => submitLabel(-1)} style={{ padding: "10px 14px" }}>Bad (-1) [1]</button>
        <button onClick={() => submitLabel(0)} style={{ padding: "10px 14px" }}>Neutral (0) [2]</button>
        <button onClick={() => submitLabel(1)} style={{ padding: "10px 14px" }}>Good (1) [3]</button>
        <button onClick={() => isPolitical(false)} style={{ padding: "10px 14px" }}>not Political</button>
        <button onClick={() => isPolitical(true)} style = {{padding: "10px 14px" }}>is Political</button>
        <button onClick={() => loadNext()} style={{ padding: "10px 14px" }}>Skip [s]</button>
      </div>
    </div>
  );
}