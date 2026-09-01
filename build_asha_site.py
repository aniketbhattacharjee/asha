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

# the About page IS the homepage now; point its nav/footer links at the root
head = head.replace('href="about.html"', 'href="index.html"')
foot = foot.replace('href="about.html"', 'href="index.html"')

# header uses the real Asha Berkeley logo (transparent cutout)
head = head.replace("assets/asha-logo.svg", "assets/asha-logo-real.png")


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
  <div class="asha-footer-cols">
    <div class="asha-footer-col asha-footer-col--brand">
      <a href="index.html"><img src="assets/asha-logo-real.png" alt="Asha Berkeley" style="border:none;"/></a>
      <p>The founding chapter of Asha for Education, a registered 501(c)(3)
      nonprofit. Secular, volunteer run, every dollar to the classroom.</p>
    </div>
    <div class="asha-footer-col">
      <h4>Pages</h4>
      <p><a href="index.html">About</a></p>
      <p><a href="projects.html">Projects</a></p>
      <p><a href="members.html">Members</a></p>
      <p><a href="join.html">Join</a></p>
      <p><a href="donations.html">Donations</a></p>
    </div>
    <div class="asha-footer-col">
      <h4>Elsewhere</h4>
      <p><a href="https://www.instagram.com/asha_berkeley/" target="_blank" rel="noopener">Instagram</a></p>
      <p><a href="https://www.facebook.com/ashaberkeley/" target="_blank" rel="noopener">Facebook</a></p>
      <p><a href="https://linktr.ee/ashaberkeley" target="_blank" rel="noopener">Linktree</a></p>
      <p><a href="https://donate.ashanet.org/?c=58" target="_blank" rel="noopener">Donate via Asha</a></p>
      <p><a href="{VENMO}" target="_blank" rel="noopener">Venmo @ashaberkeley</a></p>
      <p><a href="https://ashanet.org" target="_blank" rel="noopener">ashanet.org</a></p>
    </div>
    <div class="asha-footer-col asha-footer-col--contact">
      <h4>Contact</h4>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p>Mail: PO Box 4274,<br/>Berkeley, CA 94704-0274</p>
      <p>Checks: Asha for Education,<br/>PO Box 888080,<br/>Los Angeles, CA 90088-8080</p>
    </div>
  </div>
  <p class="fineprint">Asha for Education, UC Berkeley chapter &middot; Est. 1991</p>
