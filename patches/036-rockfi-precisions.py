# Ecosysteme: fiche RockFi, deux precisions apres relecture
#
# 1. L'a-propos disait "environ 1 500 familles" : la maison a declare
#    1 200 familles dans ses reponses signees du 14/08/2026, le texte
#    s'aligne (le compteur du hero l'etait deja).
# 2. La colonne "Honoraires de mission" passe de "non communique" a
#    "0 EUR" : le modele declare est un honoraire unique sur encours,
#    sans facturation de mission. A faire confirmer par la maison lors
#    de la validation finale de la page.
import io, sys

F = "f/rockfi.html"
s = io.open(F, encoding="utf-8").read()
o = s

if "pour 1 200 familles" in s:
    print("existe deja : precisions en place, rien a faire")
    sys.exit(0)

MISSION = '<td class="pend">non communiqué</td><td><b>'
for a, n in (
    ("pour environ 1 500 familles", 1),
    (MISSION, 5),
    ("honoraires récurrents dégressifs, calculés sur les actifs "
     "financiers gérés ;", 1),
):
    if s.count(a) != n:
        print("ECHEC %d occurrence(s) au lieu de %d : %s"
              % (s.count(a), n, a[:60]))
        sys.exit(1)

s = s.replace("pour environ 1 500 familles", "pour 1 200 familles", 1)
s = s.replace(MISSION, "<td>0 €</td><td><b>", 5)
s = s.replace("honoraires récurrents dégressifs, calculés sur les actifs "
              "financiers gérés ;",
              "honoraires récurrents dégressifs, calculés sur les actifs "
              "financiers gérés, sans honoraires de mission ;", 1)

for balise, att in (
    ("1 500", 0),
    ("pour 1 200 familles", 1),
    ("1 200", 3),
    ("<td>0 €</td>", 5),
    ("non communiqué", 4),
    ("sans honoraires de mission", 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise[:44], att))
        sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : 1 200 familles partout, mission a 0 euro")
