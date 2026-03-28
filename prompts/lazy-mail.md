# Lazy Mail

> Category: 🛒 Commerce · Version: 0.0.2

## Prompt

````
# lazy-mail — v0.0.1

[Lazy Mail Prompt — v0.0.1 — LazyUnicorn.ai]

Add a complete autonomous email engine called Lazy Mail to this project. It connects Resend to your Lovable site and handles subscriber capture, welcome sequences, automated newsletter broadcasts from your blog content, transactional emails, and self-improving open rates — without you writing or sending a single email manually.

Note: Store the Resend API key as Supabase secret RESEND_API_KEY. Never store in the database.

---

1. Database

Create these Supabase tables with RLS enabled:

mail_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), from_email (text), from_name (text), reply_to_email (text), site_url (text), resend_audience_id (text), welcome_email_enabled (boolean, default true), newsletter_enabled (boolean, default true), newsletter_frequency (text, default 'weekly' — one of daily, weekly, biweekly), newsletter_day (text, default 'monday'), double_optin_enabled (boolean, default true), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

mail_subscribers: id (uuid, primary key, default gen_random_uuid()), email (text, unique), first_name (text), status (text, default 'pending' — one of pending, confirmed, unsubscribed), resend_contact_id (text), source (text), confirmed_at (timestamptz), unsubscribed_at (timestamptz), created_at (timestamptz, default now())

mail_sequences: id (uuid, primary key, default gen_random_uuid()), name (text), trigger (text), delay_days (integer, default 0), subject (text), body (text), sends (integer, default 0), opens (integer, default 0), open_rate (real, default 0), last_optimised (timestamptz), is_active (boolean, default true), created_at (timestamptz, default now())

mail_broadcasts: id (uuid, primary key, default gen_random_uuid()), subject (text), preview_text (text), body (text), source_post_id (uuid), source_type (text), resend_broadcast_id (text), status (text, default 'draft' — one of draft, scheduled, sent), scheduled_at (timestamptz), sent_at (timestamptz), recipient_count (integer, default 0), open_count (integer, default 0), open_rate (real, default 0), created_at (timestamptz, default now())

mail_sent: id (uuid, primary key, default gen_random_uuid()), subscriber_id (uuid), sequence_id (uuid), broadcast_id (uuid), subject (text), sent_at (timestamptz, default now()), opened (boolean, default false), resend_email_id (text)

mail_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

---

2. Setup page

Create a page at /lazy-mail-setup.

Welcome message: 'Your blog publishes itself. Now your emails send themselves too. Lazy Mail captures subscribers, sends welcome sequences, and broadcasts your latest posts automatically — powered by Resend.'

Form fields:
- Brand name (text)
- Site URL (text)
- From email (text) — the email address your subscribers will see e.g. hello@yoursite.com. Must be on a domain verified in Resend.
- From name (text) — e.g. The LazyUnicorn Team
- Reply-to email (text) — where replies go. Can be the same as From email.
- Resend API key (password) — instructions: sign up at resend.com, go to API Keys, create a new key with full access. Stored as Supabase secret RESEND_API_KEY.
- Resend Audience ID (text) — instructions: in Resend go to Audiences, create a new audience for this site, copy the Audience ID. This is where your subscribers are stored in Resend.
- Newsletter frequency (select: Daily / Weekly / Biweekly)
- Newsletter day (select: Monday / Tuesday / Wednesday / Thursday / Friday — only shown if frequency is weekly or biweekly)
- Enable double opt-in (toggle, default on) — recommended for GDPR compliance. Sends a confirmation email before adding subscriber to the audience.
- Enable welcome email (toggle, default on) — sends a welcome email immediately when someone confirms their subscription.

Submit button: Activate Lazy Mail

On submit:
1. Store RESEND_API_KEY as Supabase secret
2. Save all other values to mail_settings
3. Set setup_complete to true and prompt_version to 'v0.0.1'
4. Insert the default welcome sequence into mail_sequences:
   - name: Welcome, trigger: confirmed, delay_days: 0, subject: 'Welcome to [brand_name]', body: A warm plain-text welcome email written by the built-in Lovable AI for this brand. Call the AI: 'Write a warm, genuine welcome email for a new subscriber to [brand_name] described as [site description]. 150 words maximum. Plain text. No salutation. Start with: Welcome — you are in. End with the sender name. No marketing language.'
