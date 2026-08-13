# Ecosysteme: les resultats de recherche remontent sous la barre
#
# 1. pendant une recherche, tout ce qui separait la barre des resultats se
#    masque : le mur de logos, la methodologie, et les deux entetes de bloc.
#    Le premier resultat arrive directement sous le champ.
# 2. le chapeau sous "Je fais quoi de mon argent." est retire.
import io, re, sys

F = "ecosysteme.html"
s = io.open(F, encoding="utf-8").read()
o = s
err = []


def sub(a, b, n):
    global s
    c = s.count(a)
    if c != n:
        err.append("%d occurrence(s) au lieu de %d : %s" % (c, n, a[:70]))
        return
    s = s.replace(a, b)


# ============================ 1. plus rien entre la barre et les resultats
sub("body.searching #ligue-cgp,body.searching #ligues,"
    "body.searching #actualites{display:none}",
    "body.searching #ligue-cgp,body.searching #ligues,"
    "body.searching #actualites,body.searching .wall,"
    "body.searching .metho,body.searching .blocq,"
    "body.searching .apres-h,body.searching .rbar{display:none}\n"
    "body.searching .apres{margin-top:0;padding-top:0;border-top:0}", 1)

# ============================ 2. le chapeau du bloc capital est retire
sub('    <h2 class="disp">Je fais quoi de mon argent.</h2>\n'
    '    <p class="lede">Vous avez quatorze catégories pour vendre, '
    'structurer, placer, réinvestir : banquiers d&#x27;affaires, avocats '
    'fiscalistes, notaires, experts-comptables, family offices, banques '
    'privées, conseillers en gestion de patrimoine, trésorerie, fonds. '
    'L&#x27;ordre est alphabétique, le référencement est gratuit, et être '
    'référencé ne vaut pas recommandation.</p>\n',
    '    <h2 class="disp">Je fais quoi de mon argent.</h2>\n', 1)

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

# ============================ controles de sortie
for balise, att in (
    ("body.searching .wall", 1),
    ("body.searching .metho", 1),
    ("body.searching .blocq", 1),
    ("body.searching .apres-h", 1),
    ("body.searching .rbar", 1),
    ("body.searching .apres{margin-top:0", 1),
    ("Vous avez quatorze catégories", 0),
    ("Je fais quoi de mon argent.", 1),
    ("Je fais quoi de ma vie.", 1),
    ('<div class="blocq" id="argent">', 1),
    ('<p class="over">Le capital</p>', 1),
    ('<p class="over">Le quotidien</p>', 1),
    ('<section class="cat" id=', 15),
    ('<div class="cats">', 2),
    ('<div class="toolbar">', 1),
    ("'searching'", 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise, att))
        sys.exit(1)

# le bloc capital ne garde que son surtitre et son titre
i = s.find('<div class="blocq" id="argent">')
bloc = s[i:s.find("</div>", i) + 6]
if bloc.count("<p") != 1 or bloc.count("<h2") != 1 or "lede" in bloc:
    print("ECHEC entete du bloc capital inattendue :")
    print(bloc[:400])
    sys.exit(1)

if len(re.findall(r'<li><a href="/f/', s)) != len(re.findall(r'<li><a href="/f/', o)):
    print("ECHEC nombre de lignes de maisons modifie")
    sys.exit(1)
if len(s) >= len(o):
    print("ECHEC page non reduite : %d -> %d" % (len(o), len(s)))
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : resultats sous la barre, chapeau du bloc capital retire")
