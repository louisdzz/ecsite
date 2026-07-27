# -*- coding: utf-8 -*-
"""Rattrapage manuel des logos des grandes maisons : le domaine est saisi à la
main (donc vérifié), les filtres automatiques de parenté de fichier sont donc
levés. Le contrôle se fait ensuite à l'oeil sur une planche-contact.
Sortie : assets/logos/dir/<slug>.webp + fusion dans dir-meta.json
"""
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)
sys.path.insert(0, '_build/logos')
from fetch import candidates, get, EXT  # noqa
import proc  # réutilise load/trim/flat/profile  # noqa

RAW = '/root/logoraw/rescue'
os.makedirs(RAW, exist_ok=True)

# slug -> domaine saisi à la main
DOM = {
    'rothschild-co': 'rothschildandco.com',
    'rothschild-martin-maurel': 'rothschildandco.com',
    'oddo-bhf': 'oddo-bhf.com',
    'oddo-bhf-pwm': 'oddo-bhf.com',
    'houlihan-lokey': 'hl.com',
    'deutsche-bank': 'db.com',
    'jefferies': 'jefferies.com',
    'kepler-cheuvreux': 'keplercheuvreux.com',
    'bredin-prat': 'bredinprat.com',
    'latham-watkins': 'lw.com',
    'freshfields': 'freshfields.com',
    'white-case': 'whitecase.com',
    'weil-gotshal-manges': 'weil.com',
    'august-debouzy': 'august-debouzy.com',
    'franklin': 'franklin-paris.com',
    'kirkland-ellis': 'kirkland.com',
    'cleary-gottlieb': 'clearygottlieb.com',
    'kkr': 'kkr.com',
    'apax-partners': 'apax.fr',
    'bpifrance': 'bpifrance.fr',
    'idi': 'idi.fr',
    'montefiore-investment': 'montefiore.fr',
    'seven2': 'seven2.com',
    'sofinnova-partners': 'sofinnovapartners.com',
    'xange': 'xange.vc',
    'breega': 'breega.com',
    'kurma-partners': 'kurmapartners.com',
    'eqt': 'eqtgroup.com',
    'blackstone-europe-llp': 'blackstone.com',
    'naxicap-partners': 'naxicap.fr',
    'lbo-france': 'lbofrance.com',
    'activa-capital': 'activacapital.com',
    'lombard-odier': 'lombardodier.com',
    'pictet-wealth-management': 'pictet.com',
    'groupe-crystal': 'groupe-crystal.com',
    'nortia': 'nortia.fr',
    'primonial': 'primonial.fr',
    'astoria-finance': 'astoria-finance.fr',
    'uff': 'uff.net',
    'herest': 'herest.fr',
    'kimpa': 'kimpa.com',
    'rothschild-co-martin-maurel': 'rothschildandco.com',
    # deuxième salve
    'morgan-stanley': 'morganstanley.com',
    'citigroup': 'citigroup.com',
    'bnp-paribas-cib': 'cib.bnpparibas',
    'bnp-paribas-banque-privee': 'mabanqueprivee.bnpparibas',
    'bnp-paribas-asset-management': 'bnpparibas-am.com',
    'clearwater-international': 'clearwaterinternational.com',
    'dc-advisory': 'dcadvisory.com',
    'goodwin-procter-france': 'goodwinlaw.com',
    'dentons': 'dentons.com',
    'partners-group': 'partnersgroup.com',
    'tikehau-capital': 'tikehaucapital.com',
    'icg': 'icgam.com',
    'pemberton-asset-management': 'pembertonam.com',
    'cyrus-herez': 'cyrusconseil.fr',
    'rockfi': 'rockfi.fr',
    'natixis-investment-managers': 'im.natixis.com',
    'lombard-odier': 'lombardodier.com',
    # troisième salve : logos faux repérés sur la planche du mur
    'goldman-sachs': 'goldmansachs.com',
    'natixis-partners': 'natixispartners.com',
    'alantra': 'alantra.com',
    'darrois-villey': 'darroisvilley.com',
    'gide-loyrette-nouel': 'gide.com',
    'hogan-lovells': 'hoganlovells.com',
    'dechert-llp': 'dechert.com',
    'bridgepoint': 'bridgepoint.eu',
    'pai-partners': 'paipartners.com',
}

