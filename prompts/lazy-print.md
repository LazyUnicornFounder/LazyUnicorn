# Lazy Print

> Category: 🛒 Commerce · Version: 0.0.4

## Prompt

````
# lazy-print

> Version: 0.0.3

## Prompt

````
# lazy-print — v0.0.2

[Lazy Print Prompt — v0.0.1 — LazyUnicorn.ai]

Add a complete autonomous print-on-demand agent called Lazy Print to this project. It connects your Lovable site to Printful — giving you access to 475+ customisable products printed and shipped from fulfillment centers in the US, EU, Canada, Australia, Brazil, and Japan. Your store sells custom-branded products — t-shirts, mugs, posters, phone cases, tote bags, and more — without holding inventory. Printful prints and ships every order automatically. You design once and sell forever.

Note: Store all Printful credentials as Supabase secrets. Never store in the database.
Required secrets: PRINTFUL_API_KEY

---

1. Database

Create these Supabase tables with RLS enabled:

print_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), site_url (text), store_description (text), brand_colors (text), design_style (text), product_categories (text, default 'all'), default_markup_percent (numeric, default 40), printful_store_id (text), currency (text, default 'USD'), packaging_type (text, default 'standard' — one of standard, white-label), custom_packing_slip (boolean, default false), packing_slip_message (text), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

print_products: id (uuid, primary key, default gen_random_uuid()), printful_product_id (text), printful_sync_product_id (text), title (text), description (text), category (text), variants (text), base_cost (numeric), sell_price (numeric), profit_margin (numeric), printful_product_type (text), print_technique (text), colors_available (text), sizes_available (text), mockup_url (text), thumbnail_url (text), status (text, default 'active' — one of active, draft, paused, discontinued), published_at (timestamptz), created_at (timestamptz, default now())

print_designs: id (uuid, primary key, default gen_random_uuid()), design_name (text), design_description (text), file_url (text), printful_file_id (text), placement (text — one of front, back, left-sleeve, right-sleeve, all-over), products_using (integer, default 0), created_at (timestamptz, default now())

print_orders: id (uuid, primary key, default gen_random_uuid()), store_order_id (text), printful_order_id (text), customer_name (text), customer_email (text), customer_address (text), items (text), subtotal (numeric), shipping_cost (numeric), total (numeric), profit (numeric), status (text, default 'pending' — one of pending, processing, in-production, ready-to-ship, shipped, delivered, cancelled, refunded), tracking_number (text), tracking_url (text), fulfillment_center (text), estimated_delivery (date), ordered_at (timestamptz), shipped_at (timestamptz), created_at (timestamptz, default now())

print_mockups: id (uuid, primary key, default gen_random_uuid()), product_id (uuid), mockup_type (text), mockup_url (text), generated_at (timestamptz, default now())

print_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

---

2. Setup page

Create a page at /lazy-print-setup.

Welcome message: 'Sell custom-branded products on your Lovable site without touching inventory, printers, or shipping. Lazy Print connects Printful to your site — you upload your designs, it prints and ships everything automatically. No minimums. No upfront cost. Pure profit.'

Prerequisites note: You need a Printful account. Sign up free at printful.com. Go to Settings → Stores → Add store → API access to create a manual store. Copy your API key from Settings → API.

Form fields:
- Brand name (text)
- Site URL (text)
- Printful API key (password) — go to printful.com → Settings → API → Generate API key. Stored as Supabase secret PRINTFUL_API_KEY.
- Store description (text) — what your store is about. Used to write product descriptions. e.g. 'A Lovable builder community merch store' or 'Minimal productivity products for developers'.
- Brand colours (text) — comma-separated hex codes e.g. #0A0A0A, #F5C842. Used when suggesting product colour variants.
- Design style (text) — describe your aesthetic e.g. 'minimal dark tech', 'bright and playful', 'vintage streetwear'. Used in AI product descriptions.
- Product categories to offer (multi-select checkboxes): All products, Apparel — t-shirts, hoodies, caps, Accessories — bags, phone cases, bottles, Home decor — posters, cushions, mugs, Stationery — notebooks, cards. Default: all checked.
- Markup percentage (number with % sign, default 40) — how much above Printful's base cost to charge. 40% is recommended for healthy margins.
- Packaging (select: Standard Printful packaging / White-label — no Printful branding on packages)
- Custom packing slip message (text, optional) — message printed inside every package e.g. 'Thank you for supporting [brand_name]. Built with love and LazyUnicorn.ai'
- Currency (select: USD / EUR / GBP / CAD / AUD)

