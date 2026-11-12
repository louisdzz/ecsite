#!/usr/bin/env python3
"""Copie dans _build/auto/donnees/ les JSON produits par lot_orias.py, après dédoublonnage par identifiant de fiche.
Rejet si l'identifiant existe déjà (répertoire ou f/) ou si deux sociétés du lot portent le même nom.
Les rejets et les doublons possibles du lot sont ajoutés à donnees/_rejets.json.
Usage : python3 _build/auto/copie_lot.py "<libellé du lot>" <dossier_plage> [<dossier_plage> ...]
"""
import json, glob, os, sys, re, collections, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRANSLIT = str.maketrans({"Æ": "AE", "æ": "ae", "Œ": "OE", "œ": "oe", "ß": "ss", "Ø": "O", "ø": "o", "Ł": "L", "ł": "l", "Đ": "D", "đ": "d"})
def slugify(s):
    s = unicodedata.normalize("NFKD", s.translate(TRANSLIT)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s.replace("&", " ")).strip("-")
lot, dossiers = sys.argv[1], sys.argv[2:]
houses = json.load(open(os.path.join(ROOT, "assets/ecosysteme/maison/data.json"), encoding="utf-8"))["houses"]
pris = {h["slug"] for h in houses} | {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ROOT, "f", "*.html"))}
new = [json.load(open(f, encoding="utf-8")) for d in dossiers for f in sorted(glob.glob(os.path.join(d, "[0-9]*.json")))]
# Une société ayant des établissements dans plusieurs départements sort dans plusieurs plages : un seul enregistrement par SIREN.
new = list({r["siren"]: r for r in new}.values())
vus = collections.defaultdict(list)
for r in new:
    vus[slugify(r["nom_usuel"])].append(r)
pr = os.path.join(ROOT, "_build/auto/donnees/_rejets.json")
rej = json.load(open(pr, encoding="utf-8"))
ok = 0
for sl, lst in vus.items():
    motif = None
    if len(sl) < 2:
        motif = "dénomination inexploitable comme identifiant de fiche"
    elif sl in pris:
        motif = "identifiant déjà pris par une fiche existante : doublon possible, non remplacée"
    elif len(lst) > 1:
        motif = "plusieurs sociétés du lot portent la même dénomination : homonymie non résolue, aucune fiche"
    if motif:
        rej += [{"siren": r["siren"], "nom": r["denomination"], "motif": motif, "lot": lot} for r in lst]
        continue
    r = lst[0]
    json.dump(r, open(os.path.join(ROOT, "_build/auto/donnees", r["siren"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ok += 1
for d in dossiers:
    f = os.path.join(d, "_doublons_possibles.json")
    if os.path.exists(f):
        rej += [dict(x, lot=lot) for x in json.load(open(f, encoding="utf-8"))]
json.dump(rej, open(pr, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("candidats", len(new), "copiés", ok)
