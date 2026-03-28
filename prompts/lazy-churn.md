# Lazy Churn

> Category: 🤖 Agents · Version: 0.0.1

## Prompt

````
Lazy Churn Prompt — v0.0.1 — LazyUnicorn.ai

Add an autonomous churn prevention agent called Lazy Churn to this project. It monitors your Stripe subscriber data daily, identifies customers at risk of cancelling based on login inactivity, usage drops, and renewal proximity, and automatically triggers personalised re-engagement sequences via SMS and email — before the cancellation happens.

Required secrets: STRIPE_SECRET_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, RESEND_API_KEY. Note: These are already set if Lazy Pay, Lazy SMS, and Lazy Mail are installed.

---

1. Database

Create these Supabase tables with RLS enabled:

churn_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), site_url (text), inactivity_days_threshold (integer, default 14), renewal_warning_days (integer, default 7), usage_drop_threshold (integer, default 50), send_sms (boolean, default true), send_email (boolean, default true), slack_webhook_url (text), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

churn_customers: id (uuid, primary key, default gen_random_uuid()), stripe_customer_id (text, unique), email (text), name (text), phone (text), plan_name (text), mrr (numeric), subscription_start (date), renewal_date (date), last_login (timestamptz), login_count_30d (integer, default 0), risk_score (integer, default 0 — 0 to 100), risk_reason (text), status (text, default 'healthy' — one of healthy, at-risk, critical, churned), last_contacted (timestamptz), created_at (timestamptz, default now()), updated_at (timestamptz, default now())

churn_interventions: id (uuid, primary key, default gen_random_uuid()), customer_id (uuid), intervention_type (text — one of inactivity-sms, inactivity-email, renewal-reminder-sms, renewal-reminder-email, win-back-sms, win-back-email), message_sent (text), sent_at (timestamptz, default now()), outcome (text — one of pending, logged-in, upgraded, cancelled, no-response), outcome_at (timestamptz), created_at (timestamptz, default now())

churn_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
