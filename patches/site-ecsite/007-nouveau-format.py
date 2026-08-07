# Ecosysteme: le nouveau format de profil sur les 4 224 fiches
#
# - 4 224 fiches affichaient encore le teaser « Ce qu'elle pourrait montrer »
#   avec sept modules cadenasses, sans une seule question, sans un seul tarif
# - elles recoivent le format des profils etalons : sommaire, cinq blocs
#   editoriaux (remuneration et frais, tarifs, questions des fondateurs,
#   chiffre assume, interview sans filtre), et l'appel a repondre
# - le contenu editorial des cinq blocs est fonction de la categorie, pas de
#   la maison : il est donc lu dans le profil de reference de la categorie,
#   les seuls elements propres a la maison etant son nom dans les chips de
#   reponse et les parametres des liens
# - les logos, JSON-LD, canonical, Reperes et Equipe dirigeante de chaque
#   fiche sont conserves : le teaser est remplace, la fiche n'est pas refaite

import glob
import html
import re
import sys

e = []

# --- categories -------------------------------------------------------------
# ancre ecosysteme -> (profil de reference, code categorie de /repondre)
CAT = {
    "cgp":                ("f/etalon-cgp.html",              "cgp"),
    "fonds-pe":           ("f/etalon-fonds-pe.html",         "pe"),
    "avocats":            ("f/etalon-avocat-fiscaliste.html", "avocat"),
    "fonds-vc":           ("f/etalon-fonds-vc.html",         "vc"),
    "notaires":           ("f/etalon-notaire.html",          "notaire"),
    "banques-affaires":   ("f/cambon-partners.html",         "ba"),
    "mfo":                ("f/myway-family-office.html",     "mfo"),
    "banques-privees":    ("f/mirabaud.html",                "bp"),
    "experts-comptables": ("f/etalon-expert-comptable.html", "ec"),
    "fonds-dette":        ("f/etalon-fonds-dette.html",      "dette"),
    "boutiques-ma":       ("f/cambon-partners.html",         "ma"),
    "secondaire":         ("f/etalon-secondaire.html",       "secondaire"),
    "assurance-vie-lux":  ("f/etalon-av-lux.html",           "avlux"),
}

# Effectif attendu par categorie, mesure avant patch. Un ecart signale un
# ajout ou un retrait de fiches : on s'arrete plutot que de patcher a
# l'aveugle.
EFFECTIF = {"cgp": 3073, "fonds-pe": 317, "avocats": 215, "fonds-vc": 128,
            "notaires": 90, "banques-affaires": 87, "mfo": 73,
            "banques-privees": 65, "experts-comptables": 64,
            "fonds-dette": 62, "boutiques-ma": 28, "secondaire": 19,
            "assurance-vie-lux": 3}

# Ces deux fiches ne portent aucune etiquette de categorie et sortent du
# perimetre : la premiere est la demonstration du profil verifie, la seconde
# attend son arbitrage de categorie.
HORS = {"f/demo-fiche-verifiee.html", "f/rockfi.html"}

# --- feuille de style -------------------------------------------------------
CSS = """.sect p.lead{margin-top:8px;font-size:14.5px;color:var(--muted);max-width:62ch}
.chip-attente{display:inline-flex;align-items:center;gap:6px;font-size:10.5px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);border:1px solid var(--line);background:var(--paper);border-radius:999px;padding:4px 10px}
.chip-source{display:inline-flex;align-items:center;gap:6px;font-size:10.5px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);border:1px solid var(--line);background:var(--paper);border-radius:999px;padding:4px 10px}
.etq{padding:12px 0;border-bottom:1px solid #EFEBDB;display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap}
.etq:last-child{border-bottom:0}
.etq .q{font-size:14px;color:var(--ink);font-weight:500;max-width:52ch}
.etq .q small{display:block;font-weight:400;font-size:12.5px;color:var(--muted);margin-top:3px}
table.grille{width:100%;border-collapse:collapse;margin-top:6px;font-size:13.5px}
table.grille th{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--faint);font-weight:600;text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
table.grille td{padding:11px 10px;border-bottom:1px solid #EFEBDB;color:var(--muted)}
table.grille td.deal{color:var(--ink);font-weight:600;white-space:nowrap}
table.grille td.pend{font-family:'Fraunces',Georgia,serif;font-style:italic;color:var(--faint)}
.qa{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-top:14px}
.qa .qq{font-family:'Fraunces',Georgia,serif;font-weight:400;font-size:17.5px;line-height:1.4;color:var(--ink)}
.qa .verb{margin-top:10px;padding-left:14px;border-left:3px solid var(--line);font-size:13.5px;font-style:italic;color:var(--muted)}
.qa .rep{margin-top:12px;display:flex;align-items:center;gap:10px;font-size:13px;color:var(--muted)}
.bigstat{display:flex;align-items:baseline;gap:18px;flex-wrap:wrap;margin-top:8px}
.bigstat .n{font-family:'Fraunces',Georgia,serif;font-weight:300;font-size:64px;line-height:1;color:var(--faint)}
.bigstat .l{font-size:14px;color:var(--muted);max-width:36ch}
html{scroll-behavior:smooth}
.toc{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px}
.toc a{font-size:12.5px;font-weight:600;color:var(--ink);text-decoration:none;border:1px solid var(--line);background:var(--card);border-radius:999px;padding:8px 14px}
.toc a:hover{border-color:var(--accent);color:var(--accent)}
@media(max-width:760px){.bigstat .n{font-size:46px}}
"""

