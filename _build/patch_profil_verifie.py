#!/usr/bin/env python3
"""Pose sur toutes les fiches (f/ et p/) le parcours décidé par Louis le 11 novembre 2026 :
bouton « Revendiquer ce profil » vers /revendiquer, appel « Profil vérifié » vers /tarifs avec la
mention « sans effet sur le classement », liens Méthodologie et Tarifs en bas de fiche.

Idempotent : relancer après chaque génération de fiches (python3 _build/patch_profil_verifie.py).
Ne touche ni aux données, ni aux rangs, ni aux fiches de redirection.
"""
import glob, html, os, re, sys
from urllib.parse import quote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = '<link href="/assets/annuaire/profil-verifie.css?v=20261111" rel="stylesheet"/>'
HORS_DOMAINE = ("linkedin.com", "tally.so", "google.", "facebook.com", "wa.me", "exit.club", "instagram.com", "twitter.com", "x.com", "youtube.com", "calendly.com", "cal.com")
NOTE = 'Profil vérifié : sans effet sur le classement. <a href="/methodologie">Méthodologie</a> · <a href="/tarifs">Tarifs</a>'
LIENS = ' <span class="ec-liens"><a href="/methodologie">Méthodologie</a> · <a href="/tarifs">Tarifs</a></span>'
NAV = '<a href="/methodologie">Méthodologie</a><a href="/tarifs">Tarifs</a>'
TARIF = 'Profil vérifié · 2 400 € HT par an'


