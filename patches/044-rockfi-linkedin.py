# Ecosysteme: fiche RockFi, les six profils LinkedIn en pastille
#
# Chaque membre de l'equipe recoit une pastille "in" cliquable a cote de
# son nom (profils verifies un a un, tous rattaches a RockFi), a la
# place du lien texte souligne qui occupait sa propre ligne.
# Prerequis : patch 043 deja applique.
import io, sys

F = "f/rockfi.html"
s = io.open(F, encoding="utf-8").read()
o = s

if 'class="lk"' in s:
    print("existe deja : pastilles en place, rien a faire")
    sys.exit(0)
if "Marie Bedu" not in s:
    print("ECHEC : deposer d'abord le patch 043")
    sys.exit(1)

CSS = ('.pers .lk{display:inline-flex;align-items:center;'
       'justify-content:center;width:17px;height:17px;border-radius:4px;'
       'background:#0A66C2;color:#fff;font-size:10.5px;font-weight:700;'
       'text-decoration:none;margin-left:7px;vertical-align:1px;'
       'font-family:Arial,sans-serif;line-height:1}\n')
if s.count("</style>") != 1:
    print("ECHEC style introuvable")
    sys.exit(1)
s = s.replace("</style>", CSS + "</style>", 1)

EQUIPE = (
    ("Pierre Marin", "https://fr.linkedin.com/in/pierre-marin-rockfi"),
    ("Marie Bedu", "https://www.linkedin.com/in/mariebedu/"),
    ("Maxime Durand", "https://fr.linkedin.com/in/durandmaxime"),
    ("Stéphane Carles",
     "https://www.linkedin.com/in/st%C3%A9phane-carles-98a47459/"),
    ("Bertrand Bréavoine",
     "https://www.linkedin.com/in/bertrand-breavoine-053a58150/"),
    ("Yann Garnier", "https://fr.linkedin.com/in/yann-garnier-1308ba90"),
)

# retire l'ancien lien texte de Pierre
ANC = ('<span>Co-fondateur &amp; CEO</span><a href="https://fr.linkedin'
       '.com/in/pierre-marin-rockfi" target="_blank" rel="noopener">'
       'LinkedIn</a>')
if s.count(ANC) != 1:
    print("ECHEC ancien lien Pierre introuvable")
    sys.exit(1)
s = s.replace(ANC, "<span>Co-fondateur &amp; CEO</span>", 1)

for nom, url in EQUIPE:
    a = "<b>" + nom + "</b>"
    if s.count(a) != 1:
        print("ECHEC %d occurrence(s) de %s" % (s.count(a), nom))
        sys.exit(1)
    s = s.replace(a, "<b>" + nom + '<a class="lk" href="' + url
                  + '" target="_blank" rel="noopener" '
                  'aria-label="LinkedIn">in</a></b>', 1)

for balise, att in (
    ('class="lk"', 6),
    ("pierre-marin-rockfi", 1),
    ("mariebedu", 1),
    ("durandmaxime", 1),
    ("breavoine", 1),
    ("yann-garnier-1308ba90", 1),
    (">LinkedIn</a>", 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise[:40], att))
        sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : six pastilles LinkedIn, lien texte retire")
