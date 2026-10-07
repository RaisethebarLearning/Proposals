#!/usr/bin/env python3
"""Build the WordPress-ready Empower page from the design reference.

The copy is taken from reference/empower-page-v5.html untouched. This script only
swaps the CSS, image markup, video embed and JSON-LD, then checks that every
visible word survived.

    python3 build.py            -> dist/empower-page.html (wp:html block content)
"""
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent
REF = ROOT / "reference" / "empower-page-v5.html"
CSS = ROOT / "src" / "empower.css"
OUT = ROOT / "dist" / "empower-page.html"

# Final public URL of the page. Change here if it goes live somewhere else.
PAGE_URL = "https://raisethebar.co.uk/programme/empower-women-in-business/"
UP = "https://raisethebar.co.uk/wp-content/uploads/"

# Media library variants, same crop as the original only (WordPress keeps some
# sizes of the pre-crop original, which are left out on purpose).
# Each entry: list of (path, width, height).
MEDIA = {
    "kate": [("2024/04/Kate-Headshot-2.0-e1730390055674-150x150.jpeg", 150, 150),
             ("2024/04/Kate-Headshot-2.0-e1730390055674-300x287.jpeg", 300, 287),
             ("2024/04/Kate-Headshot-2.0-e1730390055674-768x734.jpeg", 768, 734),
             ("2024/04/Kate-Headshot-2.0-e1730390055674-1024x979.jpeg", 1024, 979)],
    "sonya": [("2025/05/Sonya-Barlow-1-2024-e1746550145924-150x150.jpg", 150, 150),
              ("2025/05/Sonya-Barlow-1-2024-e1746550145924-300x300.jpg", 300, 300),
              ("2025/05/Sonya-Barlow-1-2024-e1746550145924-600x600.jpg", 600, 600),
              ("2025/05/Sonya-Barlow-1-2024-e1746550145924-768x705.jpg", 768, 705),
              ("2025/05/Sonya-Barlow-1-2024-e1746550145924.jpg", 1000, 918)],
    "penny": [("2024/04/1730381280592-e1731927873331-150x150.jpg", 150, 150),
              ("2024/04/1730381280592-e1731927873331-300x254.jpg", 300, 254),
              ("2024/04/1730381280592-e1731927873331-768x651.jpg", 768, 651),
              ("2024/04/1730381280592-e1731927873331.jpg", 800, 678)],
    "furness": [("2024/04/IMG_6591-e1750168095885-150x150.jpeg", 150, 150),
                ("2024/04/IMG_6591-e1750168095885-300x300.jpeg", 300, 300),
                ("2024/04/IMG_6591-e1750168095885-600x600.jpeg", 600, 600),
                ("2024/04/IMG_6591-e1750168095885-768x615.jpeg", 768, 615),
                ("2024/04/IMG_6591-e1750168095885.jpeg", 1024, 820)],
    "knight": [("2024/03/sarah-knight-300x300.jpg", 300, 300),
               ("2024/03/sarah-knight.jpg", 349, 349)],
    "kelly": [("2024/04/Dame-Kelly_Holmes_DKH_ProfilePic-266x300.jpeg", 266, 300),
              ("2024/04/Dame-Kelly_Holmes_DKH_ProfilePic-768x866.jpeg", 768, 866),
              ("2024/04/Dame-Kelly_Holmes_DKH_ProfilePic-908x1024.jpeg", 908, 1024)],
    "erica": [("2025/05/Erica_Farmer_Erica-Farmer-4-200x300.jpg", 200, 300),
              ("2025/05/Erica_Farmer_Erica-Farmer-4-683x1024.jpg", 683, 1024),
              ("2025/05/Erica_Farmer_Erica-Farmer-4-768x1152.jpg", 768, 1152)],
    "telent": [("2026/05/Telent-crpped-300x151.png", 300, 151),
               ("2026/05/Telent-crpped-768x387.png", 768, 387),
               ("2026/05/Telent-crpped.png", 1005, 507)],
}
# Original src in the reference -> media key
SRC_KEY = {
    "2024/04/Kate-Headshot-2.0-e1730390055674.jpeg": "kate",
    "2025/05/Sonya-Barlow-1-2024-e1746550145924.jpg": "sonya",
    "2024/04/1730381280592-e1731927873331.jpg": "penny",
    "2024/04/IMG_6591-e1750168095885.jpeg": "furness",
    "2024/03/sarah-knight.jpg": "knight",
    "2024/04/Dame-Kelly_Holmes_DKH_ProfilePic.jpeg": "kelly",
    "2025/05/Erica_Farmer_Erica-Farmer-4-scaled.jpg": "erica",
    "2026/05/Telent-crpped.png": "telent",
}
# Rendered widths per image role, used for `sizes` and to pick the fallback src.
ROLE = {
    "ledby__img": {"sizes": "116px", "min": 116, "max": 300},
    "xp__img": {"sizes": "(max-width: 1000px) min(420px, calc(100vw - 40px)), 480px", "min": 480, "max": 1024},
    "host__img": {"sizes": "(max-width: 1000px) 260px, 300px", "min": 300, "max": 349},
    "spkr": {"sizes": "(max-width: 640px) calc(100vw - 40px), (max-width: 1000px) 50vw, 380px", "min": 380, "max": 1024},
}
VIDEO_POSTER = [("2024/03/Vimeo-covers-1-768x432.png", 768, 432),
                ("2024/03/Vimeo-covers-1-1024x576.png", 1024, 576),
                ("2024/03/Vimeo-covers-1-1536x864.png", 1536, 864)]
