# Ecosysteme: fiche RockFi, la grille revient a la version fourchettes
# avec le detail du calcul sous chaque montant
#
# Le tableau est reconstruit en entier : colonne "Tout compris, en EUR
# / an" avec les fourchettes en euros et, en petit sous chaque montant,
# le calcul (patrimoine x taux). La note garde la formule, les
# definitions gere / conseille et l'exemple signe de la maison.
# S'applique depuis n'importe quel etat precedent (036 a 041).
import io, sys

F = "f/rockfi.html"
s = io.open(F, encoding="utf-8").read()
o = s

if "Tout compris, en € / an</th>" in s and "2 M€ × 1,2 %" in s \
        and "Chaque fourchette va du patrimoine" in s:
    print("existe deja : grille finale en place, rien a faire")
    sys.exit(0)

DEB = '<div style="overflow-x:auto"><table class="grille"'
if s.count(DEB) != 1:
    print("ECHEC %d occurrence(s) du debut de tableau" % s.count(DEB))
    sys.exit(1)
i = s.index(DEB)
j = s.index("</section>", i)
if not (0 < j - i < 4000):
    print("ECHEC section grille de taille inattendue")
    sys.exit(1)

SM = ('<small style="display:block;margin-top:2px;font-size:11px;'
     'color:var(--faint);white-space:nowrap">')
LIGNES = (
    ("&lt; 2 M€", "1,2 %", "jusqu’à ≈ 24 000 €", "2 M€ × 1,2 %"),
    ("2 – 5 M€", "1 %", "≈ 10 000 à 50 000 €",
     "2 M€ × 0,50 % → 5 M€ × 1 %"),
    ("5 – 15 M€", "0,8 %", "≈ 25 000 à 120 000 €",
     "5 M€ × 0,50 % → 15 M€ × 0,8 %"),
    ("15 – 50 M€", "0,6 %", "≈ 75 000 à 300 000 €",
     "15 M€ × 0,50 % → 50 M€ × 0,6 %"),
    ("50 M€ et plus", "0,5 %", "à partir de ≈ 250 000 €",
     "50 M€ × 0,50 %"),
)
t = [DEB + ' style="min-width:560px">',
     "\n        <tr><th>Patrimoine confié</th><th>Honoraires de mission"
     "</th><th>Honoraires récurrents / an</th>"
     "<th>Tout compris, en € / an</th></tr>"]
for deal, taux, mont, calc in LIGNES:
    t.append('\n        <tr><td class="deal">' + deal
             + '</td><td>0 €</td><td><b>' + taux + '</b></td><td>'
             + mont + SM + calc + '</small></td></tr>')
t.append("\n      </table></div>\n      "
         '<p style="margin-top:12px;font-size:12.5px;color:var(--faint)">'
         "Le calcul tient en une ligne : part gérée × taux de la tranche, "
         "plus part conseillée × 0,50 % environ (taux négocié pour "
         "l’immobilier et les autres actifs non gérés). Géré : les actifs "
         "financiers confiés à la maison, dont elle pilote l’allocation "
         "au quotidien. Conseillé : tout ce qui reste où il est, "
         "immobilier, participations, comptes détenus ailleurs, sur "
         "lequel elle donne une vision consolidée et des recommandations, "
         "sans le gérer. Chaque fourchette va du patrimoine entièrement "
         "conseillé (borne basse) au patrimoine entièrement géré (borne "
         "haute) ; votre coût réel se situe entre les deux, selon votre "
         "partage. Exemple réel communiqué par la maison : 5 M€ dont "
         "2 M€ gérés, 16 000 € plus 15 000 €, soit 31 000 € par an. "
         "S’ajoutent les frais d’enveloppe de l’assureur et le coût des "
         "supports, en parts clean shares à prix coûtant ; aucun "
         "honoraire de mission. Grille communiquée par la maison le "
         "14 août 2026.</p>\n    </div>\n  ")
s = s[:i] + "".join(t) + s[j:]

for balise, att in (
    ("Tout compris, en € / an</th>", 1),
    ("2 M€ × 1,2 %", 1),
    ("50 M€ × 0,50 %", 1),
    ("jusqu’à ≈ 24 000 €", 1),
    ("≈ 25 000 à 120 000 €", 1),
    ("à partir de ≈ 250 000 €", 1),
    ("Chaque fourchette va du patrimoine", 1),
    ("dont elle pilote l’allocation au quotidien", 1),
    ("<td>0 €</td>", 5),
    ("Cas type", 0),
    ("non communiqué", 0),
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
print("controle vert : fourchettes + calcul sous chaque montant, note complete")
