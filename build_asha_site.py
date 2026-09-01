#!/usr/bin/env python3
"""Build the full Asha Berkeley site.

Design rules (2026-08-31 direction):
- Flat colors only. No gradients, no glows, no background animations.
- Jaini Purva for headings, template typekit font for body.
- Real photos from the chapter (assets/photo-*.jpg).
- No emoji as icons. Copy sounds human, no em dashes.
- Animations only on interaction: nav underline, hover lifts.
- Each page opens with a different structure (home: photo hero; about: text
  statement; projects: slim header straight into the list; members: figure
  first; join: split screen; donations: centered flat).
Uses the mirrored Squarespace template only as chrome (header/nav/footer).
"""
import re, os, glob

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asha-site")
EMAIL = "berkeley@ashanet.org"
VENMO = "https://account.venmo.com/u/ashaberkeley"
AIRTABLE = "https://airtable.com/appoZNPc6yCmgft2f/shrN8PH1w1WBdqNJb"
AIRTABLE_EMBED = "https://airtable.com/embed/appoZNPc6yCmgft2f/shrN8PH1w1WBdqNJb?viewControls=on"

# from ~/Downloads/Coffee Chat Info F26.xlsx (Antara deduped)
MEMBERS = [
    ("Divya Kukreja", "President", "Senior", "Thai food hunts and a good workout",
     "https://www.linkedin.com/in/divya-kukreja-8aa320287", "https://calendly.com/divyakukreja16/new-meeting"),
    ("Rohan Vallamshetla", "Vice President", "Sophomore", "Skiing, climbing, and movie nights",
     "https://www.linkedin.com/in/rohan-vallamshetla-644b112b6/", "https://calendly.com/rohanvallamshetla-berkeley/coffee-chats"),
    ("Arya Raghavan", "Treasurer", "Junior", "Backpacking, reading, and matcha",
     "https://www.linkedin.com/in/arya-raghavan", "https://calendly.com/aryar-berkeley/arya-coffee-chat"),
    ("Sanjana Kolar", "Logistics", "Junior", "Guitar, Survivor, and board games",
     "https://www.linkedin.com/in/sanjanakolar/", "https://calendly.com/sanjanakolar-berkeley/cyc-coffee-chat"),
    ("Hrutva Patel", "Logistics", "Sophomore", "Baking and crafts",
     "https://www.linkedin.com/in/hrutva-patel/", "https://calendly.com/hrutvap-berkeley"),
    ("Antara Majumder", "Internal", "Junior", "Traveling, hiking, and trying new foods",
     "https://www.linkedin.com/in/antara-majumder-2621b3317/", "https://calendly.com/antara_maj-berkeley/asha-coffee-chats"),
    ("Niki Itharaja", "Internal", "Junior", "Ask about the boat social",
     "", "https://calendly.com/niki-itharaja-berkeley/30min"),
    ("Anya Garg", "Projects", "Sophomore", "Pilates, baking, and SF trips",
     "https://www.linkedin.com/in/anya-garg-42b3412aa/", "https://calendly.com/anya-garg/30min"),
    ("Pahel Tandel", "Projects", "Junior", "Romance novels and vintage shops",
     "https://www.linkedin.com/in/pahel-tandel-717272306/", "https://calendly.com/paheltandel-berkeley/pahel-s-projects-coffee-chats"),
    ("Aniruddh Mohan", "Consulting", "Sophomore", "Golf, skiing, and mountaineering",
     "https://www.linkedin.com/in/aniruddhmo/", "https://calendly.com/mohan_aniruddh-berkeley/asha-for-education-coffee-chat"),
    ("Akshaya Perni", "Marketing", "Junior", "Hiking, tennis, and reading",
     "https://www.linkedin.com/in/akshaya-perni-92a5022a3", "https://calendly.com/aperni06-berkeley/30min"),
    ("Sanjana Premkumar", "Marketing", "Junior", "Reading and roller coasters",
     "https://www.linkedin.com/in/sanjana-premkumar/", "https://cal.com/sanjana-premkumar-ispxmr"),
]


# ---------------------------------------------------------------- chrome ----
def find_div_block(html, start):
    depth = 0
    for m in re.finditer(r"<div\b|</div>", html[start:]):
        depth += 1 if m.group(0) != "</div>" else -1
        if depth == 0:
            return start + m.end()
    raise ValueError("unbalanced divs")


src = open(os.path.join(DIR, "join.html"), encoding="utf-8").read()
i, j = src.find("<main"), src.find("</main>") + len("</main>")
head, foot = src[:i], src[j:]

head = head.replace(" header-nav-item--active", "").replace(" header-menu-nav-item--active", "")
head = head.replace('aria-current="page"', "")

while True:
    fstart = head.find('<div class="header-nav-item header-nav-item--folder">')
    if fstart == -1:
        break
    fend = find_div_block(head, fstart)
    head = head[:fstart] + (
        '<div class="header-nav-item header-nav-item--collection">\n'
        '      <a href="members.html" data-animation-role="header-element">\n'
        '        Members\n      </a>\n    </div>') + head[fend:]

