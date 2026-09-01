#!/usr/bin/env python3
"""Rebrand the mirrored Phoenix Consulting template into Asha Berkeley.

- All Phoenix names/emails/links -> Asha Berkeley (placeholders where unknown)
- Header logo + favicon -> assets/asha-logo.svg / assets/asha-favicon.svg
- Theme reds in site CSS -> Asha orange
"""
import re, os, glob

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asha-site")
PAGES = ["index.html", "about.html", "projects.html", "members.html", "join.html", "donations.html"]

# --- theme CSS: swap red palette for Asha orange ---
CSS_COLORS = {
    "355,55%,53%": "25,95%,53%",   # crimson -> vivid orange
    "359,72%,30%": "24,95%,42%",   # dark red accent -> deep orange
}
site_css = os.path.join(DIR, "assets", "215fb2a8_site.css")
css = open(site_css, encoding="utf-8", errors="replace").read()
for old, new in CSS_COLORS.items():
    css = css.replace(old, new)
open(site_css, "w", encoding="utf-8").write(css)
print("recolored", os.path.basename(site_css))

# dead-link placeholders for Phoenix pages we didn't mirror / their socials
LINK_MAP = [
    (r'href="https://www\.phoenixconsultinggroup\.org/membershome[^"]*"', 'href="members.html"'),
    (r'href="https://www\.phoenixconsultinggroup\.org/home[^"]*"', 'href="index.html"'),
    (r'href="https://www\.phoenixconsultinggroup\.org/[^"]*"', 'href="#"'),
    (r'href="https://www\.facebook\.com/[^"]*"', 'href="#"'),
    (r'href="https://www\.instagram\.com/[^"]*"', 'href="#"'),
    (r'href="https://www\.linkedin\.com/[^"]*"', 'href="#"'),
    (r'href="https://phoenixconsulting\.medium\.com[^"]*"', 'href="#"'),
]

for name in PAGES:
    p = os.path.join(DIR, name)
    html = open(p, encoding="utf-8").read()

    # names
    html = html.replace("Phoenix Consulting Group", "Asha Berkeley")
    html = html.replace("Phoenix Consulting", "Asha Berkeley")
    html = re.sub(r"\bPhoenix\b", "Asha", html)
    html = html.replace("pcgberkeley", "ashaberkeley")
    html = html.replace("phoenixrecruitment", "ashaberkeley")

    # emails (placeholder domain until the chapter's real address is confirmed)
    html = re.sub(r"\b([A-Za-z0-9._%+-]+)@phoenix\.berkeley\.edu\b", r"\1@ashaberkeley.org", html)

    # links
    for pat, repl in LINK_MAP:
        html = re.sub(pat, repl, html)
    # leftover domain mentions (canonical/og/meta/JSON)
    html = html.replace("www.phoenixconsultinggroup.org", "www.ashaberkeley.org")
    html = html.replace("phoenixconsultinggroup.org", "ashaberkeley.org")

    # header logo images
    html = re.sub(
        r'(<img[^>]*elementtiming="nbf-header-logo[^"]*"[^>]*src=")[^"]*(")',
        r"\1assets/asha-logo.svg\2", html)
    # any other Phx logo usages (footer etc.)
    html = re.sub(r'(src=")assets/[0-9a-f]{8}_White_Phx_Logo[^"]*(")', r"\1assets/asha-logo.svg\2", html)

    # favicon
    html = re.sub(
        r'<link rel="icon"[^>]*>',
        '<link rel="icon" type="image/svg+xml" href="assets/asha-favicon.svg"/>', html)

    open(p, "w", encoding="utf-8").write(html)
    left = len(re.findall(r"(?i)phoenix", html))
    print(f"{name}: rebranded ({left} case-insensitive 'phoenix' strings left)")

print("done")
