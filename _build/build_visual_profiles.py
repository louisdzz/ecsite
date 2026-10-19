#!/usr/bin/env python3
"""Apply the approved visual profile design, preserving all source content.

Editorial facts are extracted from each existing page. Category diagrams are
explicitly labelled as descriptions of a profession, never as house promises.
Usage: python3 _build/build_visual_profiles.py --all [--check-only]
"""
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse
import argparse
import hashlib
import importlib.util
import json
import re
import html
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / '_build/visual_profiles'
VERSION = 'visual-20261019'
CSS = '/assets/maison/fiche-visuelle.css?v=20261019'
JS = '/assets/maison/fiche-visuelle.js?v=20261019'
CATEGORIES = json.loads((CONFIG/'categories.json').read_text())
DATA = json.loads((ROOT/'assets/ecosysteme/maison/data.json').read_text())
HOUSES = {h['slug']:h for h in DATA['houses']}
spec = importlib.util.spec_from_file_location('visual_content', CONFIG/'content.py')
content = importlib.util.module_from_spec(spec)
spec.loader.exec_module(content)
ARROW = '<svg class="pv-arrow" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
EXTERNAL = '<svg class="pv-arrow" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 18 18 6M6 6h12v12"/></svg>'

def esc(value):
    return html.escape(str(value or ''), quote=True)

def visible_texts(soup):
    return Counter(re.sub(r'\s+', ' ', str(n)).strip() for n in soup.body.find_all(string=True)
                   if n.parent.name not in ('style','script') and str(n).strip())

def sentence(text, limit=155):
    """Keep a complete existing sentence; never cut rates or conditions mid-way."""
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= limit:
        return text
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-Ÿ])',text)
    return sentences[0] if len(sentences[0]) <= limit else ''

def category_for(profile):
    house = HOUSES.get(profile['slug'], {})
    code = profile['category']['code']
    if code not in CATEGORIES:
        code = next((c for c in house.get('categories',[]) if c in CATEGORIES),'')
    if not code:
        code = 'cgp'
    return code, CATEGORIES[code]

def confirmed_url(profile, soup):
    # Official homepages verified on 19 October. Existing source links remain
    # in the detailed profile; press and personal biography pages are not CTAs.
    corrected = {'kpmg-france':'https://kpmg.fr',
                 'lily-of-the-valley':'https://www.lilyofthevalley.com/',
                 'beaumier':'https://www.beaumier.com/en/'}
    if profile['slug'] in corrected:
        return corrected[profile['slug']]
    if profile.get('official_url'):
        return profile['official_url']
    for selector in ('.sidebar a.btn', '.hero .actions a', '.hero a.action', '.hero a.btn'):
        for a in soup.select(selector):
            href = a.get('href','')
            if href.startswith('mailto:') and not re.search(r'louis|exit\.club', href, re.I):
                return href
            if href.startswith('https://') and not any(x in href for x in ('exit.club','tally.so','linkedin.com','google.com')):
                return href
    return ''

def logo_markup(profile, soup, diagram=False):
    house = HOUSES.get(profile['slug'], {})
    image = profile.get('logo') or {}
    src = image.get('src') or (house.get('logo') or {}).get('src')
    dark = bool(soup.select_one('.profile-visual.logo-dark')) or bool((house.get('logo') or {}).get('dark'))
    if src:
        if diagram:
            return f'<span class="pv-house-logo{" is-dark" if dark else ""}"><img src="{esc(src)}" alt="" decoding="async" width="120" height="60"></span>'
        return f'<div class="pv-brand-logo{" is-dark" if dark else ""}"><img src="{esc(src)}" alt="" decoding="async" width="74" height="61"></div>'
    if diagram:
        return f'<span class="pv-house-name">{esc(profile["name"])}</span>'
    initials = ''.join(w[0] for w in profile['name'].split()[:2]).upper()
    return f'<div class="pv-brand-logo pv-brand-initials" aria-hidden="true">{esc(initials)}</div>'

