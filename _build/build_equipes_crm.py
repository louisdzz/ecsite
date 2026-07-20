#!/usr/bin/env python3
# ÉTAPE 2 + 3 : lit les pages brutes du CRM (_build/crm_raw/p*.json),
# parse le rôle depuis Notes, et construit _build/equipes-crm.json au format
#   { "Institution exacte": [ {"nom","role","linkedin"?} ], ... }
# Une seule personne par institution (celle du CRM, première rencontrée).
# Les contacts non identifiés sont écartés.
import json, re, glob, os

ROLE_RE = re.compile(r"enrichi[^(]*\((.+?)[,;)]")
BASE = os.path.dirname(os.path.abspath(__file__))

def parse_role(notes):
    if not notes:
        return "Dirigeant"
    m = ROLE_RE.search(notes)
    if not m:
        return "Dirigeant"
    role = m.group(1).strip()
    return role or "Dirigeant"

def is_unidentified(*vals):
    for v in vals:
        if v and "non identifi" in v.lower():
            return True
    return False

rows = []
for fp in sorted(glob.glob(os.path.join(BASE, "crm_raw", "p*.json"))):
    rows.extend(json.load(open(fp)))

out = {}
skipped = 0
for r in rows:
    inst = (r.get("Institution") or "").strip()
    nom = (r.get("Nom") or "").strip()
    notes = r.get("Notes") or ""
    lk = r.get("LinkedIn")
    if not inst or not nom:
        continue
    role = parse_role(notes)
    if is_unidentified(nom, role):
        skipped += 1
        continue
    if inst in out:      # une seule personne par institution
        continue
    entry = {"nom": nom, "role": role}
    if lk:
        entry["linkedin"] = lk
    out[inst] = [entry]

with open(os.path.join(BASE, "equipes-crm.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print(f"lignes brutes: {len(rows)} | institutions retenues: {len(out)} | ecartees (non identifie): {skipped}")
