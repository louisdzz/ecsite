# Ecosysteme: mur de logos resserre, recherche remontee, bandeau et menu mobiles
#
# 1. le mur de logos passe de onze rangees a quatre, cellules plus basses
# 2. la barre de recherche remonte juste sous les compteurs, avant le mur
# 3. le bandeau Exit Tape ne se figeait plus sur telephone :
#    - la pause au survol restait collee apres un tap sur ecran tactile
#    - les animations reduites le figeaient entierement : il devient
#      glissable au doigt au lieu de rester bloque
# 4. le menu du haut passe sur deux lignes en dessous de 560 px
import io, re, sys

F = "ecosysteme.html"
s = io.open(F, encoding="utf-8").read()
o = s
err = []


def sub(a, b, n):
    global s
    c = s.count(a)
    if c != n:
        err.append("%d occurrence(s) au lieu de %d : %s" % (c, n, a[:70]))
        return
    s = s.replace(a, b)


# ============================================== 1. le menu du haut, deux lignes
sub('    <div style="display:flex;align-items:center;gap:22px">\n'
    '      <a href="/#manifeste" style="font-size:13.5px;color:var(--muted);'
    'text-decoration:none">Le club</a>\n'
    '      <a href="#ligues" style="font-size:13.5px;color:var(--muted);'
    'text-decoration:none">Les Ligues</a>\n'
    '      <a href="/#events" style="font-size:13.5px;color:var(--muted);'
    'text-decoration:none">Événements</a>\n',
    '    <div class="topnav" style="display:flex;align-items:center;gap:22px">\n'
    '      <a class="tl" href="/#manifeste" style="font-size:13.5px;'
    'color:var(--muted);text-decoration:none">Le club</a>\n'
    '      <a class="tl" href="#ligues" style="font-size:13.5px;'
    'color:var(--muted);text-decoration:none">Les Ligues</a>\n'
    '      <a class="tl" href="/#events" style="font-size:13.5px;'
    'color:var(--muted);text-decoration:none">Événements</a>\n', 1)

# ============================================== 2. le bandeau sur telephone
# la pause au survol reste collee apres un tap sur un ecran tactile : on la
# reserve aux vrais pointeurs.
sub(".tape:hover .tape__track{animation-play-state:paused}",
    "@media(hover:hover) and (pointer:fine){"
    ".tape:hover .tape__track{animation-play-state:paused}}", 1)

# animations reduites : un ruban fige se lit comme une panne. Il devient
# glissable au doigt, le contenu reste atteignable.
sub("@media(prefers-reduced-motion:reduce){.tape__track{animation:none}"
    ".tk-fresh{animation:none}}",
    "@media(prefers-reduced-motion:reduce){.tape__track{animation:none}"
    ".tk-fresh{animation:none}"
    ".tape__win{overflow-x:auto;-webkit-overflow-scrolling:touch;"
    "-webkit-mask-image:none;mask-image:none}"
    ".tape__win::-webkit-scrollbar{display:none}}", 1)

# ============================================== 3. le mur de logos resserre
sub("<span>99 maisons cliquables ci-dessous, 4&nbsp;236 profils au total</span>",
    "<span>Un aperçu des maisons recensées, 4&nbsp;236 profils au "
    "total</span>", 1)

sub(".wall__g a{background:var(--card);height:62px;",
    ".wall__g a{background:var(--card);height:52px;", 1)

sub("@media(max-width:1000px){.wall__g{grid-template-columns:repeat(6,1fr)}}\n"
    "@media(max-width:760px){.wall__g{grid-template-columns:repeat(4,1fr)}"
    ".wall__g a{height:54px;padding:9px}"
    ".wall__h{flex-direction:column;gap:4px}}",
    # neuf colonnes, quatre rangees : les logos au-dela de la 36e place sortent
    ".wall__g a:nth-child(n+37){display:none}\n"
    "@media(max-width:1000px){.wall__g{grid-template-columns:repeat(6,1fr)}"
    ".wall__g a:nth-child(n+25){display:none}}\n"
    "@media(max-width:760px){.wall__g{grid-template-columns:repeat(4,1fr)}"
    ".wall__g a{height:46px;padding:8px}"
    ".wall__g a:nth-child(n+17){display:none}"
    ".wall__h{flex-direction:column;gap:4px}}\n"
    "@media(max-width:560px){.top{flex-wrap:wrap;gap:12px;padding:18px 0}"
    ".topnav{width:100%;justify-content:space-between;gap:10px!important}"
    ".topnav .tl{font-size:12.5px!important}}", 1)

