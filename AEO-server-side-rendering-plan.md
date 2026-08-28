# Making the speaker hub and topic pages readable by AI answer engines

**Revision 3 — requirement change: output must always reflect the live speaker record. Not building further yet.**

**Prepared for:** Steve Smith
**Scope:** 7 pages — the Motivational Speakers hub + 6 `speaker_seo` topic pages
**Approach:** a single dynamic WPCode shortcode, live-queried on every request — no theme changes, no Future, no staging
**Status:** 3 of 5 requested confirmations resolved directly; 2 need access this session doesn't have — see §3

A rendered version of this plan is also published here: https://claude.ai/code/artifact/6d608147-b269-453b-b963-167e833eed9c

---

## Recommendation — revised approach

Agreed: static output can't meet an always-current requirement, and price belongs back in the rendered cards now that the output is live rather than pasted. This drops the biggest blocker from the last revision entirely — no theme changes means no dependency on Future's repository, which this session never had access to. What's left is narrower and more mechanical: three of the five things you asked to confirm empirically are confirmed, with evidence below. The other two — whether shortcodes actually execute inside these pages' Custom HTML blocks, and how Hummingbird's cache behaves — need either WPCode admin access or working network access to the live site, and this session has neither.

---

## §1 — On the requirement change

You asked, if a shortcode can't meet the always-current requirement, to say so rather than build something that half meets it. It can meet it — structurally, a shortcode that runs a fresh `WP_Query` on every request has no cache of its own to go stale; the response is only as current as WordPress's own data and whatever sits in front of it, which is exactly why §3's Hummingbird question is the one piece that decides whether "always current" actually holds in practice, not whether the mechanism is sound. No objection to the approach. The one assumption everything else depends on is whether this specific site's specific page template actually runs shortcode processing on a Custom HTML block's content — addressed honestly in §3, not assumed.

---

## §2 — Confirmed directly

### 3. Existing JS behaviour on re-render — confirmed: clears, not appends

Read the actual `renderGrid()` function on both the hub and a topic page (AI & Future of Work). Both do the same thing on every call:

```js
// page 63832 — renderGrid()
var grid = document.getElementById('sf-grid');
var shown = Math.min(state.shown, list.length);
grid.innerHTML = '';
for (var i = 0; i < shown; i++) {
    grid.appendChild(cardEl(list[i]));
}
```

This means server-rendered cards placed inside the same container the JS already targets need no de-duplication logic at all. The very first render call after data loads wipes and rebuilds the grid unconditionally — SSR cards serve crawlers and the pre-JS instant, then get cleanly replaced by the JS's own equivalent set. No stacking, no duplicates, by construction.

Worth flagging as a related discovery, not something you asked for: the topic page's script carries a `gridHydrated` flag and a dead code path that would have preserved pre-existing DOM cards under narrow conditions — but it's unreachable, because `onDataReady` sets `gridHydrated=false` in the same statement that unlocks rendering, one line before the check that would use it. Someone appears to have planned for exactly this kind of hydration before and the wiring never got finished. Not a blocker, just context worth having.

### 4. Speaker 754 — confirmed, root cause found

The topic page's own code comment names it precisely: *"Known-broken speaker records: confirmed via PHP error log to fatal inside ACF's Repeater REST formatting code."* That matters beyond just excluding the ID: the crash is inside ACF's own Repeater field formatting, which a direct PHP `get_field()` call on that record could also trigger, not only the REST layer. So the shortcode must exclude 754 explicitly at the query level regardless of mechanism — it's in the draft code in §4 as a hard-coded `post__not_in`, not inherited from the client-side workaround by assumption.

### 5. Per-page counts and HTML size — confirmed, with one honest gap

Pulled real term counts directly rather than estimating: `speaker_topics` "AI Artificial Intelligence" (586) = **99** published speakers; "Future Of Work" (669) = **57**. The AI & Future of Work page matches either (OR), so its true rendered count sits somewhere at or below 156 depending on overlap between the two topics — getting the exact de-duplicated union needs a real taxonomy query, which the tools available in this session don't expose; the shortcode's own query will report the real number the moment it exists. `speaker_categories` "Mental Health & Wellbeing" (503) = **483** — large enough that rendering it uncapped is worth a deliberate decision, not a default.

Measured actual card markup size directly from the hub's existing pinned cards: **≈1,850 characters per card** including whitespace. At that rate, a 150-card render adds roughly 270KB of HTML on top of the ≈55KB of CSS/JS already on the page — noticeable but not extreme for a listing page search engines are meant to crawl deeply.

