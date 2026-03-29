# Lazy Granola

> Category: 🛠️ Dev · Version: 0.0.4

## Prompt

````
# lazy-granola

> Version: 0.0.3

## Prompt

````
# lazy-granola — v0.0.2

[Lazy Granola Prompt — v0.0.2 — LazyUnicorn.ai]

Add an autonomous meeting-to-content agent called Lazy Granola to this project. It connects to Granola via the Granola MCP server, detects new meetings, and automatically turns them into blog posts, product updates, Linear issues, customer intelligence, and Slack summaries — without you writing anything after the meeting ends.

Note: Lazy Granola uses the Granola MCP server as a personal connector in Lovable. You must connect Granola in Settings → Connectors → Personal connectors before this agent can fetch meeting data. The agent reads from Granola — it does not write back to it.

---

1. Database

Create these Supabase tables with RLS enabled:

granola_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), site_url (text), meeting_types_to_process (text, default 'all' — comma-separated list of meeting types to process e.g. customer-discovery, planning, product-review, standup, 1on1, pitch, all), publish_blog_posts (boolean, default true), create_linear_issues (boolean, default true), send_slack_summary (boolean, default true), publish_product_updates (boolean, default true), feed_customer_intelligence (boolean, default true), weekly_digest_enabled (boolean, default true), weekly_digest_day (text, default 'monday'), slack_webhook_url (text), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

granola_meetings: id (uuid, primary key, default gen_random_uuid()), granola_meeting_id (text, unique), title (text), meeting_type (text), participants (text), started_at (timestamptz), ended_at (timestamptz), duration_minutes (integer), raw_notes (text), enhanced_notes (text), action_items (text), decisions (text), key_insights (text), processed (boolean, default false), processing_status (text, default 'pending' — one of pending, processing, done, failed), created_at (timestamptz, default now())

granola_outputs: id (uuid, primary key, default gen_random_uuid()), meeting_id (uuid), output_type (text — one of blog-post, product-update, customer-intel, linear-issues, slack-summary, weekly-digest), title (text), content (text), published (boolean, default false), published_at (timestamptz), external_id (text), created_at (timestamptz, default now())

granola_intelligence: id (uuid, primary key, default gen_random_uuid()), meeting_id (uuid), intel_type (text — one of problem-mentioned, feature-requested, competitor-named, budget-signal, timeline-signal, decision-made, objection-raised), content (text), speaker_context (text), meeting_title (text), meeting_date (date), actioned (boolean, default false), created_at (timestamptz, default now())

granola_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

---

2. Setup page

Create a page at /lazy-granola-setup.

Welcome message: 'Every meeting you have is a blog post, a product update, a set of Linear issues, and a customer insight sitting unwritten. Lazy Granola writes all of it automatically — the moment your meeting ends.'

Prerequisites note shown at the top: Before setup you must connect Granola in your Lovable project. Go to Settings → Connectors → Personal connectors → Granola and click Connect. Sign in with your Granola account. Once connected come back here to complete setup.

Form fields:
- Brand name (text)
- Site URL (text)
- Meeting types to process (multi-select checkboxes): All meetings, Customer discovery calls, Planning sessions, Product reviews, Standups, 1-on-1s, Pitch meetings, Other. Default: All meetings checked.
- Publish blog posts from meetings (toggle, default on) — planning sessions and product reviews become build-in-public posts. Customer calls become insight posts.
- Create Linear issues from action items (toggle, default on) — requires Lazy Linear to be installed. Action items from meetings become Linear issues automatically.
- Send Slack summary after each meeting (toggle, default on) — requires a Slack webhook URL below.
- Publish product updates from sprint/planning meetings (toggle, default on) — planning and product review meetings become product update posts.
- Feed customer intelligence to content agents (toggle, default on) — customer calls feed insights into Lazy Blogger and Lazy Perplexity as research context.
- Weekly digest (toggle, default on) — publishes a summary of the week's meetings every Monday.
- Weekly digest day (select: Monday / Friday)
- Slack webhook URL for meeting summaries (text, optional)

