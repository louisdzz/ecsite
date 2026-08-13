# Ecosysteme: RockFi passe de la categorie CGP aux Multi-Family Offices
#
# La maison se positionne en multi-family office moderne. Sa ligne quitte
# la liste CGP (3074 -> 3073) et rejoint les MFO (65 -> 66) a sa place
# alphabetique. Sa fiche et la page regionale Ile-de-France suivent.
# Le total du site ne change pas : meme maison, autre rayon.
import io, re, sys

err = []


def sub_in(path, a, b, n):
    s = io.open(path, encoding="utf-8").read()
    c = s.count(a)
    if c != n:
        err.append("%s : %d occurrence(s) au lieu de %d : %s"
                   % (path, c, n, a[:60]))
        return
    io.open(path, "w", encoding="utf-8").write(s.replace(a, b))


# ------------------------------------------------ 1. la page ecosysteme
F = "ecosysteme.html"
s = io.open(F, encoding="utf-8").read()
o = s

LI = '      <li><a href="/f/rockfi">RockFi</a></li>\n'
i_cgp = s.find('id="cgp"')
i_mfo = s.find('id="mfo"')
fin_cgp = s.find("</ul>", i_cgp)
fin_mfo = s.find("</ul>", i_mfo)
if not (0 < i_mfo < i_cgp):
    print("ECHEC ordre des categories inattendu (mfo puis cgp attendu)")
    sys.exit(1)

seg_cgp = s[i_cgp:fin_cgp]
if seg_cgp.count(LI) != 1:
    print("ECHEC %d ligne(s) RockFi dans la categorie CGP" % seg_cgp.count(LI))
    sys.exit(1)

# retrait de la liste CGP
s = s[:i_cgp] + seg_cgp.replace(LI, "", 1) + s[fin_cgp:]

# insertion en place alphabetique dans les MFO : avant Sagis AM,
# apres Requirem (verifie dans le depot au moment de l'ecriture)
i_mfo = s.find('id="mfo"')
fin_mfo = s.find("</ul>", i_mfo)
seg_mfo = s[i_mfo:fin_mfo]
ANCRE = '<li><a href="/f/sagis-am">Sagis AM</a></li>'
if seg_mfo.count(ANCRE) != 1:
    print("ECHEC ancre Sagis AM introuvable dans les MFO")
    sys.exit(1)
seg_mfo = seg_mfo.replace(ANCRE, LI.strip() + "</li>"[0:0] + "\n      " + ANCRE, 1)
s = s[:i_mfo] + seg_mfo + s[fin_mfo:]

# compteurs
def bump(ident, avant, apres):
    global s
    i = s.find('id="%s"' % ident)
    bloc = s[i:i + 2600]
    a = '<div class="count"><b>%d</b>' % avant
    if bloc.count(a) != 1:
        err.append("compteur %s : %d attendu introuvable" % (ident, avant))
        return
    s = s[:i] + bloc.replace(a, '<div class="count"><b>%d</b>' % apres, 1) \
        + s[i + 2600:]


bump("cgp", 3074, 3073)
bump("mfo", 65, 66)

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

# ------------------------------------------------ 2. la fiche
sub_in("f/rockfi.html",
       '<a href="/ecosysteme#cgp">Conseillers en gestion de patrimoine '
       "(CGP)</a>",
       '<a href="/ecosysteme#mfo">Multi-Family Offices</a>', 1)
sub_in("f/rockfi.html",
       '<div class="tagl">Conseillers en gestion de patrimoine (CGP)</div>',
       '<div class="tagl">Multi-Family Offices</div>', 1)

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

# ------------------------------------------------ controles de sortie
t = io.open("f/rockfi.html", encoding="utf-8").read()
if "#cgp" in t or "gestion de patrimoine (CGP)" in t:
    print("ECHEC reference CGP residuelle dans la fiche")
    sys.exit(1)
if t.count("#mfo") != 1 or t.count("Multi-Family Offices") != 2:
    print("ECHEC references MFO inattendues dans la fiche")
    sys.exit(1)

for ident, attendu in (("cgp", 3073), ("mfo", 66)):
    i = s.find('id="%s"' % ident)
    n = s[i:s.find("</ul>", i)].count('<li><a href="/f/')
    c = int(re.search(r'<div class="count"><b>(\d+)</b>', s[i:i + 2600]).group(1))
    if n != attendu or c != attendu:
        print("ECHEC %s : %d ligne(s), compteur %d, attendu %d"
              % (ident, n, c, attendu))
        sys.exit(1)

i_mfo = s.find('id="mfo"')
seg = s[i_mfo:s.find("</ul>", i_mfo)]
# l'ordre existant de la liste MFO n'est pas strictement ASCII (accents) :
# on controle seulement la place de RockFi, entre Requirem et Sagis AM
noms = re.findall(r'<li><a href="/f/([a-z0-9-]+)">', seg)
if not (noms.index("requirem") < noms.index("rockfi") < noms.index("sagis-am")):
    print("ECHEC RockFi mal place dans les MFO")
    sys.exit(1)
if s.count('<li><a href="/f/rockfi">RockFi</a></li>') != 1:
    print("ECHEC RockFi absent ou duplique sur la page")
    sys.exit(1)
if len(re.findall(r'<li><a href="/f/', s)) != len(re.findall(r'<li><a href="/f/', o)):
    print("ECHEC nombre total de lignes modifie")
    sys.exit(1)
if len(s) != len(o):
    print("ECHEC taille de page modifiee : %d -> %d" % (len(o), len(s)))
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok ecosysteme.html : RockFi CGP -> MFO, compteurs 3073 / 66")
print("ok f/rockfi.html : fil d'ariane et etiquette sur Multi-Family Offices")
print("controle vert : ordre alphabetique MFO, totaux inchanges")
