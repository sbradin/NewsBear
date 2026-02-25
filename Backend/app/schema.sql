CREATE TABLE IF NOT EXISTS articles (
    id BIGSERIAL PRIMARY KEY,
    uri TEXT UNIQUE NOT NULL,
    url TEXT,
    image TEXT,
    lang TEXT,
    title TEXT,
    body TEXT,
    body_preview TEXT,
    source_title TEXT,
    source_uri TEXT,
    sentiment DOUBLE PRECISION,
    published_at TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_lang ON articles(lang);
CREATE INDEX IF NOT EXISTS idx_articles_source_uri ON articles(source_uri);

CREATE TABLE IF NOT EXISTS article_labels(
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    labeler TEXT NOT NULL DEFAULT 'local',
    good_bad SMALLINT NOT NULL CHECK (good_bad in (-1,0,1)), -- -1 bad, 0 neutral, 1 good
    is_political BOOLEAN,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_labels_article_id ON article_labels(article_id);
CREATE INDEX IF NOT EXISTS idx_labels_good_bad ON article_labels(good_bad);

CREATE TABLE IF NOT EXISTS article_predictions (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    good_bad SMALLINT NOT NULL CHECK (good_bad IN (-1,0,1)),
    confidence DOUBLE PRECISION,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    features JSONB
);

CREATE INDEX IF NOT EXISTS idx_pred_article_id ON article_predictions(article_id);
CREATE INDEX IF NOT EXISTS idx_pred_model ON article_predictions(model_name, model_version);
