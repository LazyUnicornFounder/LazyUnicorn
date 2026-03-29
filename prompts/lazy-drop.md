# lazy-drop — v0.0.6

[Lazy Drop Prompt — v0.0.6 — LazyUnicorn.ai]

Add a complete autonomous dropshipping agent called Lazy Drop to this project. It connects your Lovable site to AutoDS — giving you access to 800M+ products from 25+ global suppliers, automatic price and stock monitoring, one-click product import, and fully automated order fulfilment. Your store discovers trending products, writes their listings, monitors prices, and fulfils orders automatically. You do nothing after setup.

Note: Store all AutoDS credentials as Supabase secrets. Never store in the database.
Required secrets: AUTODS_API_KEY, AUTODS_STORE_ID

---

1. Database

Create these Supabase tables with RLS enabled:

drop_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), site_url (text), store_niche (text), target_price_min (numeric, default 10), target_price_max (numeric, default 150), target_profit_margin (numeric, default 30), preferred_suppliers (text, default 'all'), shipping_preference (text, default 'fast' — one of fast, cheapest, us-only, eu-only), products_per_discovery_run (integer, default 10), auto_import (boolean, default true), auto_fulfil (boolean, default true), price_monitoring_enabled (boolean, default true), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

drop_products: id (uuid, primary key, default gen_random_uuid()), autods_product_id (text, unique), title (text), description (text), price_cost (numeric), price_sell (numeric), profit_margin (numeric), supplier_name (text), supplier_country (text), stock_quantity (integer), shipping_days_estimated (integer), category (text), image_urls (text), status (text, default 'active' — one of active, out-of-stock, discontinued, paused), last_price_check (timestamptz), last_stock_check (timestamptz), imported_at (timestamptz, default now()), created_at (timestamptz, default now())

drop_orders: id (uuid, primary key, default gen_random_uuid()), store_order_id (text), autods_order_id (text), product_id (uuid), customer_name (text), customer_email (text), customer_address (text), quantity (integer), sale_price (numeric), cost_price (numeric), profit (numeric), status (text, default 'pending' — one of pending, processing, fulfilled, shipped, delivered, cancelled, refunded), tracking_number (text), tracking_url (text), supplier_name (text), ordered_at (timestamptz), shipped_at (timestamptz), delivered_at (timestamptz), created_at (timestamptz, default now()))

drop_price_changes: id (uuid, primary key, default gen_random_uuid()), product_id (uuid), old_cost_price (numeric), new_cost_price (numeric), old_sell_price (numeric), new_sell_price (numeric), reason (text), applied (boolean, default false), created_at (timestamptz, default now())

drop_discoveries: id (uuid, primary key, default gen_random_uuid()), run_at (timestamptz, default now()), products_found (integer), products_imported (integer), niche (text), filters_used (text), created_at (timestamptz, default now())

drop_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

---

2. Setup page

Create a page at /lazy-drop-setup.

Welcome message: 'Connect AutoDS to your Lovable store and never source, price, or fulfil a product manually again. Lazy Drop finds trending products in your niche, imports them with one click, monitors supplier prices hourly, and fulfils every order automatically.'

Prerequisites note: You need an AutoDS account. Sign up at autods.com. Connect your store in AutoDS under My Stores. Copy your API key from AutoDS Settings → API. Copy your Store ID from your AutoDS store settings.

Form fields:
- Brand name (text)
- Site URL (text)
- AutoDS API key (password) — stored as Supabase secret AUTODS_API_KEY
- AutoDS Store ID (text) — stored as Supabase secret AUTODS_STORE_ID
- Store niche (text) — describe what your store sells e.g. 'home office accessories', 'pet products', 'fitness gear'. Used to find relevant trending products.
- Target selling price range — min price (number, default $10) and max price (number, default $150). Products outside this range are skipped.
- Target profit margin (number with % sign, default 30) — minimum margin percentage to import a product.
- Preferred suppliers (select: All suppliers / US and EU only — faster shipping / AliExpress — widest selection / AutoDS warehouse — fastest fulfilment)
- Shipping preference (select: Fastest shipping / Cheapest shipping / US suppliers only / EU suppliers only)
- Products to discover per run (select: 5 / 10 / 20 / 50)
- Auto-import discovered products (toggle, default on) — if on products meeting criteria are imported automatically. If off they are queued for manual review.
- Auto-fulfil orders (toggle, default on) — if on orders are sent to AutoDS for fulfilment automatically when placed.
- Price monitoring (toggle, default on) — monitors supplier prices hourly and adjusts sell prices to maintain target margin.

Submit button: Connect AutoDS

