# Ecosysteme: la fiche RockFi passe au format standard a cinq blocs
#
# Reconstruite sur le gabarit MFO (clone de senja-partners), en greffant tout
# ce que le profil verifie portait deja : badge 2026, stats, a-propos, equipe,
# actualites. Les cinq blocs arrivent en attente, prets a recevoir les
# reponses du kickoff du 3 septembre (formulaire Tally MFO).
# Le bouton "Repondre aux questions" pointe vers le Tally pre-rempli.
import io, re, sys

err = []
T = io.open("f/senja-partners.html", encoding="utf-8").read()
OLD = io.open("f/rockfi.html", encoding="utf-8").read()

if '<nav class="toc">' in OLD:
    print("ECHEC f/rockfi.html est deja au format standard")
    sys.exit(1)
if T.count("Senja Partners") != 10 or T.count("senja-partners") != 12:
    print("ECHEC gabarit senja-partners inattendu")
    sys.exit(1)


def graft(old, motif, nom):
    m = re.search(motif, old, re.S)
    if not m:
        err.append("greffe introuvable : " + nom)
        return ""
    return m.group(0)


# ------------------------------------------ pieces reprises du profil verifie
HERO = graft(OLD, r'<section class="hero">.*?</section>', "hero verifie")
RLINE = graft(OLD, r'<!--RLINE:START-->.*?<!--RLINE:END-->', "ligne regionale")
STATS = graft(OLD, r'<div class="stats">(?:\s*<div class="stat">.*?'
              r'</div>)+\s*</div>', "stats")
APROPOS = graft(OLD, r'<div class="card"><div class="k">À propos</div>.*?'
                     r'</p></div>', "a propos")
EQUIPE = graft(OLD, r'<div class="card"><div class="k">L\'équipe</div>.*?'
                    r'Associée</span></div></div></div>', "equipe")
OPP = graft(OLD, r'<div class="opp"><div class="opp-h">.*?</p></div>',
            "opportunite")
ACTUS = graft(OLD, r'<div class="card"><div class="k">Actualités & '
                   r'opérations</div>.*?maison\.</span></div></div>', "actus")

# le css du profil verifie dont le gabarit ne dispose pas
CSSOLD = OLD[OLD.find("<style>"):OLD.find("</style>")]
CSS = []
for cls in [r"\.logo\{", r"\.vbadge\{", r"\.fresh\{", r"\.fresh i\{",
            r"\.stats\{", r"\.stat\{", r"\.stat b\{", r"\.stat span\{",
            r"\.rline\{", r"\.rline a\{", r"\.rline b\{",
            r"\.arow\{", r"\.adate\{", r"\.xp\{",
            r"\.opp\{", r"\.opp-h\{", r"\.opp-k\{", r"\.opp-date\{",
            r"\.opp b\{", r"\.opp p\{"]:
    m = re.search(cls[:-2].replace("\\", "") and cls + r"[^}]*\}", CSSOLD)
    if m:
        CSS.append(m.group(0))
CSS.append(".hero{display:flex;gap:22px;align-items:center}")
if len(CSS) < 14:
    err.append("css du profil verifie incomplet : %d regle(s)" % len(CSS))

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

# ------------------------------------------ le nouveau document
s = T

# identite : senja -> rockfi
s = s.replace("https://www.senja-partners.com", "https://www.rockfi.fr")
s = s.replace("senja-partners.com", "rockfi.fr")
s = s.replace(
    "https://www.linkedin.com/search/results/companies/"
    "?keywords=Senja%20Partners",
    "https://www.linkedin.com/company/rockfi/")
s = s.replace("Senja%20Partners", "RockFi")
s = s.replace("senja-partners", "rockfi")
s = s.replace("Senja Partners", "RockFi")
if "enja" in s:
    print("ECHEC residu senja")
    sys.exit(1)

# le hero du gabarit cede la place au hero verifie + rline + stats
m = re.search(r'<section class="hero wl">.*?</section>', s, re.S)
if not m:
    print("ECHEC hero du gabarit introuvable")
    sys.exit(1)
s = s[:m.start()] + HERO + "\n\n  " + RLINE + "\n  " + STATS + s[m.end():]

# reperes -> a propos complet du profil verifie
m = re.search(r'<div class="card"><div class="k">Repères</div>.*?</p></div>',
              s, re.S)
if not m:
    print("ECHEC carte Reperes introuvable")
    sys.exit(1)
