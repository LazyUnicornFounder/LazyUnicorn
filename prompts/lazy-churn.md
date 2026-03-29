# Lazy Churn

> Category: ⚙️ Ops · Version: 0.0.3

## Prompt

````
# lazy-churn

> Version: 0.0.2

## Prompt

````
[Lazy Churn Prompt — v0.0.2 — LazyUnicorn.ai]

Add an autonomous churn prevention agent called Lazy Churn to this project. It monitors your Stripe subscriber data daily, identifies customers at risk of cancelling based on login inactivity, usage drops, and renewal proximity, and automatically triggers personalised re-engagement sequences via SMS and email — before the cancellation happens.

Required secrets: STRIPE_SECRET_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, RESEND_API_KEY
Note: These are already set if Lazy Pay, Lazy SMS, and Lazy Mail are installed.

---

1. Database

Create these Supabase tables with RLS enabled:

churn_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), site_url (text), inactivity_days_threshold (integer, default 14), renewal_warning_days (integer, default 7), usage_drop_threshold (integer, default 50), send_sms (boolean, default true), send_email (boolean, default true), slack_webhook_url (text), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

churn_customers: id (uuid, primary key, default gen_random_uuid()), stripe_customer_id (text, unique), email (text), name (text), phone (text), plan_name (text), mrr (numeric), subscription_start (date), renewal_date (date), last_login (timestamptz), login_count_30d (integer, default 0), risk_score (integer, default 0 — 0 to 100), risk_reason (text), status (text, default 'healthy' — one of healthy, at-risk, critical, churned), last_contacted (timestamptz), created_at (timestamptz, default now()), updated_at (timestamptz, default now())

churn_interventions: id (uuid, primary key, default gen_random_uuid()), customer_id (uuid), intervention_type (text — one of inactivity-sms, inactivity-email, renewal-reminder-sms, renewal-reminder-email, win-back-sms, win-back-email), message_sent (text), sent_at (timestamptz, default now()), outcome (text — one of pending, logged-in, upgraded, cancelled, no-response), outcome_at (timestamptz), created_at (timestamptz, default now())

churn_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

---

2. Setup page

Create a page at /lazy-churn-setup.

Welcome message: 'The cheapest customer is the one you keep. Lazy Churn monitors every subscriber daily, identifies who is drifting toward cancellation, and sends a personalised re-engagement message before they ever reach the cancel button.'

Form fields:
- Brand name (text)
- Site URL (text)
- Inactivity threshold (number, default 14) — how many days without login before triggering re-engagement
- Renewal warning window (number, default 7) — how many days before renewal to send a reminder to at-risk customers
- Usage drop threshold (number with % sign, default 50) — if a customer's usage drops by this percentage week-over-week trigger re-engagement
- Send SMS re-engagement (toggle, default on) — requires Twilio. Sends a text to at-risk customers.
- Send email re-engagement (toggle, default on) — requires Resend. Sends an email to at-risk customers.
- Slack webhook URL (text, optional) — for daily churn risk digest

Submit button: Activate Lazy Churn

On submit:
1. Save all values to churn_settings
2. Set setup_complete to true and prompt_version to 'v0.0.2'
3. Immediately trigger churn-sync to import current subscriber data from Stripe
4. Redirect to /admin with message: 'Lazy Churn is active. Syncing your subscribers now. At-risk customers will appear in /admin/churn within a few minutes.'

---

3. Edge functions

churn-sync
Cron: daily at 2am UTC — 0 2 * * *

1. Read churn_settings. If is_running false or setup_complete false exit.
2. Fetch all active Stripe subscriptions: GET https://api.stripe.com/v1/subscriptions?status=active&limit=100 with Authorization: Bearer [STRIPE_SECRET_KEY]. Handle pagination.
3. For each subscription fetch the customer: GET https://api.stripe.com/v1/customers/[customer_id].
4. Upsert into churn_customers: stripe_customer_id, email, name, phone (from customer metadata if set), plan_name, mrr (from subscription amount), renewal_date (from current_period_end).
5. For customers where you have login data (check if user_profiles table exists — Lazy Auth): join on email to get last_login and calculate login_count_30d.
6. Call churn-score for each customer to calculate risk.
Log errors to churn_errors with function_name churn-sync.

churn-score
Triggered by churn-sync. Accepts customer_id.

1. Read the churn_customers row and churn_settings.
2. Calculate risk score (0 to 100) based on these signals:
   - Days since last login: 0-7 days = 0 points, 8-14 days = 20 points, 15-21 days = 35 points, 22+ days = 50 points
   - Login count last 30 days: 10+ = 0, 5-9 = 10, 2-4 = 20, 0-1 = 30 points
   - Days until renewal: 30+ days = 0, 8-29 days = 5, 1-7 days = 15, overdue = 25 points
   - Subscription age: over 6 months = -10 points (loyalty discount), under 30 days = +10 points (new customer at risk)
   Cap total at 100.
