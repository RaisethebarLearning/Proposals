# Second opinion request: Empower page rebuild for raisethebar.co.uk

You are reviewing work already done. Please challenge the decisions below, find bugs or risks, and say what you would do differently. You don't have access to the site, so everything you need is in this file. For code-level checks, the files `dist/empower-page.html`, `src/empower.css` and `build.py` can be attached alongside this one.

## The brief

- Replace the live page https://raisethebar.co.uk/programme/empower-women-in-business/ with a new design.
- The design came as a handoff: one HTML file (`empower-page-v5.html`) plus a README of design tokens and specs.
- Requirements: fast loading, built with SEO in mind, **no copy changes at all** (text, headings, FAQ answers, alt text, link labels).
- The handoff marks the visual design as final and high fidelity.

## The site

- WordPress. Custom theme "Raise The Bar" (folder `raisethebar`). ACF Pro, Yoast SEO Premium, Hummingbird (caching and minification), Redirection plugin.
- The current Empower page is a `programme` custom post type (ID 64064). The theme renders it entirely from ACF flexible-content fields, and its post content is empty.
- Recently rebuilt programme pages (Change Catalyst, Leadership Accelerator, Coaching for High Performance) follow a different pattern. Each is a standard **Page** under the parent "Development Solutions" (`/development-programmes/`), on the page template `blank-custom.php`, with the whole design in one Custom HTML block (inline `<style>` plus markup). The old `/programme/` CPT posts for those programmes still exist.
- My only access was a WordPress REST/MCP connector covering posts, pages, media and meta. I had no theme file access, couldn't write Yoast fields, couldn't manage Redirection, and couldn't fetch the live site from this environment.

## Key decision: how to build it

The handoff README recommends a proper theme page template with ACF repeaters, an enqueued stylesheet and JSON-LD generated in `wp_head`. I **did not** do that, for two reasons:

1. I had no way to write theme files.
2. The site's own recent builds use the Page + `blank-custom.php` + Custom HTML block pattern.

So I followed the site's existing pattern. Trade-off: content isn't editable through ACF fields, and the CSS is inline on the page rather than a cached, enqueued file.

**Please weigh in:** is the site pattern the right call for now, or should this wait for a developer to build the ACF template?

## What was built

A Python build script transforms the handoff HTML rather than retyping it. It then compares every visible text node and alt text against the handoff, in order, and fails the build on any difference. The check passes: 214 text nodes, all identical.

Changes from the handoff, none of which touch copy:

| Area | Handoff | Build | Why |
|---|---|---|---|
| Fonts | Inline `@font-face` pointing at `/themes/857ifd-raise-the-bar/` and `/themes/raise-the-bar/` | Removed. Uses the theme's registered `'Capitana', capitana` and `'Agenda', agenda` families, as Change Catalyst does | Those folders don't exist (the theme is `raisethebar`), so every font request would 404 before falling back |
| Hero headshots | Full originals, up to 1171px wide, displayed at 116px | 150px variant with a 300w option in `srcset`, `sizes="116px"`, width and height set to 116 | Large byte saving, no layout shift |
| Other images | Full originals, `loading="lazy"` | Media library variants with `srcset`/`sizes`, lazy loaded, width and height set. Only variants with the same crop as the edited original are used (WordPress keeps some sizes of the pre-crop image) | Right-sized downloads |
| Vimeo | iframe loads with the page | Poster image (existing cover, media 70880) in a `<button>`; the iframe is inserted on click with autoplay and `dnt=1`. Connection warms on hover or focus. `<noscript>` iframe fallback | Keeps the Vimeo player JS off the critical path |
| Rendering | None | `content-visibility:auto; contain-intrinsic-size:auto 900px` on sections from the quotes down | Less first-render work |
| JSON-LD | Course + FAQPage, with FAQ answers shortened and the price written as "1349 GBP" | Same Course data. FAQPage generated from the **visible** FAQ text, so it matches word for word. Linked by `@id` to Yoast's existing WebPage and Organization nodes | Schema should match visible content |
| Font sizes | Four `clamp()` minimums below the brand's 20px minimum | Raised to 20px, as the handoff README instructs | Brand rule |
| FAQ icon | Vertical bar translated +7.5px, so off centre | −7.5px, centred | Visual bug |
| Comments | Internal sign-off note about illustrative quotes | All HTML comments stripped | Would have been readable in public page source |
| "WordPress fixes" CSS | Large `!important` block of theme workarounds | Kept only the empty code-block bar fix and the text colour guard | The template doesn't have the padding problems the rest worked around |
| Mobile hero | `grid-template-columns:1fr` at ≤1000px | `minmax(0,1fr)` | Stops the huge H1 widening the column and pushing buttons past the gutter |

