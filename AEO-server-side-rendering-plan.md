# Making the speaker hub and topic pages readable by AI answer engines

**Revision 2 — response to review. Not building yet.**

**Prepared for:** Steve Smith
**Scope:** 7 pages — the Motivational Speakers hub + 6 `speaker_seo` topic pages
**Environment:** staging only (`raisethebar.devbyfuture.co.uk`) — nothing built or tested on live
**Status:** blocked — see §6

A rendered version of this plan is also published here: https://claude.ai/code/artifact/6d608147-b269-453b-b963-167e833eed9c

---

## Recommendation — provisional

Still true server-side rendering (**Option 1**), but with more caveats than the first pass admitted. The core finding stands: nothing in these seven pages' own HTML/CSS/JS calls FacetWP, and four of six topic pages already prove server-side taxonomy filtering works without it. What's changed: whether FacetWP is genuinely still active on the hub via the theme template is now an open, unresolved question (§1), and either way, Option 1 turns out to need the same thing Option 3 would have needed — access to Future's theme repository, which this session doesn't have. That's now blocking, not just a detail to sort out later.

---

## §1 — Response to review

Four points raised, taken in order. Two resolve with direct evidence; two don't fully resolve from this session and are named as such rather than papered over.

### 1. FacetWP on the hub — unresolved from here

**Fair, and the first pass overstated it.** The "zero FacetWP references" finding came from grepping the page's own content field — the text stored in the WordPress database for post 63832. The WordPress REST connector this session used only ever returns that content field. It cannot see PHP in theme template files, and a page template can call `[facetwp]`, enqueue `facetwp.js`, or print a facet block entirely outside the content field — none of which would ever show up in what was grepped. That's a real blind spot, not a rounding error.

Tried to settle it directly by fetching the live rendered page (the actual HTTP response, the same thing a crawler sees) and checking for FacetWP's own asset signatures. That failed outright: this session's network egress is blocked for `raisethebar.co.uk` entirely — confirmed via both a direct fetch attempt and the proxy's own status log, which shows the connection rejected at the gateway (`gateway answered 403 to CONNECT`). So the live-rendered HTML couldn't be inspected either, by curl or by the web-fetch tool.

**What could be checked:** the hub's own script (page 63832's content field) never reads `_search`, `#filter-anchor`, `location.hash`, or uses `URLSearchParams` anywhere — confirmed by direct grep, zero matches. So today, landing on `/motivational-speakers/?_search=Term#filter-anchor` does nothing inside the bespoke script. Whether something else on that URL *does* act on it is exactly the part this session can't see.

**Best-evidence read, clearly flagged as inference:** `_search=` and `_post_type=` match FacetWP's own default (non-pretty-URL) query-string convention — an underscore-prefixed facet name — which the bespoke JS wouldn't organically have invented under its own naming style. That's real, specific evidence FacetWP was genuinely wired into this hub at some point via the theme, not just a superficial resemblance. What it doesn't settle is whether that wiring is still live today or was left behind when the bespoke rebuild replaced the visible grid. Both are plausible; distinguishing them needs either theme source (§6) or one cheap manual check: **open the hub in a browser, DevTools Network tab open, filter for "facetwp", click a category pill from a speaker profile, and see whether anything fires.** Five minutes, no code, no repo access needed — worth doing before §6 is resolved, not instead of it.

**Why it matters either way:** if FacetWP turns out to be genuinely active and functioning on that exact URL, that's two overlapping listing mechanisms answering the same page — worth knowing regardless of which SSR option gets built. And if it's functioning well enough to already filter server-side there, Option 3's cost profile in §3 gets revisited, not assumed.

Separately, on the second half of this point: the brief's claim that FacetWP's server-side filtering was "confirmed against real speaker counts" refers to verification done **elsewhere on the site**, not these seven pages — stated here explicitly rather than left implied. This session could not independently confirm where, for the same network reason above.

### 2. Three mechanisms, not one — sequencing revised

