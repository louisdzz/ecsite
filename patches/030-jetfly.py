# Ecosysteme: Jetfly rejoint la categorie Aviation d'affaires
#
# Huitieme maison de la categorie : propriete partagee sur flotte Pilatus,
# operateur europeen base au Luxembourg. Fiche au format standard clonee du
# gabarit flexjet, liste et compteur de la categorie, page /jets, sitemap.
# Total du site : 4236 -> 4237.
import io, re, sys

err = []

# ------------------------------------------------ 1. la fiche
T = io.open("f/flexjet.html", encoding="utf-8").read()
if io.open("f/flexjet.html", encoding="utf-8").read().count("Flexjet") < 5:
    print("ECHEC gabarit flexjet inattendu")
    sys.exit(1)
import os
if os.path.exists("f/jetfly.html"):
    print("ECHEC f/jetfly.html existe deja")
    sys.exit(1)

REP_OLD_M = re.search(
    r'<div class="card"><div class="k">Repères</div><p>.*?</p>', T, re.S)
if not REP_OLD_M:
    print("ECHEC reperes du gabarit introuvables")
    sys.exit(1)
REP_NEW = ('<div class="card"><div class="k">Repères</div>'
           "<p>Propriété partagée et gestion d'appareils sur "
           "une flotte Pilatus, avec affrètement à la demande, "
           "formation et maintenance intégrées. Opérateur "
           "européen, siège au Luxembourg.</p>")

t = T[:REP_OLD_M.start()] + REP_NEW + T[REP_OLD_M.end():]

SITE_M = re.search(r'<a href="https://www\.flexjet\.com"[^>]*>Site '
                   r"officiel</a>", t)
if not SITE_M:
    print("ECHEC lien site du gabarit introuvable")
    sys.exit(1)
t = (t[:SITE_M.start()]
     + '<a href="https://jetfly.com" target="_blank" rel="noopener nofollow">'
       "Site officiel</a>"
     + t[SITE_M.end():])

if t.count("institution=Flexjet") != 3:
    print("ECHEC parametre institution inattendu")
    sys.exit(1)
t = t.replace("institution=Flexjet", "institution=Jetfly")
t = t.replace("Flexjet", "Jetfly").replace("flexjet", "jetfly")
if "lexjet" in t:
    print("ECHEC residu flexjet")
    sys.exit(1)

for balise, att in (
    ('<h1 class="disp">Jetfly</h1>', 1),
    ('rel="canonical" href="https://www.exit.club/f/jetfly"', 1),
    ('"name": "Jetfly", "url": "https://www.exit.club/f/jetfly"', 1),
    ('<a class="tag" href="/ecosysteme#jets">', 1),
    ('<section class="sect"', 5),
    ("chip-attente", 8),
    ("R&eacute;ponse de Jetfly", 3),
    ("Pilatus", 1),
    ("https://jetfly.com", 1),
):
    if t.count(balise) != att:
        print("ECHEC fiche : %d occurrence(s) de %s au lieu de %d"
              % (t.count(balise), str(balise)[:48], att))
        sys.exit(1)
io.open("f/jetfly.html", "w", encoding="utf-8").write(t)
print("ok fiche f/jetfly.html (%d octets)" % len(t))

# ------------------------------------------------ 2. la page ecosysteme
F = "ecosysteme.html"
s = io.open(F, encoding="utf-8").read()
o = s


def sub(a, b, n):
    global s
    c = s.count(a)
    if c != n:
        err.append("%d occurrence(s) au lieu de %d : %s" % (c, n, a[:70]))
        return
    s = s.replace(a, b)


sub('      <li><a href="/f/lunajets">LunaJets</a></li>\n',
    '      <li><a href="/f/jetfly">Jetfly</a></li>\n'
    '      <li><a href="/f/lunajets">LunaJets</a></li>\n', 1)
i = s.find('id="jets"')
bloc = s[i:i + 2600]
if bloc.count('<div class="count"><b>7</b>') != 1:
    err.append("compteur jets a 7 introuvable")
else:
    s = s[:i] + bloc.replace('<div class="count"><b>7</b>',
                             '<div class="count"><b>8</b>', 1) + s[i + 2600:]
sub("4236", "4237", 3)
sub("4&nbsp;236", "4&nbsp;237", 2)

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

# ------------------------------------------------ 3. la page /jets
J = "jets.html"
j = io.open(J, encoding="utf-8").read()
oj = j
A = "    ['lunajets','LunaJets','Courtier, mise en concurrence des "
A += "opérateurs'],"
if j.count(A) != 1:
    print("ECHEC ligne LunaJets introuvable dans /jets")
    sys.exit(1)
j = j.replace(A,
    "    ['jetfly','Jetfly','Propriété partagée sur flotte "
    "Pilatus'],\n" + A, 1)
j = j.replace("Sept maisons, un standard commun.",
              "Huit maisons, un standard commun.", 1)
j = j.replace("Les sept maisons référencées",
              "Les huit maisons référencées")
j = j.replace("les sept maisons référencées",
              "les huit maisons référencées")
if "sept maisons" in j or j.count("'jetfly'") != 1:
    print("ECHEC page /jets incoherente")
    sys.exit(1)
io.open(J, "w", encoding="utf-8").write(j)
print("ok jets.html : 8 operateurs (%d -> %d octets)" % (len(oj), len(j)))

# ------------------------------------------------ 4. le sitemap
S = "sitemap.xml"
x = io.open(S, encoding="utf-8").read()
URL = "  <url><loc>https://www.exit.club/f/jetfly</loc></url>\n"
if URL in x:
    print("ECHEC jetfly deja au sitemap")
    sys.exit(1)
if x.count("</urlset>") != 1:
    print("ECHEC sitemap sans balise de fin")
    sys.exit(1)
x = x.replace("</urlset>", URL + "</urlset>", 1)
io.open(S, "w", encoding="utf-8").write(x)
print("ok sitemap.xml : /f/jetfly ajoute")

# ------------------------------------------------ controles de sortie
i = s.find('id="jets"')
seg = s[i:s.find("</ul>", i)]
noms = re.findall(r'<li><a href="/f/([a-z0-9-]+)">', seg)
if noms != sorted(noms):
    print("ECHEC ordre alphabetique jets : %s" % noms)
    sys.exit(1)
if len(noms) != 8 or "jetfly" not in noms:
    print("ECHEC liste jets : %s" % noms)
    sys.exit(1)
if s.count("4236") or s.count("4&nbsp;236"):
    print("ECHEC ancien total residuel")
    sys.exit(1)
if len(s) <= len(o):
    print("ECHEC page non agrandie")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : categorie a 8, total 4237" % F)
print("controle vert : fiche, liste, /jets, sitemap")
