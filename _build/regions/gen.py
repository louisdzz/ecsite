# -*- coding: utf-8 -*-
"""Pages régionales de l'Écosystème : /regions/<region>.

Pourquoi ces pages. Un cabinet ne paie pas parce que sa fiche est belle, il paie
parce que celle du confrère d'à côté l'est plus. La page régionale met les
cabinets d'un même marché côte à côte, dans le même format : celui qui publie
ses encours a une ligne de plus, celui qui est vérifié passe en tête. C'est
aussi la page que le dirigeant enverra à son associé pour justifier la dépense.

Entrées : _build/cgp-geo.json (3056 cabinets géolocalisés par le registre)
          _build/ligue-cgp/encours-*.json (encours PUBLIÉS, avec source)
          _build/places.json (places de fiches vérifiées ouvertes)
          _build/verified/*.json (fiches vérifiées existantes)
Sortie  : regions/index.html + regions/<slug>.html

Règle de prudence : un cabinet sans département identifié n'est PAS placé au
hasard, il reste hors des pages régionales. Un encours n'est affiché que s'il
est publié et sourcé.
"""
import json, os, re, unicodedata, glob, html as H

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)
OUT = 'regions'
os.makedirs(OUT, exist_ok=True)

REGIONS = [
    ("Auvergne-Rhône-Alpes", "en Auvergne-Rhône-Alpes",
     "01 03 07 15 26 38 42 43 63 69 73 74"),
    ("Bourgogne-Franche-Comté", "en Bourgogne-Franche-Comté",
     "21 25 39 58 70 71 89 90"),
    ("Bretagne", "en Bretagne", "22 29 35 56"),
    ("Centre-Val de Loire", "en Centre-Val de Loire", "18 28 36 37 41 45"),
    ("Corse", "en Corse", "20"),
    ("Grand Est", "dans le Grand Est", "08 10 51 52 54 55 57 67 68 88"),
    ("Hauts-de-France", "dans les Hauts-de-France", "02 59 60 62 80"),
    ("Île-de-France", "en Île-de-France", "75 77 78 91 92 93 94 95"),
    ("Normandie", "en Normandie", "14 27 50 61 76"),
    ("Nouvelle-Aquitaine", "en Nouvelle-Aquitaine",
     "16 17 19 23 24 33 40 47 64 79 86 87"),
    ("Occitanie", "en Occitanie",
     "09 11 12 30 31 32 34 46 48 65 66 81 82"),
    ("Pays de la Loire", "dans les Pays de la Loire", "44 49 53 72 85"),
    ("Provence-Alpes-Côte d'Azur", "en Provence-Alpes-Côte d'Azur",
     "04 05 06 13 83 84"),
    ("Outre-mer", "en Outre-mer",
     "971 972 973 974 975 976 977 978 984 986 987 988"),
]

DEPS = """01 Ain|02 Aisne|03 Allier|04 Alpes-de-Haute-Provence|05 Hautes-Alpes|
06 Alpes-Maritimes|07 Ardèche|08 Ardennes|09 Ariège|10 Aube|11 Aude|12 Aveyron|
13 Bouches-du-Rhône|14 Calvados|15 Cantal|16 Charente|17 Charente-Maritime|
18 Cher|19 Corrèze|20 Corse|21 Côte-d'Or|22 Côtes-d'Armor|23 Creuse|24 Dordogne|
25 Doubs|26 Drôme|27 Eure|28 Eure-et-Loir|29 Finistère|30 Gard|31 Haute-Garonne|
32 Gers|33 Gironde|34 Hérault|35 Ille-et-Vilaine|36 Indre|37 Indre-et-Loire|
38 Isère|39 Jura|40 Landes|41 Loir-et-Cher|42 Loire|43 Haute-Loire|
44 Loire-Atlantique|45 Loiret|46 Lot|47 Lot-et-Garonne|48 Lozère|
49 Maine-et-Loire|50 Manche|51 Marne|52 Haute-Marne|53 Mayenne|
54 Meurthe-et-Moselle|55 Meuse|56 Morbihan|57 Moselle|58 Nièvre|59 Nord|
60 Oise|61 Orne|62 Pas-de-Calais|63 Puy-de-Dôme|64 Pyrénées-Atlantiques|
65 Hautes-Pyrénées|66 Pyrénées-Orientales|67 Bas-Rhin|68 Haut-Rhin|69 Rhône|
70 Haute-Saône|71 Saône-et-Loire|72 Sarthe|73 Savoie|74 Haute-Savoie|75 Paris|
76 Seine-Maritime|77 Seine-et-Marne|78 Yvelines|79 Deux-Sèvres|80 Somme|81 Tarn|
82 Tarn-et-Garonne|83 Var|84 Vaucluse|85 Vendée|86 Vienne|87 Haute-Vienne|
88 Vosges|89 Yonne|90 Territoire de Belfort|91 Essonne|92 Hauts-de-Seine|
93 Seine-Saint-Denis|94 Val-de-Marne|95 Val-d'Oise|971 Guadeloupe|972 Martinique|
973 Guyane|974 La Réunion|975 Saint-Pierre-et-Miquelon|976 Mayotte|
977 Saint-Barthélemy|978 Saint-Martin|984 Terres australes|
986 Wallis-et-Futuna|987 Polynésie française|988 Nouvelle-Calédonie"""
DEPNAME = dict(x.strip().split(' ', 1) for x in DEPS.replace('\n', '').split('|'))


