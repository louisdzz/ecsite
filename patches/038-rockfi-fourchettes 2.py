# Ecosysteme: fiche RockFi, fourchettes en euros mises en coherence
#
# L'exemple reel de la maison (31 000 EUR pour 5 M dont 2 M geres)
# tombait sous le plancher affiche pour la tranche 5-15 M (40 000 EUR).
# Les bornes basses sont recalculees sur le modele reel : du patrimoine
# entierement conseille (environ 0,50 %) au patrimoine entierement gere
# au taux de la tranche. La note de calcul est reecrite en consequence.
# Prerequis : patch 037 deja applique.
import io, sys

F = "f/rockfi.html"
s = io.open(F, encoding="utf-8").read()
o = s

if "≈ 25 000 à 120 000 €" in s:
    print("existe deja : fourchettes coherentes, rien a faire")
    sys.exit(0)

R = [
    ("≈ 20 000 à 50 000 €", "≈ 10 000 à 50 000 €"),
    ("≈ 40 000 à 120 000 €", "≈ 25 000 à 120 000 €"),
    ("≈ 90 000 à 300 000 €", "≈ 75 000 à 300 000 €"),
    ("Montants en euros calculés en appliquant "
     "ces taux à la tranche, si la totalité est confiée en actifs "
     "financiers gérés ;",
     "Montants en euros calculés à partir des taux communiqués : la "
     "fourchette va du patrimoine entièrement conseillé (autour de "
     "0,50 %) au patrimoine entièrement géré au taux de la tranche ;"),
]
for a, b in R:
    if s.count(a) != 1:
        print("ECHEC %d occurrence(s) : %s" % (s.count(a), a[:60]))
        sys.exit(1)
for a, b in R:
    s = s.replace(a, b, 1)

for balise, att in (
    ("≈ 10 000 à 50 000 €", 1),
    ("≈ 25 000 à 120 000 €", 1),
    ("≈ 75 000 à 300 000 €", 1),
    ("entièrement conseillé", 1),
    ("31 000 €", 2),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise[:44], att))
        sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : l'exemple reel (31 000 EUR) tient dans sa tranche")
