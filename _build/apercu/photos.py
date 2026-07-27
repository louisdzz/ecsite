# -*- coding: utf-8 -*-
"""Récupère les portraits des associés sur le SITE DU CABINET lui-même.
On ne touche pas à LinkedIn : la photo d'une page « notre équipe » est publiée
par le cabinet, donc utilisable, et c'est celle que l'associé a choisie.

Règle de précision, non négociable : une photo n'est retenue que si le nom de
fichier ou l'attribut alt porte le NOM DE FAMILLE de la personne. Un mauvais
visage sur la fiche d'un dirigeant serait humiliant ; une case vide ne coûte
rien. En cas de doute, on rejette et le monogramme reste.

Sortie : assets/photos/apercu/<slug>--<personne>.webp (240x240)
         _build/apercu/photos.json  {"<slug>|<Nom Prénom>": "/assets/..."}
"""
import io, json, os, re, sys, unicodedata, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)
OUT = 'assets/photos/apercu'
os.makedirs(OUT, exist_ok=True)
STORE = '_build/apercu/photos.json'

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')

EQUIPE = re.compile(r'equipe|team|qui-sommes|qui_sommes|associes|associ%C3%A9s|nos-conseillers|'
                    r'le-cabinet|notre-cabinet|a-propos|about|conseillers|fondateur|direction',
                    re.I)
BADIMG = re.compile(r'logo|favicon|sprite|icon|banner|bandeau|placeholder|orias|cncgp|anacofi'
                    r'|qualiopi|avis|trustpilot|linkedin|facebook|twitter|instagram', re.I)


# jetons techniques ou descriptifs qui ne désignent pas une personne
TECH = """scaled copie copy final photo portrait portraits equipe team site web jpeg jpg
png webp avif image images retouche retouches uploads content petit grand large small
medium thumb thumbnail crop cropped noir blanc couleur monsieur madame mme conseiller
conseillere associe associee gerant gerante fondateur fondatrice directeur directrice
president presidente cabinet bureau photos min def hdef versionfinale nouveau new"""


def strip(s):
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


def get(url, timeout=14):
    req = urllib.request.Request(url, headers={'User-Agent': UA,
                                               'Accept-Language': 'fr,en;q=0.8'})
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read(4_000_000), r.headers.get('Content-Type', ''), r.geturl()


def pages(site):
    """Page d'accueil + les pages internes qui ressemblent à une page équipe."""
    try:
        raw, ct, final = get(site)
    except Exception:
        return []
    html = raw.decode('utf-8', 'ignore')
    host = urllib.parse.urlparse(final).netloc
    out = [(final, html)]
    seen = {final.rstrip('/')}
    cand = []
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\'#]+)["\'][^>]*>(.{0,120}?)</a>', html, re.S | re.I):
        href, txt = m.group(1), re.sub(r'<[^>]+>', ' ', m.group(2))
        u = urllib.parse.urljoin(final, href)
        if urllib.parse.urlparse(u).netloc != host:
            continue
        if u.rstrip('/') in seen or re.search(r'\.(pdf|jpg|png|zip|docx?)$', u, re.I):
            continue
        if EQUIPE.search(href) or EQUIPE.search(txt):
            seen.add(u.rstrip('/'))
            cand.append(u)
    for u in cand[:7]:
        try:
            raw, ct, fin = get(u)
            out.append((fin, raw.decode('utf-8', 'ignore')))
        except Exception:
            pass
    return out


def images(base, html):
    """Toutes les URL d'images de la page, avec le alt quand il existe."""
    found = []
    for m in re.finditer(r'<img\b([^>]*)>', html, re.I):
        a = m.group(1)
        src = re.search(r'\b(?:data-src|data-lazy-src|src)=["\']([^"\']+)["\']', a)
        alt = re.search(r'\balt=["\']([^"\']*)["\']', a)
        if src:
            found.append((urllib.parse.urljoin(base, src.group(1)),
                          alt.group(1) if alt else ''))
        ss = re.search(r'\bsrcset=["\']([^"\']+)["\']', a)
        if ss:
            for part in ss.group(1).split(','):
                u = part.strip().split(' ')[0]
                if u:
                    found.append((urllib.parse.urljoin(base, u),
                                  alt.group(1) if alt else ''))
    for m in re.finditer(r'background-image\s*:\s*url\(["\']?([^"\')]+)', html, re.I):
        found.append((urllib.parse.urljoin(base, m.group(1)), ''))
    return found


def nomparts(nom):
    """(prénoms, noms de famille) en minuscules sans accents, >= 4 lettres."""
    p = [strip(x) for x in re.split(r'[\s\-]+', nom) if len(x) > 1]
    return p[:-1], [p[-1]] if p else []


