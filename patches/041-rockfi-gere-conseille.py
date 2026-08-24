# Ecosysteme: fiche RockFi, la note definit "gere" et "conseille"
#
# Deux definitions seches inserees apres la phrase de formule, pour que
# la grille se lise sans aucun jargon. Formulations a faire valider par
# la maison avec le reste de la page.
# Prerequis : patch 040 deja applique.
import io, sys

F = "f/rockfi.html"
s = io.open(F, encoding="utf-8").read()
o = s

if "dont elle pilote l’allocation" in s:
    print("existe deja : definitions presentes, rien a faire")
    sys.exit(0)
if "part gérée × taux de la tranche" not in s:
    print("ECHEC : deposer d'abord le patch 040")
    sys.exit(1)

A = ("(taux négocié pour l’immobilier et les autres actifs non gérés). "
     "Les montants ci-dessus")
if s.count(A) != 1:
    print("ECHEC %d occurrence(s) de l'ancre" % s.count(A))
    sys.exit(1)

s = s.replace(A,
    "(taux négocié pour l’immobilier et les autres actifs non gérés). "
    "Géré : les actifs financiers confiés à la maison, dont elle pilote "
    "l’allocation au quotidien. Conseillé : tout ce qui reste où il est, "
    "immobilier, participations, comptes détenus ailleurs, sur lequel "
    "elle donne une vision consolidée et des recommandations, sans le "
    "gérer. Les montants ci-dessus", 1)

for balise, att in (
    ("dont elle pilote l’allocation au quotidien", 1),
    ("vision consolidée et des recommandations", 1),
    ("part gérée × taux de la tranche", 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise[:44], att))
        sys.exit(1)
if len(s) <= len(o):
    print("ECHEC page non agrandie")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : gere et conseille definis dans la note")
