# Ecosysteme: fiche RockFi, la colonne "Tout compris, en EUR / an" se remplit
#
# Montants calcules en appliquant les taux communiques par la maison aux
# bornes de chaque tranche, dans le cas ou la totalite est confiee en
# actifs financiers geres. La note sous le tableau le dit explicitement
# et rappelle l'exemple reel (31 000 EUR pour 5 M dont 2 M geres).
# Prerequis : patchs 035 et 036 deja appliques.
import io, sys

F = "f/rockfi.html"
s = io.open(F, encoding="utf-8").read()
o = s

if "jusqu’à ≈ 24 000 €" in s:
    print("existe deja : colonne remplie, rien a faire")
    sys.exit(0)
if "<td>0 €</td>" not in s:
    print("ECHEC : deposer d'abord le patch 036")
    sys.exit(1)

R = [
    ("<td><b>1,2 %</b></td><td>non communiqué</td></tr>",
     "<td><b>1,2 %</b></td><td>jusqu’à ≈ 24 000 €</td></tr>"),
    ("<td><b>1 %</b></td><td>non communiqué</td></tr>",
     "<td><b>1 %</b></td><td>≈ 20 000 à 50 000 €</td></tr>"),
    ("<td><b>0,8 %</b></td><td>≈ 31 000 € pour 5 M€ (détail au bloc "
     "3)</td></tr>",
     "<td><b>0,8 %</b></td><td>≈ 40 000 à 120 000 €</td></tr>"),
    ("<td><b>0,6 %</b></td><td>non communiqué</td></tr>",
     "<td><b>0,6 %</b></td><td>≈ 90 000 à 300 000 €</td></tr>"),
    ("<td><b>0,5 %</b></td><td>non communiqué</td></tr>",
     "<td><b>0,5 %</b></td><td>à partir de ≈ 250 000 €</td></tr>"),
    ("sans honoraires de mission ; le taux sur le reste du patrimoine se "
     "négocie au cas par cas.</p>",
     "sans honoraires de mission ; le taux sur le reste du patrimoine se "
     "négocie au cas par cas. Montants en euros calculés en appliquant "
     "ces taux à la tranche, si la totalité est confiée en actifs "
     "financiers gérés ; hors frais d’enveloppe de l’assureur et coût "
     "des supports, en parts clean shares à prix coûtant. Exemple réel "
     "communiqué par la maison : 31 000 € par an pour un patrimoine de "
     "5 M€ dont 2 M€ gérés (réponse détaillée au bloc 3).</p>"),
]

for a, b in R:
    if s.count(a) != 1:
        print("ECHEC %d occurrence(s) : %s" % (s.count(a), a[:60]))
        sys.exit(1)
for a, b in R:
    s = s.replace(a, b, 1)

for balise, att in (
    ("non communiqué", 0),
    ("jusqu’à ≈ 24 000 €", 1),
    ("à partir de ≈ 250 000 €", 1),
    ("31 000 €", 2),
    ("clean shares à prix coûtant", 2),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise[:44], att))
        sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : colonne tout compris remplie, note de calcul posee")