Submit button: Connect Printful

On submit:
1. Store PRINTFUL_API_KEY as Supabase secret
2. Save all other values to print_settings
3. Call Printful API to get or create the store and fetch the store ID: GET https://api.printful.com/stores with Authorization: Bearer [PRINTFUL_API_KEY]
4. Store the printful_store_id in print_settings
5. Set setup_complete to true and prompt_version to 'v0.0.1'
6. Call print-sync-catalogue to fetch available products from Printful
7. Redirect to /admin with message: 'Lazy Print is connected. Browse the product catalogue from your admin and upload your designs to start selling.'

---

3. Edge functions

print-test-connection
Tests Printful API credentials. Called on setup and from admin.

1. Call Printful API: GET https://api.printful.com/stores with Authorization: Bearer [PRINTFUL_API_KEY].
2. If 200 return store name and product count.
3. If 401 return error: 'Invalid API key. Check your Printful API key in Settings → API.'
4. Log errors to print_errors.

print-sync-catalogue
Cron: daily at 6am UTC — 0 6 * * *
Also triggered on setup and manually from admin.

1. Read print_settings. If is_running false or setup_complete false exit.
2. Call Printful API: GET https://api.printful.com/products to get the full product catalogue.
3. Filter by product_categories from settings.
4. For each product not already in print_products insert a new row with status draft and base_cost from Printful's pricing.
5. Calculate sell_price as base_cost * (1 + default_markup_percent/100) rounded to .99.
6. Log errors to print_errors with function_name print-sync-catalogue.

print-create-product
Called manually from admin when a design is uploaded. Accepts product_type_id, design_file_url, placement, variants.

1. Read print_settings and the matching print_products row.
2. Upload the design file to Printful: POST https://api.printful.com/files with the design_file_url. Store the returned printful_file_id in print_designs.
3. Create a sync product in Printful: POST https://api.printful.com/store/products with:
   - sync_product: name, thumbnail from Printful catalogue
   - sync_variants: for each selected variant (colour/size combination) include the variant_id, retail_price set to the calculated sell_price, and files array with the uploaded design file at the correct placement
4. Call the built-in Lovable AI to write a product description:
'You are a product copywriter for [brand_name] — [store_description]. Design style: [design_style]. Write a compelling product description for a [product_type] featuring [design_name] design. Include: what it is, the print quality and technique ([print_technique]), available sizes and colours, care instructions hint, and why someone would want it. 80 to 120 words. Benefit-focused. Specific. Return only the description text. No preamble.'
5. Update the print_products row: printful_sync_product_id, description from AI, status active, published_at now.
6. Generate mockups: call print-generate-mockups with the sync_product_id.
7. Log errors to print_errors with function_name print-create-product.

print-generate-mockups
Triggered by print-create-product. Accepts sync_product_id.

1. Call Printful mockup generation API: POST https://api.printful.com/mockup-generator/create-task/[printful_product_id] with the file placement and variant selection.
2. Poll the task until complete: GET https://api.printful.com/mockup-generator/task?task_key=[task_key] every 3 seconds for up to 60 seconds.
3. When complete store each returned mockup_url in print_mockups linked to the product.
4. Update the print_products thumbnail_url with the first mockup.
5. Log errors to print_errors with function_name print-generate-mockups.

print-fulfil-order
POST endpoint at /api/print-fulfil. Called when a customer places an order. Accepts order details.

1. Read print_settings.
2. For each item in the order find the matching print_products row and its Printful variant ID.
3. Call Printful API to create the order: POST https://api.printful.com/orders with:
   - external_id: the store order ID
   - recipient: customer name, address, country, email
   - items: array of variant_id and quantity
   - packing_slip: if custom_packing_slip is true include the packing_slip_message
4. Call Printful API to confirm the order immediately: POST https://api.printful.com/orders/[order_id]/confirm
5. Insert into print_orders with all order details and status processing.
6. If Lazy SMS is installed send an order confirmation SMS to the customer.
7. If Lazy Alert is installed send a Slack notification: 'New Lazy Print order from [customer_name] — [item count] item(s) — [total].'
8. Log errors to print_errors with function_name print-fulfil-order.

