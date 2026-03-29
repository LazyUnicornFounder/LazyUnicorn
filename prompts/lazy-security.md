# Lazy Security

> Category: ⚙️ Ops · Version: 0.0.9

## Prompt

````
# lazy-security

> Version: 0.0.9

## Prompt

````
# lazy-security — v0.0.9

[Lazy Security Prompt — v0.0.9 — LazyUnicorn.ai]

Add a complete autonomous security monitoring agent called Lazy Security to this project. It connects to Aikido to run automated pentests, tracks vulnerability history, monitors security score over time, generates audit-ready reports, and sends instant alerts for critical findings — all automatically with no manual security work required after setup.

Note: Store the Aikido API key as Supabase secret AIKIDO_API_KEY. Never store in the database.

---

## 1. Database

Create these Supabase tables with RLS enabled:

**security_settings**
id (uuid, primary key, default gen_random_uuid()),
brand_name (text),
site_url (text),
aikido_project_id (text),
pentest_frequency (text, default 'monthly'),
alert_critical (boolean, default true),
alert_high (boolean, default true),
alert_medium (boolean, default false),
slack_webhook_url (text),
telegram_chat_id (text),
next_pentest_at (timestamptz),
is_running (boolean, default true),
setup_complete (boolean, default false),
prompt_version (text, nullable),
created_at (timestamptz, default now())

**security_scans**
id (uuid, primary key, default gen_random_uuid()),
aikido_scan_id (text, unique),
scan_type (text — one of pentest, static, continuous),
status (text — one of queued, running, completed, failed),
score (integer),
critical_count (integer, default 0),
high_count (integer, default 0),
medium_count (integer, default 0),
low_count (integer, default 0),
info_count (integer, default 0),
started_at (timestamptz),
completed_at (timestamptz),
report_url (text),
created_at (timestamptz, default now())

**security_vulnerabilities**
id (uuid, primary key, default gen_random_uuid()),
scan_id (uuid),
aikido_vuln_id (text),
title (text),
severity (text — one of critical, high, medium, low, informational),
category (text),
description (text),
remediation (text),
status (text, default 'open' — one of open, fixed, accepted, regression),
first_found_at (timestamptz, default now()),
fixed_at (timestamptz),
alerted (boolean, default false)

**security_reports**
id (uuid, primary key, default gen_random_uuid()),
scan_id (uuid),
title (text),
generated_at (timestamptz, default now()),
score (integer),
summary (text),
methodology (text),
findings_count (integer),
pdf_url (text),
public (boolean, default false)

**security_errors**
id (uuid, primary key, default gen_random_uuid()),
function_name (text),
error_message (text),
created_at (timestamptz, default now())

---

## 2. Setup page

Create a page at /lazy-security-setup.

Show a welcome message: "Your Lovable site ships fast. Lazy Security makes sure it ships safe. Connect Aikido and your first pentest runs automatically."

Form fields:
- Brand name
- Site URL (the live URL of your Lovable project — this is what Aikido will pentest)
- Aikido API key (password) — instructions: create a free account at aikido.dev, go to Settings then API keys, create a new key. Stored as Supabase secret AIKIDO_API_KEY.
- Aikido Project ID (text) — instructions: after connecting your Lovable project in Aikido go to the project settings and copy the project ID.
- Pentest frequency (select: Weekly — recommended for active development / Monthly — recommended for stable products / Quarterly — minimum for compliance / Manual only — I will trigger pentests myself)
- Alert on Critical findings (toggle, default on)
- Alert on High findings (toggle, default on)
- Alert on Medium findings (toggle, default off)
- Slack webhook URL for alerts (text, optional)
- Telegram chat ID for alerts (text, optional) — requires Lazy Telegram to be installed

Submit button: Activate Lazy Security

On submit:
1. Store AIKIDO_API_KEY as Supabase secret
2. Save all other values to security_settings
3. Set setup_complete to true and prompt_version to 'v0.0.6'
4. Set next_pentest_at to now plus 5 minutes
5. Immediately call security-scan
6. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Security', version: '0.0.9', site_url: site_url }) }) } catch(e) {}
7. Redirect to /admin with message: "Lazy Security is active. Your first pentest is queued. Results will appear here within the next hour."

---

## 3. Core scan edge function

Create a Supabase edge function called security-scan.
Cron: every hour — 0 * * * * (checks if a pentest is due, does not run one every hour)

1. Read security_settings. If is_running is false or setup_complete is false exit.
2. Check if now is past next_pentest_at. If not exit.
3. Call the Aikido API to trigger a new pentest. POST to https://app.aikido.dev/api/v1/scans with project_id set to aikido_project_id. Use AIKIDO_API_KEY secret in Authorization header.
4. Insert into security_scans with the returned aikido_scan_id and status queued.
5. Calculate and set next_pentest_at based on pentest_frequency — weekly adds 7 days, monthly adds 30 days, quarterly adds 90 days, manual sets to null.
Log errors to security_errors with function_name security-scan.