VIMEO_SRC = "https://player.vimeo.com/video/1135782879?h=3d23b5ca09"


def srcset(variants):
    return ", ".join(f"{UP}{p} {w}w" for p, w, _ in variants)


def pick(variants, min_w):
    """Smallest variant at least min_w wide, else the largest."""
    for v in variants:
        if v[1] >= min_w:
            return v
    return variants[-1]


def rebuild_img(m):
    tag = m.group(0)
    src = re.search(r'src="([^"]+)"', tag).group(1).replace(UP, "")
    if src not in SRC_KEY:
        return tag  # single-size asset, used as is
    alt = re.search(r'alt="([^"]*)"', tag).group(1)
    cls = re.search(r'class="([^"]+)"', tag)
    cls = cls.group(1) if cls else None
    role = ROLE[cls] if cls else ROLE["spkr"]
    variants = [v for v in MEDIA[SRC_KEY[src]] if v[1] <= role["max"]]
    fb = pick(variants, role["min"])
    if cls == "ledby__img":
        w = h = 116  # rendered size, stops layout shift in the hero
        lazy = ""
    else:
        w, h = fb[1], fb[2]
        lazy = ' loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{UP}{fb[0]}" srcset="{srcset(variants)}" sizes="{role["sizes"]}"'
            f' alt="{alt}" width="{w}" height="{h}"{lazy} decoding="async" />')


VIDEO_HTML = f"""<div class="vid">
        <button type="button" class="vid__btn" data-src="{VIMEO_SRC}&amp;autoplay=1&amp;dnt=1" aria-label="Play video: Empower programme">
          <img src="{UP}{VIDEO_POSTER[0][0]}" srcset="{srcset(VIDEO_POSTER)}" sizes="(max-width: 1180px) calc(100vw - 40px), 1124px" alt="" width="768" height="432" loading="lazy" decoding="async" />
          <span class="vid__play" aria-hidden="true"></span>
        </button>
        <noscript><iframe title="Empower programme" src="{VIMEO_SRC}&amp;dnt=1" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></noscript>
      </div>"""

# Tiny loader: swap the poster for the Vimeo iframe on click, warm the connection on hover.
VIDEO_JS = """<script>
(function(){var b=document.querySelectorAll('.emp-page .vid__btn');for(var i=0;i<b.length;i++){(function(btn){var warm=function(){if(warm.done)return;warm.done=1;var l=document.createElement('link');l.rel='preconnect';l.href='https://player.vimeo.com';document.head.appendChild(l);};btn.addEventListener('pointerenter',warm,{once:true});btn.addEventListener('focus',warm,{once:true});btn.addEventListener('click',function(){var f=document.createElement('iframe');f.src=btn.getAttribute('data-src');f.title='Empower programme';f.allow='autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share';f.setAttribute('allowfullscreen','');f.referrerPolicy='strict-origin-when-cross-origin';btn.parentNode.replaceChild(f,btn);f.focus();});})(b[i]);}})();
</script>"""


