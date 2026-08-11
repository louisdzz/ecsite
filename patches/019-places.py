# Ecosysteme: retrait des lignes de places non entamees
#
# Treize categories affichaient "N places restantes sur N", ce qui annoncait
# publiquement qu'aucune place n'avait ete vendue. Ces lignes sont retirees.
# La CGP conserve la sienne : elle porte "1 deja en ligne", seule preuve utile.
# Les marqueurs SLOTS, la barre des regions et les CTA restent en place.
import io, re, sys

F = "ecosysteme.html"
s = io.open(F, encoding="utf-8").read()
o = s

MOTIF = re.compile(r'[ \t]*<p class="slotline">.*?</p>\n?', re.S)
lignes = MOTIF.findall(s)

if len(lignes) != 14:
    print("ECHEC %d ligne(s) de places au lieu de 14" % len(lignes))
    sys.exit(1)

garde = [x for x in lignes if "déjà en ligne" in x]
retire = [x for x in lignes if "déjà en ligne" not in x]

if len(garde) != 1:
    print("ECHEC %d ligne(s) portant une place vendue au lieu de 1" % len(garde))
    sys.exit(1)
if len(retire) != 13:
    print("ECHEC %d ligne(s) a retirer au lieu de 13" % len(retire))
    sys.exit(1)

for x in retire:
    if s.count(x) < 1:
        print("ECHEC ligne introuvable : " + re.sub(r"<[^>]+>", "", x)[:60])
        sys.exit(1)
    s = s.replace(x, "", 1)

# ------------------------------------------------------------- controles
restantes = MOTIF.findall(s)
if len(restantes) != 1 or "déjà en ligne" not in restantes[0]:
    print("ECHEC %d ligne(s) restante(s), attendu la seule CGP" % len(restantes))
    sys.exit(1)
if s.replace(restantes[0], "").count("restantes sur"):
    print("ECHEC mention 'restantes sur' residuelle hors CGP")
    sys.exit(1)
for balise, att in (
    ('<section class="cat" id=', 14),
    ("<!--SLOTS:START-->", 13),
    ("<!--SLOTS:END-->", 13),
    ('<div class="rbar">', 1),
    ('<a class="linkbtn" href="/fiche-verifiee?cat=', 14),
    ('<ul class="firms">', 14),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise, att))
        sys.exit(1)
if "<!--SLOTS:START--><!--SLOTS:END-->" not in s:
    print("ECHEC les blocs vides ne se sont pas refermes comme prevu")
    sys.exit(1)
if len(s) >= len(o):
    print("ECHEC page non reduite")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok 13 lignes de places retirees, la CGP conserve la sienne")
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : 14 categories, 14 CTA de profil verifie, barre des regions intacte")