</div>'''
foot = re.sub(r'(<footer[^>]*data-footer-sections[^>]*>).*?(</footer>)',
              lambda m: m.group(1) + FOOTER_HTML + m.group(2), foot, count=1, flags=re.S)

# strip scripts previous builds injected (chrome is self-sourced)
foot = re.sub(r"<script>\(function\(\)\{var h=document\.getElementById\('header'\).*?</script>\n?",
              "", foot, flags=re.S)
foot = re.sub(r'<script id="asha-reveal">.*?</script>\n?', "", foot, flags=re.S)
foot = re.sub(r'<script id="asha-fx"[^>]*>.*?</script>\n?', "", foot, flags=re.S)
foot = re.sub(r'<script id="asha-menu">.*?</script>\n?', "", foot, flags=re.S)
foot = re.sub(r'<script src="https://cdn\.jsdelivr\.net/npm/animejs[^"]*"></script>\n?', "", foot)

# scroll-reveal: rows, list items, and figures ease in as they enter the viewport
REVEAL_JS = '''<script id="asha-reveal">(function(){
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
if (location.pathname.indexOf('join') !== -1) return;
var els = document.querySelectorAll('.asha-row, .asha-item, .asha-figure, .asha-stat, .asha-embed-frame');
if (!('IntersectionObserver' in window)) return;
var io = new IntersectionObserver(function(entries){
  entries.forEach(function(e){
    if (e.isIntersecting) { e.target.classList.add('asha-in'); io.unobserve(e.target); }
  });
}, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
els.forEach(function(el, i){
  el.classList.add('asha-reveal');
  el.style.transitionDelay = Math.min((i % 4) * 70, 210) + 'ms';
  io.observe(el);
});
})();</script>'''
foot = foot.replace("</body>", REVEAL_JS + "\n</body>")

# our own burger toggle: replaces the buttons (dropping any template listeners)
MENU_JS = '''<script id="asha-menu">(function(){
document.querySelectorAll('.header-burger-btn').forEach(function(btn){
  var b = btn.cloneNode(true);
  btn.parentNode.replaceChild(b, btn);
  b.addEventListener('click', function(ev){
    ev.preventDefault(); ev.stopPropagation();
    document.body.classList.toggle('asha-menu-open');
  });
});
document.querySelectorAll('.header-menu a').forEach(function(a){
  a.addEventListener('click', function(){
    document.body.classList.remove('asha-menu-open');
  });
});
})();</script>'''
foot = foot.replace("</body>", MENU_JS + "\n</body>")

# anime.js hero entrance + MagicUI-style number tickers on stats
FX_JS = '''<script src="https://cdn.jsdelivr.net/npm/animejs@3.2.2/lib/anime.min.js"></script>
<script id="asha-fx">(function(){
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !window.anime) return;
var fmt = function(n){ return n.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, ','); };
var tick = new IntersectionObserver(function(entries){
  entries.forEach(function(e){
    if (!e.isIntersecting) return;
    tick.unobserve(e.target);
    var raw = e.target.textContent.trim();
    var m = raw.match(/^([^0-9]*)([0-9][0-9,]*)(.*)$/);
    if (!m) return;
    var target = parseInt(m[2].replace(/,/g, ''), 10);
    var obj = { v: 0 };
    anime({ targets: obj, v: target, round: 1, duration: 1400, easing: 'easeOutExpo',
      update: function(){ e.target.textContent = m[1] + fmt(obj.v) + m[3]; } });
  });
}, { threshold: 0.6 });
document.querySelectorAll('.asha-stat b').forEach(function(el){ tick.observe(el); });
})();</script>'''
foot = foot.replace("</body>", FX_JS + "\n</body>")

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

  /* small logo tucked hard into the top-left corner (links home) */
  #header .header-inner { padding-top:10px !important; padding-bottom:10px !important;
    padding-left:14px !important; }
  #header .header-title-logo img, #header .header-mobile-logo img {
    max-height:34px !important; width:auto !important; }
  /* backing pill so the logo stays legible over any content while scrolling */
  #header .header-title-logo a, #header .header-mobile-logo a {
    display:inline-block; background:rgba(12,8,5,.78); padding:6px 10px;
    border-radius:10px; line-height:0; }

  /* header text: own colors (theme went black on transparent bg) + theme font */
  #header .header-inner, #header .header-inner * { opacity:1 !important;
    visibility:visible !important; }
  #header .header-nav-item a { color:#f4e9d7 !important;
    font-family:'Jaini Purva',serif !important; font-size:1.25rem;
    letter-spacing:.05em; }
  #header .header-title-logo a, #header .header-mobile-logo a { color:#f4e9d7 !important; }
  #header .burger-inner > div { background-color:#f4e9d7 !important; }
  .header-menu-nav-item a { font-family:'Jaini Purva',serif !important; }

  /* mobile menu overlay: self-contained, no dependence on template JS */
  #header .header-burger { display:none; }
  #header .header-burger-btn { cursor:pointer; padding:12px; background:none;
    border:none; }
  #header .burger-box { width:26px; height:18px; position:relative; display:block; }
  #header .burger-inner > div { position:absolute; left:0; right:0; height:2px !important;
    background-color:#f4e9d7 !important; transition:transform .25s ease, opacity .2s ease; }
  #header .top-bun { top:0; } #header .patty { top:8px; } #header .bottom-bun { top:16px; }
  body.asha-menu-open #header .top-bun { transform:translateY(8px) rotate(45deg); }
  body.asha-menu-open #header .patty { opacity:0; }
  body.asha-menu-open #header .bottom-bun { transform:translateY(-8px) rotate(-45deg); }

  .header-menu { position:fixed !important; inset:0 !important; z-index:900 !important;
    background:#0f0b07 !important; opacity:0 !important; visibility:hidden !important;
    pointer-events:none !important; transform:none !important;
    transition:opacity .25s ease !important; overflow-y:auto !important;
    display:flex !important; align-items:center !important; justify-content:center !important; }
  body.asha-menu-open .header-menu { opacity:1 !important; visibility:visible !important;
    pointer-events:auto !important; }
  body.asha-menu-open { overflow:hidden; }
  .header-menu .header-menu-bg { background:#0f0b07 !important; }
  .header-menu-nav-item a { color:#f4e9d7 !important; font-size:2rem !important;
    display:block; padding:.55em 0; text-align:center; text-decoration:none; }
  .header-menu-nav-item a:hover,
  .header-menu-nav-item--active a { color:#f27b21 !important; }
  .header-menu-nav-folder { position:static !important; transform:none !important; }
  .header-menu-controls { display:none !important; }

  @media (max-width:799px), (pointer:coarse) and (max-width:1024px) {
    #header .header-burger { display:flex; }
    #header .header-nav { display:none; } }

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
  /* MagicUI-style shimmer on primary buttons */
  .asha-btn { position:relative; overflow:hidden; }
  .asha-btn::after { content:""; position:absolute; top:0; bottom:0; width:44%;
    left:-60%; background:linear-gradient(105deg, transparent 20%,
    rgba(255,255,255,.38) 50%, transparent 80%);
    animation:asha-shimmer 3.4s ease-in-out infinite; }
  .asha-btn--ghost::after { display:none; }
  @keyframes asha-shimmer { 0%, 55% { left:-60%; } 90%, 100% { left:120%; } }
  @media (prefers-reduced-motion:reduce) { .asha-btn::after { animation:none; display:none; } }
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

  /* footer: full contact info in columns (colors forced; the template theme
     paints footer text black otherwise) */
  .asha-footer { background:#0c0805; border-top:1px solid var(--line);
    padding:4.5rem 7vw 3rem; color:#c9b89e !important; }
  .asha-footer p, .asha-footer span { color:#c9b89e !important; }
  .asha-footer h4 { color:#f4e9d7 !important; }
  .asha-footer a { color:#f4e9d7 !important; }
  .asha-footer a:hover { color:#f27b21 !important; }
  .asha-footer-cols { display:flex; flex-wrap:wrap; gap:3.5rem 7rem;
    max-width:1360px; margin:0 auto 3rem; align-items:center;
    justify-content:space-between; }
  .asha-footer-col { flex:1 1 210px; min-width:200px; }
  .asha-footer-col--brand { flex:1.5 1 300px; }
  .asha-footer-col--brand img { width:260px; max-width:100%; height:auto;
    margin-bottom:1.2rem; }
  .asha-footer-col--contact { margin-left:auto; text-align:right;
    align-self:flex-end; }
  .asha-footer-col img { height:auto; margin-bottom:1rem; }
  .asha-footer-col h4 { font-family:'Jaini Purva',serif !important;
    font-weight:400 !important; font-size:1.5rem; color:var(--cream);
    margin:0 0 1rem; }
  .asha-footer-col p { margin:0 0 .85rem; font-size:1.02rem; line-height:1.7; }
  .asha-footer-col a { color:var(--cream); text-decoration:none;
    border-bottom:1px solid var(--orange); padding-bottom:2px; transition:color .2s; }
  .asha-footer-col a:hover { color:var(--orange); }
  .asha-footer .fineprint { font-size:.88rem; opacity:.75; text-align:center;
    margin:0; padding-top:2rem; border-top:1px solid var(--line); }

  /* scroll-reveal (added by JS; without JS everything stays visible) */
  .asha-reveal { opacity:0; transform:translateY(26px);
    transition:opacity .6s ease, transform .6s ease; }
  .asha-reveal.asha-in { opacity:1; transform:none; }
  @media (prefers-reduced-motion:reduce) {
    .asha-reveal { opacity:1 !important; transform:none !important; } }

  /* airtable embed: framed and dimmed so it sits with the dark theme */
  .asha-embed-frame { border:1px solid var(--line); border-radius:10px;
    padding:10px; background:#171109; }
  .asha-embed-frame iframe { display:block; width:100%; height:1066px;
    border:none; border-radius:6px;
    filter:brightness(.88) contrast(.97) saturate(.95); }

  /* FAQ accordion */
  .asha-faq { border-bottom:1px solid var(--line); }
  .asha-faq summary { cursor:pointer; list-style:none; display:flex;
    justify-content:space-between; align-items:center; gap:1.5rem;
    padding:1.5rem 0; font-size:1.15rem; color:var(--cream);
    transition:color .2s ease; }
  .asha-faq summary::-webkit-details-marker { display:none; }
  .asha-faq summary::after { content:"+"; font-family:'Jaini Purva',serif;
    font-size:1.6rem; color:var(--orange); transition:transform .25s ease; }
  .asha-faq[open] summary::after { transform:rotate(45deg); }
  .asha-faq summary:hover { color:var(--orange); }
  .asha-faq p { margin:0 0 1.5rem; line-height:1.75; color:var(--muted);
    max-width:720px; }
  .asha-faq a { color:var(--orange); }

  /* compact recruitment timeline */
  .rt-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(215px,1fr));
    gap:1.2rem; }
  .rt-card { border:1px solid var(--line); border-radius:10px; padding:1.4rem 1.4rem 1.5rem;
    background:var(--panel); transition:border-color .25s ease; }
  .rt-card:hover { border-color:var(--orange); }
  .rt-date { display:inline-block; font-size:.74rem; letter-spacing:.14em;
    text-transform:uppercase; color:var(--orange); border:1px solid rgba(242,123,33,.45);
    border-radius:999px; padding:.3em .9em; margin-bottom:.8rem; }
  .rt-card h3 { font-size:1.25rem; margin:0 0 .4rem; }
  .rt-card p { margin:0; font-size:.9rem; line-height:1.6; color:var(--muted); }
  .rt-card a { color:var(--orange); }

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
    #header .header-title-logo img, #header .header-mobile-logo img {
      max-height:42px !important; width:auto !important; }
    .asha-hero { padding:12vh 6vw 6vh; min-height:76vh; align-items:center; }
    .asha-hero h1 { font-size:clamp(2.2rem,10vw,3rem) !important; }
    .asha-sub { font-size:1rem; }
    .asha-statement { padding:13vh 6vw 4vh; }
    .asha-statement h1 { font-size:clamp(1.9rem,8vw,2.6rem); }
    .asha-pagehead { padding:12vh 6vw 3vh; min-height:0; }
    .asha-pagehead h1 { font-size:clamp(2rem,9vw,2.6rem); }
    .asha-section { padding:6vh 6vw; }
    .asha-figure { padding:0 6vw 5vh; }
    .asha-row { gap:2rem; }
    .asha-split { min-height:0; }
    .asha-split-text { padding:14vh 6vw 6vh; }
    .asha-split-text h1 { font-size:clamp(2rem,9vw,2.6rem); }
    .asha-split-photo { min-height:280px; flex-basis:100%; }
    .asha-item { gap:1.1rem; padding:1.5rem 0; flex-wrap:wrap; }
    .asha-item .num { flex:0 0 2.2rem; font-size:1.5rem; }
    .asha-item p { max-width:100%; }
    .asha-ctas { gap:.8em; }
    .asha-btn { padding:.85em 1.6em; font-size:.95rem; }
    .asha-stats { gap:1.4rem; }
    .asha-stat b { font-size:1.9rem; }
    .asha-stat { flex:1 1 40%; padding-left:1rem; }
    .asha-board-row { padding:.9rem 1rem; }
    .asha-board-row .who { font-size:.9rem; }
    .proj-grid { grid-template-columns:1fr; gap:1.4rem; }
    .proj-card h3 { font-size:1.35rem; }
    .rt-grid { grid-template-columns:1fr 1fr; gap:.9rem; }
    .rt-card { padding:1.1rem; }
    .rt-card h3 { font-size:1.05rem; }
    .rt-card p { font-size:.82rem; }
    .asha-faq summary { font-size:1rem; padding:1.2rem 0; }
    .asha-embed-frame iframe { height:70vh; min-height:480px; }
    .asha-footer { padding:3.5rem 6vw 2.5rem; }
    .asha-footer-cols { gap:2.5rem 2rem; }
    .asha-footer-col--brand img { width:200px; }
    .asha-footer-col p { font-size:.95rem; }
    .asha-footer-col--contact { margin-left:0; text-align:left; align-self:auto; }
    .proj-loc { display:block; margin:.3em 0 .5em; } }
  @media (max-width:430px) {
    .rt-grid { grid-template-columns:1fr; } }
  @media (prefers-reduced-motion:reduce) {
    .asha * { transition:none !important; } }

  /* projects gallery */
  .proj-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr));
    gap:2rem; }
  .proj-card { border:1px solid var(--line); border-radius:12px; overflow:hidden;
    background:var(--panel); display:flex; flex-direction:column;
    transition:border-color .3s ease, box-shadow .3s ease; }
  .proj-card:hover { border-color:var(--orange);
    box-shadow:0 16px 46px rgba(0,0,0,.4); }
  .proj-card img { width:100%; aspect-ratio:3/2; object-fit:cover; display:block; }
  .proj-card-body { padding:1.6rem 1.7rem 1.8rem; display:flex;
    flex-direction:column; gap:.45rem; flex:1; }
  .proj-card h3 { font-size:1.5rem; margin:0; }
  .proj-card .proj-meta { font-size:.78rem; letter-spacing:.08em;
    text-transform:uppercase; color:rgba(244,233,215,.55); }
  .proj-card p.desc { margin:.4rem 0 0; line-height:1.65; color:var(--muted);
    font-size:.95rem; flex:1; }
  .proj-loc { font-size:.78rem; letter-spacing:.16em; text-transform:uppercase;
    color:var(--orange); }
  .proj-link { font-size:.9rem; color:var(--cream); text-decoration:none;
    border-bottom:1px solid var(--orange); padding-bottom:2px; transition:color .2s; }
  .proj-link:hover { color:var(--orange); }
</style>'''