Output: about 60KB of HTML with inline CSS and JS, in one `wp:html` block.

## Current state

- Draft Page **79676**, slug `empower-women-in-business`, parent 64019, template `blank-custom.php`, featured image 79305. **Not published.** The live page is untouched.
- The content stored in WordPress was read back and is byte-identical to the build.
- A test save confirmed WordPress keeps `<style>`, `<script>`, JSON-LD and `&&` intact (the account has unfiltered HTML).
- Layout checked in headless Chromium at 1440px and 390px. Images and brand fonts were blocked in that environment, so it hasn't been visually checked with the real assets or the theme header and footer.

## Outstanding before go-live

1. The six testimonial quotes are illustrative, written from session outcomes. They need verified replacements or sign-off.
2. Yoast fields need entering by hand (the API wouldn't accept them). Proposed:
   - Title: `Empower | Women in Leadership Programme | Raise the Bar`
   - Meta description: `Four online masterclasses led by high-performing women in business, built around confidence, visibility, influence and performing under pressure. £1,349 + VAT.`
   - Focus keyphrase: `women in leadership programme`
   - Social image: existing `Empower.png` (79304)
3. **URL.** The new page will live at `/development-programmes/empower-women-in-business/` and the schema uses that URL. The old `/programme/empower-women-in-business/` needs a 301 redirect via Redirection. The old CPT post also feeds the programme listing cards, so what the listing links to needs checking.
4. Preview the draft logged in; after launch, run PageSpeed Insights and the Rich Results Test, and request indexing.

## Specific questions for you

1. **URL change.** Moving from `/programme/…` to `/development-programmes/…` with a 301, versus finding a way to keep the original URL. Which has the better SEO outcome here, given the sibling pages already use the new path?
2. **Inline CSS.** About 25KB of minified CSS inline on the page, versus an enqueued stylesheet. With Hummingbird page caching on, does this matter?
3. **`content-visibility:auto`.** Any risk to anchor links (`#empower-enquire` sits at the bottom and is the target for four CTAs), to find-in-page, or to how crawlers render the page?
4. **Video facade.** Is the poster-and-click approach right for SEO? There's no VideoObject schema, because the upload date and a real Vimeo thumbnail weren't available.
5. **FAQ schema.** Google now limits FAQ rich results mostly to government and health sites. Is it still worth including for AI answer engines, or is it noise?
6. **Fonts.** The build assumes the theme registers Capitana weights 400, 700, 800 and 900 and Agenda 300 and 700 under those family names. Any fallback worth adding in case it doesn't?
7. Anything in the markup or CSS that you think will break inside a WordPress theme wrapper.

## Known limitations I accept

- The Telent case-study image is a 660KB PNG (the 768px variant is 351KB). It should be re-exported as JPG or WebP.
- Flipped expert rows keep the handoff's column widths, so the text column is the narrower one. That matches the reference.
- The handoff's open brand notes still stand: the coloured left-border accents aren't a documented brand pattern, and the Empower symbol is a drawn SVG because no official logo exists.
