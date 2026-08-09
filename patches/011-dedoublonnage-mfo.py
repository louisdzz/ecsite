# Ecosysteme: dedoublonnage de la categorie Multi-Family Offices
#
# - huit maisons en double ou triple (imports distincts), 74 -> 65 entrees
# - le profil le plus riche est conserve, les doublons deviennent des
#   redirections, sortent de la liste, du sitemap et des compteurs
import os, re, sys
R = {"blackpearl-family-office": "black-pearl", "fobs-family-office": "fobs",
     "hapyfew": "hapyfew-multi-family-office", "herest-family-office": "herest",
     "herest-gestion-de-fortune-family-office": "herest",
     "keepers-family-office": "keepers", "obsido": "obsido-family-office",
     "pulse": "pulse-family-office",
     "sagis-family-office-gestion-d-actifs": "sagis-am"}
e = []
B = ('<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name='
     '"robots" content="noindex"><link rel="canonical" href="https://www.exit'
     '.club/f/{C}"><meta http-equiv="refresh" content="0;url=/f/{C}"><title>'
     'Redirection</title></head><body><p>Profil fusionné : <a href="/f/{C}">'
     "continuer</a>.</p></body></html>\n")
s = open("ecosysteme.html", encoding="utf-8").read()
m2 = open("sitemap.xml", encoding="utf-8").read()
for d, c in R.items():
    if not os.path.exists("f/%s.html" % c): e.append("ECHEC %s absent" % c)
    open("f/%s.html" % d, "w", encoding="utf-8").write(B.replace("{C}", c))
    m = re.search(r'[ \t]*<li><a href="/f/%s">[^<]+</a></li>\n' % d, s)
    if not m: e.append("ECHEC liste %s" % d)
    else: s = s.replace(m.group(0), "", 1)
    u = "  <url><loc>https://www.exit.club/f/%s</loc></url>\n" % d
    if u not in m2: e.append("ECHEC sitemap %s" % d)
    else: m2 = m2.replace(u, "", 1)
if e: print("\n".join(e)); sys.exit(1)
o = '<div class="count"><b>74</b> référencés</div>'
if s.count(o) != 1: print("ECHEC compteur MFO"); sys.exit(1)
s = s.replace(o, o.replace("74", "65"))
n = s.count("4&nbsp;230") + s.count("4230")
if n < 4: print("ECHEC total: %d" % n); sys.exit(1)
s = s.replace("4&nbsp;230", "4&nbsp;221").replace("4230", "4221")
open("ecosysteme.html", "w", encoding="utf-8").write(s)
open("sitemap.xml", "w", encoding="utf-8").write(m2)
print("controle vert : 9 doublons fusionnes, MFO 65, total 4221")
