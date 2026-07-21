#!/usr/bin/env python3
# Injecte / régénère le bandeau "L'EXIT TAPE" (ticker à la Bloomberg) en tête de
# ecosysteme.html. Trois flux dans un même ruban :
#   - deals (cible + montant M€ + conseil) depuis _build/ligues-deals.json,
#   - nominations (mouvements de dirigeants) depuis _build/nominations.json,
#   - en LIVE : le front récupère /api/ecosysteme-tape et reconstruit le ruban
#     avec les derniers deals à jour (fallback = version statique ci-dessous).
# Jetons cliquables (→ fiche du conseil / de la firme) + flash vert sur les
# opérations de moins de 7 jours. Idempotent : re-exécutable (marqueurs).
# Usage : python3 _build/build_ticker.py
import json, re, html, unicodedata, datetime

NB_TOKENS = 30
SEC_PAR_TOKEN = 4.0
API = "https://exit-club-app.vercel.app/api/ecosysteme-tape"

def esc(s): return html.escape(str(s), quote=False)
def nk(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())
def fmt_meur(v):
    if v is None: return None
    return f"{int(v)}" if float(v) == int(v) else f"{v}".replace(".", ",")

deals = json.load(open('_build/ligues-deals.json'))["deals"]
noms = json.load(open('_build/nominations.json'))["nominations"]
page = open('ecosysteme.html').read()

slugs = {}
for m in re.finditer(r'<li><a href="/f/([^"]+)">([^<]+)</a></li>', page):
    slugs[nk(html.unescape(m.group(2)))] = m.group(1)

