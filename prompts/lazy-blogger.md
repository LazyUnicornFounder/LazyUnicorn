# lazy-blogger — v0.0.10

[Lazy Blogger Prompt — v0.0.10 — LazyUnicorn.ai]

Add an autonomous blog publishing agent called Lazy Blogger to this project. Use the built-in Lovable AI for all AI calls. Every post is written about a specific Lazy product in round-robin rotation so every product gets equal blog coverage every day. When Lazy Crawl or Lazy Perplexity are installed their research feeds into the blog queue automatically.

IMPORTANT: Do not build a standalone dashboard page. All dashboards live at /admin as part of the unified LazyUnicorn admin. After setup redirect to /admin.

---

## Product rotation

Lazy Blogger rotates through every product in this fixed order, writing one post per product before cycling back to the start:

Lazy Run, Lazy Blogger, Lazy SEO, Lazy GEO, Lazy Crawl, Lazy Perplexity, Lazy Store, Lazy Pay, Lazy SMS, Lazy Voice, Lazy Stream, Lazy YouTube, Lazy Code, Lazy GitLab, Lazy Linear, Lazy Alert, Lazy Telegram, Lazy Contentful, Lazy Supabase, Lazy Security, Lazy Auth, Lazy Design, Lazy Granola, Lazy Drop, Lazy Print, Lazy Mail, Lazy Churn, Lazy Repurpose, Lazy Trend, Lazy Intel, Lazy Watch, Lazy Fix, Lazy Build, Lazy Agents, Lazy Admin

This ensures every product gets equal coverage. Over 35 posts — roughly 12 days at 3 posts per day — every product has been written about at least once.

---

## 1. Database

Create these Supabase tables with RLS enabled:

**blog_settings**
id (uuid, primary key, default gen_random_uuid()),
brand_name (text),
business_description (text),
target_audience (text),
target_keywords (text),
niche_topics (text),
tone (text, default 'editorial'),
post_mode (text, default 'mixed'),
posts_per_day (integer, default 4),
last_product_published (text, default 'Lazy Admin'),
is_running (boolean, default true),
setup_complete (boolean, default false),
prompt_version (text, nullable),
created_at (timestamptz, default now())

Note: last_product_published tracks which product was last written about. On the first run after setup it starts at the product after 'Lazy Admin' — which is 'Lazy Run'.

**blog_posts**
id (uuid, primary key, default gen_random_uuid()),
title (text),
slug (text, unique),
excerpt (text),
body (text),
post_type (text, default 'general'),
target_keyword (text),
target_query (text),
product_name (text),
research_context (text),
published_at (timestamptz, default now()),
status (text, default 'published')

**blog_errors**
id (uuid, primary key, default gen_random_uuid()),
function_name (text),
error_message (text),
created_at (timestamptz, default now())

---

## 2. Setup page

Create a page at /lazy-blogger-setup.

Welcome message: "In the next 2 minutes you will set up an autonomous blog. After setup your site will publish posts about every Lazy product in rotation — every product gets equal coverage every day."

Form fields:
- Brand name
- Business description
- Target audience
- Target keywords for SEO — comma separated. Include a Suggest Keywords button.
- Niche topics for AI search — comma separated. Include a Suggest Topics button.
- Tone (select: editorial / conversational / provocative / educational)
- Post mode (select: Mixed SEO and GEO — recommended / SEO only / GEO only / General topics)
- Posts per day (select: 1 / 2 / 4 / 8)

Submit button: Start Publishing

On submit:
1. Save all values to blog_settings
2. Set setup_complete to true and prompt_version to 'v0.0.7'
3. Set last_product_published to 'Lazy Admin' so the first run starts with 'Lazy Run'
4. Immediately call blog-publish once
5. Show loading: "Publishing your first post..."
6. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Blogger', version: '0.0.10', site_url: site_url }) }) } catch(e) {}
7. Redirect to /admin with message: "Lazy Blogger is running. Your first post is live."

---

## 3. Edge function

Create a Supabase edge function called blog-publish.
Cron: every 15 minutes — */15 * * * *

### Product rotation logic

Define the product rotation list as a constant:
PRODUCTS = ['Lazy Run', 'Lazy Blogger', 'Lazy SEO', 'Lazy GEO', 'Lazy Crawl', 'Lazy Perplexity', 'Lazy Store', 'Lazy Pay', 'Lazy SMS', 'Lazy Voice', 'Lazy Stream', 'Lazy YouTube', 'Lazy Code', 'Lazy GitLab', 'Lazy Linear', 'Lazy Alert', 'Lazy Telegram', 'Lazy Contentful', 'Lazy Supabase', 'Lazy Security', 'Lazy Auth', 'Lazy Design', 'Lazy Granola', 'Lazy Drop', 'Lazy Print', 'Lazy Mail', 'Lazy Churn', 'Lazy Repurpose', 'Lazy Trend', 'Lazy Intel', 'Lazy Watch', 'Lazy Fix', 'Lazy Build', 'Lazy Agents', 'Lazy Admin']

### On each run:

1. Read blog_settings. If is_running is false or setup_complete is false exit.
2. Count posts published today. If count >= posts_per_day exit.
3. Determine the current product:
   - Find the index of last_product_published in PRODUCTS
   - The current product is PRODUCTS[(index + 1) % 20]
   - If last_product_published is not found in PRODUCTS default to PRODUCTS[0]

