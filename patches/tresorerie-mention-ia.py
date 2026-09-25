# Tresorerie: mention du releve coordonne par une IA et renvoi a la source officielle
#
# Par prudence, la page /tresorerie dit desormais comment ses chiffres sont
# obtenus et ou les verifier :
# - une ligne sous les filtres : releve coordonne par une IA, sous la
#   responsabilite de l'Exit Club, chaque ligne renvoie a la page officielle,
#   verifier le chiffre a la source avant toute decision
# - le lien de chaque ligne devient « Verifier la source », la colonne
#   « Source officielle », avec la place necessaire
# - la meme phrase dans la section « Comment lire ce tableau » et dans la
#   description partagee (og:description)
#
# Aucune donnee modifiee.

import sys

REMPL = [('<p class="compte" id="compte"></p>', '<p class="compte" id="compte"></p>\n      <p class="prudence">Relevé coordonné par une IA, sous la responsabilité de l’Exit Club. Chaque ligne renvoie à la page officielle de la maison : vérifiez le chiffre à la source avant toute décision, les taux bougent.</p>', 1), ('.compte{font-size:12px;color:var(--muted);margin:14px 0 0}', '.compte{font-size:12px;color:var(--muted);margin:14px 0 0}\n    .prudence{font-size:12.5px;line-height:1.6;color:var(--ink);margin:12px 0 0;padding:12px 16px;border-left:2px solid #b89d5a;background:var(--wash);max-width:78ch}', 1), ('Source <span aria-hidden="true">↗</span>', 'Vérifier <span aria-hidden="true">↗</span>', 2), ('<th scope="col" class="num c-src">Source</th>', '<th scope="col" class="num c-src">Source officielle</th>', 1), ('.src{white-space:nowrap;text-align:right}', '.src{white-space:normal;text-align:right}\n    .src a{white-space:nowrap}', 1), ('table.treso th.c-pm{width:4%}table.treso th.c-src{width:5%}', 'table.treso th.c-pm{width:4%}table.treso th.c-src{width:8%}', 1), ('table.treso th.c-pm{width:5%}table.treso th.c-src{width:7%}', 'table.treso th.c-pm{width:5%}table.treso th.c-src{width:9%}', 1), ('<p><b>Ce que ce tableau n’est pas.</b> L’Annuaire référence, il ne recommande pas.', '<p><b>Ce que ce tableau n’est pas.</b> Le relevé est coordonné par une IA, sous la responsabilité de l’Exit Club ; seule la page officielle de chaque maison fait foi, elle est liée sur chaque ligne. L’Annuaire référence, il ne recommande pas.', 1), ('<meta property="og:description" content="Neuf maisons, quatorze produits, les taux tels qu’ils sont publiés. Relevés le 25 septembre 2026, avec la source de chaque chiffre.">', '<meta property="og:description" content="Neuf maisons, quatorze produits, les taux tels qu’ils sont publiés, avec la source officielle de chaque chiffre. Relevé coordonné par une IA, à vérifier à la source.">', 1)]

p = "tresorerie.html"
try:
    s = open(p, encoding="utf-8").read()
except FileNotFoundError:
    print("ECHEC: tresorerie.html introuvable (deposer d'abord tresorerie-comparateur.py)")
    sys.exit(1)

echecs = []
for a, b, n in REMPL:
    c = s.count(a)
    if c != n:
        echecs.append("ECHEC: « " + a[:60].replace("\n", " ") + " » attendu " + str(n) + " fois, trouve " + str(c))
if "class=\"prudence\"" in s:
    echecs.append("ECHEC: la mention est deja en place")
if echecs:
    for e in echecs:
        print(e)
    sys.exit(1)

for a, b, n in REMPL:
    s = s.replace(a, b)
    print("  ok  " + str(n) + "x  " + a[:60].replace("\n", " "))
open(p, "w", encoding="utf-8").write(s)
print("")
print("Termine : la page dit comment elle est faite et ou verifier.")
