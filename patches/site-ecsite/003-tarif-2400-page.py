# Ecosysteme: page produit au tarif unique 2 400 EUR HT/an
#
# - la grille de quatre paliers (990 / 2 000 / 3 900 / 6 900 EUR HT par an)
#   devient une carte unique « Profil verifie » a 2 400 EUR HT/an, 240 EUR/mois
# - la carte porte data-p="standard" data-an="2400" data-mois="240" : le
#   selecteur annuel/mensuel, la preselection et paintPrix tournent sans
#   une ligne de JS a changer
# - paragraphe « Ce que vous payez » reecrit : un prix pour toutes les
#   categories et toutes les tailles, la qualification porte sur ce que la
#   maison accepte de publier
# - ligne de mentions : tarif de lancement du 6 aout 2026, bloque a vie pour
#   les maisons qui souscrivent avant la publication de la page de leur
#   categorie
# - meta description, message de validation du formulaire et preselection par
#   defaut alignes sur l'offre unique
# - feuille d'appel salve 1 : cible et rappel de tarif alignes

import sys

P = "fiche-verifiee.html"
A = "_build/appels/feuille-appel-salve1.html"

e = []
s = open(P, encoding="utf-8").read()


def sub(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        e.append("ECHEC %d/%d attendus : %s" % (c, n, a[:60]))
        return
    s = s.replace(a, b)
    print("ok %dx %s" % (c, a[:60]))


# --- grille -> carte unique ------------------------------------------------
ANCIENNE = """    <div class="grid" id="paliers">
      <label class="pal" data-p="p1" data-an="990" data-mois="99">
        <input type="radio" name="palier" value="p1">
        <div class="n">Cabinet indépendant</div>
        <div class="p"><b class="v">990 €</b> <span class="u">HT / an</span></div>
        <div class="c">Moins de 100 M€ d'encours, ou cabinet mono-site</div>
      </label>
      <label class="pal" data-p="p2" data-an="2000" data-mois="200">
        <input type="radio" name="palier" value="p2">
        <div class="n">Maison établie</div>
        <div class="p"><b class="v">2 000 €</b> <span class="u">HT / an</span></div>
        <div class="c">100 à 500 M€ d'encours, ou plusieurs bureaux</div>
      </label>
      <label class="pal" data-p="p3" data-an="3900" data-mois="390">
        <input type="radio" name="palier" value="p3">
        <div class="n">Grande maison</div>
        <div class="p"><b class="v">3 900 €</b> <span class="u">HT / an</span></div>
        <div class="c">500 M€ à 2 Md€ d'encours, ou réseau national</div>
      </label>
      <label class="pal" data-p="p4" data-an="6900" data-mois="690">
        <input type="radio" name="palier" value="p4">
        <div class="n">Institution</div>
        <div class="p"><b class="v">6 900 €</b> <span class="u">HT / an</span></div>
        <div class="c">Plus de 2 Md€ d'encours, banque, réseau international</div>
      </label>
    </div>"""

NOUVELLE = """    <div class="grid" id="paliers">
      <label class="pal" data-p="standard" data-an="2400" data-mois="240">
        <input type="radio" name="palier" value="standard">
        <div class="n">Profil vérifié</div>
        <div class="p"><b class="v">2 400 €</b> <span class="u">HT / an</span></div>
        <div class="c">Toutes catégories, toutes tailles de maison</div>
      </label>
    </div>"""

sub(ANCIENNE, NOUVELLE)

# Une seule carte : la colonne unique evite une carte a demi-largeur. `.grid`
# n'est utilise qu'ici, la regle de la media query devient redondante et reste
# inoffensive.
sub(".grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:18px 0 0}",
    ".grid{display:grid;grid-template-columns:1fr;gap:14px;margin:18px 0 0}")

# --- copy ------------------------------------------------------------------
sub("Vous payez selon la taille de votre maison, pas selon votre appétit. "
    "La grille se lit en encours pour les CGP et les banques privées, en "
    "taille de structure pour les autres catégories. Le palier est arrêté "
    "avec vous à la qualification.",
    "Vous payez le même prix que toutes les maisons de l'Écosystème, quelle "
    "que soit votre catégorie, quelle que soit votre taille. 2 400 € HT par "
    "an, ou 240 € HT par mois. La qualification porte sur ce que votre maison "
    "accepte de publier.")

sub("Sans engagement de reconduction : vous arrêtez quand vous voulez, votre "
    "maison reste recensée gratuitement. Vous n'êtes pas retenu à la "
    "qualification : vous êtes remboursé intégralement.",
    "Sans engagement de reconduction : vous arrêtez quand vous voulez, votre "
    "maison reste recensée gratuitement. Vous êtes remboursé intégralement si "
    "vous renoncez à la qualification. Tarif de lancement du 6 août 2026, "
    "bloqué à vie pour les maisons qui souscrivent avant la publication de la "
    "page de leur catégorie.")

sub("De 990 à 6 900 € HT par an.", "2 400 € HT par an.")

# Une seule carte, prechochee : « choisir un palier » designe un geste qui
# n'existe plus dans le formulaire.
sub("Merci de choisir un palier et de remplir votre maison, votre catégorie, "
    "votre nom et un email valide.",
    "Merci de remplir votre maison, votre catégorie, votre nom et un email "
    "valide.")

# Un lien profond ?palier=p3 retombait deja sur la premiere carte par le
# fallback ; la valeur par defaut nomme desormais l'offre reelle.
sub('(pre || "p1")', '(pre || "standard")')

if e:
    print("\n".join(e))
    sys.exit(1)

open(P, "w", encoding="utf-8").write(s)

# --- controles de sortie, page produit -------------------------------------
s = open(P, encoding="utf-8").read()
for x in ['data-p="standard" data-an="2400" data-mois="240"',
          '<b class="v">2 400 €</b>',
          "Profil vérifié</div>",
          "Tarif de lancement du 6 août 2026",
          "2 400 € HT par an."]:
    if x not in s:
        e.append("ECHEC page : %s absent" % x)
# Les anciens montants ne doivent plus figurer nulle part sur la page, ni en
# affichage, ni en attribut de donnee.
for x in ["990", "6 900", "6900", "3 900", "3900", "2 000", '"2000"',
          'value="p1"', 'value="p2"', 'value="p3"', 'value="p4"',
          "choisir un palier", "Cabinet indépendant", "Maison établie",
          "Grande maison", "Institution</div>"]:
    if x in s:
        e.append("ECHEC page : %s subsiste" % x)
if e:
    print("\n".join(e))
    sys.exit(1)

# --- feuille d'appel salve 1 ----------------------------------------------
s = open(A, encoding="utf-8").read()
sub("cible 990 €", "cible 2 400 €", 18)
sub("cible 1900 €", "cible 2 400 €", 2)
sub("cible 3900 €", "cible 2 400 €", 1)
sub("Tarif : 990 € sous 100 M€ · 1 900 € de 100 à 500 M€ · 3 900 € de 500 M€ "
    "à 2 Md€ · 6 900 € au-delà.",
    "Tarif : 2 400 € HT par an pour toutes les maisons, ou 240 € HT par mois. "
    "Tarif de lancement du 6 août 2026, bloqué à vie pour qui souscrit avant "
    "la publication de la page de sa catégorie.")
if e:
    print("\n".join(e))
    sys.exit(1)
open(A, "w", encoding="utf-8").write(s)

s = open(A, encoding="utf-8").read()
for x in ["cible 990 €", "cible 1900 €", "cible 3900 €", "sous 100 M€"]:
    if x in s:
        e.append("ECHEC feuille d'appel : %s subsiste" % x)
if e:
    print("\n".join(e))
    sys.exit(1)

print("controle vert : page produit et feuille d'appel a 2 400 EUR HT/an")
