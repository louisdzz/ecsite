# Ecosysteme: derniers residus « fiche » sur la page produit
#
# - « voir la fiche » devient « voir le profil » sur les quatre exemples
# - « les fiches completes uniques » devient « les profils complets uniques »
# - « Votre fiche est en ligne » devient « Votre profil est en ligne »
# - benefice « lien de rendez-vous » supprime, redondant avec l'agenda
# - indentation de la liste des benefices normalisee
import re, sys, html
p = "fiche-verifiee.html"; s = open(p, encoding="utf-8").read(); e = []
def sub(a, b, n):
    global s
    c = s.count(a)
    if c != n: e.append("ECHEC %d/%d %s" % (c, n, a[:40])); return
    s = s.replace(a, b); print("ok %dx %s" % (c, a[:50]))
sub("voir la fiche", "voir le profil", 4)
sub("les fiches complètes uniques", "les profils complets uniques", 1)
sub("Votre fiche est en ligne sous 7 jours", "Votre profil est en ligne sous 7 jours", 1)
sub("          <li>Votre lien de rendez-vous, en direct</li>\n", "", 1)
sub("        <li>Votre agenda en accès direct, sans formulaire de contact</li>\n        <li>Votre logo en tête de profil</li>",
    "          <li>Votre agenda en accès direct, sans formulaire de contact</li>\n          <li>Votre logo en tête de profil</li>", 1)
open(p, "w", encoding="utf-8").write(s)
v = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S)
v = html.unescape(re.sub(r'<[^>]+>', ' ', v))
r = re.findall(r'.{0,40}\bfiches?\b.{0,40}', v, re.I)
if r: e.append("ECHEC reste « fiche » : " + " | ".join(re.sub(r'\s+', ' ', x) for x in r[:4]))
if e: print("\n".join(e)); sys.exit(1)
print("controle vert : aucun « fiche » visible")
