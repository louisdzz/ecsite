# -*- coding: utf-8 -*-
"""Normalise les logos bruts : rognage, redimensionnement, webp, détection des
logos clairs qui ont besoin d'un fond sombre, rejet des icônes génériques.
Entrée  : /root/logoraw/*  +  _build/logos/raw-state.json
Sortie  : assets/logos/dir/<slug>.webp
          _build/logos/dir-meta.json  {slug:{"f","dark","wide","w","h"}}
"""
import hashlib, io, json, os, re, sys
from collections import Counter
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)
OUT = 'assets/logos/dir'
os.makedirs(OUT, exist_ok=True)
MAX = 192

state = json.load(open('_build/logos/raw-state.json'))
rows = {s: v for s, v in state.items() if v and os.path.exists(v['file'])}

# domaines écartés par la deuxième passe de vérification : pas de logo non plus
VP = '_build/domains/verdict.json'
DROP = ({s for s, v in json.load(open(VP)).items() if not v['ok']}
        if os.path.exists(VP) else set())

# --- icônes génériques : même octet exact chez plusieurs institutions
def generiques():
    h2s = {}
    for s, v in rows.items():
        try:
            h = hashlib.sha1(open(v['file'], 'rb').read()).hexdigest()
        except Exception:
            continue
        h2s.setdefault(h, []).append(s)
    return {s for h, ss in h2s.items() if len(ss) >= 4 for s in ss}


# --- logos qui ne sont pas celui de la maison : réseaux sociaux, labels,
# moyens de paiement, associations professionnelles, icônes PWA génériques.
BAN_WORD = re.compile(
    r'\b(facebook|fb|google|amazon|aws|twitter|linkedin|instagram|youtube|whatsapp|tiktok'
    r'|qualiopi|trustindex|trustpilot|avis[-_]?verifies|orias|cncgp|anacofi|cnb|afg'
    r'|bose|dell|pasteur|wordpress|wpml|visa|mastercard|paypal|stripe|applepay|apple[-_]pay'
    r'|logo192|logo512|android[-_]chrome|placeholder|default|sedo|buffer'
    r'|b[-_]?corp|bcorporation|certified|great[-_]?place|ecovadis|iso9001|texture)\b', re.I)
BAN_PATH = re.compile(r'/(partenaires?|clients?|references?|badges?|labels?|awards?|'
                      r'certifications?|logos[-_]partenaires)/', re.I)


def banned(src):
    seg = src.split('?')[0].rsplit('/', 1)[-1]
    seg = re.sub(r'[^A-Za-z0-9]+', ' ', seg)
    return bool(BAN_WORD.search(seg) or BAN_PATH.search(src))


sys.path.insert(0, '_build/domains')
from resolve import words, STOP  # noqa


def related(v):
    """Le fichier doit s'appeler 'logo', ou citer le domaine, ou un mot du nom.
    Écarte les logos de partenaires posés sur une page par ailleurs correcte."""
    src = v['src'].lower()
    seg = src.split('?')[0].rsplit('/', 1)[-1]
    flat_src = re.sub(r'[^a-z0-9]', '', src)
    base = v['domain'].rsplit('.', 1)[0].replace('-', '')
    if 'logo' in seg:
        return True
    if len(base) >= 6 and base[:6] in flat_src:
        return True
    return any(w in flat_src for w in words(v['nom']) if w not in STOP and len(w) > 3)


def load(path):
    if path.lower().endswith('.svg'):
        import cairosvg, html as _html
        raw = open(path, 'rb').read()
        if len(raw) < 120:
            raise ValueError('svg tronqué')
        txt = raw.decode('utf-8', 'ignore')
        if '&#39;' in txt[:400] or '&quot;' in txt[:400]:   # svg sorti d'un attribut HTML
            txt = _html.unescape(txt)
        png = cairosvg.svg2png(bytestring=txt.encode('utf-8'), output_width=MAX * 2)
        return Image.open(io.BytesIO(png)).convert('RGBA')
    im = Image.open(path)
    if getattr(im, 'n_frames', 1) > 1:          # .ico multi-tailles
        best, area = None, -1
        for i in range(im.n_frames):
            im.seek(i)
            if im.size[0] * im.size[1] > area:
                area = im.size[0] * im.size[1]
                best = im.convert('RGBA')
        return best
    return im.convert('RGBA')