def compact_facts(facts):
    small = [f for f in facts if len(f['value']) <= 65 and len(f['label']) <= 85][:3]
    if not small:
        return '', ''
    mobile = '<dl class="pv-compact-facts pv-house-facts">' + ''.join(
        f'<div><dt>{esc(f["value"])}</dt><dd>{esc(f["label"])}</dd></div>' for f in small) + '</dl>'
    desktop = f'<section class="pv-reasons pv-house-reasons pv-count-{len(small)}" aria-label="Repères propres à la maison">' + ''.join(
        f'<div class="pv-reason"><span class="pv-reason-value">{esc(f["value"])}</span><p>{esc(f["label"])}</p></div>' for f in small) + '</section>'
    return mobile, desktop

def render_summary(profile, soup):
    code, cat = category_for(profile)
    name = profile['name']
    lead = profile.get('lead','')
    existing_lede = soup.select_one('.hero .lede, .hero-profile .lede')
    short_lede = existing_lede.get_text(' ',strip=True) if existing_lede else ''
    headline = short_lede if short_lede and len(short_lede)<=155 and content._informative(short_lede,lead=True) else (sentence(lead) if lead else '')
    # A complete, existing service sentence takes precedence over the profession.
    if not headline:
        headline = cat['headline']
    house_specific = bool(lead)
    if house_specific:
        below = lead
        if headline and below.startswith(headline):
            below = below[len(headline):].strip()
        if not below:
            below = 'Retrouvez ci-dessous les repères disponibles sur la maison, puis sa présentation complète.'
    else:
        below = f'{name} est répertorié dans la catégorie « {cat["label"]} ». Les spécialités et les conditions propres à la maison restent à documenter.'
    # Long original descriptions remain fully accessible in the detailed profile.
    if len(below) > 400:
        below = sentence(below, 350) or cat['context']
    facts = profile.get('facts',[])[:3]
    mobile, desktop = compact_facts(facts)
    status = profile.get('status') or 'Profil référencé'
    if len(status) > 100 or re.search(r'étalon|aperçu|nouveau format',status,re.I) or not re.search(r'profil|fiche|annuaire',status,re.I):
        status = 'Profil référencé'
    url = confirmed_url(profile, soup)
    if url:
        primary = f'<a class="pv-primary" href="{esc(url)}"' + (' target="_blank" rel="noopener noreferrer"' if url.startswith('https://') else '') + f'>{"Contacter la maison" if url.startswith("mailto:") else "Découvrir la maison"} {EXTERNAL}</a>'
    else:
        primary = f'<a class="pv-primary" href="#dossier-complet">Consulter la fiche {ARROW}</a>'
    rows = ''.join(f'<div><dt>{esc(f["label"])}</dt><dd>{esc(f["value"])}</dd></div>' for f in facts)
    if not rows:
        missing_label = 'Repères complémentaires' if house_specific else 'Spécialités et différences'
        rows = f'<div><dt>Métier référencé</dt><dd>{esc(cat["label"])}</dd></div><div><dt>{missing_label}</dt><dd>Non renseignés dans cette fiche.</dd></div><div><dt>Frais et accès</dt><dd>À préciser avec la maison.</dd></div>'
    category_link = f'/annuaire?metier={code}'
    other_cats = [CATEGORIES[c]['label'] for c in HOUSES.get(profile['slug'],{}).get('categories',[]) if c in CATEGORIES and c!=code]
    extra_cats = ('<p class="pv-other-cats">Également référencé : '+esc(' · '.join(other_cats))+'</p>') if other_cats else ''
    lead_note = '' if house_specific else '<p class="pv-completion-note">Fiche documentaire : les particularités de cette maison ne sont pas encore renseignées.</p>'
    visible_risk = ''
    risk_node = soup.select_one('.risk, .risk-note, .risque')
    if risk_node:
        risk_text = risk_node.get_text(' ',strip=True)
        if len(risk_text)<=650:
            visible_risk = f'<p class="pv-risk">{esc(risk_text)}</p>'
    root_tag = 'section' if soup.find('main') else 'main'
    return f'''<{root_tag} class="pv-main pv-house-summary" id="fiche-visuelle" data-category="{esc(code)}">
<header class="pv-identity"><div class="pv-brand">{logo_markup(profile,soup)}<div><h1>{esc(name)}</h1><a class="pv-category" href="{category_link}">{esc(cat['label'])}</a></div></div><p class="pv-status">{esc(status)}</p></header>
<section class="pv-hero" id="pv-offre" aria-labelledby="pv-offre-titre"><div class="pv-hero-copy"><p class="pv-eyebrow">{esc('La maison' if house_specific else 'Le métier')}</p><h2 id="pv-offre-titre">{esc(headline)}</h2>{mobile}<p class="pv-lead">{esc(below)}</p>{extra_cats}<div class="pv-actions">{primary}<a class="pv-secondary" href="{category_link}">Comparer les acteurs {ARROW}</a></div>{lead_note}</div>
<figure class="pv-diagram pv-profession-diagram" aria-labelledby="pv-diagram-title"><div class="pv-flow"><div class="pv-from">{esc(cat['flow'][0])}</div><div class="pv-connector" aria-hidden="true"></div><div class="pv-investment"><div class="pv-investment-head">{logo_markup(profile,soup,True)}<span class="pv-product-label">{esc('Repères du métier')}</span></div><h3 class="pv-map-role" id="pv-diagram-title">{esc(cat['flow'][1])}</h3><div class="pv-map-output">{ARROW}<span>{esc(cat['flow'][2])}</span></div></div></div><figcaption class="pv-diagram-caption">Repères du métier. Périmètre propre à {esc(name)} à confirmer.</figcaption></figure></section>
{visible_risk}{desktop}<nav class="pv-tabs" aria-label="Sections de la fiche"><a href="#pv-offre">L’offre</a><a href="#reperes-maison">Les repères</a><a href="#questions-avant-contact">À comparer</a><a href="#dossier-complet">La fiche complète</a></nav>
<div class="pv-information"><section id="reperes-maison" aria-labelledby="pv-reperes-title"><h2 class="pv-section-title" id="pv-reperes-title">{'Les repères de la maison.' if facts else 'Ce qui est renseigné.'}</h2><p class="pv-section-description">{'Informations reprises de la fiche existante. Sources et dates dans le dossier complet.' if facts else 'Le référencement identifie un acteur. Il ne préjuge pas de ses conditions ni de son approche.'}</p><dl class="pv-condition-list">{rows}</dl><p class="pv-source-note">{esc(cat['context'])}</p></section>
<aside class="pv-compare" id="questions-avant-contact" aria-labelledby="pv-compare-title"><p class="pv-compare-label">Avant de prendre contact</p><h2 id="pv-compare-title">Trois questions utiles.</h2><ol>{''.join(f'<li>{esc(q)}</li>' for q in cat['questions'])}</ol><a class="pv-secondary" href="{category_link}">Voir les autres acteurs {ARROW}</a></aside></div>
<details class="pv-detail" id="dossier-complet"><summary><span>Consulter la fiche complète<span class="pv-details-caption">Présentation, sources, conditions et contacts disponibles.</span></span></summary><div class="pv-legacy-content"></div></details><div class="pv-bottom"><a href="{category_link}">{ARROW} Retour à la catégorie</a><p>Le référencement ne vaut pas recommandation de l’Exit Club.</p></div>
</{root_tag}>'''