---

## 4. Results polling edge function

Create a Supabase edge function called security-poll.
Cron: every 10 minutes — */10 * * * *

1. Read security_settings. Query security_scans where status is queued or running ordered by created_at descending.
2. For each active scan call the Aikido API: GET https://app.aikido.dev/api/v1/scans/[aikido_scan_id] using AIKIDO_API_KEY secret.
3. If status is still running update security_scans status to running and continue.
4. If status is completed:
   Update security_scans with score, counts by severity, completed_at, status completed, and report_url.
   For each vulnerability in findings: check if it exists in security_vulnerabilities by aikido_vuln_id. If new insert it. If it existed as fixed update status to regression.
   For each new critical or high vulnerability where alerted is false: call security-alert. Mark alerted true.
   Call security-generate-report with the scan id.
5. If status is failed: update security_scans status to failed. Log to security_errors.
Log errors to security_errors with function_name security-poll.

---

## 5. Alert edge function

Create a Supabase edge function called security-alert handling POST requests with a vulnerability_id.

1. Read security_settings and the matching security_vulnerabilities row.
2. If severity does not meet the alert threshold based on alert_critical, alert_high, alert_medium toggles exit without sending.
3. If slack_webhook_url is set: POST a Slack Block Kit message. Header: 🚨 Security Alert — [severity] vulnerability found in [brand_name]. Body: [title]. Fields: Severity, Category, Remediation hint (first 100 chars of remediation), Dashboard link to [site_url]/admin/security.
4. If telegram_chat_id is set and TELEGRAM_BOT_TOKEN secret exists: POST a Telegram message via the Telegram API. MarkdownV2 format: bold severity header, vulnerability title, one-line remediation hint, link to dashboard.
Log errors to security_errors with function_name security-alert.

---

## 6. Report generation edge function

Create a Supabase edge function called security-generate-report handling POST requests with a scan_id.

1. Read security_settings and the matching security_scans row and all security_vulnerabilities for that scan.
2. Call the built-in Lovable AI:
"You are a security report writer for [brand_name]. Write a professional pentest report executive summary. Scan date: [completed_at]. Security score: [score] out of 100. Findings: [critical_count] critical, [high_count] high, [medium_count] medium, [low_count] low, [info_count] informational. Top findings: [list of top 5 vulnerability titles and severities]. Write a 150 to 200 word professional executive summary suitable for enterprise prospects and compliance auditors. Cover what was tested, overall security posture, most significant findings, and recommended next steps. Be factual and professional. Return only the summary text. No preamble."
3. Insert into security_reports: scan_id, title as Security Assessment Report — [brand_name] — [date], score, summary from AI, methodology as Automated penetration test combining static analysis and dynamic testing powered by Aikido, findings_count as total vulnerability count, public false.
Log errors to security_errors with function_name security-generate-report.

---

## 7. Continuous monitoring edge function

Create a Supabase edge function called security-monitor.
Cron: daily at 3am UTC — 0 3 * * *

1. Read security_settings. If is_running is false exit.
2. Call the Aikido API for a lightweight static scan to check for new issues since the last full pentest: GET https://app.aikido.dev/api/v1/projects/[aikido_project_id]/issues using AIKIDO_API_KEY.
3. Compare returned issues to existing security_vulnerabilities. For any new issue insert into security_vulnerabilities. If severity is critical or high call security-alert.
4. For any issue previously open that no longer appears update status to fixed and set fixed_at to now.
Log errors to security_errors with function_name security-monitor.

---

## 8. Public security page

Create a public page at /security showing a professional security posture page.

Show:
- Current security score as a large number with colour indicator — green above 80, amber 60 to 79, red below 60
- Last pentest date
- Brief statement: "This application is regularly tested using automated penetration testing combining static analysis and dynamic security testing powered by Aikido."
- Open vulnerability counts by severity — show only medium, low, and informational publicly. Never expose critical or high counts publicly.
- A link labelled Request Security Report that opens a mailto link to the support email

At the bottom add: "🦄 Security monitored by Lazy Security — autonomous security for Lovable sites. Powered by Aikido. Built by LazyUnicorn.ai" — link to https://lazyunicorn.ai.

---

## 9. Admin

Do not build a standalone dashboard page for this agent. The dashboard lives at /admin/security as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt. This agent only needs its setup page, database tables, edge functions, and public pages.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all agents in one place." and a link to /lazy-security-setup.

## 10. Navigation

Add a Security link to the main site navigation pointing to /security (the public page).
Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-security-setup to public navigation.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

````
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