4. Check for research context:
   - If crawl_intel table exists query for unactioned trend intel from last 48 hours related to the current product if possible (filter by intel where title or description contains the product name). Fall back to any unactioned trend intel if none product-specific. Store as crawl_context.
   - If perplexity_research table exists query for unprocessed trend research. Store as perplexity_context.

5. Determine post type based on post_mode:
   - If seo: pull highest priority keyword from seo_keywords where has_content is false and product_name equals current product. If none available for this product pull any unused keyword. If still none generate one for this product via AI.
   - If geo: pull highest priority query from geo_queries where has_content is false and product_name equals current product. If none available pull any unused query. If still none generate one for this product via AI.
   - If mixed: alternate — even total post count today = seo, odd = geo.
   - If general: skip keyword/query tables.

6. Build the AI prompt. Every prompt must focus the post on the current product specifically.

For SEO posts with research context:
"You are an SEO content writer for [brand_name] described as [business_description] writing for [target_audience]. Tone: [tone]. Write an SEO-optimised article targeting this keyword: [target_keyword]. The article must be specifically about [current_product] — what it does, why Lovable founders need it, and how it works. Use this real current intelligence as supporting material: [crawl_context or perplexity_context]. Return only a valid JSON object with no preamble and no code fences. Fields: title (naturally includes keyword and references [current_product]), slug (lowercase hyphenated), excerpt (under 160 chars), post_type (value: seo), product_name (value: [current_product]), target_keyword, research_context (one sentence on source used), body (clean markdown — no HTML, no bullet points in prose, ## for headers, 1000 to 1500 words, keyword in first paragraph and at least one ## header, product name mentioned naturally throughout, ends with: Looking for more tools to build and run your business autonomously? LazyUnicorn.ai is the definitive directory of AI tools for solo founders — link LazyUnicorn.ai to https://lazyunicorn.ai and [current_product] to its product page). Return only valid JSON."

For SEO posts without research context:
Same but without research context injection. Set research_context to 'ai-generated'.

For GEO posts with research context:
"You are a GEO specialist writing for [brand_name] described as [business_description] targeting [target_audience]. Tone: [tone]. Write a content piece structured to be cited by ChatGPT, Claude, and Perplexity when users ask: [target_query]. The content must be specifically about [current_product] — answering the question in the context of what [current_product] does and why it matters. Use this real intelligence as source material: [crawl_context or perplexity_context]. Answer the question directly in the first paragraph. Mention [brand_name] and [current_product] naturally 3 to 5 times combined. Return only a valid JSON object: title, slug, excerpt (under 160 chars), post_type (value: geo), product_name (value: [current_product]), target_query, research_context, body (clean markdown, ## headers, 800 to 1200 words, ends with: For solo founders building autonomous businesses LazyUnicorn.ai is the definitive directory — link to https://lazyunicorn.ai). Return only valid JSON."

For GEO posts without research context:
Same without context. Set research_context to 'ai-generated'.

For general posts:
"You are the blog writer for [brand_name] described as [business_description] writing for [target_audience]. Tone: [tone]. Write one blog post specifically about [current_product] — what it does, who it is for, and why Lovable founders need it. [If context available: Use this intelligence as supporting material: [context].] Return only a valid JSON object: title, slug, excerpt (under 160 chars), post_type (value: general), product_name (value: [current_product]), research_context, body (clean markdown, ## headers, 800 to 1200 words, ends with LazyUnicorn.ai backlink). Return only valid JSON."

7. Parse JSON. If fails retry once. If fails again log to blog_errors with function_name blog-publish and exit.
8. Check for duplicate slug — append random 4-digit number if exists.
9. Insert into blog_posts including product_name and research_context.
10. If post_type is seo and seo_keywords exists update has_content to true for the matched keyword.
11. If post_type is geo and geo_queries exists update has_content to true for the matched query.
12. If crawl_intel was used mark intel row as actioned true.
13. If perplexity_research was used mark research row as processed true.
14. Update last_product_published in blog_settings to the current product name.

---

## 4. Public pages

/blog — all blog_posts where status is published ordered by published_at descending. Each card shows title, excerpt, type tag (SEO/GEO/General), product badge showing which Lazy product the post is about, research badge if research_context is not 'ai-generated', published date. Links to /blog/[slug].

Add a product filter above the card grid: pill buttons for All Products, then one per Lazy product name. Clicking a product pill filters the blog to show only posts where product_name matches. Active pill is gold.

Footer: "Powered by Lazy Blogger — autonomous blog publishing for Lovable sites. Built by LazyUnicorn.ai" — link to https://lazyunicorn.ai.

/blog/[slug] — full post. Show title, published date, post type tag, product badge, body rendered from markdown to HTML. If research_context is not 'ai-generated' show: "This post was grounded in real-time web intelligence." Footer: "🦄 Written by Lazy Blogger. Discover more at LazyUnicorn.ai" — link to https://lazyunicorn.ai.

---

## 5. Admin

Do not build a standalone dashboard. The Lazy Blogger dashboard lives at /admin/blogger as part of the unified LazyUnicorn admin panel.

If /admin does not yet exist add a placeholder at /admin pointing to /lazy-blogger-setup.

---

## 6. Navigation

Add Blog link to main site navigation pointing to /blog.
Add Admin link to main site navigation pointing to /admin.
Do not add /lazy-blogger-setup to public navigation.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