# --- textes -----------------------------------------------------------------
GAP_BIG = ('<p class="big">Vous représentez {NOM} ? <em>Une heure '
           "d'interview sans filtre remplit ce profil.</em></p>")

GAP_SMALL = ('<p class="small">Vos futurs clients consultent l\'Écosystème '
             "pour choisir leurs conseils. Les questions ci-dessus sont les "
             "leurs, mot pour mot, relevées dans les échanges entre nos "
             "membres.</p>")

MENTIONS = ('<p style="margin-top:30px;font-size:12px;color:var(--faint);'
            'line-height:1.5">Les éléments marqués « interview sans filtre à '
            "venir » seront renseignés par la maison et validés par elle "
            "avant publication : leur absence ne traduit aucun refus de sa "
            "part. Être référencé ne vaut pas recommandation de l'Exit "
            "Club : il s'agit d'un recensement du marché, pas d'une "
            "sélection.</p>")

DESC = ("Rémunération et frais, tarifs, questions des fondateurs, chiffre "
        "assumé : interview sans filtre à venir.")

MENTIONS_OLD = ('<p style="margin-top:30px;font-size:12px;color:var(--faint);'
                'line-height:1.5">Profil non revendiqué. Être référencé ne '
                "vaut pas recommandation de l'Exit Club : il s'agit d'un "
                "recensement du marché, pas d'une sélection.</p>")


# --- lecture des profils de reference ---------------------------------------
def source(chemin):
    """Sommaire et cinq blocs d'un profil de reference, neutralises."""
    s = open(chemin, encoding="utf-8").read()

    m = re.search(r'<nav class="toc">.*?</nav>', s, re.S)
    if not m:
        e.append("ECHEC %s : sommaire introuvable" % chemin)
        return None
    toc = m.group(0)
    if "sans filtre" not in toc:
        e.append("ECHEC %s : sommaire sans « sans filtre », appliquer 005 "
                 "avant 007" % chemin)
        return None

    i = s.find('<section class="sect" id=')
    j = s.find('<div class="gap">')
    if i < 0 or j < i:
        e.append("ECHEC %s : blocs introuvables" % chemin)
        return None
    blocs = s[i:j].rstrip()

    ids = re.findall(r'<section class="sect" id="([^"]+)"', blocs)
    if len(ids) != 5 or ids[-1] != "interview":
        e.append("ECHEC %s : %d bloc(s) %s, 5 attendus" % (chemin, len(ids), ids))
        return None

    # Le bouton « repondre » du profil de reference est retire : chaque fiche
    # recoit le sien, avec ses propres parametres.
    blocs = re.sub(r'\s*<p style="margin-top:16px"><a class="linkbtn" '
                   r'href="/repondre[^"]*">[^<]*</a></p>', "", blocs)
    if "/repondre" in blocs:
        e.append("ECHEC %s : lien /repondre residuel dans les blocs" % chemin)
        return None

    # Le nom de la maison de reference laisse la place a celui de la fiche.
    h1 = re.search(r'<h1 class="disp">([^<]+)</h1>', s)
    if not h1:
        e.append("ECHEC %s : titre introuvable" % chemin)
        return None
    blocs = blocs.replace("Réponse de %s ·" % h1.group(1), "Réponse de {NOM} ·")
    blocs = blocs.replace("Réponse de la maison ·", "Réponse de {NOM} ·")
    n = blocs.count("Réponse de {NOM} ·")
    if n < 1:
        e.append("ECHEC %s : aucune chip de reponse a personnaliser" % chemin)
        return None
    if h1.group(1) in blocs:
        e.append("ECHEC %s : « %s » subsiste dans les blocs"
                 % (chemin, h1.group(1)))
        return None
    return toc, blocs


