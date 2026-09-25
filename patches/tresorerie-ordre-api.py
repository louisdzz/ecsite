# Tresorerie: le taux lu en direct a le dernier mot
#
# La page chargeait en parallele tresorerie.json et la route /api/tresorerie
# de l'app ; les deux repondent en 240 ms et le dernier arrive gagnait, donc
# une fois sur deux le taux Spiko affiche etait celui du JSON de la veille et
# non celui de l'API. Les deux lectures sont maintenant enchainees : le JSON du
# site d'abord, la route de l'app ensuite.

import sys

ANCRE = "    var url = '/tresorerie.json?v=' + Math.floor(Date.now() / 3600000);\n    fetch(url, { cache: 'no-cache' }).then(function(r){ return r.ok ? r.json() : null; }).then(fusionner).catch(function(){});\n    fetch('https://exit-club-app.vercel.app/api/tresorerie', { mode: 'cors' }).then(function(r){ return r.ok ? r.json() : null; }).then(fusionner).catch(function(){});\n"
NOUVEAU = "    /* Dans l'ordre : le JSON du site d'abord, la route de l'app ensuite, pour que le taux lu en direct ait le dernier mot. */\n    var url = '/tresorerie.json?v=' + Math.floor(Date.now() / 3600000);\n    fetch(url, { cache: 'no-cache' })\n      .then(function(r){ return r.ok ? r.json() : null; }).then(fusionner).catch(function(){})\n      .then(function(){ return fetch('https://exit-club-app.vercel.app/api/tresorerie', { mode: 'cors' }); })\n      .then(function(r){ return r.ok ? r.json() : null; }).then(fusionner).catch(function(){});\n"

p = "tresorerie.html"
try:
    s = open(p, encoding="utf-8").read()
except FileNotFoundError:
    print("ECHEC: tresorerie.html introuvable")
    sys.exit(1)
c = s.count(ANCRE)
if c != 1:
    print("ECHEC: bloc de chargement attendu 1 fois, trouve " + str(c) + " (patch deja applique ?)")
    sys.exit(1)
open(p, "w", encoding="utf-8").write(s.replace(ANCRE, NOUVEAU))
print("  ok  chargement enchaine : JSON du site puis route de l'app")
print("")
print("Termine : le taux lu en direct s'affiche toujours.")
