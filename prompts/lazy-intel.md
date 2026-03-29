[Lazy Intel Prompt — v0.0.5 — LazyUnicorn.ai]

Add an autonomous performance intelligence agent called Lazy Intel to this project. Every Monday at 6am it reads all available content analytics, YouTube performance, customer discovery signals, comment intelligence, and competitor data — generates a weekly content strategy brief — and automatically adds the best SEO keywords and GEO queries to your content queues. Your strategy writes itself.

Note: Lazy Intel uses no external APIs. It reads your existing Supabase tables from other installed Lazy agents. The more agents installed, the richer the intelligence.

---

1. Database

Create these Supabase tables with RLS enabled:

intel_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), site_url (text), niche_description (text), auto_add_keywords (boolean, default true), auto_add_geo_queries (boolean, default true), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

Note: Store SLACK_WEBHOOK_URL as Supabase secret (optional). Never store in the database.

intel_runs: id (uuid, primary key, default gen_random_uuid()), status (text — one of running, completed, failed), data_sources_read (integer, default 0), keywords_added (integer, default 0), geo_queries_added (integer, default 0), weekly_summary (text), top_performing_topic (text), started_at (timestamptz, default now()), completed_at (timestamptz), created_at (timestamptz, default now())

intel_briefs: id (uuid, primary key, default gen_random_uuid()), week_of (date), top_performing_topic (text), underserved_topics (text), recommended_seo_keywords (text), recommended_geo_queries (text), weekly_summary (text), data_sources_used (text), created_at (timestamptz, default now())

intel_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

---

2. Setup page

Create a page at /lazy-intel-setup.

Welcome message: 'Lazy Intel reads everything your agents produce — blog analytics, YouTube performance, customer call signals, comment intelligence, competitor data — and turns it into a weekly content strategy. Every Monday morning your SEO and GEO queues are already updated for the week.'

Form fields:
- Brand name (text)
- Site URL (text)
- Niche description (text) — describe your audience and content focus e.g. 'Lovable site builders and no-code founders who want to automate their business'
- Auto-add SEO keywords (toggle, default on) — automatically adds recommended keywords to seo_keywords table each week
- Auto-add GEO queries (toggle, default on) — automatically adds recommended queries to geo_queries table each week
- Slack webhook URL (password, optional) — stored as SLACK_WEBHOOK_URL secret

Submit button: Activate Lazy Intel

On submit:
1. Store SLACK_WEBHOOK_URL as Supabase secret if provided
2. Save all other values to intel_settings
3. Set setup_complete to true and prompt_version to 'v0.0.5'
3. Immediately trigger intel-analyse to run once with last 7 days of data
4. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Intel', version: '0.0.5', site_url: site_url }) }) } catch(e) {}
5. Redirect to /admin with message: 'Lazy Intel is active. Your first strategy brief is being generated. Check /admin/intel in a few minutes.'

---

3. Edge functions

intel-analyse
Cron: every Monday at 6am UTC — 0 6 * * 1
Also triggered on setup and manually from admin.

1. Read intel_settings. If is_running false or setup_complete false exit.
2. Insert into intel_runs with status running.
3. Gather all available intelligence — for each data source try the query, catch errors for non-existent tables silently, track data_sources_read count:

Blog performance: query blog_posts — count total posts, count posts per post_type in last 30 days, find the post_type with highest count (top performing agent), find any post_type with 0 posts in last 14 days despite the agent being installed (detected by settings table existing).

SEO coverage: query seo_posts — count by target_keyword pattern to find keyword clusters, find keywords added in last 7 days, count total keywords covered.

GEO coverage: query geo_posts — count by target_query pattern, find queries added in last 7 days.

YouTube performance (if youtube_videos exists): get top 5 videos by view_count, get view count trends (comparing last 14 days vs previous 14 days), note top performing video topics.

YouTube comments intelligence (if youtube_intelligence exists): fetch all rows where intel_type is question-asked and actioned is false, limit 20. These are questions your audience is asking.

