#!/usr/bin/env python3
"""Ajoute un lot de brèves au fil d'actualité : une page par brève dans actualites/, une carte dans actualites.html
(ordre par date d'annonce décroissante), option de maison dans le filtre, compteur, sitemap. Idempotent : une brève
dont la page existe déjà est ignorée. Le texte vient du suivi éditorial (statut « Prêt à publier »), sans réécriture.
Usage : python3 _build/actualites_ajoute.py _build/actualites-lot-AAAAMMJJ.json
"""
import json, os, re, sys, html, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lot = json.load(open(sys.argv[1], encoding="utf-8"))
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
def fr(d):
    p = d.split("-")
    if len(p) == 2:
        return "%s %s" % (MOIS[int(p[1]) - 1], p[0])
    j = int(p[2])
    return "%s %s %s" % ("1er" if j == 1 else j, MOIS[int(p[1]) - 1], p[0])
def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s.replace("&", " ")).strip("-")
e = lambda s: html.escape(s, quote=False)
ea = lambda s: html.escape(s, quote=True)
pub, cons = lot["publie_le"], lot["consulte_le"]
pa = os.path.join(ROOT, "actualites.html")
idx = open(pa, encoding="utf-8").read()
ps = os.path.join(ROOT, "sitemap.xml")
sm = open(ps, encoding="utf-8").read()
cards = re.findall(r'<article class="news-card".*?</article>', idx, re.S)
debut = idx.index(cards[0]); fin = idx.index(cards[-1]) + len(cards[-1])
assert idx[debut:fin] == "".join(cards), "cartes non contiguës"
def date_carte(c):
    return re.search(r'<time datetime="([^"]*)"', c).group(1)
n = 0
for b in lot["breves"]:
    slug = b["slug"]; f = os.path.join(ROOT, "actualites", slug + ".html")
    if os.path.exists(f):
        continue
    if b.get("fiche"):
        assert os.path.exists(os.path.join(ROOT, "f", b["fiche"] + ".html")), b["fiche"]
    url = "https://www.exit.club/actualites/" + slug
    d = b["date_annonce"]; jour = len(d) == 10
    dates = ('Annonce du <time datetime="%s">%s</time>' if jour else 'Annonce : <time datetime="%s">%s</time>') % (d, fr(d))
    ld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": b["titre"], "description": b["chapo"], "datePublished": pub + "T23:00:00+01:00",
          "publisher": {"@type": "Organization", "name": "Exit Club"}, "mainEntityOfPage": url}
    panel = ('<div class="news-house-panel"><div><p class="eyebrow">Dans l’annuaire</p><h2>%s</h2><p>%s</p></div><a class="news-button" href="/f/%s">Voir la fiche ↗</a></div>' % (e(b["maison"]), e(b["theme_libelle"]), b["fiche"])) if b.get("fiche") else ""
    page = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(t)s | L’Annuaire de l’Exit</title><meta name="description" content="%(da)s">