# ------------------------------------------------------------- page mains ---
MAINS = {}

# HOME = ABOUT: the about page is the landing page now (old home removed).
MAINS["index"] = '''<section class="asha-hero" style="background-image:url(assets/photo-kurta.jpg); background-position:center 35%;">
  <div class="shade"></div>
  <div class="asha-hero-inner" style="max-width:940px;">
    <span class="asha-kicker">Asha for Education, UC Berkeley</span>
    <h1 style="font-size:clamp(2.4rem,4.8vw,3.9rem); line-height:1.1;">Asha means hope.
    The plan since 1991: find people doing honest work for kids in India, fund them,
    and <em>stay connected the whole way</em>.</h1>
    <div class="asha-ctas" style="margin-top:1.6em;">
      <a class="asha-btn" href="donations.html">Donate</a>
      <a class="asha-btn asha-btn--ghost" href="join.html">Join us</a>
    </div>
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
      <p><strong>We follow through.</strong> Funded projects send us progress
      reports, and we keep funding the ones that are working.</p>
    </div>
    <img src="assets/photo-culture.jpg" alt="Members celebrating in traditional dress on campus" loading="lazy"/>
  </div>
</div></section>
<section class="asha-section asha-section--orange"><div class="asha-wrap">
  <div class="asha-row">
    <div>
      <h2>Your money goes further than you'd think.</h2>
      <p>Donations pay for things like school supplies, teachers' stipends, and
      scholarships that keep kids in class.</p>
    </div>
    <div style="flex:0 1 auto;">
      <a class="asha-btn" style="background:#171109; border-color:#171109; color:#f4e9d7 !important;"
         href="donations.html">Give today</a>
    </div>
  </div>
</div></section>'''