MOIS = ["", "janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
def mois(d): return MOIS[int(d.split("-")[1])]
TODAY = datetime.date.today()
def is_fresh(d):
    try: return (TODAY - datetime.date.fromisoformat(d)).days <= 7
    except Exception: return False

def deal_token(cible, val, conseil, date):
    v = fmt_meur(val)
    money = f'<span class="v">▲ {v} M€</span>' if v is not None else '<span class="v nc">n.c.</span>'
    meta = f'<span class="m">{esc(conseil)}</span>' if conseil else ''
    inner = f'<b>{esc(cible)}</b>{money}{meta}<span class="d">{mois(date)}</span>'
    cls = "tk" + (" tk-fresh" if is_fresh(date) else "")
    slug = slugs.get(nk(conseil)) if conseil else None
    if slug:
        return f'<a class="{cls}" href="/f/{slug}">{inner}</a>'
    return f'<span class="{cls}">{inner}</span>'

def nom_token(n):
    inner = (f'<span class="chip-nom">Nomination</span><b>{esc(n["nom"])}</b>'
             f'<span class="r">{esc(n["role"])}</span>'
             f'<span class="f">→ {esc(n["firme"])}</span>')
    slug = slugs.get(nk(n["firme"]))
    cls = "tk tk-nom"
    if slug:
        return f'<a class="{cls}" href="/f/{slug}">{inner}</a>'
    return f'<span class="{cls}">{inner}</span>'

# --- ruban statique (fallback) : cumul + deals récents, une nomination tous les 5 deals ---
avec_montant = sorted((d for d in deals if d.get("valeur") is not None),
                      key=lambda r: r["date"], reverse=True)[:NB_TOKENS]
total = sum(d["valeur"] for d in deals if d.get("valeur") is not None)
n_ops = len(deals)

toks = [f'<a class="tk tk-hi" href="#ligues"><b>CUMUL SUIVI</b>'
        f'<span class="v">{int(round(total))} M€</span>'
        f'<span class="m">{n_ops} opérations · saison 25-26</span></a>']
ni = 0
for i, d in enumerate(avec_montant):
    conseil = (d.get("conseils") or [None])[0]
    toks.append(deal_token(d["cible"], d["valeur"], conseil, d["date"]))
    if (i + 1) % 5 == 0 and ni < len(noms):
        toks.append(nom_token(noms[ni])); ni += 1
while ni < len(noms):
    toks.append(nom_token(noms[ni])); ni += 1

track = "".join(toks)
dur = round(len(toks) * SEC_PAR_TOKEN, 1)

# données pour la reconstruction LIVE côté client
noms_json = json.dumps(noms, ensure_ascii=False)
slugs_json = json.dumps(slugs, ensure_ascii=False)

tape_html = (
    '<!--TAPE_START-->\n'
    '<div class="tape">\n'
    '  <a class="tape__tag" href="#ligues"><span class="dot"></span>EXIT&nbsp;TAPE</a>\n'
    f'  <div class="tape__win"><div class="tape__track" id="tapeTrack" style="animation-duration:{dur}s">{track}{track}</div></div>\n'
    '</div>\n'
    f'<script id="tape-noms" type="application/json">{noms_json}</script>\n'
    f'<script id="tape-slugs" type="application/json">{slugs_json}</script>\n'
    '<script>\n'
    '(function(){\n'
    '  var MOIS=["","janv.","févr.","mars","avr.","mai","juin","juil.","août","sept.","oct.","nov.","déc."];\n'
    '  function esc(s){var d=document.createElement("div");d.textContent=s==null?"":String(s);return d.innerHTML;}\n'
    '  function nk(s){return (s||"").normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").toLowerCase().replace(/[^a-z0-9]/g,"");}\n'
    '  var slugs={}, noms=[];\n'
    '  try{slugs=JSON.parse(document.getElementById("tape-slugs").textContent);}catch(e){}\n'
    '  try{noms=JSON.parse(document.getElementById("tape-noms").textContent);}catch(e){}\n'
    '  function fmt(v){return v==null?null:(v%1===0?String(v):String(v).replace(".",","));}\n'
    '  function fresh(d){var t=(Date.now()-new Date(d).getTime())/86400000;return t>=0&&t<=7;}\n'
    '  function dealTok(d){\n'
    '    var v=fmt(d.valeur); var money=v!=null?\'<span class="v">▲ \'+v+\' M€</span>\':\'<span class="v nc">n.c.</span>\';\n'
    '    var conseil=(d.conseils&&d.conseils[0])||""; var meta=conseil?\'<span class="m">\'+esc(conseil)+"</span>":"";\n'
    '    var inner="<b>"+esc(d.cible)+"</b>"+money+meta+\'<span class="d">\'+MOIS[parseInt(String(d.date).split("-")[1],10)]+"</span>";\n'
    '    var cls="tk"+(fresh(d.date)?" tk-fresh":""); var slug=conseil?slugs[nk(conseil)]:null;\n'
    '    return slug?\'<a class="\'+cls+\'" href="/f/\'+slug+\'">\'+inner+"</a>":\'<span class="\'+cls+\'">\'+inner+"</span>";\n'
    '  }\n'
    '  function nomTok(n){\n'
    '    var inner=\'<span class="chip-nom">Nomination</span><b>\'+esc(n.nom)+"</b>"+\'<span class="r">\'+esc(n.role)+"</span>"+\'<span class="f">→ \'+esc(n.firme)+"</span>";\n'
    '    var slug=slugs[nk(n.firme)]; var cls="tk tk-nom";\n'
    '    return slug?\'<a class="\'+cls+\'" href="/f/\'+slug+\'">\'+inner+"</a>":\'<span class="\'+cls+\'">\'+inner+"</span>";\n'
    '  }\n'
    '  fetch(API_URL).then(function(r){if(!r.ok)throw 0;return r.json();}).then(function(d){\n'
    '    if(!d.deals||!d.deals.length)return;\n'
    '    var deals=d.deals.slice(0,30);\n'
    '    var toks=[\'<a class="tk tk-hi" href="#ligues"><b>CUMUL SUIVI</b><span class="v">\'+(d.total||0)+\' M€</span><span class="m">\'+(d.count||deals.length)+" opérations · saison 25-26</span></a>"];\n'
    '    var ni=0;\n'
    '    deals.forEach(function(x,i){ toks.push(dealTok(x)); if((i+1)%5===0&&ni<noms.length){toks.push(nomTok(noms[ni]));ni++;} });\n'
    '    while(ni<noms.length){toks.push(nomTok(noms[ni]));ni++;}\n'
    '    var track=toks.join(""); var el=document.getElementById("tapeTrack");\n'
    '    el.style.animationDuration=(toks.length*4.0)+"s"; el.innerHTML=track+track;\n'
    '  }).catch(function(){});\n'
    '})();\n'
    '</script>\n'
    '<!--TAPE_END-->'
).replace("API_URL", '"' + API + '"')

tape_css = (
    '/*TAPE_CSS_START*/\n'
    '.tape{display:flex;align-items:stretch;position:sticky;top:0;z-index:50;'
    'background:#20290F;border-bottom:1px solid #3A4522;height:38px;overflow:hidden;font-size:12.5px}\n'
    '.tape__tag{flex:none;display:flex;align-items:center;gap:7px;padding:0 16px;'
    'background:#161C0A;color:#E7E2C9;font-weight:700;letter-spacing:.14em;font-size:11px;'
    'text-transform:uppercase;border-right:1px solid #3A4522;z-index:2;text-decoration:none}\n'
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
    ".tk{display:inline-flex;align-items:baseline;gap:8px;padding:0 18px;text-decoration:none;"
    "font-family:ui-monospace,'SF Mono',Menlo,Consolas,monospace}\n"
    '.tk+.tk{border-left:1px solid #333E1E}\n'
    'a.tk:hover b{text-decoration:underline}\n'
    '.tk b{color:#F1ECD6;font-weight:600}\n'
    '.tk .v{color:#9BD17B;font-weight:600}\n'
    '.tk .v.nc{color:#6E7A50}\n'
    '.tk .m{color:#8E9A6E}\n'
    '.tk .d{color:#5F6B42;font-size:11px;text-transform:uppercase;letter-spacing:.06em}\n'
    '.tk-hi b{color:#D9C68A}.tk-hi .v{color:#E7D9A6}\n'
    '.tk-nom b{color:#E7D9A6}.tk-nom .r{color:#8E9A6E}.tk-nom .f{color:#C9B876}\n'
    '.chip-nom{font-family:Inter,sans-serif;font-size:9.5px;font-weight:700;letter-spacing:.12em;'
    'text-transform:uppercase;color:#20290F;background:#C9B876;border-radius:3px;padding:2px 6px;align-self:center}\n'
    '@keyframes tkflash{0%,100%{background:transparent}25%,60%{background:rgba(155,209,123,.20)}}\n'
    '.tk-fresh{animation:tkflash 1.1s ease-in-out 3}\n'
    '.cat,.league,.actus{scroll-margin-top:52px}\n'
    '@media(max-width:760px){.tape__tag{padding:0 11px;font-size:10px}.tk{padding:0 13px}}\n'
    '@media(prefers-reduced-motion:reduce){.tape__track{animation:none}.tk-fresh{animation:none}}\n'
    '/*TAPE_CSS_END*/'
)

page = re.sub(r'<!--TAPE_START-->.*?<!--TAPE_END-->\n?', '', page, flags=re.S)
page = re.sub(r'/\*TAPE_CSS_START\*/.*?/\*TAPE_CSS_END\*/\n?', '', page, flags=re.S)
page = page.replace('</style>', tape_css + '\n</style>', 1)
page = page.replace('<body>', '<body>\n' + tape_html, 1)
open('ecosysteme.html', 'w').write(page)
print(f"tape OK — {len(avec_montant)} deals + {len(noms)} nominations, cumul {int(round(total))} M€, durée {dur}s, fresh<=7j")