# Le chapeau du bloc 1 « Remuneration et frais » etait construit sur une
# negation sur neuf profils etalons, et sur une variante enumerative sur le
# profil banque privee. Les dix prennent une seule phrase, neutre, avant
# d'etre diffusees sur 4 224 fiches. Les chapeaux de cambon-partners et de
# myway-family-office ne sont pas touches : ils portent le propos propre a
# leur categorie (activite non regulee pour le M&A, MIF 2 pour les MFO).
LEAD_OLD = [
    ("Des déclarations, pas des chiffres confidentiels : le modèle est "
     "déclaré ici, les montants sont dans la grille."),
    ("Trois déclarations, sans chiffres confidentiels. C'est le modèle "
     "qui est déclaré ici ; les montants sont dans la grille."),
]
LEAD_NEW = "Les chiffres sont ceux déclarés par la maison."
n = 0
for chemin in sorted(set(c for c, _ in CAT.values())):
    s = open(chemin, encoding="utf-8").read()
    o = s
    for a in LEAD_OLD:
        s = s.replace(a, LEAD_NEW)
    if s != o:
        open(chemin, "w", encoding="utf-8").write(s)
        n += 1
if n != 10:
    print("ECHEC chapeau du bloc 1 : %d profil(s) corrige(s), 10 attendu(s)" % n)
    sys.exit(1)
print("ok chapeau du bloc 1 reformule sur %d profils de reference" % n)

SRC = {}
for a, (chemin, _) in sorted(CAT.items()):
    if chemin not in SRC:
        SRC[chemin] = source(chemin)
if e:
    print("\n".join(e))
    sys.exit(1)
print("ok %d profils de reference lus" % len(SRC))

# --- inventaire des fiches a convertir --------------------------------------
fiches = {}
sans_tag = []
for f in sorted(glob.glob("f/*.html")):
    s = open(f, encoding="utf-8").read()
    if '<nav class="toc">' in s:
        continue
    if f in HORS:
        continue
    t = re.findall(r'<a class="tag" href="/ecosysteme#([^"]+)"', s)
    if not t:
        sans_tag.append(f)
        continue
    if t[0] not in CAT:
        e.append("ECHEC %s : categorie « %s » sans profil de reference"
                 % (f, t[0]))
        continue
    fiches.setdefault(t[0], []).append(f)

if sans_tag:
    e.append("ECHEC fiches sans etiquette de categorie : %s"
             % ", ".join(sans_tag))
for a, n in sorted(EFFECTIF.items()):
    v = len(fiches.get(a, []))
    if v != n:
        e.append("ECHEC effectif %s : %d fiche(s), %d attendue(s)" % (a, v, n))
if e:
    print("\n".join(e))
    sys.exit(1)

total = sum(len(v) for v in fiches.values())
print("ok %d fiches a convertir dans %d categories" % (total, len(fiches)))


# --- conversion -------------------------------------------------------------
def convertir(f, ancre):
    chemin, code = CAT[ancre]
    toc, blocs = SRC[chemin]
    s = open(f, encoding="utf-8").read()

    h1 = re.search(r'<h1 class="disp">([^<]+)</h1>', s)
    if not h1:
        return "titre introuvable"
    nom = h1.group(1)

    # Les parametres des liens sont repris tels quels : l'encodage du nom de
    # la maison est deja fait, et il varie d'une fiche a l'autre.
    ref = re.search(r'href="(/referencement\?institution=([^"&]*)&cat='
                    r'[^"&]*&fiche=([^"&]*)&demande=referencer)"', s)
    if not ref:
        return "lien de referencement introuvable"
    inst, slug = ref.group(2), ref.group(3)
    href_rep = "/repondre?fiche=%s&cat=%s&institution=%s" % (slug, code, inst)

    # 1. feuille de style
    if s.count("</style>") != 1:
        return "%d balise(s) </style>" % s.count("</style>")
    s = s.replace("</style>", CSS + "</style>")

    # 2. sommaire, juste apres le bloc de titre
    hi = s.find('<section class="hero')
    if hi < 0:
        return "bloc de titre introuvable"
    hj = s.find("</section>", hi)
    if hj < 0:
        return "fin du bloc de titre introuvable"
    hj += len("</section>")
    s = s[:hj] + "\n\n  " + toc + s[hj:]

    # 3. les cinq blocs a la place du teaser. Aucun bouton n'est ajoute dans
    # le cinquieme : l'appel a l'action le suit immediatement.
    tz = re.search(r'\n  <section class="sect">\s*<div class="k">Réservé aux '
                   r'profils vérifiés</div>.*?\n  </section>\n', s, re.S)
    if not tz:
        return "teaser introuvable"
    s = s[:tz.start()] + "\n  " + blocs.replace("{NOM}", nom) + "\n" + s[tz.end():]

    # 4. l'appel a l'action
    small = re.search(r'<p class="small">.*?</p>', s, re.S)
    if not small:
        return "sous-titre de l'appel a l'action introuvable"
    s = s[:small.start()] + GAP_SMALL + s[small.end():]
    big = re.search(r'<p class="big">.*?</p>', s, re.S)
    if not big:
        return "titre de l'appel a l'action introuvable"
    s = s[:big.start()] + GAP_BIG.replace("{NOM}", nom) + s[big.end():]

    b = re.search(r'<div class="btns">.*?</div>', s, re.S)
    if not b:
        return "boutons introuvables"
    suite = (b.group(0)[len('<div class="btns">'):]
             .replace('class="btn btn-inv"', 'class="btn btn-line"'))
    s = (s[:b.start()] + '<div class="btns">\n      <a class="btn btn-inv" '
         'href="' + href_rep + '">Répondre aux questions · 3 min →</a>'
         + suite + s[b.end():])

    # 5. mentions de bas de page
    if MENTIONS_OLD not in s:
        return "mentions de bas de page introuvables"
    s = s.replace(MENTIONS_OLD, MENTIONS)

    # 6. description de reference, qui annoncait un profil vide
    s = s.replace("Profil non revendiqué.", DESC)
    if "Profil non revendiqué" in s:
        return "mention « profil non revendiqué » residuelle"

    open(f, "w", encoding="utf-8").write(s)
    return None