head = re.sub(r'data-folder-id="members\.html"\s*href="members\.html"',
              'href="members.html"', head)
while True:
    pstart = head.find('<div data-folder="members.html" class="header-menu-nav-folder">')
    if pstart == -1:
        break
    pend = find_div_block(head, pstart)
    head = head[:pstart] + head[pend:]
head = head.replace('<span class="visually-hidden">Folder:</span>', "")

head = re.sub(
    r'<div class="[^"]*(?:header-nav-item|header-nav-folder-item|header-menu-nav-item)'
    r'[^"]*--external[^"]*">\s*<a[^>]*>\s*Health Engine\s*</a>\s*</div>', "", head)
head = re.sub(
    r'<div class="header-nav-item[^"]*">\s*<a[^>]*>\s*DeCal\s*</a>\s*</div>', "", head)
head = re.sub(
    r'<div class="container header-menu-nav-item[^"]*">\s*<a[^>]*>\s*'
    r'<div class="header-menu-nav-item-content">\s*DeCal\s*</div>\s*</a>\s*</div>', "", head)


def swap_assets(s):
    s = re.sub(r'assets/[0-9a-f]{8}_White_Phx_Logo[^"\\ ,)]*', "assets/asha-logo.svg", s)
    s = re.sub(r'assets/[0-9a-f]{8}_Untitled_Artwork[^"\\ ,)]*', "assets/asha-logo.svg", s)
    s = re.sub(r'assets/[0-9a-f]{8}_PCG[^"\\ ,)]*', "assets/asha-footer-bg.svg", s)
    s = re.sub(r'assets/[0-9a-f]{8}_phx_chibi[^"\\ ,)]*', "assets/asha-favicon.svg", s)
    s = re.sub(r'(?:PCG|Phoenix[_ ]Consulting-?)[0-9]*\.(?:jpg|jpeg|png)', "asha-footer-bg.svg", s)
    s = s.replace("facebook.com/ucbpcg", "facebook.com/ashaberkeley")
    return s


head, foot = swap_assets(head), swap_assets(foot)

# stop the header items vanishing and re-animating on every page load
head = head.replace(' data-animation-role="header-element"', "")
foot = foot.replace(' data-animation-role="header-element"', "")
foot = foot.replace(' data-animation-role="image"', "")
foot = re.sub(r'\s*data-animation-role="image"', "", foot)
# kill the typekit wf-loading hide (made all text transparent for up to 3s per load)
head = head.replace("<script>document.documentElement.classList.add('wf-loading')</script>", "")
head = re.sub(r'<style>@keyframes fonts-loading.*?</style>', "", head, flags=re.S)

head = re.sub(r'(property="og:image" content=")[^"]*(")', r"\1assets/asha-logo.svg\2", head)
head = re.sub(r'(itemprop="(?:image|thumbnailUrl)" content=")[^"]*(")', r"\1assets/asha-logo.svg\2", head)
head = re.sub(r'(<link rel="image_src" href=")[^"]*(")', r"\1assets/asha-logo.svg\2", head)
foot = re.sub(r'(src=")assets/[0-9a-f]{8}_PCG[^"]*(")', r"\1assets/asha-footer-bg.svg\2", foot)
foot = re.sub(r'(srcset=")[^"]*(")', r"\1\2", foot)

# replace the template's fluid-grid footer with a flat, evenly spaced one
FOOTER_HTML = f'''
<div class="asha-footer">
  <img src="assets/asha-logo.svg" alt="Asha Berkeley"/>
  <nav class="asha-footer-nav">
    <a href="about.html">About</a>
    <a href="projects.html">Projects</a>
    <a href="members.html">Members</a>
    <a href="join.html">Join</a>
    <a href="donations.html">Donations</a>
  </nav>
  <p><a href="mailto:{EMAIL}">{EMAIL}</a> &nbsp;&middot;&nbsp;
     <a href="{VENMO}" target="_blank" rel="noopener">Venmo @ashaberkeley</a></p>
  <p class="fineprint">Asha for Education, UC Berkeley chapter. Secular, volunteer run,
  every dollar to the classroom.</p>
</div>'''
foot = re.sub(r'(<footer[^>]*data-footer-sections[^>]*>).*?(</footer>)',
              lambda m: m.group(1) + FOOTER_HTML + m.group(2), foot, count=1, flags=re.S)

# strip the scroll-toggle script a previous build injected (chrome is self-sourced)
foot = re.sub(r"<script>\(function\(\)\{var h=document\.getElementById\('header'\).*?</script>\n?",
              "", foot, flags=re.S)

# disable the template's dynamic (fade in/out) header behavior at the config level
head = head.replace("&quot;headerStyle&quot;: &quot;dynamic&quot;",
                    "&quot;headerStyle&quot;: &quot;solid&quot;")
head = head.replace('data-header-style="dynamic"', 'data-header-style="solid"')

# drop the stale mobile "/members" folder panel (Back button + duplicate link)
while True:
    pstart = head.find('<div data-folder="/members" class="header-menu-nav-folder">')
    if pstart == -1:
        break
    pend = find_div_block(head, pstart)
    head = head[:pstart] + head[pend:]
