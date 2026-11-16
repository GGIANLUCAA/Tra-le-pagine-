-- ArtVision Bridge public shared memory. Stored items MUST already be public.
-- Do not store conversations, login tokens, customer details or private messages here.
CREATE TABLE IF NOT EXISTS public_context (
  key TEXT PRIMARY KEY NOT NULL,
  category TEXT NOT NULL CHECK(category IN ('rules','workflow','quality','integration','costs')),
  summary TEXT NOT NULL CHECK(length(summary) <= 1300),
  source_url TEXT NOT NULL,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_public_context_category ON public_context(category);