def match(url, alt, nom, cabinet):
    """Le fichier ou le alt doit porter le nom de famille. Sinon on refuse."""
    seg = urllib.parse.unquote(url.split('?')[0].rsplit('/', 1)[-1])
    hay = strip(seg + ' ' + alt)
    hay = re.sub(r'[^a-z0-9]+', ' ', hay)
    if BADIMG.search(seg) or BADIMG.search(alt):
        return False
    pre, fam = nomparts(nom)
    if not fam:
        return False
    f = fam[0]
    if len(f) < 4:
        return False
    # un patronyme qui est aussi dans la raison sociale (Tanguy Finances) ne
    # prouve rien à lui seul : on exige alors aussi le prénom
    ambigu = f in strip(cabinet)
    hit_f = re.search(r'\b%s' % re.escape(f), hay) is not None
    hit_p = any(len(x) >= 4 and re.search(r'\b%s' % re.escape(x), hay) for x in pre)
    if not hit_f or (ambigu and not hit_p):
        return False
    if hit_p:
        return True
    # le patronyme seul ne suffit pas si le fichier nomme QUELQU'UN D'AUTRE :
    # "Laurence-MARTINEZ.png" n'est pas la photo de Sébastien Martinez.
    tech = set(TECH.split()) | set(re.split(r'[^a-z0-9]+', strip(cabinet)))
    intrus = [t for t in hay.split()
              if len(t) >= 4 and t != f and t not in tech and not t.isdigit()
              and not re.fullmatch(r'\d+x\d+|[a-z]?\d+', t)]
    return not intrus


def proches(html, noms):
    """Deuxième passe : beaucoup de pages « notre équipe » nomment leurs images
    equipe-1.jpg. On rattache alors une image à une personne par la PROXIMITÉ
    dans le HTML : le nom doit apparaître juste après la balise <img>, et être
    le nom le plus proche de cette balise. Renvoie {nom: url}.
    """
    plat = strip(html)
    pos = {}
    for n in noms:
        pre, fam = nomparts(n)
        if not fam:
            continue
        pat = r'%s\W{0,40}%s' % (re.escape(pre[0]), re.escape(fam[0])) if pre else re.escape(fam[0])
        m = list(re.finditer(pat, plat))
        if len(m) == 1:                      # ambigu si le nom apparaît partout
            pos[n] = m[0].start()
    if not pos:
        return {}
    tags = [(m.start(), m.group(0)) for m in re.finditer(r'<img\b[^>]*>', html, re.I)]
    out = {}
    for n, p in pos.items():
        best, bd = None, 10 ** 9
        for i, tag in tags:
            d = p - i
            if 0 < d < 700 and d < bd:       # l'image précède le nom
                best, bd = tag, d
        if not best:
            continue
        # le nom retenu doit être le plus proche de cette image
        if any(abs(pos[o] - (p - bd)) < bd for o in pos if o != n):
            continue
        src = re.search(r'\b(?:data-src|data-lazy-src|src)=["\']([^"\']+)["\']', best)
        if src and not BADIMG.search(src.group(1)):
            out[n] = src.group(1)
    return out


def portrait(data):
    im = Image.open(io.BytesIO(data))
    im = im.convert('RGB')
    w, h = im.size
    if min(w, h) < 110 or not (0.5 <= w / h <= 1.9):
        raise ValueError('forme %dx%d' % (w, h))
    if len(set(im.resize((48, 48)).getdata())) < 900:      # aplat = pas une photo
        raise ValueError('pas une photo')
    s = min(w, h)
    left = (w - s) // 2
    top = int((h - s) * 0.18)                              # la tête est en haut
    im = im.crop((left, top, left + s, top + s)).resize((240, 240), Image.LANCZOS)
    return im


def save(slug, nom, u, res, got, src):
    try:
        data, ct, _ = get(u)
        if len(data) < 1200:
            return False
        im = portrait(data)
    except Exception:
        return False
    pslug = re.sub(r'[^a-z0-9]+', '-', strip(nom)).strip('-')
    f = os.path.join(OUT, '%s--%s.webp' % (slug, pslug))
    im.save(f, 'WEBP', quality=84, method=5)
    res['%s|%s' % (slug, nom)] = {'f': '/' + f, 'src': u, 'via': src}
    got.add(nom)
    return True


def one(slug, cabinet, gens):
    res = {}
    got = set()
    pp = pages(cabinet_site[cabinet])
    # passe 1 : le nom de famille est dans le nom de fichier ou le alt
    for base, html in pp:
        for nom in [n for n in gens if n not in got]:
            for u, alt in images(base, html):
                if match(u, alt, nom, cabinet) and save(slug, nom, u, res, got, 'nom'):
                    break
    # passe 2 : rattachement par proximité dans le HTML
    for base, html in pp:
        rest = [n for n in gens if n not in got]
        if not rest:
            break
        for nom, rel in proches(html, rest).items():
            save(slug, nom, urllib.parse.urljoin(base, rel), res, got, 'proximité')
    return res


if __name__ == '__main__':
    sys.path.insert(0, '_build/apercu')
    import importlib.util
    spec = importlib.util.spec_from_file_location('g', '_build/apercu/gen.py')
    # gen.py écrit des fichiers à l'import : on relit juste ses tables en texte
    src = open('_build/apercu/gen.py', encoding='utf-8').read()
    ns = {}
    exec(src[src.index('D = {'):src.index('\nMODULES')], {'dict': dict}, ns)
    D = ns['D']
    S = json.load(open('_build/enrich/salve1.json'))
    cabinet_site = {c['nom'].split(' (')[0]: c.get('site') for c in S}
    IDX = json.load(open('_build/apercu/index.json'))

    jobs = [(v['slug'], nom, [x[0] for x in D[nom]['equipe']])
            for nom, v in IDX.items() if cabinet_site.get(nom)]
    out = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(lambda a: one(*a), jobs):
            out.update(r)
    json.dump(out, open(STORE, 'w'), ensure_ascii=False, indent=0)
    print('portraits trouvés : %d' % len(out))
    for k, v in sorted(out.items()):
        print('  %-52s %-12s %s' % (k, v['via'], v['src'][:70]))