# old placeholder email may linger in chrome text
head = head.replace("contact@ashaberkeley.org", EMAIL)
foot = foot.replace("contact@ashaberkeley.org", EMAIL)


def set_title(html, title):
    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1, flags=re.S)
    html = re.sub(r'(property="og:title" content=")[^"]*(")', r"\1" + title + r"\2", html)
    return html


def set_active(html, href):
    if not href:
        return html
    html = re.sub(
        r'<div class="header-nav-item header-nav-item--collection">(\s*<a\s+href="' + href + '")',
        r'<div class="header-nav-item header-nav-item--collection header-nav-item--active">\1 aria-current="page"',
        html, count=1)
    html = re.sub(
        r'<div class="container header-menu-nav-item header-menu-nav-item--collection">(\s*<a\s+href="' + href + '")',
        r'<div class="container header-menu-nav-item header-menu-nav-item--collection header-menu-nav-item--active">\1 aria-current="page"',
        html, count=1)
    return html


# ------------------------------------------------------------- shared css ---
ASHA_CSS = '''<style>
  @font-face { font-family:'Jaini Purva';
    src:url('assets/jaini-purva-latin.woff2') format('woff2'); font-display:swap; }

  .asha { --bg:#0f0b07; --panel:#171109; --line:#2e2214; --orange:#f27b21;
          --orange-deep:#c85f10; --cream:#f4e9d7; --muted:#c9b89e;
          color:var(--cream); background:var(--bg); }
  .asha h1,.asha h2,.asha h3,.asha .num {
    font-family:'Jaini Purva',serif !important; font-weight:400 !important;
    letter-spacing:.015em; color:var(--cream); }
  .asha em { font-style:normal; color:var(--orange); }

  /* dark overscroll so fast scrolling never flashes white */
  html, body { background:#0f0b07 !important; }

  /* keep the header pinned and fully transparent; kill the template's
     "dynamic" header animation that faded it in and out on scroll */
  #header { position:fixed !important; top:0; left:0; right:0; z-index:1000;
    background:transparent !important; transform:none !important;
    opacity:1 !important; transition:none !important; visibility:visible !important; }
  #header .header-background { display:none !important; }
  #header .header-announcement-bar-wrapper { transform:none !important;
    transition:none !important; }
  #header .header-blur-background { display:none !important; }

  /* header text: own colors (theme went black on transparent bg) + theme font */
  #header .header-inner, #header .header-inner * { opacity:1 !important;
    visibility:visible !important; }
  #header .header-nav-item a { color:#f4e9d7 !important;
    font-family:'Jaini Purva',serif !important; font-size:1.25rem;
    letter-spacing:.05em; }
  #header .header-title-logo a, #header .header-mobile-logo a { color:#f4e9d7 !important; }
  #header .burger-inner > div { background-color:#f4e9d7 !important; }
  .header-menu-nav-item a { font-family:'Jaini Purva',serif !important; }

  /* nav highlight animation for the top pages */
  .header-nav-item a { position:relative; transition:color .2s ease; }
  .header-nav-item a::after { content:""; position:absolute; left:0; right:0;
    bottom:-6px; height:2px; background:#f27b21;
    transform:scaleX(0); transform-origin:left center; transition:transform .28s ease; }
  .header-nav-item a:hover::after,
  .header-nav-item--active a::after { transform:scaleX(1); }
  .header-nav-item a:hover { color:#f27b21 !important; }

  .asha-kicker { display:block; font-size:.82rem; letter-spacing:.3em;
    text-transform:uppercase; color:var(--orange); margin-bottom:1.2em; }
  .asha-sub { font-size:clamp(1.02rem,1.4vw,1.2rem); line-height:1.7;
    max-width:560px; margin:0 0 2em; }
  .asha-ctas { display:flex; gap:1em; flex-wrap:wrap; align-items:center; }
  .asha-btn { display:inline-block; font-weight:600; font-size:1rem;
    color:#171109 !important; text-decoration:none; padding:.9em 2em;
    border-radius:6px; background:var(--orange); border:1px solid var(--orange);
    transition:background .2s ease, transform .2s ease; }
  .asha-btn:hover { background:var(--orange-deep); border-color:var(--orange-deep);
    transform:translateY(-2px); }
  .asha-btn--ghost { background:transparent; color:var(--cream) !important;
    border:1px solid rgba(244,233,215,.45); }
  .asha-btn--ghost:hover { background:rgba(244,233,215,.08); border-color:var(--cream);
    transform:translateY(-2px); }

  /* home hero: text sits high, in the immediate landing view */
  .asha-hero { position:relative; display:flex; align-items:center;
    min-height:88vh; padding:13vh 7vw 8vh; background-size:cover;
    background-position:center; }
  .asha-hero .shade { position:absolute; inset:0; background:rgba(12,8,4,.62); }
  .asha-hero-inner { position:relative; z-index:2; max-width:820px; }
  .asha-hero h1 { font-size:clamp(3rem,7vw,5.4rem); line-height:1.02; margin:0 0 .3em; }

  /* page header, centered in the landing view (projects, members, donations) */
  .asha-pagehead { min-height:56vh; display:flex; flex-direction:column;
    justify-content:center; align-items:center; text-align:center;
    padding:14vh 7vw 4vh; }
  .asha-pagehead h1 { font-size:clamp(2.4rem,4.6vw,3.8rem); margin:.2em 0 .3em; }
  .asha-pagehead p { max-width:600px; line-height:1.7; color:var(--muted); margin:0 auto; }
  .asha-pagehead--snug { min-height:0; padding:15vh 7vw 5vh; }

  /* editorial statement opening (about) */
  .asha-statement { padding:17vh 7vw 6vh; }
  .asha-statement h1 { font-size:clamp(2.6rem,5.4vw,4.6rem); line-height:1.08;
    max-width:940px; margin:.2em 0 0; }

  /* split opening (join); fills the landing so the next section arrives on scroll */
  .asha-split { display:flex; min-height:100vh; flex-wrap:wrap; }
  .asha-split-text { flex:1 1 460px; display:flex; flex-direction:column;
    justify-content:center; padding:16vh 5vw 8vh 7vw; background:var(--panel); }
  .asha-split-text h1 { font-size:clamp(2.6rem,4.8vw,4rem); line-height:1.05;
    margin:0 0 .4em; }
  .asha-split-photo { flex:1 1 380px; min-height:420px; background-size:cover;
    background-position:center; }

  /* full-width figure (members) */
  .asha-figure { padding:0 7vw 6vh; margin:0; }
  .asha-figure img { width:100%; height:auto; display:block; border-radius:4px;
    border:1px solid var(--line); }
  .asha-figure figcaption { font-size:.85rem; color:var(--muted); padding-top:.8em;
    letter-spacing:.04em; }

  .asha-section { padding:8vh 7vw; background:var(--bg); }
  .asha-section--panel { background:var(--panel); }
  .asha-section--orange { background:var(--orange); }
  .asha-section--orange h2, .asha-section--orange p { color:#171109 !important; }
  .asha-section h2 { font-size:clamp(2rem,3.6vw,3rem); margin:0 0 1.6rem; }
  .asha-wrap { max-width:1120px; margin:0 auto; }

  .asha-row { display:flex; gap:4rem; align-items:center; flex-wrap:wrap; }
  .asha-row--flip { flex-direction:row-reverse; }
  .asha-row > * { flex:1 1 380px; min-width:300px; }
  .asha-row img { width:100%; height:auto; display:block; border-radius:4px;
    border:1px solid var(--line); transition:transform .35s ease; }
  .asha-row img:hover { transform:scale(1.015); }
  .asha-row p { line-height:1.75; color:var(--muted); margin:0 0 1em; }
  .asha-row p strong { color:var(--cream); }

  .asha-list { border-top:1px solid var(--line); }
  .asha-item { display:flex; gap:2.2rem; padding:2rem 0; border-bottom:1px solid var(--line);
    align-items:baseline; transition:background .2s ease; }
  .asha-item:hover { background:rgba(242,123,33,.05); }
  .asha-item .num { flex:0 0 3.2rem; font-size:1.9rem; color:var(--orange); }
  .asha-item h3 { font-size:1.45rem; margin:0 0 .35em; }
  .asha-item p { margin:0; line-height:1.7; color:var(--muted); max-width:640px; }

  .asha-stats { display:flex; flex-wrap:wrap; gap:2rem; }
  .asha-stat { flex:1 1 180px; border-left:2px solid var(--orange); padding-left:1.4rem; }
  .asha-stat b { display:block; font-family:'Jaini Purva',serif; font-weight:400;
    font-size:2.6rem; line-height:1.1; }
  .asha-stat span { font-size:.85rem; letter-spacing:.14em; text-transform:uppercase;
    color:var(--muted); }

  /* member directory */
  .asha-people { display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr));
    gap:1.5rem; }
  .asha-person { border:1px solid var(--line); border-radius:4px; padding:1.6rem;
    background:var(--panel); display:flex; flex-direction:column; gap:.4rem;
    transition:border-color .2s ease, transform .2s ease; }
  .asha-person:hover { border-color:var(--orange); transform:translateY(-3px); }
  .asha-person .init { width:52px; height:52px; border-radius:4px; background:var(--orange);
    color:#171109; display:flex; align-items:center; justify-content:center;
    font-weight:700; font-size:1.15rem; margin-bottom:.6rem; }
  .asha-person h3 { font-size:1.25rem; margin:0; }
  .asha-person .role { font-size:.78rem; letter-spacing:.12em; text-transform:uppercase;
    color:var(--orange); }
  .asha-person .likes { font-size:.9rem; color:var(--muted); line-height:1.5; flex:1; }
  .asha-person .links { display:flex; gap:1.2em; padding-top:.7rem; }
  .asha-person .links a { font-size:.85rem; color:var(--cream); text-decoration:none;
    border-bottom:1px solid var(--orange); padding-bottom:2px; transition:color .2s; }
  .asha-person .links a:hover { color:var(--orange); }

  .asha-board { max-width:640px; margin:0 auto; border:1px solid var(--line);
    border-radius:4px; overflow:hidden; }
  .asha-board-row { display:flex; justify-content:space-between; align-items:center;
    padding:1.1rem 1.6rem; border-bottom:1px solid var(--line); background:var(--panel);
    transition:background .2s ease; }
  .asha-board-row:last-child { border-bottom:none; }
  .asha-board-row:hover { background:rgba(242,123,33,.08); }
  .asha-board-row .rank { color:var(--orange); font-family:'Jaini Purva',serif;
    font-size:1.3rem; width:2.4rem; }
  .asha-board-row .who { flex:1; color:var(--muted); letter-spacing:.04em; }
  .asha-board-row .amt { font-weight:700; }

  /* footer, rebuilt flat and evenly spaced */
  .asha-footer { background:#0c0805; border-top:1px solid var(--line);
    padding:4.5rem 7vw 3.5rem; display:flex; flex-direction:column;
    align-items:center; gap:1.4rem; text-align:center; color:var(--muted); }
  .asha-footer img { width:150px; height:auto; }
  .asha-footer-nav { display:flex; gap:2.2rem; flex-wrap:wrap; justify-content:center; }
  .asha-footer-nav a { color:var(--cream); text-decoration:none; font-size:.95rem;
    letter-spacing:.06em; padding-bottom:3px;
    border-bottom:1px solid var(--orange); transition:color .2s; }
  .asha-footer-nav a:hover { color:var(--orange); }
  .asha-footer p { margin:0; font-size:.9rem; }
  .asha-footer a { color:var(--orange); }
  .asha-footer .fineprint { font-size:.78rem; opacity:.7; }

  .asha-prose { max-width:680px; line-height:1.8; color:var(--muted); }
  .asha-prose strong { color:var(--cream); }
  .asha-prose a { color:var(--orange); }
  .asha-note { font-size:.85rem; color:var(--muted); letter-spacing:.04em; }

  /* footer logo: the template's image block is huge, rein it in and center it */
  #footer-sections .sqs-block-image .sqs-block-content { display:flex; justify-content:center; }
  #footer-sections .sqs-block-image img { max-width:190px !important; width:100% !important;
    height:auto !important; margin:0 auto !important; display:block; }
  #footer-sections .sqs-block-image .content-fit { max-width:190px !important; margin:0 auto; }

  /* mobile */
  @media (max-width:760px) {
    .asha-hero { padding:12vh 6vw 6vh; min-height:76vh; align-items:center; }
    .asha-hero h1 { font-size:clamp(2.4rem,11vw,3.2rem); }
    .asha-statement { padding:13vh 6vw 4vh; }
    .asha-statement h1 { font-size:clamp(1.9rem,8vw,2.6rem); }
    .asha-pagehead { padding:12vh 6vw 3vh; }
    .asha-section { padding:7vh 6vw; }
    .asha-figure { padding:0 6vw 5vh; }
    .asha-row { gap:2rem; }
    .asha-split-text { padding:12vh 6vw 6vh; }
    .asha-split-photo { min-height:300px; flex-basis:100%; }
    .asha-item { gap:1.1rem; padding:1.5rem 0; flex-wrap:wrap; }
    .asha-item .num { flex:0 0 2.2rem; font-size:1.5rem; }
    .asha-item p { max-width:100%; }
    .asha-ctas { gap:.8em; }
    .asha-btn { padding:.85em 1.6em; font-size:.95rem; }
    .asha-stats { gap:1.4rem; }
    .asha-stat b { font-size:2rem; }
    .asha-board-row { padding:.9rem 1rem; }
    .asha-board-row .who { font-size:.9rem; }
    .proj-loc { display:block; margin:.3em 0 .5em; } }
  @media (prefers-reduced-motion:reduce) {
    .asha * { transition:none !important; } }

  /* projects page */
  .proj-loc { font-size:.78rem; letter-spacing:.16em; text-transform:uppercase;
    color:var(--orange); }
  .proj-link { font-size:.9rem; color:var(--cream); text-decoration:none;
    border-bottom:1px solid var(--orange); padding-bottom:2px; transition:color .2s; }
  .proj-link:hover { color:var(--orange); }
</style>'''