# ------------------------------- l'espace sous les compteurs et le double filet
sub("border-bottom:1px solid var(--line);margin-top:34px}",
    "border-bottom:1px solid var(--line);margin-top:20px}", 1)
sub(".wall__h{display:flex;align-items:baseline;justify-content:space-between;"
    "gap:16px;border-top:1px solid var(--line);padding-top:14px}",
    ".wall__h{display:flex;align-items:baseline;justify-content:space-between;"
    "gap:16px;padding-top:16px}", 1)
# sur telephone les deux compteurs se cassaient en deux lignes : un par ligne
sub(".kpis{display:flex;gap:14px;margin-top:26px;flex-wrap:wrap}",
    ".kpis{display:flex;gap:14px;margin-top:26px;flex-wrap:wrap}\n"
    "@media(max-width:560px){.kpis .kpi{flex:1 0 100%}"
    ".kpis .kpi b{font-size:32px}}", 1)

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

# ============================================== 4. la recherche remonte
A = '\n<div class="toolbar">'
B = '\n\n  <details class="metho">'
i = s.find(A)
j = s.find(B, i)
if i < 0 or j < 0:
    print("ECHEC ancres de la barre de recherche introuvables")
    sys.exit(1)
bloc = s[i:j]
if 'id="q"' not in bloc or 'class="jump"' not in bloc:
    print("ECHEC le bloc deplace ne contient pas la barre et le sommaire")
    sys.exit(1)
if bloc.count("<div") != bloc.count("</div>"):
    print("ECHEC bloc deplace desequilibre : %d ouvrants, %d fermants"
          % (bloc.count("<div"), bloc.count("</div>")))
    sys.exit(1)
s = s[:i] + s[j:]

C = "\n  <!-- LOGOWALL:START -->"
k = s.find(C)
if k < 0:
    print("ECHEC ancre du mur de logos introuvable")
    sys.exit(1)
s = s[:k] + bloc + s[k:]

# ============================================== controles de sortie
for balise, att in (
    ('<div class="toolbar">', 1),
    ('id="q"', 1),
    ('class="jump"', 1),
    ('class="topnav"', 1),
    ('class="tl"', 3),
    ("nth-child(n+37)", 1),
    ("nth-child(n+25)", 1),
    ("nth-child(n+17)", 1),
    ("@media(hover:hover) and (pointer:fine)", 1),
    (".tape__win{overflow-x:auto", 1),
    ("margin-top:20px}", 1),
    (".wall__h{display:flex;align-items:baseline;justify-content:space-between;gap:16px;border-top", 0),
    (".wall__h{display:flex;align-items:baseline;justify-content:space-between;gap:16px;padding-top:16px}", 1),
    ("@media(max-width:560px){.kpis .kpi{flex:1 0 100%}", 1),
    ("99 maisons cliquables", 0),
    ("height:62px", 0),
    ('<section class="cat" id=', 15),
    ('<div class="cats">', 2),
    ("Je fais quoi de mon argent.", 1),
    ("Je fais quoi de ma vie.", 1),
    ('<!-- LOGOWALL:START -->', 1),
    ('<!-- LOGOWALL:END -->', 1),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise, att))
        sys.exit(1)

# l'ordre de la page : compteurs, recherche, mur, methodologie, categories
i_kpi = s.find('class="kpis"')
i_tb = s.find('<div class="toolbar">')
i_wall = s.find("<!-- LOGOWALL:START -->")
i_met = s.find('<details class="metho">')
i_cats = s.find('<div class="cats">')
if not (i_kpi < i_tb < i_wall < i_met < i_cats):
    print("ECHEC ordre de la page casse : %d %d %d %d %d"
          % (i_kpi, i_tb, i_wall, i_met, i_cats))
    sys.exit(1)

if s.count("<div") != o.count("<div") or s.count("</div>") != o.count("</div>"):
    print("ECHEC nombre de div modifie : %d/%d avant, %d/%d apres"
          % (o.count("<div"), o.count("</div>"), s.count("<div"), s.count("</div>")))
    sys.exit(1)
if len(re.findall(r'<li><a href="/f/', s)) != len(re.findall(r'<li><a href="/f/', o)):
    print("ECHEC nombre de lignes de maisons modifie")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : mur a 4 rangees, recherche sous les compteurs,")
print("                bandeau glissable, menu sur deux lignes en dessous de 560")
