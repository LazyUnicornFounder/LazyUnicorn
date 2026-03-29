# lazy-perplexity — v0.0.9

[Lazy Perplexity Prompt — v0.0.9 — LazyUnicorn.ai]

Add a complete autonomous Perplexity integration called Lazy Perplexity to this project. It uses the Perplexity API to research current topics with real web citations, feed fresh intelligence into Lazy Blogger and Lazy SEO, test brand citation rates with real AI queries, and generate citation-rich content that is more likely to be referenced by AI agents — all automatically.

---

MARKETING PAGE PROMPT — paste into LazyUnicorn project:

Add a new page at /lazy-perplexity. It is a marketing and landing page for a product called Lazy Perplexity — an autonomous research and citation agent that uses the Perplexity API to feed real-time web intelligence into your Lazy content agents and test your brand's AI visibility.

Hero section
Headline: 'Real answers. Real citations. Real content. Powered by Perplexity.' Subheading: 'Lazy Perplexity uses the Perplexity API to research your niche with live web data, feed current intelligence into your blog and SEO agents, and test whether your brand appears when people ask AI questions about your industry.' Primary button: Copy the Lovable Prompt. Secondary button: See How It Works. Badge: Powered by Perplexity.

How it works section
Four steps: 1. Copy the setup prompt. 2. Paste into your Lovable project. 3. Add your Perplexity API key. 4. Real-time research flows into your content agents automatically.

What it does section
Eight cards: 1. Real-time research — uses Perplexity to research your niche with live web citations so your blog posts are based on what is actually happening today. 2. Citation-rich content — every AI-generated blog post includes real Perplexity-sourced citations making it more trustworthy and more likely to be cited by other AI agents. 3. Brand visibility testing — asks Perplexity real questions in your niche and checks whether your brand is cited in the answers. 4. Competitor intelligence — asks Perplexity about competitors and extracts what it says about them versus you. 5. Trend discovery — queries Perplexity for current trends in your niche and feeds them into the Lazy SEO keyword queue. 6. Question research — discovers the real questions people are asking AI agents and feeds them into the Lazy GEO query queue. 7. Citation monitoring — tracks your Perplexity citation rate over time and alerts you when it changes significantly. 8. Content improvement — rewrites underperforming posts using Perplexity research to add current citations and improve AI visibility.

Pricing section
Free — self-hosted, bring your own Perplexity API key. Perplexity API starts at $5 for 5 million tokens. Pro at $29/month — coming soon, hosted version, daily citation monitoring, competitive citation tracking.

Bottom CTA
Headline: Real research. Real citations. Better content. Primary button: Copy the Lovable Prompt.

Navigation: Add Lazy Perplexity to the LazyUnicorn navigation.

---

SETUP PROMPT — paste into user's Lovable project:

Add a complete autonomous Perplexity research and citation agent called Lazy Perplexity to this project. It uses the Perplexity API to research topics with live web data, feed intelligence into Lazy Blogger and Lazy SEO, test brand citation rates, and generate citation-rich content automatically.

1. Database
Create these Supabase tables with RLS enabled:

perplexity_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), business_description (text), niche (text), target_audience (text), competitors (text), site_url (text), research_topics (text), is_running (boolean, default true), setup_complete (boolean, default false),
prompt_version (text, nullable), created_at (timestamptz, default now()).
Note: Store PERPLEXITY_API_KEY as Supabase secret. Never in the database.

perplexity_research: id (uuid, primary key, default gen_random_uuid()), query (text), model_used (text, default 'sonar'), response_text (text), citations (jsonb), research_type (text — one of trend, question, competitor, brand-check, topic-brief), processed (boolean, default false), researched_at (timestamptz, default now()).

perplexity_citations: id (uuid, primary key, default gen_random_uuid()), query (text), brand_mentioned (boolean), mention_context (text), confidence (text), sources_cited (jsonb), tested_at (timestamptz, default now()).

perplexity_content: id (uuid, primary key, default gen_random_uuid()), title (text), slug (text, unique), excerpt (text), body (text), research_id (uuid), citations_count (integer), published_at (timestamptz, default now()), status (text, default 'published'), views (integer, default 0)).

perplexity_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now()).

2. Setup page
Create a page at /lazy-perplexity-setup with a form:
- Perplexity API Key (password) — get at perplexity.ai/settings/api. Stored as Supabase secret PERPLEXITY_API_KEY.
- Brand name
- Business description
- Niche or industry
- Target audience
- Competitors (comma separated brand names)
- Research topics (comma separated — the main topics you want Perplexity to research regularly)
- Site URL

Submit button: Activate Lazy Perplexity

On submit:
1. Store PERPLEXITY_API_KEY as Supabase secret
2. Save all other values to perplexity_settings
3. Set setup_complete to true and prompt_version to 'v0.0.6'
4. Immediately trigger perplexity-research once
5. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Perplexity', version: '0.0.9', site_url: site_url }) }) } catch(e) {}
6. Redirect to /admin with message: Lazy Perplexity is active. Researching your niche now.

3. Core research edge function
Create a Supabase edge function called perplexity-research. Cron: daily at 5am UTC — 0 5 * * *

