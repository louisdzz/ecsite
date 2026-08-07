# Ecosysteme: l'interview devient « l'interview sans filtre »
#
# - le bloc 5 des fiches au nouveau format s'appelait « L'interview » : titre,
#   sommaire, intitule de bloc, chips d'attente et cellules de tableau
# - il devient partout « l'interview sans filtre », y compris dans la promesse
#   « une heure d'interview sans filtre, nous ecrivons tout, vous validez tout »
# - les ancres id="interview" et href="#interview" ne changent pas : les liens
#   deja partages continuent de fonctionner
# - la page fiche-verifiee et la page de remerciement sont alignees

import glob
import re
import sys

e = []

SUBS = [
    ("L'interview", "L'interview sans filtre"),
    ("Interview à venir", "Interview sans filtre à venir"),
    ("interview à venir", "interview sans filtre à venir"),
    ("d'interview", "d'interview sans filtre"),
]

# Compte global attendu, mesure avant patch. Un ecart signale une fiche
# ajoutee ou retiree depuis : on s'arrete plutot que de patcher a l'aveugle.
ATTENDU = {
    "L'interview": 39,
    "Interview à venir": 34,
    "interview à venir": 149,
    "d'interview": 15,
    'id="interview"': 13,
    'href="#interview"': 13,
}

# Le marqueur du nouveau format est le sommaire, pas l'identifiant du bloc 1 :
# celui-ci vaut « etiquette » sur douze fiches et « conflits » sur
# cambon-partners.
fiches = [f for f in sorted(glob.glob("f/*.html"))
          if '<nav class="toc">' in open(f, encoding="utf-8").read()]
if len(fiches) != 13:
    print("ECHEC : %d fiches au nouveau format, 13 attendues" % len(fiches))
    sys.exit(1)

cibles = fiches + ["fiche-verifiee.html", "merci-fiche-verifiee.html"]

vu = dict.fromkeys(ATTENDU, 0)
for f in cibles:
    s = open(f, encoding="utf-8").read()
    for k in vu:
        vu[k] += s.count(k)
for k, n in sorted(ATTENDU.items()):
    if vu[k] != n:
        e.append("ECHEC decompte %s : %d trouve(s), %d attendu(s)"
                 % (k, vu[k], n))
if e:
    print("\n".join(e))
    sys.exit(1)

for f in cibles:
    s = open(f, encoding="utf-8").read()
    o = s
    for a, b in SUBS:
        s = s.replace(a, b)
    if s == o:
        e.append("ECHEC %s : aucune substitution" % f)
        continue
    open(f, "w", encoding="utf-8").write(s)

if e:
    print("\n".join(e))
    sys.exit(1)
print("ok %d fiches et 2 pages renommees" % len(fiches))

# --- controles de sortie ---------------------------------------------------
# Aucune occurrence de « interview » ne doit subsister sans « sans filtre »,
# hors ancres id= et href=.
for f in cibles:
    s = open(f, encoding="utf-8").read()
    r = (s.replace('id="interview"', "@")
          .replace('href="#interview"', "@")
          .replace("interview sans filtre", "@")
          .replace("Interview sans filtre", "@"))
    for m in re.finditer(r"[Ii]nterview", r):
        d = r[max(0, m.start() - 30):m.end() + 30]
        e.append("ECHEC %s : occurrence non renommee « %s »" % (f, d))

# Les ancres sont intactes et le sommaire pointe toujours sur le bloc 5.
for f in fiches:
    s = open(f, encoding="utf-8").read()
    for x in ['<section class="sect" id="interview">',
              '<a href="#interview">L\'interview sans filtre</a>',
              "<h2>L'interview sans filtre.</h2>",
              "Bloc 5 · L'interview sans filtre"]:
        if x not in s:
            e.append("ECHEC %s : %s absent" % (f, x))

if e:
    print("\n".join(e))
    sys.exit(1)

print("controle vert : l'interview sans filtre sur %d fiches, ancres intactes"
      % len(fiches))
