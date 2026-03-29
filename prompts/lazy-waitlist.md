# Lazy Waitlist v0.0.1
## Pre-Launch Email Capture Engine with Viral Referral System

This engine creates a complete pre-launch waitlist system with viral referral mechanics, automated welcome sequences via Resend, Slack notifications for new signups, a live counter, and launch-day conversion to user accounts.

---

## Database Schema

### Table: waitlist_settings
Stores all configuration: waitlist name, launch date, referral settings, welcome/follow-up/launch email templates, Slack settings, page customization (headline, subheadline, CTA, accent color, counter/position toggles), and social sharing text.

### Table: waitlist_subscribers
Stores subscribers with: email, name, unique referral_code, referred_by reference, referral_count, position (auto-assigned via trigger), priority_score, status (waiting/priority/converted/unsubscribed), email tracking booleans, UTM parameters, and metadata.

Triggers:
- assign_waitlist_position: auto-assigns incrementing position on insert
- generate_referral_code: generates unique 8-char code from MD5 hash
- increment_referral_count: updates referrer count and promotes to priority when threshold is met

### Table: waitlist_errors
Error logging with type, message, details (JSONB), subscriber reference, function name, and resolved flag.

### Table: waitlist_stats
Daily aggregate stats: signups_count, referrals_count, conversions_count, unsubscribes_count. Uses upsert via increment_daily_signups() RPC.

---

## Edge Functions

### waitlist-signup
Handles new signups: validates email, checks duplicates (returns existing position if found), resolves referral codes, inserts subscriber, calls increment_daily_signups RPC, triggers welcome email and Slack notification.

### waitlist-send-email
Sends emails via Resend API (welcome, follow-up, or launch). Replaces template variables {{name}}, {{position}}, {{referral_link}}, {{referral_code}}. Updates subscriber email tracking fields.

### waitlist-notify-slack
Posts formatted message to Slack via incoming webhook when a new subscriber joins.

---

## Pages

### /waitlist — Public Waitlist Page
Conversion-optimised landing page with configurable headline/subheadline/CTA, email + name capture, live signup counter (30s refresh), countdown timer, referral tracking via ?ref= query param, success state with position/referral link/social share buttons, referral progress bar, and Powered by LazyUnicorn.ai backlink.

### /admin/waitlist — Admin Dashboard
5-tab dashboard: Subscribers (search/filter/paginate/CSV export), Analytics (daily stats/referral leaderboard), Emails (send counts), Launch (checklist/one-click launch), Errors (error log). Stat cards for Total/Today/Priority/Converted. Engine toggle.

### /admin/waitlist/setup — Setup Wizard
3-step wizard: Waitlist config → Page design → Email templates.

---

## Required Secrets
- RESEND_API_KEY (required for emails)
- RESEND_FROM_EMAIL (verified sender email)
- WAITLIST_SLACK_WEBHOOK (optional, for Slack notifications)

🦄 Powered by Lazy Unicorn — lazyunicorn.ai