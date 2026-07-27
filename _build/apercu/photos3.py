# -*- coding: utf-8 -*-
"""Troisième passe : rattachement STRUCTUREL sur les pages équipe.

Beaucoup de cabinets sont sur Wix, Webflow ou un thème WordPress qui nomme les
images en hash (932808_82dac...mv2.png, 666d9e7e_photo21.jpg). Le nom de
fichier ne dira jamais qui est sur la photo. Mais la page, elle, le dit : une
grille d'équipe met l'image juste avant le nom.

Règle retenue, volontairement étroite : on accepte une image pour une personne
seulement si cette image est la dernière balise img avant l'occurrence du nom,
ET qu'aucun autre nom de l'équipe ne se trouve entre les deux. Autrement dit
l'image appartient à la carte de cette personne et d'aucune autre.

Chaque photo retenue est journalisée avec la légende lue autour de l'image :
_build/apercu/photos-audit.txt, relu à la main avant publication.
"""
import json, os, re, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import photos as P
os.chdir(ROOT)

STORE = '_build/apercu/photos.json'
AUDIT = '_build/apercu/photos-audit.txt'
WIN = 2600          # distance max entre l'image et le nom, en caracteres de HTML


def txt(html, a, b):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html[a:b])).strip()


def occurrences(html, noms):
    """[(position, nom)] pour chaque mention prenom+nom dans la page."""
    plat = P.strip(html)
    out = []
    for n in noms:
        pre, fam = P.nomparts(n)
        if not fam:
            continue
        if pre:
            pat = r'%s\W{0,60}%s' % (re.escape(pre[0]), re.escape(fam[0]))
        else:
            pat = re.escape(fam[0])
        for m in re.finditer(pat, plat):
            out.append((m.start(), n))
    return sorted(out)


def cartes(html, noms):
    """{nom: (url_relative, legende)} par rattachement de carte."""
    occ = occurrences(html, noms)
    if not occ:
        return {}
    tags = [(m.start(), m.group(0)) for m in re.finditer(r'<img\b[^>]*>', html, re.I)]
    res = {}
    for i, (pos, nom) in enumerate(occ):
        prev = occ[i - 1][0] if i else -1
        cand = [(p, t) for p, t in tags if prev < p < pos and pos - p <= WIN]
        if not cand:
            continue
        p, tag = cand[-1]                      # la derniere image avant le nom
        src = re.search(r'\b(?:data-src|data-lazy-src|src)=["\']([^"\']+)["\']', tag)
        if not src:
            continue
        u = src.group(1)
        if u.startswith('data:') or P.BADIMG.search(u):
            continue
        # garde-fou : un fichier qui porte le nom ou le prenom d'un AUTRE associe
        # n'est pas la photo de celui-ci (Christophe-551x500.jpg pour Gregory).
        seg = P.strip(urllib.parse.unquote(u.split('?')[0].rsplit('/', 1)[-1]))
        seg = re.sub(r'[^a-z0-9]+', ' ', seg)
        autre = False
        for o in noms:
            if o == nom:
                continue
            for part in [x for x in sum(P.nomparts(o), []) if len(x) >= 4]:
                if re.search(r'\b%s' % re.escape(part), seg):
                    autre = True
        if autre:
            continue
        if nom in res:
            continue
        res[nom] = (u, txt(html, p, pos + 90)[-150:])
    return res


if __name__ == '__main__':
    src = open('_build/apercu/gen.py', encoding='utf-8').read()
    ns = {}
    exec(src[src.index('D = {'):src.index('\nMODULES')], {'dict': dict}, ns)
    D = ns['D']
    S = json.load(open('_build/enrich/salve1.json'))
    site_of = {c['nom'].split(' (')[0]: c.get('site') for c in S}
    IDX = json.load(open('_build/apercu/index.json'))
    have = json.load(open(STORE)) if os.path.exists(STORE) else {}

    log = []
    for nom, v in IDX.items():
        slug = v['slug']
        manque = [x[0] for x in D[nom]['equipe'] if '%s|%s' % (slug, x[0]) not in have]
        s = site_of.get(nom)
        if not manque or not s:
            continue
        if not s.startswith('http'):
            s = 'https://' + s
        pp = P.pages(s)
        got, res = set(), {}
        for base, html in pp:
            rest = [x for x in manque if x not in got]
            if not rest:
                break
            for n, (rel, leg) in cartes(html, rest).items():
                u = urllib.parse.urljoin(base, rel)
                if P.save(slug, n, u, res, got, 'carte'):
                    log.append('%-30s | %-24s | %s\n    legende lue : %s\n    fichier    : %s'
                               % (nom, n, base[:60], leg, u[:110]))
        have.update(res)
        print('%-30s %d/%d' % (nom, len(res), len(manque)), flush=True)

    json.dump(have, open(STORE, 'w'), ensure_ascii=False, indent=0)
    open(AUDIT, 'w', encoding='utf-8').write('\n'.join(log))
    print('total portraits : %d' % len(have))