# ------------------------------------------------------------- page mains ---
MAINS = {}

# HOME: short. Photo hero, one stat strip, one orange band. Done.
MAINS["index"] = '''<section class="asha-hero" style="background-image:url(assets/photo-kurta.jpg); background-position:center 35%;">
  <div class="shade"></div>
  <div class="asha-hero-inner">
    <span class="asha-kicker">Asha for Education, UC Berkeley</span>
    <h1>Hope, one <em>classroom</em> at a time.</h1>
    <p class="asha-sub">We're Berkeley students raising money so kids in India can
    stay in school. Asha means hope. We've been at it since 1991.</p>
    <div class="asha-ctas">
      <a class="asha-btn" href="donations.html">Donate</a>
      <a class="asha-btn asha-btn--ghost" href="join.html">Join us</a>
    </div>
  </div>
</section>
<section class="asha-section asha-section--panel"><div class="asha-wrap">
  <div class="asha-stats">
    <div class="asha-stat"><b>1991</b><span>Founded at Berkeley</span></div>
    <div class="asha-stat"><b>100%</b><span>Volunteer run</span></div>
    <div class="asha-stat"><b>$0</b><span>Taken as overhead</span></div>
  </div>
</div></section>
<section class="asha-section asha-section--orange"><div class="asha-wrap">
  <div class="asha-row">
    <div>
      <h2>A little from you goes a long way there.</h2>
      <p>School supplies, a teacher's stipend, a scholarship that keeps a girl in
      class. That's what your donation turns into.</p>
    </div>
    <div style="flex:0 1 auto;">
      <a class="asha-btn" style="background:#171109; border-color:#171109; color:#f4e9d7 !important;"
         href="donations.html">Give today</a>
    </div>
  </div>
</div></section>'''

