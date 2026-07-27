# -*- coding: utf-8 -*-
"""Crée la catégorie « Experts-comptables & auditeurs » de l'Écosystème.

- lit _build/experts-comptables/sourced.json (noms + domaines vérifiés, source par entrée)
- génère une fiche /f/<slug>.html par cabinet à partir de _build/fiche_template.html
- injecte la section <section class="cat" id="experts-comptables"> dans ecosysteme.html
- ajoute l'entrée dans _build/places.json et les URL dans sitemap.xml
Idempotent : relançable sans doublon.
"""
import json, re, os, unicodedata
from urllib.parse import quote

CAT_ID = 'experts-comptables'
CAT_LABEL = "Experts-comptables &amp; auditeurs"
CAT_LABEL_TXT = "Experts-comptables & auditeurs"
CDESC = ("Audit des comptes, évaluation, vendor due diligence et fiscalité du "
         "dirigeant : avant la cession comme après.")
PLACES = 6

# groupements / instances : pas des cabinets que l'on mandate
EXCLUS = {'ATH', 'CGCI (Comité des Groupements de Cabinets Indépendants)'}

GROUPEMENTS = {'Absoluce', 'France Défi', 'Eurus', 'Synerga', 'Audécia',
               'Talenz', 'Walter France', 'Exco', 'HLB France', 'PKF France',
               'Crowe France', 'Moore France', 'Cerfrance'}

DESC_SPEC = {
    'Finexsi': "Expertise et conseil financier indépendants : évaluation d'entreprise, attestation d'équité, expertise indépendante.",
    'Ledouble': "Experts financiers indépendants : évaluation d'entreprise et fairness opinion.",
    'Exelmans Audit & Conseil': "Cabinet d'audit et de conseil dédié aux fonds d'investissement et aux entrepreneurs.",
    'Advolis Orfis': "Commissariat aux comptes, aux apports et à la fusion, fiscalité de l'entreprise et du dirigeant.",
    'Primexis': "Expertise comptable et financière des groupes internationaux et des fonds d'investissement.",
    'RYDGE Conseil': "Expertise comptable, audit et conseil, avec une offre dédiée à la cession et à la transmission d'entreprise.",
    'TGS France': "Groupe pluridisciplinaire d'expertise comptable, d'audit et de conseil, avec une offre dédiée à la transmission d'entreprise.",
}


def slugify(s):
    s = s.replace('&', ' et ').replace("'", ' ').replace('’', ' ')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return re.sub(r'-+', '-', s)


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def desc(e):
    n = e['nom']
    if n in DESC_SPEC:
        return DESC_SPEC[n]
    if n in GROUPEMENTS:
        return "Groupement ou réseau national de cabinets d'expertise comptable et de commissariat aux comptes indépendants."
    base = "Cabinet d'expertise comptable et d'audit"
    if e.get('reseau'):
        base += ", membre du réseau %s" % e['reseau']
    base += '.'
    if e.get('ville'):
        base += " Siège à %s." % e['ville']
    return base


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

DATA = json.load(open('_build/experts-comptables/sourced.json', encoding='utf-8'))
FIRMS = []
seen = set()
for e in DATA:
    if e['nom'] in EXCLUS:
        continue
    sl = slugify(e['nom'])
    if sl in seen:
        continue
    seen.add(sl)
    e['slug'] = sl
    FIRMS.append(e)
FIRMS.sort(key=lambda e: e['nom'].lower())
print(len(FIRMS), 'cabinets retenus')

