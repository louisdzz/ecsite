#!/usr/bin/env python3
"""Apply the approved common shell without adding any actor facts.
Run with explicit slugs for sample review, or --all after verification.
Original text, anchors, outgoing links, metadata and analytics are retained.
"""
from pathlib import Path
from bs4 import BeautifulSoup
from collections import Counter
import json,sys,re
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'assets/ecosysteme/maison/data.json').read_text())
HOUSES={h['slug']:h for h in DATA['houses']}
GROUPS=[('essentiel','L’essentiel'),('usages','Quand les solliciter'),('fonctionnement','Le fonctionnement'),('conditions','Prix et conditions'),('equipe','L’équipe'),('entretien','L’entretien'),('actualites','Les actualités'),('sources','Les sources')]

def texts(s):
 return Counter(str(n).strip() for n in s.body.find_all(string=True) if n.parent.name not in ['script','style'] and str(n).strip())
def classify(node):
 ident=node.get('id','').lower();cls=node.get('class',[]);t=node.get_text(' ',strip=True).lower();h=node.find(['h2','h3']);heading=h.get_text(' ',strip=True).lower() if h else ''
 if ident in ['interview','entretien','questions']: return 'entretien'
 if ident in ['sources'] or 'sources' in heading or 'à propos de cette fiche' in heading: return 'sources'
 if ident in ['equipe','fondateur','team'] or 'équipe' in heading or 'fondateur' in heading or (cls==['card'] and ('équipe dirigeante' in t)): return 'equipe'
 if ident in ['actualites','news'] or 'actualités' in heading: return 'actualites'
 if ident in ['interview','entretien','questions'] or 'interview' in heading: return 'entretien'
 if ident in ['parcours','fonctionnement','deroulement','etapes'] or 'déroulement' in heading or 'comment se construit' in heading: return 'fonctionnement'
 if ident in ['etiquette','conflits','grille','conditions','remuneration','budget','tarifs'] or any(w in heading for w in ['budget','tarif','rémunér','conditions','frais']): return 'conditions'
 if ident in ['projet','approche','services','usages','expertises','metiers'] or any(w in heading for w in ['approche','solliciter','accompagn','projet']): return 'usages'
 return 'essentiel'

