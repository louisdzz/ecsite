#!/usr/bin/env python3
"""Lot CIF : sociétés actives du registre (NAF donné, département donné) inscrites CIF à l'ORIAS et absentes du site.
Dédoublonnage strict : SIREN déjà connus (cgp-geo.json, donnees/), dénomination ou enseigne déjà au répertoire.
Entrepreneurs individuels et entités non diffusibles exclus. Aucune donnée de site : seuls registre et ORIAS.
Usage : python3 lot_orias.py <naf> <departement> <nombre> <sortie_dir> [page_debut] [page_fin] [--code_postal=75008] [--nature_juridique=5710] [--tranche_effectif_salarie=NN]
Le registre ne rend que les 10 000 premiers résultats d'une recherche. Au-delà, on découpe : --code_postal remplace le département
dans la requête (le département reste dans le libellé d'origine), et les autres options --clé=valeur sont ajoutées telles quelles à la requête
(plusieurs valeurs séparées par des virgules). Les SIREN déjà publiés sont écartés d'office, une plage peut donc en recouvrir une autre.
Le nom affiché est la dénomination exacte du registre, sans transformation de casse ni d'accents (consigne du 11 novembre 2026).
"""
import json, os, sys, time, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collecte import get, orias, norm, NJ, TODAY
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
argv = [a for a in sys.argv if not a.startswith("--")]
naf, dep, want, out = argv[1], argv[2], int(argv[3]), argv[4]
page = int(argv[5]) if len(argv) > 5 else 1
page_fin = int(argv[6]) if len(argv) > 6 else 10**6
cp = opts.pop("code_postal", None)
zone = ("code_postal=%s" % cp if cp else "departement=%s" % dep) + "".join("&%s=%s" % kv for kv in sorted(opts.items()))
os.makedirs(out, exist_ok=True)
geo = json.load(open(os.path.join(ROOT, "_build/cgp-geo.json"), encoding="utf-8"))
connus = {v.get("siren") for v in geo.values() if v.get("siren")} | {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ROOT, "_build/auto/donnees/[0-9]*.json"))}
houses = json.load(open(os.path.join(ROOT, "assets/ecosysteme/maison/data.json"), encoding="utf-8"))["houses"]
noms = {norm(h["name"]) for h in houses} | {h["slug"].replace("-", " ") for h in houses}
GEN = {"sas", "sarl", "sasu", "eurl", "sa", "groupe", "group", "holding", "et", "cie", "the", "la", "le", "les", "de", "du", "des"}
def cle(s):
    return " ".join(w for w in norm(s).split() if w not in GEN)
noms_cle = {cle(h["name"]) for h in houses}
def api(url):
    for k in range(6):
        u, t = get(url)
        if u:
            try:
                return json.loads(t)
            except Exception:
                pass
        # Erreur 429 : on ralentit nettement avant de réessayer.
        time.sleep(30 * (k + 1) if "429" in t else 2 * (k + 1))
    return None
def orias_sur(s):
    for k in range(4):
        o = orias(s)
        if o:
            return o
        time.sleep(20 * (k + 1))
    return None
kept, vus, rej = 0, 0, []
erreurs = []
while kept < want and page <= page_fin:
    r = api("https://recherche-entreprises.api.gouv.fr/search?activite_principale=%s&etat_administratif=A&%s&per_page=25&page=%d" % (naf, zone, page))
    if not r or not r.get("results"):
        break
    for a in r["results"]:
        vus += 1
        s = a["siren"]
        if s in connus or a.get("nature_juridique") in ("1000", None) or a.get("statut_diffusion") != "O" or a.get("etat_administratif") != "A":
            continue
        sg = a.get("siege") or {}
        den = a.get("nom_raison_sociale") or a.get("nom_complet")
        ens = sg.get("nom_commercial") or ((sg.get("liste_enseignes") or [None])[0])
        if not den or any(cle(x) in noms_cle or norm(x) in noms for x in (den, ens) if x) or not cle(den):
            rej.append({"siren": s, "nom": den, "motif": "dénomination ou enseigne déjà au répertoire : doublon possible"})
            continue
        o = orias_sur(s)
        time.sleep(0.3)
        if o is None:
            erreurs.append(s)
            continue
        if not o.get("inscrit") or not any(k["code"] == "CIF" and k["etat"] == "Inscrit" for k in o["categories"]):
            continue
        dirs = []
        for d in a.get("dirigeants") or []:
            q = d.get("qualite") or ""
            if re.search(r"commissaire aux comptes", q, re.I):
                continue
            if d.get("type_dirigeant") == "personne physique":
                dirs.append({"type": "pp", "prenoms": d.get("prenoms"), "nom": d.get("nom"), "qualite": q})
            else:
                dirs.append({"type": "pm", "denomination": d.get("denomination"), "siren": d.get("siren"), "qualite": q})
        reg = "https://annuaire-entreprises.data.gouv.fr/entreprise/%s" % s
        rec = {"nom_usuel": den, "categorie": "cgp", "crm": None, "slug_existant": None, "consulte_le": TODAY, "sources": {}, "origine": "lot ORIAS CIF %s dép. %s" % (naf, dep) + (" (code postal %s)" % cp if cp else ""),
               "siren_source": {"type": "registre", "url": reg}, "siren": s, "denomination": den, "nom_complet": a.get("nom_complet"), "sigle": a.get("sigle"), "enseigne": ens,
               "forme": NJ.get(a.get("nature_juridique")), "forme_code": a.get("nature_juridique"), "creation": a.get("date_creation"), "ville": sg.get("libelle_commune"), "actif": True,
               "naf": a.get("activite_principale"), "opposition_prospection": bool(a.get("opposition_diffusion_commerciale")), "registre_url": reg, "maj_rne": a.get("date_mise_a_jour_rne"),
               "dirigeants": dirs, "orias": o, "orias_site": {}, "site": None, "site_pages": [], "linkedin": None,
               "raison": {"texte": "Inscrite au registre ORIAS en catégorie conseiller en investissements financiers (CIF).", "label": "Registre ORIAS", "url": o["url"]}}
        json.dump(rec, open(os.path.join(out, s + ".json"), "w"), ensure_ascii=False, indent=1)
        connus.add(s); noms_cle.add(cle(den)); kept += 1
        print("OK", s, rec["nom_usuel"], rec["ville"], o["numero"], len(dirs), flush=True)
        if kept >= want:
            break
    page += 1
json.dump(erreurs, open(os.path.join(out, "_erreurs_orias.json"), "w"))
json.dump(rej, open(os.path.join(out, "_doublons_possibles.json"), "w"), ensure_ascii=False, indent=1)
print("FIN page suivante", page, "vus", vus, "retenus", kept, "doublons possibles", len(rej), "erreurs ORIAS", len(erreurs))
