# Infinity PPP — Design Spec

**Date:** 2026-03-31
**Product:** Infinity PPP
**Stack:** Lovable (React SPA) + Supabase (Postgres + Edge Functions)
**Scope:** Global real-time directory of Public-Private Partnership (PPP) projects

---

## 1. Overview

Infinity PPP is a standalone public website that aggregates, enriches, and displays PPP projects from around the world. Data is sourced automatically from structured APIs and web scraping, enriched by AI, and published via a confidence-scored auto-publish pipeline with a human review fallback. An admin panel provides full curation control.

**Initial focus region:** MENA. Architecture is global from day one.

**Target audiences:** Investors and advisors, government bodies and project sponsors, researchers and journalists, general public.

---

## 2. Architecture

Three layers:

**Ingestion layer** — Supabase edge functions run daily at 6am UTC. Pull from the World Bank PPI API, IsDB project database, and a configurable list of scraped sources (government portals, MEED, Reuters, regional news). Raw records land in `ppp_raw` with source metadata and an initial confidence score.

**Processing layer** — AI enrichment normalizes raw records into structured fields. Records scoring ≥ confidence threshold (default 0.8) auto-publish to `ppp_projects`. Records below threshold go to `ppp_review_queue` for human review.

**Presentation layer** — Public directory at `/` with search, filters, and an interactive Mapbox map. Project detail pages at `/projects/[id]`. Admin panel at `/admin`.

---

## 3. Database Schema

### `ppp_projects`
Live directory of published projects.

| Field | Type | Notes |
|---|---|---|
| id | uuid | primary key |
| name | text | project name |
| country | text | |
| region | text | e.g. MENA, Sub-Saharan Africa, Southeast Asia |
| sector | text | energy / transport / water / health / education / telecoms / social infrastructure |
| status | text | pipeline / procurement / awarded / financial-close / operational / completed / cancelled |
| total_value_usd | numeric | |
| public_contribution_usd | numeric | |
| private_investment_usd | numeric | |
| currency_original | text | original currency before USD conversion |
| government_sponsor | text | |
| private_operator | text | |
| lenders | text | |
| advisors | text | |
| announcement_date | date | |
| tender_date | date | |
| award_date | date | |
| financial_close_date | date | |
| completion_date | date | |
| lat | numeric | |
| lng | numeric | |
| source_url | text | |
| source_name | text | |
| confidence_score | numeric | 0–1 |
| is_verified | boolean | manually confirmed by admin |
| created_at | timestamptz | |
| updated_at | timestamptz | |

### `ppp_raw`
Staging table for all ingested records before processing.

Same shape as `ppp_projects` plus:
- `raw_payload` (jsonb) — original scraped/API response
- `processing_status` (text) — pending / processed / failed

### `ppp_review_queue`
Low-confidence records awaiting human review.

Fields: id (uuid, primary key), ppp_raw_id (uuid, foreign key → ppp_raw), extracted_fields (jsonb — the normalized fields from enrichment), confidence_score (numeric), reviewer_notes (text), reviewed_by (text), reviewed_at (timestamptz), review_action (text — approved / rejected), created_at (timestamptz).

### `ppp_sources`
Configurable source registry.

| Field | Type | Notes |
|---|---|---|
| id | uuid | primary key |
| name | text | |
| url | text | |
| type | text | api / scrape / manual |
| region | text | |
| is_active | boolean | |
| last_crawled_at | timestamptz | |
| crawl_frequency_hours | integer | default 24 |
| record_count | integer | total records ingested from this source |

### `ppp_errors`
Ingestion and enrichment errors: function_name, error_message, raw_id (nullable), created_at.

### `ppp_settings`
Single-row config: confidence_threshold (numeric, default 0.8), auto_publish_enabled (boolean, default true), is_running (boolean, default true), prompt_version (text).

---

## 4. Ingestion & Enrichment Pipeline

### `ppp-crawl`
**Cron:** Daily at 6am UTC (`0 6 * * *`). Also triggerable manually from admin.

1. Read all active `ppp_sources`.
2. For each source:
   - **API type:** Call REST endpoint, paginate through all results, extract raw records.
   - **Scrape type:** Fetch page HTML, extract text content.
3. Deduplicate by `source_url + name` before inserting — skip records already in `ppp_raw` or `ppp_projects`.
4. Insert new records into `ppp_raw` with `processing_status = pending`.
5. Trigger `ppp-enrich` on completion.

**Initial sources to configure:**
- World Bank PPI API (structured, global, high confidence)
- IsDB project database (structured, MENA/OIC focus, high confidence)
- MEED Projects (scrape, MENA focus)
- Reuters infrastructure news (scrape, global)
- Country-specific government procurement portals (scrape, per-country)

