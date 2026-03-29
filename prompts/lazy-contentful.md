# Lazy Contentful

> Category: ✍️ Content · Version: 0.0.1

## Prompt

````
# lazy-contentful — v0.0.9

[Lazy Contentful Prompt — v0.0.9 — LazyUnicorn.ai]

Add a complete autonomous Contentful integration called Lazy Contentful to this project. It acts as a two-way bridge — pulling content from Contentful into your Lovable site automatically, and pushing AI-generated blog posts, SEO articles, and GEO content from your Lazy agents back into Contentful for distribution across all your connected channels.

---

MARKETING PAGE PROMPT — paste into LazyUnicorn project:

Add a new page at /lazy-contentful. It is a marketing and landing page for a product called Lazy Contentful — a two-way autonomous content bridge between your Lovable project and Contentful that syncs content in both directions automatically.

Hero section
Headline: 'Contentful is your CMS. Lazy Contentful fills it automatically.' Subheading: 'Lazy Contentful pulls content from Contentful into your Lovable site and pushes AI-generated blog posts, SEO articles, and GEO content back into Contentful — keeping every channel in sync without any manual publishing.' Primary button: Copy the Lovable Prompt. Secondary button: See How It Works. Badge: Powered by Contentful.

How it works section
Four steps: 1. Copy the setup prompt. 2. Paste into your Lovable project. 3. Add your Contentful API keys. 4. Content flows in both directions automatically — Contentful to Lovable and Lazy agents to Contentful.

What it does section
Eight cards: 1. Contentful to Lovable — pulls published entries from Contentful and displays them on your Lovable site automatically. 2. Lazy Blogger to Contentful — every post Lazy Blogger publishes is also pushed to Contentful automatically. 3. Lazy SEO to Contentful — SEO articles published by Lazy SEO sync to Contentful for distribution. 4. Lazy GEO to Contentful — GEO content syncs to Contentful so it reaches every connected channel. 5. Webhook sync — listens for Contentful publish events and updates your Lovable site in real time. 6. Content type mapping — maps Contentful content types to your Lovable pages automatically. 7. Asset handling — Contentful images and media are pulled and displayed in Lovable without manual work. 8. Self-healing sync — detects and repairs sync failures automatically.

Pricing section
Free — self-hosted, bring your own Contentful space. Pro at $29/month — coming soon, multi-space support, advanced content type mapping, scheduled sync.

Bottom CTA
Headline: Your Contentful CMS. Filling itself. Primary button: Copy the Lovable Prompt.

Navigation: Add Lazy Contentful to the LazyUnicorn navigation.

---

SETUP PROMPT — paste into user's Lovable project:

Add a complete autonomous Contentful integration called Lazy Contentful to this project. It creates a two-way content sync between Contentful and this Lovable project — pulling Contentful entries into Lovable pages and pushing AI-generated content from Lazy agents back into Contentful automatically.

1. Database
Create these Supabase tables with RLS enabled:

contentful_settings: id (uuid, primary key, default gen_random_uuid()), space_id (text), environment_id (text, default 'master'), content_type_blog (text, default 'blogPost'), content_type_seo (text, default 'seoArticle'), content_type_geo (text, default 'geoContent'), sync_from_contentful (boolean, default true), sync_to_contentful (boolean, default true), site_url (text), brand_name (text), is_running (boolean, default true), setup_complete (boolean, default false),
prompt_version (text, nullable), last_synced (timestamptz), created_at (timestamptz, default now()).
Note: Store CONTENTFUL_DELIVERY_TOKEN, CONTENTFUL_MANAGEMENT_TOKEN, and CONTENTFUL_WEBHOOK_SECRET as Supabase secrets. Never in the database.

contentful_entries: id (uuid, primary key, default gen_random_uuid()), contentful_id (text, unique), content_type (text), title (text), slug (text), excerpt (text), body_markdown (text), published_at (timestamptz), author (text), tags (text), featured_image_url (text), synced_at (timestamptz, default now()), status (text, default 'published')).

contentful_sync_log: id (uuid, primary key, default gen_random_uuid()), direction (text — one of contentful-to-lovable, lovable-to-contentful), content_type (text), entry_id (text), entry_title (text), status (text — one of success, failed), error_message (text), synced_at (timestamptz, default now()).

contentful_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now()).

