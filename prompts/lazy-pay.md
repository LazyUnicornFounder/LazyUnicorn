# Lazy Pay

> Category: 🛒 Commerce · Version: 0.0.5

## Prompt

````
# lazy-pay — v0.0.4

[Lazy Pay Prompt — v0.0.4 — LazyUnicorn.ai]

Add a complete self-improving Stripe payments engine called Lazy Pay to this project. It installs one-time payments, subscriptions, webhook handling, a customer portal, confirmation emails, a revenue dashboard, autonomous conversion optimisation, and abandoned checkout recovery — with no manual Stripe integration required after setup.

---

## 1. Database

Create these Supabase tables with RLS enabled:

**pay_settings**
id (uuid, primary key, default gen_random_uuid()),
business_name (text),
support_email (text),
site_url (text),
currency (text, default 'usd'),
is_running (boolean, default true),
setup_complete (boolean, default false),
prompt_version (text, nullable),
created_at (timestamptz, default now())

Note: Store Stripe keys as Supabase secrets — STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET. Never store them in the database table.

**pay_products**
id (uuid, primary key, default gen_random_uuid()),
name (text),
description (text),
price_cents (integer),
billing_type (text),
billing_interval (text, nullable),
stripe_price_id (text),
stripe_product_id (text),
active (boolean, default true),
views (integer, default 0),
last_optimised (timestamptz),
created_at (timestamptz, default now())

**pay_customers**
id (uuid, primary key, default gen_random_uuid()),
email (text, unique),
stripe_customer_id (text, unique),
name (text),
created_at (timestamptz, default now())

**pay_transactions**
id (uuid, primary key, default gen_random_uuid()),
customer_id (uuid),
product_id (uuid),
stripe_session_id (text),
amount_cents (integer),
currency (text),
status (text),
billing_type (text),
created_at (timestamptz, default now())

**pay_subscriptions**
id (uuid, primary key, default gen_random_uuid()),
customer_id (uuid),
product_id (uuid),
stripe_subscription_id (text, unique),
status (text),
current_period_start (timestamptz),
current_period_end (timestamptz),
cancel_at_period_end (boolean, default false),
created_at (timestamptz, default now())

**pay_abandoned**
id (uuid, primary key, default gen_random_uuid()),
customer_email (text),
product_id (uuid),
stripe_session_id (text, unique),
recovery_email_sent (boolean, default false),
recovery_sent_at (timestamptz),
converted (boolean, default false),
created_at (timestamptz, default now())

**pay_optimisation_log**
id (uuid, primary key, default gen_random_uuid()),
product_id (uuid),
product_name (text),
old_description (text),
new_description (text),
old_conversion_rate (numeric),
optimised_at (timestamptz, default now())

**pay_errors**
id (uuid, primary key, default gen_random_uuid()),
function_name (text),
error_message (text),
context (text),
created_at (timestamptz, default now())

---

## 2. Setup page

Create a page at /lazy-pay-setup with a form:
- Business name
- Support email address
- Site URL
- Currency (select: USD / GBP / EUR / AUD)
- Stripe Publishable Key (text) — note: will be stored as Supabase secret STRIPE_PUBLISHABLE_KEY
- Stripe Secret Key (password) — note: will be stored as Supabase secret STRIPE_SECRET_KEY
- Stripe Webhook Secret (password) — with instructions: In the Stripe dashboard create a webhook pointing to [site_url]/api/stripe-webhook listening for: payment_intent.succeeded, payment_intent.payment_failed, checkout.session.completed, checkout.session.expired, customer.subscription.created, customer.subscription.updated, customer.subscription.deleted, invoice.payment_failed. Paste the signing secret here. — will be stored as Supabase secret STRIPE_WEBHOOK_SECRET.

Submit button: Activate Lazy Pay

On submit:
1. Store Stripe keys as Supabase secrets
2. Save business_name, support_email, site_url, currency to pay_settings
3. Set setup_complete to true and prompt_version to 'v0.0.3'
4. Redirect to /admin with message: "Lazy Pay is active. Add your first product to start taking payments."

---

## 3. Core edge functions