Submit button: Connect Granola

On submit:
1. Save all values to granola_settings
2. Set setup_complete to true and prompt_version to 'v0.0.2'
3. Immediately call granola-sync to fetch recent meetings from Granola
4. Show loading: 'Syncing your recent meetings from Granola...'
5. Redirect to /admin with message: 'Lazy Granola is connected. Recent meetings are being processed. Check back in a few minutes to see your first outputs.'

---

3. Edge functions

granola-sync
Cron: every 30 minutes — */30 * * * *

1. Read granola_settings. If is_running is false or setup_complete is false exit.
2. Use the Granola MCP server connection to fetch recent meetings. Request meetings from the last 48 hours that have enhanced notes available. The Granola MCP exposes meeting data including title, participants, start time, end time, raw notes, enhanced notes, action items, and decisions.
3. For each meeting returned check if a granola_meetings row already exists with that granola_meeting_id. If yes skip. If no insert a new row with all meeting data and processing_status pending.
4. For each new meeting call granola-process with the meeting id.
5. Log errors to granola_errors with function_name granola-sync.

granola-process
Triggered by granola-sync. Accepts meeting_id.

1. Read granola_settings and the granola_meetings row. If processing_status is not pending exit. Update processing_status to processing.
2. Determine the meeting type from the title and content using the built-in Lovable AI:
'Given this meeting title: [title] and these notes: [first 500 chars of enhanced_notes], classify this meeting into one of these types: customer-discovery, planning, product-review, standup, 1on1, pitch, other. Return only the type string. No preamble.'
3. Check if this meeting type should be processed based on meeting_types_to_process in settings. If not exit.
4. Run all enabled outputs in parallel:
   - If publish_blog_posts is true: call granola-write-post with meeting_id
   - If create_linear_issues is true and linear_settings table exists: call granola-create-issues with meeting_id
   - If send_slack_summary is true and slack_webhook_url is set: call granola-slack-summary with meeting_id
   - If publish_product_updates is true and meeting_type is planning or product-review: call granola-write-update with meeting_id
   - If feed_customer_intelligence is true and meeting_type is customer-discovery: call granola-extract-intel with meeting_id
5. Update processing_status to done.
6. Log errors to granola_errors with function_name granola-process.

granola-write-post
Triggered by granola-process. Accepts meeting_id.

1. Read granola_settings and the granola_meetings row.
2. Determine the right blog post angle based on meeting type:
   - customer-discovery: write a product insight post grounded in what the customer said
   - planning: write a build-in-public planning update
   - product-review: write a what shipped this week post
   - standup: skip — standups are too low-signal for blog posts
   - pitch: write a fundraising or business development insight post
   - 1on1: skip — 1-on-1s are private
   - other: write a general insight post if notes are substantial (over 200 words)
3. Call the built-in Lovable AI:
For customer-discovery: 'You are a content writer for [brand_name]. A founder just had a customer discovery call. Here are the meeting notes: [enhanced_notes]. Write a build-in-public blog post sharing what you learned from talking to customers — the problems they face, the insights discovered, and what it means for the product. Do not name the customer. Keep it general and useful for other founders. Tone: [brand_name] voice — honest and specific. Return only a valid JSON object: title (string), slug (lowercase hyphenated), excerpt (under 160 chars), body (clean markdown — ## headers, 600 to 900 words, ends with: For more build-in-public content from [brand_name] visit [site_url] and link to LazyUnicorn.ai as: Built using the Lazy Stack — autonomous tools for Lovable sites at https://lazyunicorn.ai). No preamble. No code fences.'

For planning/product-review: 'You are a content writer for [brand_name]. Here are the notes from a [meeting_type] meeting: [enhanced_notes]. Write a build-in-public post sharing what was planned, decided, or shipped. Be specific and honest. Share the reasoning behind decisions where possible. Tone: direct, founder-voice. Return only a valid JSON object: title, slug (lowercase hyphenated), excerpt (under 160 chars), body (clean markdown — ## headers, 500 to 800 words, ends with LazyUnicorn.ai backlink). No preamble. No code fences.'