# PROJECTS: the chapter's real partner projects (from berkeley.ashanet.org).
PROJECTS = [  # (name, location, partner, facts, description, link, photo)
    ("Rewards Trust", "Rural Tamil Nadu", "Rewards Trust",
     "8,000 students &middot; 25 villages",
     "A volunteer-run, zero-overhead organization building a stronger government "
     "school system in rural Tamil Nadu. It places trained teachers in public "
     "schools and keeps investing in their development, so close to 8,000 "
     "students across 25 villages get consistent, quality instruction.",
     "http://ashanet.org/project/?pid=590", "proj-rewards.jpg"),
    ("Sakhi", "Mumbai, Maharashtra", "Sakhi for Girls Education",
     "Founded 2008 &middot; Girls' education",
     "Sakhi creates quality learning spaces at the community level for girls in "
     "Mumbai's slums. Founded in 2008 by Aarti Naik, it runs after-school "
     "programs that give girls a secure place to study, catch up, and stay in "
     "school past the point where most are pulled out.",
     "http://sakhiforgirlseducation.org/", "proj-sakhi.jpg"),
    ("Mera Sahara", "Noida, Uttar Pradesh", "Joint Women's Programme",
     "Day shelter &middot; School preparation",
     "An education center and day shelter for children of migrant day laborers. "
     "Kids who would otherwise spend the day on worksites get basic education, "
     "meals, and a safe place, with a path toward government school enrollment "
     "and vocational training.",
     "http://ashanet.org/project/?pid=1068", "proj-mera.jpg"),
    ("Jamghat", "Old Delhi", "Jamghat",
     "3 facilities &middot; 15 students funded by us",
     "A registered NGO creating a safe environment for street children in Old "
     "Delhi, across three facilities including overnight shelters and day "
     "programs. Our chapter directly funds the education of 15 residents at the "
     "boys' shelter.",
     "http://ashanet.org/project/?pid=1082", "proj-jamghat.jpg"),
    ("Avantika Vidhya Bhavan", "Madhya Pradesh", "Arpan Society",
     "K-12 &middot; 430 children &middot; 13 villages",
     "A full K-12 school serving about 430 children from impoverished families "
     "across 13 villages. Beyond qualified instruction, the school provides "
     "meals, transportation, and medical care, removing the everyday barriers "
     "that keep kids out of class.",
     "http://ashanet.org/project/?pid=872", "proj-avantika.jpg"),
    ("Little Stars", "Varanasi, Uttar Pradesh", "Little Stars School",
     "600+ children &middot; Pre-nursery to 10th grade",
     "A free school educating more than 600 children from pre-nursery through "
     "10th grade, funded entirely by private donations. It is the only "
     "independent quality school serving poor families in its part of Varanasi.",
     "http://ashanet.org/project/?pid=98", "proj-littlestars.jpg"),
    ("Tihar", "Delhi", "Samarpan Foundation",
     "Funded since May 2015",
     "An education program inside the Tihar Jail complex, one of the largest "
     "prison complexes in South Asia. Run with the Samarpan Foundation, it "
     "provides education to incarcerated people with rehabilitation and family "
     "support at its center. Our newest project, funded since May 2015.",
     "http://ashanet.org/project/?pid=1213", "proj-tihar.jpg"),
]
_proj_cards = "\n".join(f'''    <div class="proj-card">
      <img src="assets/{photo}" alt="Children at {n}" loading="lazy"/>
      <div class="proj-card-body">
        <h3>{n}</h3>
        <span class="proj-loc">{loc}</span>
        <span class="proj-meta">{partner} &middot; {facts}</span>
        <p class="desc">{desc}</p>
        <p style="margin:1rem 0 0;"><a class="proj-link" href="{url}" target="_blank" rel="noopener">Learn more</a></p>
      </div>
    </div>''' for i, (n, loc, partner, facts, desc, url, photo) in enumerate(PROJECTS))

