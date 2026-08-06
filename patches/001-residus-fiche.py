# Ecosysteme: derniers residus « fiche » sur la page produit
#
# - « voir la fiche » devient « voir le profil » sur les quatre exemples de questions
# - « les fiches completes uniques » devient « les profils complets uniques »
# - « Votre fiche est en ligne sous 7 jours » devient « Votre profil est en ligne sous 7 jours »
# - benefice « Votre lien de rendez-vous, en direct » supprime, redondant avec l'agenda en acces direct
# - indentation de la liste des benefices normalisee

import re, sys, html as H

p = "fiche-verifiee.html"
s = open(p, encoding="utf-8").read()
echecs = []

def sub(a, b, n):
    global s
    c = s.count(a)
    if c != n:
        echecs.append("ECHEC: « %s » attendu %d fois, trouve %d" % (a[:55], n, c))
        return
    s = s.replace(a, b)
    print("  ok  %dx  %s" % (c, a[:60].replace("\n", "\\n")))

sub("voir la fiche", "voir le profil", 4)
sub("les fiches complètes uniques", "les profils complets uniques", 1)
sub("Votre fiche est en ligne sous 7 jours", "Votre profil est en ligne sous 7 jours", 1)
sub("          <li>Votre lien de rendez-vous, en direct</li>\n", "", 1)
sub("        <li>Votre agenda en accès direct, sans formulaire de contact</li>\n"
    "        <li>Votre logo en tête de profil</li>",
    "          <li>Votre agenda en accès direct, sans formulaire de contact</li>\n"
    "          <li>Votre logo en tête de profil</li>", 1)

open(p, "w", encoding="utf-8").write(s)

# controle : plus aucune occurrence visible du mot « fiche » sur la page produit
v = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S)
v = H.unescape(re.sub(r'<[^>]+>', ' ', v))
rest = re.findall(r'.{0,40}\bfiches?\b.{0,40}', v, re.I)
if rest:
    echecs.append("ECHEC: %d occurrence(s) visible(s) de « fiche » : %s"
                  % (len(rest), " | ".join(re.sub(r'\s+', ' ', r) for r in rest[:4])))

if echecs:
    print("\n".join(echecs))
    sys.exit(1)
print("\ncontrole : aucune occurrence visible de « fiche » sur la page produit")