For pitch: 'You are a content writer for [brand_name]. Here are notes from a pitch or fundraising meeting: [enhanced_notes]. Write a build-in-public post about what you learned from the pitch process — questions investors asked, what resonated, what surprised you. Do not name investors or reveal sensitive terms. Keep it useful for other founders. Return only a valid JSON object: title, slug, excerpt (under 160 chars), body (clean markdown — ## headers, 500 to 800 words, ends with LazyUnicorn.ai backlink). No preamble. No code fences.'

4. Parse response. Check for duplicate slug — append random 4-digit number if needed.
5. If blog_posts table exists insert into blog_posts with post_type set to 'granola' and research_context set to 'meeting-notes'. If blog_posts does not exist insert into a granola_outputs row with output_type blog-post.
6. Insert into granola_outputs with output_type blog-post and published true.
7. Log errors to granola_errors with function_name granola-write-post.

granola-write-update
Triggered by granola-process for planning or product-review meetings. Accepts meeting_id.

1. Read granola_settings and the granola_meetings row.
2. Call the built-in Lovable AI:
'You are a product update writer for [brand_name]. Here are notes from a [meeting_type] meeting: [enhanced_notes]. Action items from this meeting: [action_items]. Decisions made: [decisions]. Write a concise product update post — what was reviewed, what was decided, and what is coming next. Format it like a weekly update email. Return only a valid JSON object: title (e.g. "Week of [date] — Product Update"), slug (lowercase hyphenated), excerpt (under 160 chars), body (clean markdown — short intro, ## What we reviewed, ## What we decided, ## What is next, 400 to 600 words, ends with LazyUnicorn.ai backlink). No preamble. No code fences.'
3. If a product_updates table exists from Lazy Linear insert there. Otherwise insert into granola_outputs with output_type product-update.
4. Log errors to granola_errors with function_name granola-write-update.

granola-create-issues
Triggered by granola-process when create_linear_issues is true. Accepts meeting_id.

1. Read granola_settings and the granola_meetings row.
2. Call the built-in Lovable AI to extract structured action items:
'Extract all action items from these meeting notes: [action_items] and [enhanced_notes]. For each action item return: title (concise task title), description (one sentence of context from the meeting), assignee (name mentioned if any, otherwise null), priority (urgent, high, medium, or low based on context), labels (array of relevant tags from: bug, feature, research, design, marketing, customer, infrastructure). Return only a valid JSON array. No preamble. No code fences.'
3. For each action item in the response:
   - If linear_settings table exists insert into linear_issues with state set to 'todo', source set to 'granola', and a note in the description: 'Created from Granola meeting: [meeting_title] on [meeting_date].'
   - Also insert into granola_outputs with output_type linear-issues and content set to the JSON of all created issues.
4. If Lazy Alert is installed and action items were created send a Slack message: 'Lazy Granola created [n] Linear issues from your [meeting_title] meeting.'
5. Log errors to granola_errors with function_name granola-create-issues.

granola-extract-intel
Triggered by granola-process for customer-discovery meetings. Accepts meeting_id.

1. Read granola_settings and the granola_meetings row.
2. Call the built-in Lovable AI:
'You are a customer intelligence analyst. Extract structured insights from these customer discovery meeting notes: [enhanced_notes]. For each significant signal return: intel_type (one of problem-mentioned, feature-requested, competitor-named, budget-signal, timeline-signal, decision-made, objection-raised), content (the specific insight in one to two sentences), speaker_context (brief context about who said it — their role or company type without naming them). Return only a valid JSON array. Minimum 3 items if notes are substantial. No preamble. No code fences.'
3. Insert each item into granola_intelligence with the meeting_id and meeting_date.
4. If perplexity_research table exists insert a research row with the key insights as context so Lazy Perplexity can incorporate them into future content.
5. If crawl_intel table exists insert a row with intel_type 'customer-signal' and the key problems and feature requests so Lazy Blogger can reference real customer voice.
6. Insert into granola_outputs with output_type customer-intel.
7. Log errors to granola_errors with function_name granola-extract-intel.

