# Ecosysteme: la fiche RockFi et les pages regionales suivent la bascule MFO
#
# La fiche renvoyait encore vers "les 871 cabinets de gestion de patrimoine
# en Ile-de-France". RockFi etant desormais un multi-family office :
# 1. sa ligne regionale pointe vers les 66 MFO de la categorie
# 2. sa ligne sort de la page regionale CGP Ile-de-France
# 3. les compteurs 871 passent a 870 sur les 16 pages qui les portent
import glob
import io
import re
import sys

err = []


def sub_in(path, a, b, n):
    s = io.open(path, encoding="utf-8").read()
    c = s.count(a)
    if c != n:
        err.append("%s : %d occurrence(s) au lieu de %d : %s"
                   % (path, c, n, a[:60]))
        return
    io.open(path, "w", encoding="utf-8").write(s.replace(a, b))


# ------------------------------------------------ 1. la ligne de la fiche
sub_in("f/rockfi.html",
       '<p class="rline">Cabinet à <b>Paris</b> · '
       '<a href="/regions/ile-de-france">Voir les 871 cabinets de gestion '
       "de patrimoine en Île-de-France →</a></p>",
       '<p class="rline">Maison à <b>Paris</b> · '
       '<a href="/ecosysteme#mfo">Voir les 66 multi-family offices '
       "recensés →</a></p>", 1)

# ------------------------------------------------ 2. la page regionale CGP
sub_in("regions/ile-de-france.html",
       '<li><a href="/f/rockfi">RockFi</a> <i>Paris</i> <s>✓</s></li>', "", 1)

# ------------------------------------------------ 3. les compteurs 871
# titre, meta, og (x2), lede, kpi, h2 : les 7 occurrences passent a 870
sub_in("regions/ile-de-france.html",
       "871 cabinets de conseil en gestion de patrimoine",
       "870 cabinets de conseil en gestion de patrimoine", 3)
sub_in("regions/ile-de-france.html", "871 cabinets recensés",
       "870 cabinets recensés", 2)
sub_in("regions/ile-de-france.html",
       "<b>871</b><span>cabinets de gestion de patrimoine</span>",
       "<b>870</b><span>cabinets de gestion de patrimoine</span>", 1)
sub_in("regions/ile-de-france.html",
       "Les 871 cabinets de gestion de patrimoine en Île-de-Franc",
       "Les 870 cabinets de gestion de patrimoine en Île-de-Franc", 1)

# la barre inter-regions des 15 pages regionales (index compris)
BARRE_A = "<b>Île-de-France</b><span>871 cabinets</span>"
BARRE_B = "<b>Île-de-France</b><span>870 cabinets</span>"
pages = sorted(glob.glob("regions/*.html"))
if len(pages) != 15:
    print("ECHEC %d page(s) regionale(s) au lieu de 15" % len(pages))
    sys.exit(1)
for p in pages:
    s = io.open(p, encoding="utf-8").read()
    if s.count(BARRE_A) == 1:
        io.open(p, "w", encoding="utf-8").write(s.replace(BARRE_A, BARRE_B))
    elif s.count(BARRE_B) != 1 and p != "regions/ile-de-france.html":
        err.append("%s : barre inter-regions introuvable" % p)

# le sommaire regional de la page ecosysteme
sub_in("ecosysteme.html",
       '<a href="/regions/ile-de-france">Île-de-France<span>871</span></a>',
       '<a href="/regions/ile-de-france">Île-de-France<span>870</span></a>', 1)

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

# ------------------------------------------------ controles de sortie
t = io.open("f/rockfi.html", encoding="utf-8").read()
if "871" in t or "ile-de-france" in t or "gestion de patrimoine" in t:
    print("ECHEC reference CGP ou regionale residuelle dans la fiche")
    sys.exit(1)
if t.count("Voir les 66 multi-family offices") != 1:
    print("ECHEC nouvelle ligne regionale absente")
    sys.exit(1)

r = io.open("regions/ile-de-france.html", encoding="utf-8").read()
if "rockfi" in r:
    print("ECHEC RockFi encore present sur la page regionale")
    sys.exit(1)
if "871" in r:
    print("ECHEC compteur 871 residuel sur la page regionale")
    sys.exit(1)
# la page porte aussi d'autres listes de liens (976 li au total avant
# retrait) : on ne controle que le retrait net d'une seule ligne
n_li = len(re.findall(r'<li><a href="/f/', r))
if n_li != 975:
    print("ECHEC %d ligne(s) listees, 975 attendues apres retrait" % n_li)
    sys.exit(1)

for p in pages:
    if "871" in io.open(p, encoding="utf-8").read():
        print("ECHEC 871 residuel dans " + p)
        sys.exit(1)
e = io.open("ecosysteme.html", encoding="utf-8").read()
if "Île-de-France<span>871</span>" in e:
    print("ECHEC sommaire regional non mis a jour")
    sys.exit(1)

print("ok f/rockfi.html : ligne regionale sur les 66 MFO")
print("ok regions/ile-de-france.html : RockFi retire, 870 cabinets")
print("ok barre inter-regions : 15 pages a 870")
print("controle vert : zero 871 residuel, zero rockfi regional")
