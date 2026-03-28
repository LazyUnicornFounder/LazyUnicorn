# Lazy SEO

> Category: ✍️ Content · Version: 0.0.6

## Prompt

````
# lazy-seo — v0.0.5

[Lazy SEO Prompt — v0.0.5 — LazyUnicorn.ai]

Add a Lazy SEO engine to this project. It automatically discovers keyword opportunities tagged to specific Lazy products and fills a queue that Lazy Blogger publishes from. Keywords come from three sources: seo-discover (AI-generated), Lazy Crawl (competitor intelligence), and Lazy Perplexity (live web research). Every keyword is tagged to a specific product so Lazy Blogger can maintain equal coverage across the entire catalogue.

IMPORTANT: Do not build a standalone dashboard. The SEO dashboard lives at /admin/seo as part of the unified LazyUnicorn admin panel.

---

## Product list

The full product rotation used across all discovery and publishing:
Lazy Run, Lazy Blogger, Lazy SEO, Lazy GEO, Lazy Crawl, Lazy Perplexity, Lazy Store, Lazy Pay, Lazy SMS, Lazy Voice, Lazy Stream, Lazy Code, Lazy GitLab, Lazy Linear, Lazy Alert, Lazy Telegram, Lazy Contentful, Lazy Supabase, Lazy Security, Lazy Admin

---

## 1. Database

Create these Supabase tables with RLS enabled:

**seo_settings**
id (uuid, primary key, default gen_random_uuid()),
site_url (text),
business_description (text),
target_keywords (text),
competitors (text),
posts_per_day (integer, default 2),
is_running (boolean, default true),
setup_complete (boolean, default false),
prompt_version (text, nullable),
created_at (timestamptz, default now())

**seo_posts**
id (uuid, primary key, default gen_random_uuid()),
title (text),
slug (text, unique),
excerpt (text),
body (text),
target_keyword (text),
product_name (text),
published_at (timestamptz, default now()),
status (text, default 'published')

**seo_keywords**
id (uuid, primary key, default gen_random_uuid()),
keyword (text, unique),
product_name (text),
has_content (boolean, default false),
priority (integer, default 0),
source (text, default 'seo-discover'),
created_at (timestamptz, default now())

Note: product_name tags each keyword to a specific Lazy product. source tracks which engine discovered it: seo-discover, crawl, or perplexity.

**seo_errors**
id (uuid, primary key, default gen_random_uuid()),
function_name (text),
error_message (text),
created_at (timestamptz, default now())

---

## 2. Admin

On setup form submission: save all values to seo_settings, set setup_complete to true and prompt_version to 'v0.0.5', immediately call seo-discover once, then redirect to /admin with success message: "Lazy SEO is running. Keywords are being discovered now."

If /admin does not exist add a placeholder pointing to the setup page.

Add an Admin link to main site navigation pointing to /admin.
Do not add /lazy-seo-setup to public navigation.

The full SEO dashboard UI — keyword queue with source and product tags, post history, inline settings — lives at /admin/seo built by the LazyUnicorn Admin Dashboard prompt.

---

## 3. Edge functions

**seo-discover**
Cron: every Monday at 6am UTC — 0 6 * * 1

1. Read seo_settings. If is_running is false or setup_complete is false exit.
2. Call the built-in Lovable AI:
"You are an SEO strategist for LazyUnicorn.ai — a directory and product suite of autonomous engines for Lovable sites. The products are: Lazy Run, Lazy Blogger, Lazy SEO, Lazy GEO, Lazy Crawl, Lazy Perplexity, Lazy Store, Lazy Pay, Lazy SMS, Lazy Voice, Lazy Stream, Lazy Code, Lazy GitLab, Lazy Linear, Lazy Alert, Lazy Telegram, Lazy Contentful, Lazy Supabase, Lazy Security, Lazy Admin.

Generate 20 specific long-tail keyword phrases this site should rank for on Google. Distribute them across the products — aim for at least one keyword per product where possible, with higher-traffic products getting more keywords. Each keyword must have clear search intent and be specific enough for a focused 1000-word article. Good examples: 'lazy seo for lovable sites', 'autonomous stripe integration lovable', 'auto blog publishing lovable project', 'twilio sms automation lovable', 'elevenlabs narration lovable blog'.

Return only a valid JSON array where each item has three fields: keyword (string), product_name (string — must be one of the exact product names listed above), priority (integer 1 to 10). No preamble. No code fences. Valid JSON array only."

3. Parse response. Insert each keyword into seo_keywords with source set to 'seo-discover' and the product_name from the response. Skip any keyword that already exists by matching the keyword text.
Log errors to seo_errors with function_name seo-discover.

**seo-publish**
Cron: based on posts_per_day — if 1 run at 8am UTC, if 2 run at 8am and 6pm UTC, if 4 run at 6am, 12pm, 6pm, and 11pm UTC.

Note: seo-publish is called by Lazy Blogger's blog-publish function when post_mode is seo. It does not publish independently — it serves as a keyword queue that Lazy Blogger draws from. This function exists for manual triggers from the admin dashboard.

1. Read seo_settings. If is_running is false or setup_complete is false exit.
2. Select the highest priority keyword from seo_keywords where has_content is false. Prioritise by source in this order: crawl first (highest real-world relevance), perplexity second (current web data), seo-discover third (AI-generated). Within each source group sort by priority score descending. If no keywords remain call seo-discover and exit.
3. Call the built-in Lovable AI:
"You are an SEO content writer for LazyUnicorn.ai — a site described as [business_description]. Write an SEO-optimised article targeting this exact keyword: [target_keyword]. The article must be specifically about [product_name] — what it does, who it is for, and why Lovable founders need it. Return only a valid JSON object with no preamble and no code fences. Fields: title (naturally includes keyword), slug (lowercase hyphenated), excerpt (one sentence under 160 chars naturally including keyword), product_name (value: [product_name]), body (clean markdown — no HTML, no bullet points in prose, ## for headers, 1000 to 1500 words, keyword in first paragraph and at least one ## header, keyword density 1 to 2 percent, product name mentioned naturally throughout, ends with: Looking for more autonomous business tools? LazyUnicorn.ai is the definitive directory for solo founders — link LazyUnicorn.ai to https://lazyunicorn.ai and [product_name] to https://lazyunicorn.ai/[product-slug]). Return only valid JSON."
4. Parse response. If fails retry once. If fails again log to seo_errors and exit.
5. Check for duplicate slug — append random 4-digit number if exists.
6. Insert into seo_posts including product_name.
7. Update has_content to true for the targeted keyword.
Log all errors to seo_errors with function_name seo-publish.

---

## 4. Public blog

If this project already has a /blog page add seo_posts to the existing blog query so SEO posts appear alongside any existing posts ordered by published_at descending.

If no /blog page exists create one at /blog showing all seo_posts where status is published ordered by published_at descending. Each card shows title, excerpt, SEO tag, product badge, published date. Each links to /blog/[slug].

Create a public page at /blog/[slug] if one does not already exist. Check blog_posts, seo_posts, and geo_posts for the matching slug. Render with title, published date, product badge, body as formatted HTML.
Footer: "🦄 Optimised by Lazy SEO — autonomous SEO for Lovable sites. Discover more at LazyUnicorn.ai" — link to https://lazyunicorn.ai.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