# ABOUT: photo hero (board photo), statement-style heading over it.
MAINS["about"] = '''<section class="asha-hero" style="background-image:url(assets/photo-board.jpg); background-position:center 30%;">
  <div class="shade"></div>
  <div class="asha-hero-inner" style="max-width:940px;">
    <span class="asha-kicker">About us</span>
    <h1 style="font-size:clamp(2.4rem,4.8vw,3.9rem); line-height:1.1;">Asha means hope.
    The plan since 1991: find people doing honest work for kids in India, fund them,
    and <em>stay out of the way</em>.</h1>
  </div>
</section>
<section class="asha-section"><div class="asha-wrap">
  <div class="asha-row asha-row--flip">
    <div>
      <h2>Where we come from</h2>
      <p>In 1991, a few Berkeley students asked what they could do from here for
      children in India who never get a fair shot at school. The answer became Asha,
      and it grew into chapters around the world.</p>
      <p>Three decades later we're still students and still volunteers. Everything
      we raise goes to classrooms in India.</p>
    </div>
    <img src="assets/photo-leads.jpg" alt="Asha Berkeley officers in front of Doe Library" loading="lazy"/>
  </div>
</div></section>
<section class="asha-section asha-section--panel"><div class="asha-wrap">
  <h2>What we hold ourselves to</h2>
  <div class="asha-list">
    <div class="asha-item"><span class="num">01</span><div>
      <h3>Secular and non-political</h3>
      <p>Education is for every child. We work with projects regardless of religion,
      caste, or politics.</p></div></div>
    <div class="asha-item"><span class="num">02</span><div>
      <h3>Volunteer run</h3>
      <p>No salaries and no office. Students do the work, so donations go to
      children instead of overhead.</p></div></div>
    <div class="asha-item"><span class="num">03</span><div>
      <h3>Transparent</h3>
      <p>Every project is reviewed and voted on by the chapter. Funded projects
      report back, and our books are open.</p></div></div>
  </div>
</div></section>
<section class="asha-section"><div class="asha-wrap">
  <div class="asha-row">
    <div>
      <h2>How a project gets funded</h2>
      <p><strong>A project applies.</strong> Grassroots NGOs working on education in
      India send us a proposal and a budget.</p>
      <p><strong>We dig in.</strong> Volunteers study it, talk with the people
      running it, and when we can, visit in person.</p>
      <p><strong>The chapter votes.</strong> Funding decisions happen at general
      meetings. Every member gets a voice.</p>
      <p><strong>We follow through.</strong> Projects report progress, and the ones
      that deliver for kids keep our support.</p>
    </div>
    <img src="assets/photo-culture.jpg" alt="Members celebrating in traditional dress on campus" loading="lazy"/>
  </div>
</div></section>'''

