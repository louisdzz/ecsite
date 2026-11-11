#!/usr/bin/env python3
"""Fiches automatiques de l'Annuaire (maisons et personnes).

Entrée : _build/auto/donnees/<siren>.json, produits par _build/auto/collecte.py
à partir de sources publiques uniquement (API Recherche d'entreprises de l'État,
registre ORIAS, site officiel de la maison). Chaque champ affiché porte sa source
et sa date de consultation. Un champ sans source reste « Non renseigné ».

Sorties :
  f/<slug>.html                    maison sans fiche existante
  annuaire-apercu/f/<slug>.html    aperçu (noindex) pour une maison déjà dotée d'une
                                   fiche : la fiche existante n'est jamais écrasée
  p/<slug>.html                    personne dont le rôle est prouvé par le registre
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
    m = re.match(r"^(.*?)\s*\((.*?)\)\s*$", nom or "")
    if m:
        return "%s %s (%s)" % (nom_propre(prenom), nom_propre(m.group(1)), nom_propre(m.group(2)))
    return nom_propre((prenom or "") + " " + (nom or ""))


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
        num, pu = next(iter(r["orias_site"].items()))
        regl = '<dl class="pv-condition-list">%s</dl><p class="fa-vide">Inscription déclarée par la maison, non retrouvée sous ce SIREN au registre ORIAS lors de la consultation. <a href="https://www.orias.fr/" rel="noopener nofollow" target="_blank">Vérifier sur orias.fr</a></p>' % champ("ORIAS", "N° %s (déclaré par la maison)" % e(num), src("site officiel de la maison", pu, d))
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
    liste = "".join('<li><b><a href="/p/%s">%s</a></b><span>%s</span></li>' % (x["slug"], e(x["nom"]), e(x["fonction"])) for x in personnes if x["siren"] == r["siren"] and x.get("slug"))
    body = """<div class="crumb"><a href="/annuaire">L’Annuaire de l’Exit</a> · <a href="/annuaire#{cat}">{label}</a></div>