5. Immediately call mail-send-test to verify the Resend connection by sending a test email to the from_email address
6. Redirect to /admin with message: 'Lazy Mail is active. Test email sent to [from_email] to confirm everything is working.'

---

3. Edge functions

mail-subscribe
POST endpoint at /api/mail-subscribe. Accepts email and optionally first_name and source.

1. Validate email format. If invalid return 400.
2. Check if email already exists in mail_subscribers. If status is confirmed return 200 with message: Already subscribed. If status is unsubscribed update status to pending and continue. If new insert with status pending.
3. If double_optin_enabled is true: call mail-send-confirmation with the subscriber id. Return 200 with message: Check your email to confirm your subscription.
4. If double_optin_enabled is false: update status to confirmed, set confirmed_at to now. Create a Resend contact via POST to https://api.resend.com/audiences/[resend_audience_id]/contacts with email, first_name, and unsubscribed false. Store the returned id as resend_contact_id. Call mail-send-sequence with trigger 'confirmed' and the subscriber id. Return 200 with message: You are subscribed.
Log errors to mail_errors with function_name mail-subscribe.

mail-send-confirmation
Sends a double opt-in confirmation email. Accepts subscriber_id.

1. Read mail_settings and the mail_subscribers row.
2. Generate a secure confirmation token — a UUID stored temporarily in a mail_confirmation_tokens table (id, subscriber_id, token, expires_at set to 24 hours from now).
3. Call Resend API to send a confirmation email: POST https://api.resend.com/emails. From: [from_name] <[from_email]>. To: subscriber email. Subject: 'Confirm your subscription to [brand_name]'. Body: clean HTML email with: headline 'One click to confirm', one sentence 'Click the button below to confirm your subscription to [brand_name]', a large confirm button linking to [site_url]/api/mail-confirm?token=[token], footer with unsubscribe note.
Log errors to mail_errors with function_name mail-send-confirmation.

mail-confirm
GET endpoint at /api/mail-confirm. Accepts token query parameter.

1. Look up token in mail_confirmation_tokens. If not found or expired return a 400 page: Token invalid or expired. If valid continue.
2. Update mail_subscribers status to confirmed, set confirmed_at to now.
3. Create Resend contact in the audience. Store resend_contact_id.
4. Delete the used token from mail_confirmation_tokens.
5. Call mail-send-sequence with trigger 'confirmed' and the subscriber id.
6. Redirect to [site_url]/subscribed or render a simple success page: You are confirmed. Welcome to [brand_name].
Log errors to mail_errors with function_name mail-confirm.

mail-send-sequence
Triggered by mail-confirm or mail-subscribe. Accepts trigger and subscriber_id.

1. Read mail_settings. Query all mail_sequences where trigger matches and is_active is true.
2. For sequences with delay_days 0: call mail-send immediately.
3. For sequences with delay_days greater than 0: store in a mail_sequence_queue table (subscriber_id, sequence_id, send_at set to now plus delay_days). mail-send-queued processes these on a schedule.
Log errors to mail_errors with function_name mail-send-sequence.

mail-send
Sends one email to one subscriber. Accepts subscriber_id, subject, body, sequence_id or broadcast_id.

1. Read mail_settings and the subscriber row. If status is not confirmed exit.
2. Call Resend API: POST https://api.resend.com/emails. From: [from_name] <[from_email]>. Reply-To: [reply_to_email]. To: subscriber email. Subject: subject. Html: render body markdown to clean HTML with the brand header, content, and an unsubscribe footer linking to [site_url]/api/mail-unsubscribe?id=[subscriber_id].
3. Store the returned resend email id in mail_sent. Increment sends count on the matching sequence or broadcast.
Log errors to mail_errors with function_name mail-send.

mail-send-queued
Cron: every hour — 0 * * * *

1. Query mail_sequence_queue where send_at is in the past and sent is false.
2. For each row call mail-send with the subscriber_id and sequence details.
3. Mark as sent.
Log errors to mail_errors with function_name mail-send-queued.

mail-unsubscribe
GET endpoint at /api/mail-unsubscribe. Accepts id (subscriber id).

