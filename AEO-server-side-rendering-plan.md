# Making the speaker hub and topic pages readable by AI answer engines

**Prepared for:** Steve Smith
**Scope:** 7 pages — the Motivational Speakers hub + 6 `speaker_seo` topic pages
**Environment:** staging only (`raisethebar.devbyfuture.co.uk`) — nothing built or tested on live
**Status:** awaiting sign-off before any code is written, per the brief

A rendered version of this plan is also published here: https://claude.ai/code/artifact/6d608147-b269-453b-b963-167e833eed9c

---

## Recommendation

Build **true server-side rendering (Option 1)** — not dynamic rendering / bot-detection (Option 2), and not extending FacetWP (Option 3).

Reading the actual code behind all seven pages changes the picture the brief started from: FacetWP is not wired into any of them today, and four of the six topic pages already prove server-side taxonomy filtering works without it. SSR turns out to be the smallest, least novel change of the three — not just the most thorough one, as the brief itself already suspected.

---

## 1. What's actually there today

Pulled the live content field for all seven pages (read-only, via the site's WordPress connection) and traced the JavaScript. Every page follows the same template — pinned cards marked `data-ssr="1"`, then a script that builds the rest — but the topic pages differ in how they source the remainder.

| Page | Post ID | Pinned today | How the rest gets built | Server-side filter |
|---|---|---|---|---|
| Motivational Speakers (hub) | 63832 | 11 | Fetches `rtb-speaker-directory.json`, falls back to a full paginated REST pull; searches/filters entirely client-side against the in-memory result | No taxonomy filter — broad pool |
| Change & Transformation | 73446 | 13 | REST fetch filtered by `speaker_topics` | Confirmed working |
| Economy, Politics & Geopolitics | 78412 | 12 | REST fetch filtered by `speaker_topics` | Confirmed working |
| Mental Health, Wellbeing & Burnout | 75741 | 11 | REST fetch filtered by `speaker_categories` (the one page filtering on category, not topic) | Confirmed working |
| AI & Future of Work | 75691 | 10 | REST fetch filtered by `speaker_topics` — the page's own code comment confirms this was tested directly against the live API | Confirmed working |
| Most Booked Speakers | 76761 | 14 | No API call at all — the full 14-speaker list is a hardcoded JS array baked into the page | Not taxonomy-driven |
| New In Speakers | 76645 | 21 | Same pattern — a hardcoded JS array of 21 speakers, no live query | Not taxonomy-driven |

### Two things worth flagging directly

**A. FacetWP is not used on any of these seven pages.** It's active on the site, and its server-side filtering has been verified elsewhere — but nothing in these seven pages' HTML, CSS or JavaScript calls it: no `[facetwp]` shortcode, no `facetwp-facet` classes, no `FWP()` calls, no `admin-ajax.php` requests. Option 3 in the brief isn't "extend the existing mechanism" — it would mean introducing FacetWP to seven bespoke pages that don't use it today.

**B. Server-side taxonomy filtering already works, right now, without FacetWP.** Four topic pages pull from `/wp-json/wp/v2/speaker?speaker_topics=<id>` or `?speaker_categories=<id>` — WordPress core's own REST taxonomy filtering, proven live. That's the same query a PHP `WP_Query` with `tax_query` would run, just moved in-process instead of over HTTP.

Context: the `speaker` CPT currently has 999 published records (the brief's ~871 figure has grown since); taxonomies are `speaker_categories` (20 terms) and `speaker_topics` (89 terms).

---

## 2. Why Option 1, given what's actually there

| | Option 1 — True SSR (recommended) | Option 2 — Dynamic rendering / prerendering | Option 3 — FacetWP server-side pagination |
|---|---|---|---|
| What it takes here | Reuses proven taxonomy filtering (4 pages), already-inline static lists (2 pages), and the existing `data-ssr` card markup (all 7) | A separate snapshot pipeline that has to be generated and kept in sync with the live JS-driven page | Retrofitting FacetWP onto seven pages built entirely outside it — adapting bespoke designs to FacetWP's own rendering |
| Drift / cloaking risk | None — one code path, bots and visitors see the same HTML by construction | Real — a stale or mismatched snapshot is treated as cloaking, not a cosmetic bug | Real, if the retrofit doesn't fully match today's design |
| UX risk to real visitors | Low — existing JS layers on top unchanged | None by design — real visitors never see the alternate version | Highest of the three, per the brief's own read, unless deliberately engineered otherwise |
| Engineering lift here | Smallest, given what these pages already do | Moderate | Largest |

---

## 3. What changes, concretely

For each page, at request time: run the same taxonomy filter (or the same fixed ID list) the page's own JavaScript already uses — via `WP_Query` and `tax_query` directly, in PHP, not over HTTP — and render the full matching set as `data-ssr="1"` cards, using the exact same card markup already on the page. Nothing about the visual design changes; the existing search, filters and "Load more" stay in place as progressive enhancement over what's now already there on load.

### How the PHP gets onto the page without another WPCode incident

A prior WPCode snippet on this site once affected an unrelated live page. So: not WPCode, and not a global content filter. Instead, one small, purpose-built plugin that registers a single shortcode — e.g. `[rtb_ssr_speakers topics="586,669"]` — placed once into each page's own content field, additive only:

- **Opt-in per page.** It only ever runs on a page that contains the shortcode — no path by which it can touch a page nobody added it to.
- **Off by default.** Gated behind a flag that starts switched off, per the hard requirement, until explicitly confirmed safe on staging.
- **Trivially reversible.** Removing the shortcode tag removes the behaviour — no snippet-manager config to unwind.

---

## 4. Suggested build order

The brief's instinct is to start with the hub, given its traffic. Worth naming honestly: the hub is also the most complex of the seven — two data sources, a session cache, and result re-prioritisation — so starting there means proving the pattern on its hardest case first.

**Alternative on the table:** prove the mechanism first on **AI & Future of Work** — the page whose own code comments already confirm server-side filtering works — then roll out to the other three taxonomy-filtered topic pages, then the two hardcoded-list pages, and take the hub last with lessons already learned.

Not deciding this unilaterally — flagged below as the first thing to confirm. Happy to follow the hub-first instinct if traffic or timeline make that the right call.

---

## 5. What needs deciding before writing code

1. **Build order.** Hub first, as originally suggested, or the simplest proven topic page first, as recommended above.
2. **De-duplication on the client.** The existing JavaScript needs a small adjustment so it recognises cards the server already rendered (via `data-ssr="1"`) and never renders them a second time.
3. **Hub search scope.** Does the hub's search box need to reach beyond the server-rendered set — i.e. search the full ~999-speaker roster? If so it still needs the JSON directory or REST fallback for that broader reach, even once SSR covers the default view. Needs confirming this doesn't regress today's all-speaker search.
4. **Staging vs. live database — flagged, not resolved.** This investigation ran against the live site's WordPress connection; the environment it ran in can't reach `raisethebar.devbyfuture.co.uk` directly to check. One indirect signal: **WP Migrate Pro** is installed and active, which is specifically a push/pull tool between separate environments — suggestive of a genuinely separate staging database, but that's an inference, not a confirmation. Needs an explicit yes/no from whoever manages hosting before staging work is treated as safe for taxonomy reads, per the brief's own instruction. This plan only ever reads `speaker_categories` / `speaker_topics` data, never writes to it, either way.

---

## 6. Verification, once built on staging

- `curl` the finished page's raw HTML — the same thing a non-JS crawler receives — and confirm the full matching speaker set is present as real `data-ssr="1"` markup, not just the original pinned handful.
- Cross-check the server-rendered count against the true count for that taxonomy filter, via a direct read-only query, to confirm nothing is silently truncated.
- Load the page normally with JavaScript on: identical visual design, no duplicate cards, search / filters / "Load more" behave exactly as they do on live today.
- No bot-vs-human parity check is needed the way it would be for Options 2 or 3 — this approach serves identical HTML to everyone by construction, one code path only.

---

## Before any code gets written

Waiting for confirmation on this plan — the chosen approach, and specifically the four items in §5 — before building anything, on staging or otherwise. Once confirmed, work starts on `raisethebar.devbyfuture.co.uk` only, one page at a time, verified per §6 before moving to the next.

No content, taxonomy term, or speaker/category/topic assignment was created, changed, or removed in the course of this review — it was read-only throughout.
