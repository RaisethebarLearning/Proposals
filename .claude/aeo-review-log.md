# AEO/SEO reviewer verdict log

Read by `rtb-seo-aeo-reviewer` at the start of every run so it has memory across invocations, since it has no Write access of its own. Whoever invokes the reviewer is responsible for appending its verdict here immediately after each run — newest entry at the bottom, dated, with the verdict and what was checked. Don't edit or delete past entries; a wrong verdict getting corrected later is itself a useful record.

---

## 2026-08-28 — Full review — AEO-server-side-rendering-plan.md (revision 3)

**Verdict: approved with conditions** (as a plan/process document; nothing built or deployed).

Run note: this run was executed by a general-purpose agent carrying the reviewer's full instructions verbatim, not the registered `rtb-seo-aeo-reviewer` subagent itself — that subagent was added mid-session and only registers on session restart. Functionally equivalent for this run; the real subagent should read this log on its first real invocation.

Network check: `curl` to `raisethebar.co.uk` failed with a 403 on the CONNECT itself (policy denial, not timeout) — confirmed via proxy status log, 6 occurrences. Corroborates, does not contradict, the plan's own §3 claim. No live HTTP checks (robots.txt, llms.txt, sitemap, raw HTML of any of the 7 pages or of post 79215) were possible from this environment.

**Blockers:**
1. §6 runbook step 2 never verifies `noindex,nofollow` is genuinely in the raw HTML response, not just saved in the Yoast admin field — given §5 already notes Yoast's robots meta isn't exposed via this session's REST connector. Fix: add a raw-HTML grep for the meta tag before treating the test page as safe, and reorder so noindex is set and confirmed *before* publishing, not after.
2. §3 items 1 (shortcode execution inside `wp:html`) and 2 (Hummingbird cache invalidation) remain open — correctly stated as unresolved by the plan, not reasoned around. Needs someone with WPCode admin + live network access to run §6.

**Unproven/secondhand claims flagged:** §7's page-by-page pattern table is explicitly stale ("carried forward, unchanged") and should be re-read immediately before rollout, not trusted from this revision; the 754 root-cause is sourced from an existing code comment (secondhand), not independently confirmed via the PHP error log; "999 published speakers" lacks the same explicit sourcing given to the other counts in the same paragraph; "private post = zero exposure" is standard WP behaviour but untested on this specific install, worth a curl-expect-404 check as part of §6 step 2; draft card CSS class names (`tp-card`, `tp-price` etc.) are presumed, not confirmed, alongside the already-flagged ACF field name TODOs.

**Non-blocking:** add explicit width/height to the draft `<img>` tag (low risk, aspect-ratio wrapper already mitigates most CLS); §10 verification has no post-rollout performance re-check against the baseline (mobile 57 / desktop 87 / CLS 0.115) despite the ~270KB/page markup cost landing on real visitors too, not just crawlers; **robots.txt / llms.txt / sitemap have never been checked in any revision** — the whole project assumes GPTBot/ClaudeBot/PerplexityBot/CCBot/Google-Extended are actually allowed to crawl these pages, and that's unverified. Recommended as a five-minute check before further §6 investment.

**Not checked (access gap, not oversight):** any live HTTP to raisethebar.co.uk; §3 items 1/2 directly; real ACF field map; freshness of §7's table; the published Artifact mirror (out of scope, no reason to distrust).
