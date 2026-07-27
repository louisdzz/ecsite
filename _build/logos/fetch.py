# -*- coding: utf-8 -*-
"""Récupère le logo public de chaque cabinet depuis son propre site.
Ordre de préférence : balise <img> du header contenant 'logo', apple-touch-icon,
og:image, favicon. Enregistre dans assets/logos/<slug>.<ext>."""
import json, os, re, sys, urllib.parse, urllib.request, ssl, unicodedata

OUT = 'assets/logos'
os.makedirs(OUT, exist_ok=True)
UA = 'Mozilla/5.0 (compatible; ExitClubBot/1.0; +https://www.exit.club)'
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def slugify(s):
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r"[^a-zA-Z0-9]+", '-', s).strip('-').lower()
    return s


def get(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read(), r.headers.get('Content-Type', ''), r.geturl()


def candidates(html, base):
    out = []
    # <img ... logo ...>
    for m in re.finditer(r'<img[^>]+>', html, re.I):
        tag = m.group(0)
        src = re.search(r'(?:data-src|srcset|src)\s*=\s*["\']([^"\']+)["\']', tag, re.I)
        if not src:
            continue
        u = src.group(1).split()[0]
        blob = tag.lower()
        if 'logo' in blob or 'logo' in u.lower():
            out.append(u)
    for pat in [r'<link[^>]+rel=["\'][^"\']*apple-touch-icon[^"\']*["\'][^>]+href=["\']([^"\']+)["\']',
                r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\'][^"\']*apple-touch-icon[^"\']*["\']',
                r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
                r'<link[^>]+rel=["\'][^"\']*icon[^"\']*["\'][^>]+href=["\']([^"\']+)["\']']:
        for m in re.finditer(pat, html, re.I):
            out.append(m.group(1))
    seen, res = set(), []
    for u in out:
        u = urllib.parse.urljoin(base, u.strip())
        if u in seen:
            continue
        seen.add(u)
        if u.lower().split('?')[0].endswith(('.svg', '.png', '.jpg', '.jpeg', '.webp', '.ico', '.gif')) or 'image' in u:
            res.append(u)
    return res


EXT = {'image/png': '.png', 'image/jpeg': '.jpg', 'image/svg+xml': '.svg',
       'image/webp': '.webp', 'image/x-icon': '.ico', 'image/vnd.microsoft.icon': '.ico',
       'image/gif': '.gif'}


def grab(nom, site):
    slug = slugify(nom)
    try:
        html, ct, final = get(site)
        html = html.decode('utf-8', 'ignore')
    except Exception as e:
        return slug, None, 'home:%s' % type(e).__name__
    for u in candidates(html, final)[:8]:
        try:
            data, ct, _ = get(u)
        except Exception:
            continue
        ct = ct.split(';')[0].strip().lower()
        ext = EXT.get(ct)
        if not ext:
            continue
        if len(data) < 400 and ext != '.svg':
            continue
        if len(data) > 900_000:
            continue
        p = os.path.join(OUT, slug + ext)
        open(p, 'wb').write(data)
        return slug, p, u
    return slug, None, 'aucun candidat'


if __name__ == '__main__':
    S = json.load(open('_build/enrich/salve1.json'))
    APPEL = {'APPELER_PRIORITE_A', 'APPELER'}
    res = {}
    for c in S:
        if c['verdict'] not in APPEL or not c.get('site'):
            continue
        nom = c['nom'].split(' (')[0]
        slug, path, src = grab(nom, c['site'])
        res[nom] = {'slug': slug, 'fichier': path, 'source': src}
        print('%-32s %-46s %s' % (nom, path or '-', src), flush=True)
    json.dump(res, open('_build/logos/index.json', 'w'), ensure_ascii=False, indent=1)
