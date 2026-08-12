# Ecosysteme: les deux questions qu'on se pose une fois qu'on a vendu
#
# L'annuaire s'organise desormais sur les deux questions du fondateur qui
# vient de vendre, et non sur une chronologie avant/apres cession :
#   bloc 1  Je fais quoi de mon argent.   (14 categories, le capital)
#   bloc 2  Je fais quoi de ma vie.       (les categories de service)
# L'ancre du bloc 2 passe de #apres a #vie. Rien ne pointait sur #apres.
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


# ---------------------------------------------- l'entete du premier bloc
ARGENT = (
    '  <div class="blocq" id="argent">\n'
    '    <p class="over">Le capital</p>\n'
    '    <h2 class="disp">Je fais quoi de mon argent.</h2>\n'
    "    <p class=\"lede\">Vous avez quatorze catégories pour vendre, "
    "structurer, placer, réinvestir : banquiers d&#x27;affaires, avocats "
    "fiscalistes, notaires, experts-comptables, family offices, banques "
    "privées, conseillers en gestion de patrimoine, trésorerie, fonds. "
    "L&#x27;ordre est alphabétique, le référencement est gratuit, et être "
    "référencé ne vaut pas recommandation.</p>\n"
    "  </div>\n\n"
)

sub("  </details>\n\n  <div class=\"cats\">\n",
    "  </details>\n\n" + ARGENT + "  <div class=\"cats\">\n", 1)

# ---------------------------------------------- l'entete du second bloc
sub('<div class="apres" id="apres">\n    <div class="apres-h">\n'
    '      <p class="over">Après la cession</p>\n'
    '      <h2 class="disp">Qui vous sert, une fois l&#x27;argent '
    'encaissé.</h2>\n'
    '      <p class="lede">Les quatorze catégories ci-dessus recensent ceux '
    'qui conseillent la vente et le capital. Celles-ci recensent ceux que les '
    'fondateurs appellent après, sous le même standard : les mêmes blocs, les '
    'mêmes questions, les mêmes chiffres à assumer.</p>\n'
    '    </div>\n',
    '<div class="apres" id="vie">\n    <div class="apres-h">\n'
    '      <p class="over">La suite</p>\n'
    '      <h2 class="disp">Je fais quoi de ma vie.</h2>\n'
    '      <p class="lede">Vous récupérez d&#x27;un coup tout le temps que '
    'l&#x27;entreprise prenait, et personne ne vous y a préparé. Cette moitié '
    'de l&#x27;Écosystème recense ceux qui reprennent la main sur le concret : '
    'le temps de trajet, l&#x27;école des enfants, la maison, le corps, le '
    'personnel. Mêmes blocs, mêmes questions posées, même standard.</p>\n'
    '    </div>\n', 1)

# ---------------------------------------------- le style de l'entete
sub("</style>",
    ".blocq{max-width:680px;margin:8px 0 26px}\n"
    ".blocq h2{font-size:32px;line-height:1.08;margin-top:6px}\n"
    ".blocq .lede{font-size:15px;color:var(--muted);margin-top:14px;"
    "line-height:1.6}\n"
    "@media(max-width:760px){.blocq h2,.apres-h h2{font-size:26px}}\n"
    "</style>", 1)

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

# ---------------------------------------------- controles de sortie
for balise, att in (
    ('id="argent"', 1),
    ('id="vie"', 1),
    ('id="apres"', 0),
    ('href="#apres"', 0),
    ("Je fais quoi de mon argent.", 1),
    ("Je fais quoi de ma vie.", 1),
    ("Après la cession", 0),
    ("Qui vous sert, une fois l&#x27;argent encaissé.", 0),
    ('<div class="cats">', 2),
    ('<div class="blocq"', 1),
    ('<div class="apres-h">', 1),
    (".blocq{max-width:680px", 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise, att))
        sys.exit(1)

# l'entete du capital doit precéder la premiere grille, celle de la vie la seconde
i_arg = s.find('id="argent"')
i_g1 = s.find('<div class="cats">')
i_vie = s.find('id="vie"')
i_g2 = s.find('<div class="cats">', i_g1 + 1)
if not (i_arg < i_g1 < i_vie < i_g2):
    print("ECHEC ordre des blocs casse : %d %d %d %d" % (i_arg, i_g1, i_vie, i_g2))
    sys.exit(1)

if len(re.findall(r'<section class="cat" id="[a-z-]+"', s)) != 15:
    print("ECHEC nombre de categories inattendu")
    sys.exit(1)
if len(re.findall(r'<h2 class="disp">Je fais quoi', s)) != 2:
    print("ECHEC les deux questions ne sont pas en h2")
    sys.exit(1)
if len(s) <= len(o):
    print("ECHEC page non agrandie")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : deux blocs, deux questions, ancres #argent et #vie")
