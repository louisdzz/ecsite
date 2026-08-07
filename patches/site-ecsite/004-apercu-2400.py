# Ecosysteme: apercus CGP au tarif unique 2 400 EUR HT/an
#
# - les 21 apercus de f/apercu/ affichaient encore la grille degressive
#   990 / 1 900 / 3 900 / 6 900 EUR selon l'encours du cabinet, avec la tranche
#   du destinataire mise en avant : ce sont les pages envoyees en prospection
# - la grille devient deux reperes, 2 400 EUR HT par an et 240 EUR HT par mois
# - le paragraphe « Ce que ca coute » nomme le tarif unique et la date de
#   lancement, bloque a vie pour qui souscrit avant la publication de la page
#   de sa categorie
# - le gabarit _build/apercu/tpl.html et le generateur _build/apercu/gen.py
#   sont alignes pour qu'une regeneration ne reintroduise pas l'ancienne grille

import glob
import sys

e = []

PR_NEW = ('<div class="prices"><div class="pr cur"><b>2 400 €</b>'
          '<span>HT / an</span></div><div class="pr"><b>240 €</b>'
          '<span>HT / mois</span></div></div>')

P_NEW = ("Tarif unique, quelle que soit la taille du cabinet. Tarif de "
         "lancement du 6 août 2026, bloqué à vie pour les cabinets qui "
         "souscrivent avant la publication de la page de leur catégorie.")

# Les trois variantes de grille ne diffèrent que par la tranche mise en
# avant (classe « cur »), et les trois variantes de paragraphe par la tranche
# nommée. Chaque apercu en porte exactement une de chaque.
TR = ["&lt; 100 M€", "100 – 500 M€", "500 M€ – 2 Md€"]
CARTES = ['<div class="pr%s"><b>990 €</b><span>< 100 M€</span></div>',
          '<div class="pr%s"><b>1 900 €</b><span>100 – 500 M€</span></div>',
          '<div class="pr%s"><b>3 900 €</b><span>500 M€ – 2 Md€</span></div>',
          '<div class="pr%s"><b>6 900 €</b><span>> 2 Md€</span></div>']

GRILLES = []
for i in range(3):
    GRILLES.append('<div class="prices">'
                   + ''.join(c % (" cur" if j == i else "")
                             for j, c in enumerate(CARTES))
                   + '</div>')

PARAS = ["Tarif annuel, dégressif selon l'encours du cabinet. Votre "
         "tranche&nbsp;: %s." % t for t in TR]

fichiers = sorted(glob.glob("f/apercu/*.html"))
if len(fichiers) != 21:
    print("ECHEC : %d apercus trouves, 21 attendus" % len(fichiers))
    sys.exit(1)

for f in fichiers:
    s = open(f, encoding="utf-8").read()
    ng = sum(s.count(g) for g in GRILLES)
    npar = sum(s.count(p) for p in PARAS)
    if ng != 1 or npar != 1:
        e.append("ECHEC %s : %d grille(s), %d paragraphe(s), 1 et 1 attendus"
                 % (f, ng, npar))
        continue
    for g in GRILLES:
        s = s.replace(g, PR_NEW)
    for p in PARAS:
        s = s.replace(p, P_NEW)
    open(f, "w", encoding="utf-8").write(s)

if e:
    print("\n".join(e))
    sys.exit(1)

# --- controles de sortie, apercus -----------------------------------------
for f in fichiers:
    s = open(f, encoding="utf-8").read()
    for x in ['<b>2 400 €</b>', '<b>240 €</b>', "Tarif de lancement du 6 août 2026"]:
        if x not in s:
            e.append("ECHEC %s : %s absent" % (f, x))
    for x in ["990", "1 900", "3 900", "6 900", "dégressif", "Votre tranche",
              "100 M€", "2 Md€"]:
        if x in s:
            e.append("ECHEC %s : %s subsiste" % (f, x))
if e:
    print("\n".join(e))
    sys.exit(1)
print("ok 21 apercus a 2 400 EUR HT/an")


def un(chemin, a, b):
    s = open(chemin, encoding="utf-8").read()
    c = s.count(a)
    if c != 1:
        e.append("ECHEC %s : %d/1 pour %s" % (chemin, c, a[:60]))
        return
    open(chemin, "w", encoding="utf-8").write(s.replace(a, b))
    print("ok %s : %s" % (chemin, a[:60]))


# --- gabarit ---------------------------------------------------------------
un("_build/apercu/tpl.html",
   "    <p>Tarif annuel, dégressif selon l'encours du cabinet. Votre "
   "tranche&nbsp;: {tranche}.</p>",
   "    <p>" + P_NEW + "</p>")

# --- generateur ------------------------------------------------------------
# La grille n'est plus fonction de la tranche : deux reperes fixes. Les
# donnees prix= et tranche= des 21 entrees restent en place, inertes, elles
# servent encore au ciblage des salves d'appel.
un("_build/apercu/gen.py",
   "    grid = ''\n"
   "    for t in TR:\n"
   "        cur = ' cur' if t == d['tranche'] else ''\n"
   "        grid += '<div class=\"pr%s\"><b>%s</b><span>%s</span></div>' % (cur, TRP[t], t)",
   "    grid = ('<div class=\"pr cur\"><b>2 400 €</b><span>HT / an</span></div>'\n"
   "            '<div class=\"pr\"><b>240 €</b><span>HT / mois</span></div>')")

if e:
    print("\n".join(e))
    sys.exit(1)

# Le gabarit ne doit plus contenir de grille degressive, et le generateur ne
# doit plus construire la grille depuis la tranche.
s = open("_build/apercu/tpl.html", encoding="utf-8").read()
if "dégressif" in s or "{tranche}" in s:
    e.append("ECHEC tpl.html : ancienne formulation du tarif subsiste")
if "Tarif de lancement du 6 août 2026" not in s:
    e.append("ECHEC tpl.html : nouvelle mention absente")
s = open("_build/apercu/gen.py", encoding="utf-8").read()
if "TRP[t], t)" in s:
    e.append("ECHEC gen.py : construction de la grille par tranche subsiste")
if '<b>2 400 €</b>' not in s:
    e.append("ECHEC gen.py : nouveau bloc de prix absent")
if e:
    print("\n".join(e))
    sys.exit(1)

print("controle vert : apercus, gabarit et generateur a 2 400 EUR HT/an")
