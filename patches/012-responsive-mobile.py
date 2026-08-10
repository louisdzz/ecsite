# Ecosysteme: la page tient dans un ecran de telephone
#
# - la Ligue des CGP vit dans la grille des categories : son tableau large
#   imposait sa largeur a toutes les cartes, la page debordait de 256 px sur
#   mobile (constate au rendu Chromium 390 px, correction mesuree 646 -> 390)
# - min-width:0 sur les elements de la grille, tableaux des Ligues en
#   defilement horizontal sous 760 px, garde-fou overflow-x sur le body
import sys
p = "ecosysteme.html"
s = open(p, encoding="utf-8").read()
A = "</style>"
N = (".cats>*{min-width:0}\n"
     "@media(max-width:760px){body{overflow-x:clip}"
     "#ligue-cgp{overflow-x:auto}"
     ".league table,.league-t table{display:block;overflow-x:auto;"
     "-webkit-overflow-scrolling:touch}}\n")
if s.count(A) != 1 or "min-width:0" in s:
    print("ECHEC etat inattendu"); sys.exit(1)
s = s.replace(A, N + A)
open(p, "w", encoding="utf-8").write(s)
if ".cats>*{min-width:0}" not in s or "overflow-x:clip" not in s:
    print("ECHEC insertion"); sys.exit(1)
print("controle vert : responsive mobile corrige")
