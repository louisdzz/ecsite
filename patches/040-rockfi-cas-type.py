# Ecosysteme: fiche RockFi, la colonne en euros devient un cas type
# par million, et la note donne la formule
#
# Le tableau de la grille est reconstruit en entier : mission a 0 EUR,
# taux de tranche, et une colonne "Cas type, en EUR par M confie / an"
# calculee sur le partage de l'exemple reel de la maison (40 % gere,
# 60 % conseille a 0,50 %). La note explique le calcul en une ligne et
# retrace l'exemple signe (31 000 EUR pour 5 M, soit 6 200 EUR par M).
# Ce patch remplace les patchs 037, 038 et 039, deposes ou non : il
# s'applique indifferemment depuis l'etat 036 ou apres eux.
import io, sys

F = "f/rockfi.html"
s = io.open(F, encoding="utf-8").read()
o = s

if "Cas type, en € par M€" in s:
    print("existe deja : colonne cas type en place, rien a faire")
    sys.exit(0)

DEB = '<div style="overflow-x:auto"><table class="grille"'
if s.count(DEB) != 1:
    print("ECHEC %d occurrence(s) du debut de tableau" % s.count(DEB))
    sys.exit(1)
i = s.index(DEB)
j = s.index("</section>", i)
if not (0 < j - i < 3000):
    print("ECHEC section grille de taille inattendue")
    sys.exit(1)

LIGNES = (
    ("&lt; 2 M€", "1,2 %", "7 800 €"),
    ("2 – 5 M€", "1 %", "7 000 €"),
    ("5 – 15 M€", "0,8 %", "6 200 €"),
    ("15 – 50 M€", "0,6 %", "5 400 €"),
    ("50 M€ et plus", "0,5 %", "5 000 €"),
)
t = [DEB + ' style="min-width:560px">',
     "\n        <tr><th>Patrimoine confié</th><th>Honoraires de mission"
     "</th><th>Honoraires récurrents / an</th>"
     "<th>Cas type, en € par M€ / an</th></tr>"]
for deal, taux, cas in LIGNES:
    t.append('\n        <tr><td class="deal">' + deal
             + '</td><td>0 €</td><td><b>' + taux + '</b></td><td><b>'
             + cas + '</b></td></tr>')
t.append("\n      </table></div>\n      "
         '<p style="margin-top:12px;font-size:12.5px;color:var(--faint)">'
         "Le calcul tient en une ligne : part gérée × taux de la tranche, "
         "plus part conseillée × 0,50 % environ (taux négocié pour "
         "l’immobilier et les autres actifs non gérés). Les montants "
         "ci-dessus reprennent le partage de l’exemple réel communiqué "
         "par la maison, 40 % géré et 60 % conseillé : 5 M€ dont 2 M€ "
         "gérés, 16 000 € plus 15 000 €, soit 31 000 € par an, 6 200 € "
         "par M€. Votre partage est différent ? La formule vous donne "
         "votre chiffre. S’ajoutent les frais d’enveloppe de l’assureur "
         "et le coût des supports, en parts clean shares à prix coûtant ; "
         "aucun honoraire de mission. Grille communiquée par la maison le "
         "14 août 2026.</p>\n    </div>\n  ")
s = s[:i] + "".join(t) + s[j:]

for balise, att in (
    ("Cas type, en € par M€ / an", 1),
    ("7 800 €", 1),
    ("6 200 €", 2),
    ("<b>5 000 €</b>", 1),
    ("part gérée × taux de la tranche", 1),
    ("<td>0 €</td>", 5),
    ("non communiqué", 0),
    ("La colonne qui compte", 0),
    ("31 000 €", 2),
    ('<table class="grille"', 1),
    ("</table>", 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise[:44], att))
        sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : cas type par million, formule dans la note")
