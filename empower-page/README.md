# Empower page rebuild

Replaces https://raisethebar.co.uk/programme/empower-women-in-business/ (programme post 64064, ACF layout).

**Status:** the new build is the content of the original Empower programme post **64064** (rewritten in place 7 October, keeping `/programme/empower-women-in-business/`). The post needs its template set to Blank in the editor so the new layout renders. Draft page 79676 is the earlier copy under `/development-programmes/`. It is unpublished and can be deleted.

## Files

- `reference/` design handoff as supplied (copy source of truth)
- `src/empower.css` page stylesheet, scoped under `.emp-page`
- `build.py` builds `dist/empower-page.html` from the reference and fails if any visible text or alt text differs from it
- `dist/empower-page.html` the exact content stored on draft 79676

Rebuild after any change: `python3 build.py`, then paste `dist/empower-page.html` into the page's Custom HTML block (or push it via the MCP connector).

## Changes signed off on 7 October

Applied through `EDITS` in `build.py`, so the copy check still guards everything else.

- More space above the hero (144px desktop, 96px mobile) to clear the site menu.
- Drawn Empower symbol replaced with the Raise the Bar arrow (`RTB-Pink-Arrow.png`, media 65815) on a purple-tint circle.
- Hero strip: "One place or fifty. No minimum." removed.
- Empower+ button now reads "Let's talk".
- Format and investment: Format card removed. The Investment card now runs full width, with the price on the left and the list on the right (stacked on mobile).
- All five enquiry buttons (both "Book places on the next cohort", "Talk to us about a group", "Let's talk" and "Enquire about Empower") open an email to enquiries@raisethebar.co.uk with the subject "Empower Enquiry", as on Change Catalyst.
- Network cards: tags moved to the bottom-left of the image so they don't cover faces (this was hiding Dame Kelly Holmes).

## What changed from the reference (no copy changes)

- Dropped the inline `@font-face` rules. They pointed at `/themes/857ifd-raise-the-bar/` and `/themes/raise-the-bar/`, which do not exist (the theme folder is `raisethebar`), so every font request would 404 before falling back. The page now uses the theme's own Capitana and Agenda, as Change Catalyst does.
- Images use the media library's sized variants with `srcset`/`sizes`. Hero avatars load a 150px file instead of up to 1171px originals. Everything below the hero is lazy loaded, with width and height set to stop layout shift.
- Vimeo loads on click behind a poster (existing cover, media 70880). The player's scripts no longer load with the page. There's a `<noscript>` iframe fallback.
- Sections below the experts use `content-visibility:auto` to cut first-render work.
- JSON-LD is generated from the visible FAQ text, so the schema matches the page word for word (the reference's schema had shortened answers and "1349 GBP"). Course and FAQPage link to Yoast's WebPage and Organization by `@id` instead of duplicating them.
- Brand 20px minimum applied to `.hero__sub`, `.q blockquote`, `.faq summary` and `.final p`.
- FAQ plus icon: the vertical bar was offset 7.5px the wrong way in the reference. Now centred.
- HTML comments removed, including the internal quote sign-off note, which would otherwise have been visible in the public page source.
- The WordPress-fixes block was cut to what the theme actually overrides: the empty code-block bar and theme text colours.

## Before go-live

1. **Quote sign-off.** The six quotes in "In their words" are illustrative. They need to be replaced with verified feedback, or Rucha needs to approve them.
2. **Yoast** (can't be set via the API, so add in the editor):
   - SEO title: `Empower | Women in Leadership Programme | Raise the Bar`
   - Meta description: `Four online masterclasses led by high-performing women in business, built around confidence, visibility, influence and performing under pressure. £1,349 + VAT.`
   - Focus keyphrase: `women in leadership programme`
   - Social image: `Empower.png` (79304), the same one the current page uses
   - Turn off Yoast's own FAQ/Course blocks if anyone adds them. The page already outputs both.
3. **URL.** The draft sits at `/development-programmes/empower-women-in-business/`, which matches Change Catalyst. The schema uses that URL. To keep the old URL instead, change `PAGE_URL` in `build.py`, rebuild and re-paste.
4. **Redirect.** When publishing, add a 301 in Redirection from `/programme/empower-women-in-business/` to the new URL. Leave the programme post published until the redirect is live, then set it to draft. It feeds the programme listing cards, so check what the Development Solutions page links to.
5. **Preview check.** Preview draft 79676 while logged in. Confirm the header and footer look right and fonts render in Capitana and Agenda.
6. After publishing, run PageSpeed Insights and the Rich Results Test on the live URL, then request indexing in Search Console.

## Worth doing later

- `Telent-crpped.png` is a 660KB PNG (the 768px variant is 351KB). A JPG or WebP export would cut that to under 60KB.
- Open brand notes from the handoff still stand: the coloured left-border accents (sections 5 and 6) and the drawn Empower symbol (no official logo in the brand assets).
