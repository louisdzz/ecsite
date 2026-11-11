#!/usr/bin/env python3
"""Fiches automatiques de l'Annuaire (maisons et personnes).

Entrée : _build/auto/donnees/<siren>.json, produits par _build/auto/collecte.py
à partir de sources publiques uniquement (API Recherche d'entreprises de l'État,
registre ORIAS, site officiel de la maison). Chaque champ affiché porte sa source
et sa date de consultation. Un champ sans source reste « Non renseigné ».

Sorties :
  f/<slug>.html                    maison sans fiche, ou remplacement d'une fiche existante
                                   non revendiquée (décision de Louis du 11 novembre 2026).
                                   L'ancienne version est archivée sous
                                   _build/auto/historique/f/ avant remplacement. Une fiche
                                   revendiquée, vérifiée ou liée à une offre au CRM
                                   (PROTEGES) n'est jamais remplacée.
  p/<slug>.html                    président, gérant, directeur général ou directeur général
                                   délégué au registre ; aucun autre mandataire
  _build/auto/manifeste.json       inventaire de ce qui a été généré et des refus

Règles : aucune note, aucun rang, aucune donnée privée du CRM, aucune date de
naissance, aucune adresse personnelle, aucune coordonnée. Entité non diffusible
ou homonymie non résolue : pas de fiche.
"""
import json, os, re, glob, html, unicodedata, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTO = os.path.join(ROOT, "_build", "auto")
MOIS = "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split()

CATS = {
    "mfo": {"label": "Multi-Family Offices",
            "metier": "Le métier de family office consiste à organiser le suivi du patrimoine et à coordonner les intervenants. Les services et les modes de rémunération varient selon la maison.",
            "questions": ["Quels sujets prenez-vous en charge directement ?", "Comment êtes-vous rémunérés par vos clients et les prestataires ?", "Quel suivi permet de voir l’ensemble du patrimoine ?"]},
    "cgp": {"label": "Conseillers en gestion de patrimoine (CGP)",
            "metier": "Le conseil en gestion de patrimoine part de la situation et des objectifs du client pour proposer une organisation et des placements. Le statut, les produits et la rémunération sont à comparer.",
            "questions": ["Quels statuts et habilitations couvrent votre intervention ?", "Comment êtes-vous rémunéré sur les solutions proposées ?", "Quels risques, frais et contraintes de sortie faut-il prévoir ?"]},
}
ORIAS_LIB = {"CIF": "Conseiller en investissements financiers", "COA": "Courtier d'assurance ou de réassurance", "COBSP": "Courtier en opérations de banque et en services de paiement", "MIOBSP": "Mandataire d'intermédiaire en opérations de banque et en services de paiement", "MOBSP": "Mandataire non exclusif en opérations de banque et en services de paiement", "MOBSPL": "Mandataire exclusif en opérations de banque et en services de paiement", "AGA": "Agent général d'assurance", "MA": "Mandataire d'assurance", "MIA": "Mandataire d'intermédiaire d'assurance", "ALPSI": "Agent lié de prestataire de services d'investissement", "CIP": "Conseiller en investissements participatifs", "IFP": "Intermédiaire en financement participatif"}
PARTICULES = {"de", "du", "des", "le", "la", "d", "van", "von", "den", "der"}
# Fiches existantes jamais remplacées : offre ou échange Annuaire au CRM (contrôle du 11 novembre 2026).
PROTEGES = {"myway-family-office", "norman-k"}
FONCTION_OK = re.compile(r"^(pr[ée]sident(?! du conseil de surveillance)|g[ée]rant|co-?g[ée]rant|directeur g[ée]n[ée]ral)", re.I)


def fonction_retenue(q):
    """Fiche personne seulement pour président, gérant, directeur général (délégué)."""
    return bool(FONCTION_OK.match((q or "").strip()))


def e(s):
    return html.escape(str(s), quote=True)


def fr_date(iso):
    y, m, d = (iso.split("-") + ["", ""])[:3]
    if d:
        return "%s %s %s" % ("1er" if int(d) == 1 else int(d), MOIS[int(m) - 1], y)
    return "%s %s" % (MOIS[int(m) - 1], y) if m else y


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s.replace("&", " ")).strip("-")