def normalize(slug):
 path=ROOT/'f'/f'{slug}.html'
 if not path.exists(): return {'slug':slug,'status':'missing'}
 original=path.read_text();s=BeautifulSoup(original,'html.parser')
 if s.body is None or s.find('h1') is None: return {'slug':slug,'status':'not-profile'}
 if s.body.get('data-profile-layout')=='20261006' or slug=='ibc-aviation': return {'slug':slug,'status':'already-common'}
 before=texts(s);links=Counter(a.get('href') for a in s.select('a[href]'));ids=Counter(x['id'] for x in s.select('[id]'))
 wrap=s.select_one('.wrap');hero=s.select_one('.hero');
 if wrap is None or hero is None: return {'slug':slug,'status':'unsupported'}
 s.body['class']=list(dict.fromkeys(s.body.get('class',[])+['profile-page']))
 s.body['data-profile-layout']='20261006'
 s.head.append(s.new_tag('link',rel='stylesheet',href='/assets/maison/profil-commun.css?v=20261006-common'))
 # Move the existing identity image to the common visual panel.
 visual=s.new_tag('div',attrs={'class':'profile-visual','aria-label':'Identité de la maison'})
 logo=hero.select_one('img')
 if logo:
  dark=logo.find_parent(class_='dk') or 'dark' in logo.get('class',[])
  logo.extract();visual.append(logo)
  if dark: visual['class']='profile-visual logo-dark'
  for holder in hero.select('.flogo'):
   if not holder.get_text(strip=True) and not holder.find('img'): holder.decompose()
 else:
  plate=hero.select_one('.wordmark')
  if plate: plate.extract();plate['class']='house-nameplate';visual.append(plate)
  else:
   imgdata=HOUSES[slug].get('logo')
   if imgdata:
    im=s.new_tag('img',src=imgdata['src'],alt=HOUSES[slug]['name'],decoding='async');visual.append(im)
    if imgdata.get('dark'): visual['class']='profile-visual logo-dark'
   else:
    mark=s.new_tag('span',attrs={'class':'house-nameplate'});mark.string=HOUSES[slug]['name'];visual.append(mark)
 header=s.new_tag('div',attrs={'class':'hero-profile'});hero.replace_with(header);header.append(hero);header.append(visual)
 # Group the original nodes under common labels. Contents remain unchanged.
 container=s.new_tag('div',attrs={'class':'profile-body'});content=s.new_tag('div',attrs={'class':'profile-content'});container.append(content)
 header.insert_after(container)
 groups={};end=[];oldnav=[]
 for node in list(wrap.children):
  if not getattr(node,'name',None) or node is header or node is container: continue
  cls=node.get('class',[])
  if 'top' in cls or 'crumb' in cls: continue
  if node.name=='nav' and any(x in cls for x in ['toc','jump']): oldnav.append(node.extract());continue
  if node.name in ['footer','script'] or any(x in cls for x in ['foot','back','gap']):end.append(node.extract());continue
  if node.name=='aside' or (node.name=='p' and not node.get('id')):end.append(node.extract());continue
  group=classify(node);groups.setdefault(group,[]).append(node.extract())
 nav=s.new_tag('nav',attrs={'class':'anchors','aria-label':'Sections de la fiche'})
 header.insert_after(nav)
 for key,label in GROUPS:
  if key not in groups: continue
  section=s.new_tag('section',attrs={'class':'section common-section','id':f'profil-{key}'})
  title=s.new_tag('h2');title.string=label;section.append(title)
  pending=key=='entretien' and all('interview sans filtre à venir' in n.get_text(' ',strip=True).lower() or n.get('id') in ['interview','questions'] for n in groups[key])
  target=section
  if pending:
   det=s.new_tag('details',attrs={'class':'profile-extra'});summ=s.new_tag('summary');summ.string='Questions proposées · réponses à recueillir';det.append(summ);section.append(det);target=det
  for node in groups[key]:
   node['class']=list(dict.fromkeys(node.get('class',[])+['profile-subsection']))
   target.append(node)
  content.append(section)
  a=s.new_tag('a',href=f'#profil-{key}');a.string=label;nav.append(a)
 if oldnav:
  extra=s.new_tag('details',attrs={'class':'profile-extra'});summary=s.new_tag('summary');summary.string='Liens complémentaires';extra.append(summary)
  for node in oldnav:
   node['class']=list(dict.fromkeys(node.get('class',[])+['legacy-nav']))
   extra.append(node)
  content.append(extra)
 for node in end:content.append(node)
 side=s.new_tag('aside',attrs={'class':'sidebar'})
 label=s.new_tag('span',attrs={'class':'eyebrow'});label.string='La maison';side.append(label)
 title=s.new_tag('h3');title.string=HOUSES[slug]['name'];side.append(title)
 # A real existing company contact or website, never an inferred address.
 candidates=s.select('a[href]');chosen=None
 for a in candidates:
  href=a.get('href','');txt=a.get_text(' ',strip=True).lower()
  if href.startswith('mailto:') and not any(z in href.lower() for z in ['louis@','exit.club','louis.debouzy']): chosen=a;break
 if not chosen:
  for a in candidates:
   href=a.get('href','');txt=a.get_text(' ',strip=True).lower()
   if href.startswith('https://') and not any(z in href for z in ['google.com','linkedin.com','exit.club','tally.so']) and any(z in txt for z in ['site','contacter','parler de','découvrir nativ','mirabaud.com','lazard.com']):chosen=a;break
 if chosen:
  href=chosen['href'];label='Contacter la maison' if href.startswith('mailto:') else ('Prendre rendez-vous' if 'calendly.com' in href else 'Consulter leur site')
  a=s.new_tag('a',href=href,attrs={'class':'btn'});a.string=label
  if href.startswith('https://'):a['target']='_blank';a['rel']='noopener noreferrer'
  side.append(a)
 else:
  p=s.new_tag('p');p.string='Coordonnées à compléter par la maison.';side.append(p)
 if 'entretien' in groups:
  a=s.new_tag('a',href='#profil-entretien',attrs={'class':'btn light'});a.string='L’entretien';side.append(a)
 p=s.new_tag('p');p.string='Le référencement ne vaut pas recommandation.';p['class']='sidebar-note';side.append(p)
 container.append(side)
 after=texts(s);lost=before-after
 if lost: raise ValueError(f'Text lost on {slug}: {lost}')
 if links-Counter(a.get('href') for a in s.select('a[href]')):raise ValueError(f'Links lost on {slug}')
 if ids-Counter(x['id'] for x in s.select('[id]')):raise ValueError(f'IDs lost on {slug}')
 path.write_text(str(s));return {'slug':slug,'status':'updated','text_preserved':True,'links_preserved':True,'anchors_preserved':True,'sections':list(groups)}
if __name__=='__main__':
 slugs=list(HOUSES) if '--all' in sys.argv else sys.argv[1:]
 results=[]
 for slug in slugs: results.append(normalize(slug))
 print(json.dumps(results,ensure_ascii=False,indent=2))