On submit:
1. Store AUTODS_API_KEY and AUTODS_STORE_ID as Supabase secrets
2. Save all other values to drop_settings
3. Set setup_complete to true and prompt_version to 'v0.0.3'
4. Immediately call drop-test-connection to verify credentials
5. If connection succeeds immediately call drop-discover to find first products
6. Show loading: 'Connecting to AutoDS and finding your first products...'
7. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Drop', version: '0.0.6', site_url: site_url }) }) } catch(e) {}
8. Redirect to /admin with message: 'Lazy Drop is connected. Your first products are being discovered. Check back in a few minutes.'

---

3. Edge functions

drop-test-connection
Verifies AutoDS API credentials work. Called on setup and from admin dashboard.

1. Call AutoDS API: GET https://api.autods.com/v1/stores/[AUTODS_STORE_ID] with Authorization: Bearer [AUTODS_API_KEY].
2. If response is 200 and contains store data: return success with store name and plan.
3. If response is 401: return error 'Invalid API key. Check your AutoDS API key in Settings.'
4. If response is 404: return error 'Store not found. Check your AutoDS Store ID.'
5. Log errors to drop_errors with function_name drop-test-connection.

drop-discover
Cron: daily at 7am UTC — 0 7 * * *
Also triggered manually from admin and on setup.

1. Read drop_settings. If is_running is false or setup_complete is false exit.
2. Call AutoDS product research API: GET https://api.autods.com/v1/products/trending with params:
   - niche: store_niche
   - min_price: target_price_min (cost price)
   - max_price: target_price_max (cost price)
   - min_margin: target_profit_margin
   - supplier_preference: preferred_suppliers
   - shipping: shipping_preference
   - limit: products_per_discovery_run
3. For each product returned check if autods_product_id already exists in drop_products. Skip duplicates.
4. For each new product evaluate against criteria:
   - Cost price within target range: yes/no
   - Estimated profit margin meets minimum: calculate as (suggested_sell_price - cost_price) / suggested_sell_price * 100
   - Stock quantity above 10: yes/no
   - Shipping days under 14: yes/no
   Skip any product failing these checks.
5. If auto_import is true: for each qualifying product call drop-import with the AutoDS product ID.
   If auto_import is false: insert into drop_products with status 'pending-review' and do not import to store.
6. Insert a row into drop_discoveries with the run stats.
7. Log errors to drop_errors with function_name drop-discover.

drop-import
Triggered by drop-discover or manually. Accepts autods_product_id.

1. Read drop_settings.
2. Call AutoDS API to get full product details: GET https://api.autods.com/v1/products/[autods_product_id].
3. Calculate the sell price: cost_price / (1 - target_profit_margin/100) rounded to .99.
4. Call the built-in Lovable AI to write a better product description:
'You are a conversion copywriter for [brand_name] — a [store_niche] store. Write a compelling product description for: [product title]. Original description from supplier: [original description]. Make it benefit-focused, specific, and persuasive. 100 to 150 words. No bullet points. No generic filler. Start with the main benefit. End with a reason to buy today. Return only the description text. No preamble.'
5. Call AutoDS API to import the product to the store: POST https://api.autods.com/v1/products/import with:
   - store_id: AUTODS_STORE_ID
   - product_id: autods_product_id
   - selling_price: calculated sell price
   - custom_description: AI-written description
6. Insert into drop_products with all product data, the AI description, calculated sell price, and profit margin.
7. If store_products table exists from Lazy Store also insert there so the product appears in the store.
8. Log errors to drop_errors with function_name drop-import.

drop-monitor-prices
Cron: every hour — 0 * * * *

1. Read drop_settings. If is_running is false or price_monitoring_enabled is false exit.
2. Query all drop_products where status is active. Process in batches of 50.
3. For each batch call AutoDS API: GET https://api.autods.com/v1/products/prices with a list of autods_product_ids.
4. For each product where the returned cost price differs from the stored price_cost:
   - Calculate new sell price using the same margin formula
   - If new sell price is more than 10% different from current sell price insert a row into drop_price_changes
   - If auto-apply is sensible (margin still meets minimum): update the sell price in AutoDS via PATCH https://api.autods.com/v1/products/[id] with new selling_price
   - Update drop_products with new price_cost, price_sell, profit_margin, last_price_check
5. For each product where returned stock is 0: update status to out-of-stock and pause the product in AutoDS.
6. Update last_price_check and last_stock_check on all processed products.
7. Log errors to drop_errors with function_name drop-monitor-prices.

drop-fulfil-order
POST endpoint at /api/autods-fulfil. Called when a customer places an order. Accepts order details.