def norm(s):
    return re.sub(r"[^a-z]+", " ", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()).strip()


def nom_propre(s):
    out = []
    for i, w in enumerate(re.split(r"(\s+|-|')", (s or "").lower())):
        out.append(w if (w in PARTICULES and i) or not w.strip() or w in "-'" else w[:1].upper() + w[1:])
    return "".join(out).strip()


def nom_registre(prenom, nom):
    # Le nom d'état civil que le registre donne entre parenthèses n'est jamais affiché.
    nom = re.sub(r"\s*\(.*?\)\s*", " ", nom or "").strip()
    return nom_propre((prenom or "") + " " + nom)


def qualite(q):
    q = (q or "").strip()
    return "Mandataire, qualité non précisée au registre" if q in ("", "Autre") else q


def initiales(s):
    w = [x for x in re.split(r"[^A-Za-zÀ-ÿ0-9]+", s) if x and x.lower() not in PARTICULES and x != "&"]
    return "".join(x[0] for x in w[:2]).upper() or "·"


def src(label, url, date):
    """Mention de source affichée sous chaque champ."""
    lien = '<a href="%s" rel="noopener nofollow" target="_blank">%s</a>' % (e(url), e(label)) if url else e(label)
    return '<small class="fa-src">Source : %s, consulté le %s</small>' % (lien, fr_date(date))


def champ(dt, dd, source=""):
    return "<div><dt>%s</dt><dd>%s%s</dd></div>" % (e(dt), dd, source)


def head(titre, desc, canon, noindex, base_style, jsonld):
    return """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>%s | L’Annuaire de l’Exit</title>
<meta content="%s" name="description"/>
<meta content="%s · L’Annuaire de l’Exit" property="og:title"/>
<meta content="%s" property="og:description"/>
<meta content="%s" property="og:url"/>
<link href="%s" rel="canonical"/>%s
<style>%s</style>
<script type="application/ld+json">%s</script>
<link href="/assets/annuaire-navigation.css?v=20260915" rel="stylesheet"/>
<meta content="origin" name="referrer"/>
<script defer="" src="/assets/annuaire-mesure.js?v=20261013"></script>
<link href="/assets/maison/profil-commun.css?v=20261006-common" rel="stylesheet"/><link href="/assets/site/site.css?v=20261013-2" rel="stylesheet"/><script defer="" src="/assets/site/site.js?v=20261013-2"></script><link href="/favicon.ico" rel="icon"/><link href="/favicon.svg" rel="icon" type="image/svg+xml"/><meta content="https://www.exit.club/og-image.png" property="og:image"/><meta content="summary_large_image" name="twitter:card"/><link as="font" crossorigin="" href="/assets/mercury/font-6.woff2" rel="preload" type="font/woff2"/><link href="/assets/maison/fiche-visuelle.css?v=20261020-comparison" rel="stylesheet"/><link href="/assets/maison/fiche-auto.css?v=20261111" rel="stylesheet"/></head>
<body class="profile-page profile-visual-v2 fiche-auto" data-profile-design="auto-20261111">
<div class="wrap">
<div class="top">
<a class="mark" href="/" style="text-decoration:none;color:var(--ink)"><i>exit</i><b>.club</b></a>
<div style="display:flex;align-items:center;gap:22px">
<a href="/annuaire" style="font-size:13.5px;color:var(--muted);text-decoration:none">L’Annuaire de l’Exit</a>
<a href="https://tally.so/r/wADNZN" rel="noopener" style="font-size:13px;font-weight:600;color:var(--paper);background:var(--accent);padding:9px 16px;border-radius:999px;text-decoration:none" target="_blank">Rejoindre</a>
</div>
</div>
""" % (e(titre), e(desc), e(titre), e(desc), e(canon), e(canon), '\n<meta content="noindex, nofollow" name="robots"/>' if noindex else "", base_style, jsonld)


