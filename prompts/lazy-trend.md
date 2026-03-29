[Lazy Trend Prompt — v0.0.4 — LazyUnicorn.ai]

Add an autonomous trend detection agent called Lazy Trend to this project. It monitors trending topics in your niche every 6 hours using Firecrawl and Perplexity, identifies spikes relevant to your content, adds urgent keywords to your SEO queue, queues GEO articles for immediate publication, and alerts you via Slack — so you publish on trending topics within hours, not days.

Required secrets: FIRECRAWL_API_KEY, PERPLEXITY_API_KEY. Note: These are already set if Lazy Crawl and Lazy Perplexity are installed.

---

1. Database

Create these Supabase tables with RLS enabled:

trend_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), site_url (text), niche_keywords (text), competitor_urls (text), trend_sources (text, default 'perplexity,firecrawl'), spike_threshold (integer, default 3), auto_queue_seo (boolean, default true), auto_queue_geo (boolean, default true), slack_webhook_url (text), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

trend_signals: id (uuid, primary key, default gen_random_uuid()), topic (text), signal_strength (integer — 1 to 10), signal_source (text), context (text), first_detected_at (timestamptz, default now()), seo_queued (boolean, default false), geo_queued (boolean, default false), actioned (boolean, default false), created_at (timestamptz, default now())

trend_runs: id (uuid, primary key, default gen_random_uuid()), status (text — one of running, completed, failed), signals_detected (integer, default 0), keywords_queued (integer, default 0), geo_queued (integer, default 0), summary (text), started_at (timestamptz, default now()), completed_at (timestamptz), created_at (timestamptz, default now())

trend_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

Note: Store FIRECRAWL_API_KEY and PERPLEXITY_API_KEY as Supabase secrets. Never store in the database.

---

2. Setup page

Create a page at /lazy-trend-setup.

Welcome message: 'Lazy Trend monitors trending topics in your niche every 6 hours. When it detects a spike it queues urgent SEO keywords and GEO articles, then alerts you via Slack — so you publish on trending topics within hours, not days.'

Form fields:
- Brand name (text)
- Site URL (text)
- Niche keywords (text, comma-separated) — topics to monitor
- Competitor URLs (text, comma-separated, optional) — competitor sites to track
- Trend sources (checkboxes: Perplexity, Firecrawl, both selected by default)
- Spike threshold (number, default 3) — how many mentions in 6 hours to consider trending
- Auto-queue SEO keywords (toggle, default on) — adds urgent keywords to SEO queue automatically
- Auto-queue GEO articles (toggle, default on) — queues GEO content for trending queries
- Slack webhook URL (text, optional)

Submit button: Activate Lazy Trend

On submit:
1. Save all values to trend_settings
2. Set setup_complete to true and prompt_version to 'v0.0.4'
3. Immediately trigger trend-detect to run once as a test
4. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Trend', version: '0.0.4', site_url: site_url }) }) } catch(e) {}
5. Redirect to /admin with message: 'Lazy Trend is active. It just ran its first detection cycle. Check /admin/trend for signals.'

---

3. Edge functions

trend-detect
Cron: every 6 hours — 0 */6 * * *

1. Read trend_settings. If is_running false or setup_complete false exit.
2. Insert into trend_runs with status running.
3. If Perplexity is enabled in trend_sources call Perplexity API for each niche keyword with query: "What is trending right now related to [keyword]?". Use PERPLEXITY_API_KEY secret.
4. If Firecrawl is enabled crawl competitor URLs and industry news pages using Firecrawl API with FIRECRAWL_API_KEY secret.
5. For each result call built-in Lovable AI:
'You are a trend detection analyst for [brand_name] in [niche]. Here is data from [source]: [content truncated to 2000 chars]. Identify trending topics, spikes, and urgent keywords relevant to [niche_keywords]. Assign signal strength 1 to 10 based on urgency and relevance. Return only a valid JSON array of trend signals: topic (string), signal_strength (integer 1-10), context (string — why this is trending and why it matters now). No preamble. No code fences.'
6. Parse response. For each signal insert into trend_signals if not duplicate.
7. For signals with signal_strength >= spike_threshold:
   a. If auto_queue_seo true and seo_keywords table exists: insert topic as keyword with priority high and source trend-detection.
   b. If auto_queue_geo true and geo_queries table exists: insert as query with priority high and source trend-detection.
   c. Mark seo_queued and geo_queued true on trend_signals row.
   d. If slack_webhook_url set: POST to Slack: '🔥 *Trending Now* — [topic] (strength: [signal_strength]/10). [context]. Queued for immediate publishing.'
8. Update trend_runs: status completed, signals_detected count, keywords_queued count, geo_queued count, completed_at now, summary text.
Log errors to trend_errors with function_name trend-detect.

---

4. Admin dashboard

Do not build a standalone dashboard. Lazy Trend lives at /admin/trend as part of the unified LazyUnicorn admin panel.

If /admin does not yet exist add a placeholder at /admin pointing to /lazy-trend-setup.

The /admin/trend section shows:

Status bar: last run time, next run time, total signals detected today, a Run Now button.

Active trend signals: all trend_signals from last 48 hours where actioned false ordered by signal_strength descending. Columns: topic, signal strength as visual bar (red 8-10, orange 5-7, yellow 1-4), source badge, context, detected time, queued badges showing if SEO/GEO queued, Queue Now buttons.

Trend history: all trend_runs ordered by started_at descending, last 20 rows. Columns: run time, status, signals detected, keywords queued, GEO queued.

Settings: all trend_settings fields editable, is_running toggle.

Error log: trend_errors last 20 rows, collapsed by default.

---

5. Navigation

Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-trend-setup to public navigation.

## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