1. Read drop_settings. If auto_fulfil is false log the order as pending and exit.
2. Find the matching drop_products row by product ID.
3. Call AutoDS API to place the fulfilment order: POST https://api.autods.com/v1/orders with:
   - store_id: AUTODS_STORE_ID
   - product_id: autods_product_id
   - customer details from the order
   - quantity
4. Insert into drop_orders with the returned autods_order_id and status processing.
5. If Lazy SMS is installed call sms-send with an order confirmation to the customer phone number.
6. Log errors to drop_errors with function_name drop-fulfil-order.

drop-check-orders
Cron: every 2 hours — 0 */2 * * *

1. Read drop_settings. If is_running is false exit.
2. Query drop_orders where status is processing or fulfilled. For each order call AutoDS API: GET https://api.autods.com/v1/orders/[autods_order_id].
3. If status changed to shipped: update drop_orders with tracking_number, tracking_url, shipped_at, status shipped.
   If Lazy SMS is installed send a shipping notification to the customer with the tracking link.
   If Lazy Alert is installed send a Slack notification: 'Order shipped: [customer_name] — [tracking_number].'
4. If status is delivered: update status to delivered, set delivered_at.
5. If status is cancelled or failed: update status, alert via Lazy Alert if installed.
6. Log errors to drop_errors with function_name drop-check-orders.

drop-optimise
Cron: every Sunday at 2pm UTC — 0 14 * * 0

1. Read drop_settings. If is_running is false exit.
2. Query drop_products. Find the 5 products with lowest sell-through rate (ordered placed in last 30 days divided by days live). Find the 5 products with highest profit margin.
3. Call the built-in Lovable AI:
'You are an ecommerce optimiser for [brand_name] — a [store_niche] store. Here are the 5 worst-performing products by sell-through rate in the last 30 days: [list with titles, prices, margins, days live]. Here are the 5 best-performing: [list]. Recommend 3 specific improvements: should any slow products be paused and replaced? Are the prices too high? Are there supplier alternatives to check? Return only a valid JSON object: recommendations (array of 3 strings, each a specific actionable recommendation). No preamble. No code fences.'
4. Insert the recommendations as a row in a simple drop_recommendations table (id, recommendations text, created_at). Surface in the admin dashboard.
5. Log errors to drop_errors with function_name drop-optimise.

---

4. Store integration

If store_products table exists from Lazy Store: drop-import writes to both drop_products and store_products so AutoDS products appear in the existing Lovable store automatically.

If no store exists: create a public page at /shop showing all drop_products where status is active ordered by profit_margin descending. Each product card shows title, image (first image from image_urls), sell price, estimated shipping days badge. Each card links to /shop/[product-id] showing the full description and an Add to Cart button.

The Add to Cart button triggers a checkout flow using Lazy Pay (Stripe) if pay_settings table exists. On payment success call drop-fulfil-order automatically.

If neither Lazy Store nor Lazy Pay is installed show product cards with a Contact to order button that opens a mailto link.

---

5. Admin

Do not build a standalone dashboard. The Lazy Drop dashboard lives at /admin/drop as part of the unified LazyUnicorn admin panel.

If /admin does not yet exist add a placeholder at /admin pointing to /lazy-drop-setup.

The /admin/drop section shows:

Overview stats: total products imported, products active, products out of stock, orders fulfilled this month, total profit this month (sum of profit from drop_orders where status is delivered or shipped), average profit margin across active products.

Products table: all drop_products ordered by imported_at descending. Columns: image thumbnail, title, supplier badge, cost price, sell price, profit margin %, stock quantity, status badge, last price check, actions (Pause/Resume, Remove). Search by title. Filter by status and supplier.

Price changes log: all drop_price_changes ordered by created_at descending. Columns: product title, old cost, new cost, old sell price, new sell price, margin impact, applied badge. An Apply All Pending button applies all unapplied price changes.

Orders table: all drop_orders ordered by ordered_at descending. Columns: customer name, product title, quantity, sale price, cost price, profit, status badge with colour (green=delivered, blue=shipped, amber=processing, red=cancelled), tracking number with link, ordered date.

Discovery log: all drop_discoveries ordered by run_at descending. Columns: date, products found, products imported, niche, filters.

Optimisation recommendations: the latest drop_recommendations row displayed as three numbered recommendation cards in gold borders.

Controls section: Test Connection button, Discover Products Now button (triggers drop-discover), Optimise Now button, pause/resume toggle, edit settings link.

---

6. Navigation

Add a Shop link to the main site navigation pointing to /shop if no store existed before this prompt.
Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-drop-setup to public navigation.

## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