for ancre in sorted(fiches):
    ko = 0
    for f in fiches[ancre]:
        r = convertir(f, ancre)
        if r:
            ko += 1
            if ko <= 3:
                e.append("ECHEC %s : %s" % (f, r))
    if ko:
        e.append("ECHEC %s : %d/%d fiche(s) en echec"
                 % (ancre, ko, len(fiches[ancre])))
    else:
        print("ok %-20s %5d fiches" % (ancre, len(fiches[ancre])))
if e:
    print("\n".join(e))
    sys.exit(1)

# --- controles de sortie ----------------------------------------------------
for ancre in sorted(fiches):
    code = CAT[ancre][1]
    for f in fiches[ancre]:
        s = open(f, encoding="utf-8").read()
        for x in ['<nav class="toc">', '<section class="sect" id="interview">',
                  "L'interview sans filtre", "cat=%s&institution=" % code,
                  '<a class="btn btn-inv" href="/repondre?',
                  "Les éléments marqués « interview sans filtre à venir »"]:
            if x not in s:
                e.append("ECHEC %s : %s absent" % (f, x))
        for x in ["Ce qu'elle pourrait montrer", "Réservé aux profils vérifiés",
                  "Réponse de la maison ·", "Réponse de {NOM}",
                  "Profil non revendiqué.",
                  # Formulations validees puis retirees : aucune ne doit
                  # reapparaitre par une extraction faite sur un profil de
                  # reference resté en arriere.
                  "pas des chiffres confidentiels", "Trois déclarations",
                  "n'a pas encore répondu"]:
            if x in s:
                e.append("ECHEC %s : %s subsiste" % (f, x))
        if s.count('<section class="sect" id=') != 5:
            e.append("ECHEC %s : %d bloc(s), 5 attendus"
                     % (f, s.count('<section class="sect" id=')))
        if s.count('<nav class="toc">') != 1:
            e.append("ECHEC %s : %d sommaire(s)" % (f, s.count('<nav class="toc">')))
        if s.count(".chip-attente{") != 1:
            e.append("ECHEC %s : %d regle(s) .chip-attente"
                     % (f, s.count(".chip-attente{")))
        # Le chapeau valide s'applique aux dix categories dont le bloc 1
        # s'intitule « Remuneration et frais ». Les trois autres (banques
        # d'affaires, boutiques M&A, MFO) gardent le chapeau propre a leur
        # categorie, lu sur cambon-partners et myway-family-office.
        attendu = LEAD_NEW if code not in ("ba", "ma", "mfo") else None
        if attendu and attendu not in s:
            e.append("ECHEC %s : chapeau du bloc 1 absent" % f)
    if e:
        print("\n".join(e[:12]))
        sys.exit(1)

# --- /repondre : la categorie « boutique M&A » n'avait pas de jeu de
# questions et retombait sur le jeu generique.
s = open("repondre.html", encoding="utf-8").read()
if "SETS.ma" not in s:
    a = "var set = SETS[cat] || SETS.generic;"
    if s.count(a) != 1:
        e.append("ECHEC repondre.html : %d/1 pour la selection du jeu"
                 % s.count(a))
    else:
        s = s.replace(a, "SETS.ma = SETS.ba; // meme metier, meme jeu\n  " + a)
        open("repondre.html", "w", encoding="utf-8").write(s)
        print("ok repondre.html : jeu de questions des boutiques M&A")
if e:
    print("\n".join(e))
    sys.exit(1)

print("controle vert : %d fiches au nouveau format, cinq blocs et sommaire"
      % total)
