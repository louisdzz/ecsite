# Ecosysteme: Byzantine et Regular dans Tresorerie & monetaire
#
# Deux acteurs du rendement sur actifs numeriques, cibles trésoreries
# d'entreprises et family offices. La categorie passe de 7 a 9, total 4229.
# La description de la categorie s'elargit pour couvrir cette classe de produit.
import io, os, sys
from urllib.parse import quote

err = []


def esc(t):
    return t.replace("'", "&#x27;")


T = io.open("f/spiko.html", encoding="utf-8").read()

REPERES_OLD = (
    "<p>Fonds monétaires tokenisés en euro et en dollar, souscrits par "
    "des sociétés comme par des particuliers, avec intérêts "
    "calculés quotidiennement et retraits rapides. Le panier est valorisé "
    "par une société de gestion et logé hors bilan de la plateforme. "
    "Usage typique chez nos membres : garer la trésorerie d&#x27;une holding "
    "entre la cession et le réinvestissement.</p>"
)
LIENS_OLD = (
    '<p style="margin-top:10px;font-size:13px">'
    '<a href="https://www.spiko.io" target="_blank" rel="noopener nofollow">'
    "Site officiel</a> · "
    '<a href="https://www.linkedin.com/company/spiko-eu/" target="_blank" '
    'rel="noopener nofollow">LinkedIn</a></p>'
)
LIENS_NEW = (
    '<p style="margin-top:10px;font-size:13px">'
    '<a href="%s" target="_blank" rel="noopener nofollow">Site officiel</a></p>'
)
STATUT_OLD = (
    "<small>Agrément AMF, société de gestion, dépositaire : les trois noms, "
    "et le numéro d&#x27;agrément.</small>"
)
STATUT_NEW = (
    "<small>Agrément bancaire ou statut d&#x27;établissement, autorité de "
    "tutelle, numéro d&#x27;agrément, et qui conserve les fonds.</small>"
)

for x in (REPERES_OLD, LIENS_OLD, STATUT_OLD):
    if T.count(x) != 1:
        err.append("gabarit : %d occurrence(s) de %s" % (T.count(x), x[:50]))

M = [
    (
        "Byzantine",
        "byzantine",
        "https://www.byzantine.fi/fr",
        "Comptes rémunérés en stablecoins destinés aux trésoreries "
        "d'entreprises, aux family offices et aux plateformes, avec intérêts "
        "versés chaque heure et retraits dans l'heure. Une variante assurée est "
        "proposée à un taux inférieur. La maison déclare ne pas être une banque "
        "et ne pas conserver les actifs : le routage des fonds passe par des "
        "contrats intelligents et par un partenaire régulé sous MiCA.",
    ),
    (
        "Regular",
        "regular",
        "https://www.regular.eu/",
        "Compte de placement en actifs numériques adossé à des parts de pools de "
        "liquidité, avec intérêts versés quotidiennement, ouvert aux "
        "particuliers, aux sociétés, aux conseillers en gestion de patrimoine et "
        "aux family offices. Regular Finance SAS se déclare enregistrée comme "
        "prestataire de services sur actifs numériques auprès de l'AMF sous le "
        "numéro E2023-72, les actifs étant conservés hors de son bilan chez un "
        "dépositaire tiers.",
    ),
]

for nom, slug, site, rep in M:
    c = os.path.join("f", slug + ".html")
    if os.path.exists(c):
        err.append("existe deja : " + c)
        continue
    t = T.replace(REPERES_OLD, "<p>" + esc(rep) + "</p>")
    t = t.replace(LIENS_OLD, LIENS_NEW % site)
    t = t.replace(STATUT_OLD, STATUT_NEW)
    if t.count("institution=Spiko") != 3:
        err.append("gabarit : parametre institution introuvable")
        break
    t = t.replace("institution=Spiko", "institution=@@INST@@")
    t = t.replace("Spiko", nom).replace("spiko", slug)
    t = t.replace("@@INST@@", quote(nom))
    if "Spiko" in t or "spiko" in t:
        err.append("residu Spiko dans " + c)
        continue
    for garde, att in (
        ('<nav class="toc">', 1),
        ('<a class="tag" href="/ecosysteme#treso">', 1),
        ('<section class="sect"', 5),
        ("chip-attente", 8),
        ('<h1 class="disp">%s</h1>' % nom, 1),
        ('rel="canonical" href="https://www.exit.club/f/%s"' % slug, 1),
        ('og:url" content="https://www.exit.club/f/%s"' % slug, 1),
        ('"name": "%s", "url": "https://www.exit.club/f/%s"' % (nom, slug), 1),
        ("institution=" + quote(nom), 3),
        (STATUT_NEW, 1),
        (STATUT_OLD, 0),
    ):
        if t.count(garde) != att:
            err.append("%s : %d occurrence(s) de %s au lieu de %d"
                       % (c, t.count(garde), str(garde)[:40], att))
    if err:
        continue
    io.open(c, "w", encoding="utf-8").write(t)
    print("ok fiche %s (%d octets)" % (c, len(t)))

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


sub(
    '      <li><a href="/f/cashbee">Cashbee</a></li>\n',
    '      <li><a href="/f/byzantine">Byzantine</a></li>\n'
    '      <li><a href="/f/cashbee">Cashbee</a></li>\n',
    1,
)
sub(
    '      <li><a href="/f/revolut">Revolut</a></li>\n',
    '      <li><a href="/f/regular">Regular</a></li>\n'
    '      <li><a href="/f/revolut">Revolut</a></li>\n',
    1,
)
sub('<div class="count"><b>7</b> référencés</div>',
    '<div class="count"><b>9</b> référencés</div>', 1)
sub("comptes à terme, fonds monétaires, monétaire tokenisé.",
    "comptes à terme, fonds monétaires, monétaire tokenisé, rendement sur "
    "actifs numériques.", 1)
sub("4227", "4229", 3)
sub("4&nbsp;227", "4&nbsp;229", 2)

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

# ------------------------------------------------------------- controles
i = s.find('id="treso"')
bloc = s[i:s.find("</ul>", i)]
attendu = ["byzantine", "cashbee", "memo-bank", "n26", "qonto", "regular",
           "revolut", "spiko", "trade-republic"]
trouve = [x.split('">')[0] for x in bloc.split('<li><a href="/f/')[1:]]
if trouve != attendu:
    print("ECHEC ordre alphabetique casse :")
    print("  " + " ".join(trouve))
    sys.exit(1)
for slug in [r[1] for r in M]:
    if s.count('"/f/%s"' % slug) != 1:
        print("ECHEC lien manquant ou double : /f/" + slug)
        sys.exit(1)
if s.count("4227") or s.count("4&nbsp;227"):
    print("ECHEC ancien total residuel")
    sys.exit(1)
if s.count("4229") != 3 or s.count("4&nbsp;229") != 2:
    print("ECHEC nouveau total incomplet")
    sys.exit(1)
if len(s) <= len(o):
    print("ECHEC page non agrandie")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : Byzantine et Regular ajoutes, categorie a 9, total 4229")
