# Ecosysteme: nouveau titre de la page produit
#
# - H1 « Votre confrere d'a cote a deja son logo » remplace par
#   « Votre profil repond aux questions que les exiters posent. Frais, remuneration, tarifs. »
# - retour a la ligne avant l'italique vert, neutralise sous 760 px
# - premier benefice reformule, il repetait le titre mot pour mot
import sys
p = "fiche-verifiee.html"; s = open(p, encoding="utf-8").read(); e = []
def sub(a, b, n):
    global s
    c = s.count(a)
    if c != n: e.append("ECHEC %d/%d %s" % (c, n, a[:40])); return
    s = s.replace(a, b); print("ok %dx %s" % (c, a[:40]))
I = '<span style="font-style:italic;color:var(--accent)">'
sub("Votre confrère d'à côté " + I + "a déjà son logo.",
    "Votre profil répond aux questions que les exiters posent. <br>" + I + "Frais, rémunération, tarifs.", 1)
sub("h1.disp{font-size:33px}", "h1.disp{font-size:33px}h1.disp br{display:none}", 1)
sub("questions que les exiters se posent : frais, rémunération, tarifs",
    "questions de votre catégorie, écrites puis validées par vous", 1)
open(p, "w", encoding="utf-8").write(s)
if "confrère" in s: e.append("ECHEC reste « confrere »")
if "posent. <br>" + I + "Frais" not in s: e.append("ECHEC titre mal forme")
if "br{display:none}" not in s: e.append("ECHEC garde-fou mobile absent")
if e: print("\n".join(e)); sys.exit(1)
print("controle vert")