Correct, and it changes §5. The hub (63832) fetches the pre-built `rtb-speaker-directory.json` snapshot first; if that fails, it falls back to a full paginated pull of every published speaker via REST, **unfiltered by any taxonomy** — then re-orders and searches the whole pooled set client-side. That's a third pattern, distinct from both the four taxonomy-filtered topic pages and the two hardcoded-list pages. Proving SSR on the hub first would mean proving the hardest, least-representative case first and learning nothing transferable to the other six. Revised sequencing is in §5.

### 3. Speaker 754 — confirmed independently

Confirmed directly: requesting speaker post 754 through this session's own read-only WordPress connector failed outright ("tool execution failed"), consistent with the fatal you described. That's the REST/API layer failing, not necessarily `WP_Query` itself — a direct in-process query might not hit the same failure, since the crash plausibly sits in REST field serialization (e.g. a malformed ACF value) rather than post retrieval. That's an assumption, not a finding, and Option 1 must not rely on it being true. Explicit handling now required in §6.

### 4. Future's theme repo — blocking

Agreed, and the first pass's proposed workaround — a small standalone plugin instead of theme code — doesn't actually dodge this. Nothing custom appears to run on this site today outside WPCode snippets and the theme itself; introducing a genuinely new plugin would likely be a new deployment pattern in its own right, not a lighter path around Future. Given Option 1 is theme-level PHP, access to Future's repository (or an equivalent, agreed deployment route through Future) is a prerequisite for starting build, not a detail to confirm mid-build. This session only has the `Proposals` documentation repo attached — nothing that touches the live site's code. Moved to §6 as blocking.

---

## §2 — What's actually there today

Pulled the live content field for all seven pages (read-only) and traced the JavaScript. This covers what's stored as page content, not what a theme template might add around it — see §1 for that gap. Every page follows the same template — pinned cards marked `data-ssr="1"`, then a script that builds the rest — but the seven pages split into **three** distinct patterns for how they source the remainder.

| Page | Post ID | Pinned today | How the rest gets built | Server-side filter |
|---|---|---|---|---|
| Motivational Speakers (hub) | 63832 | 11 | Fetches `rtb-speaker-directory.json`, falls back to a full paginated, **unfiltered** REST pull of every published speaker; searches/filters entirely client-side against the pooled result | Pattern C — no taxonomy filter, broad pool |
| Change & Transformation | 73446 | 13 | REST fetch filtered by `speaker_topics` | Pattern A — confirmed working |
| Economy, Politics & Geopolitics | 78412 | 12 | REST fetch filtered by `speaker_topics` | Pattern A — confirmed working |
| Mental Health, Wellbeing & Burnout | 75741 | 11 | REST fetch filtered by `speaker_categories` (the one page filtering on category, not topic) | Pattern A — confirmed working |
| AI & Future of Work | 75691 | 10 | REST fetch filtered by `speaker_topics` — the page's own code comment confirms this was tested directly against the live API | Pattern A — confirmed working |
| Most Booked Speakers | 76761 | 14 | No API call at all — the full 14-speaker list is a hardcoded JS array baked into the page | Pattern B — not taxonomy-driven |
| New In Speakers | 76645 | 21 | Same pattern — a hardcoded JS array of 21 speakers, no live query | Pattern B — not taxonomy-driven |

### Three things worth flagging directly

**A.** None of the seven pages' own content calls FacetWP. No `[facetwp]` shortcode, no `facetwp-facet` classes, no `FWP()` calls, no `admin-ajax.php` requests, anywhere in what's stored in their content fields. That's narrower than "FacetWP isn't wired in" — whether it's wired in via the theme is a genuinely open question, addressed honestly in §1 rather than assumed either way.

**B.** Server-side taxonomy filtering already works, right now, without FacetWP. Four topic pages pull from `/wp-json/wp/v2/speaker?speaker_topics=<id>` or `?speaker_categories=<id>` — WordPress core's own REST taxonomy filtering, proven live. That's the same query a PHP `WP_Query` with `tax_query` would run, just moved in-process instead of over HTTP.

**C.** Speaker post 754 breaks the API. Confirmed independently in this session (§1) — any new query path has to account for it explicitly, not inherit the client-side workaround by accident.