# PROJECTS: the chapter's real partner projects (from berkeley.ashanet.org).
PROJECTS = [  # (name, location, description, link, photo)
    ("Rewards Trust", "Rural Tamil Nadu",
     "Strengthens government schools by placing trained teachers in them and "
     "keeping those teachers growing. Close to 8,000 students across 25 villages.",
     "http://ashanet.org/project/?pid=590", "proj-rewards.jpg"),
    ("Sakhi", "Mumbai, Maharashtra",
     "An after-school learning program for girls in Mumbai's slums, founded in "
     "2008 by Aarti Naik. Run by Sakhi for Girls Education.",
     "http://sakhiforgirlseducation.org/", "proj-sakhi.jpg"),
    ("Mera Sahara", "Noida, Uttar Pradesh",
     "A day shelter and education center for children of migrant laborers, "
     "preparing them for government school and vocational paths. Run by the "
     "Joint Women's Programme.",
     "http://ashanet.org/project/?pid=1068", "proj-mera.jpg"),
    ("Jamghat", "Old Delhi",
     "Shelters for street children across three facilities. Our chapter funds the "
     "education of 15 residents at the boys' shelter.",
     "http://ashanet.org/project/?pid=1082", "proj-jamghat.jpg"),
    ("Avantika Vidhya Bhavan", "Madhya Pradesh",
     "A K-12 school run by the Arpan Society serving about 430 children from 13 "
     "villages, with meals and transportation included.",
     "http://ashanet.org/project/?pid=872", "proj-avantika.jpg"),
    ("Little Stars", "Varanasi, Uttar Pradesh",
     "A free school educating more than 600 children from pre-K through 10th "
     "grade, the only one of its kind serving poor families in its area.",
     "http://ashanet.org/project/?pid=98", "proj-littlestars.jpg"),
    ("Tihar", "Delhi",
     "An education program inside the Tihar Jail complex, run with the Samarpan "
     "Foundation and aimed at rehabilitation and family support. Funded since 2015.",
     "http://ashanet.org/project/?pid=1213", "proj-tihar.jpg"),
]
_proj_rows = "\n".join(f'''  <div class="asha-row{' asha-row--flip' if i % 2 else ''}" style="margin-bottom:6rem;">
    <img src="assets/{photo}" alt="Children at {n}" loading="lazy"/>
    <div>
      <span class="num" style="font-size:1.6rem; color:var(--orange);">{i+1:02d}</span>
      <h3 style="font-size:clamp(1.6rem,2.6vw,2.2rem); margin:.3em 0 .4em;">{n}</h3>
      <span class="proj-loc">{loc}</span>
      <p style="margin-top:1em;">{desc}</p>
      <p style="margin-top:1.2em;"><a class="proj-link" href="{url}" target="_blank" rel="noopener">Learn more</a></p>
    </div>
  </div>''' for i, (n, loc, desc, url, photo) in enumerate(PROJECTS))