# le lien vers le site et le LinkedIn, que la carte a-propos ne portait pas
LIENS = ('<p style="margin-top:10px;font-size:13px">'
         '<a class="sitel" href="https://www.rockfi.fr" target="_blank" '
         'rel="noopener">rockfi.fr</a> · '
         '<a href="https://www.linkedin.com/company/rockfi/" target="_blank" '
         'rel="noopener">LinkedIn</a></p>')
if not APROPOS.endswith("</p></div>"):
    print("ECHEC fin de la carte a-propos inattendue")
    sys.exit(1)
APROPOS2 = APROPOS[:-6] + LIENS + "</div>"
s = s[:m.start()] + APROPOS2 + "\n  " + OPP + s[m.end():]

# equipe recherchee -> equipe fournie par la maison
m = re.search(r'<div class="card"><div class="k">Équipe dirigeante</div>'
              r'.*?Écrivez-moi</a></p></div>', s, re.S)
if not m:
    print("ECHEC carte equipe introuvable")
    sys.exit(1)
s = s[:m.start()] + EQUIPE + s[m.end():]

# le statut "Profil référencé · non revendiqué" vivait dans le hero du
# gabarit : il est parti avec lui, le hero verifie porte deja le badge 2026

# actualites apres le bloc 5, avant l'encart
i = s.find('<div class="gap">')
if i < 0:
    print("ECHEC encart gap introuvable")
    sys.exit(1)
s = s[:i] + ACTUS + "\n\n  " + s[i:]

# les boutons : un seul, vers le formulaire Tally MFO pre-rempli
m = re.search(r'<div class="btns">.*?</div>\n', s, re.S)
if not m:
    print("ECHEC boutons introuvables")
    sys.exit(1)
s = s[:m.start()] + (
    '<div class="btns">\n'
    '      <a class="btn btn-inv" href="https://tally.so/r/QK94Jk'
    '?fiche=rockfi&cat=mfo&maison=RockFi">'
    "Répondre aux questions · 3 min →</a>\n"
    "    </div>\n") + s[m.end():]

# l'encart : la maison est deja cliente, le texte suit
s = s.replace(
    "<p class=\"big\">Vous représentez RockFi ? <em>Une heure "
    "d'interview sans filtre remplit ce profil.</em></p>",
    "<p class=\"big\">Ce profil se remplit avec la maison. <em>Les réponses "
    "publiées ici seront les siennes, mot pour mot.</em></p>", 1)

# la mention de bas de page porte le statut verifie
s = s.replace(
    "Être référencé ne vaut pas recommandation de l'Exit Club : il s'agit "
    "d'un recensement du marché, pas d'une sélection.",
    "Profil vérifié : contenu fourni et validé par la firme. La vérification "
    "est un engagement commercial qui n'influence ni la présence dans "
    "l'annuaire, ni l'ordre d'affichage, ni les Ligues. Être référencé ne "
    "vaut pas recommandation de l'Exit Club.", 1)

# le css greffe
s = s.replace("</style>", "\n".join(CSS) + "\n</style>", 1)

# ------------------------------------------ controles de sortie
for balise, att in (
    ('<nav class="toc">', 1),
    ('<section class="sect"', 5),
    ("chip-attente", 7),
    ('<h1 class="disp">RockFi</h1>', 1),
    ("Profil référencé · non revendiqué", 0),
    ("vbadge", 2),
    ('<div class="stats">', 1),
    ("Pierre Marin", 1),
    ("Actualités & opérations", 1),
    ("Opportunité du moment", 1),
    ('<div class="k">À propos</div>', 1),
    (".hero{display:flex", 1),
    ("tally.so/r/QK94Jk?fiche=rockfi&cat=mfo&maison=RockFi", 1),
    ("/repondre?", 0),
    ("/fiche-verifiee?", 0),
    ("/referencement?institution", 0),
    ("Voir les 66 multi-family offices", 1),
    ('rel="canonical" href="https://www.exit.club/f/rockfi"', 1),
    ("Réponse de RockFi", 3),
    ("rockfi.fr", 3),
    ("linkedin.com/company/rockfi", 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), str(balise)[:52], att))
        sys.exit(1)
if len(s) < len(T):
    print("ECHEC page plus courte que le gabarit")
    sys.exit(1)

io.open("f/rockfi.html", "w", encoding="utf-8").write(s)
print("ok f/rockfi.html : format standard 5 blocs, %d octets (%d avant)"
      % (len(s), len(OLD)))
print("controle vert : hero verifie, stats, equipe, actus, Tally branche")