# ---------- 1. fiches ----------
T = open('_build/fiche_template.html', encoding='utf-8').read()
CARD = ('\n  <div class="card"><div class="k">Repères</div><p>%s</p>%s</div>\n')
written = 0
for e in FIRMS:
    nom, sl = e['nom'], e['slug']
    nom_h = esc(nom)
    site = e.get('site')
    lien = ''
    if site:
        url = 'https://' + site if not site.startswith('http') else site
        lien = ('<p style="margin-top:10px;font-size:13px"><a href="%s" target="_blank" '
                'rel="noopener nofollow">%s</a> · <a href="https://www.linkedin.com/'
                'search/results/companies/?keywords=%s" target="_blank" rel="noopener '
                'nofollow">LinkedIn</a></p>' % (url, esc(site), quote(nom)))
    mailto = ('/referencement?institution=%s&cat=%s&fiche=%s&demande=referencer'
              % (quote(nom), CAT_ID, sl))
    h = T
    for k, v in [('__CAT_ID__', CAT_ID), ('__CAT_LABEL__', CAT_LABEL),
                 ('__CATS_TEXT__', 'la catégorie ' + CAT_LABEL),
                 ('__NOM__', nom_h), ('__NOM_ATTR__', nom_h),
                 ('__NOM_Q__', quote(nom)), ('__SLUG__', sl),
                 ('__MAILTO__', mailto),
                 ('__TAGS__', '<a class="tag" href="/ecosysteme#%s">%s</a>'
                  % (CAT_ID, CAT_LABEL))]:
        h = h.replace(k, v)
    # carte Repères juste après le hero
    anchor = '  </section>\n'
    i = h.find('</section>')
    i = h.index('\n', i) + 1
    h = h[:i] + CARD % (esc(desc(e)), lien) + h[i:]
    open('f/%s.html' % sl, 'w', encoding='utf-8').write(h)
    written += 1
print(written, 'fiches écrites dans f/')

# ---------- 2. section catégorie ----------
lis = '\n'.join('      <li><a href="/f/%s">%s</a></li>' % (e['slug'], esc(e['nom']))
                for e in FIRMS)
SEC = """<section class="cat" id="{cid}">
    <div class="ch">
      <div><h3>{label}</h3><p class="cdesc">{cdesc}</p></div>
      <div class="count"><b>{n}</b> référencés</div>
    </div>
    <!--SLOTS:START--><p class="slotline"><b>{pl} places</b> de fiche vérifiée restantes sur {pl} ouvertes pour 2026<a href="/referencement?cat={cid}&demande=verifier">Faire vérifier ma fiche</a></p><!--SLOTS:END-->
    <ul class="firms">
{lis}
    </ul>
    <div class="cta">
      <a class="linkbtn" href="/referencement?cat={cid}&demande=referencer">Vous ne figurez pas dans la liste ? Faites-vous référencer, c'est gratuit →</a>
      <a class="linkbtn" href="/referencement?cat={cid}&demande=verifier">Faire vérifier ma fiche →</a>
    </div>
  </section>
  """.format(cid=CAT_ID, label=CAT_LABEL, cdesc=CDESC, n=len(FIRMS),
             pl=PLACES, lis=lis)

H = open('ecosysteme.html', encoding='utf-8').read()
pat = re.compile(r'<section class="cat" id="%s">.*?\n  </section>\n  ' % CAT_ID, re.S)
if pat.search(H):
    H = pat.sub(lambda m: SEC, H)
    print('section remplacée')
else:
    a = H.index('<section class="cat" id="notaires">')
    H = H[:a] + SEC + H[a:]
    print('section insérée avant notaires')

# nav d'ancres
jm = re.search(r'<div class="jump">.*?</div>', H, re.S)
if ('#' + CAT_ID) not in jm.group(0):
    link = '<a href="#%s">%s</a>' % (CAT_ID, CAT_LABEL)
    nj = jm.group(0).replace('<a href="#notaires">', link + ' <a href="#notaires">')
    H = H[:jm.start()] + nj + H[jm.end():]
    print('lien ajouté à la nav')
open('ecosysteme.html', 'w', encoding='utf-8').write(H)

# ---------- 3. places.json ----------
P = json.load(open('_build/places.json', encoding='utf-8'))
P[CAT_ID] = {'label': CAT_LABEL_TXT.replace('&amp;', '&'), 'places': PLACES, 'prises': 0}
json.dump(P, open('_build/places.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# ---------- 4. sitemap ----------
S = open('sitemap.xml', encoding='utf-8').read()
add = [e['slug'] for e in FIRMS
       if '/f/%s</loc>' % e['slug'] not in S]
if add:
    block = ''.join('  <url><loc>https://www.exit.club/f/%s</loc></url>\n' % s
                    for s in add)
    S = S.replace('</urlset>', block + '</urlset>')
    open('sitemap.xml', 'w', encoding='utf-8').write(S)
print(len(add), 'URL ajoutées au sitemap')