MAINS["projects"] = f'''<section class="asha-pagehead">
  <span class="asha-kicker">Our projects</span>
  <h1>Seven projects. One goal.</h1>
  <p>These are the real places your money goes. Each one was read, questioned, and
  voted on by students in this chapter.</p>
</section>
<section class="asha-section"><div class="asha-wrap">
{_proj_rows}
  <p style="text-align:center;"><a class="asha-btn" href="donations.html">Support a project</a></p>
</div></section>'''

# MEMBERS: figure first, then the Airtable directory (leadership grid removed;
# the Airtable is the member directory now). MEMBERS list kept above for reference.
MAINS["members"] = f'''<section class="asha-pagehead asha-pagehead--snug">
  <span class="asha-kicker">Our team</span>
  <h1>The people behind the hope.</h1>
</section>
<figure class="asha-figure">
  <img src="assets/photo-team.jpg" alt="The Asha Berkeley team on the steps of Doe Library"/>
  <figcaption>The chapter on the steps of Doe Library, UC Berkeley.</figcaption>
</figure>
<section class="asha-section" style="padding-left:2vw; padding-right:2vw; background:#000;">
  <div class="asha-wrap">
    <h2>Meet us over coffee</h2>
    <p class="asha-prose" style="margin-bottom:2rem;">Every one of us is a volunteer.
    Browse the table, pick a person, and book a chat.</p>
  </div>
  <iframe class="airtable-embed" title="Asha Berkeley coffee chats"
    src="{AIRTABLE_EMBED}"
    frameborder="0" width="100%" height="1100"
    style="background:transparent; border:1px solid var(--line); border-radius:4px; display:block;"></iframe>
  <p class="asha-note" style="margin-top:1rem; text-align:center;">Table not loading?
  <a href="{AIRTABLE}" target="_blank" rel="noopener">Open it on Airtable</a>.</p>
</section>
<section class="asha-section"><div class="asha-wrap">
  <div class="asha-row">
    <div>
      <h2>Want your name here?</h2>
      <p class="asha-prose">Any major, any year, no experience needed. Come to a
      meeting and see if it feels right.</p>
    </div>
    <div style="flex:0 1 auto;">
      <a class="asha-btn" href="join.html">Join Asha Berkeley</a>
    </div>
  </div>
</div></section>'''

# JOIN: split-screen opening + coffee chat CTA with the Airtable link.
MAINS["join"] = f'''<section class="asha-split">
  <div class="asha-split-text">
    <span class="asha-kicker">Get involved</span>
    <h1>Do something <em>real</em> with your semester.</h1>
    <p class="asha-sub">Help decide which projects get funded, run fundraisers that
    matter, and meet people worth keeping.</p>
    <div class="asha-ctas">
      <a class="asha-btn" href="{AIRTABLE}" target="_blank" rel="noopener">Sign up for a coffee chat</a>
      <a class="asha-btn asha-btn--ghost" href="mailto:{EMAIL}?subject=Joining%20Asha%20Berkeley">Email us</a>
    </div>
  </div>
  <div class="asha-split-photo" style="background-image:url(assets/photo-social.jpg);"></div>
</section>
<section class="asha-section"><div class="asha-wrap">
  <h2>Start with a coffee chat</h2>
  <p class="asha-prose">The easiest way to figure out if Asha is for you is to talk
  to someone in it. Pick a time on our
  <a href="{AIRTABLE}" target="_blank" rel="noopener">coffee chat Airtable</a>,
  or book directly with anyone on the <a href="members.html">members page</a>.
  No prep needed. Come with questions.</p>
</div></section>
<section class="asha-section asha-section--panel"><div class="asha-wrap">
  <h2>How joining works</h2>
  <div class="asha-list">
    <div class="asha-item"><span class="num">1</span><div>
      <h3>Grab a coffee chat</h3>
      <p>Meet a current member, hear the honest version of what we do, and ask
      anything.</p></div></div>
    <div class="asha-item"><span class="num">2</span><div>
      <h3>Come to a general meeting</h3>
      <p>No application pressure and no experience needed. Times are posted each
      semester. <!-- TODO: add meeting time and location --></p></div></div>
    <div class="asha-item"><span class="num">3</span><div>
      <h3>Pick your team</h3>
      <p>Projects, events, publicity, finance, or Team Asha. Find the corner that
      fits you and make it count.</p></div></div>
  </div>
  <p class="asha-prose" style="margin-top:2.5rem;">Questions? Write to
  <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</div></section>'''