### `ppp-enrich`
Triggered after `ppp-crawl`. Also runnable manually.

1. Fetch all `ppp_raw` records with `processing_status = pending`.
2. For each record, call AI with the raw payload and prompt it to extract and normalize: name, country, region, sector, status, all financial fields, all party fields, all date fields.
3. Calculate confidence_score based on: field completeness (how many fields were extracted), source type (api = higher base score than scrape), source reliability history.
4. If confidence_score ≥ `ppp_settings.confidence_threshold`: upsert into `ppp_projects`.
5. If confidence_score < threshold: insert into `ppp_review_queue`.
6. Update `ppp_raw.processing_status` to `processed` or `failed`.

### `ppp-geocode`
Triggered after `ppp-enrich`. Also runnable manually.

1. Find all `ppp_projects` records where `lat` or `lng` is null.
2. For each: attempt to resolve coordinates using project name + country via Mapbox Geocoding API.
3. Fallback: use country centroid coordinates.
4. Update the record with resolved coordinates.

### `ppp-dedup`
**Cron:** Weekly on Sundays at 6am UTC.

1. Find potential duplicate pairs: same country + name similarity > 0.85 + overlapping date ranges.
2. Flag duplicates in `ppp_review_queue` with `reviewer_notes = 'Potential duplicate of project [id]'`.

---

## 5. Public Directory

### Homepage `/`
- Hero: Infinity PPP name, tagline, live count of total projects and total value in USD.
- Stats bar: total projects, total value, countries covered, last updated timestamp.
- Full-width interactive Mapbox map with clustered project pins. Pin color indicates status (pipeline = blue, procurement = yellow, awarded = orange, operational = green, completed = grey, cancelled = red).
- Filterable project grid below the map.

### Filters
- Region (multi-select)
- Country (multi-select, searchable)
- Sector (multi-select)
- Status (multi-select)
- Total value range (USD slider)
- Year range (announcement date)

Filters update both map and grid simultaneously without page reload.

### Project Grid
Cards showing: project name, country flag + name, sector icon, status badge, total value (USD), private operator (if known). Paginated (50 per page). Sortable by total value, announcement date, award date.

### Project Detail Page `/projects/[id]`
- All fields displayed.
- Timeline visualization: announcement → tender → award → financial close → completion.
- Parties section: government sponsor, private operator, lenders, advisors — each with role label.
- Source attribution with link and last verified date.
- Map showing project location pin.
- "Is this data incorrect?" link opens a feedback form (inserts into `ppp_errors` with type = user_report).

### Search
Full-text search across project name, government sponsor, private operator, country. Available in the nav and on the homepage. Results highlight matched terms.

No login required. All data publicly accessible.

---

## 6. Admin Panel `/admin`

Protected by Supabase Auth (email/password). Single admin user initially.

### Review Queue
- Cards showing low-confidence raw records with all extracted fields pre-filled for editing.
- Actions per card: Approve, Edit + Approve, Reject (with required note).
- Bulk approve for records from designated trusted sources.
- Queue count badge in nav.

### Manual Entry
- Form to add a project directly to `ppp_projects`.
- Required minimum: name, country, sector, status.
- All other fields optional.

### Projects Table
- Full searchable/filterable table of all live projects.
- Inline edit any field.
- Toggle `is_verified` to mark manually confirmed records.
- Soft delete (sets status to `cancelled`, does not remove from DB).

### Sources Manager
- CRUD interface for `ppp_sources`.
- Add, edit, deactivate sources.
- Displays: last crawl time, total records ingested, active/inactive toggle.
- "Crawl Now" button per source triggers `ppp-crawl` for that source only.

### Run Controls
- Trigger `ppp-crawl`, `ppp-enrich`, `ppp-geocode`, `ppp-dedup` manually.
- Run history table showing start time, duration, records processed, errors.
- Error log from `ppp_errors`.

### Settings
- Confidence threshold (numeric input, 0–1).
- Auto-publish toggle.
- prompt_version display.

---

## 7. Key Constraints

- All data publicly readable, no auth required for directory.
- Admin panel requires Supabase Auth.
- No API keys stored in the database — Mapbox token and any scraping service keys stored as Supabase secrets.
- RLS enabled on all tables: public can SELECT from `ppp_projects` only; all other operations require service role.
- Map requires a Mapbox public token (stored as `MAPBOX_PUBLIC_TOKEN` secret).
- AI enrichment uses the built-in Lovable AI (no external AI API key required).
