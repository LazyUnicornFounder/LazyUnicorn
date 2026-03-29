# Lazy Store

> Category: 🛒 Commerce · Version: 0.0.8

## Prompt

````
# lazy-store

> Version: 0.0.8

## Prompt

````
# lazy-store — v0.0.8

[Lazy Store Prompt — v0.0.8 — LazyUnicorn.ai]

Add an autonomous e-commerce agent called Lazy Store to this project. It automatically discovers products, writes listings, monitors pricing, runs promotions, optimises conversion, and publishes SEO content — with no manual input required after setup. Payments are handled by Stripe checkout. All management pages are admin-only.

---

## 1. Database

Create these Supabase tables with RLS enabled:

**store_settings**
id (uuid, primary key, default gen_random_uuid()),
brand_name (text),
business_description (text),
niche (text),
target_audience (text),
store_model (text),
brand_voice (text),
currency (text, default 'USD'),
price_range_min (integer),
price_range_max (integer),
site_url (text),
is_running (boolean, default true),
setup_complete (boolean, default false),
prompt_version (text, nullable),
created_at (timestamptz, default now())

Note: Store Stripe keys as Supabase secrets — STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY. Never store in database.

**store_products**
id (uuid, primary key, default gen_random_uuid()),
name (text),
slug (text, unique),
description (text),
excerpt (text),
price (numeric),
compare_at_price (numeric),
category (text),
tags (text),
source_url (text),
affiliate_url (text),
stripe_price_id (text),
stripe_product_id (text),
status (text, default 'published'),
views (integer, default 0),
sales (integer, default 0),
conversion_rate (numeric, default 0),
last_optimised (timestamptz),
created_at (timestamptz, default now())

**store_promotions**
id (uuid, primary key, default gen_random_uuid()),
product_id (uuid),
promotion_type (text),
discount_percent (integer),
start_date (timestamptz),
end_date (timestamptz),
active (boolean, default true),
created_at (timestamptz, default now())

**store_content**
id (uuid, primary key, default gen_random_uuid()),
title (text),
slug (text, unique),
excerpt (text),
body (text),
content_type (text),
target_keyword (text),
published_at (timestamptz, default now()),
status (text, default 'published')

**store_errors**
id (uuid, primary key, default gen_random_uuid()),
function_name (text),
error_message (text),
created_at (timestamptz, default now())

---

## 2. Setup page

Create a page at /lazy-store-setup with a welcome message:
"In the next 2 minutes you will set up an autonomous store. After setup your store will discover products, write listings, set prices, and publish buying guides — automatically."

Form fields:
- Brand name
- Store niche (what products or category does this store focus on?)
- Target audience (who are your ideal customers?)
- Store model (select: Affiliate — earn commission on every sale, no inventory / Digital Products — AI generates and sells digital products, zero fulfilment / Physical / Dropshipping — list physical products, connect your own fulfilment)
- Brand voice (select: Professional / Friendly / Minimal / Bold)
- Target price range minimum ($)
- Target price range maximum ($)
- Currency (select: USD / GBP / EUR / AUD)
- Site URL
- Stripe Publishable Key (text) — stored as Supabase secret STRIPE_PUBLISHABLE_KEY
- Stripe Secret Key (password) — stored as Supabase secret STRIPE_SECRET_KEY

Submit button: Launch My Store

On submit:
1. Store Stripe keys as Supabase secrets
2. Save all other values to store_settings
3. Set setup_complete to true and prompt_version to 'v0.0.5'
4. Immediately call store-discover once
5. Show loading: "Discovering products for your store..."
6. Redirect to /admin with message: "Your store is live. Products are being discovered and listed automatically."

---

## 3. Autonomous edge functions

**store-discover**
Cron: daily at 7am UTC — 0 7 * * *

1. Read store_settings. If is_running is false or setup_complete is false exit.
2. Call the built-in Lovable AI:
"You are a product research specialist for a [store_model] store in the niche [niche] targeting [target_audience] with a price range of [price_range_min] to [price_range_max] [currency]. Identify 5 trending products this store should be selling. Return only a valid JSON array where each item has: name (string), category (string), suggested_price (number), affiliate_url (string — a plausible product search URL, or empty string if not applicable), reason (string — one sentence why this is trending). No preamble. No code fences. Valid JSON array only."
3. For each product call store-listings to generate the listing.
Log errors to store_errors with function_name store-discover.

**store-listings**
Cron: every 2 hours — 0 */2 * * *

1. Read store_settings. If is_running is false exit.
2. Find all store_products where description is null or empty.
3. For each product call the built-in Lovable AI:
"You are a product copywriter for [brand_name] in [brand_voice] voice. Write a compelling listing for this product in the [niche] niche for [target_audience]. Product name: [name]. Category: [category]. Price: [price] [currency]. Return only a valid JSON object: description (string, 100 to 150 words), excerpt (string, one punchy sentence under 160 characters), slug (lowercase hyphenated string). No preamble. No code fences."
4. Update the product with the generated description, excerpt, and slug.
5. If Stripe keys exist create the product in Stripe and store stripe_product_id and stripe_price_id.
Log errors to store_errors with function_name store-listings.

