# Ecosysteme: compteurs de la page recalcules depuis les listes
#
# - quatre chiffres se contredisaient : 4 225 dans le bandeau, 4226 en somme
#   des compteurs, 4247 dans le titre, la meta et le champ de recherche
# - chaque compteur de categorie est recalcule depuis sa liste
# - le total devient le nombre de maisons distinctes : dix-sept figurent dans
#   deux categories, comptees une fois au total, une fois par categorie
import re, sys
p = "ecosysteme.html"
s = open(p, encoding="utf-8").read()
C = re.findall(r'<section class="cat" id="([^"]+)">(.*?)</ul>', s, re.S)
if len(C) != 13:
    print("ECHEC %d categories" % len(C)); sys.exit(1)
R = r'<div class="count"><b>(\d+)</b> référencés</div>'
g = set()
for a, b in C:
    L = re.findall(r'<li><a href="/f/([^"]+)">', b)
    g |= set(L)
    m = re.search(R, b)
    if not m:
        print("ECHEC compteur %s" % a); sys.exit(1)
    if m.group(1) != str(len(L)):
        s = s.replace(b, b.replace(m.group(0), m.group(0).replace(
            ">%s<" % m.group(1), ">%d<" % len(L))), 1)
        print("ok %s %s -> %d" % (a, m.group(1), len(L)))
T = str(len(g))
n = s.count("4&nbsp;225") + s.count("4247")
if n < 4:
    print("ECHEC %d occurrence(s) du total" % n); sys.exit(1)
s = s.replace("4&nbsp;225", T[:1] + "&nbsp;" + T[1:]).replace("4247", T)
open(p, "w", encoding="utf-8").write(s)
if sum(int(x) for x in re.findall(R, s)) != len(re.findall(r'<li><a href="/f/', s)):
    print("ECHEC somme des compteurs"); sys.exit(1)
print("controle vert : total %s, %d occurrences" % (T, n))