**Recommendation for the hub specifically:** the hub has no taxonomy filter at all — its pool is every published speaker (999 today). Rendering all 999 server-side would mean roughly 1.8MB of card markup on one response, which is excessive for a page whose actual value to a crawler is "the full roster exists and is reachable," not "every one of 999 speakers sits in a single response." Recommend capping the hub's server-rendered set at a defined number (a few hundred, prioritised the same way the existing `HUB_POOL_IDS` reordering already prioritises today) rather than rendering the entire roster in one page — full reachability can come from the topic pages, which are naturally bounded by their taxonomy filters, plus normal pagination/sitemap coverage for the rest. This is a recommendation, not a decision made unilaterally — flagged for sign-off alongside §9's other open items.

---

## §3 — Not confirmed, and why, precisely

These two don't resolve from this session. Not reasoned around, not assumed — named as blocked, with the specific access each one needs.

### 1. Shortcodes inside a `wp:html` Custom HTML block — blocked, no tool to test it

Testing this for real means creating an actual WPCode PHP snippet and observing whether it fires. This session's WordPress connector has no tool that manages WPCode, or any other mechanism for deploying a PHP snippet or plugin file to the site — it can read and write posts, pages, terms and meta, nothing that installs code. That's a hard stop, not a workaround-and-continue situation.

There is a structural reason to expect it works: `do_shortcode` is registered on the `the_content` filter and runs against the final assembled HTML string regardless of which block contributed which part of it, so a shortcode inside a Custom HTML block's raw content should get processed exactly like one anywhere else — *provided* the page template actually calls the standard `the_content()` pipeline to output it. Given how far outside normal WordPress page rendering these seven pages already sit (one large custom blob per page, built outside the usual template hierarchy per the original brief), a template that fetches and echoes raw post content directly — bypassing that filter chain entirely — is a real possibility here, not a theoretical one. That reasoning is offered as context only. You asked for it confirmed empirically, not reasoned about, and it isn't — the runbook in §6 is the fastest real path to an answer.

### 2. Hummingbird cache behaviour and invalidation — blocked, no live access

Hummingbird Pro is confirmed active (from the plugin list pulled in the first pass), but its cache configuration — whether page caching is even on for these pages, what TTL applies, and whether anything purges the cache on a speaker's `save_post` — isn't exposed through any tool available here, and testing it live (edit a speaker, fetch the raw response, see whether it changed) needs HTTP access to the live site. This session's network egress is blocked for `raisethebar.co.uk` entirely, confirmed via both a direct fetch attempt and the proxy's own connection log. Your own framing is the right bar here: auto-updating output behind a stale cache does not meet the requirement, so this has to be answered with a real observation, not assumed favourable.

---

## §4 — Draft shortcode

One shortcode, three modes, no global hooks — only `add_shortcode()`. A page without `[rtb_ssr_speakers]` in its content executes none of this. Marked draft: the card markup below is structurally correct but not yet byte-matched to the real ACF field names the existing `cardEl()` JS pulls from (image, bio, topic pills, and now price) — that mapping needs one more pass against the live field list before this goes anywhere near production, and is exactly what §6's first live step should confirm alongside the shortcode-execution question.

```php
// WPCode PHP snippet (draft) — created switched off
add_shortcode('rtb_ssr_speakers', function ($atts) {
    $atts = shortcode_atts([
        'ids'        => '',   // explicit post IDs, comma-separated, in order
        'topics'     => '',   // speaker_topics term IDs, comma-separated, OR-matched
        'categories' => '',   // speaker_categories term IDs, comma-separated, OR-matched
        'limit'      => 300,  // hard cap on rendered cards
    ], $atts, 'rtb_ssr_speakers');

    $always_excluded = [754]; // ACF Repeater REST-formatting fatal - confirmed root cause

    $query_args = [
        'post_type'      => 'speaker',
        'post_status'    => 'publish',
        'posts_per_page' => min((int) $atts['limit'], 500),
        'post__not_in'   => $always_excluded,
        'no_found_rows'  => true,
    ];

    if (!empty($atts['ids'])) {
        $ids = array_diff(array_filter(array_map('intval', explode(',', $atts['ids']))), $always_excluded);
        if (empty($ids)) return '';
        $query_args['post__in'] = $ids;
        $query_args['orderby']  = 'post__in';
    } elseif (!empty($atts['topics'])) {
        $terms = array_filter(array_map('intval', explode(',', $atts['topics'])));
        if (empty($terms)) return '';
        $query_args['tax_query'] = [[ 'taxonomy' => 'speaker_topics', 'field' => 'term_id', 'terms' => $terms ]];
    } elseif (!empty($atts['categories'])) {
        $terms = array_filter(array_map('intval', explode(',', $atts['categories'])));
        if (empty($terms)) return '';
        $query_args['tax_query'] = [[ 'taxonomy' => 'speaker_categories', 'field' => 'term_id', 'terms' => $terms ]];
    } else {
        return ''; // no criteria given - render nothing, fail safe
    }

    $query = new WP_Query($query_args);
    if (!$query->have_posts()) return '';

    ob_start();
    foreach ($query->posts as $speaker) {
        $name  = get_the_title($speaker);
        $link  = get_permalink($speaker);
        $image = get_the_post_thumbnail_url($speaker, 'medium');
        // TODO before real use: confirm these against the real ACF field
        // map used by the existing cardEl() JS - bio, topic pills, price.
        $hook  = get_field('short_bio', $speaker->ID);
        $price = get_field('fee_range', $speaker->ID);
        ?>
        <a href="<?php echo esc_url($link); ?>" class="tp-card" data-ssr="1">
            <div style="position:relative;aspect-ratio:4/5;overflow:hidden;background:#e7e1ea">
                <img src="<?php echo esc_url($image); ?>" alt="<?php echo esc_attr($name); ?>" loading="lazy">
            </div>
            <div class="tp-card-body">
                <h3><?php echo esc_html($name); ?></h3>
                <?php if ($hook): ?><p><?php echo esc_html($hook); ?></p><?php endif; ?>
                <?php if ($price): ?><p class="tp-price"><?php echo esc_html($price); ?></p><?php endif; ?>
            </div>
        </a>
        <?php
    }
    wp_reset_postdata();
    return ob_get_clean();
});
```