def texte(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def domaine(h):
    for pat in (r'class="sitel" href="(https?://[^"]+)"', r'<dt>Site officiel</dt><dd><a href="(https?://[^"]+)"',
                r'class="pv-primary" href="(https?://[^"]+)"[^>]*>Découvrir la maison', r'<a href="(https?://[^"]+)"[^>]*>Site (?:de la maison|officiel)'):
        m = re.search(pat, h)
        if m:
            d = (urlparse(html.unescape(m.group(1))).hostname or "").lower()
            d = d[4:] if d.startswith("www.") else d
            if d and "." in d and not any(x in d for x in HORS_DOMAINE):
                return d
    return ""


def dom_site(url):
    d = (urlparse(url or "").hostname or "").lower()
    d = d[4:] if d.startswith("www.") else d
    return d if d and "." in d and not any(x in d for x in HORS_DOMAINE) else ""


def lien(slug, kind, maison="", nom="", dom=""):
    p = [("fiche", slug), ("type", kind)]
    if nom:
        p.append(("nom", nom))
    if maison:
        p.append(("maison", maison))
    if dom:
        p.append(("domaine", dom))
    return "/revendiquer?" + "&amp;".join("%s=%s" % (k, quote(v, safe="")) for k, v in p)


DOMAINES = {}


def domaine_maison(slug):
    if slug not in DOMAINES:
        p = os.path.join(ROOT, "f", slug + ".html")
        DOMAINES[slug] = domaine(open(p, encoding="utf-8").read()) if os.path.exists(p) else ""
    return DOMAINES[slug]


def patch(path):
    h0 = h = open(path, encoding="utf-8").read()
    if 'http-equiv="refresh"' in h:
        return None
    slug = os.path.basename(path)[:-5]
    personne = os.sep + "p" + os.sep in path
    m1 = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    titre = texte(m1.group(1)) if m1 else ""
    if personne:
        mm = re.search(r'<a class="pv-category" href="/f/([^"]+)">(.*?)</a>', h)
        claim = lien(slug, "personne", maison=texte(mm.group(2)) if mm else "", nom=titre, dom=domaine_maison(mm.group(1)) if mm else "")
    else:
        claim = lien(slug, "maison", maison=titre, dom=domaine(h))
    bouton = '<a class="ec-claim" data-ec-claim="" href="%s">Revendiquer ce profil</a>' % claim
    verifie = "ec-premium-status" in h or "ec-verifie-status" in h
    modele = slug.startswith("etalon-") or slug == "demo-fiche-verifiee"

    # Vocabulaire du profil payant : « Profil vérifié », jamais d'autre nom.
    if "ec-premium" in h or "Profil Premium" in h:
        h = h.replace("/assets/maison/premium.css", "/assets/maison/profil-verifie.css").replace("/assets/maison/premium.js", "/assets/maison/profil-verifie.js")
        h = re.sub(r'(profil-verifie\.(?:css|js))\?v=[^"]*', r"\1?v=20261111", h)
        h = h.replace("premium-info-", "verifie-info-").replace("ec-premium-", "ec-verifie-")
        h = h.replace("Profil Premium<span", "Profil vérifié<span").replace("Profil Premium :", "Profil vérifié :")
        h = h.replace("Présentation enrichie dans le cadre d’un abonnement payant. Sans influence sur les classements.", "Profil détaillé dans le cadre d’une offre payante. Sans effet sur le classement.")
        h = re.sub(r'(<div class="ec-verifie-status">.*?</div>)(?!<span class="ec-badge-note")', r'\1', h, count=1, flags=re.S)
        if 'ec-badge-note' not in h:
            h = re.sub(r'(<span class="ec-verifie-tooltip"[^>]*>.*?</span></div>)', r'\1<span class="ec-badge-note">sans effet sur le classement</span>', h, count=1, flags=re.S)
            h = h.replace('<div class="ec-verifie-status">', '<div class="ec-claim-box"><div class="ec-verifie-status">', 1).replace('<span class="ec-badge-note">sans effet sur le classement</span>', '<span class="ec-badge-note">sans effet sur le classement</span></div>', 1)

    if not modele:
        # 1. Bouton en tête de fiche (gabarit automatique et gabarit visuel).
        if "data-ec-claim" not in h and not verifie and 'class="pv-identity"' in h:
            st = re.search(r'<p class="pv-status">([^<]*)</p></header>', h)
            if st and "non revendiqu" in st.group(1):
                h = h.replace(st.group(0), '<div class="ec-claim-box"><p class="pv-status">%s</p>%s</div></header>' % (st.group(1), bouton), 1)
            elif not st and re.search(r'<header class="pv-identity">.*?</header>', h, re.S) and "pv-status" not in h:
                h = re.sub(r'(<header class="pv-identity">.*?)</header>', lambda m: m.group(1) + '<div class="ec-claim-box">%s</div></header>' % bouton, h, count=1, flags=re.S)
        # 2. Fiche automatique, maison.
        h = re.sub(r'<div class="fa-ctas"><a class="pv-primary" href="mailto:[^"]*">Corriger gratuitement</a><a class="pv-secondary" href="/fiche-verifiee[^"]*">Obtenir la fiche vérifiée</a></div>',
                   lambda m: '<div class="fa-ctas"><a class="pv-primary" href="%s">Revendiquer ce profil</a><a class="pv-secondary" href="/tarifs">%s</a></div><p class="ec-sans-effet">Revendiquer et corriger ses faits est gratuit. %s</p>' % (claim, TARIF, NOTE), h)
        # 3. Fiche automatique, personne.
        h = re.sub(r'<div class="fa-ctas"><a class="pv-primary" href="(mailto:[^"]*)">Corriger ou retirer ma fiche</a><a class="pv-secondary" href="/f/[^"]*">Voir la maison</a></div>',
                   lambda m: '<div class="fa-ctas"><a class="pv-primary" href="%s">Revendiquer ce profil</a><a class="pv-secondary" href="%s">Corriger ou retirer ma fiche</a></div><p class="ec-sans-effet">Revendiquer et corriger ses faits est gratuit. %s</p>' % (claim, m.group(1), NOTE), h)
        # 4. Ancien gabarit : bloc « Vous représentez … ».
        h = re.sub(r'<a class="(btn btn-(?:line|inv))" href="https://wa\.me/33749094435">Revendiquer ce profil</a>', lambda m: '<a class="%s" href="%s">Revendiquer ce profil</a>' % (m.group(1), claim), h)
        h = re.sub(r'<a class="btn btn-line" href="/fiche-verifiee[^"]*">Faire vérifier mon profil</a>\s*</div>',
                   lambda m: '<a class="btn btn-line" href="/tarifs">%s</a>\n</div><p class="small ec-sans-effet">%s</p>' % (TARIF, NOTE), h)
        h = re.sub(r'<a class="action" href="https://wa\.me/33749094435">Vous représentez [^<]*</a>', lambda m: '<a class="action" href="%s">Revendiquer ce profil</a>' % claim, h)
        h = re.sub(r'<a class="(action(?: primary)?)" href="/fiche-verifiee[^"]*">Compléter (?:la fiche|le profil)(?: · 2 400 € HT/an)?</a>', lambda m: '<a class="%s" href="/tarifs">%s · sans effet sur le classement</a>' % (m.group(1), TARIF), h)
        # 5. Fiches simples (patrimoine.css) : bouton sous le chapeau.
        if "data-ec-claim" not in h and not verifie and 'class="pv-identity"' not in h and "<main" in h and m1:
            bloc = '<p class="ec-claim-simple">%s</p><p class="ec-sans-effet">%s</p>' % (bouton, NOTE)
            lead = re.search(r'<p class="lead">.*?</p>', h, re.S)
            if lead and lead.start() > m1.start():
                h = h.replace(lead.group(0), lead.group(0) + bloc, 1)
            else:
                h = h.replace(m1.group(0), m1.group(0) + bloc, 1)

    # 6. Bas de fiche et pied de page : méthodologie et tarifs.
    if "ec-liens" not in h:
        h = h.replace("<p>Le référencement ne vaut pas recommandation de l’Exit Club.</p></div>", "<p>Le référencement ne vaut pas recommandation de l’Exit Club.%s</p></div>" % LIENS)
    if NAV not in h:
        h, n = re.subn(r'(<nav(?=[^>]*class="ec-legal-nav")[^>]*>)', lambda m: m.group(1) + NAV, h, count=1)
        if not n and "ec-liens" not in h:
            h = re.sub(r"</footer>", lambda m: LIENS + "</footer>", h, count=1)
    if h != h0 and "profil-verifie.css?v=" not in h.split("</head>")[0].replace("/assets/maison/profil-verifie.css", ""):
        h = h.replace("</head>", CSS + "</head>", 1)
    if h != h0:
        open(path, "w", encoding="utf-8").write(h)
    return h != h0


def main():
    stats = {"modifiées": 0, "inchangées": 0, "redirections": 0}
    sans_bouton = []
    for path in sorted(glob.glob(os.path.join(ROOT, "f", "*.html")) + glob.glob(os.path.join(ROOT, "p", "*.html"))):
        r = patch(path)
        stats["redirections" if r is None else "modifiées" if r else "inchangées"] += 1
        if r is not None and "/revendiquer?" not in open(path, encoding="utf-8").read():
            sans_bouton.append(os.path.relpath(path, ROOT))
    print(stats)
    print("fiches sans bouton « Revendiquer ce profil » (%d) : %s" % (len(sans_bouton), ", ".join(sans_bouton)))


if __name__ == "__main__":
    main()