PIED = """</div>
<nav aria-label="Informations légales" class="ec-legal-nav"><a href="/confidentialite">Confidentialité</a><a href="/cgu">CGU et mentions légales</a><button data-cookie-preferences="" type="button">Préférences cookies</button></nav></body>
</html>
"""


def fiche_maison(r, slug, apercu, personnes, base_style):
    c = CATS[r["categorie"]]
    d = r["consulte_le"]
    nom = r["nom_usuel"]
    reg = lambda: src("Annuaire des entreprises (registres SIRENE et RNE)", r["registre_url"], d)
    ident = [champ("Dénomination", e(r["denomination"]), reg())]
    if r.get("enseigne") and norm(r["enseigne"]) != norm(r["denomination"]):
        ident.append(champ("Enseigne", e(r["enseigne"]), reg()))
    ident.append(champ("Forme juridique", e(r["forme"]) if r.get("forme") else "Non renseignée", reg() if r.get("forme") else ""))
    ident.append(champ("SIREN", e("%s %s %s" % (r["siren"][:3], r["siren"][3:6], r["siren"][6:])), reg()))
    ident.append(champ("Création", e(fr_date(r["creation"])) if r.get("creation") else "Non renseignée", reg() if r.get("creation") else ""))
    ident.append(champ("Ville du siège", e(nom_propre(r["ville"])) if r.get("ville") else "Non renseignée", reg() if r.get("ville") else ""))
    ident.append(champ("Statut", "Active au registre" if r["actif"] else "Cessée au registre", reg()))

    lignes = []
    for p in r["dirigeants"]:
        if p["type"] == "pp":
            pers = next((x for x in personnes if x["cle"] == (r["siren"], norm(p["prenoms"] or "") + "|" + norm(p["nom"] or ""))), None)
            n = pers["nom"] if pers else nom_registre(re.split(r"[ ,]+", (p["prenoms"] or "").strip())[0], p["nom"])
            lab = '<a href="/p/%s">%s</a>' % (pers["slug"], e(n)) if pers and pers.get("slug") else e(n)
        else:
            lab = e(p.get("denomination") or "Personne morale") + " <span class=\"fa-pm\">(personne morale)</span>"
        lignes.append("<li><b>%s</b><span>%s</span></li>" % (lab, e(qualite(p["qualite"]))))
    dirig = ('<ul class="fa-people">%s</ul>%s' % ("".join(lignes), reg())) if lignes else '<p class="fa-vide">Non renseigné au registre consulté.</p>'

    o = r.get("orias") or {}
    if o.get("inscrit"):
        cats = "".join("<li><b>%s</b><span>%s · %s le %s</span></li>" % (e(k["code"]), e(ORIAS_LIB.get(k["code"], k["libelle"])), "inscrit" if k["etat"] == "Inscrit" else e(k["etat"].lower()), e(k["date"])) for k in o["categories"])
        regl = '<dl class="pv-condition-list">%s</dl>%s' % (
            champ("ORIAS", "N° %s%s" % (e(o["numero"]), " · " + e(o["etat"].lower()) if o.get("etat") else ""), src("Registre ORIAS", o["url"], d)),
            ('<ul class="fa-people">%s</ul>%s' % (cats, src("Registre ORIAS", o["url"], d))) if cats else "")
    elif r.get("orias_site"):
        # Un numéro publié sur le site peut appartenir à une autre entité (filiale, partenaire) : il n'est pas attribué à ce SIREN.
        pu = next(iter(r["orias_site"].values()))
        regl = '<p class="fa-vide">Aucune inscription retrouvée sous ce SIREN au <a href="%s" rel="noopener nofollow" target="_blank">registre ORIAS</a> le %s. Le site de la maison mentionne des inscriptions ORIAS, qui peuvent être portées par d’autres entités.%s</p>' % (e(o.get("url") or "https://www.orias.fr/"), fr_date(d), src("site officiel de la maison", pu, d))
    else:
        regl = '<p class="fa-vide">Aucune inscription retrouvée sous ce SIREN au <a href="%s" rel="noopener nofollow" target="_blank">registre ORIAS</a> le %s. Agrément AMF, barreau ou chambre : non renseigné.</p>' % (e(o.get("url") or "https://www.orias.fr/"), fr_date(d))

    rs = r.get("raison")
    raison = ('%s%s' % (e(rs["texte"]), src(rs["label"], rs["url"], d))) if rs else "Rubrique issue du recensement initial de l’Annuaire. Justification publique non renseignée."
    liens = []
    if r.get("site"):
        liens.append(champ("Site officiel", '<a href="%s" rel="noopener nofollow" target="_blank">%s</a>' % (e(r["site"]), e(re.sub(r"^https?://(www\.)?|/$", "", r["site"]))), src("site officiel de la maison", (r.get("siren_source") or {}).get("url") or r["site"], d)))
    else:
        liens.append(champ("Site officiel", "Non renseigné"))
    if r.get("linkedin"):
        liens.append(champ("LinkedIn", '<a href="%s" rel="noopener nofollow" target="_blank">Page de la maison</a>' % e(r["linkedin"]["url"]), src("lien publié sur le site officiel", r["linkedin"]["source"], d)))
    else:
        liens.append(champ("LinkedIn", "Non renseigné"))

    url_pub = "https://www.exit.club/f/%s" % slug
    canon = url_pub
    corr = "mailto:louis@exit.club?subject=" + e("Fiche %s · correction" % slug).replace(" ", "%20")
    verif = "/fiche-verifiee?institution=%s&amp;cat=%s&amp;fiche=%s" % (e(nom).replace(" ", "%20"), r["categorie"], slug)
    jsonld = json.dumps({"@context": "https://schema.org", "@type": "Organization", "name": nom, "legalName": r["denomination"], "url": url_pub, **({"sameAs": [r["site"]]} if r.get("site") else {})}, ensure_ascii=False)
    desc = "%s : fiche générée à partir de sources publiques (registre, ORIAS, site officiel). Rubrique %s de L’Annuaire de l’Exit." % (nom, c["label"])
    h = head("%s · %s" % (nom, c["label"]), desc, canon, apercu, base_style, jsonld)
    av = '<p class="fa-apercu">Aperçu interne · cette maison a déjà une fiche publiée (<a href="/f/%s">/f/%s</a>), qui n’est pas modifiée.</p>' % (slug, slug) if apercu else ""
    lg = r.get("_logo")
    if isinstance(lg, dict) and lg.get("src") and os.path.exists(os.path.join(ROOT, lg["src"].lstrip("/"))):
        logo = '<div class="pv-brand-logo%s"><img alt="" decoding="async" src="%s"/></div>' % (" is-dark" if lg.get("dark") else "", e(lg["src"]))
    else:
        logo = '<div aria-hidden="true" class="pv-brand-logo pv-brand-initials">%s</div>' % e(initiales(nom))
    if r.get("_actus"):
        activite = '<ul class="fa-people">%s</ul><small class="fa-src">Source : articles de L’Annuaire de l’Exit, chacun avec ses sources</small>' % "".join('<li><b><a href="%s">%s</a></b><span>%s</span></li>' % (e(a["url"]), e(a["titre"]), fr_date(a["date"])) for a in r["_actus"][:8])
    else:
        activite = '<p class="fa-vide">Aucune opération ni actualité publique datée n’est rattachée à cette maison dans l’Annuaire à ce jour. Une information absente n’est pas une absence d’activité.</p>'
    liste = "".join('<li><b><a href="/p/%s">%s</a></b><span>%s</span></li>' % (x["slug"], e(x["nom"]), e(x["fonction"])) for x in personnes if x["siren"] == r["siren"] and x.get("slug"))
    body = """<div class="crumb"><a href="/annuaire">L’Annuaire de l’Exit</a> · <a href="/annuaire#{cat}">{label}</a></div>
<main class="pv-main pv-house-summary fa-main" data-category="{cat}" data-fiche-auto="maison" id="fiche-visuelle">{av}
<header class="pv-identity"><div class="pv-brand">{logo}<div><h1>{nom}</h1><a class="pv-category" href="/annuaire?metier={cat}">{label}</a></div></div></header>
<p class="fa-bandeau">Fiche générée à partir de sources publiques · non relue par la maison · consultée le {date}</p>
<div class="pv-information"><div>
<section aria-labelledby="fa-identite" id="identite"><h2 class="pv-section-title" id="fa-identite">Identité.</h2><dl class="pv-condition-list">{ident}</dl></section>
<section aria-labelledby="fa-dirigeants" id="dirigeants"><h2 class="pv-section-title" id="fa-dirigeants">Dirigeants légaux.</h2>{dirig}</section>
<section aria-labelledby="fa-statuts" id="statuts"><h2 class="pv-section-title" id="fa-statuts">Statuts réglementaires.</h2>{regl}</section>
<section aria-labelledby="fa-rubrique" id="rubrique"><h2 class="pv-section-title" id="fa-rubrique">Rubrique et raison du classement.</h2><dl class="pv-condition-list">{rub}{rai}</dl><p class="pv-source-note">{metier} Le référencement identifie un acteur. Il ne vaut ni note ni recommandation, et aucun paiement ne modifie un rang.</p></section>
<section aria-labelledby="fa-liens" id="liens"><h2 class="pv-section-title" id="fa-liens">Site officiel et LinkedIn.</h2><dl class="pv-condition-list">{liens}</dl></section>
<section aria-labelledby="fa-activite" id="activite"><h2 class="pv-section-title" id="fa-activite">Activité documentée.</h2>{activite}</section>
{pers}</div>
<div><aside aria-labelledby="pv-compare-title" class="pv-compare" id="questions-avant-contact"><p class="pv-compare-label">Avant de prendre contact</p><h2 id="pv-compare-title">Trois questions utiles.</h2><ol>{q}</ol><a class="pv-secondary" href="/annuaire?metier={cat}">Voir les autres acteurs</a></aside>
<aside aria-labelledby="fa-nr" class="pv-compare fa-nonrenseigne" id="non-renseigne"><p class="pv-compare-label">Non renseigné</p><h2 id="fa-nr">Ce que cette fiche ne dit pas.</h2><ul><li>Spécialités</li><li>Clientèle</li><li>Ticket d’entrée</li><li>Frais</li><li>Équipe</li><li>Entretien</li></ul><p class="fa-cta-q">Vous représentez cette maison ?</p><div class="fa-ctas"><a class="pv-primary" href="{corr}">Corriger gratuitement</a><a class="pv-secondary" href="{verif}">Obtenir la fiche vérifiée</a></div></aside></div></div>
<div class="pv-bottom"><a href="/annuaire?metier={cat}">Retour à la catégorie</a><p>Le référencement ne vaut pas recommandation de l’Exit Club.</p></div>
</main>
""".format(cat=r["categorie"], label=e(c["label"]), av=av, logo=logo, activite=activite, nom=e(nom), date=fr_date(d), ident="".join(ident), dirig=dirig, regl=regl,
           rub=champ("Rubrique", e(c["label"])), rai=champ("Raison", raison), metier=e(c["metier"]), liens="".join(liens),
           pers=('<section aria-labelledby="fa-personnes" id="personnes"><h2 class="pv-section-title" id="fa-personnes">Personnes de la maison.</h2><ul class="fa-people">%s</ul></section>' % liste) if liste else "",
           q="".join("<li>%s</li>" % e(x) for x in c["questions"]), corr=corr, verif=verif)
    return h + body + PIED


