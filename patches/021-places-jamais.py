# Ecosysteme: plus aucune ligne de places, y compris apres une vente
#
# La derniere ligne, celle de la CGP, est retiree. Le gabarit du generateur
# est neutralise pour qu'aucune passe de rebuild ne la reinjecte.
# La barre des regions de la CGP et les 14 CTA restent en place.
import io, os, re, sys

F = "ecosysteme.html"
s = io.open(F, encoding="utf-8").read()
o = s

MOTIF = re.compile(r'[ \t]*<p class="slotline">.*?</p>\n?', re.S)
lignes = MOTIF.findall(s)

if len(lignes) != 1:
    print("ECHEC %d ligne(s) de places au lieu de 1" % len(lignes))
    sys.exit(1)
if "déjà en ligne" not in lignes[0]:
    print("ECHEC la ligne restante n'est pas celle de la CGP")
    sys.exit(1)

s = s.replace(lignes[0], "", 1)

# ------------------------------------------------- le gabarit du generateur
G = os.path.join("_build", "experts-comptables", "gen.py")
gfait = "absent"
if os.path.exists(G):
    g = io.open(G, encoding="utf-8").read()
    m = re.search(r'[ \t]*<!--SLOTS:START--><p class="slotline">.*?'
                  r'<!--SLOTS:END-->\n?', g, re.S)
    if m:
        g = g.replace(m.group(0), "", 1)
        if 'class="slotline"' in g:
            print("ECHEC gabarit slotline residuel dans " + G)
            sys.exit(1)
        io.open(G, "w", encoding="utf-8").write(g)
        gfait = "neutralise"
    else:
        gfait = "gabarit introuvable, rien a faire"

# ------------------------------------------------------------- controles
if MOTIF.findall(s):
    print("ECHEC ligne de places residuelle")
    sys.exit(1)
if 'class="slotline"' in s:
    print("ECHEC classe slotline residuelle dans la page")
    sys.exit(1)
if "restantes sur" in s:
    print("ECHEC mention 'restantes sur' residuelle")
    sys.exit(1)
for balise, att in (
    ('<section class="cat" id=', 14),
    ("<!--SLOTS:START-->", 13),
    ("<!--SLOTS:END-->", 13),
    ('<div class="rbar">', 1),
    ('<a class="linkbtn" href="/fiche-verifiee?cat=', 14),
    ('<ul class="firms">', 14),
    ("<!--SLOTS:START--><div class=\"rbar\">", 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise, att))
        sys.exit(1)
if len(s) >= len(o):
    print("ECHEC page non reduite")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok ligne de places de la CGP retiree")
print("ok gabarit du generateur : %s" % gfait)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : zero ligne de places, 14 CTA, barre des regions intacte")