**pay-checkout** — handles POST requests
- Accept product_id (uuid) and customer_email (text)
- Read matching product from pay_products, increment views by 1
- Read pay_settings and Stripe keys from Supabase secrets
- Create or retrieve Stripe customer, insert into pay_customers if new
- Create Stripe checkout session using stripe_price_id. Set mode to subscription or payment based on billing_type. Set success_url to site_url/payment-success, cancel_url to site_url/payment-cancelled
- Insert into pay_abandoned with stripe_session_id and recovery_email_sent false
- Return checkout URL
- Log errors to pay_errors with function_name pay-checkout

**pay-webhook** — handles POST requests at /api/stripe-webhook
- Verify Stripe webhook signature using STRIPE_WEBHOOK_SECRET secret — reject invalid with 400
- Handle checkout.session.completed: set converted to true in pay_abandoned, insert successful transaction in pay_transactions, send confirmation email with subject "Payment confirmed — [business_name]"
- Handle checkout.session.expired: mark pay_abandoned row as ready for recovery (recovery_email_sent false, converted false)
- Handle payment_intent.payment_failed: update transaction status to failed
- Handle customer.subscription.created: insert into pay_subscriptions with status active
- Handle customer.subscription.updated: update matching pay_subscriptions row
- Handle customer.subscription.deleted: update status to cancelled
- Handle invoice.payment_failed: update subscription status to past_due
- Log all errors to pay_errors with function_name pay-webhook

**pay-portal** — handles POST requests
- Accept customer_email (text)
- Look up stripe_customer_id from pay_customers
- Create Stripe billing portal session with return_url set to site_url
- Return portal URL
- Log errors to pay_errors with function_name pay-portal

---

## 4. Self-improving edge functions

**pay-optimise**
Cron: every Sunday at 11am UTC — 0 11 * * 0

1. Read pay_settings. If is_running is false or setup_complete is false exit.
2. For each active product in pay_products calculate conversion rate: (successful transactions in last 30 days / views) * 100.
3. If conversion rate < 3% and views > 30 and last_optimised is null or older than 14 days:
   Call the built-in Lovable AI:
   "You are a conversion rate specialist for [business_name]. This product has a [conversion_rate]% conversion rate from [views] views. Rewrite the name and description to be significantly more compelling. Product: [name]. Current description: [description]. Price: [price]. Return only a valid JSON object with two fields: name (string) and description (string, 80 to 120 words). No preamble. No code fences. Valid JSON only."
4. Insert into pay_optimisation_log with old and new values.
5. Update name and description in pay_products.
6. Update the product in Stripe via the Products API using STRIPE_SECRET_KEY secret.
7. Set last_optimised to now.
Log errors to pay_errors with function_name pay-optimise.

**pay-recover**
Cron: daily at 10am UTC — 0 10 * * *

1. Read pay_settings. If is_running is false or setup_complete is false exit.
2. Query pay_abandoned where recovery_email_sent is false and converted is false and created_at is older than 24 hours.
3. For each row get the matching product from pay_products.
4. Call pay-checkout to generate a fresh checkout URL for the customer email and product.
5. Send recovery email: subject "You left something behind" body "You started checking out [product_name] but did not complete your purchase. Complete it here: [fresh checkout URL]. This link is valid for 48 hours. Questions? [support_email]"
6. Update pay_abandoned: set recovery_email_sent to true, recovery_sent_at to now.
Log errors to pay_errors with function_name pay-recover.

---

## 5. Public pages

**/pricing**
Show all active pay_products ordered by price_cents ascending. Each card shows name, description, formatted price, billing interval for subscriptions, and a Buy Now button. On click show email input modal then call pay-checkout and redirect to the Stripe checkout URL.

**/payment-success**
Show: "Payment confirmed. Thank you for your purchase." Link home.

**/payment-cancelled**
Show: "Payment cancelled. No charge was made." Link to /pricing.

**/manage-subscription**
Show email input. On submit call pay-portal and redirect to Stripe customer portal.

---

## 6. Admin

Do not build a standalone dashboard page for this engine. The dashboard lives at /admin/pay as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt. This engine only needs its setup page, database tables, edge functions, and public pages.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all engines in one place." and a link to /lazy-pay-setup.

## 7. Navigation

Add a Pricing link to the main site navigation pointing to /pricing.
Add a Manage Subscription link in the site footer pointing to /manage-subscription.
Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-pay-setup to public navigation.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