def fiche_personne(p, r, slug_maison, base_style):
    d = r["consulte_le"]
    url = "https://www.exit.club/p/%s" % p["slug"]
    reg = src("Annuaire des entreprises (registre RNE)", r["registre_url"], d)
    corr = "mailto:louis@exit.club?subject=" + e("Fiche personne %s · corriger ou retirer" % p["slug"]).replace(" ", "%20")
    jsonld = json.dumps({"@context": "https://schema.org", "@type": "Person", "name": p["nom"], "jobTitle": p["fonction"], "worksFor": {"@type": "Organization", "name": r["nom_usuel"]}, "url": url}, ensure_ascii=False)
    desc = "%s, %s de %s. Fiche générée à partir de sources publiques dans L’Annuaire de l’Exit." % (p["nom"], p["fonction"], r["nom_usuel"])
    h = head("%s · %s" % (p["nom"], r["nom_usuel"]), desc, url, False, base_style, jsonld)
    c = CATS[r["categorie"]]
    body = """<div class="crumb"><a href="/annuaire">L’Annuaire de l’Exit</a> · <a href="/annuaire#{cat}">{label}</a> · <a href="/f/{sm}">{maison}</a></div>
<main class="pv-main fa-main" data-fiche-auto="personne" id="fiche-visuelle">
<header class="pv-identity"><div class="pv-brand"><div aria-hidden="true" class="pv-brand-logo pv-brand-initials">{ini}</div><div><h1>{nom}</h1><a class="pv-category" href="/f/{sm}">{maison}</a></div></div></header>
<p class="fa-bandeau">Fiche générée à partir de sources publiques · non relue par la personne · consultée le {date}</p>
<div class="pv-information"><div>
<section aria-labelledby="fa-role"><h2 class="pv-section-title" id="fa-role">Fonction et maison.</h2><dl class="pv-condition-list">{f}{m}{a}{i}</dl></section>
<section aria-labelledby="fa-ops"><h2 class="pv-section-title" id="fa-ops">Opérations documentées.</h2><p class="fa-vide">Aucune opération nominativement documentée dans l’Annuaire à ce jour. Une information absente n’est pas une absence d’activité.</p></section>
</div>
<div><aside class="pv-compare fa-nonrenseigne"><p class="pv-compare-label">Vos droits</p><h2>Cette fiche vous concerne ?</h2><p class="fa-cta-q">Elle ne contient que des informations professionnelles publiques. Vous pouvez la faire corriger ou retirer, gratuitement.</p><div class="fa-ctas"><a class="pv-primary" href="{corr}">Corriger ou retirer ma fiche</a><a class="pv-secondary" href="/f/{sm}">Voir la maison</a></div></aside></div></div>
<div class="pv-bottom"><a href="/f/{sm}">Retour à la fiche de {maison}</a><p>Le référencement ne vaut pas recommandation de l’Exit Club.</p></div>
</main>
""".format(cat=r["categorie"], label=e(c["label"]), sm=slug_maison, maison=e(r["nom_usuel"]), ini=e(initiales(p["nom"])), nom=e(p["nom"]), date=fr_date(d),
           f=champ("Fonction", e(p["fonction"]), reg), m=champ("Maison", '<a href="/f/%s">%s</a>' % (slug_maison, e(r["nom_usuel"])), reg),
           a=champ("Date d’affiliation", "Non renseignée"), i=champ("Inscription réglementaire individuelle", "Non renseignée"), corr=corr)
    return h + body + PIED


