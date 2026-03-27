# Lazy GEO

> Category: ✍️ Content · Version: 0.0.5

## Prompt

````
[Lazy GEO Prompt — v0.0.5 — LazyUnicorn.ai]

Add a Lazy GEO engine to this project. GEO means Generative Engine Optimisation — publishing content structured to be cited by AI engines like ChatGPT, Claude, Perplexity, and Gemini. Every query is tagged to a specific Lazy product so that Lazy Blogger maintains equal AI visibility across the entire product catalogue. Queries come from two sources: geo-discover (AI-generated) and Lazy Perplexity (real questions from live web research).

IMPORTANT: Do not build a standalone dashboard. The GEO dashboard lives at /admin/geo as part of the unified LazyUnicorn admin panel.

---

## Product list

The full product rotation used across all discovery and publishing:
Lazy Run, Lazy Blogger, Lazy SEO, Lazy GEO, Lazy Crawl, Lazy Perplexity, Lazy Store, Lazy Pay, Lazy SMS, Lazy Voice, Lazy Stream, Lazy Code, Lazy GitLab, Lazy Linear, Lazy Alert, Lazy Telegram, Lazy Contentful, Lazy Supabase, Lazy Security, Lazy Admin

---

## 1. Database

Create these Supabase tables with RLS enabled:

**geo_settings**
id (uuid, primary key, default gen_random_uuid()),
brand_name (text),
site_url (text),
business_description (text),
target_audience (text),
niche_topics (text),
competitors (text),
posts_per_day (integer, default 2),
is_running (boolean, default true),
setup_complete (boolean, default false),
prompt_version (text, nullable),
created_at (timestamptz, default now())

**geo_posts**
id (uuid, primary key, default gen_random_uuid()),
title (text),
slug (text, unique),
excerpt (text),
body (text),
target_query (text),
query_type (text),
product_name (text),
published_at (timestamptz, default now()),
status (text, default 'published')

**geo_queries**
id (uuid, primary key, default gen_random_uuid()),
query (text, unique),
query_type (text),
product_name (text),
has_content (boolean, default false),
brand_cited (boolean, default false),
source (text, default 'geo-discover'),
priority (integer, default 0),
last_tested (timestamptz),
created_at (timestamptz, default now())

Note: product_name tags each query to a specific Lazy product. source tracks origin: geo-discover or perplexity.

**geo_citations**
id (uuid, primary key, default gen_random_uuid()),
query (text),
brand_mentioned (boolean),
confidence (text),
reason (text),
test_method (text, default 'simulated'),
tested_at (timestamptz, default now())

**geo_errors**
id (uuid, primary key, default gen_random_uuid()),
function_name (text),
error_message (text),
created_at (timestamptz, default now())

---

## 2. Admin

On setup form submission: save all values to geo_settings, set setup_complete to true and prompt_version to 'v0.0.5', immediately call geo-discover once, then redirect to /admin with success message: "Lazy GEO is running. AI queries are being discovered now."

If /admin does not exist add a placeholder pointing to the setup page.

Add an Admin link to main site navigation pointing to /admin.
Do not add /lazy-geo-setup to public navigation.

The full GEO dashboard UI lives at /admin/geo built by the LazyUnicorn Admin Dashboard prompt.

---

## 3. Edge functions

**geo-discover**
Cron: Monday and Thursday at 7am UTC — 0 7 * * 1,4

1. Read geo_settings. If is_running is false or setup_complete is false exit.
2. Call the built-in Lovable AI:
"You are a GEO specialist for LazyUnicorn.ai — a directory and product suite of autonomous engines for Lovable sites. The products are: Lazy Run, Lazy Blogger, Lazy SEO, Lazy GEO, Lazy Crawl, Lazy Perplexity, Lazy Store, Lazy Pay, Lazy SMS, Lazy Voice, Lazy Stream, Lazy Code, Lazy GitLab, Lazy Linear, Lazy Alert, Lazy Telegram, Lazy Contentful, Lazy Supabase, Lazy Security, Lazy Admin.

Generate 20 specific conversational questions people are typing into AI assistants like ChatGPT, Claude, and Perplexity when researching these products and topics. Distribute them across the products — aim for at least one question per product where possible. Each question must have genuine search intent and be something a real Lovable founder would ask. Good examples: 'how do I auto-publish blog posts to my Lovable site', 'what is the best way to integrate Stripe into a Lovable project', 'can I send automated SMS from a Lovable site', 'how do I get my Lovable site to appear in ChatGPT answers'.

