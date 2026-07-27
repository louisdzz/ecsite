# -*- coding: utf-8 -*-
"""Retire proprement un logo faux : meta + fichier webp + hero de la fiche
+ clé logo du schema.org. Usage : python3 _build/logos/purge.py <slug> [<slug>...]
"""
import json, os, re, sys
os.chdir('/root/ecsite')
MP='_build/logos/dir-meta.json'
def purge(slugs):
    m=json.load(open(MP)); done=[]
    for slug in slugs:
        v=m.pop(slug,None)
        if v and os.path.exists(v['f'].lstrip('/')): os.remove(v['f'].lstrip('/'))
        p='f/%s.html'%slug
        if os.path.exists(p):
            h=open(p,encoding='utf-8').read()
            h2=re.sub(r'<section class="hero wl"><div class="flogo[^"]*"><img[^>]*></div><div class="hb">(.*?)</div></section>',
                      r'<section class="hero">\1</section>', h, count=1, flags=re.S)
            h2=re.sub(r',\s*"logo":\s*"https://www\.exit\.club/assets/logos/dir/%s\.webp"'%re.escape(slug),'',h2,count=1)
            if h2!=h: open(p,'w',encoding='utf-8').write(h2)
        done.append(slug)
    json.dump(m, open(MP,'w'), ensure_ascii=False, indent=0)
    print('purgés: %s | meta: %d'%(', '.join(done), len(m)))
if __name__=='__main__':
    purge(sys.argv[1:])
