#!/usr/bin/env python3
"""Mirror phoenixconsultinggroup.org subpages into a static local copy."""
import concurrent.futures
import hashlib
import os
import re
import subprocess
import urllib.parse

SITE = "https://www.phoenixconsultinggroup.org"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asha-site")
ASSETS = os.path.join(OUT, "assets")
os.makedirs(ASSETS, exist_ok=True)

PAGES = {
    "index": "/",
    "about": "/about",
    "projects": "/projects",
    "members": "/members",
    "join": "/join",
}

ASSET_HOSTS = (
    "images.squarespace-cdn.com",
    "static1.squarespace.com",
    "static.squarespace.com",
    "file.squarespace-cdn.com",
    "assets.squarespace.com",
    "use.typekit.net",
)

URL_RE = re.compile(
    r'(?:https?:)?//(' + "|".join(re.escape(h) for h in ASSET_HOSTS) + r')(/[^\s"\'<>\\()]+)'
)


def curl(url, dest=None):
    cmd = ["curl", "-sL", "--compressed", "--max-time", "120", url]
    if dest:
        cmd += ["-o", dest]
        return subprocess.run(cmd).returncode
    r = subprocess.run(cmd, capture_output=True)
    return r.stdout


def fetch_pages():
    pages = {}
    for name, path in PAGES.items():
        html = curl(SITE + path).decode("utf-8", "replace")
        assert len(html) > 10000, f"page {path} too small"
        pages[name] = html
        print(f"fetched {path}: {len(html)} bytes")
    return pages


def local_name(host, path):
    base = urllib.parse.unquote(path.rsplit("/", 1)[-1]).replace("+", " ")
    base = re.sub(r"[^A-Za-z0-9._-]", "_", base)[-60:]
    h = hashlib.md5((host + path).encode()).hexdigest()[:8]
    return f"{h}_{base}"


def collect(text, registry):
    """Find asset URLs; registry[(host,path)] = (download_url, local_file)."""
    for m in URL_RE.finditer(text):
        host, rest = m.group(1), m.group(2)
        if "?" in rest:
            path, query = rest.split("?", 1)
        else:
            path, query = rest, ""
        key = (host, path)
        if key in registry:
            continue
        if host == "images.squarespace-cdn.com":
            dl = f"https://{host}{path}?format=1500w"
        else:
            q = query.replace("&amp;", "&")
            dl = f"https://{host}{path}" + (f"?{q}" if q else "")
        registry[key] = (dl, local_name(host, path))


def rewrite(text, registry, prefix="assets/"):
    def repl_for(host, path, local):
        pat = re.compile(
            r'(?:https?:)?//' + re.escape(host) + re.escape(path) + r'(\?[^\s"\'<>\\()]*)?'
        )
        return pat

    for (host, path), (_, local) in registry.items():
        text = repl_for(host, path, local).sub(prefix + local, text)
    return text


def download_all(registry):
    def job(item):
        dl, local = item
        dest = os.path.join(ASSETS, local)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            return local, True
        rc = curl(dl, dest)
        ok = rc == 0 and os.path.exists(dest) and os.path.getsize(dest) > 0
        return local, ok

    fails = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for local, ok in ex.map(job, registry.values()):
            if not ok:
                fails.append(local)
    return fails


DESKTOP_ITEM = """
    <div class="header-nav-item header-nav-item--collection{active}">
      <a href="donations.html" data-animation-role="header-element"{aria}>
        Donations
      </a>
    </div>
  """

MOBILE_ITEM = """
            <div class="container header-menu-nav-item header-menu-nav-item--collection{active}">
              <a href="donations.html"{aria}>
                <div class="header-menu-nav-item-content">
                  Donations
                </div>
              </a>
            </div>
"""


def inject_nav(html, active=False):
    a = " header-menu-nav-item--active" if active else ""
    da = " header-nav-item--active" if active else ""
    aria = ' aria-current="page"' if active else ""
    # desktop: insert before the </nav> that closes header-nav-list
    i = html.find('header-nav-list')
    if i != -1:
        j = html.find("</nav>", i)
        if j != -1:
            html = html[:j] + DESKTOP_ITEM.format(active=da, aria=aria) + html[j:]
    # mobile: insert after the Projects mobile item
    pat = re.compile(
        r'(<div class="container header-menu-nav-item header-menu-nav-item--collection[^"]*">\s*'
        r'<a\s*href="(?:projects\.html|/projects)".*?</a>\s*</div>)',
        re.S,
    )
    html = pat.sub(lambda m: m.group(1) + MOBILE_ITEM.format(active=a, aria=aria), html, count=1)
    return html


def fix_links(html):
    for name, path in PAGES.items():
        target = "index.html" if name == "index" else f"{name}.html"
        html = re.sub(r'(href|data-href|data-folder-id)="' + re.escape(path) + r'(["#])',
                      r'\1="' + target + r'\2', html)
        html = re.sub(r'(href|data-href)="' + re.escape(SITE + path) + r'(["#])',
                      r'\1="' + target + r'\2', html)
    # remaining root-relative links -> live site
    html = re.sub(r'(href|data-href|data-folder-id)="(/[a-z][a-z0-9-]*(?:#[^"]*)?)"',
                  r'\1="' + SITE + r'\2"', html)
    return html


def inject_lazy_src(html):
    def fix(m):
        tag = m.group(0)
        if ' src=' in tag:
            return tag
        dm = re.search(r'data-src="([^"]+)"', tag)
        if not dm:
            return tag
        return tag[:4] + f' src="{dm.group(1)}"' + tag[4:]

    return re.sub(r'<img[^>]*>', fix, html)


def main():
    pages = fetch_pages()
    registry = {}
    for html in pages.values():
        collect(html, registry)
    print(f"assets found in HTML: {len(registry)}")
    fails = download_all(registry)

    # second level: css/js files referencing fonts/images
    css_registry = {}
    for (host, path), (_, local) in list(registry.items()):
        if not local.endswith((".css",)):
            continue
        p = os.path.join(ASSETS, local)
        if not os.path.exists(p):
            continue
        css = open(p, encoding="utf-8", errors="replace").read()
        collect(css, css_registry)
    for k in list(css_registry):
        if k in registry:
            del css_registry[k]
    print(f"assets found in CSS: {len(css_registry)}")
    fails += download_all(css_registry)
    # rewrite css files (font/image refs live in same dir -> no prefix)
    both = {**registry, **css_registry}
    for (host, path), (_, local) in registry.items():
        if local.endswith(".css"):
            p = os.path.join(ASSETS, local)
            css = open(p, encoding="utf-8", errors="replace").read()
            css = rewrite(css, both, prefix="")
            open(p, "w", encoding="utf-8").write(css)

    for name, html in pages.items():
        html = rewrite(html, both)
        html = fix_links(html)
        html = inject_lazy_src(html)
        html = inject_nav(html)
        out = os.path.join(OUT, "index.html" if name == "index" else f"{name}.html")
        open(out, "w", encoding="utf-8").write(html)
        print(f"wrote {out}")

    if fails:
        print("FAILED downloads:", fails)
    print("done")


if __name__ == "__main__":
    main()