def strip(s):
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


def slugify(s):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', strip(s))).strip('-')


def norm(s):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', strip(s))).strip()


def ville(c):
    """PARIS 8E ARRONDISSEMENT -> Paris 8e."""
    if not c:
        return ''
    c = c.title().replace('Arrondissement', '').strip()
    c = re.sub(r'\b(\d+)E\b', lambda m: m.group(1) + 'e', c)
    return re.sub(r'\s+', ' ', c)


def e(s):
    return H.escape(s or '', quote=True)


# ---------------------------------------------------------------- données
GEO = json.load(open('_build/cgp-geo.json'))
for v in GEO.values():                       # outre-mer : le code à 2 chiffres
    d, cp = v.get('dep'), v.get('cp') or ''  # ne distingue pas les territoires
    if d in ('97', '98') and len(cp) >= 3 and cp[:3].isdigit():
        v['dep'] = cp[:3]
PLACES = json.load(open('_build/places.json'))
CGP = PLACES['cgp']

ENC = {}
for p in ['_build/ligue-cgp/encours-gros.json',
          '_build/ligue-cgp/encours-intermediaires.json']:
    for r in json.load(open(p)):
        base = re.split(r'[(/–-]', r['nom'])[0]
        for k in {norm(r['nom']), norm(base)}:
            if k:
                ENC.setdefault(k, r)
BYNOM = {}
for slug, v in GEO.items():
    BYNOM.setdefault(norm(v['nom']), slug)
ENCS = {}                                   # slug -> enregistrement encours
for k, r in ENC.items():
    s = BYNOM.get(k)
    if s and s not in ENCS:
        ENCS[s] = r

VERIF = {os.path.basename(p)[:-5] for p in glob.glob('_build/verified/*.json')
         if not os.path.basename(p).startswith('demo')}


# Le recensement mélange, dans la catégorie gestion privée, des cabinets de
# conseil patrimonial et des intermédiaires de courtage, crédit ou financement.
# Le discriminant réel est le statut CIF à l'ORIAS, que nous n'avons pas à
# l'échelle. On se rabat sur l'activité DÉCLARÉE par la raison sociale : un
# cabinet qui s'appelle « Credits Immo » ne se présente pas comme un CGP. Le
# libellé retenu reste neutre et les deux listes sont publiées.
COURT = re.compile(r'courtage|courtier|credit|immobili|immo\b|emprunt|\bpret\b|prets|'
                   r'financement|assurance|mandataire|garantie|hypoth|banque|rachat|'
                   r'\bnego|\btaux\b|meilleurtaux|\.com\b|\.fr\b')
PATRI = re.compile(r'patrimoi|patrimon|gestion privee|family office|wealth|fortune')
# Ni conseil patrimonial ni courtage : associations, syndicats, structures qui
# n'exercent aucune des deux activites. Elles sortent des deux listes visibles.
HORS = re.compile(r'\bassociation\b|\basso\b|\bsyndicat|\bcopropriet|\bamicale\b|'
                  r'\bfondation\b|\bcomite\b|\bmutuelle\b')


def courtage(nom):
    n = strip(nom)
    return bool(COURT.search(n)) and not PATRI.search(n)


def hors(nom):
    n = strip(nom)
    return bool(HORS.search(n)) and not PATRI.search(n)


