# Ecosysteme: recherche tolerante et etat de resultat visible
#
# - la normalisation retire espaces, points et tirets : "rock fi", "J.P. Morgan",
#   "my way", "spiko " retrouvent desormais leur maison
# - une ligne sous le champ annonce le nombre d'acteurs trouves
# - zero resultat affiche un message au lieu d'une page vide
import io, sys

F = "ecosysteme.html"
s = io.open(F, encoding="utf-8").read()
o = s
err = []


def sub(a, b, n):
    global s
    c = s.count(a)
    if c != n:
        err.append("%d occurrence(s) au lieu de %d : %s" % (c, n, a[:60]))
        return
    s = s.replace(a, b)


# 1. normalisation tolerante
sub(
    "var norm=function(s){return s.normalize('NFD')"
    ".replace(/[\\u0300-\\u036f]/g,'').toLowerCase()};",
    "var norm=function(s){return s.normalize('NFD')"
    ".replace(/[\\u0300-\\u036f]/g,'').toLowerCase()"
    ".replace(/[^a-z0-9]/g,'')};",
    1,
)

# 2. la ligne de resultat dans la barre
sub(
    ' autocomplete="off">\n    <div class="jump">',
    ' autocomplete="off">\n    <div class="qres" id="qres"></div>\n    <div class="jump">',
    1,
)

# 3. le style de cette ligne
sub(
    "</style>",
    ".qres{margin-top:9px;font-size:13px;color:var(--muted);min-height:1px}\n"
    ".qres b{color:var(--ink);font-weight:600}\n"
    ".qres.none{color:var(--accent)}\n"
    ".qres a{color:inherit;border-bottom:1px dotted currentColor;text-decoration:none}\n"
    "body.searching #ligue-cgp,body.searching #ligues,"
    "body.searching #actualites{display:none}\n"
    "</style>",
    1,
)

# 4. le comptage et l'etat vide
A = """  q.addEventListener('input',function(){
    var v=norm(q.value.trim());
    lis.forEach(function(li){
      var show=!v||li.dataset.n.indexOf(v)>-1;
      li.classList.toggle('hidden',!show);
      li.classList.toggle('hit',!!v&&show);
    });
    document.querySelectorAll('.cat').forEach(function(cat){
      var any=cat.querySelector('.firms li:not(.hidden)');
      cat.style.display=any?'':'none';
    });
  });"""
B = """  var res=document.getElementById('qres');
  q.addEventListener('input',function(){
    var v=norm(q.value.trim());
    var n=0;
    document.body.classList.toggle('searching',!!v);
    lis.forEach(function(li){
      var show=!v||li.dataset.n.indexOf(v)>-1;
      if(show)n++;
      li.classList.toggle('hidden',!show);
      li.classList.toggle('hit',!!v&&show);
    });
    document.querySelectorAll('.cat').forEach(function(cat){
      var any=cat.querySelector('.firms li:not(.hidden)');
      cat.style.display=any?'':'none';
    });
    if(!res)return;
    if(!v){res.textContent='';res.className='qres';return}
    if(n){
      res.className='qres';
      res.innerHTML='<b>'+n+'</b> '+(n>1?'acteurs trouv\\u00e9s':'acteur trouv\\u00e9');
      return;
    }
    res.className='qres none';
    res.textContent='Aucun acteur ne correspond \\u00e0 \\u00ab '+q.value.trim()+' \\u00bb. ';
    var a=document.createElement('a');
    a.href='mailto:louis@exit.club?subject=%C3%89cosyst%C3%A8me%20%C2%B7%20acteur%20manquant';
    a.textContent='Signalez-le, on l\\'ajoute.';
    res.appendChild(a);
  });"""
sub(A, B, 1)

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

# controles de sortie
if s.count(".replace(/[^a-z0-9]/g,'')") != 1:
    print("ECHEC normalisation absente")
    sys.exit(1)
if s.count('id="qres"') != 1 or s.count("getElementById('qres')") != 1:
    print("ECHEC ligne de resultat absente")
    sys.exit(1)
if s.count("body.searching #ligue-cgp") != 1 or s.count("'searching'") != 1:
    print("ECHEC masquage de la Ligue absent")
    sys.exit(1)
if len(s) <= len(o):
    print("ECHEC fichier non agrandi")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : recherche tolerante, compteur, etat vide")
