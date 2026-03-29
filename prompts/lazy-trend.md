# Lazy Trend

> Category: ⚙️ Ops · Version: 0.0.3

## Prompt

````
Lazy Trend Prompt — v0.0.1 — LazyUnicorn.ai

Add an autonomous trend detection agent called Lazy Trend to this project. It monitors trending topics in your niche every 6 hours using Firecrawl and Perplexity, identifies spikes relevant to your content, adds urgent keywords to your SEO queue, queues GEO articles for immediate publication, and alerts you via Slack — so you publish on trending topics within hours, not days.

Required secrets: FIRECRAWL_API_KEY, PERPLEXITY_API_KEY. Note: These are already set if Lazy Crawl and Lazy Perplexity are installed.

---

1. Database

Create these Supabase tables with RLS enabled:

trend_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), site_url (text), niche_keywords (text), competitor_urls (text), trend_sources (text, default 'perplexity,firecrawl'), spike_threshold (integer, default 3), auto_queue_seo (boolean, default true), auto_queue_geo (boolean, default true), slack_webhook_url (text), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

trend_signals: id (uuid, primary key, default gen_random_uuid()), topic (text), signal_strength (integer — 1 to 10), signal_source (text), context (text), first_detected_at (timestamptz, default now()), seo_queued (boolean, default false), geo_queued (boolean, default false), actioned (boolean, default false), created_at (timestamptz, default now())

trend_runs: id (uuid, primary key, default gen_random_uuid()), status (text — one of running, completed, failed), signals_detected (integer, default 0), keywords_queued (integer, default 0), geo_queued (integer, default 0), summary (text), started_at (timestamptz, default now()), completed_at (timestamptz), created_at (timestamptz, default now())

trend_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