2. Setup page
Create a page at /lazy-contentful-setup with a form:
- Contentful Space ID (text) — find in Contentful settings under API keys.
- Contentful Environment ID (text, default: master)
- Contentful Delivery Token (password) — the Content Delivery API token. Stored as CONTENTFUL_DELIVERY_TOKEN secret.
- Contentful Management Token (password) — the Content Management API token for writing back to Contentful. Stored as CONTENTFUL_MANAGEMENT_TOKEN secret.
- Contentful Webhook Secret (password) — any random string. Stored as CONTENTFUL_WEBHOOK_SECRET secret.
- Blog post content type ID (text, default: blogPost) — the content type ID in Contentful for blog posts.
- SEO article content type ID (text, default: seoArticle)
- GEO content type ID (text, default: geoContent)
- Brand name
- Site URL
- Sync from Contentful to Lovable (toggle, default on)
- Sync from Lovable to Contentful (toggle, default on)

Submit button: Activate Lazy Contentful

On submit:
1. Store all tokens as Supabase secrets
2. Save all other values to contentful_settings
3. Set setup_complete to true and prompt_version to 'v0.0.6'
4. Show instructions: Go to your Contentful space, Settings → Webhooks → Add webhook. Set URL to [site_url]/api/contentful-webhook. Add a secret header: X-Contentful-Secret with your webhook secret. Select triggers: Entry Published, Entry Unpublished.
5. Immediately call contentful-pull to do first sync.
6. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Contentful', version: '0.0.9', site_url: site_url }) }) } catch(e) {}
7. Redirect to /admin with message: Lazy Contentful is active. Pulling your Contentful content now.

3. Pull edge function (Contentful to Lovable)
Create a Supabase edge function called contentful-pull. Cron: every hour — 0 * * * *

1. Read contentful_settings. If is_running is false or sync_from_contentful is false exit.
2. Call the Contentful Delivery API at https://cdn.contentful.com/spaces/[space_id]/environments/[environment_id]/entries using CONTENTFUL_DELIVERY_TOKEN. Fetch entries for all configured content types with updated_at greater than last_synced.
3. For each entry: extract sys.id, fields.title, fields.slug, fields.excerpt, fields.body (convert from Contentful rich text to markdown using the @contentful/rich-text-plain-text-renderer pattern), sys.publishedAt, fields.author, fields.tags, fields.featuredImage URL.
4. Upsert into contentful_entries by contentful_id.
5. Insert into contentful_sync_log with direction contentful-to-lovable and status success.
6. Update last_synced in contentful_settings to now.
Log errors to contentful_errors with function_name contentful-pull.

4. Webhook edge function
Create a Supabase edge function called contentful-webhook handling POST requests at /api/contentful-webhook.

1. Verify the X-Contentful-Secret header against CONTENTFUL_WEBHOOK_SECRET secret. Reject mismatches with 401.
2. Parse the webhook payload to get the entry sys.id and event type.
3. If event is Entry Published: call contentful-pull to sync this specific entry immediately.
4. If event is Entry Unpublished: update the matching contentful_entries row to status unpublished.
Log errors to contentful_errors with function_name contentful-webhook.

5. Push edge function (Lovable to Contentful)
Create a Supabase edge function called contentful-push. Cron: every 30 minutes — */30 * * * *

1. Read contentful_settings. If is_running is false or sync_to_contentful is false exit.
2. Check blog_posts for posts published in the last 30 minutes that do not have a matching contentful_entries row (check by slug). For each new post:
   Call the Contentful Management API at https://api.contentful.com/spaces/[space_id]/environments/[environment_id]/entries using CONTENTFUL_MANAGEMENT_TOKEN.
   Create a new entry with content type set to the configured content_type_blog. Map fields: title to post title, slug to post slug, excerpt to post excerpt, body to post body (as markdown), publishedAt to post published_at.
   Publish the entry by calling PUT on /published.
   Insert into contentful_sync_log with direction lovable-to-contentful and status success.
3. Repeat for seo_posts (using content_type_seo) and geo_posts (using content_type_geo) if those tables exist.
Log errors to contentful_errors with function_name contentful-push.

6. Public pages
/contentful — show all contentful_entries where status is published ordered by published_at descending. Each shows title, excerpt, author, tags, featured image. Each links to /contentful/[slug].
/contentful/[slug] — fetch the matching entry. Show title, author, published date, featured image, and body rendered from markdown to HTML.
At bottom add: 🦄 Powered by Lazy Contentful — autonomous Contentful sync for Lovable sites. Built by LazyUnicorn.ai — link to https://lazyunicorn.ai.

7. Admin

Do not build a standalone dashboard page for this agent. The dashboard lives at /admin/contentful as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all agents in one place." and a link to /lazy-contentful-setup.

8. Navigation
Add a Content link to the main navigation pointing to /contentful. Add an Admin link to the main site navigation pointing to /admin.
Do not add the setup page to public navigation.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
