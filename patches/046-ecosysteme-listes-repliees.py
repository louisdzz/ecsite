# Ecosysteme: chaque categorie replie sa liste derriere un bouton
# "Afficher les N autres"
#
# Les quinze categories affichaient leur annuaire entier en dur, 4 254
# noms d'un coup dont 3 073 CGP : 63 ecrans de scroll en desktop, 173
# sur mobile. Chaque liste ne montre plus que ses 30 premiers noms
# (12 sur mobile), le reste se deroule au clic. Les petites categories
# restent entieres. La recherche continue de couvrir tout : des qu'on
# tape, le repli se leve (via body.searching, deja en place). Tous les
# liens restent dans le HTML, rien ne change pour le SEO.
import io, sys

F = "ecosysteme.html"
s = io.open(F, encoding="utf-8").read()
o = s

if "li.xcap" in s:
    print("existe deja : listes repliees en place, rien a faire")
    sys.exit(0)

for balise, att in (
    ("</style>", 1),
    ("</body>", 1),
    ('class="firms"', 15),
    ("toggle('searching',!!v)", 1),
    (".firms li.hidden{display:none}", 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise[:40], att))
        sys.exit(1)

CSS = (
    ".firms li.xcap{display:none}\n"
    "body.searching .firms li.xcap{display:list-item}\n"
    "body.searching .firms li.hidden{display:none}\n"
    "body.searching .voirplus{display:none}\n"
    ".voirplus{margin-top:14px;display:inline-block;font-size:13px;"
    "font-weight:600;color:var(--accent);background:none;"
    "border:1px solid var(--accent);border-radius:999px;"
    "padding:7px 16px;cursor:pointer;font-family:inherit}\n"
    ".voirplus:hover{background:var(--accent);color:#fff}\n")
s = s.replace("</style>", CSS + "</style>", 1)

JS = (
    "<script>\n"
    "(function(){\n"
    "  var N=matchMedia('(max-width:760px)').matches?12:30;\n"
    "  document.querySelectorAll('section.cat ul.firms')"
    ".forEach(function(ul){\n"
    "    var lis=[].slice.call(ul.querySelectorAll('li'));\n"
    "    if(lis.length<=N+8)return;\n"
    "    var extra=lis.slice(N);\n"
    "    extra.forEach(function(li){li.classList.add('xcap')});\n"
    "    var b=document.createElement('button');\n"
    "    b.className='voirplus';b.type='button';\n"
    "    b.textContent='Afficher les '+extra.length+' autres';\n"
    "    b.addEventListener('click',function(){\n"
    "      extra.forEach(function(li){li.classList.remove('xcap')});\n"
    "      b.remove();\n"
    "    });\n"
    "    ul.parentNode.insertBefore(b,ul.nextSibling);\n"
    "  });\n"
    "})();\n"
    "</script>\n")
s = s.replace("</body>", JS + "</body>", 1)

for balise, att in (
    ("li.xcap", 2),
    ("display:list-item", 1),
    (".voirplus", 3),
    ("'voirplus'", 1),
    ("Afficher les ", 1),
    ("N+8", 1),
    ("</style>", 1),
    ("</body>", 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise[:40], att))
        sys.exit(1)
if len(s) <= len(o):
    print("ECHEC page non agrandie")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : listes repliees a 30 (12 mobile), recherche intacte")