MAINS["projects"] = f'''<section class="asha-pagehead asha-pagehead--snug" style="padding-bottom:3vh;">
  <span class="asha-kicker">Our projects</span>
  <h1>The projects we fund.</h1>
  <p>This is where the money goes. Students in this chapter read each partner's
  proposal, asked them hard questions, and voted before funding anything. Every
  project reports back on the children it serves.</p>
</section>
<section class="asha-section" style="padding-top:0;"><div class="asha-wrap">
  <div class="asha-stats" style="margin-bottom:3rem;">
    <div class="asha-stat"><b>7</b><span>Partner projects</span></div>
    <div class="asha-stat"><b>6</b><span>States across India</span></div>
    <div class="asha-stat"><b>9,000+</b><span>Children reached</span></div>
    <div class="asha-stat"><b>100%</b><span>Chapter voted</span></div>
  </div>
  <div class="proj-grid">
{_proj_cards}
  </div>
  <p style="text-align:center; margin-top:4rem;"><a class="asha-btn" href="donations.html">Support a project</a></p>
</div></section>'''

# MEMBERS: figure first, then the Airtable directory (leadership grid removed;
# the Airtable is the member directory now). MEMBERS list kept above for reference.
MAINS["members"] = f'''<section class="asha-pagehead asha-pagehead--snug">
  <span class="asha-kicker">Our team</span>
  <h1>Meet the chapter.</h1>
</section>
<figure class="asha-figure">
  <img src="assets/photo-team.jpg" alt="The Asha Berkeley team on the steps of Doe Library"/>
  <figcaption>The chapter on the steps of Doe Library, UC Berkeley.</figcaption>
</figure>
<section class="asha-section" style="background:#000;"><div class="asha-wrap">
  <h2 style="margin-bottom:2rem;">Meet us over coffee</h2>
  <div class="asha-embed-frame">
    <iframe class="airtable-embed" title="Asha Berkeley coffee chats"
      src="{AIRTABLE_EMBED}" frameborder="0"></iframe>
  </div>
  <p class="asha-note" style="margin-top:1rem; text-align:center;">Table not loading?
  <a href="{AIRTABLE}" target="_blank" rel="noopener">Open it on Airtable</a>.</p>
</div></section>
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

# JOIN: recruitment page modeled on the Phoenix join tab (timeline, application,
# FAQ), with Asha content. Coffee chats live on the Members page.
MAINS["join"] = f'''<section class="asha-split">
  <div class="asha-split-text">
    <span class="asha-kicker">Recruitment</span>
    <h1>We're recruiting our <em>Fall 2026</em> class.</h1>
    <p class="asha-sub">Hey there! Asha Berkeley is looking for people who care about
    getting kids in India a good education. Check out the timeline and FAQ below, then come say hi.</p>
    <div class="asha-ctas">
      <a class="asha-btn" href="https://docs.google.com/forms/d/e/1FAIpQLScJCUTwTBdaumWnkpgEn1W5iBwTvK9SCMTFJNJyN10K6cRkCA/viewform" target="_blank" rel="noopener">Apply now</a>
      <a class="asha-btn asha-btn--ghost" href="mailto:{EMAIL}?subject=Joining%20Asha%20Berkeley">Email us</a>
    </div>
  </div>
  <div class="asha-split-photo" style="background-image:url(assets/photo-social.jpg);"></div>
