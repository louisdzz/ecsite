# -*- coding: utf-8 -*-
"""Mur de logos sous le hero de l'Écosystème.
Liste triée à la main : le mur est la première preuve de sérieux que voit un
visiteur, il doit avoir zéro taux d'erreur. Grille STATIQUE (la page porte déjà
un bandeau animé en haut, une deuxième animation serait du bruit).
Injecté entre <!-- LOGOWALL:START --> et <!-- LOGOWALL:END -->.
"""
import hashlib, json, os, re, unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)

META = json.load(open('_build/logos/dir-meta.json'))

# Ordre voulu : banques d'affaires, avocats, fonds, gestion privée.
# Un slug sans logo ou sans fiche est simplement sauté.
CURATED = """
lazard jp-morgan morgan-stanley bank-of-america citigroup deutsche-bank jefferies
rothschild-co oddo-bhf kepler-cheuvreux societe-generale-cib credit-agricole-cib ubs
mediobanca pjt-partners cambon-partners clipperton
bredin-prat darrois-villey gide-loyrette-nouel latham-watkins weil-gotshal-manges
kirkland-ellis cleary-gottlieb linklaters clifford-chance hogan-lovells baker-mckenzie
jones-day willkie-farr goodwin-procter-france mcdermott-will-schulte davis-polk dentons
august-debouzy franklin ll-berg villechenon
ardian eurazeo pai-partners astorg-partner kkr partners-group apax-partners advent-international-sas
tikehau-capital icg pemberton-asset-management 17capital bpifrance idi montefiore-investment
naxicap-partners lbo-france activa-capital qualium-investissement siparex ik-partners
abenex ekkio-capital motion-equity-partners eqt keensight-capital emz-partners parquest
access-capital-partners elyan-partners brookfield antin-infrastructure-partners
infravia-capital-partners meridiam andera-partners omnes-capital chequers-capital
argos-conseil sagard-sas aestia-capital
sofinnova-partners breega kurma-partners daphni isai-gestion educapital jolt-capital
supernova-invest france-valley
rockfi cyrus-herez pictet-wealth-management milleis-banque-privee bordier-cie
quintet-private-bank-lu kermony-office scala-patrimoine groupe-premium herest
rothschild-co-martin-maurel oddo-bhf-pwm bnp-paribas-banque-privee banque-transatlantique
hsbc-private-banking natixis-investment-managers bnp-paribas-asset-management
amundi-asset-management axa-investment-managers nordea lazard-freres-gestion
montpensier-arbevel
""".split()

# Une marque n'apparaît qu'une fois : Rothschild & Co et Rothschild Martin Maurel
# portent le même logo, deux tuiles identiques feraient amateur.
GROUPES = ('rothschild', 'oddo', 'bnp paribas', 'lazard', 'societe generale',
           'credit agricole', 'hsbc', 'natixis', 'jp morgan', 'morgan stanley',
           'goldman', 'degroof', 'pictet', 'ubs', 'amundi', 'axa', 'infravia', 'isai')


def marque(slug, nom):
    n = unicodedata.normalize('NFKD', nom.lower())
    n = ''.join(c for c in n if not unicodedata.combining(c))
    for g in GROUPES:
        if n.startswith(g):
            return g
    return slug

CSS = """/*WALL_CSS_START*/
.wall{margin:34px 0 0}
.wall__h{display:flex;align-items:baseline;justify-content:space-between;gap:16px;border-top:1px solid var(--line);padding-top:14px}
.wall__h p{font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--faint)}
.wall__h span{font-size:12.5px;color:var(--muted)}
.wall__g{margin-top:16px;display:grid;grid-template-columns:repeat(9,1fr);gap:1px;background:var(--line);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.wall__g a{background:var(--card);height:62px;display:flex;align-items:center;justify-content:center;padding:11px;transition:background .18s}
.wall__g a.dk{background:var(--ink)}
.wall__g img{max-width:100%;max-height:100%;object-fit:contain;filter:grayscale(1);opacity:.55;transition:filter .18s,opacity .18s}
.wall__g a.dk img{filter:grayscale(1) brightness(1.9);opacity:.5}
.wall__g a:hover{background:#fff}
.wall__g a:hover img,.wall__g a:focus-visible img{filter:none;opacity:1}
.wall__g a.dk:hover{background:var(--ink)}
.wall__f{margin-top:12px;font-size:13px;color:var(--muted)}
.wall__f a{color:var(--accent);text-decoration:none;border-bottom:1px solid var(--line)}
@media(max-width:1000px){.wall__g{grid-template-columns:repeat(6,1fr)}}
@media(max-width:760px){.wall__g{grid-template-columns:repeat(4,1fr)}.wall__g a{height:54px;padding:9px}.wall__h{flex-direction:column;gap:4px}}
/*WALL_CSS_END*/
"""


def build():
    seen, cells = set(), []
    for slug in CURATED:
        m = META.get(slug)
        if not m or not os.path.exists('f/%s.html' % slug):
            continue
        k = marque(slug, m['nom'])
        try:
            k2 = hashlib.sha1(open(m['f'].lstrip('/'), 'rb').read()).hexdigest()
        except Exception:
            k2 = slug
        if k in seen or k2 in seen:
            continue
        seen.add(k)
        seen.add(k2)
        nom = re.sub(r'["<>]', '', m['nom'])[:80]
        cells.append('<a href="/f/%s"%s title="%s"><img src="%s" alt="%s" '
                     'loading="lazy" width="%d" height="%d"></a>'
                     % (slug, ' class="dk"' if m['dark'] else '', nom,
                        m['f'], nom, m['w'], m['h']))
    n = len(cells)
    # une grille pleine : on coupe au dernier multiple de 9 pour éviter une ligne trouée
    n9 = n - (n % 9)
    cells = cells[:n9]
    html = (
        '<!-- LOGOWALL:START -->\n'
        '<section class="wall" aria-label="Institutions recensées">\n'
        '  <div class="wall__h"><p>Ils sont dans l\'Écosystème</p>'
        '<span>%d maisons cliquables ci-dessous, %s fiches au total</span></div>\n'
        '  <div class="wall__g">%s</div>\n'
        '  <p class="wall__f">Chaque logo mène à la fiche publique de la maison. '
        '<a href="#cgp">Voir les 12 catégories</a></p>\n'
        '</section>\n'
        '<!-- LOGOWALL:END -->' % (len(cells), '4&nbsp;160', ''.join(cells)))
    return html, len(cells)


if __name__ == '__main__':
    block, n = build()
    p = 'ecosysteme.html'
    h = open(p, encoding='utf-8').read()

    if '/*WALL_CSS_START*/' in h:
        h = re.sub(r'/\*WALL_CSS_START\*/.*?/\*WALL_CSS_END\*/', CSS.strip(), h, flags=re.S)
    else:
        anchor = '/*TAPE_CSS_END*/'
        assert h.count(anchor) >= 1
        h = h.replace(anchor, anchor + '\n' + CSS, 1)

    if '<!-- LOGOWALL:START -->' in h:
        h = re.sub(r'<!-- LOGOWALL:START -->.*?<!-- LOGOWALL:END -->', block, h, flags=re.S)
    else:
        anchor = '<div class="toolbar">'
        assert h.count(anchor) == 1
        h = h.replace(anchor, block + '\n\n' + anchor, 1)

    open(p, 'w', encoding='utf-8').write(h)
    print('mur de logos : %d institutions' % n)
