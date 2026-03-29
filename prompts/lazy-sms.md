# lazy-sms — v0.0.8

[Lazy SMS Prompt — v0.0.8 — LazyUnicorn.ai]

Add a complete self-improving Twilio SMS agent called Lazy SMS to this project. It installs payment confirmations, subscription alerts, abandoned checkout recovery texts, welcome sequences, two-way messaging, opt-out management, delivery tracking, and autonomous message optimisation — with no manual Twilio integration required after setup.

---

## 1. Database

Create these Supabase tables with RLS enabled:

**sms_settings**
id (uuid, primary key, default gen_random_uuid()),
business_name (text),
site_url (text),
twilio_phone_number (text),
is_running (boolean, default true),
setup_complete (boolean, default false),
prompt_version (text, nullable),
created_at (timestamptz, default now())

Note: Store Twilio credentials as Supabase secrets — TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN. Never store in the database table.

**sms_contacts**
id (uuid, primary key, default gen_random_uuid()),
phone_number (text, unique),
name (text),
email (text),
opted_out (boolean, default false),
opted_out_at (timestamptz),
created_at (timestamptz, default now())

**sms_messages**
id (uuid, primary key, default gen_random_uuid()),
contact_id (uuid),
phone_number (text),
message_body (text),
direction (text),
message_type (text),
twilio_message_sid (text),
status (text, default 'queued'),
sent_at (timestamptz),
delivered_at (timestamptz),
created_at (timestamptz, default now())

**sms_sequences**
id (uuid, primary key, default gen_random_uuid()),
name (text),
trigger (text),
step_number (integer),
delay_hours (integer),
message_template (text),
response_rate (numeric, default 0),
sends (integer, default 0),
responses (integer, default 0),
last_optimised (timestamptz),
active (boolean, default true),
created_at (timestamptz, default now())

**sms_optouts**
id (uuid, primary key, default gen_random_uuid()),
phone_number (text, unique),
opted_out_at (timestamptz, default now())

**sms_optimisation_log**
id (uuid, primary key, default gen_random_uuid()),
sequence_id (uuid),
sequence_name (text),
old_template (text),
new_template (text),
old_response_rate (numeric),
optimised_at (timestamptz, default now())

**sms_errors**
id (uuid, primary key, default gen_random_uuid()),
function_name (text),
error_message (text),
created_at (timestamptz, default now())

---

## 2. Setup page

Create a page at /lazy-sms-setup with a form:
- Twilio Account SID (text) — find in Twilio console. Stored as Supabase secret TWILIO_ACCOUNT_SID.
- Twilio Auth Token (password) — find in Twilio console. Stored as Supabase secret TWILIO_AUTH_TOKEN.
- Twilio Phone Number (text) — the SMS-enabled number in E.164 format e.g. +12025551234
- Business name
- Site URL

Show a notice on the setup page:
"After saving, go to your Twilio console, select your phone number, and set:
Messaging webhook URL: [site_url]/api/sms-receive (HTTP POST)
Status Callback URL: [site_url]/api/sms-status (HTTP POST)"

Submit button: Activate Lazy SMS

On submit:
1. Store TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN as Supabase secrets
2. Save twilio_phone_number, business_name, site_url to sms_settings
3. Set setup_complete to true and prompt_version to 'v0.0.5'
4. Seed sms_sequences with four default sequences:
   - trigger: new-customer, step: 1, delay: 0, template: "Welcome to [business_name]. We are glad to have you. Reply STOP to opt out."
   - trigger: payment-success, step: 1, delay: 0, template: "Payment confirmed. Thank you for your purchase from [business_name]. Reply STOP to opt out."
   - trigger: subscription-renewal, step: 1, delay: 72, template: "Your [business_name] subscription renews in 3 days. Manage it here: [site_url]/manage-subscription. Reply STOP to opt out."
   - trigger: checkout-abandoned, step: 1, delay: 1, template: "You left something at [business_name]. Complete your purchase here: [checkout_url]. Reply STOP to opt out."
5. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy SMS', version: '0.0.8', site_url: site_url }) }) } catch(e) {}
6. Redirect to /admin with message: "Lazy SMS is active. Your site will now text customers automatically."

---

## 3. Core edge functions

**sms-send** — handles POST requests
- Accept phone_number (text), message_body (text), message_type (text), contact_id (uuid optional)
- Check sms_optouts for the phone number — if found return without sending
- Read TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN from Supabase secrets
- Send via Twilio Messages API: https://api.twilio.com/2010-04-01/Accounts/[TWILIO_ACCOUNT_SID]/Messages.json using Basic Auth
- Body: From = twilio_phone_number, To = phone_number, Body = message_body
- Insert into sms_messages with twilio_message_sid from response and status sent
- Log errors to sms_errors with function_name sms-send

**sms-receive** — handles POST requests at /api/sms-receive
- Parse Twilio webhook: From (sender number), Body (message text), MessageSid
- If body is STOP, STOPALL, UNSUBSCRIBE, CANCEL, END, or QUIT: insert into sms_optouts, update opted_out in sms_contacts, insert inbound message with message_type opt-out. Exit.
- For all other messages: insert into sms_messages with direction inbound. Find contact in sms_contacts by phone number. Increment responses on matching outbound messages.
- Call the built-in Lovable AI:
  "You are a helpful customer service assistant for [business_name]. A customer texted: [message_body]. Write a brief helpful SMS reply under 160 characters. Be friendly and concise. Do not use emojis. End with: Reply STOP to opt out. Return only the message text, nothing else."
- Call sms-send with the reply and customer phone number and message_type reply
- Log errors to sms_errors with function_name sms-receive

**sms-status** — handles POST requests at /api/sms-status
- Parse Twilio webhook: MessageSid and MessageStatus
- Update matching sms_messages row — set status, set delivered_at to now if status is delivered
- Log errors to sms_errors with function_name sms-status

---

## 4. Sequence edge function

**sms-sequences-run**
Cron: every hour — 0 * * * *

1. Read sms_settings. If is_running is false or setup_complete is false exit.
2. For each active sequence in sms_sequences find eligible contacts:
   - new-customer: sms_contacts created in the last hour
   - payment-success: pay_transactions where status is succeeded and created_at in the last hour (skip if pay_transactions table does not exist)
   - checkout-abandoned: pay_abandoned where recovery_email_sent is true and created_at between 1 and 2 hours ago (skip if table does not exist)
   - subscription-renewal: pay_subscriptions where current_period_end is between 72 and 73 hours from now (skip if table does not exist)
3. For each matching contact: check they have not already received this sequence step (query sms_messages). Check they are not in sms_optouts.
4. Personalise template: replace [business_name], [site_url], [checkout_url] with values from sms_settings.
5. Call sms-send for each eligible contact.
6. Increment sends on the sequence row.
Log errors to sms_errors with function_name sms-sequences-run.

---

## 5. Self-improving edge function

**sms-optimise**
Cron: every Sunday at 12pm UTC — 0 12 * * 0

1. Read sms_settings. If is_running is false exit.
2. For each active sequence where sends > 20: calculate response_rate = (responses / sends) * 100. Update response_rate in sms_sequences.
3. If response_rate < 5 and (last_optimised is null or older than 14 days):
   Call the built-in Lovable AI:
   "You are an SMS marketing specialist for [business_name]. This message has a [response_rate]% response rate from [sends] sends. Rewrite it to be more engaging. Keep it under 160 characters. Current message: [message_template]. Trigger context: [trigger]. Return only the new message text. Do not include STOP instructions — those will be appended automatically."
4. Insert into sms_optimisation_log with old and new values.
5. Update message_template in sms_sequences.
6. Set last_optimised to now.
Log errors to sms_errors with function_name sms-optimise.

---

## 6. Admin

Do not build a standalone dashboard page for this agent. The dashboard lives at /admin/sms as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt. This agent only needs its setup page, database tables, edge functions, and public pages.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all agents in one place." and a link to /lazy-sms-setup.

## 7. Navigation

Do not add any Lazy SMS pages to the public navigation. All pages are admin-only.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.