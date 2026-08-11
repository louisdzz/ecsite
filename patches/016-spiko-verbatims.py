# Ecosysteme: fiche Spiko, verbatims resserres
#
# - la question « ou est l'arnaque ? », le constat « personne n'y a repondu »,
#   le CAT a plus de 4 %, le rappel sur les escroqueries et la mention du prix
#   de l'intermediation sortent de la fiche : trop accusatoires sur un profil
#   qui porte le nom d'une maison
# - les trois questions et le KPI restent intacts
import sys
p = "f/spiko.html"
s = open(p, encoding="utf-8").read()
V = '<p class="verb">'
R = [
 (V + "« Où est l&#x27;arnaque ? » La question revient à chaque annonce de taux dans les échanges entre membres. Personne n&#x27;y a répondu.</p>",
  V + "La question revient à chaque annonce de taux dans les échanges entre membres.</p>"),
 (V + "Un membre a quitté son support en découvrant 1,31 % servis. Un autre : « CAT à plus de 4 %, impossible aujourd&#x27;hui sauf anciens contrats. »</p>",
  V + "Un membre a quitté son support en découvrant 1,31 % servis.</p>"),
 (V + "Le sujet est systématiquement posé après le rappel qu&#x27;« un tiers des propositions d&#x27;investissement en France sont des escroqueries ».</p>",
  V + "Le sujet est systématiquement posé dès qu&#x27;un support nouveau est cité.</p>"),
 ("sur douze mois. C&#x27;est le prix de l&#x27;intermédiation.", "sur douze mois."),
]
for a, b in R:
    if s.count(a) != 1:
        print("ECHEC %d/1 : %s" % (s.count(a), a[-50:])); sys.exit(1)
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
for x in ["arnaque", "escroqueries", "plus de 4 %", "intermédiation."]:
    if x in s:
        print("ECHEC residu : %s" % x); sys.exit(1)
if "1,31 %" not in s or s.count('<section class="sect" id=') != 5:
    print("ECHEC structure"); sys.exit(1)
print("controle vert : verbatims resserres, blocs intacts")