**store-prices**
Cron: daily at 9am UTC — 0 9 * * *

1. Read store_settings. If is_running is false exit.
2. For all published products call the built-in Lovable AI:
"You are a pricing strategist for a [store_model] store in the [niche] niche targeting [target_audience]. Price range: [price_range_min] to [price_range_max] [currency]. Review these products and suggest competitive prices: [list of product names and current prices]. Return only a valid JSON array where each item has: product_id (string), suggested_price (number), compare_at_price (number — the original price to show as crossed out, must be higher than suggested_price). No preamble. No code fences."
3. Update price and compare_at_price in store_products where the suggested price differs by more than 5%.
Log errors to store_errors with function_name store-prices.

**store-promote**
Cron: every Monday at 8am UTC — 0 8 * * 1

1. Read store_settings. If is_running is false exit.
2. Query store_products where status is published and sales < 2 and created_at is older than 7 days.
3. Call the built-in Lovable AI:
"You are a promotions manager for [brand_name] selling [niche] products. These products are underperforming: [list of product names]. Suggest a promotion for each. Return only a valid JSON array where each item has: product_id (string), promotion_type (string — flash-sale, bundle-deal, or limited-time), discount_percent (integer 10 to 40), duration_days (integer). No preamble. No code fences."
4. Insert promotions into store_promotions with active true and calculated end_date.
Log errors to store_errors with function_name store-promote.

**store-optimise**
Cron: every Sunday at 10am UTC — 0 10 * * 0

1. Read store_settings. If is_running is false exit.
2. Query store_products where views > 20 and conversion_rate < 2 and (last_optimised is null or older than 14 days).
3. For each underperforming product call the built-in Lovable AI:
"You are a conversion rate specialist for [brand_name] in [brand_voice] voice. This product page has a [conversion_rate]% conversion rate from [views] views. Rewrite the description to be more compelling. Product: [name]. Current description: [description]. Target audience: [target_audience]. Return only a valid JSON object with two fields: description (string, 100 to 150 words) and excerpt (string, under 160 characters). No preamble. No code fences."
4. Update description and excerpt in store_products.
5. If stripe_product_id exists update the product description in Stripe.
6. Set last_optimised to now.
Log errors to store_errors with function_name store-optimise.

**store-content**
Cron: Tuesday and Friday at 8am UTC — 0 8 * * 2,5

1. Read store_settings. If is_running is false exit.
2. Call the built-in Lovable AI:
"You are an SEO content writer for [brand_name] selling [niche] products to [target_audience]. Write one piece of SEO content that attracts shoppers before they are ready to buy. Choose from: a buying guide, a product comparison, or a product review. Pick a fresh angle every time. Return only a valid JSON object: title (string), slug (lowercase hyphenated), excerpt (one sentence under 160 characters), content_type (string — buying-guide, comparison, or review), target_keyword (string), body (clean markdown — no HTML, no bullet points in prose, ## for headers, 800 to 1200 words, ends with a CTA linking to /store, then exactly: Discover more autonomous business tools at LazyUnicorn.ai — link LazyUnicorn.ai to https://lazyunicorn.ai). No preamble. No code fences."
3. Check for duplicate slug — append random 4-digit number if exists.
4. Insert into store_content.
Log errors to store_errors with function_name store-content.

---

## 4. Checkout edge function

**store-checkout** — handles POST requests
- Accept product_id (uuid) and customer_email (text)
- Read matching product from store_products, increment views
- Read STRIPE_SECRET_KEY from Supabase secrets
- Create Stripe checkout session using stripe_price_id with mode payment
- Set success_url to site_url/store/success, cancel_url to site_url/store
- Return checkout URL
- Log errors to store_errors with function_name store-checkout

---

## 5. Public pages

**/store**
Show all store_products where status is published ordered by created_at descending. Grid layout. Each card shows name, excerpt, formatted price. If an active promotion exists in store_promotions show compare_at_price crossed out and the discounted price with a badge. Each card links to /store/[slug].

**/store/[slug]**
Show full product: name, description, price, promotion badge if active, and a Buy Now button. On click show email input modal then call store-checkout and redirect to Stripe checkout URL. Track page views by incrementing views on each visit. At the bottom add: "🦄 Powered by Lazy Store — autonomous e-commerce for Lovable sites. Built by LazyUnicorn.ai" — link to https://lazyunicorn.ai.

**/store/guides**
Show all store_content where status is published ordered by published_at descending. Each shows title, content_type tag, target_keyword, published date. Each links to /store/guides/[slug].

**/store/guides/[slug]**
Show full content with title, content type, published date, full body rendered from markdown to HTML.

**/store/success**
Show payment success message and link to /store.

---

## 6. Admin

Do not build a standalone dashboard page for this agent. The dashboard lives at /admin/store as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt. This agent only needs its setup page, database tables, edge functions, and public pages.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all agents in one place." and a link to /lazy-store-setup.

## 7. Navigation

Add a Shop link to the main site navigation pointing to /store.
Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-store-setup to public navigation.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

````
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
