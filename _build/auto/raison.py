#!/usr/bin/env python3
"""Raison du classement : terme employé par la maison sur son site officiel, à défaut dénomination au registre ou catégorie ORIAS."""
import json, glob, re, sys
sys.path.insert(0, '.')
from collecte import get, text
PAT = {"mfo": r"multi[- ]family[- ]office|family[- ]office|family advisory", "cgp": r"conseil(?:ler|lers|s)? en gestion de patrimoine|gestion de patrimoine|gestion priv[ée]e|gestion de fortune|conseil patrimonial"}
for f in sorted(glob.glob((sys.argv[1] if len(sys.argv)>1 else 'donnees')+'/[0-9]*.json')):
    r = json.load(open(f)); r.pop("raison", None); c = r["categorie"]
    m = None
    if r.get("site"):
        u, h = get(r["site"], 15)
        if u:
            m = re.search(PAT[c], text(h), re.I)
            if m:
                r["raison"] = {"texte": "La maison emploie le terme « %s » sur son site officiel." % m.group(0).lower(), "label": "site officiel de la maison", "url": u}
    if not m:
        noms = " ".join(filter(None, [r.get("denomination"), r.get("enseigne")]))
        if c == "mfo" and re.search(r"family office|\bM?FO\b", noms, re.I):
            r["raison"] = {"texte": "Dénomination ou enseigne déclarée au registre : « %s »." % (r["denomination"] if re.search(r"family office|\bM?FO\b", r["denomination"], re.I) else r["enseigne"]), "label": "Annuaire des entreprises (registre)", "url": r["registre_url"]}
        elif c == "cgp" and any(k["code"] == "CIF" and k["etat"] == "Inscrit" for k in (r.get("orias") or {}).get("categories", [])):
            r["raison"] = {"texte": "Inscrite au registre ORIAS en catégorie conseiller en investissements financiers (CIF).", "label": "Registre ORIAS", "url": r["orias"]["url"]}
    json.dump(r, open(f, "w"), ensure_ascii=False, indent=1)
    print(r["nom_usuel"], "|", (r.get("raison") or {}).get("texte"))
