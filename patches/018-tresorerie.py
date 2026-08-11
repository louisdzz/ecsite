# Ecosysteme: six maisons dans Tresorerie & monetaire
#
# Cashbee, Memo Bank, N26, Qonto, Revolut, Trade Republic rejoignent Spiko.
# La categorie passe de 1 a 7 references.
# Au passage, le doublon /f/greenhill-mizuho-2 partait en 404 : retire.
# Total de 4222 a 4227.
# Chaque fiche est generee au format standard, blocs en attente d'interview.
import io, os, sys
from urllib.parse import quote

err = []


def esc(t):
    return t.replace("'", "&#x27;")


# ---------------------------------------------------------------- le gabarit
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

# la question 1 du bloc 1 vise un fonds chez Spiko, une banque chez les six
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

# ---------------------------------------------------------------- les maisons
M = [
    (
        "Cashbee",
        "cashbee",
        "https://www.cashbee.fr",
        "Application d'épargne française avec une offre professionnelle, Cashbee "
        "Pro, qui donne accès à des comptes à terme et à des comptes rémunérés "
        "ouverts auprès de banques partenaires. Usage typique chez nos membres : "
        "placer la trésorerie d'une holding sur des échéances de trois à "
        "trente-six mois.",
    ),
    (
        "Memo Bank",
        "memo-bank",
        "https://memo.bank",
        "Banque française indépendante dédiée aux PME et aux holdings : compte "
        "courant, comptes à terme, crédit, avec un interlocuteur nommé. Usage "
        "typique chez nos membres : la banque du quotidien de la holding, qui "
        "héberge aussi sa trésorerie excédentaire.",
    ),
    (
        "N26",
        "n26",
        "https://n26.com/fr-fr",
        "Banque en ligne allemande, comptes courants et comptes d'épargne "
        "rémunérés en euro, pour les particuliers. Usage typique chez nos "
        "membres : garer la trésorerie personnelle entre deux opérations.",
    ),
    (
        "Qonto",
        "qonto",
        "https://qonto.com/fr",
        "Compte professionnel français pour sociétés et holdings, avec une offre "
        "de placement de trésorerie adossée à des fonds monétaires et à des "
        "comptes à terme. Usage typique chez nos membres : le compte courant de "
        "la holding et le premier support de sa trésorerie.",
    ),
    (
        "Revolut",
        "revolut",
        "https://www.revolut.com/fr-FR/",
        "Groupe bancaire européen, comptes particuliers et professionnels "
        "multi-devises, épargne rémunérée et accès à des fonds monétaires. Usage "
        "typique chez nos membres : rémunérer les liquidités et gérer plusieurs "
        "devises depuis un seul compte.",
    ),
    (
        "Trade Republic",
        "trade-republic",
        "https://traderepublic.com/fr-fr",
        "Courtier allemand accessible aux particuliers, avec rémunération des "
        "liquidités non investies et accès aux fonds monétaires, aux obligations "
        "et aux ETF. Usage typique chez nos membres : garer le cash à côté des "
        "positions cotées.",
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
            err.append(
                "%s : %d occurrence(s) de %s au lieu de %d"
                % (c, t.count(garde), str(garde)[:40], att)
            )
    if err:
        continue
    io.open(c, "w", encoding="utf-8").write(t)
    print("ok fiche %s (%d octets)" % (c, len(t)))

# ---------------------------------------------------------------- la categorie
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


LI = '      <li><a href="/f/%s">%s</a></li>\n'
liste = "".join(LI % (slug, nom) for nom, slug, x, y in
                sorted(M, key=lambda r: r[0].lower()))

sub(
    '<ul class="firms">\n      <li><a href="/f/spiko">Spiko</a></li>\n    </ul>',
    '<ul class="firms">\n'
    + "".join(LI % (sl, nm) for nm, sl in sorted(
        [(n, s2) for n, s2, a, b in M] + [("Spiko", "spiko")],
        key=lambda r: r[0].lower()))
    + "    </ul>",
    1,
)
sub('<div class="count"><b>1</b> référencé</div>',
    '<div class="count"><b>7</b> référencés</div>', 1)

# doublon qui renvoyait vers une fiche inexistante : /f/greenhill-mizuho-2 en 404
# le li de la categorie et l'alias du bandeau pointaient tous deux dans le vide
sub('      <li><a href="/f/greenhill-mizuho-2">Greenhill / Mizuho</a></li>\n', "", 1)
sub('"greenhillmizuho": "greenhill-mizuho-2"',
    '"greenhillmizuho": "greenhill-mizuho"', 1)
sub('<div class="count"><b>41</b> référencés</div>',
    '<div class="count"><b>40</b> référencés</div>', 1)

sub("4222", "4227", 3)
sub("4&nbsp;222", "4&nbsp;227", 2)

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

# ---------------------------------------------------------------- controles
for slug in [r[1] for r in M]:
    if s.count('"/f/%s"' % slug) != 1:
        print("ECHEC lien manquant ou double : /f/" + slug)
        sys.exit(1)
if s.count("4222") or s.count("4&nbsp;222"):
    print("ECHEC ancien total residuel")
    sys.exit(1)
if s.count("4227") != 3 or s.count("4&nbsp;227") != 2:
    print("ECHEC nouveau total incomplet")
    sys.exit(1)
if s.count("greenhill-mizuho-2"):
    print("ECHEC doublon greenhill toujours present")
    sys.exit(1)
if s.count('<div class="count"><b>41</b> référencés</div>'):
    print("ECHEC compteur boutiques M&A non corrige")
    sys.exit(1)
if len(s) <= len(o):
    print("ECHEC page non agrandie")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : 6 maisons, categorie a 7, doublon greenhill retire, total 4227")