1. Update mail_subscribers status to unsubscribed, set unsubscribed_at to now.
2. Update Resend contact: PATCH https://api.resend.com/audiences/[resend_audience_id]/contacts/[resend_contact_id] with unsubscribed true.
3. Render a simple confirmation page: You have been unsubscribed. You will not receive any more emails from [brand_name].
Log errors to mail_errors with function_name mail-unsubscribe.

mail-broadcast
Cron: runs on the configured newsletter_day at 9am UTC. Also callable manually from the admin dashboard.

1. Read mail_settings. If is_running is false or newsletter_enabled is false exit.
2. Check if a broadcast was already sent today. If yes exit.
3. Find the most recent published post to feature. Check in this order: blog_posts table, seo_posts table, geo_posts table. Pick the most recently published post that has not already been used as a source_post_id in mail_broadcasts.
4. If no new post is found in any table exit without sending.
5. Call the built-in Lovable AI to write the newsletter email:
'You are writing a newsletter email for [brand_name] subscribers. The featured post is titled: [post title]. Excerpt: [post excerpt]. Tone: conversational and genuine. Write a short newsletter email introducing this post. 3 short paragraphs maximum. First paragraph: a personal hook relating to the topic. Second paragraph: introduce the post and what readers will learn. Third paragraph: a call to action to read the full post. Return only a valid JSON object: subject (email subject line — compelling, under 50 chars), preview_text (preview snippet under 90 chars), body (the 3 paragraphs in clean markdown). No preamble. No code fences.'
6. Parse the response. Insert into mail_broadcasts with status scheduled.
7. Call Resend broadcast API or send individually to all confirmed subscribers using mail-send in batches of 50 with a 1-second delay between batches.
8. Update mail_broadcasts with status sent, sent_at, recipient_count.
9. If slack_webhook_url is set in mail_settings send a Slack notification: 'Lazy Mail sent a newsletter to [recipient_count] subscribers. Subject: [subject].'
Log errors to mail_errors with function_name mail-broadcast.

mail-optimise
Cron: every Sunday at 11am UTC — 0 11 * * 0

1. Read mail_settings. If is_running is false exit.
2. Query mail_sequences. For any sequence with sends greater than 20 and open_rate below 20 percent:
3. Call built-in Lovable AI:
'You are an email copywriter. This welcome email subject has an open rate of [open_rate]% after [sends] sends: [subject]. Body: [body]. Rewrite the subject line to improve open rate. Keep the same intent. Return only a valid JSON object: new_subject (string), reason (one sentence). No preamble. No code fences.'
4. Update the sequence with the new subject. Store the old subject and reason in a log field.
Log errors to mail_errors with function_name mail-optimise.

mail-send-test
Sends a test email to the from_email address to verify the connection. Accepts no parameters.

1. Call Resend API to send a simple test email to from_email.
Subject: 'Lazy Mail is connected — [brand_name]'
Body: 'Your Resend integration is working. Lazy Mail will now handle all emails for [brand_name] automatically. Subscribers, welcome sequences, and newsletters are ready.'
Log errors to mail_errors with function_name mail-send-test.

---

4. Subscribe form component

Create a reusable Subscribe component that can be embedded anywhere on the site. It shows an email input and a subscribe button. On submit it calls /api/mail-subscribe. On success it shows: 'Check your email to confirm' if double opt-in is enabled, or 'You are subscribed' if not. On error it shows a red message.

Add this component to:
- The homepage if one exists — in the hero or below it
- The footer of every public page
- The /blog page if it exists
- Below every individual blog post, SEO post, and GEO post

---

5. Public pages

/subscribe — a standalone subscribe page with the Subscribe component centred on the page. Headline: 'Stay in the loop.' Subheadline: '[brand_name] sends a newsletter when new content publishes. No spam. Unsubscribe any time.'

/subscribed — the page subscribers land on after confirming. Headline: 'You are in.' Body: 'Welcome to [brand_name]. Check your inbox for a welcome email.' Link back to the homepage.

---

6. Admin

Do not build a standalone dashboard. The Lazy Mail dashboard lives at /admin/mail as part of the unified LazyUnicorn admin panel.

If /admin does not yet exist add a placeholder at /admin pointing to /lazy-mail-setup.

---

7. Navigation

Add a Subscribe link to the footer navigation pointing to /subscribe.
Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-mail-setup or /subscribed to public navigation.

## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
