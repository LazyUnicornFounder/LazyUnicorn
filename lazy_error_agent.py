"""
LazyUnicorn Error Monitoring Agent
===================================
Reads error tables from all installed Lazy engines in Supabase,
diagnoses issues using Claude, and opens GitHub issues automatically.

Run this on a cron every hour:
  0 * * * * python3 /path/to/lazy_error_agent.py

Requirements:
  pip install anthropic supabase PyGithub python-dotenv

Environment variables (put in .env file):
  ANTHROPIC_API_KEY=your_anthropic_key
  SUPABASE_URL=your_supabase_url
  SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
  GITHUB_TOKEN=your_github_token
  GITHUB_REPO=your_username/lazyunicorn
  SLACK_WEBHOOK_URL=your_slack_webhook (optional)
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import anthropic
from supabase import create_client
from github import Github

load_dotenv()

# ── Clients ──────────────────────────────────────────────────────────────────
claude  = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
sb      = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
gh      = Github(os.environ["GITHUB_TOKEN"])
repo    = gh.get_repo(os.environ["GITHUB_REPO"])

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL")
ERROR_THRESHOLD = 3        # errors in the window before creating an issue
LOOKBACK_HOURS  = 1        # how far back to look for errors

# ── All known error tables across the Lazy Stack ─────────────────────────────
ERROR_TABLES = [
    "blogger_errors",
    "seo_errors",
    "geo_errors",
    "crawl_errors",
    "perplexity_errors",
    "store_errors",
    "pay_errors",
    "sms_errors",
    "voice_errors",
    "stream_errors",
    "code_errors",
    "gitlab_errors",
    "linear_errors",
    "alert_errors",
    "telegram_errors",
    "contentful_errors",
    "supabase_errors",
    "security_errors",
    "design_errors",
    "auth_errors",
    "drop_errors",
    "granola_errors",
    "print_errors",
    "youtube_errors",
    "mail_errors",
]

# ── Helper: send Slack notification ──────────────────────────────────────────
def notify_slack(message: str):
    if not SLACK_WEBHOOK:
        return
    try:
        requests.post(SLACK_WEBHOOK, json={"text": message}, timeout=5)
    except Exception:
        pass

# ── Step 1: Fetch recent errors from all tables ───────────────────────────────
def fetch_errors() -> dict[str, list[dict]]:
    """
    Query every error table. Returns a dict of
    { table_name: [error_rows] } for tables that exist and have errors.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)).isoformat()
    found  = {}

    for table in ERROR_TABLES:
        try:
            result = (
                sb.table(table)
                  .select("*")
                  .gte("created_at", cutoff)
                  .order("created_at", desc=True)
                  .execute()
            )
            if result.data:
                found[table] = result.data
        except Exception:
            # Table doesn't exist — engine not installed, skip silently
            pass

    return found

# ── Step 2: Check for existing open GitHub issues ────────────────────────────
def get_open_issue_titles() -> set[str]:
    """Return titles of all currently open GitHub issues."""
    open_issues = repo.get_issues(state="open", labels=["lazy-error"])
    return {issue.title for issue in open_issues}