def trim(im):
    a = im.split()[3]
    bb = a.getbbox() if a.getextrema()[0] < 250 else None
    if bb is None:                               # opaque : rogner sur la couleur de bord
        rgb = im.convert('RGB')
        bg = rgb.getpixel((0, 0))
        from PIL import ImageChops
        diff = ImageChops.difference(rgb, Image.new('RGB', rgb.size, bg)).convert('L')
        bb = diff.point(lambda p: 255 if p > 18 else 0).getbbox()
    if bb and bb[2] - bb[0] > 3 and bb[3] - bb[1] > 3:
        im = im.crop(bb)
    return im


def flat(im):
    """True si l'image est quasiment unie (donc inutilisable).
    Sur un logo à fond transparent, c'est la silhouette alpha qu'il faut juger :
    convertir en RGB écraserait le transparent en noir et ferait passer un
    wordmark fin pour une image unie."""
    a = im.split()[3]
    if a.getextrema()[0] < 250:                 # il y a de la transparence
        q = a.resize((16, 16))
        c = Counter(q.getdata())
        return c.most_common(1)[0][1] > 244
    q = im.convert('RGB').resize((16, 16))
    c = Counter(q.getdata())
    return c.most_common(1)[0][1] > 230


def photoish(im):
    """True si l'image ressemble à une photo (og:image de bandeau) et non à un logo."""
    q = im.convert('RGB').resize((48, 48))
    return len(set(q.getdata())) > 620


def profile(im):
    px = im.getdata()
    n = tot = lum = 0
    for r, g, b, a in px:
        tot += 1
        if a < 40:
            n += 1
        else:
            lum += .299 * r + .587 * g + .114 * b
    op = tot - n
    return (n / tot if tot else 0), (lum / op if op else 0)


def run():
  GENERIC = generiques()
  meta, ko = {}, Counter()
  for slug, v in sorted(rows.items()):
      if slug in GENERIC:
          ko['générique'] += 1
          continue
      if slug in DROP:
          ko['domaine non confirmé'] += 1
          continue
      if banned(v['src']):
          ko['logo tiers'] += 1
          continue
      if not related(v):
          ko['fichier sans rapport'] += 1
          continue
      try:
          im = load(v['file'])
      except Exception:
          ko['illisible'] += 1
          continue
      if im.size[0] < 24 or im.size[1] < 24:
          ko['trop petit'] += 1
          continue
      im = trim(im)
      w, h = im.size
      if w < 20 or h < 12 or w / h > 9 or h / w > 5:
          ko['forme'] += 1
          continue
      if flat(im):
          ko['uni'] += 1
          continue
      if 'logo' not in v['src'].lower() and photoish(im):
          ko['photo'] += 1
          continue
      sc = min(MAX / w, MAX / h, 1.0)
      if sc < 1.0:
          im = im.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.LANCZOS)
      transp, l = profile(im)
      f = os.path.join(OUT, slug + '.webp')
      im.save(f, 'WEBP', quality=82, method=5)
      meta[slug] = {'f': '/' + f, 'dark': bool(transp > .30 and l > 185),
                    'wide': bool(im.size[0] / im.size[1] > 2.2),
                    'w': im.size[0], 'h': im.size[1], 'nom': v['nom']}

  json.dump(meta, open('_build/logos/dir-meta.json', 'w'), ensure_ascii=False, indent=0)
  print('%d logos retenus · rejets %s' % (len(meta), dict(ko)))
  print('fond sombre requis : %d · wordmarks larges : %d'
        % (sum(1 for m in meta.values() if m['dark']), sum(1 for m in meta.values() if m['wide'])))


if __name__ == '__main__':
    run()