Context: the `speaker` CPT currently has 999 published records (the brief's ~871 figure has grown since); taxonomies are `speaker_categories` (20 terms) and `speaker_topics` (89 terms).

---

## §3 — Why Option 1, given what's actually there

| | Option 1 — True SSR (recommended) | Option 2 — Dynamic rendering / prerendering | Option 3 — FacetWP server-side pagination |
|---|---|---|---|
| What it takes here | Reuses proven taxonomy filtering (4 pages), already-inline static lists (2 pages), and the existing `data-ssr` card markup (all 7). Confirmed requirement: theme-level PHP, via Future (§6) | A separate snapshot pipeline that has to be generated and kept in sync with the live JS-driven page | The bespoke card grids on all seven pages sit outside FacetWP regardless of §1's outcome, so retrofitting them is real work either way |
| Drift / cloaking risk | None — one code path, bots and visitors see the same HTML by construction | Real — a stale or mismatched snapshot is treated as cloaking, not a cosmetic bug | Real, if the retrofit doesn't fully match today's design |
| UX risk to real visitors | Low — existing JS layers on top unchanged | None by design — real visitors never see the alternate version | Highest of the three, per the brief's own read, unless deliberately engineered otherwise |
| Engineering lift here | Smallest, given what these pages already do | Moderate | Largest — though if §1 turns out to confirm FacetWP is genuinely live on the hub via the theme, this option's cost specifically for the hub is worth revisiting before ruling it out there |

---

## §4 — What changes, concretely

For each page, at request time: run the same taxonomy filter (or the same fixed ID list) the page's own JavaScript already uses — via `WP_Query` and `tax_query` directly, in PHP, not over HTTP — and render the full matching set as `data-ssr="1"` cards, using the exact same card markup already on the page. Nothing about the visual design changes; the existing search, filters and "Load more" stay in place as progressive enhancement over what's now already there on load.

### Where the PHP actually lives

Confirmed as theme-level PHP, not a standalone plugin. The first pass proposed a small purpose-built plugin registering a shortcode specifically to avoid touching the theme after the prior WPCode incident — but that doesn't remove the dependency, it just relocates it: nothing custom appears to run on this site today outside WPCode snippets and the theme, so a genuinely new plugin would likely be its own new deployment pattern, not a lighter path around Future. Whatever the exact mechanism, it needs the same things the prior incident argues for:

- **Scoped, not global.** Gated to the seven known page/post IDs explicitly, however it's implemented — no path by which it can touch a page nobody intended it for.
- **Off by default.** Behind a flag that starts switched off, per the hard requirement, until explicitly confirmed safe on staging.
- **Owned by whoever deploys theme code today** — which is Future. See §6.

---

## §5 — Build sequencing

Revised from a single hub-first pass to three tracks, since the seven pages run three distinct data mechanisms (§1, point 2) rather than one pattern the hub happens to demonstrate hardest.

1. **Track A — taxonomy-filtered (4 pages).** Prove server-side `tax_query` rendering on **AI & Future of Work** first — the page whose own code comments already confirm server-side filtering works against the live API — then roll the same mechanism out to Change & Transformation, Economy/Politics/Geopolitics, and Mental Health/Wellbeing/Burnout.
2. **Track B — fixed list (2 pages).** Trivial by comparison: render the same hardcoded speaker list server-side instead of client-side. Prove on one of Most Booked / New In, apply to the other.
3. **Track C — the hub (1 page).** Its own track, last, informed by A and B but not a copy of either — it pools broadly (directory JSON + unfiltered REST fallback) rather than filtering by taxonomy, and carries the search-scope question in §7.

**Still open:** the brief's own instinct was hub-first, given its traffic. This plan proposes A → B → C instead, on the grounds that Track A proves the mechanism on the cleanest, already-validated case rather than the hardest one. Not deciding this unilaterally — happy to follow hub-first if traffic or timeline pressure make that the right call; flagged in §7.

---

## §6 — Blocking: needed before any build starts

Four items. None of these are "nice to confirm eventually" — each one stops Track A from starting.

1. **Future's theme repository.** Option 1 is theme-level PHP (§4). This session has only the `Proposals` documentation repo attached — nothing that touches the live site's code. Needs either the theme repo attached to whoever builds this, or an agreed route where Future implements against a spec this plan provides. Blocking Track A outright.
2. **The FacetWP-on-the-hub check.** The five-minute manual diagnostic from §1: open the hub with DevTools Network open, filter "facetwp", click a category pill from a speaker profile, see what fires. Doesn't block Track A or B (neither page has this ambiguity), but blocks starting Track C until it's known whether the hub already has a second, possibly-live filtering mechanism sitting underneath the bespoke grid.
3. **Speaker 754 — exclude or fix.** Confirmed independently (§1) that this record breaks the REST layer. Before Track A's first build: either explicitly exclude ID 754 from the new server-side query (`post__not_in`) as a stopgap, or root-cause the underlying corrupt field so the speaker can appear normally — a decision for whoever owns the speaker data, not something to default silently.
4. **Cost and scope, plainly.** The brief framed Option 3 as extending a plugin already licensed — configuration effort, not new spend. Option 1 puts the work inside the theme, which means engaging Future: a scoped, quoted piece of development work, not a config change within existing licensing. That shift needs business sign-off in its own right, separate from the technical case in §3. Worth noting honestly: Option 3 would likely also need real developer effort to retrofit FacetWP's rendering onto seven bespoke designs, quite possibly also via Future — so the licensing-cost framing may overstate the gap between the two options. Either way, get a scoped estimate from Future before committing to a page, not after starting one.

---

## §7 — Still to decide, once unblocked

1. **Sequencing.** A → B → C as proposed in §5, or hub-first as the brief originally suggested.
2. **De-duplication on the client.** The existing JavaScript needs a small adjustment so it recognises cards the server already rendered (via `data-ssr="1"`) and never renders them a second time.
3. **Hub search scope (Track C specifically).** Does the hub's search box need to reach beyond the server-rendered set — i.e. search the full ~999-speaker roster? If so it still needs the JSON directory or REST fallback for that broader reach, even once SSR covers the default view. Needs confirming this doesn't regress today's all-speaker search.
4. **Staging vs. live database.** Still unresolved — this session cannot reach `raisethebar.devbyfuture.co.uk` at all, for any purpose, confirmed via the proxy's own connection log as well as a direct request. One indirect signal: **WP Migrate Pro** is installed and active, which is specifically a push/pull tool between separate environments — suggestive of a genuinely separate staging database, but that's an inference, not a confirmation. Needs an explicit yes/no from whoever manages hosting before staging work is treated as safe for taxonomy reads, per the brief's own instruction. This plan only ever reads `speaker_categories` / `speaker_topics` data, never writes to it, either way.

---

## §8 — Verification, once built on staging

- `curl` the finished page's raw HTML — the same thing a non-JS crawler receives — and confirm the full matching speaker set is present as real `data-ssr="1"` markup, not just the original pinned handful.
- Cross-check the server-rendered count against the true count for that taxonomy filter, via a direct read-only query, to confirm nothing is silently truncated.
- Load the page normally with JavaScript on: identical visual design, no duplicate cards, search / filters / "Load more" behave exactly as they do on live today.
- No bot-vs-human parity check is needed the way it would be for Options 2 or 3 — this approach serves identical HTML to everyone by construction, one code path only.
- Confirm speaker 754's handling explicitly: either verify it's cleanly excluded from the server-rendered set with no PHP error or warning in the response, or, if fixed at the data level, that it now renders correctly and isn't silently duplicated.

---

## Not building yet

Waiting on the four blocking items in §6 — Future's repo access above all — before Track A starts, and on the §7 decisions before locking sequencing. Once unblocked, work starts on `raisethebar.devbyfuture.co.uk` only, one page at a time, verified per §8 before moving to the next.

No content, taxonomy term, or speaker/category/topic assignment was created, changed, or removed in the course of this review — it was read-only throughout, and included one direct read-only diagnostic request against the speaker API to confirm the ID 754 failure.