<main class="pv-main pv-house-summary fa-main" data-category="{cat}" data-fiche-auto="maison" id="fiche-visuelle">{av}
<header class="pv-identity"><div class="pv-brand"><div aria-hidden="true" class="pv-brand-logo pv-brand-initials">{ini}</div><div><h1>{nom}</h1><a class="pv-category" href="/annuaire?metier={cat}">{label}</a></div></div></header>
<p class="fa-bandeau">Fiche générée à partir de sources publiques · non relue par la maison · consultée le {date}</p>
<div class="pv-information"><div>
<section aria-labelledby="fa-identite" id="identite"><h2 class="pv-section-title" id="fa-identite">Identité.</h2><dl class="pv-condition-list">{ident}</dl></section>
<section aria-labelledby="fa-dirigeants" id="dirigeants"><h2 class="pv-section-title" id="fa-dirigeants">Dirigeants légaux.</h2>{dirig}</section>
<section aria-labelledby="fa-statuts" id="statuts"><h2 class="pv-section-title" id="fa-statuts">Statuts réglementaires.</h2>{regl}</section>
<section aria-labelledby="fa-rubrique" id="rubrique"><h2 class="pv-section-title" id="fa-rubrique">Rubrique et raison du classement.</h2><dl class="pv-condition-list">{rub}{rai}</dl><p class="pv-source-note">{metier} Le référencement identifie un acteur. Il ne vaut ni note ni recommandation, et aucun paiement ne modifie un rang.</p></section>
<section aria-labelledby="fa-liens" id="liens"><h2 class="pv-section-title" id="fa-liens">Site officiel et LinkedIn.</h2><dl class="pv-condition-list">{liens}</dl></section>
<section aria-labelledby="fa-activite" id="activite"><h2 class="pv-section-title" id="fa-activite">Activité documentée.</h2><p class="fa-vide">Aucune opération ni actualité publique datée n’est rattachée à cette maison dans l’Annuaire à ce jour. Une information absente n’est pas une absence d’activité.</p></section>
{pers}</div>
<div><aside aria-labelledby="pv-compare-title" class="pv-compare" id="questions-avant-contact"><p class="pv-compare-label">Avant de prendre contact</p><h2 id="pv-compare-title">Trois questions utiles.</h2><ol>{q}</ol><a class="pv-secondary" href="/annuaire?metier={cat}">Voir les autres acteurs</a></aside>
<aside aria-labelledby="fa-nr" class="pv-compare fa-nonrenseigne" id="non-renseigne"><p class="pv-compare-label">Non renseigné</p><h2 id="fa-nr">Ce que cette fiche ne dit pas.</h2><ul><li>Spécialités</li><li>Clientèle</li><li>Ticket d’entrée</li><li>Frais</li><li>Équipe</li><li>Entretien</li></ul><p class="fa-cta-q">Vous représentez cette maison ?</p><div class="fa-ctas"><a class="pv-primary" href="{corr}">Corriger gratuitement</a><a class="pv-secondary" href="{verif}">Obtenir la fiche vérifiée</a></div></aside></div></div>
<div class="pv-bottom"><a href="/annuaire?metier={cat}">Retour à la catégorie</a><p>Le référencement ne vaut pas recommandation de l’Exit Club.</p></div>
</main>
""".format(cat=r["categorie"], label=e(c["label"]), av=av, ini=e(initiales(nom)), nom=e(nom), date=fr_date(d), ident="".join(ident), dirig=dirig, regl=regl,
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


def main():
    base_style = re.search(r"<style>(.*?)</style>", open(os.path.join(ROOT, "f", "norman-k.html"), encoding="utf-8").read(), re.S).group(1)
    existants = {os.path.basename(x)[:-5] for x in glob.glob(os.path.join(ROOT, "f", "*.html"))}
    profils_js = open(os.path.join(ROOT, "assets", "annuaire", "profils.js"), encoding="utf-8").read()
    usuels = json.load(open(os.path.join(AUTO, "noms_usuels.json"), encoding="utf-8")) if os.path.exists(os.path.join(AUTO, "noms_usuels.json")) else []
    usuels = {norm(x): x for x in usuels}
    recs = [json.load(open(x, encoding="utf-8")) for x in sorted(glob.glob(os.path.join(AUTO, "donnees", "[0-9]*.json")))]
    manifeste = {"maisons": [], "personnes": [], "refus": []}
    deja_auto = {m["slug"] for m in (json.load(open(os.path.join(AUTO, "manifeste.json"))).get("maisons", []) if os.path.exists(os.path.join(AUTO, "manifeste.json")) else []) if not m["apercu"]}

    # Personnes : dirigeants personnes physiques du registre. Homonymie entre maisons : pas de fiche.
    personnes, vus = [], {}
    for r in recs:
        if not r["actif"]:
            continue
        for p in r["dirigeants"]:
            if p["type"] != "pp" or not p.get("nom") or not p.get("prenoms"):
                continue
            prenom = re.split(r"[ ,]+", p["prenoms"].strip())[0]
            cle = (r["siren"], norm(p["prenoms"]) + "|" + norm(p["nom"]))
            fonction = qualite(p["qualite"])
            m = re.match(r"^(.*?)\s*\((.*?)\)\s*$", p["nom"])
            if m:
                # Le registre donne deux noms (naissance et usage). Le nom professionnel n'est retenu
                # que s'il est corroboré par une source professionnelle publique ; sinon pas de fiche.
                ok = [usuels[norm(prenom + " " + part)] for part in m.groups() if norm(prenom + " " + part) in usuels]
                if len(ok) != 1:
                    personnes.append({"cle": cle, "siren": r["siren"], "nom": nom_registre(prenom, p["nom"]), "fonction": fonction, "slug": None})
                    manifeste["refus"].append({"personne": nom_registre(prenom, p["nom"]), "motif": "deux noms au registre, nom professionnel non corroboré"})
                    continue
                nom = ok[0]
            else:
                brut = nom_propre(prenom + " " + p["nom"])
                nom = usuels.get(norm(brut), brut)
            x = {"cle": cle, "siren": r["siren"], "nom": nom, "fonction": fonction, "slug": slugify(nom)}
            personnes.append(x)
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
    os.makedirs(os.path.join(ROOT, "annuaire-apercu", "f"), exist_ok=True)
    slugs = {}
    for r in recs:
        if not r["actif"]:
            manifeste["refus"].append({"maison": r["nom_usuel"], "motif": "entité cessée au registre"})
            continue
        slug = r.get("slug_existant") or slugify(r["nom_usuel"])
        if slug in slugs:
            manifeste["refus"].append({"maison": r["nom_usuel"], "motif": "slug en doublon avec " + slugs[slug]})
            continue
        slugs[slug] = r["nom_usuel"]
        apercu = bool(r.get("slug_existant")) or (slug in existants and slug not in deja_auto)
        r["_slug"], r["_apercu"] = slug, apercu
    for r in recs:
        if "_slug" not in r:
            continue
        slug, apercu = r["_slug"], r["_apercu"]
        dest = os.path.join(ROOT, "annuaire-apercu", "f", slug + ".html") if apercu else os.path.join(ROOT, "f", slug + ".html")
        open(dest, "w", encoding="utf-8").write(fiche_maison(r, slug, apercu, personnes, base_style))
        manifeste["maisons"].append({"slug": slug, "nom": r["nom_usuel"], "siren": r["siren"], "apercu": apercu, "chemin": os.path.relpath(dest, ROOT), "crm": r.get("crm"), "orias": (r.get("orias") or {}).get("numero"), "opposition_prospection": r.get("opposition_prospection")})
        for p in personnes:
            if p["siren"] == r["siren"] and p.get("slug"):
                open(os.path.join(ROOT, "p", p["slug"] + ".html"), "w", encoding="utf-8").write(fiche_personne(p, r, slug, base_style))
                manifeste["personnes"].append({"slug": p["slug"], "nom": p["nom"], "fonction": p["fonction"], "maison": slug, "siren": r["siren"], "chemin": "p/%s.html" % p["slug"]})
    json.dump(manifeste, open(os.path.join(AUTO, "manifeste.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("maisons", len(manifeste["maisons"]), "dont aperçus", sum(m["apercu"] for m in manifeste["maisons"]), "· personnes", len(manifeste["personnes"]), "· refus", len(manifeste["refus"]))


if __name__ == "__main__":
    main()