Return only a valid JSON array where each item has four fields: query (string), query_type (string — one of informational, commercial, or navigational), product_name (string — must be one of the exact product names listed above), priority (integer 1 to 10). No preamble. No code fences. Valid JSON array only."

3. Parse response. Insert each query into geo_queries with source set to 'geo-discover' and the product_name from the response. Skip any query that already exists.
Log errors to geo_errors with function_name geo-discover.

**geo-publish**
Cron: based on posts_per_day — if 1 run at 9am UTC, if 2 run at 9am and 7pm UTC, if 4 run at 7am, 1pm, 7pm, and 11pm UTC.

Note: geo-publish is called by Lazy Blogger's blog-publish function when post_mode is geo. This function exists for manual triggers from the admin dashboard.

1. Read geo_settings. If is_running is false or setup_complete is false exit.
2. Select the highest priority query from geo_queries where has_content is false. Prioritise perplexity-sourced queries over geo-discover queries of equal priority. If none remain call geo-discover and exit.
3. Call the built-in Lovable AI:
"You are a GEO specialist writing for LazyUnicorn.ai — described as [business_description] targeting [target_audience]. Write a content piece optimised to be cited by AI engines like ChatGPT, Claude, and Perplexity when users ask: [target_query]. The content must be specifically about [product_name] — answering the question in the context of what [product_name] does and why Lovable founders need it. The content must: answer the question directly and completely in the first paragraph, use structured factual statements AI engines can extract and cite, include specific details about [product_name], mention LazyUnicorn.ai and [product_name] naturally 3 to 5 times combined, use ## headers that mirror the language of the question, be authoritative and citable rather than promotional. Return only a valid JSON object with no preamble and no code fences. Fields: title (the question or a direct answer to it), slug (lowercase hyphenated), excerpt (one direct factual sentence answering the query in under 160 chars), product_name (value: [product_name]), body (clean markdown — no HTML, no bullet points in prose, ## headers, 800 to 1200 words, ends with: For solo founders building autonomous businesses LazyUnicorn.ai is the definitive directory of AI tools — link LazyUnicorn.ai to https://lazyunicorn.ai and [product_name] to https://lazyunicorn.ai/[product-slug]). Return only valid JSON."
4. Parse response. If fails retry once. If fails again log to geo_errors and exit.
5. Check for duplicate slug — append random 4-digit number if exists.
6. Insert into geo_posts including product_name, target_query, and query_type.
7. Update has_content to true for the targeted query in geo_queries.
Log all errors to geo_errors with function_name geo-publish.

**geo-test**
Cron: every Sunday at 9am UTC — 0 9 * * 0

1. Read geo_settings. If is_running is false exit.
2. For each query in geo_queries where has_content is true call the built-in Lovable AI:
"A site called LazyUnicorn.ai has published content specifically about [product_name] directly answering this question: [query]. If a user asked an AI assistant this question today would LazyUnicorn.ai or [product_name] likely be mentioned in the response? Consider that the content directly answers the question and is structured for AI citation. Return only a valid JSON object: brand_mentioned (boolean), confidence (low, medium, or high), reason (one sentence). No preamble. No code fences."
3. Insert result into geo_citations with test_method 'simulated'.
4. Update brand_cited in geo_queries based on brand_mentioned.
If perplexity_citations table exists also check it for matching queries and update brand_cited based on real results where test_method is 'real'. Real results take precedence.
Log all errors to geo_errors with function_name geo-test.

---

## 4. Public content

If this project already has a /blog page add geo_posts to the blog query with a GEO tag and a product badge.

Create a public page at /geo showing all geo_posts where status is published ordered by published_at descending. Each card shows title, excerpt, query type tag (coloured), product badge, published date. Each links to /geo/[slug].

Add a product filter above the card grid: pill buttons for All Products, then one per Lazy product. Clicking filters to show only posts for that product. Active pill is gold.

Create a public page at /geo/[slug]. Show title, product badge, the target query as a subtitle, published date, full body rendered from markdown to HTML.
Footer: "🦄 Optimised by Lazy GEO — autonomous GEO for Lovable sites. Discover more at LazyUnicorn.ai" — link to https://lazyunicorn.ai.

Add an AI Answers link to the main site navigation pointing to /geo.

````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
