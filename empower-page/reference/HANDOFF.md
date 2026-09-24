# Handoff: Empower (Women in Business) programme page

## Overview
A marketing landing page for **Empower**, the Raise the Bar programme for women in business. It goes on raisethebar.co.uk (WordPress) at `/programme/empower-women-in-business/`. It sells four online masterclasses to L&D and talent buyers and drives enquiries to `/contact-us/`.

## About the design files
`empower-page-v5.html` is a **design reference built in HTML**. It is a single fragment: two `<style>` blocks, one `<div class="emp-page">` and a JSON-LD `<script>`. Right now it could be pasted into a Custom HTML block. The task is to **rebuild it properly inside the existing Raise the Bar WordPress theme**, following the theme's own patterns: a page template or Gutenberg/ACF blocks, the theme's enqueued fonts and CSS, and editable content fields. Choose whichever of those the theme already uses. Don't ship the pasted HTML as is.

**The copy is final. Do not change any text**, including headings, list items, FAQ answers, alt text and link labels.

## Fidelity
**High fidelity.** Colours, type, spacing, radii, shadows and states are final and have been checked against the Raise the Bar brand system. Match them exactly.

## Recommended WordPress structure
- Create a page template, e.g. `page-templates/programme-empower.php`, or a set of reusable "programme" blocks if the theme already has a block pattern for programme pages (Change Catalyst etc.). **Check first and reuse.**
- Put the CSS in an enqueued theme stylesheet (e.g. `assets/css/programme-empower.css`), loaded only on this template. Keep everything scoped under `.emp-page`.
- Fonts: the theme already ships Capitana and Agenda in `/wp-content/themes/<theme>/fonts/`. Use the theme's existing `@font-face` rules. The inline `@font-face` rules in the reference are only a fallback for the paste-in version.
- Editable content: use ACF (or blocks) for experts (repeater), quotes (repeater), why items, use items, Empower+ items, detail lists, featured speaker cards and FAQs (repeater). Hero stats, price and cohort months should be fields, because they repeat across the page and in the schema.
- **JSON-LD** (Course + FAQPage): generate it from the same ACF fields in `wp_head`, so the FAQ schema always matches the visible FAQs. If Yoast/RankMath already outputs page schema, merge rather than duplicate.
- The "WORDPRESS FIXES" `<style>` block in the reference is a set of `!important` workarounds for pasting into post content (hiding theme padding, the `wp-block-code` wrapper and colour drift). A proper template shouldn't need most of it. Drop whatever isn't needed and keep only what the theme genuinely overrides.
- Anchors that must exist: `#empower-experts`, `#empower-enquire`.

## Design tokens
Colours:
- Purple `#bf57ff` (primary accent, eyebrows, solid button, price card, final CTA)
- Pink `#f78888` (panel box, bullet accents)
- Green `#58ebce` (bullet/outline accents only)
- Ink `#15242b` (all headings, never true black)
- White `#ffffff`
- Faded white `#f4f0ed` (the "blush" sections)
- Purple tint `#e7e1ea` (the "lilac" sections)
- Pink tint `#ffd2cc` (the "rose" section, quote cards)
- Green tint `#d0f1e4` (quote cards, speaker tag)
- Text: fg-1 `#15242b`, fg-2 `#3b4a52` (body), fg-3 `#5c6a72` (credentials, tags)
- Lines: soft `rgba(21,36,43,0.08)`, default `rgba(21,36,43,0.16)`, strong `rgba(21,36,43,0.32)`

Type:
- Display: `'Capitana','Bahnschrift','DIN Alternate','Trebuchet MS',system-ui,sans-serif`. Weights used: 400, 700, 800, 900.
- Body: `'Agenda','Tahoma','Verdana',system-ui,sans-serif`. Base 20px / 1.55, weight 300 (Light) as the theme default, 700 for `strong`.
- **Brand minimum is 20px.** A few `clamp()` minimums in the reference still go below it: `.hero__sub` 19px, `.q blockquote` 19px, `.faq summary` 18px, `.final p` 19px. **Raise them all to a 20px minimum** in the build.
- Scale:
  - `.h1`: Capitana 900, `clamp(66px, 9.4vw, 132px)`, line-height 0.86, tracking -0.042em, uppercase
  - `.h2`: Capitana 900, `clamp(32px, 3.9vw, 52px)`, line-height 1.0, tracking -0.024em, uppercase, bottom margin 22px
  - `.h3`: Capitana 800, `clamp(21px, 2vw, 26px)`, line-height 1.14, tracking -0.012em
  - Eyebrow: Capitana 800, 20px, tracking 0.14em, uppercase, purple, bottom margin 18px
  - Lead / intro: Capitana 400, `clamp(20px, 1.7vw, 24px)`, line-height 1.48, fg-2, max-width 62ch
  - Body: Agenda, 20px, line-height 1.62, fg-2, max-width 68ch

