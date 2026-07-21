#!/usr/bin/env python3
# Injecte / régénère le bandeau "L'EXIT TAPE" (ticker à la Bloomberg) en haut de
# ecosysteme.html, alimenté par _build/ligues-deals.json (cibles + montants M€ + conseils).
# Idempotent : re-exécutable, remplace le CSS et le HTML entre marqueurs.
# Usage : python3 _build/build_ticker.py  (depuis la racine du repo ecsite)
import json, re, html, unicodedata

NB_TOKENS = 30           # nb de deals affichés dans le ruban
SEC_PAR_TOKEN = 4.0      # vitesse : secondes par jeton pour une passe complète

def esc(s): return html.escape(str(s), quote=False)
def nk(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())

def fmt_meur(v):
    if v is None: return None
    if float(v) == int(v): return f"{int(v)}"
    return f"{v}".replace(".", ",")

deals = json.load(open('_build/ligues-deals.json'))["deals"]
page = open('ecosysteme.html').read()

# slugs pour lier chaque conseil à sa fiche
slugs = {}
for m in re.finditer(r'<li><a href="/f/([^"]+)">([^<]+)</a></li>', page):
    slugs[nk(html.unescape(m.group(2)))] = m.group(1)

MOIS = ["", "janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
def mois(d):
    y, m, _ = d.split("-"); return f"{MOIS[int(m)]}"

# derniers deals À MONTANT connu, du plus récent au plus ancien
avec_montant = sorted((d for d in deals if d.get("valeur") is not None),
                      key=lambda r: r["date"], reverse=True)[:NB_TOKENS]

total = sum(d["valeur"] for d in deals if d.get("valeur") is not None)
n_ops = len(deals)

def token(cible, val, conseil, date):
    v = fmt_meur(val)
    m = ""
    if conseil:
        s = slugs.get(nk(conseil))
        lbl = esc(conseil)
        m = f'<span class="m">{lbl}</span>'
    return (f'<span class="tk"><b>{esc(cible)}</b>'
            f'<span class="v">▲ {v} M€</span>{m}'
            f'<span class="d">{mois(date)}</span></span>')

toks = []
# jeton d'en-tête : cumul suivi
toks.append(f'<span class="tk tk-hi"><b>CUMUL SUIVI</b>'
            f'<span class="v">{int(round(total))} M€</span>'
            f'<span class="m">{n_ops} opérations · saison 25-26</span></span>')
for d in avec_montant:
    conseil = (d.get("conseils") or [None])[0]
    toks.append(token(d["cible"], d["valeur"], conseil, d["date"]))
# jeton vérifié en vitrine
toks.append('<span class="tk tk-star">✦ <b>RockFi</b>'
            '<span class="m">nouvelle fiche vérifiée</span></span>')

track = "".join(toks)
dur = round((len(toks)) * SEC_PAR_TOKEN, 1)

# --- HTML du bandeau (contenu dupliqué 2× pour une boucle sans couture) ---
tape_html = (
    '<!--TAPE_START-->\n'
    '<a class="tape" href="#ligues" aria-label="Fil des opérations de cession suivies par l\'Exit Club">\n'
    '  <span class="tape__tag"><span class="dot"></span>EXIT&nbsp;TAPE</span>\n'
    f'  <span class="tape__win"><span class="tape__track" style="animation-duration:{dur}s">{track}{track}</span></span>\n'
    '</a>\n'
    '<!--TAPE_END-->'
)

# --- CSS du bandeau ---
tape_css = (
    '/*TAPE_CSS_START*/\n'
    '.tape{display:flex;align-items:stretch;position:sticky;top:0;z-index:50;'
    'background:#20290F;border-bottom:1px solid #3A4522;height:38px;overflow:hidden;'
    'text-decoration:none;font-size:12.5px;cursor:pointer}\n'
    '.tape__tag{flex:none;display:flex;align-items:center;gap:7px;padding:0 16px;'
    'background:#161C0A;color:#E7E2C9;font-weight:700;letter-spacing:.14em;font-size:11px;'
    'text-transform:uppercase;border-right:1px solid #3A4522;z-index:2}\n'
    '.tape__tag .dot{width:7px;height:7px;border-radius:50%;background:#9BD17B;'
    'box-shadow:0 0 0 0 rgba(155,209,123,.7);animation:tapepulse 1.8s infinite}\n'
    '@keyframes tapepulse{0%{box-shadow:0 0 0 0 rgba(155,209,123,.6)}'
    '70%{box-shadow:0 0 0 7px rgba(155,209,123,0)}100%{box-shadow:0 0 0 0 rgba(155,209,123,0)}}\n'
    '.tape__win{flex:1;overflow:hidden;display:flex;align-items:center;'
    '-webkit-mask-image:linear-gradient(90deg,transparent,#000 3%,#000 97%,transparent);'
    'mask-image:linear-gradient(90deg,transparent,#000 3%,#000 97%,transparent)}\n'
    '.tape__track{display:inline-flex;align-items:center;white-space:nowrap;'
    'will-change:transform;animation:tapescroll linear infinite}\n'
    '@keyframes tapescroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}\n'
    '.tape:hover .tape__track{animation-play-state:paused}\n'
    '.tk{display:inline-flex;align-items:baseline;gap:8px;padding:0 18px;'
    "font-family:ui-monospace,'SF Mono',Menlo,Consolas,monospace}\n"
    '.tk+.tk{border-left:1px solid #333E1E}\n'
    '.tk b{color:#F1ECD6;font-weight:600;letter-spacing:.01em}\n'
    '.tk .v{color:#9BD17B;font-weight:600}\n'
    '.tk .m{color:#8E9A6E}\n'
    '.tk .d{color:#5F6B42;font-size:11px;text-transform:uppercase;letter-spacing:.06em}\n'
    '.tk-hi b{color:#D9C68A}\n'
    '.tk-hi .v{color:#E7D9A6}\n'
    '.tk-star b{color:#F1ECD6}\n'
    '.tk-star{color:#9BD17B}\n'
    '.cat,.league,.actus{scroll-margin-top:52px}\n'
    '@media(max-width:760px){.tape__tag{padding:0 11px;font-size:10px}.tk{padding:0 13px}}\n'
    '@media(prefers-reduced-motion:reduce){.tape__track{animation:none}}\n'
    '/*TAPE_CSS_END*/'
)

# purge d'éventuelles versions précédentes
page = re.sub(r'<!--TAPE_START-->.*?<!--TAPE_END-->\n?', '', page, flags=re.S)
page = re.sub(r'/\*TAPE_CSS_START\*/.*?/\*TAPE_CSS_END\*/\n?', '', page, flags=re.S)

# injecte le CSS juste avant la 1re fermeture </style>
page = page.replace('</style>', tape_css + '\n</style>', 1)
# injecte le bandeau juste après <body>
page = page.replace('<body>', '<body>\n' + tape_html, 1)

open('ecosysteme.html', 'w').write(page)
print(f"tape OK — {len(avec_montant)} deals dans le ruban, cumul {int(round(total))} M€, durée {dur}s")