---

## §5 — Test page: prepared, not live

Created one new `speaker_seo` item as the diagnostic target: **post 79215**, "AEO SSR diagnostic (unlinked, do not index)". Set to `private`, not `publish` — private posts return nothing to an anonymous request, so there's zero exposure while it sits unfinished. Its content already carries the diagnostic shortcode call, ready to activate:

```
[rtb_ssr_speakers ids="23751,11570"]
```

Deliberately not published yet, and not marked noindex/nofollow yet either — this session's WordPress connector can read and write standard post meta, but no Yoast SEO fields came back when queried against an existing page, meaning Yoast's robots meta likely isn't exposed to REST on this install. Setting noindex/nofollow reliably needs the WP admin UI, by hand, as the first step of §6 before this page goes public.

---

## §6 — Runbook for whoever has WPCode and live access

Written so it needs judgement only where the spec above leaves a real decision, not for interpreting these steps.

1. **Create the WPCode snippet.** Paste the §4 draft in as a PHP snippet, save it **Inactive**. Before activating anything, fix the two `TODO` field names against the real ACF field map for the `speaker` CPT (bio, price/fee, topic pills) so the output actually matches the existing cards.
2. **Prepare post 79215.** Set it to `publish`, add `noindex,nofollow` via Yoast's meta box, confirm it's not linked from any menu, sitemap, or internal link.
3. **Baseline with the snippet off.** Load the page with JS disabled (or view-source) — confirm the literal text `[rtb_ssr_speakers ids="23751,11570"]` is what actually renders, unprocessed. If it's already silently vanished or altered with the snippet Inactive, stop — that alone answers §3 item 1 in the negative and the whole approach needs rethinking before going further.
4. **Activate the snippet in WPCode.** Reload the test page's raw HTML (curl, or view-source with JS off). Confirm real card markup for both speaker IDs is present, matching the existing card design. This is the direct answer to §3 item 1.
5. **Diff three unrelated live pages.** Curl three pages that don't carry the shortcode, before and after activation, and diff. No difference confirms the shortcode fires only where it's literally placed, exactly as intended.
6. **Edit one of the two test speakers.** Change something visible (bio text is enough), save, then re-fetch the test page's raw HTML without doing anything else. If the change appears immediately: no page cache is interfering, and Hummingbird either isn't caching this URL or purges correctly on speaker save — answers §3 item 2 directly. If it doesn't appear, check Hummingbird's caching settings and its "clear cache on content update" option before concluding the requirement can't be met this way — the fix may be a cache-exclusion rule for these pages or an explicit purge hook on `save_post_speaker`, not a reason to abandon the approach.
7. **Report back** with what happened at steps 3, 4 and 6 specifically. That closes §3, and this plan gets updated to build sequencing for the real seven pages from there.

---

## §7 — Page-by-page evidence

Carried forward from the previous revision, unchanged: pulled the live content field for all seven pages (read-only) and traced the JavaScript. Every page follows the same template — pinned cards marked `data-ssr="1"`, then a script that builds the rest — but the seven pages split into three distinct patterns for how they source the remainder.