class TextGrab(HTMLParser):
    """Collect visible text plus alt text, skipping style/script."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.out = []

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "noscript"):
            self.skip += 1
        if tag == "img":
            alt = dict(attrs).get("alt")
            if alt:
                self.out.append(f"[alt:{alt}]")

    def handle_endtag(self, tag):
        if tag in ("style", "script", "noscript"):
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.out.append(" ".join(data.split()))


def visible_text(markup):
    p = TextGrab()
    p.feed(markup)
    return p.out


def faq_items(markup):
    """Pull question and answer text from the visible FAQ so the schema always matches."""
    items = []
    for d in re.findall(r"<details>(.*?)</details>", markup, re.S):
        q = re.search(r"<summary>(.*?)</summary>", d, re.S).group(1)
        paras = re.findall(r"<p>(.*?)</p>", d, re.S)
        clean = lambda s: " ".join(html.unescape(re.sub(r"<[^>]+>", "", s)).split())
        items.append((clean(q), " ".join(clean(p) for p in paras)))
    return items


def schema(markup):
    course = {
        "@type": "Course",
        "@id": PAGE_URL + "#course",
        "name": "Empower: Women in Leadership Programme",
        "description": "Four online masterclasses led by high-performing women in business, built around what slows progression for women at work: confidence, visibility, influence and performing under pressure.",
        "url": PAGE_URL,
        "mainEntityOfPage": {"@id": PAGE_URL},
        "inLanguage": "en-GB",
        "provider": {"@type": "Organization", "@id": "https://raisethebar.co.uk/#organization", "name": "Raise the Bar", "url": "https://raisethebar.co.uk/"},
        "audience": {"@type": "Audience", "audienceType": "High-performing female managers, emerging leaders and identified talent"},
        "offers": {"@type": "Offer", "price": "1349", "priceCurrency": "GBP", "category": "Per person, excluding VAT",
                   "availability": "https://schema.org/InStock", "url": PAGE_URL},
        "hasCourseInstance": {
            "@type": "CourseInstance",
            "courseMode": "Online",
            "courseWorkload": "PT4H",
            "instructor": [{"@type": "Person", "name": n} for n in
                           ("Kate Richardson-Walsh OBE", "Sonya Barlow", "Penny Haslam", "Sarah Furness")],
        },
    }
    faq = {
        "@type": "FAQPage",
        "@id": PAGE_URL + "#faq",
        "isPartOf": {"@id": PAGE_URL},
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in faq_items(markup)],
    }
    data = {"@context": "https://schema.org", "@graph": [course, faq]}
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
            + "</script>")


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    css = re.sub(r":\s+", ":", css)
    return css.replace(";}", "}").strip()


# Changes signed off after the handoff (7 Oct). Applied to the reference before
# the build, so the copy check still guards everything else.
ARROW = UP + "2024/04/RTB-Pink-Arrow.png"
MAILTO = "mailto:enquiries@raisethebar.co.uk?subject=Empower%20Enquiry"
EDITS = [
    # Raise the Bar arrow replaces the drawn Empower symbol
    (r'<svg viewBox="0 0 200 320".*?</svg>',
     f'<img src="{ARROW}" alt="" width="528" height="528" decoding="async" />'),
    # Hero strip: drop the "no minimum" flag
    (r'\s*<span class="flag">One place or fifty\. No minimum\.</span>', ""),
    # Empower+ button label
    (r'>Talk to us about scope</a>', ">Let&rsquo;s talk</a>"),
    # Final CTA opens an email, as on Change Catalyst
    (r'href="https://raisethebar\.co\.uk/contact-us/">Enquire about Empower',
     f'href="{MAILTO}">Enquire about Empower'),
    # Every enquiry button opens the same email (4 buttons)
    (r'href="#empower-enquire"', f'href="{MAILTO}"', 4),
    # FAQ: drop the Change Catalyst comparison
    (r'\s*<details>\s*<summary>How does Empower compare to Change Catalyst\?</summary>.*?</details>', ""),
    # Format and investment: remove the Format card
    (r'\s*<div class="dcard">\s*<h3>Format</h3>.*?</ul>\s*</div>', ""),
]


def apply_edits(markup):
    for pattern, repl, *expect in EDITS:
        expect = expect[0] if expect else 1
        markup, n = re.subn(pattern, repl, markup, count=expect, flags=re.S)
        if n != expect:
            sys.exit(f"Edit did not apply: {pattern}")
    return markup


def build():
    ref = apply_edits(REF.read_text(encoding="utf-8"))
    body = re.search(r'(<div class="emp-page">.*</div>)\s*<script type="application/ld\+json">', ref, re.S).group(1)

    body = re.sub(r"<!--.*?-->\s*", "", body, flags=re.S)  # internal notes must not ship in page source
    body = re.sub(r"<img\b[^>]*>", rebuild_img, body)
    body = re.sub(r'<div class="vid">.*?</div>', VIDEO_HTML, body, count=1, flags=re.S)
    # Defer rendering of sections well below the fold
    body = re.sub(r'<section class="(s(?: s--(?:lilac|rose|blush))?)">', r'<section class="\1 cv">', body)
    body = body.replace('<section class="s final" id="empower-enquire">', '<section class="s final cv" id="empower-enquire">')
    # Tidy indentation to keep the payload small
    body = "\n".join(line.strip() for line in body.splitlines() if line.strip())

    out = ("<!-- wp:html -->\n"
           f"<style>{minify_css(CSS.read_text(encoding='utf-8'))}</style>\n"
           f"{body}\n{schema(ref)}\n{VIDEO_JS}\n"
           "<!-- /wp:html -->\n")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(out, encoding="utf-8")

    # Guard: every visible string and alt text in the reference must be in the build, in order.
    before, after = visible_text(ref), visible_text(out)
    if before != after:
        import difflib
        sys.stderr.write("\n".join(difflib.unified_diff(before, after, "reference", "build", lineterm="")))
        sys.exit("Copy check FAILED: visible text differs from the reference")
    faqs = faq_items(ref)
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(out.encode()):,} bytes). "
          f"Copy check passed on {len(before)} text nodes. FAQ schema items: {len(faqs)}.")


if __name__ == "__main__":
    build()
