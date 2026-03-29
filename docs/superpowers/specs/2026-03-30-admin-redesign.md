# Admin Redesign — Design Spec
Date: 2026-03-30

## Goal

Rebuild `/admin` to serve two audiences equally: new users who need to set up agents, and returning users who need to monitor and control a running stack. The current admin was designed only for monitoring — it fails new users entirely.

---

## Layout: Tabs + Stats + Grid (Layout A)

One URL, one view, no mode switching. The grid adapts based on agent state.

### Top bar
- Left: 🦄 LAZY UNICORN logo, agent running count (● 8 AGENTS RUNNING)
- Right: PAUSE ALL text button, LAZY CLOUD ↗ gold pill link

### Category tabs
Gold underline on active tab. Tabs filter the agent grid.

| Tab | Agents |
|---|---|
| ALL | Everything |
| CONTENT | Blogger, SEO, GEO, Crawl, Perplexity, Repurpose, Trend |
| COMMERCE | Store, Drop, Print, Pay, Mail, SMS, Churn |
| MEDIA | Voice, Stream, YouTube |
| DEV | Code, GitLab, Linear, Contentful, Design, Auth, Granola |
| MONITOR | Alert, Telegram, Supabase, Security, Watch |
| INTELLIGENCE | Fix, Build, Intel, Agents |

Platform tools (Run, Admin, Cloud, Waitlist) are not in the tab system — they are infrastructure, not agents.

### Stats row (only shown when at least one agent is installed)
5 stats: Posts Today, Agents Active (x/36), Revenue Today, Errors Today (red tint if >0), Security Score.

### Agent grid
Two sections — installed agents first, not installed below. Installed agents are divided visually but not by separate headings in a way that feels judgmental.

---

## Agent Card States

All cards use the website palette: `#0a0a08` background, `#f0ead6` cream text, `#c9a84c` gold accent, `rgba(240,234,214,0.x)` borders. Status dots use color (green/amber/red) as the only exception.

| State | Border | Dot | CTA |
|---|---|---|---|
| Not installed | `rgba(240,234,214,0.06)`, muted opacity | None | `+ INSTALL` ghost button |
| Needs setup | `rgba(201,168,76,0.25)` gold | Amber | `COMPLETE SETUP →` gold fill button |
| Running | `rgba(240,234,214,0.12)` | Green | `MANAGE →` ghost button |
| Error | `rgba(248,113,113,0.2)` red | Red | `MANAGE →` + inline "How to fix →" gold link |
| Paused | `rgba(240,234,214,0.08)`, 60% opacity | Grey | `RESUME →` ghost button |

**Needs setup card**: shows a gold left-border callout listing exactly which secrets or config are missing — never a generic message.

**Error card**: shows the specific error message and a "How to fix →" link inline. No separate error page needed for common failures.

---

## Agent Detail Page

Reached by clicking MANAGE → on any installed agent card. Back button returns to overview.

### Header
Agent name, subtitle, running status dot, ON/OFF toggle.

### Two-column layout (equal weight)

**Left — Status**
- 2×2 stat grid (key metrics for that agent)
- Next up queue (what the agent will do next)
- Recent activity (last 3 rows, with external links)

**Right — Actions**
- Primary action: gold fill button (e.g. PUBLISH NOW →)
- Secondary actions: ghost buttons
- Settings: inline editable key/value rows — edit without leaving the page
- Error log: collapsed by default, shows "No errors" state when clean

---

## Error Handling (global)

Never show a generic "failed" or spinning loader with no resolution.

1. **Agent not configured** → replace entire panel with setup card + CTA to setup page
2. **Edge function fails** → show actual error + categorised "How to fix" based on error content
3. **Missing secret** → name the exact secret and link to Supabase secrets settings
4. **Empty state** → "No data yet — click [primary action] to run your first check"

---

## Navigation

Cloud, Run, Admin, and Waitlist are outside the agent tab system. Run gets a permanent status indicator in the top bar. Cloud gets a top-right pill link. Admin is the page itself. Waitlist lives in Settings.

---

## Implementation target

This design replaces `lazy-admin.md`. The output of implementation is an updated `lazy-admin.md` prompt file that Lovable can consume to rebuild `/admin` from scratch.
