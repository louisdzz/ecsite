# Ecosysteme: fiche RockFi, le detail du calcul s'affiche sous chaque
# montant de la colonne "Tout compris", comme dans l'exemple de la maison
# (patrimoine x taux, borne basse conseillee, borne haute geree).
# Prerequis : patch 038 deja applique.
import io, sys

F = "f/rockfi.html"
s = io.open(F, encoding="utf-8").read()
o = s

if "2 M€ × 1,2 %" in s:
    print("existe deja : detail du calcul present, rien a faire")
    sys.exit(0)

D = ('<small style="display:block;margin-top:2px;font-size:11px;'
     'color:var(--faint)">')
R = [
    ("<td>jusqu’à ≈ 24 000 €</td>",
     "<td>jusqu’à ≈ 24 000 €" + D + "2 M€ × 1,2 %</small></td>"),
    ("<td>≈ 10 000 à 50 000 €</td>",
     "<td>≈ 10 000 à 50 000 €" + D
     + "2 M€ × 0,50 % → 5 M€ × 1 %</small></td>"),
    ("<td>≈ 25 000 à 120 000 €</td>",
     "<td>≈ 25 000 à 120 000 €" + D
     + "5 M€ × 0,50 % → 15 M€ × 0,8 %</small></td>"),
    ("<td>≈ 75 000 à 300 000 €</td>",
     "<td>≈ 75 000 à 300 000 €" + D
     + "15 M€ × 0,50 % → 50 M€ × 0,6 %</small></td>"),
    ("<td>à partir de ≈ 250 000 €</td>",
     "<td>à partir de ≈ 250 000 €" + D
     + "50 M€ × 0,50 %</small></td>"),
]
for a, b in R:
    if s.count(a) != 1:
        print("ECHEC %d occurrence(s) : %s" % (s.count(a), a[:60]))
        sys.exit(1)
for a, b in R:
    s = s.replace(a, b, 1)

for balise, att in (
    ("× 0,50 %", 4),
    ("2 M€ × 1,2 %", 1),
    ("50 M€ × 0,6 %", 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise[:40], att))
        sys.exit(1)
if len(s) <= len(o):
    print("ECHEC page non agrandie")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : chaque montant affiche son calcul")