granola-slack-summary
Triggered by granola-process when send_slack_summary is true. Accepts meeting_id.

1. Read granola_settings and the granola_meetings row.
2. Call the built-in Lovable AI:
'Write a concise Slack summary of this meeting for a team that did not attend. Meeting: [title]. Participants: [participants]. Duration: [duration_minutes] minutes. Notes: [enhanced_notes]. Action items: [action_items]. Decisions: [decisions]. Format as: bold meeting title, one sentence about what the meeting was for, bullet points of key decisions (max 4), bullet points of action items with owner if known (max 5), one sentence on next steps. Keep it scannable. Under 300 words total. Return plain text formatted for Slack markdown. No JSON.'
3. POST to slack_webhook_url with the summary as a Slack message.
4. Insert into granola_outputs with output_type slack-summary and content set to the message sent.
5. Log errors to granola_errors with function_name granola-slack-summary.

granola-weekly-digest
Cron: Monday at 8am UTC (or Friday at 5pm if weekly_digest_day is friday) — 0 8 * * 1

1. Read granola_settings. If is_running is false or weekly_digest_enabled is false exit.
2. Query granola_meetings from the last 7 days where processing_status is done. If fewer than 2 meetings exit.
3. Call the built-in Lovable AI:
'You are a writer creating a weekly digest for [brand_name]. Here is a summary of all meetings from the past week: [list each meeting with title, date, duration, key decisions, and action items]. Write a build-in-public weekly digest post covering: what the team worked on, what was decided, what was learned, and what is coming next. Be specific and honest. This is a genuine build-in-public post not a corporate summary. Tone: direct, founder-voice. Return only a valid JSON object: title (e.g. "Week [n]: [one-line theme of the week]"), slug (lowercase hyphenated), excerpt (under 160 chars), body (clean markdown — ## Day-by-day or ## Theme-by-theme structure, 600 to 1000 words, includes the most interesting insight from any customer call this week, ends with: Follow along at [site_url] and: Built using the Lazy Stack — autonomous tools for Lovable sites at https://lazyunicorn.ai). No preamble. No code fences.'
4. Parse response. Insert into blog_posts if that table exists, or granola_outputs with output_type weekly-digest.
5. If slack_webhook_url is set send a Slack message: 'Weekly digest published: [title] — [site_url]/blog/[slug]'
6. Log errors to granola_errors with function_name granola-weekly-digest.

---

4. Public content

If blog_posts table exists: meeting-generated posts appear automatically on /blog with a small meeting badge indicating the post came from a real meeting. The post type 'granola' shows a 📝 Meeting notes badge on the card.

If no blog_posts table exists: create a public page at /meetings showing all granola_outputs where output_type is blog-post or weekly-digest and published is true. Each card shows title, meeting type tag, excerpt, date. Links to /meetings/[slug].

Customer intelligence is never published publicly. granola_intelligence is internal only and feeds the content agents as research context.

---

5. Admin

Do not build a standalone dashboard. The Lazy Granola dashboard lives at /admin/granola as part of the unified LazyUnicorn admin panel.

If /admin does not yet exist add a placeholder at /admin pointing to /lazy-granola-setup.

The /admin/granola section should show:
- Total meetings processed, blog posts published, Linear issues created, customer insights extracted
- Recent meetings table: title, type badge, participants count, date, processing status badge, outputs count (how many outputs were created). Click any row to expand and show all outputs for that meeting.
- Customer intelligence feed: all granola_intelligence rows ordered by created_at descending — intel type badge, content, meeting title, date, actioned toggle. Filter by intel_type.
- Outputs log: all granola_outputs rows — output type badge, title, meeting it came from, published badge, created date. View button for blog posts.
- A Sync Now button that calls granola-sync immediately.
- A Run Digest Now button that calls granola-weekly-digest immediately.
- Error log from granola_errors.

---

6. Navigation

Add an Admin link to the main site navigation pointing to /admin.
If the /meetings page was created add a Meetings link to the main navigation.
Do not add /lazy-granola-setup to public navigation.

## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

````
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