def transform(path, write=True, source_path=None):
    source_path = source_path or path
    raw = source_path.read_text()
    old = BeautifulSoup(raw, content.PARSER)
    if old.body is None or old.find('h1') is None:
        return {'slug':path.stem,'status':'excluded'}
    if old.body.get('data-profile-design') == VERSION:
        return {'slug':path.stem,'status':'already-visual'}
    profile = content.extract_profile(source_path)
    if not profile:
        return {'slug':path.stem,'status':'excluded'}
    before_texts = visible_texts(old)
    before_links = Counter(a['href'] for a in old.select('a[href]'))
    before_ids = Counter(n['id'] for n in old.select('[id]'))
    if path.stem == 'spiko':
        new = BeautifulSoup((CONFIG/'spiko-approved.html').read_text(), content.PARSER)
    else:
        new = old
        hero = new.select_one('.hero-profile') or new.select_one('.hero')
        if hero is None:
            raise ValueError(f'Hero manquant : {path.stem}')
        markup = BeautifulSoup(render_summary(profile, new), content.PARSER)
        summary = markup.select_one('.pv-main')
        legacy = summary.select_one('.pv-legacy-content')
        # Capture every node from the original hero to the end of its container.
        # Headers and breadcrumbs stay in place; no detailed sections disappear.
        siblings = list(hero.next_siblings)
        hero.insert_before(summary)
        legacy.append(hero.extract())
        for node in siblings:
            legacy.append(node.extract())
        for heading in legacy.find_all('h1'):
            heading.name = 'h2'
        hero['class'] = ['pv-original-intro']
        for nested_main in legacy.find_all('main'):
            nested_main.name = 'div'
        for existing_hero in legacy.select('.hero'):
            existing_hero['class'] = ['pv-original-copy']
        for nav in legacy.select('nav.anchors'):
            nav['class'] = ['pv-legacy-links']
        classes = list(dict.fromkeys(new.body.get('class',[]) + ['profile-page','profile-visual-v2']))
        new.body['class'] = classes
        new.body['data-profile-design'] = VERSION
        new.head.append(new.new_tag('link',rel='stylesheet',href=CSS))
        script = new.new_tag('script',src=JS)
        script['defer'] = ''
        new.head.append(script)
    # Invariants apply to every real company, including historical variants.
    after_texts = visible_texts(new)
    lost_texts = before_texts-after_texts
    if path.stem == 'spiko':
        # The approved prototype consolidates the duplicate category tag into
        # its identity line. The category remains in the breadcrumb and links.
        lost_texts -= Counter({'Trésorerie & monétaire':1})
    if lost_texts:
        raise ValueError(f'Textes perdus sur {path.stem}: {list(lost_texts)[:5]}')
    if before_links-Counter(a['href'] for a in new.select('a[href]')):
        raise ValueError(f'Liens perdus sur {path.stem}')
    if before_ids-Counter(n['id'] for n in new.select('[id]')):
        raise ValueError(f'Ancres perdues sur {path.stem}')
    all_ids = [n['id'] for n in new.select('[id]')]
    previous_duplicates = {i for i,n in before_ids.items() if n>1}
    duplicates = {i for i,n in Counter(all_ids).items() if n>1}-previous_duplicates
    if duplicates:
        raise ValueError(f'Identifiants nouveaux dupliqués sur {path.stem}: {duplicates}')
    if len(new.find_all('h1')) != 1:
        raise ValueError(f'H1 non unique sur {path.stem}')
    for selector in ('link[rel="canonical"]','[data-cookie-preferences]','script[src^="/assets/site/site.js"]'):
        if old.select_one(selector) and not new.select_one(selector):
            raise ValueError(f'Élément obligatoire perdu sur {path.stem}: {selector}')
    if len(new.find_all('main')) > max(1,len(old.find_all('main'))):
        raise ValueError(f'Repères main ajoutés en double sur {path.stem}')
    if write:
        path.write_text(str(new))
    return {'slug':path.stem,'status':'updated' if write else 'checked',
            'category':category_for(profile)[0], 'specific_lead':bool(profile.get('lead')),
            'specific_facts':len(profile.get('facts',[])), 'original_texts':sum(before_texts.values()),
            'text_preserved':True,'links_preserved':True,'anchors_preserved':True}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('slugs',nargs='*')
    parser.add_argument('--all',action='store_true')
    parser.add_argument('--check-only',action='store_true')
    parser.add_argument('--report')
    parser.add_argument('--source-directory',help='Répertoire f de la version de départ pour reconstruire une génération en cours de revue.')
    args=parser.parse_args()
    paths = sorted((ROOT/'f').glob('*.html')) if args.all else [ROOT/'f'/f'{s}.html' for s in args.slugs]
    if not paths:
        parser.error('Fournir des slugs ou --all')
    results=[]
    for i,path in enumerate(paths):
        source = Path(args.source_directory)/path.name if args.source_directory else None
        results.append(transform(path, write=not args.check_only,source_path=source))
        if (i+1)%500 == 0:
            print(f'{i+1}/{len(paths)} fiches contrôlées',flush=True)
    report={'version':VERSION,'counts':dict(Counter(r['status'] for r in results)),'profiles':results}
    if args.report:
        Path(args.report).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report['counts'],ensure_ascii=False),flush=True)

if __name__=='__main__':
    main()
