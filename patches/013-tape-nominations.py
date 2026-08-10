# Ecosysteme: la tape n'affiche plus de nominations perimees
#
# - six nominations de fevrier tournaient encore dans le bandeau, cote
#   statique et cote script live (le JSON embarque n'a pas de source fraiche)
# - le JSON tape-noms est vide et les jetons statiques retires : le ruban
#   n'affiche que les deals, qui eux se rechargent tout seuls depuis l'API
import re, sys
p = "ecosysteme.html"
s = open(p, encoding="utf-8").read()
m = re.search(r'(<script id="tape-noms" type="application/json">).*?(</script>)',
              s, re.S)
if not m:
    print("ECHEC tape-noms introuvable"); sys.exit(1)
s = s[:m.start()] + m.group(1) + "[]" + m.group(2) + s[m.end():]
n = 0
for mm in list(re.finditer(
        r'<(a|span) class="tk tk-nom"[^>]*>.*?<span class="f">[^<]*</span></\1>', s)):
    s = s.replace(mm.group(0), "", 1); n += 1
open(p, "w", encoding="utf-8").write(s)
s = open(p, encoding="utf-8").read()
# la variable cls="tk tk-nom" du script live et la regle CSS .chip-nom
# restent : ce sont du code, pas du contenu perime
if s.count('class="tk tk-nom"') or '"tape-noms" type="application/json">[]<' not in s:
    print("ECHEC residus"); sys.exit(1)
print("controle vert : %d jetons de nomination retires, JSON vide" % n)