NAT = {'conseilles': 'conseillés', 'conseillés': 'conseillés',
       'sous gestion': 'sous gestion', 'groupe': 'consolidés'}


def md(m):
    """1 100 -> 1,1 Md€ ; 850 -> 850 M€."""
    if m >= 1000:
        s = ('%.1f' % (m / 1000.0)).replace('.0', '').replace('.', ',')
        return s + ' Md€'
    return '%d M€' % m


# ---------------------------------------------------------------- gabarit
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;1,9..144,300;1,9..144,400&family=Inter:wght@400;500;600&display=swap');
:root{--paper:#F7F3E4;--ink:#2A351A;--accent:#47621E;--muted:#6F7854;--faint:#98A07E;--line:#DDD6BC;--card:#FCFAF0;--draft:#8A6A1F}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--paper);color:var(--ink);font-family:'Inter',Arial,sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased}
.disp{font-family:'Fraunces',Georgia,serif;font-variation-settings:"opsz" 144;font-weight:300;letter-spacing:-.01em}
.disp .it{font-style:italic}
.wrap{max-width:1040px;margin:0 auto;padding:0 40px}
.top{display:flex;align-items:center;justify-content:space-between;padding:26px 0}
.mark{font-family:'Fraunces',Georgia,serif;font-size:21px;text-decoration:none;color:var(--ink)}
.mark i{font-style:italic}.mark b{font-weight:600}
.nav{display:flex;align-items:center;gap:22px}
.nav a{font-size:13.5px;color:var(--muted);text-decoration:none}
.nav a.cta{font-size:13px;font-weight:600;color:var(--paper);background:var(--accent);padding:9px 16px;border-radius:999px}
.crumb{font-size:13px;color:var(--muted);margin:14px 0 0}
.crumb a{color:var(--muted);text-decoration:none;border-bottom:1px dotted var(--line)}
.hero{padding:26px 0 8px}
.over{font-size:12px;letter-spacing:.26em;text-transform:uppercase;color:var(--faint);margin:0 0 14px}
h1.disp{font-size:52px;line-height:1.02}
.lede{margin-top:16px;font-size:16.5px;color:var(--muted);max-width:62ch}
.kpi{display:flex;gap:34px;flex-wrap:wrap;border-top:1px solid var(--line);margin-top:26px;padding-top:16px}
.kpi div b{display:block;font-family:'Fraunces',Georgia,serif;font-weight:400;font-size:27px;line-height:1.1}
.kpi div span{display:block;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);margin-top:4px}
.slots{margin-top:26px;background:var(--ink);color:var(--paper);border-radius:18px;padding:24px 28px;display:flex;gap:26px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.slots .n{font-family:'Fraunces',Georgia,serif;font-weight:300;font-size:40px;line-height:1;color:#E9D9A4}
.slots .tx{min-width:0;flex:1}
.slots p.big{font-family:'Fraunces',Georgia,serif;font-weight:300;font-size:20px;line-height:1.35;max-width:52ch}
.slots p.small{margin-top:8px;font-size:13px;color:#C9CBB4;max-width:66ch}
.btn{display:inline-block;font-size:13.5px;font-weight:600;padding:12px 20px;border-radius:999px;text-decoration:none;background:var(--paper);color:var(--ink)}
.sect{margin-top:46px}
.sect .k{font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--faint);font-weight:600}
.sect h2{font-family:'Fraunces',Georgia,serif;font-weight:300;font-size:31px;margin-top:8px}
.sect p.intro{margin-top:10px;font-size:14.5px;color:var(--muted);max-width:70ch}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:20px}
.cd{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px 20px}
.cd .hd{display:flex;align-items:baseline;justify-content:space-between;gap:12px}
.cd a.nm{font-size:15.5px;font-weight:600;color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line)}
.cd .enc{flex:none;font-family:'Fraunces',Georgia,serif;font-size:19px;font-weight:400;color:var(--accent)}
.cd .mt{margin-top:8px;font-size:12.5px;color:var(--faint)}
.cd .mt a{color:var(--faint)}
.vb{display:inline-block;font-size:10.5px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);border:1px solid var(--line);background:var(--paper);border-radius:999px;padding:3px 9px;margin-left:8px}
.empty{margin-top:20px;background:var(--card);border:1px dashed var(--line);border-radius:16px;padding:24px}
.empty p{font-size:14.5px;color:var(--muted);max-width:70ch}
.empty p.f{font-family:'Fraunces',Georgia,serif;font-size:19px;font-weight:300;color:var(--ink);margin-bottom:8px}
.tools{margin-top:20px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.tools input{font-family:'Inter',Arial,sans-serif;font-size:14px;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:999px;padding:11px 18px;width:280px;outline:none}
.tools input:focus{border-color:var(--accent)}
.tools .hint{font-size:12.5px;color:var(--faint)}
.dep{margin-top:30px}
.dep h3{font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--faint);font-weight:600;border-top:1px solid var(--line);padding-top:12px}
.firms{list-style:none;columns:3;column-gap:26px;margin-top:12px}
.firms li{break-inside:avoid;padding:3px 0;font-size:14px}
.firms li a{color:var(--ink);text-decoration:none;border-bottom:1px solid transparent}
.firms li a:hover{border-bottom-color:var(--accent)}
.firms li i{font-style:normal;color:var(--faint);font-size:12.5px}
.firms li s{text-decoration:none;color:var(--accent);font-size:12px;font-weight:600}
.rgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:20px}
.rg{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;text-decoration:none;display:block}
.rg b{display:block;font-family:'Fraunces',Georgia,serif;font-weight:400;font-size:19px;color:var(--ink)}
.rg span{display:block;font-size:12.5px;color:var(--faint);margin-top:4px}
.back{margin:40px 0 0}
.linkbtn{display:inline-flex;align-items:center;gap:8px;font-size:13px;font-weight:600;color:var(--ink);border:1px solid var(--line);border-radius:999px;padding:9px 16px;text-decoration:none}
.note{margin-top:28px;font-size:12px;color:var(--faint);line-height:1.55;max-width:80ch}
.foot{border-top:1px solid var(--line);margin-top:48px;padding:22px 0 40px;font-size:12px;color:var(--faint);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
.foot a{color:var(--muted);text-decoration:none}
@media(max-width:860px){.wrap{padding:0 22px}h1.disp{font-size:36px}.cards{grid-template-columns:1fr}.firms{columns:2}.rgrid{grid-template-columns:1fr 1fr}.slots{padding:20px}.kpi{gap:22px}}
@media(max-width:560px){.firms{columns:1}.rgrid{grid-template-columns:1fr}.tools input{width:100%}}
"""

HEAD = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITLE}}</title>
<meta name="description" content="{{DESC}}">
<meta property="og:title" content="{{OG}}">
<meta property="og:description" content="{{DESC}}">
<meta property="og:url" content="{{URL}}">
<link rel="canonical" href="{{URL}}">
<style>{{CSS}}</style>
</head>
<body>
<div class="wrap">

  <div class="top">
    <a class="mark" href="/"><i>exit</i><b>.club</b></a>
    <div class="nav">
      <a href="/ecosysteme">L'Écosystème</a>
      <a class="cta" href="https://tally.so/r/wADNZN" target="_blank" rel="noopener">Rejoindre</a>
    </div>
  </div>
"""

FOOT = """
  <div class="foot">
    <div>Exit Club · L'Écosystème de l'Exit · recensement du marché</div>
    <div><a href="/referencement">Se référencer</a> · <a href="mailto:louis@exit.club?subject=Pages%20r%C3%A9gionales%20%C2%B7%20remarque">Un bug, une remarque ? Écrivez-moi</a></div>
  </div>

</div>
</body>
</html>
"""

FILTRE = """
<script>
(function(){
  var q=document.getElementById('q'), items=[].slice.call(document.querySelectorAll('.firms li')),
      blocs=[].slice.call(document.querySelectorAll('.dep')), out=document.getElementById('nres');
  function norm(s){return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();}
  items.forEach(function(li){li.dataset.n=norm(li.textContent);});
  function run(){
    var v=norm(q.value.trim()), n=0;
    items.forEach(function(li){var ok=!v||li.dataset.n.indexOf(v)>=0;li.style.display=ok?'':'none';if(ok)n++;});
    blocs.forEach(function(b){
      var vis=[].slice.call(b.querySelectorAll('.firms li')).some(function(li){return li.style.display!=='none';});
      b.style.display=vis?'':'none';
    });
    out.textContent=v?(n+' cabinet'+(n>1?'s':'')+' trouvé'+(n>1?'s':'')):'';
  }
  q.addEventListener('input',run);
})();
</script>
"""


def page(title, desc, url, body, script=''):
    h = (HEAD.replace('{{TITLE}}', e(title)).replace('{{DESC}}', e(desc))
         .replace('{{OG}}', e(title.split(' | ')[0])).replace('{{URL}}', url)
         .replace('{{CSS}}', CSS))
    return h + body + script + FOOT


# ---------------------------------------------------------------- construction
def cabinets(deps):
    out = []
    for slug, v in GEO.items():
        d = v.get('dep')
        if not d or d not in deps:
            continue
        out.append((slug, v))
    return out


def carte(slug, v, r):
    src = ''
    if r.get('source_url'):
        an = (r.get('date') or '')[:4]
        src = (' · <a href="%s" target="_blank" rel="noopener nofollow">source %s</a>'
               % (e(r['source_url']), e(an)))
    enc = '<span class="enc">%s</span>' % md(r['encours_meur']) if r.get('encours_meur') else ''
    vb = '<span class="vb">✓ Vérifié</span>' if slug in VERIF else ''
    nat = ' · encours %s' % NAT.get(r['nature'], r['nature']) if r.get('nature') else ''
    # un groupement equipe des centaines de cabinets : son encours n'est pas
    # celui du cabinet local. On le dit, sinon le chiffre trompe.
    if 'groupement' in (r.get('note') or '').lower() or r.get('nature') == 'groupe':
        nat += ' · périmètre groupe'
    return ('<div class="cd"><div class="hd"><div><a class="nm" href="/f/%s">%s</a>%s</div>%s</div>'
            '<div class="mt">%s%s%s</div></div>'
            % (e(slug), e(v['nom']), vb, enc,
               e(ville(v.get('commune')) or '—'), nat, src))


TOTAL = len(GEO)
ITOT = 4160                     # institutions de l'Écosystème, toutes catégories
counts = {}      # cabinets de CONSEIL patrimonial, hors courtage declare
LOCALL = 0       # tous les cabinets localises, courtage inclus
for nom, prep, deps in REGIONS:
    _c = cabinets(set(deps.split()))
    LOCALL += len(_c)
    counts[nom] = len([1 for s_, v_ in _c
                       if not courtage(v_['nom']) and not hors(v_['nom'])])

nfiles = 0
for nom, prep, deps in REGIONS:
    dset = set(deps.split())
    cab = sorted(cabinets(dset), key=lambda x: strip(x[1]['nom']))
    if not cab:
        continue
    conseil = [(s, v) for s, v in cab if not courtage(v['nom']) and not hors(v['nom'])]
    crt = [(s, v) for s, v in cab if courtage(v['nom']) and not hors(v['nom'])]
    rslug = slugify(nom)
    nver = sum(1 for s, v in cab if s in VERIF)
    withenc = sorted([(s, v, ENCS[s]) for s, v in cab if s in ENCS],
                     key=lambda x: -(x[2].get('encours_meur') or 0))
    ndep = len({v['dep'] for s, v in conseil})
    nvil = len({v.get('commune') for s, v in conseil if v.get('commune')})
    rest = CGP['places'] - CGP['prises']

    b = ['<div class="crumb"><a href="/ecosysteme">L\'Écosystème de l\'Exit</a> · '
         '<a href="/regions">Régions</a> · <a href="/ecosysteme#cgp">Gestion privée</a></div>']
    b.append('<section class="hero"><p class="over">Gestion privée · %s</p>'
             '<h1 class="disp">L\'Écosystème de l\'Exit <span class="it">%s.</span></h1>'
             '<p class="lede">%d cabinets de conseil en gestion de patrimoine recensés %s, '
             'sur les %s institutions du marché français de la cession. Un fondateur qui vient '
             'de signer arrive ici pour choisir son cabinet.</p></section>'
             % (e(nom), e(prep), len(conseil), e(prep),
                '{:,}'.format(ITOT).replace(',', ' ')))
    b.append('<div class="kpi"><div><b>%d</b><span>cabinets de gestion de patrimoine</span></div>'
             '<div><b>%d</b><span>départements</span></div>'
             '<div><b>%d</b><span>villes</span></div>'
             '<div><b>%d</b><span>encours publiés</span></div>'
             '<div><b>%d</b><span>fiches vérifiées</span></div></div>'
             % (len(conseil), ndep, nvil, len(withenc), nver))

    if nver:
        big = ('%d cabinet%s de la région %s <em>déjà vérifié%s</em>.'
               % (nver, 's' if nver > 1 else '', 'sont' if nver > 1 else 'est',
                  's' if nver > 1 else ''))
    else:
        big = ('Aucun cabinet %s n\'est encore vérifié. <em>Le premier apparaîtra ici, en tête.</em>'
               % e(prep))
    b.append('<div class="slots"><div class="n">%d</div><div class="tx">'
             '<p class="big">%s</p>'
             '<p class="small">%d places de fiches vérifiées sont ouvertes pour 2026 en gestion privée, '
             'toutes régions confondues. %d %s prise%s. Une fiche vérifiée porte le logo, les visages '
             'des associés, l\'expertise post-cession et la prise de rendez-vous directe. '
             'La vérification n\'influence ni la présence dans le recensement, ni l\'ordre '
             'd\'affichage, ni les Ligues.</p></div>'
             '<a class="btn" href="/referencement?cat=cgp&region=%s&demande=verifier">Faire vérifier ma fiche</a>'
             '</div>'
             % (rest, big, CGP['places'], CGP['prises'],
                'est' if CGP['prises'] < 2 else 'sont',
                's' if CGP['prises'] > 1 else '', e(rslug)))

    b.append('<section class="sect"><div class="k">Ce que le marché sait déjà</div>'
             '<h2>Les cabinets qui publient leurs encours.</h2>')
    if withenc:
        b.append('<p class="intro">Encours relevés dans une source publique, datée et liée. '
                 'Les autres cabinets de la région n\'en publient aucun.</p>')
        b.append('<div class="cards">%s</div>'
                 % ''.join(carte(s, v, r) for s, v, r in withenc))
    else:
        b.append('<div class="empty"><p class="f">Aucun cabinet %s ne publie ses encours.</p>'
                 '<p>Le premier qui le fait occupe cette place, seul, en haut de la page '
                 'régionale que consultent les fondateurs en cession.</p></div>' % e(prep))
    b.append('</section>')

    def deps_html(items):
        out = []
        for d in sorted(dset):
            grp = [(s, v) for s, v in items if v['dep'] == d]
            if not grp:
                continue
            li = []
            for s, v in grp:
                extra = ''
                if s in ENCS and ENCS[s].get('encours_meur'):
                    extra = ' <s>%s</s>' % md(ENCS[s]['encours_meur'])
                if s in VERIF:
                    extra += ' <s>✓</s>'
                li.append('<li><a href="/f/%s">%s</a> <i>%s</i>%s</li>'
                          % (e(s), e(v['nom']), e(ville(v.get('commune'))), extra))
            out.append('<div class="dep"><h3>%s (%s) · %d</h3><ul class="firms">%s</ul></div>'
                       % (e(DEPNAME.get(d, d)), e(d), len(grp), ''.join(li)))
        return ''.join(out)

    b.append('<section class="sect"><div class="k">Recensement</div>'
             '<h2>Les %d cabinets de gestion de patrimoine %s.</h2>'
             '<p class="intro">Classés par département, puis par ordre alphabétique. '
             'Être recensé ne vaut pas recommandation.</p>' % (len(conseil), e(prep)))
    b.append('<div class="tools"><input id="q" type="search" placeholder="Chercher un cabinet, une ville">'
             '<span class="hint" id="nres"></span></div>')
    b.append(deps_html(conseil))
    b.append('</section>')

    if crt:
        b.append('<section class="sect"><div class="k">Même catégorie, autre métier</div>'
                 '<h2>Courtage, crédit, financement %s.</h2>'
                 '<p class="intro">%d structures recensées %s dont la raison sociale déclare '
                 'une activité de courtage, de crédit, de financement ou d\'intermédiation '
                 'en assurance. Elles restent publiées : le recensement est ouvert à tous. '
                 'Un fondateur qui cherche un conseil patrimonial regarde la liste du dessus.</p>'
                 % (e(prep), len(crt), e(prep)))
        b.append(deps_html(crt))
        b.append('</section>')

    autres = [(n2, counts[n2]) for n2, p2, d2 in REGIONS if n2 != nom and counts[n2]]
    b.append('<section class="sect"><div class="k">Les autres régions</div>'
             '<h2>Le marché, région par région.</h2><div class="rgrid">%s</div></section>'
             % ''.join('<a class="rg" href="/regions/%s"><b>%s</b><span>%d cabinets</span></a>'
                       % (slugify(n2), e(n2), c) for n2, c in autres))

    b.append('<div class="back"><a class="linkbtn" href="/ecosysteme#cgp">← '
             'Revenir à la catégorie gestion privée</a></div>')
    b.append('<p class="note">Recensement public : la présence dans l\'Écosystème de l\'Exit '
             'est gratuite et ouverte à tous. Être recensé ne vaut pas recommandation de l\'Exit '
             'Club. Localisation issue du registre national des entreprises. Encours issus de '
             'sources publiques datées, jamais d\'une estimation. Une correction ? '
             '<a href="mailto:louis@exit.club?subject=%C3%89cosyst%C3%A8me%20%C2%B7%20correction" '
             'style="color:var(--muted)">Écrivez-moi</a>.</p>')

    t = ('Gestion privée %s : %d cabinets recensés | L\'Écosystème de l\'Exit'
         % (prep, len(conseil)))
    d_ = ('Les %d cabinets de conseil en gestion de patrimoine recensés %s dans '
          'l\'Écosystème de l\'Exit : villes, encours publiés, fiches vérifiées.'
          % (len(conseil), prep))
    open(os.path.join(OUT, rslug + '.html'), 'w', encoding='utf-8').write(
        page(t, d_, 'https://www.exit.club/regions/' + rslug, ''.join(b), FILTRE))
    nfiles += 1
    print('%-30s %4d conseil + %3d courtage · %2d encours · %d vérifiés'
          % (nom, len(conseil), len(crt), len(withenc), nver))

# ---------------------------------------------------------------- index
loc = sum(counts.values())
b = ['<div class="crumb"><a href="/ecosysteme">L\'Écosystème de l\'Exit</a> · Régions</div>']
b.append('<section class="hero"><p class="over">Gestion privée · France</p>'
         '<h1 class="disp">Le marché, <span class="it">région par région.</span></h1>'
         '<p class="lede">%s cabinets de conseil en gestion de patrimoine localisés par le '
         'registre national des entreprises. Chaque page régionale met les cabinets d\'un même '
         'marché côte à côte : ville, encours publiés, fiches vérifiées.</p></section>'
         % '{:,}'.format(loc).replace(',', ' '))
b.append('<div class="kpi"><div><b>%d</b><span>régions</span></div>'
         '<div><b>%s</b><span>cabinets de gestion de patrimoine</span></div>'
         '<div><b>%d</b><span>encours publiés</span></div>'
         '<div><b>%d</b><span>places vérifiées restantes</span></div></div>'
         % (len([1 for n2 in counts if counts[n2]]),
            '{:,}'.format(loc).replace(',', ' '), len(ENCS),
            CGP['places'] - CGP['prises']))
b.append('<section class="sect"><div class="k">Recensement</div>'
         '<h2>Choisissez une région.</h2><div class="rgrid">%s</div></section>'
         % ''.join('<a class="rg" href="/regions/%s"><b>%s</b><span>%d cabinets</span></a>'
                   % (slugify(n2), e(n2), counts[n2])
                   for n2, p2, d2 in REGIONS if counts[n2]))
b.append('<div class="back"><a class="linkbtn" href="/ecosysteme">← '
         'Revenir à l\'Écosystème de l\'Exit</a></div>')
b.append('<p class="note">Localisation issue du registre national des entreprises. '
         '%d cabinets recensés dans l\'Écosystème n\'ont pas de siège identifié avec certitude : '
         'ils ne sont volontairement rattachés à aucune région. Être recensé ne vaut pas '
         'recommandation de l\'Exit Club.</p>' % (TOTAL - LOCALL))
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(
    page('Gestion privée région par région | L\'Écosystème de l\'Exit',
         'Les cabinets de gestion de patrimoine du marché français de la cession, '
         'région par région : villes, encours publiés, fiches vérifiées.',
         'https://www.exit.club/regions', ''.join(b)))

json.dump({slugify(n): {'nom': n, 'prep': p, 'n': counts[n]}
           for n, p, d in REGIONS if counts[n]},
          open('_build/regions/index.json', 'w'), ensure_ascii=False, indent=1)
print('%d pages régionales + index · %d cabinets localisés sur %d' % (nfiles, loc, TOTAL))