# DONATIONS: flat centered opening + static board.
_board = [("1", "$500"), ("2", "$250"), ("3", "$100"), ("4", "$75"), ("5", "$50"),
          ("6", "$40"), ("7", "$25"), ("8", "$20")]
_board_html = "\n".join(
    f'''    <div class="asha-board-row"><span class="rank">{r}</span>
      <span class="who">Template Donation</span><span class="amt">{a}</span></div>'''
    for r, a in _board)

MAINS["donations"] = f'''<section class="asha-pagehead">
  <span class="asha-kicker">Donations</span>
  <h1>Keep a kid <em>in school</em>.</h1>
  <p style="margin:0 auto;">Your donation funds classrooms, scholarships, and
  teachers for underserved children in India. We take nothing off the top.</p>
  <div class="asha-ctas" style="justify-content:center; margin-top:2.2rem;">
    <a class="asha-btn" href="{VENMO}" target="_blank" rel="noopener">Donate on Venmo</a>
    <span class="asha-note">Venmo @ashaberkeley</span>
  </div>
</section>
<section class="asha-section asha-section--panel"><div class="asha-wrap">
  <h2 style="text-align:center;">Top donations</h2>
  <p class="asha-note" style="text-align:center; margin-bottom:2.5rem;">Placeholder
  entries until real donations are wired up.</p>
  <div class="asha-board">
{_board_html}
  </div>
</div></section>
<section class="asha-section"><div class="asha-wrap">
  <h2>Ways to give</h2>
  <div class="asha-list">
    <div class="asha-item"><span class="num">01</span><div>
      <h3>One-time gift</h3>
      <p>Any amount helps. A single donation buys school supplies, funds a
      scholarship, or supports a partner project.</p></div></div>
    <div class="asha-item"><span class="num">02</span><div>
      <h3>Monthly giving</h3>
      <p>Recurring gifts let us commit to long-term programs and plan ahead with
      confidence.</p></div></div>
    <div class="asha-item"><span class="num">03</span><div>
      <h3>Corporate matching</h3>
      <p>Many employers match charitable donations. Ask your HR team, or reach out
      and we'll help with the paperwork.</p></div></div>
  </div>
  <p class="asha-prose" style="margin-top:2.5rem;">Questions about donating,
  sponsorships, or in-kind gifts? Write to <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</div></section>'''

TITLES = {
    "index": ("Asha Berkeley", None),
    "about": ("About | Asha Berkeley", "about.html"),
    "projects": ("Projects | Asha Berkeley", "projects.html"),
    "members": ("Members | Asha Berkeley", "members.html"),
    "join": ("Join | Asha Berkeley", "join.html"),
    "donations": ("Donations | Asha Berkeley", "donations.html"),
}

for name, main_html in MAINS.items():
    assert "—" not in main_html and "&mdash;" not in main_html, f"em dash in {name}"
    title, active = TITLES[name]
    page = head + '<main id="page" class="container" role="main">\n' + ASHA_CSS + \
        '\n<div class="asha">\n' + main_html + '\n</div>\n</main>' + foot
    page = set_title(page, title)
    page = set_active(page, active)
    out = os.path.join(DIR, "index.html" if name == "index" else f"{name}.html")
    open(out, "w", encoding="utf-8").write(page)
    print("wrote", os.path.basename(out), len(page))

referenced = set()
for f in glob.glob(os.path.join(DIR, "*.html")) + glob.glob(os.path.join(DIR, "assets", "*.css")):
    t = open(f, encoding="utf-8", errors="replace").read()
    referenced.update(re.findall(r'(?:assets/)?([0-9a-zA-Z_-]+\.(?:jpg|jpeg|png|gif|webp|ico|svg))', t))
removed = 0
for f in glob.glob(os.path.join(DIR, "assets", "*")):
    b = os.path.basename(f)
    if b.rsplit(".", 1)[-1].lower() in ("jpg", "jpeg", "png", "gif", "webp") and b not in referenced:
        os.remove(f)
        removed += 1
print(f"pruned {removed} unused image files")
print("done")
