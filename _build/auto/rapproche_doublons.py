#!/usr/bin/env python3
"""Rapprochement par SIREN des doublons possibles écartés par lot_orias.py.
Pour chaque société écartée (dénomination ou enseigne déjà au répertoire), on cherche la fiche existante de même nom,
on lit le site connu de cette fiche (_build/domains/) et on ne conclut que si ce site publie le SIREN de la société
(mentions légales). Dans ce cas seulement, et si la fiche existante est non revendiquée et de rubrique cgp ou mfo,
un enregistrement sourcé est produit avec slug_existant : build_fiches_auto.py archive l'ancienne version et la remplace.
Aucune conclusion sur le nom seul. Reprise possible : le fichier de sortie est relu.
Usage : python3 _build/auto/rapproche_doublons.py <sortie_dir> [libellé de lot contenu dans le champ lot]
"""
import json, os, sys, re, glob, time, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collecte import get, orias, norm, NJ, TODAY, site_scan, api
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out = sys.argv[1]
filtre = sys.argv[2] if len(sys.argv) > 2 else ""
os.makedirs(out, exist_ok=True)
GEN = {"sas", "sarl", "sasu", "eurl", "sa", "groupe", "group", "holding", "et", "cie", "the", "la", "le", "les", "de", "du", "des"}
cle = lambda s: " ".join(w for w in norm(s).split() if w not in GEN)
houses = json.load(open(os.path.join(ROOT, "assets/ecosysteme/maison/data.json"), encoding="utf-8"))["houses"]
par = {}
for h in houses:
    for k in {cle(h["name"]), norm(h["name"]), h["slug"].replace("-", " ")}:
        par.setdefault(k, set()).add(h["slug"])
cat = {h["slug"]: h["categories"] for h in houses}
dom = {}
for f in sorted(glob.glob(os.path.join(ROOT, "_build/domains/*.json"))):
    for k, v in json.load(open(f, encoding="utf-8")).items():
        if isinstance(v, dict) and v.get("url"):
            dom[k] = v["url"]
publies = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ROOT, "_build/auto/donnees/[0-9]*.json"))}
rej = [x for x in json.load(open(os.path.join(ROOT, "_build/auto/donnees/_rejets.json"), encoding="utf-8")) if x.get("siren") and filtre in (x.get("lot") or "")]
pj = os.path.join(out, "_journal.json")
journal = json.load(open(pj, encoding="utf-8")) if os.path.exists(pj) else {}
for x in rej:
    s = x["siren"]
    if s in journal or s in publies:
        continue
    a = api(s)
    time.sleep(0.4)
    if not a:
        journal[s] = {"nom": x["nom"], "issue": "registre injoignable"}; continue
    sg = a.get("siege") or {}
    den = a.get("nom_raison_sociale") or a.get("nom_complet")
    ens = sg.get("nom_commercial") or ((sg.get("liste_enseignes") or [None])[0])
    cands = sorted({sl for n in (den, ens) if n for k in (cle(n), norm(n)) for sl in par.get(k, ())})
    j = {"nom": den, "candidats": cands}
    if a.get("etat_administratif") != "A" or a.get("statut_diffusion") != "O" or a.get("nature_juridique") in ("1000", None):
        j["issue"] = "société cessée, non diffusible ou entrepreneur individuel"
    elif len(cands) != 1:
        j["issue"] = "aucune ou plusieurs fiches de même nom : non résolu"
    else:
        sl = cands[0]
        old = open(os.path.join(ROOT, "f", sl + ".html"), encoding="utf-8").read()
        c = cat[sl]
        if 'data-fiche-auto="maison"' in old:
            j["issue"] = "la fiche de même nom est déjà une fiche automatique d'un autre SIREN : homonyme, non résolu"
        elif "non revendiqué" not in old:
            j["issue"] = "fiche existante revendiquée, vérifiée ou protégée : intacte"
        elif len(c) != 1 or c[0] not in ("cgp", "mfo"):
            j["issue"] = "fiche existante d'une autre rubrique (%s) : intacte" % ", ".join(c)
        elif sl not in dom:
            j["issue"] = "aucun site connu pour la fiche existante : identité non établie"
        else:
            sc = site_scan(dom[sl])
            j["site"], j["pages"], j["sirens_site"] = dom[sl], sc["pages"], list(sc["sirens"])
            if s not in sc["sirens"]:
                j["issue"] = "le site connu ne publie pas ce SIREN : identité non établie"
            else:
                o = None
                for k in range(4):
                    o = orias(s)
                    if o:
                        break
                    time.sleep(15 * (k + 1))
                if not o or not o.get("inscrit") or not any(k["code"] == "CIF" and k["etat"] == "Inscrit" for k in o["categories"]):
                    j["issue"] = "ORIAS : CIF non inscrit ou registre injoignable"
                else:
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
                    # Nom affiché : dénomination exacte du registre (le nom du site n'est pas relevé par ce script).
                    rec = {"nom_usuel": den, "categorie": c[0], "crm": None, "slug_existant": sl, "consulte_le": TODAY, "sources": {},
                           "origine": "rapprochement par SIREN d'un doublon possible (%s)" % (x.get("lot") or ""),
                           "siren_source": {"type": "site officiel", "url": sc["sirens"][s]}, "siren": s, "denomination": den, "nom_complet": a.get("nom_complet"), "sigle": a.get("sigle"), "enseigne": ens,
                           "forme": NJ.get(a.get("nature_juridique")), "forme_code": a.get("nature_juridique"), "creation": a.get("date_creation"), "ville": sg.get("libelle_commune"), "actif": True,
                           "naf": a.get("activite_principale"), "opposition_prospection": bool(a.get("opposition_diffusion_commerciale")), "registre_url": reg, "maj_rne": a.get("date_mise_a_jour_rne"),
                           "dirigeants": dirs, "orias": o, "orias_site": {}, "site": dom[sl], "site_pages": sc["pages"], "linkedin": sc["linkedin"],
                           "raison": {"texte": "Inscrite au registre ORIAS en catégorie conseiller en investissements financiers (CIF).", "label": "Registre ORIAS", "url": o["url"]}}
                    json.dump(rec, open(os.path.join(out, s + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                    j["issue"] = "identité établie par le SIREN publié sur le site : remplacement"
                    j["slug"] = sl
    journal[s] = j
    print(s, den, "|", j["issue"], flush=True)
    json.dump(journal, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(journal, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import collections
print(collections.Counter(v["issue"] for v in journal.values()).most_common())
