# Ecosysteme: la fiche Kepler Cheuvreux dit enfin son metier, et deux
# corrections de veracite relevees au meme controle
#
# 1. Kepler Cheuvreux : le texte generique de categorie cede la place au
#    metier reel, verifie sur sources primaires le 14/08/2026 : premier
#    courtier-analyste independant europeen, premier fournisseur independant
#    de produits structures en France (Kepler Cheuvreux Solutions), et une
#    activite banque d'affaires via le partenariat ECM avec CACIB.
# 2. Qonto : la fiche annoncait des fonds monetaires et des comptes a terme;
#    l'offre reelle est la remuneration des excedents du compte pro.
# 3. GlobeAir : "tarifs publies" devient "devis instantane en ligne",
#    conforme a ce que la maison propose reellement.
import io, sys

err = []


def sub_in(path, a, b, n):
    s = io.open(path, encoding="utf-8").read()
    c = s.count(a)
    if c != n:
        err.append("%s : %d occurrence(s) au lieu de %d : %s"
                   % (path, c, n, a[:60]))
        return
    io.open(path, "w", encoding="utf-8").write(s.replace(a, b))


# ------------------------------------------------ 1. Kepler Cheuvreux
sub_in("f/kepler-cheuvreux.html",
       "<p>Banque d'affaires : conseil en cession, acquisition et "
       "financement.</p>",
       "<p>Premier groupe européen indépendant de recherche actions et "
       "d'intermédiation, né du rapprochement de Kepler Capital Markets et "
       "de Crédit Agricole Cheuvreux. Sa filiale Kepler Cheuvreux Solutions "
       "est classée premier fournisseur indépendant de produits structurés "
       "en France. Le groupe intervient aussi en banque d'affaires sur les "
       "marchés actions, notamment via son partenariat Equity Capital "
       "Markets avec Crédit Agricole CIB.</p>", 1)

# ------------------------------------------------ 2. Qonto
sub_in("f/qonto.html",
       "avec une offre "
       "de placement de trésorerie adossée à des fonds monétaires et à des "
       "comptes à terme.",
       "avec rémunération des excédents de trésorerie directement sur le "
       "compte, à taux variable et capital disponible.", 1)

# ------------------------------------------------ 3. GlobeAir
sub_in("f/globeair.html",
       "avec réservation en ligne et tarifs publiés.",
       "avec devis instantané et réservation en ligne.", 1)

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

# ------------------------------------------------ controles de sortie
k = io.open("f/kepler-cheuvreux.html", encoding="utf-8").read()
for balise, att in (
    ("produits structurés", 1),
    ("recherche actions", 1),
    ("Kepler Cheuvreux Solutions", 1),
    ("Crédit Agricole CIB", 1),
    ("Banque d'affaires : conseil en cession", 0),
    ('<div class="k">Repères</div>', 1),
    ("keplercheuvreux.com", 3),
):
    if k.count(balise) != att:
        print("ECHEC kepler : %d occurrence(s) de %s au lieu de %d"
              % (k.count(balise), balise[:44], att))
        sys.exit(1)

q = io.open("f/qonto.html", encoding="utf-8").read()
if "fonds monétaires" in q or "comptes à terme" in q.split("grille")[0]:
    print("ECHEC qonto : mention residuelle de supports non proposes")
    sys.exit(1)
if q.count("excédents de trésorerie") != 1:
    print("ECHEC qonto : nouveau texte absent")
    sys.exit(1)

g = io.open("f/globeair.html", encoding="utf-8").read()
if "tarifs publi" in g:
    print("ECHEC globeair : tarifs publies residuel")
    sys.exit(1)

print("ok f/kepler-cheuvreux.html : metier reel, sources verifiees")
print("ok f/qonto.html : remuneration des excedents, sans CAT ni monetaire")
print("ok f/globeair.html : devis instantane en ligne")
print("controle vert : trois fiches alignees sur les faits")