<link rel="canonical" href="%(u)s"><meta property="og:title" content="%(ta)s"><meta property="og:description" content="%(da)s"><meta property="og:url" content="%(u)s"><meta property="og:image" content="https://www.exit.club/og-image.png">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Fraunces:ital,opsz,wght@0,9..144,350;0,9..144,400;1,9..144,350&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ecosysteme/maison/style.css?v=20260915-bluefish"><link rel="stylesheet" href="/assets/actualites.css?v=20260926">
<script src="/assets/actualites.js?v=20260926" defer></script><script type="application/ld+json">%(ld)s</script><link rel="stylesheet" href="/assets/site/site.css?v=20261013-2"><script defer src="/assets/site/site.js?v=20261013-2"></script><link rel="icon" href="/favicon.ico"><link rel="icon" type="image/svg+xml" href="/favicon.svg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Exit Club et L’Annuaire de l’Exit"><meta name="twitter:card" content="summary_large_image"></head><body>
<a class="skip" href="#contenu">Aller au contenu</a>
<header class="header shell"><a class="wordmark" href="/" aria-label="Exit Club, accueil">exit<span>.</span><i>club</i></a><nav class="main-nav" aria-label="Navigation principale"><a href="/annuaire">L’Annuaire de l’Exit</a><a class="current" href="/actualites" aria-current="page">Actualités</a><a href="/#manifeste">Le Club</a></nav><a class="header-cta" href="/proposer-actualite">Proposer une actualité ↗</a></header>
<main id="contenu" class="shell news-main"><article class="news-article"><a class="news-back" href="/actualites">← Toutes les actualités</a><div class="news-meta"><span>%(th)s</span><span class="news-kind">%(k)s</span></div><h1>%(t)s</h1><p class="news-deck">%(d)s</p><p class="news-dates">%(dates)s · Publié le %(pub)s</p><div class="news-body">%(corps)s</div>
<div class="news-source"><strong>Source</strong><a href="%(src)s" target="_blank" rel="noopener noreferrer">%(srcl)s ↗</a><small>Consultée le %(cons)s</small></div>
%(panel)s
<p class="news-correction"><a href="mailto:louis@exit.club?subject=Correction%%20actualite%%20%(slug)s">Signaler une correction</a></p></article></main>
<footer class="shell news-footer"><span>Exit Club · L’Annuaire de l’Exit</span><a href="/annuaire">Toutes les maisons</a><a href="/proposer-actualite">Transmettre une nouvelle</a><a href="mailto:louis@exit.club">Nous écrire</a></footer><nav class="ec-legal-nav" aria-label="Informations légales"><a href="/confidentialite">Confidentialité</a><a href="/cgu">CGU et mentions légales</a><button type="button" data-cookie-preferences>Préférences cookies</button></nav></body></html>
""" % dict(t=e(b["titre"]), ta=ea(b["titre"]), da=ea(b["chapo"]), d=e(b["chapo"]), u=url, ld=json.dumps(ld, ensure_ascii=False).replace("</", "<\\/"), th=e(b["theme_libelle"]), k=e(b["type"]),
           dates=dates, pub=fr(pub), corps="".join("<p>%s</p>" % e(p) for p in b["corps"]), src=ea(b["source_url"]), srcl=e(b["source_libelle"]), cons=fr(cons), panel=panel, slug=slug)
    open(f, "w", encoding="utf-8").write(page)
    hs = b.get("fiche") or slugify(b["maison"])
    house = ('<a class="news-house" href="/f/%s"><span>%s<small>%s</small></span></a>' % (b["fiche"], e(b["maison"]), e(b["theme_libelle"]))) if b.get("fiche") else ('<span class="news-house"><span>%s<small>%s</small></span></span>' % (e(b["maison"]), e(b["theme_libelle"])))
    search = " ".join([b["titre"], b["maison"], b["chapo"], b["theme_libelle"], b["type"]])
    card = ('<article class="news-card" data-news data-theme="%s" data-house="%s" data-kind="%s" data-search="%s">\n<div class="news-meta"><time datetime="%s">%s</time><span class="news-kind">%s</span></div>\n'
            '<h2><a href="/actualites/%s">%s</a></h2><p class="news-summary">%s</p>\n<div class="news-card-foot">%s<a class="news-read" href="/actualites/%s" aria-label="Lire : %s">Lire ↗</a></div></article>') % (
            b["theme"], hs, ea(b["type"]), ea(search), d, fr(d), e(b["type"]), slug, e(b["titre"]), e(b["chapo"]), house, slug, ea(b["titre"]))
    # insertion : avant la première carte de date strictement inférieure (les plus récentes en tête ; un mois seul passe après ses jours)
    pos = next((i for i, c in enumerate(cards) if date_carte(c) < d), len(cards))
    cards.insert(pos, card)
    if 'option value="%s"' % hs not in idx:
        idx_opt = '<option value="%s">%s</option>' % (hs, e(b["maison"]))
        k = idx.index('</select></div><button type="reset"')
        idx = idx[:k] + idx_opt + idx[k:]
        debut = idx.index('<article class="news-card"')
        fin += len(idx_opt)
    loc = "<ns0:url><ns0:loc>%s</ns0:loc></ns0:url>" % url
    if url + "<" not in sm:
        k = sm.index("<ns0:url><ns0:loc>https://www.exit.club/actualites/")
        sm = sm[:k] + loc + sm[k:]
    n += 1
idx = idx[:debut] + "".join(cards) + idx[fin:]
idx = re.sub(r'(<p id="news-count"[^>]*>)\d+ actualités', lambda m: "%s%d actualités" % (m.group(1), len(cards)), idx)
open(pa, "w", encoding="utf-8").write(idx)
open(ps, "w", encoding="utf-8").write(sm)
print("brèves ajoutées", n, "· cartes", len(cards))