</section>
<section class="asha-section"><div class="asha-wrap">
  <h2>Recruitment timeline</h2>
  <p class="asha-prose" style="margin-bottom:2rem;">Exact dates, times, and rooms
  drop on our <a href="https://www.instagram.com/asha_berkeley/" target="_blank"
  rel="noopener">Instagram</a> at the start of the semester.</p>
  <div class="rt-grid">
    <div class="rt-card"><span class="rt-date">Mon 8/31</span>
      <h3>Coffee chats &amp; apps open</h3></div>
    <div class="rt-card"><span class="rt-date">Thu 9/3 &middot; 8-9 PM</span>
      <h3>Infosession 1</h3>
      <p>Dwinelle 259</p></div>
    <div class="rt-card"><span class="rt-date">Wed 9/9 &middot; 8-9 PM</span>
      <h3>Infosession 2</h3>
      <p>Dwinelle 79</p></div>
    <div class="rt-card"><span class="rt-date">Fri 9/11 &middot; 11:59 PM</span>
      <h3>Written apps due</h3></div>
    <div class="rt-card"><span class="rt-date">Sat 9/12</span>
      <h3>First round interviews</h3>
      <p>Invite only</p></div>
    <div class="rt-card"><span class="rt-date">Sun 9/13</span>
      <h3>Social night</h3>
      <p>Invite only</p></div>
  </div>
