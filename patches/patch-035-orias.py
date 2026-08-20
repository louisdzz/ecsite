# Ecosysteme: retirer le faux ORIAS 24003039 des fiches
# - 66 fiches: meme numero + tampon registre public
# - remplace par a confirmer sur pieces, sans chip registre

import pathlib, sys
OLD = "<div class=\"etq\"><div class=\"q\">Statuts réglementaires<small>CIF · ORIAS n° 24003039 · membre CNCGP (association agréée par l'AMF).</small></div><span class=\"chip-source\">✓ Registre public</span></div>"
NEW = "<div class=\"etq\"><div class=\"q\">Statuts réglementaires<small>À confirmer sur pièces (ORIAS, association professionnelle).</small></div><span class=\"chip-attente\">Interview sans filtre à venir</span></div>"
root = pathlib.Path("f")
if not root.is_dir():
    print("ECHEC: dossier f/ absent"); sys.exit(1)
hits = [p for p in sorted(root.glob("*.html")) if "24003039" in p.read_text(encoding="utf-8")]
if not hits:
    print("existe deja"); sys.exit(0)
for p in hits:
    t = p.read_text(encoding="utf-8")
    n = t.count(OLD)
    if n != 1:
        print(f"ECHEC: {p.name} occurrences={n}"); sys.exit(1)
    p.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
left = [q.name for q in root.glob("*.html") if "24003039" in q.read_text(encoding="utf-8")]
if left:
    print("ECHEC: reste", ",".join(left)); sys.exit(1)
print(f"ok {len(hits)} fiches")