3. Determine risk_reason: the single most significant factor contributing to the score.
4. Determine status: score 0-30 = healthy, 31-60 = at-risk, 61-100 = critical.
5. Update churn_customers with risk_score, risk_reason, status, updated_at.
6. If status changed to at-risk or critical: call churn-intervene with the customer_id.
Log errors to churn_errors with function_name churn-score.

churn-intervene
Triggered by churn-score when customer becomes at-risk or critical. Accepts customer_id.

1. Read churn_settings, churn_customers row.
2. Check churn_interventions — if this customer was contacted in the last 7 days exit. Do not spam.
3. Determine intervention type based on risk_reason:
   - Inactivity → inactivity-sms and inactivity-email
   - Renewal approaching → renewal-reminder-sms and renewal-reminder-email
   - Critical (score 70+) → win-back-sms and win-back-email
4. Call built-in Lovable AI to write personalised messages:
'You are writing re-engagement messages for [brand_name]. Customer: [name]. Plan: [plan_name]. MRR: [mrr]. Risk reason: [risk_reason]. Days since last login: [n]. Days until renewal: [n]. Risk level: [status]. Write two messages: one SMS (under 160 chars, personal, specific, not salesy — mention their specific plan and a concrete benefit they might be missing) and one email (subject line under 50 chars, body under 150 words — warm, direct, one specific question or offer that relates to their risk reason). Return only a valid JSON object: sms_message (string), email_subject (string), email_body (string). No preamble. No code fences.'
5. Parse response.
6. If send_sms is true and customer phone exists and TWILIO credentials exist: send SMS via Twilio API POST https://api.twilio.com/2010-04-01/Accounts/[SID]/Messages. Insert into churn_interventions with type inactivity-sms or renewal-reminder-sms.
7. If send_email is true and RESEND_API_KEY exists: send email via Resend POST https://api.resend.com/emails. Insert into churn_interventions with type inactivity-email or renewal-reminder-email.
8. Update churn_customers last_contacted to now.
9. If slack_webhook_url set: POST to Slack: '⚠️ Lazy Churn — [name] ([plan_name], $[mrr]/mo) is [status]. [risk_reason]. Re-engagement sent.'
Log errors to churn_errors with function_name churn-intervene.

churn-track-outcomes
Cron: daily at 3am UTC — 0 3 * * *

1. Read all churn_interventions where outcome is pending and sent_at is more than 48 hours ago.
2. For each intervention fetch the customer from churn_customers.
3. Check if customer last_login is after the intervention sent_at. If yes: update intervention outcome to logged-in.
4. Check Stripe for subscription status. If cancelled: update outcome to cancelled, update customer status to churned.
5. Update risk scores for all customers where outcome changed.
Log errors to churn_errors with function_name churn-track-outcomes.

churn-daily-digest
Cron: daily at 8am UTC — 0 8 * * *

1. Read churn_settings. If is_running false or slack_webhook_url not set exit.
2. Count customers by status. Count interventions sent yesterday. Count outcomes.
3. POST to Slack: '📊 *Lazy Churn Daily* — [date]
✅ Healthy: [n] customers
⚠️ At-risk: [n] customers
🔴 Critical: [n] customers
💬 Re-engagements sent yesterday: [n]
↩️ Logged back in after contact: [n]
❌ Churned: [n] this week'
Log errors to churn_errors with function_name churn-daily-digest.

---

4. Admin dashboard

Do not build a standalone dashboard. Lazy Churn lives at /admin/churn as part of the unified LazyUnicorn admin panel.

The /admin/churn section shows:

MRR at risk: a prominent card at the top showing total MRR at risk (sum of mrr for all at-risk and critical customers). Sub-stats: healthy count, at-risk count, critical count.

Customer risk table: all churn_customers ordered by risk_score descending. Columns: name, email, plan, MRR, risk score as a visual progress bar (red for 70+, orange for 40-69, green for under 40), risk reason, status badge, last login, renewal date, last contacted date. Click any row to see full intervention history for that customer. Manual Send Message button opens a modal with the AI-generated message pre-filled for editing.

Interventions log: all churn_interventions ordered by sent_at descending last 50 rows — customer name, type badge, sent time, outcome badge (pending grey / logged-in green / cancelled red / no-response amber). Filter by outcome.

Recovery chart: recharts bar chart showing interventions sent vs logins recovered per week for last 8 weeks.

Settings: all thresholds editable inline, toggle controls, Slack status, is_running toggle.

Error log: churn_errors last 20 rows, collapsed.

---

5. Navigation

Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-churn-setup to public navigation.

## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.
````
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
