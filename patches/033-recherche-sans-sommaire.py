# Ecosysteme: pendant une recherche, les resultats collent a la barre
#
# Le sommaire des quinze categories (trois lignes de liens) restait affiche
# entre la barre et les resultats : le premier resultat partait a mi-ecran,
# et les suivants sous le pli. Pendant la frappe, le sommaire se masque et
# tout remonte. Il revient des que le champ se vide.
import io, sys

F = "ecosysteme.html"
s = io.open(F, encoding="utf-8").read()
o = s

A = ("body.searching #ligue-cgp,body.searching #ligues,"
     "body.searching #actualites,body.searching .wall,"
     "body.searching .metho,body.searching .blocq,"
     "body.searching .apres-h,body.searching .rbar{display:none}")
B = ("body.searching #ligue-cgp,body.searching #ligues,"
     "body.searching #actualites,body.searching .wall,"
     "body.searching .metho,body.searching .blocq,"
     "body.searching .apres-h,body.searching .rbar,"
     "body.searching .jump{display:none}\n"
     "body.searching .cats{margin-top:6px}")

if s.count(A) != 1:
    print("ECHEC regle de masquage introuvable")
    sys.exit(1)
s = s.replace(A, B, 1)

for balise, att in (
    ("body.searching .jump", 1),
    ("body.searching .cats{margin-top:6px}", 1),
    ('class="jump"', 1),
    ("'searching'", 1),
    ('<div class="toolbar">', 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise, att))
        sys.exit(1)
if len(s) <= len(o):
    print("ECHEC page non agrandie")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : sommaire masque pendant la recherche")