Radii: md 8px, lg 12px (list cards), xl 20px (feature panels, images, cards), pill 999px (buttons, tags).

Shadows:
- sh-1 `0 1px 2px rgba(21,36,43,.06), 0 1px 3px rgba(21,36,43,.04)`
- sh-2 `0 4px 12px rgba(21,36,43,.08), 0 2px 4px rgba(21,36,43,.04)`
- sh-3 `0 12px 32px rgba(21,36,43,.12), 0 4px 8px rgba(21,36,43,.06)`

Motion: easing `cubic-bezier(0.22,1,0.36,1)`, durations 120ms (press) and 200ms (default).

Layout:
- `.wrap` max-width 1180px, side padding 28px (20px at ≤640px)
- Section padding 104px vertical (70px at ≤640px)
- Breakpoints: 1000px and 640px

## Components and states
- **Buttons** (pill, Capitana 800, 20px, uppercase, tracking 0.015em, padding 17px 32px, 2px border):
  - solid: purple background, white text. Hover: opacity 0.88.
  - outline: transparent background, ink text, strong-line border. Hover: ink fill, white text.
  - onpurple: ink background, white text. Hover: white background, ink text.
  - All buttons: press scale(0.97) over 120ms. Focus: 2px purple outline, 2px offset.
  - Buttons sit in a flex row with 14px gap and 34px top margin. At ≤640px they go full width.
- **Text links** (`.xp__link`, `.netlinks a`): Capitana 800, 20px, uppercase, tracking 0.05em, ink, 2px purple underline border, 4px padding below. Hover: purple text.
- **Cards** (speaker cards, detail cards): white, radius 20px, sh-2. Hover (speaker cards only, which are links): sh-3. No movement or scale.
- **FAQ**: native `<details>`/`<summary>`. Bottom border on each item. Plus icon drawn with `::before`/`::after` (18×3px purple bars, right side). When open, the vertical bar fades to 0 over 200ms. Focus: 2px purple outline. Keep native `<details>`, it's accessible and needs no JS.
- `prefers-reduced-motion`: kill transitions and the press scale.

## Sections (top to bottom)
1. **Hero**. White background, 84px top padding (56px mobile).
   - Grid `1.52fr 1fr`, 56px gap. Left column: eyebrow, H1 "Empower", `.hero__desc` (Capitana 800, `clamp(24px, 2.9vw, 40px)`, uppercase, purple), `.hero__line` (Capitana 700, `clamp(21px, 2vw, 28px)`, max 24ch, 3px ink top rule with 26px padding above), `.hero__sub`, then solid and outline buttons. Right column: the Empower symbol as inline SVG (purple circle plus cross, 26px stroke) at 78% width over a pink-tint circle at 85% opacity.
   - "Led by" strip: 2px ink top rule, a label, then a 4-column grid of leaders. Each leader has a 116px circular photo (4px white border, sh-2, 3px inner outline in purple, pink, green, purple in that order), the name in Capitana 800 20px, and a line in fg-3.
   - Stat strip: 1px top line, a flex row of Capitana 800 20px items (gap 12px 40px). The last item is purple.
   - Mobile: the grid stacks with the symbol first (max 230px). The leaders grid goes to 2 columns, then 1. The strip stacks.
2. **Problem**. White, 112px padding. 88×6px pink rule (radius 3), H2 (max 22ch), a paragraph in Capitana 400 `clamp(21px, 1.75vw, 25px)`, max 56ch.
3. **Experts** `#empower-experts`. Faded-white background. Eyebrow, H2, lead.
   - Four `.xp` rows: grid `0.86fr 1.14fr`, 62px gap, 72px vertical padding, soft divider line between rows. Rows 2 and 4 are flipped.
   - Media: square image, radius 20px, sh-3, object-position `center 16%`. Behind it sits a tint block offset 26px (purple, pink, green, purple tint per row).
   - Text: session label (Capitana 800, tracking 0.13em; purple on rows 1 and 4, ink on rows 2 and 3), name (Capitana 900, `clamp(30px, 3.4vw, 46px)`, uppercase), credentials (fg-3), topic (Capitana 800, `clamp(20px, 1.9vw, 25px)`), body, a "Key outcomes" label, an outcomes list with 11px dot bullets coloured per row, and a text link.
   - Closing `.panelbox`: pink background, radius 20px, padding 46px 48px, grid `1fr 1.4fr`, ink text.
   - Mobile: rows stack with the image first (max 420px) and the offset drops to 20px.