# rejetés à la relecture visuelle : mauvaise marque ou pas un logo
SKIP = {'freshfields', 'xange', 'seven2', 'primonial', 'kimpa',
        'rothschild-martin-maurel', 'lombard-odier', 'goldman-sachs',
        'natixis-partners', 'alantra', 'bridgepoint', 'dechert-llp',
        'degroof-petercam-cf', 'degroof-petercam'}


import fetch as _f
CHROME = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
          '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')


def grab(slug, domain):
    for ua in (_f.UA, CHROME):
        _f.UA = ua
        f, u = _grab(slug, domain)
        if f:
            return f, u
    return None, None


def _grab(slug, domain):
    for base in ('https://www.%s/' % domain, 'https://%s/' % domain):
        try:
            html, ct, final = get(base, timeout=15)
        except Exception:
            continue
        html = html.decode('utf-8', 'ignore')
        for u in candidates(html, final)[:8]:
            if proc.banned(u):
                continue
            low = u.lower()
            own = ('favicon' in low or 'apple-touch' in low or 'touch-icon' in low)
            if not own and not proc.related({'src': u, 'nom': slug.replace('-', ' '),
                                             'domain': domain}):
                continue
            try:
                data, ct2, _ = get(u, timeout=15)
            except Exception:
                continue
            ext = EXT.get(ct2.split(';')[0].strip().lower())
            if not ext or (len(data) < 300 and ext != '.svg') or len(data) > 2_000_000:
                continue
            f = os.path.join(RAW, slug + ext)
            open(f, 'wb').write(data)
            return f, u
    return None, None


META = '_build/logos/dir-meta.json'
meta = json.load(open(META))
NOMS = {}
import glob
for p in sorted(glob.glob('_build/domains/*-*.json')):
    for s, v in json.load(open(p)).items():
        NOMS.setdefault(s, v['nom'])

ok, ko = 0, []
for slug, domain in sorted(DOM.items()):
    if slug in SKIP:
        continue
    f, src = grab(slug, domain)
    if not f:
        ko.append(slug + ':injoignable')
        continue
    try:
        im = proc.load(f)
    except Exception as e:
        ko.append(slug + ':illisible')
        continue
    im = proc.trim(im)
    w, h = im.size
    # les wordmarks de cabinets d'avocats sont naturellement très larges
    if w < 20 or h < 8 or w / h > 22 or h / w > 5:
        ko.append('%s:forme %dx%d' % (slug, w, h))
        continue
    if proc.flat(im):
        ko.append(slug + ':uni')
        continue
    sc = min(proc.MAX / w, proc.MAX / h, 1.0)
    if sc < 1.0:
        from PIL import Image
        im = im.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.LANCZOS)
    transp, l = proc.profile(im)
    out = os.path.join('assets/logos/dir', slug + '.webp')
    im.save(out, 'WEBP', quality=82, method=5)
    meta[slug] = {'f': '/' + out, 'dark': bool(transp > .30 and l > 185),
                  'wide': bool(im.size[0] / im.size[1] > 2.2),
                  'xwide': bool(im.size[0] / im.size[1] > 6.5),
                  'w': im.size[0], 'h': im.size[1],
                  'nom': NOMS.get(slug, slug), 'src': src, 'rescue': True}
    ok += 1

json.dump(meta, open(META, 'w'), ensure_ascii=False, indent=0)
print('rattrapés : %d / %d' % (ok, len(DOM)))
print('échecs :', ko)