Granola customer intelligence (if granola_intelligence exists): fetch all rows where intel_type is problem-mentioned or feature-requested and actioned is false, limit 20.

Crawl intelligence (if crawl_intel exists): fetch most recent 10 rows ordered by created_at descending. Competitor signals.

Perplexity research (if perplexity_research exists): fetch most recent 10 queries and topics researched.

4. Assemble all gathered data into a structured intelligence package JSON.
5. Call the built-in Lovable AI for weekly strategy synthesis:
'You are the autonomous content strategist for [brand_name] — [niche_description]. Today is Monday. Here is everything you know from last week: [intelligence package JSON]. Generate the weekly content intelligence brief. Return only a valid JSON object with these fields: top_performing_topic (string — the single topic getting most traction across all signals), underserved_topics (array of 3 strings — topics with clear demand signals but insufficient content coverage), recommended_seo_keywords (array of 5 strings — specific long-tail keyword phrases to target this week, based on questions asked and competitor gaps), recommended_geo_queries (array of 3 strings — specific questions people ask AI agents that your content should answer), weekly_summary (2 punchy sentences: first sentence what worked last week, second sentence the main opportunity for this week), data_quality_note (one sentence rating the data quality — e.g. Strong data from 6 sources or Limited data — only blog posts available). No preamble. No code fences.'
6. Parse response.
7. Insert into intel_briefs with all fields, week_of set to today's date, data_sources_used as a comma-separated list of which tables were successfully queried.
8. If auto_add_keywords is true and seo_keywords table exists: for each keyword in recommended_seo_keywords insert a row with keyword text, source set to lazy-intel, priority set to high, created_at now. Skip duplicates.
9. If auto_add_geo_queries is true and geo_queries table exists: for each query in recommended_geo_queries insert a row with query text, source set to lazy-intel, created_at now. Skip duplicates.
10. If youtube_intelligence exists and any question-asked rows were used: update those rows setting actioned to true.
11. If granola_intelligence exists and any rows were used: update those rows setting actioned to true.
12. If SLACK_WEBHOOK_URL secret is set: POST a formatted weekly brief to Slack:
'📊 *Lazy Intel Weekly Brief — [date]*
🏆 Top topic: [top_performing_topic]
🎯 Focus this week: [first underserved topic]
🔑 New keywords added: [count] (e.g. [first keyword])
🤖 New GEO queries added: [count]
📝 [weekly_summary]'
13. Update intel_runs: status completed, data_sources_read count, keywords_added count, geo_queries_added count, weekly_summary, top_performing_topic, completed_at now.
Log errors to intel_errors with function_name intel-analyse.

---

4. Admin dashboard

Do not build a standalone dashboard. Lazy Intel lives at /admin/intel as part of the unified LazyUnicorn admin panel.

The /admin/intel section shows:

This week's brief card — prominently displayed at the top. Shows the most recent intel_briefs row: week_of date, top_performing_topic in a gold badge, underserved_topics as three clickable tags (clicking adds to SEO queue), recommended keywords as a list with Add to Queue buttons, recommended GEO queries with Add to Queue buttons, weekly_summary in a large readable font, data_sources_used as small badges. A Regenerate Brief button triggers intel-analyse immediately.

Data source status panel: a grid showing all data sources Lazy Intel can read and whether each table exists in the project (green Connected / grey Not installed). Sources shown: blog_posts, seo_posts, geo_posts, youtube_videos, youtube_intelligence, granola_intelligence, crawl_intel, perplexity_research. This motivates installing more agents.

Brief history: all intel_briefs ordered by created_at descending. Last 8 rows shown as collapsed accordion cards. Each card shows week_of date and top_performing_topic as the header. Expand to see full brief details.

Run history: all intel_runs last 10 rows. Columns: started time, status badge, data sources read, keywords added, GEO queries added, duration.

Settings: niche description (editable), auto-add toggles, Slack status, is_running toggle.

Error log: intel_errors last 20 rows, collapsed by default.

---

5. Navigation

Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-intel-setup to public navigation.

## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