| Page | Post ID | Pinned today | How the rest gets built | Server-side filter |
|---|---|---|---|---|
| Motivational Speakers (hub) | 63832 | 11 | Fetches `rtb-speaker-directory.json`, falls back to a full paginated, unfiltered REST pull of every published speaker; searches/filters entirely client-side | Pattern C — no taxonomy filter, broad pool |
| Change & Transformation | 73446 | 13 | REST fetch filtered by `speaker_topics` | Pattern A — confirmed working |
| Economy, Politics & Geopolitics | 78412 | 12 | REST fetch filtered by `speaker_topics` | Pattern A — confirmed working |
| Mental Health, Wellbeing & Burnout | 75741 | 11 | REST fetch filtered by `speaker_categories` | Pattern A — confirmed working |
| AI & Future of Work | 75691 | 10 | REST fetch filtered by `speaker_topics` — confirmed against the live API per the page's own code comment | Pattern A — confirmed working |
| Most Booked Speakers | 76761 | 14 | Hardcoded JS array of 14 speakers, no live query | Pattern B — not taxonomy-driven |
| New In Speakers | 76645 | 21 | Hardcoded JS array of 21 speakers, no live query | Pattern B — not taxonomy-driven |

**A.** None of the seven pages' own content calls FacetWP — no shortcode, classes, JS calls, or AJAX requests anywhere in their content fields. Moot now since the shortcode approach doesn't touch or depend on the theme either way.

**B.** A validated real-time server-side taxonomy query already exists in this codebase — the topic pages' own fallback fetcher hits `/wp-json/wp/v2/speaker?speaker_topics=<id>` or `?speaker_categories=<id>`, confirmed working against the live API per their own code comments. That's the same query the §4 shortcode's `tax_query` runs, just in-process instead of over HTTP.

**C.** Speaker post 754 breaks the API — root cause confirmed (§2, item 4). The §4 shortcode excludes it explicitly.

---

## §8 — Where this leaves the three original options

Superseded by the requirement change, kept for the record. The always-current requirement rules out any option that pre-renders and stores output, which is what made the earlier "true SSR via theme PHP" framing of Option 1 workable but static-leaning. A live-queried shortcode is still Option 1 in spirit — one code path, bots and visitors see the same real-time HTML by construction — just implemented in a way that also sidesteps Option 1's biggest blocker from the last revision (theme access via Future) entirely. Option 2 (dynamic rendering/prerendering) is ruled out directly: a snapshot is static by definition, however often it's regenerated. Option 3 (FacetWP) isn't revisited this round — still the larger lift of retrofitting FacetWP onto seven bespoke card grids built entirely outside it, and the shortcode already meets the requirement without it.

---

## §9 — Still to decide, once §3 resolves

1. **Hub roster cap.** Whether to cap the hub's server-rendered set (recommended in §2, item 5) rather than rendering all 999 published speakers in one response, and if so, at what number and by what priority order.
2. **Hub search scope.** Does the hub's search box need to reach beyond whatever gets server-rendered by default — i.e. search the full roster, not just the capped/prioritised set? If so, something still needs to serve that broader reach client-side, even once SSR covers the default view.
3. **Real ACF field names.** The §4 draft has two placeholder field names (`short_bio`, `fee_range`) that need confirming against the actual field map before the card output can be trusted to match the existing design.
4. **Rollout order across the real seven pages.** Deliberately not decided yet — premature until §3 resolves. Once it does, this plan gets updated with a concrete page-by-page order.

---

## §10 — Verification, once §3 is resolved and this rolls out for real

- `curl` each finished page's raw HTML — the same thing a non-JS crawler receives — and confirm the full matching speaker set is present as real `data-ssr="1"` markup, not just the original pinned handful.
- Cross-check the server-rendered count against the taxonomy term's real `count` to confirm nothing is silently truncated.
- Load each page normally with JavaScript on: identical visual design, no duplicate cards (expected to hold automatically per §2, item 3), search / filters / "Load more" behave exactly as they do today.
- Re-run the §6 cache-freshness check (edit a speaker, re-fetch, confirm the change appears) on each real page once it carries the shortcode, not just the diagnostic page — Hummingbird's behaviour could plausibly differ by URL or post type.
- Confirm speaker 754 is cleanly excluded on every page, with no PHP warning or error in the response.

---

## Not building further yet

Post 79215 is staged and the draft shortcode is written, but nothing is active. Waiting on the §6 runbook being run by whoever has WPCode admin and live network access — that's what actually answers §3's two open items. Once it reports back, this plan gets updated with a real rollout order for the seven live pages and the §9 decisions get closed out.

Prepared from a read-only review of the live page content and JavaScript, plus one new private (not publicly visible) diagnostic page created for §5. Live HTTP access and WPCode admin access were not available from this session (§3). No content, taxonomy term, or speaker/category/topic assignment was created, changed, or removed in the course of this review — the only write was creating post 79215 itself, and its query-affecting fields were left as drafted above.