def actualites_par_maison():
    """Articles déjà publiés sur le site qui citent une maison (lien /f/<slug>)."""
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "actualites", "*.html"))):
        h = open(f, encoding="utf-8").read()
        t = re.search(r'<meta property="og:title" content="([^"]*)"', h)
        dt = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})"', h)
        if not t or not dt:
            continue
        for sl in set(re.findall(r'href="/f/([a-z0-9-]+)"', h)):
            out.setdefault(sl, []).append({"date": dt.group(1), "titre": html.unescape(t.group(1)), "url": "/actualites/" + os.path.basename(f)[:-5]})
    for v in out.values():
        v.sort(key=lambda x: x["date"], reverse=True)
    return out


def est_auto(h):
    return 'data-fiche-auto="maison"' in h


def main():
    base_style = re.search(r"<style>(.*?)</style>", open(os.path.join(ROOT, "f", "norman-k.html"), encoding="utf-8").read(), re.S).group(1)
    profils_js = open(os.path.join(ROOT, "assets", "annuaire", "profils.js"), encoding="utf-8").read()
    usuels = json.load(open(os.path.join(AUTO, "noms_usuels.json"), encoding="utf-8")) if os.path.exists(os.path.join(AUTO, "noms_usuels.json")) else []
    usuels = {norm(x): x for x in usuels}
    recs = [json.load(open(x, encoding="utf-8")) for x in sorted(glob.glob(os.path.join(AUTO, "donnees", "[0-9]*.json")))]
    houses = {h["slug"]: h for h in json.load(open(os.path.join(ROOT, "assets", "ecosysteme", "maison", "data.json"), encoding="utf-8"))["houses"]}
    actus = actualites_par_maison()
    ancien = json.load(open(os.path.join(AUTO, "manifeste.json"), encoding="utf-8")) if os.path.exists(os.path.join(AUTO, "manifeste.json")) else {"maisons": [], "personnes": []}
    manifeste = {"maisons": [], "personnes": [], "refus": [], "retraits": []}

    # Maisons retenues : actives, slug unique, fiche existante remplaçable.
    # Le slug d'une fiche déjà publiée ne change jamais, même si le nom affiché est corrigé.
    slug_fixe = {x["siren"]: x["slug"] for x in ancien.get("maisons", [])}
    slugs, retenus = {}, []
    for r in recs:
        if not r["actif"]:
            manifeste["refus"].append({"maison": r["nom_usuel"], "motif": "entité cessée au registre"})
            continue
        slug = r.get("slug_existant") or slug_fixe.get(r["siren"]) or slugify(r["nom_usuel"])
        if slug in slugs:
            manifeste["refus"].append({"maison": r["nom_usuel"], "motif": "slug en doublon avec " + slugs[slug]})
            continue
        dest = os.path.join(ROOT, "f", slug + ".html")
        remplace = False
        if os.path.exists(dest):
            old = open(dest, encoding="utf-8").read()
            if not est_auto(old):
                if slug in PROTEGES or "non revendiqué" not in old:
                    manifeste["refus"].append({"maison": r["nom_usuel"], "motif": "fiche existante revendiquée, vérifiée ou liée à une offre au CRM : non remplacée"})
                    continue
                if not r.get("slug_existant"):
                    manifeste["refus"].append({"maison": r["nom_usuel"], "siren": r["siren"], "motif": "slug déjà pris par une autre fiche, rapprochement non établi"})
                    continue
                hist = os.path.join(AUTO, "historique", "f", slug + ".html")
                os.makedirs(os.path.dirname(hist), exist_ok=True)
                if not os.path.exists(hist):
                    open(hist, "w", encoding="utf-8").write(old)
                remplace = True
            else:
                remplace = os.path.exists(os.path.join(AUTO, "historique", "f", slug + ".html"))
        slugs[slug] = r["nom_usuel"]
        r["_slug"], r["_remplace"] = slug, remplace
        r["_logo"] = (houses.get(slug) or {}).get("logo") or None
        r["_actus"] = actus.get(slug, [])
        retenus.append(r)

    # Personnes : président, gérant, directeur général (délégué) du registre. Homonymie entre maisons : pas de fiche.
    personnes, vus = [], {}
    for r in retenus:
        for p in r["dirigeants"]:
            if p["type"] != "pp" or not p.get("nom") or not p.get("prenoms"):
                continue
            toks = re.split(r"[ ,]+", p["prenoms"].strip())
            prenom = toks[0]
            # Prénom composé saisi avec une espace au registre (« JEAN- LOUIS ») : les deux parties sont réunies sur la fiche maison,
            # et aucune fiche personne n'est créée, le nom exact n'étant pas établi.
            coupe = prenom.endswith("-") and len(toks) > 1
            if coupe:
                prenom = prenom + toks[1]
            cle = (r["siren"], norm(p["prenoms"]) + "|" + norm(p["nom"]))
            fonction = qualite(p["qualite"])
            m = re.match(r"^(.*?)\s*\((.*?)\)\s*$", p["nom"])
            if m:
                # Deux noms au registre : le nom professionnel corroboré par une source publique est retenu,
                # sinon le nom hors parenthèse. Le nom entre parenthèses n'est jamais affiché.
                ok = [usuels[norm(prenom + " " + part)] for part in m.groups() if norm(prenom + " " + part) in usuels]
                nom = ok[0] if len(ok) == 1 else nom_propre(prenom + " " + m.group(1))
            else:
                brut = nom_propre(prenom + " " + p["nom"])
                nom = usuels.get(norm(brut), brut)
            incertain = (bool(m) and len(ok) != 1) or coupe
            x = {"cle": cle, "siren": r["siren"], "nom": nom, "fonction": fonction, "slug": slugify(nom) if fonction_retenue(p["qualite"]) and not incertain else None}
            if coupe and fonction_retenue(p["qualite"]):
                manifeste["refus"].append({"personne": nom, "motif": "prénom composé mal saisi au registre : listée sur la fiche maison, pas de fiche personne"})
            elif incertain and fonction_retenue(p["qualite"]):
                manifeste["refus"].append({"personne": nom, "motif": "deux noms au registre, nom professionnel non corroboré par le site de la maison : listée sur la fiche maison, pas de fiche personne"})
            personnes.append(x)
            if x["slug"]:
                vus.setdefault(x["slug"], []).append(x)
    for s, lst in vus.items():
        refus = None
        if len({x["siren"] for x in lst}) > 1 or len(lst) > 1:
            refus = "homonymie ou mandats multiples non résolus"
        elif re.search(r'"%s"|\b%s\b' % (re.escape(s), re.escape(lst[0]["nom"])), profils_js):
            refus = "personne déjà présente dans les profils publiés : pas de doublon"
        if refus:
            for x in lst:
                x["slug"] = None
            manifeste["refus"].append({"personne": lst[0]["nom"], "motif": refus})

    os.makedirs(os.path.join(ROOT, "p"), exist_ok=True)
    for r in retenus:
        slug = r["_slug"]
        dest = os.path.join(ROOT, "f", slug + ".html")
        open(dest, "w", encoding="utf-8").write(fiche_maison(r, slug, False, personnes, base_style))
        manifeste["maisons"].append({"slug": slug, "nom": r["nom_usuel"], "categorie": r["categorie"], "siren": r["siren"], "apercu": False, "remplace": r["_remplace"], "chemin": "f/%s.html" % slug, "crm": r.get("crm"), "orias": (r.get("orias") or {}).get("numero"), "opposition_prospection": r.get("opposition_prospection"), "consulte_le": r["consulte_le"]})
        for p in personnes:
            if p["siren"] == r["siren"] and p.get("slug"):
                open(os.path.join(ROOT, "p", p["slug"] + ".html"), "w", encoding="utf-8").write(fiche_personne(p, r, slug, base_style))
                manifeste["personnes"].append({"slug": p["slug"], "nom": p["nom"], "fonction": p["fonction"], "maison": slug, "siren": r["siren"], "chemin": "p/%s.html" % p["slug"]})

    # Fiches personnes qui ne sont plus produites (autres mandataires, retraits) : supprimées. Aperçus : supprimés.
    garde = {p["slug"] for p in manifeste["personnes"]}
    for f in glob.glob(os.path.join(ROOT, "p", "*.html")):
        sl = os.path.basename(f)[:-5]
        if sl not in garde and 'data-fiche-auto="personne"' in open(f, encoding="utf-8").read():
            os.remove(f)
            manifeste["retraits"].append({"personne": sl, "motif": "fonction hors président, gérant, directeur général, ou fiche non reconduite"})
    for f in glob.glob(os.path.join(ROOT, "annuaire-apercu", "f", "*.html")):
        os.remove(f)
    for d in (os.path.join(ROOT, "annuaire-apercu", "f"), os.path.join(ROOT, "annuaire-apercu")):
        if os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d)
    json.dump(manifeste, open(os.path.join(AUTO, "manifeste.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("maisons", len(manifeste["maisons"]), "dont remplacements", sum(m["remplace"] for m in manifeste["maisons"]), "· personnes", len(manifeste["personnes"]), "· refus", len(manifeste["refus"]), "· retraits", len(manifeste["retraits"]))


if __name__ == "__main__":
    main()