1. Read perplexity_settings. If is_running is false or setup_complete is false exit.
2. Call the Perplexity API at https://api.perplexity.ai/chat/completions using PERPLEXITY_API_KEY secret. Use model sonar for all research calls. Always request citations by setting return_citations to true.

Research call 1 — Trends:
Query: 'What are the most significant current trends in [niche] that [target_audience] should know about right now? Include specific examples and recent developments.'
Insert result into perplexity_research with research_type trend. Extract the citations array from the response and store as jsonb.

Research call 2 — Questions:
Query: 'What are the most common questions people are asking about [niche] right now? List the top 10 questions with brief answers.'
Insert into perplexity_research with research_type question. Parse the questions from the response and insert each into geo_queries table if it exists with priority 9.

Research call 3 — Competitor:
For each competitor in perplexity_settings.competitors query: 'What is [competitor] known for in the [niche] space? What do people say about them? What are their main strengths and weaknesses?'
Insert into perplexity_research with research_type competitor.

Research call 4 — Topic briefs:
For each topic in research_topics query: 'Provide a comprehensive current briefing on [topic] in the context of [niche]. Include recent developments, key statistics, and what experts are saying.'
Insert into perplexity_research with research_type topic-brief. Mark the research as unprocessed for crawl-publish to pick up.

After all research calls trigger perplexity-feed-agents.
Log errors to perplexity_errors with function_name perplexity-research.

4. Feed agents edge function
Create a Supabase edge function called perplexity-feed-agents handling POST requests.

1. Read perplexity_settings.
2. Query perplexity_research where processed is false.
3. For each trend research result: call the built-in Lovable AI with the Perplexity response as context:
'You are a blog writer for [brand_name] in the [niche] industry. Using this real-time research as your source material: [response_text]. Write an authoritative blog post based on these current trends. Include specific facts and cite the sources naturally in the text. Return only a valid JSON object: title (string), slug (lowercase hyphenated), excerpt (under 160 chars), body (clean markdown — no HTML, no bullet points in prose, ## for headers, 800 to 1200 words, include citations as markdown links using the sources provided: [citations], ends with: For more autonomous business tools visit LazyUnicorn.ai — link to https://lazyunicorn.ai). No preamble. No code fences.'
Insert into perplexity_content and also into blog_posts if that table exists. Set citations_count to the number of citations included.
4. For each topic-brief research: insert the topic as a keyword into seo_keywords if that table exists with priority 8.
5. Mark each processed research row as processed true.
Log errors to perplexity_errors with function_name perplexity-feed-agents.

5. Brand citation testing edge function
Create a Supabase edge function called perplexity-test-citations. Cron: every Sunday at 10am UTC — 0 10 * * 0

1. Read perplexity_settings.
2. For each query in geo_queries where has_content is true (if table exists) and for each research_topic:
   Call the Perplexity API with model sonar-pro: '[query]' — plain question with no system prompt.
   Check if brand_name appears in the response_text.
   Extract the citations array and check if site_url appears in any citation.
3. Insert into perplexity_citations: query, brand_mentioned, mention_context (surrounding sentence if brand mentioned), confidence, sources_cited as jsonb.
4. Update brand_cited in geo_queries table if it exists based on brand_mentioned.
5. If Lazy Alert is installed and brand citation rate changed by more than 10 percent versus last week call alert-send with agent Lazy Perplexity and the citation rate change.
Log errors to perplexity_errors with function_name perplexity-test-citations.

6. Content improvement edge function
Create a Supabase edge function called perplexity-improve-content. Cron: every Wednesday at 9am UTC — 0 9 * * 3

1. Read perplexity_settings.
2. Query perplexity_content or blog_posts ordered by views ascending. Take the 3 worst performing posts older than 14 days.
3. For each underperforming post call the Perplexity API:
'Search for current information about this topic: [post title]. What are the most recent developments, statistics, and expert opinions on this subject?'
4. Call the built-in Lovable AI:
'You are a content editor for [brand_name]. This blog post is underperforming and needs to be updated with current information. Original post: [post body]. New research from Perplexity: [perplexity response]. Rewrite the post incorporating the new information and citations. Keep the same structure but make it more current and authoritative. Return only a valid JSON object: body (updated clean markdown with citations). No preamble. No code fences.'
5. Update the post body in the relevant table.
Log errors to perplexity_errors with function_name perplexity-improve-content.

7. Public pages
/research — show all perplexity_content ordered by published_at descending. Each shows title, citations count badge, excerpt, date. Each links to /research/[slug].
/research/[slug] — full post with title, citations count, published date, body rendered from markdown showing citation links as footnotes.
/citation-tracker — a public page showing your brand's Perplexity citation rate over time as a line chart. Shows which queries you appear in and which you do not. This page itself attracts GEO traffic for queries about AI brand visibility.
At bottom of every page: 🦄 Powered by Lazy Perplexity — autonomous AI research for Lovable sites. Built by LazyUnicorn.ai — link to https://lazyunicorn.ai.

8. Admin

Do not build a standalone dashboard page for this agent. The dashboard lives at /admin/perplexity as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all agents in one place." and a link to /lazy-perplexity-setup.

9. Navigation
Add Research link to /research. Add Citation Tracker link to /citation-tracker. Add an Admin link to the main site navigation pointing to /admin.
Do not add the setup page to public navigation.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