# ── Step 3: Diagnose errors using Claude ─────────────────────────────────────
def diagnose_errors(table: str, errors: list[dict]) -> dict:
    """
    Ask Claude to analyse the errors for one engine and return
    a structured diagnosis with recommended fix.
    """
    # Derive engine name from table name e.g. blogger_errors → Lazy Blogger
    engine_name = "Lazy " + table.replace("_errors", "").replace("_", " ").title()

    error_summary = json.dumps(errors[:10], indent=2, default=str)

    prompt = f"""You are a senior engineer reviewing error logs for {engine_name} —
an autonomous Lovable site engine built on Supabase edge functions.

Here are the {len(errors)} errors from the last {LOOKBACK_HOURS} hour(s):

{error_summary}

Diagnose the root cause and provide a fix recommendation.

Return ONLY a valid JSON object with these fields:
- severity: "critical" | "high" | "medium" (critical = engine completely broken, high = partial failure, medium = occasional errors)
- root_cause: one sentence describing the most likely cause
- affected_function: the edge function name most likely responsible
- recommended_fix: 2-3 specific actionable steps to fix it
- github_issue_title: a concise issue title (max 80 chars) starting with [{engine_name}]
- github_issue_body: a full markdown GitHub issue body with sections: ## Error Summary, ## Root Cause, ## Recommended Fix, ## Error Samples (show 3 example errors)

No preamble. No code fences."""

    response = claude.messages.create(
        model="claude-opus-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return json.loads(response.content[0].text)
    except Exception:
        # Fallback if JSON parsing fails
        return {
            "severity": "high",
            "root_cause": "Unable to parse diagnosis",
            "affected_function": "unknown",
            "recommended_fix": "Manually review error logs",
            "github_issue_title": f"[{engine_name}] {len(errors)} errors in last hour",
            "github_issue_body": f"## Error Summary\n\n{len(errors)} errors detected.\n\n## Error Samples\n\n```json\n{error_summary[:2000]}\n```"
        }

# ── Step 4: Open a GitHub issue ───────────────────────────────────────────────
def open_github_issue(diagnosis: dict, error_count: int) -> str:
    """Create a GitHub issue and return its URL."""
    severity = diagnosis.get("severity", "high")

    # Severity → label colour mapping
    label_map = {
        "critical": "critical-error",
        "high":     "high-error",
        "medium":   "medium-error",
    }

    # Ensure labels exist on the repo
    existing_labels = {l.name for l in repo.get_labels()}
    label_name = label_map.get(severity, "high-error")

    for needed in ["lazy-error", label_name]:
        if needed not in existing_labels:
            color = "d73a4a" if "critical" in needed else "e4e669" if "medium" in needed else "e99695"
            repo.create_label(needed, color)

    body = diagnosis["github_issue_body"] + f"""

---
*🤖 Auto-generated by LazyUnicorn Error Monitoring Agent*
*Detected: {error_count} errors in the last {LOOKBACK_HOURS} hour(s)*
*Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*

@claude Please investigate and fix this issue following CLAUDE.md rules."""

    issue = repo.create_issue(
        title=diagnosis["github_issue_title"],
        body=body,
        labels=["lazy-error", label_name]
    )
    return issue.html_url

# ── Step 5: Generate weekly summary report ───────────────────────────────────
def generate_weekly_summary(all_errors: dict) -> str:
    """Ask Claude to write a weekly ops summary from all errors found."""
    if not all_errors:
        return "✅ No errors detected across all engines this run."

    summary_data = {
        table: len(errors)
        for table, errors in all_errors.items()
    }

    response = claude.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"""Write a brief Slack-friendly ops summary for LazyUnicorn.
Error counts by engine this hour: {json.dumps(summary_data, indent=2)}
Format: emoji + engine name + error count + one-line status.
Keep it under 200 words. No preamble."""
        }]
    )
    return response.content[0].text

# ── Main agent loop ───────────────────────────────────────────────────────────
def run_agent():
    print(f"\n{'='*60}")
    print(f"LazyUnicorn Error Agent — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    # 1. Fetch errors
    print("\n📊 Fetching errors from Supabase...")
    all_errors = fetch_errors()

    if not all_errors:
        print("✅ No errors found across any engine. All clear.")
        return

    total_errors = sum(len(e) for e in all_errors.values())
    print(f"⚠️  Found errors in {len(all_errors)} engine(s). Total: {total_errors} errors.")

    # 2. Get existing issues to avoid duplicates
    print("\n🔍 Checking existing GitHub issues...")
    open_titles = get_open_issue_titles()

    issues_opened = []
    issues_skipped = []

    for table, errors in all_errors.items():
        engine_name = "Lazy " + table.replace("_errors", "").replace("_", " ").title()
        print(f"\n🔧 Analysing {engine_name} — {len(errors)} error(s)...")

        # Only open issue if above threshold
        if len(errors) < ERROR_THRESHOLD:
            print(f"   ↳ Below threshold ({ERROR_THRESHOLD}), skipping.")
            continue

        # Diagnose with Claude
        diagnosis = diagnose_errors(table, errors)
        issue_title = diagnosis.get("github_issue_title", f"[{engine_name}] Errors detected")

        # Skip if issue already open
        if issue_title in open_titles:
            print(f"   ↳ Issue already open, skipping.")
            issues_skipped.append(engine_name)
            continue

        # Open GitHub issue
        issue_url = open_github_issue(diagnosis, len(errors))
        issues_opened.append({
            "engine":   engine_name,
            "severity": diagnosis.get("severity"),
            "count":    len(errors),
            "url":      issue_url
        })
        print(f"   ↳ ✅ Issue opened: {issue_url}")

        # Rate limit — be kind to APIs
        time.sleep(1)

    # 3. Summary report
    print(f"\n{'='*60}")
    print(f"Summary: {len(issues_opened)} issue(s) opened, {len(issues_skipped)} skipped (already open)")

    # 4. Slack notification
    if issues_opened:
        slack_lines = [f"🚨 *LazyUnicorn Error Agent* — {datetime.now(timezone.utc).strftime('%H:%M UTC')}"]
        for item in issues_opened:
            severity_emoji = "🔴" if item["severity"] == "critical" else "🟡" if item["severity"] == "high" else "🟠"
            slack_lines.append(
                f"{severity_emoji} *{item['engine']}* — {item['count']} errors → <{item['url']}|View Issue>"
            )
        slack_lines.append(f"\n@claude has been tagged to investigate each issue.")
        notify_slack("\n".join(slack_lines))
    else:
        summary = generate_weekly_summary(all_errors)
        print(f"\n{summary}")
        if SLACK_WEBHOOK:
            notify_slack(f"📊 LazyUnicorn Error Agent\n{summary}")

if __name__ == "__main__":
    run_agent()
