# Lazy Crawl

> Category: ✍️ Content · Version: 0.0.7

## Prompt

````
# lazy-crawl

> Version: 0.0.6

## Prompt

````
# lazy-crawl — v0.0.5

[Lazy Crawl Prompt — v0.0.5 — LazyUnicorn.ai]

Add a complete autonomous web intelligence agent called Lazy Crawl to this project. It uses the Firecrawl API to monitor competitors, track industry trends, extract leads, analyse ranking content, and automatically feed intelligence into Lazy Blogger, Lazy SEO, and Lazy Alert — all on a schedule with no manual research required after setup.

Note: Store the Firecrawl API key as Supabase secret FIRECRAWL_API_KEY. Never store in the database.

---

## 1. Database

Create these Supabase tables with RLS enabled:

**crawl_settings**
id (uuid, primary key, default gen_random_uuid()),
brand_name (text),
business_description (text),
niche (text),
site_url (text),
is_running (boolean, default true),
setup_complete (boolean, default false),
prompt_version (text, nullable),
created_at (timestamptz, default now())

**crawl_targets**
id (uuid, primary key, default gen_random_uuid()),
name (text),
url (text),
target_type (text — one of competitor, news, pricing, leads, ranking, brand-monitor),
crawl_frequency (text — one of hourly, daily, weekly),
last_crawled (timestamptz),
active (boolean, default true),
crawl_prompt (text),
created_at (timestamptz, default now())

**crawl_results**
id (uuid, primary key, default gen_random_uuid()),
target_id (uuid),
url_crawled (text),
raw_markdown (text),
extracted_data (jsonb),
summary (text),
content_type (text),
processed (boolean, default false),
crawled_at (timestamptz, default now())

**crawl_intel**
id (uuid, primary key, default gen_random_uuid()),
target_id (uuid),
intel_type (text — one of price-change, new-content, trend, lead, keyword, brand-mention),
title (text),
description (text),
data (jsonb),
actioned (boolean, default false),
alerted (boolean, default false),
created_at (timestamptz, default now())

**crawl_leads**
id (uuid, primary key, default gen_random_uuid()),
source_url (text),
name (text),
email (text),
company (text),
title (text),
description (text),
source_target_id (uuid),
qualified (boolean, default false),
created_at (timestamptz, default now())

**crawl_errors**
id (uuid, primary key, default gen_random_uuid()),
function_name (text),
error_message (text),
target_url (text),
created_at (timestamptz, default now())

---

## 2. Setup page

Create a page at /lazy-crawl-setup.

Show a welcome message: "In the next 3 minutes you will set up an autonomous web intelligence agent. After setup Lazy Crawl will monitor competitors, track trends, and feed real intelligence into your blog and SEO agents — automatically."

Form fields:
- Brand name
- Business description
- Niche or industry
- Site URL
- Firecrawl API key (password) — get at firecrawl.dev. Stored as Supabase secret FIRECRAWL_API_KEY.

Targets section: five default crawl targets as a list with toggles:
- Competitor 1 (URL input, type: competitor, frequency: weekly)
- Competitor 2 (URL input, type: competitor, frequency: weekly)
- Industry news source (URL input, type: news, frequency: daily)
- Pricing monitor (URL input, type: pricing, frequency: daily)
- Keyword research target (URL input, type: ranking, frequency: weekly)

Add Another Target button that adds a row with URL input, type select, frequency select.

Submit button: Launch Lazy Crawl

On submit:
1. Store FIRECRAWL_API_KEY as Supabase secret
2. Save core values to crawl_settings
3. Insert all enabled targets into crawl_targets
4. Set setup_complete to true and prompt_version to 'v0.0.1'
5. Immediately call crawl-run for each active target
6. Show loading: "Crawling your first targets..."
7. Redirect to /admin with message: "Lazy Crawl is running. Your first intelligence reports will appear within a few minutes."

---

## 3. Core crawl edge function

Create a Supabase edge function called crawl-run.
Cron: every 30 minutes — */30 * * * *

Handles both scheduled runs and POST requests with optional target_id.

1. Read crawl_settings. If is_running is false or setup_complete is false exit.
2. If target_id in POST body process only that target. Otherwise query crawl_targets where active is true and last_crawled exceeds its frequency threshold.
3. For each target due to crawl:
   Call Firecrawl API at https://api.firecrawl.dev/v1/scrape using FIRECRAWL_API_KEY secret.
   Body: url set to target URL, formats array containing markdown, options onlyMainContent true.
   If crawl fails log to crawl_errors and continue.
   Insert raw result into crawl_results with target_id, url_crawled, raw_markdown, crawled_at.
   Update last_crawled on crawl_targets row.
   Call crawl-extract with the crawl_result id.
Log all errors to crawl_errors with function_name crawl-run.

---

## 4. Intelligence extraction edge function

Create a Supabase edge function called crawl-extract handling POST requests with crawl_result_id.

1. Read the matching crawl_results and crawl_targets rows.
2. Read crawl_settings for brand context.
3. Call the built-in Lovable AI with a prompt tailored to the target_type:

For competitor targets:
"You are a competitive intelligence analyst for [brand_name] in the [niche] industry. You crawled this competitor page: [url_crawled]. Content: [raw_markdown truncated to 3000 chars]. Extract competitive intelligence. Look for: pricing, new features, key claims, content topics. Return only a valid JSON object: summary (string, 2-3 sentences), intel_items (array of objects each with intel_type as one of price-change, new-content, or keyword, title, description). No preamble. No code fences."

For news targets:
"You are a content research analyst for [brand_name] in the [niche] industry. You crawled this news page: [url_crawled]. Content: [raw_markdown truncated to 3000 chars]. Identify relevant trends. Return only a valid JSON object: summary (string), intel_items (array with intel_type: trend, title, description, blog_angle as a specific blog post angle). No preamble. No code fences."

For pricing targets:
"You are a pricing analyst for [brand_name]. You crawled: [url_crawled]. Content: [raw_markdown truncated to 2000 chars]. Extract all pricing. Return only a valid JSON object: summary (string), prices (array with product_name, price, currency, billing_interval, features summary), intel_items (array of observations). No preamble. No code fences."

For ranking targets:
"You are an SEO analyst for [brand_name] in [niche]. You crawled this high-ranking page: [url_crawled]. Content: [raw_markdown truncated to 3000 chars]. Return only a valid JSON object: summary (string), target_keyword (string), secondary_keywords (string array), content_structure (string), word_count_estimate (integer), intel_items (array with intel_type: keyword, title, description). No preamble. No code fences."

For leads targets:
"You are a lead extraction specialist for [brand_name] targeting [niche] customers. You crawled: [url_crawled]. Content: [raw_markdown truncated to 4000 chars]. Extract potential leads. Return only a valid JSON object: summary (string), leads (array with name, email if visible, company, title if visible, description). Only real data from the page. No preamble. No code fences."

For brand-monitor targets:
"You are a brand monitoring specialist for [brand_name] in [niche]. You crawled: [url_crawled]. Content: [raw_markdown truncated to 3000 chars]. Check for mentions of [brand_name] or competitors. Return only a valid JSON object: summary (string), brand_mentions (array with brand_mentioned, context, sentiment as positive/neutral/negative), intel_items (array with intel_type: brand-mention, title, description). No preamble. No code fences."

4. Parse JSON response. Update crawl_results with extracted_data and summary.
5. Insert each intel_item into crawl_intel.
6. For leads targets insert each lead into crawl_leads.
7. For news targets with blog_angle: insert into seo_keywords if table exists with source set to crawl and priority 8.
8. For ranking targets: insert target_keyword into seo_keywords with source crawl and priority 9. Insert secondary_keywords with priority 7.
9. For price-change intel: if alert_settings table exists call alert-send with agent Lazy Crawl, event_type price-change.
10. For brand-mention intel: if alert_settings table exists call alert-send with agent Lazy Crawl, event_type brand-mention.
11. Mark crawl_results as processed.
Log all errors to crawl_errors with function_name crawl-extract.

---

## 5. Content generation edge function

Create a Supabase edge function called crawl-publish.
Cron: daily at 6am UTC — 0 6 * * *

1. Read crawl_settings. If is_running is false exit.
2. Query crawl_intel where intel_type is trend and actioned is false ordered by created_at descending. Take top 3.
3. For each trend call the built-in Lovable AI:
"You are a blog writer for [brand_name] in the [niche] industry. Based on this industry trend: [title] — [description] — write an engaging blog post from the perspective of [brand_name]. Make it opinionated and useful. 800 to 1200 words. Return only a valid JSON object: title (string), slug (lowercase hyphenated), excerpt (under 160 chars), body (clean markdown, ## for headers, no bullet points in prose, ends with: Looking for more autonomous business tools? LazyUnicorn.ai is the definitive directory for solo founders — link to https://lazyunicorn.ai). No preamble. No code fences."
4. Check for duplicate slug — append 4-digit number if exists.
5. Insert into blog_posts if table exists.
6. Mark each processed intel row as actioned true.
Log errors to crawl_errors with function_name crawl-publish.

---

## 6. Public pages

Create a public page at /intelligence showing recent crawl_intel that is not sensitive. Show trending topics, brand mentions with positive sentiment, and industry trends. A live intelligence feed for your niche. Each item shows intel type tag, title, description, and time.

At the bottom add: "🦄 Powered by Lazy Crawl — autonomous web intelligence for Lovable sites. Built by LazyUnicorn.ai" — link to https://lazyunicorn.ai.

---

## 7. Admin

Do not build a standalone dashboard page for this agent. The dashboard lives at /admin/crawl as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt. This agent only needs its setup page, database tables, edge functions, and public pages.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all agents in one place." and a link to /lazy-crawl-setup.

## 8. Navigation

Add an Intelligence link to main navigation pointing to /intelligence.
Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-crawl-setup to public navigation.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

````
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