4. **Quotes**. Purple-tint background. A 3-column grid of 6 cards (gap 22px), each radius 20px with padding 36px 34px 32px.
   - Card backgrounds: 1 white + sh-2, 2 pink tint, 3 green tint, 4 green tint, 5 white + sh-2, 6 pink tint.
   - Each card: a purple Capitana 900 46px quote mark, the quote in Capitana 700, and a tag in Capitana 800 uppercase fg-3.
   - Below the grid: a note paragraph, then a Vimeo embed (16:9, radius 20px, sh-3, ink background). Grid goes to 2 columns, then 1.
   - **Sign-off note from the source:** these quotes are illustrative, written from documented session outcomes. They must be replaced with verified feedback, or approved by Rucha, before go-live.
5. **Why Empower**. White background. A 2×2 grid with hairline borders (1px vertical divider between columns, 34px/40px padding).
   - Each item: H3 in Capitana 800 23px with a 6px coloured bar on the left (purple, pink, green, purple), plus a paragraph.
   - Stacks to 1 column at ≤1000px.
6. **How organisations use it**. Pink-tint background. Grid `1.1fr 0.9fr`.
   - Left: eyebrow, H2, body.
   - Right: 3 white list cards (radius 12px, sh-1, padding 24px 28px) with a 6px left border in purple, pink, green.
7. **Host**. White background. Grid `300px 1fr`. Circular photo of Sarah Knight (6px white border, sh-3), eyebrow, H2, two body paragraphs.
8. **Empower+**. Faded-white background. Grid `1fr 1.05fr`.
   - Left: eyebrow, H2, lead, outline button.
   - Right: a list separated by hairlines. Each item has a bold Capitana title on its own line, then Agenda text.
9. **Details**. White background. Eyebrow, H2, lead, then a 2-column card grid.
   - Format card: white, sh-2, heading with a hairline underline, purple dot list.
   - Investment card: purple background, no shadow, price in Capitana 900 `clamp(42px, 4.8vw, 64px)` with the VAT line underneath, ink dot list.
   - Then solid and outline buttons.
10. **Network**. Faded-white background. Header in flex space-between: text on the left, two text links stacked on the right.
    - 3 speaker/case-study link cards. Image area 68% aspect, purple-tint placeholder background. Pill tag top-left (green tint "Featured speaker", pink tint "Case study"). Body: Capitana 900 21px uppercase title, then text.
    - Grid goes to 2 columns, then 1.
11. **FAQ**. Purple-tint background, max-width 900px. 13 items.
12. **Final CTA** `#empower-enquire`. Purple background, centred, max-width 800px. Eyebrow in ink, H2, paragraph in ink, and the onpurple button linking to `/contact-us/`.

## Colour-drift guard
The theme colours text on its own. Make sure headings are always `#15242b`, body text `#3b4a52`, eyebrows purple, and that all text on the purple and pink panels (`.panelbox`, `.dcard--price`, `.final`) is ink. Contrast on those panels depends on this.

## Open brand notes (the client's call, not changed)
- The use-list cards (section 6) and the Why H3 bars (section 5) use a coloured left-border accent. It isn't a documented brand pattern. It's fine to keep, but flag it.
- The Empower symbol is drawn as inline SVG because no official Empower logo exists in the brand assets. If one exists, swap it in.

## Assets
All images are already in the WordPress media library (`/wp-content/uploads/...`, URLs are in the reference file). In the build, pull them in as attachment IDs so WordPress can serve responsive `srcset`s.
- Expert headshots: Kate Richardson-Walsh, Sonya Barlow, Penny Haslam, Sarah Furness. Each is used twice, in the hero strip and in the expert row.
- Host: Sarah Knight.
- Network cards: Dame Kelly Holmes, Erica Farmer, Telent case study.
- Video: Vimeo `1135782879?h=3d23b5ca09`.
- Fonts: Capitana and Agenda, from the theme.

## Files
- `empower-page-v5.html`: the full design reference, with all copy, CSS, markup and JSON-LD.