</div></section>
<section class="asha-section asha-section--panel"><div class="asha-wrap">
  <h2>What you'd actually do</h2>
  <div class="asha-cards" style="justify-content:flex-start;">
    <div class="asha-card"><h3>Evaluate real projects</h3>
      <p>Read proposals from NGOs in India, question their budgets, and vote on
      which ones we fund. You'll vote on where the chapter's money actually goes.</p></div>
    <div class="asha-card"><h3>Run fundraisers</h3>
      <p>Campus events, community drives, and Team Asha. What we raise is what our
      seven partner projects get.</p></div>
    <div class="asha-card"><h3>Build the community</h3>
      <p>Socials, retreats, big-little families. People stick around here well past
      graduation.</p></div>
  </div>
</div></section>
<section class="asha-section"><div class="asha-wrap">
  <h2>Frequently asked questions</h2>
  <div style="margin-top:2.5rem;">
    <details class="asha-faq">
      <summary>Why education in India?</summary>
      <p>Education is one of the best routes out of poverty, and India has more
      school-age kids than any other country. Small amounts of money go
      remarkably far there: a semester of fundraising here can pay teachers, buy
      books, and keep whole classrooms running. We fund people already doing that
      work well and stay connected with them through the year.</p>
    </details>
    <details class="asha-faq">
      <summary>What exactly can I expect as a member?</summary>
      <p>You join a committee (projects, events, publicity, finance, or Team Asha)
      and work with it through the semester. You read funding proposals from
      partner NGOs, help run fundraisers, and vote at general meetings on where the
      money goes. Every member gets a voice in funding decisions, including brand
      new ones.</p>
    </details>
    <details class="asha-faq">
      <summary>I'm not planning a nonprofit career. Is Asha still a good fit?</summary>
      <p>Almost none of us are. Most of us are headed into engineering, medicine,
      policy, or whatever else. Asha is the thing we do that isn't about our own
      careers. You'll get real practice reading budgets, running events, and working with
      a team, which is useful no matter what you do after Berkeley.</p>
    </details>
    <details class="asha-faq">
      <summary>What does Asha look for in applicants?</summary>
      <p>No specific major, year, or experience. We look for people who care about this work and follow through on what they
      sign up for. If you'd read a school's budget proposal carefully because kids
      depend on it, you're our kind of person.</p>
    </details>
    <details class="asha-faq">
      <summary>What's the time commitment?</summary>
      <p>A few hours a week for most members: general meetings plus your committee
      work. It ramps up around big fundraisers and project voting, and you'll know
      those weeks in advance. Many members balance Asha with heavy course loads and
      other clubs.</p>
    </details>
    <details class="asha-faq">
      <summary>What's the new member experience like?</summary>
      <p>You get a big through our big-little program and join a committee right
      away. New members vote on funding decisions in their first semester.</p>
    </details>
    <details class="asha-faq">
      <summary>How do I take my best shot at applying?</summary>
      <p>Come to an infosession and book a <a href="members.html">coffee chat</a>.
      They're the best way to see what we're about, and it helps us put a face to
      your application. Then be real in the application. We'd
      rather read why this mission matters to you than a list of titles.</p>
    </details>
  </div>
  <p class="asha-prose" style="margin-top:3rem;">Anything else? Write to
  <a href="mailto:{EMAIL}">{EMAIL}</a> or DM us on
  <a href="https://www.instagram.com/asha_berkeley/" target="_blank" rel="noopener">Instagram</a>.</p>
</div></section>'''

# DONATIONS: flat centered opening + static board.
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
  <h2>Where your money goes</h2>
  <p class="asha-prose">All of it goes to our projects and programs. We're entirely
  volunteer run, and every dollar is accounted for by our finance team.</p>
  <p class="asha-prose" style="margin-top:1.2em;">Questions about donating,
  sponsorships, or in-kind gifts? Write to <a href="mailto:{EMAIL}">{EMAIL}</a>
  or reach us on <a href="{VENMO}" target="_blank" rel="noopener">Venmo
  @ashaberkeley</a>.</p>
</div></section>'''

TITLES = {
    "index": ("Asha Berkeley", "index.html"),
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
