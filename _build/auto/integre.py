#!/usr/bin/env python3
"""Intègre les fiches automatiques au site : répertoire (data.json), liste statique de
annuaire.html, sitemap. Idempotent. Usage : python3 _build/auto/integre.py [version-cache]"""
import json, os, re, sys, html, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
m = json.load(open(os.path.join(ROOT, "_build/auto/manifeste.json"), encoding="utf-8"))
key = lambda s: unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()

# 1. Répertoire dynamique
pd = os.path.join(ROOT, "assets/ecosysteme/maison/data.json")
raw = open(pd, encoding="utf-8").read()
d = json.loads(raw)
have = {h["slug"] for h in d["houses"]}
add = [x for x in m["maisons"] if x["slug"] not in have]
for x in add:
    # L'ordre existant du répertoire est conservé : insertion avant la première maison de slug supérieur.
    i = next((k for k, h in enumerate(d["houses"]) if h["slug"] > x["slug"]), len(d["houses"]))
    d["houses"].insert(i, {"slug": x["slug"], "name": x["nom"], "categories": [x["categorie"]], "logo": False})
if add:
    compact = ": " not in raw[:200]
    open(pd, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, separators=(",", ":")) if compact else json.dumps(d, ensure_ascii=False))

# 2. Liste statique (noscript) de annuaire.html
pa = os.path.join(ROOT, "annuaire.html")
h = open(pa, encoding="utf-8").read()
n_static = 0
for x in m["maisons"]:
    if 'href="/f/%s"' % x["slug"] in h:
        continue
    sec = re.search(r'(<section id="%s">.*?<ul>)(.*?)(</ul>)' % re.escape(x["categorie"]), h, re.S)
    items = re.findall(r'<li><a href="/f/[^"]+">.*?</a></li>', sec.group(2))
    items.append('<li><a href="/f/%s">%s</a></li>' % (x["slug"], html.escape(x["nom"], quote=False)))
    items.sort(key=lambda li: key(html.unescape(re.sub(r"<[^>]+>", "", li))))
    h = h[:sec.start(2)] + "".join(items) + h[sec.end(2):]
    n_static += 1
if len(sys.argv) > 1:
    h = re.sub(r'(/assets/ecosysteme/maison/app\.js\?v=)[^"]+', r"\g<1>" + sys.argv[1], h)
    pj = os.path.join(ROOT, "assets/ecosysteme/maison/app.js")
    js = open(pj, encoding="utf-8").read()
    open(pj, "w", encoding="utf-8").write(re.sub(r"(/assets/ecosysteme/maison/data\.json\?v=)[^']+", r"\g<1>" + sys.argv[1], js))
open(pa, "w", encoding="utf-8").write(h)

# 3. Sitemap : fiches maisons et personnes publiques ; retrait des pages supprimées
ps = os.path.join(ROOT, "sitemap.xml")
s = open(ps, encoding="utf-8").read()
want = ["https://www.exit.club/f/" + x["slug"] for x in m["maisons"]] + ["https://www.exit.club/p/" + x["slug"] for x in m["personnes"]]
n_map = 0
for u in want:
    if "<ns0:loc>%s</ns0:loc>" % u not in s:
        s = s.replace("</ns0:urlset>", "<ns0:url><ns0:loc>%s</ns0:loc></ns0:url></ns0:urlset>" % u)
        n_map += 1
n_out = 0
for u in re.findall(r"<ns0:loc>(https://www\.exit\.club/(?:f|p)/[^<]+)</ns0:loc>", s):
    kind, sl = u.rsplit("/", 2)[-2:]
    if not os.path.exists(os.path.join(ROOT, kind, sl + ".html")):
        s = s.replace("<ns0:url><ns0:loc>%s</ns0:loc></ns0:url>" % u, "")
        n_out += 1
open(ps, "w", encoding="utf-8").write(s)
print("répertoire +%d · liste statique +%d · sitemap +%d -%d" % (len(add), n_static, n_map, n_out))