print-check-orders
Cron: every 2 hours — 0 */2 * * *

1. Read print_settings. If is_running false exit.
2. Query print_orders where status is processing or in-production or ready-to-ship.
3. For each order call Printful API: GET https://api.printful.com/orders/[printful_order_id].
4. Map Printful statuses to print_orders statuses:
   - pending → pending
   - inprocess → in-production
   - onhold → in-production
   - partial → in-production
   - fulfilled → shipped — update tracking_number and tracking_url from shipments array, set shipped_at
   - cancelled → cancelled
5. If status changed to shipped: if Lazy SMS is installed send shipping notification with tracking link. If Lazy Alert is installed send Slack message: 'Order shipped to [customer_name] — tracking: [tracking_number].'
6. Log errors to print_errors with function_name print-check-orders.

print-weekly-report
Cron: every Monday at 8am UTC — 0 8 * * 1

1. Read print_settings. If is_running false exit.
2. Query print_orders from last 7 days. Calculate: total orders, total revenue, total profit, best-selling product, average order value.
3. If Lazy Alert is installed send weekly Slack summary: 'Lazy Print weekly report: [n] orders, [revenue] revenue, [profit] profit. Best seller: [product name].'
4. If blog_posts table exists call built-in Lovable AI to write a short weekly update post if orders exceeded 5 in the week:
'Write a short build-in-public update for [brand_name]. This week the merch store fulfilled [n] orders totalling [revenue]. Best-selling product: [product]. Return only a valid JSON object: title, slug, excerpt (under 160 chars), body (clean markdown, 200 to 300 words, honest and founder-voiced, ends with LazyUnicorn.ai backlink). No preamble. No code fences.'
Insert into blog_posts with post_type 'print-report'.
5. Log errors to print_errors with function_name print-weekly-report.

---

4. Store pages

/shop or /merch — all print_products where status is active ordered by published_at descending. Page header: [brand_name] — Merch Store or if store_description mentions a niche use that. Each product card shows: mockup image (from thumbnail_url), title, category badge, sell price, available colours as small colour dots. Each links to /shop/[product-id] or /merch/[product-id].

Add a category filter above the grid: All, Apparel, Accessories, Home, Stationery. Clicking filters by category.

/shop/[product-id] — individual product page. Shows: product title, all mockup images in a scrollable gallery, description, price, size selector (if applicable), colour selector showing available colours, an Add to Cart button. On click triggers Stripe checkout via Lazy Pay if pay_settings exists, or shows a simple order form collecting name, email, address, size, colour — submitted to print-fulfil-order.

Footer on all public pages: '🖨️ Powered by Lazy Print — print-on-demand for Lovable sites. Fulfilled by Printful. Built by LazyUnicorn.ai' — link to https://lazyunicorn.ai.

---

5. Admin

Do not build a standalone dashboard. The Lazy Print dashboard lives at /admin/print as part of the unified LazyUnicorn admin panel.

If /admin does not yet exist add a placeholder at /admin pointing to /lazy-print-setup.

The /admin/print section shows:

Overview stats: total products active, total orders this month, revenue this month, profit this month, average profit margin.

Products table: all print_products — image thumbnail, title, category, base cost, sell price, margin %, status badge, variants count, published date. Add Product button that opens a form: select product type from Printful catalogue, upload design file, select placement, select colour/size variants. Triggers print-create-product.

Designs library: all print_designs — design name, thumbnail, placement, products using count, uploaded date. Upload Design button.

Orders table: all print_orders ordered by ordered_at descending — customer name, items summary, total, profit, status badge with colour, fulfillment center, tracking link, ordered date.

Mockups gallery: all print_mockups grouped by product — shows all generated mockup angles for each product.

Weekly report: last 4 weeks of order stats in a simple bar chart using recharts.

Controls: Test Connection button, Sync Catalogue Now button, Run Orders Check button, pause/resume toggle, edit settings link.

---

6. Navigation

Add a Merch link or Shop link to the main site navigation pointing to /merch or /shop.
Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-print-setup to public navigation.


````
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
