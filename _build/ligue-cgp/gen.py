# -*- coding: utf-8 -*-
"""Génère La Ligue des CGP et l'injecte dans ecosysteme.html entre les marqueurs
<!-- LIGUE-CGP:START --> et <!-- LIGUE-CGP:END -->.
Sources : _build/ligue-cgp/encours-gros.json + encours-intermediaires.json
(recherche documentée, chaque ligne porte son URL de source et sa date)."""
import json, os, re, unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)
SRC = '_build/ligue-cgp'

ROWS = json.load(open(SRC + '/encours-gros.json')) +             json.load(open(SRC + '/encours-intermediaires.json'))

MOIS = {1: 'janv.', 2: 'févr.', 3: 'mars', 4: 'avr.', 5: 'mai', 6: 'juin',
        7: 'juil.', 8: 'août', 9: 'sept.', 10: 'oct.', 11: 'nov.', 12: 'déc.'}

# ---------------------------------------------------------------- classement
# (nom_source, affichage, encours M€, nature, actionnaire de référence)
GROUPES = [
 ("Valoria Capital",                  "Valoria Capital",        36000, "groupe",     "TA Associates, IK Partners"),
 ("Groupe Crystal",                   "Groupe Crystal",         28000, "groupe",     "Goldman Sachs Alternatives, Seven2"),
 ("Cyrus Herez",                      "Cyrus Herez",            22000, "groupe",     "PAI Partners"),
 ("Groupe Premium",                   "Groupe Premium",         21000, "conseilles", "Montefiore, Eurazeo, Blackstone"),
 ("Astoria Finance",                  "Astoria Finance",        14000, "gestion",    "Carac"),
 ("UFF - Union Financiere de France",  "UFF",                   13000, "groupe",     "Abeille Assurances (Aéma)"),
 ("Groupe Patrimmofi",                "Groupe Patrimmofi",       4000, "gestion",    "Groupe VYV"),
 ("Advenis (groupe)",                 "Advenis",                 4000, "gestion",    "Inovalis, Hoche Partners"),
 ("Finzzle Groupe",                   "Finzzle Groupe",          3400, "conseilles", "Bridgepoint"),
 ("Groupe Synalp",                    "Groupe Synalp",           3000, "conseilles", "Capital Croissance (minoritaire)"),
 ("La Financiere d'Orion / Groupe Orion", "Groupe Orion",         3000, "conseilles", "Siparex (minoritaire)"),
 ("Fluence",                          "Fluence",                 3000, "conseilles", None),
 ("Rhetores Group",                   "Rhetores",                2700, "conseilles", "IK Partners"),
 ("Olifan Group",                     "Olifan Group",            2500, "conseilles", "Seven2"),
 ("Magnacarta Group",                 "Magnacarta",              2500, "groupe",     "Groupe April (KKR)"),
 ("Groupe Allen",                     "Groupe Allen",            2000, "conseilles", "Qualium Investissement"),
 ("Groupe Rayne",                     "Groupe Rayne",            2000, "gestion",    "Partenariat Tikehau Capital"),
 ("Equance",                          "Equance",                 1500, "conseilles", "Calcium Capital"),
 ("Inovea (Inovea Finance / Inovea Groupe)", "Inovea",            1300, "groupe",     "INDEP"),
 ("Metagram",                         "Métagram",                1100, "conseilles", "Meanings Capital Partners"),
 ("Emeraude Capital",                 "Emeraude Capital",         800, "groupe",     "Abenex, Arkéa Capital"),
]

# (nom_source, affichage, encours M€, nature, adossement | "INDEP" | None)
CABINETS = [
 ("iVesta Family Office",             "iVesta Family Office",    6000, "conseilles", "INDEP"),
 ("Aliquis Conseil",                  "Aliquis Conseil",         1100, "gestion",    "Cyrus Herez"),
 ("Come Maison Financiere",           "Come Maison Financière",  1000, "conseilles", None),
 ("Haussmann Patrimoine",             "Haussmann Patrimoine",     956, "conseilles", "INDEP"),
 ("Neowise",                          "Neowise",                  850, "conseilles", "Groupe Orion"),
 ("Colbert Patrimoine Finance",       "Colbert Patrimoine Finance", 650, "conseilles", "INDEP"),
 ("Haenggi & Associés",               "Haenggi &amp; Associés",   640, None,         "Groupe Premium"),
 ("Novalfi",                          "Novalfi",                  600, "gestion",    "INDEP"),
 ("Financière du Capitole",           "Financière du Capitole",   500, "gestion",    "Laplace (Groupe Crystal)"),
 ("Groupe CG Patrimoine (CG Finance / CG Family Office)", "Groupe CG Patrimoine", 500, "gestion", "INDEP"),
 ("Patrimoine & Gestion",             "Patrimoine &amp; Gestion", 500, "conseilles", "Groupe Patrimmofi"),
 ("HSC Finance",                      "HSC Finance",              450, None,         "Fluence"),
 ("Patrimum Groupe",                  "Patrimum Groupe",          450, "gestion",    "INDEP"),
 ("Héron Conseil (ex-COREP)",         "Héron Conseil",            400, "conseilles", "Laplace (Groupe Crystal)"),
 ("Fipagest",                         "Fipagest",                 400, "gestion",    "Astoria Finance"),
 ("Cimea Patrimoine",                 "Cimea Patrimoine",         400, "gestion",    "Cyrus Herez"),
 ("Groupe Sarro",                     "Groupe Sarro",             380, "gestion",    "INDEP"),
 ("CF Gestion Privée (CFGP)",         "CF Gestion Privée",        360, "gestion",    "Groupe CF"),
 ("ID Groupe (ID Patrimoine)",        "ID Groupe",                360, "gestion",    "Groupe Premium"),
 ("Option Patrimoine",                "Option Patrimoine",        360, None,         "Cyrus Herez"),
 ("Financière Conseil",               "Financière Conseil",       350, None,         "Cyrus Herez"),
 ("Partners Patrimoine",              "Partners Patrimoine",      340, None,         "Cyrus Herez"),
 ("Fair",                             "Fair",                     315, "gestion",    "Astoria Finance"),
 ("DLCM Finances",                    "DLCM Finances",            300, "gestion",    "Cyrus Herez"),
 ("Sefima",                           "Sefima",                   260, "gestion",    "Groupe Premium"),
 ("Groupe Corelliance (Montgrand, Cabinet Bedin)", "Groupe Corelliance", 250, "conseilles", "Laplace (Groupe Crystal)"),
 ("PCA Est",                          "PCA Est",                  250, "gestion",    "Astoria Finance"),
 ("Valeurs & Conseils (groupe V&C : JMS Patrimoine, Actif Conseil)", "Valeurs &amp; Conseils", 250, "gestion", "Métagram"),
 ("Delta Finance",                    "Delta Finance",            210, "gestion",    "Laplace (Groupe Crystal)"),
 ("Evolia",                           "Evolia",                   210, "conseilles", "Groupe Allen"),
 ("Vauban Patrimoine",                "Vauban Patrimoine",        200, "gestion",    "Métagram"),
 ("Euro Patrimoine Investissement (E.P.I. / Episa)", "Euro Patrimoine Investissement", 200, "gestion", "INDEP"),
 ("Alias Finance",                    "Alias Finance",            200, None,         "Groupe Patrimmofi"),
 ("Honova",                           "Honova",                   200, "conseilles", "Meilleurtaux Placement"),
 ("Conseils Patrimoine Services (CPS)", "Conseils Patrimoine Services", 180, "gestion", "Kereis"),
 ("Vendôme Investissement Conseil",   "Vendôme Investissement Conseil", 180, "gestion", "Groupe Patrimmofi"),
 ("Kara Patrimoine – Previka",        "Kara Patrimoine, Previka", 170, "conseilles", "Laplace (Groupe Crystal)"),
 ("Asfidia",                          "Asfidia",                  150, "gestion",    "Groupe Patrimmofi"),
 ("Hortus Patrimoine & Associés",     "Hortus Patrimoine &amp; Associés", 145, None, "Groupe Patrimmofi"),
 ("ICF (Institut de Conseil Financier)", "ICF",                   140, "gestion",    "Groupe Patrimmofi"),
 ("Adéquation",                       "Adéquation",               135, "conseilles", "Laplace (Groupe Crystal)"),
 ("Financiel",                        "Financiel",                130, "conseilles", "Astoria Finance"),
 ("V2A Patrimoine",                   "V2A Patrimoine",           130, None,         "Cyrus Herez"),
 ("Coté Profinance",                  "Coté Profinance",          120, None,         "Laplace (Groupe Crystal)"),
 ("Cabinet Conseil Torandell",        "Cabinet Conseil Torandell", 120, None,        "Groupe Patrimmofi"),
 ("JEC Finances",                     "JEC Finances",             115, "gestion",    "Astoria Finance"),
 ("Kribs Conseils",                   "Kribs Conseils",           110, "conseilles", "Laplace (Groupe Crystal)"),
 ("Traditia",                         "Traditia",                 100, "gestion",    "Olifan Group"),
 ("Actwin",                           "Actwin",                   100, "gestion",    "Groupe Premium (ID Groupe)"),
 ("Groupe Quinze – Gestion Privée",   "Groupe Quinze",            100, None,         "INDEP"),
]

# écartés du classement, et pourquoi (affiché publiquement : c'est la garantie)
ECARTES = [
 ("Nortia", "12,2 Md€", "plateforme de distribution B2B au service de plus de 3 000 CGP, pas un cabinet de conseil"),
 ("Financière d'Uzès", "2 Md€", "entreprise d'investissement agréée par l'ACPR, pas un CIF"),
 ("Primonial Ingénierie &amp; Développement", "13 Md€", "absorbé par le Groupe Crystal en juin 2024, déjà compté"),
 ("Herez", "5 Md€", "marque fusionnée dans Cyrus Herez, déjà comptée"),
 ("Amplegest", "5,7 Md€", "société de gestion filiale de Cyrus Herez, déjà comptée"),
 ("Métagram pôle Sud-Ouest", "350 M€", "pôle régional d'un consolidateur, pas un cabinet autonome"),
 ("Laplace, Kereis Expertises", "n.p.", "aucun encours propre publié"),
 ("Fiducée Gestion Privée", "n.p.", "entité disparue, absorbée par Magnacarta"),
]

NAT = {"gestion": "sous gestion", "conseilles": "conseillés", "groupe": "groupe"}

# ------------------------------------------------------------------ sources
BY = {}
for r in ROWS:
    BY.setdefault(r['nom'], r)


def norm(s):
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


H = open('ecosysteme.html', encoding='utf-8').read()
SLUG = {}
for m in re.finditer(r'href="/f/([a-z0-9\-]+)"[^>]*>(.*?)</a>', H, re.S):
    nm = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    SLUG.setdefault(norm(nm), m.group(1))

OVERRIDE = {"Fair": None, "Alias Finance": None, "Kara Patrimoine, Previka": None,
            "PCA Est": None, "JEC Finances": None, "Conseils Patrimoine Services": None,
            "Patrimoine & Gestion": None, "HSC Finance": None,
            "Groupe Allen": "groupe-allen-carat-capital-hedon-family-office",
            "Groupe Crystal": "crystal", "Rhetores": "rhetores-groupe",
            "Haenggi & Associés": "haenggi-associes", "ICF": "icf-groupe-patrimmofi"}


def slug_of(nom_src, disp):
    plain = re.sub(r'&amp;', '&', disp)
    if plain in OVERRIDE:
        return OVERRIDE[plain]
    cands = [plain, nom_src.split(' (')[0].split(' – ')[0].split(',')[0].strip(),
             plain.split(',')[0].strip()]
    for cand in cands:
        s = SLUG.get(norm(cand))
        if s:
            return s
    # repli : une seule fiche dont le nom commence par le nom affiché
    for cand in cands:
        k = norm(cand)
        if len(k) < 6:
            continue
        hits = sorted({v for kk, v in SLUG.items() if kk.startswith(k + ' ')})
        if len(hits) == 1:
            return hits[0]
    return None


def fmt_meur(v):
    if v >= 1000:
        return ('%.1f' % (v / 1000.0)).replace('.0', '').replace('.', ',') + ' <i>Md€</i>'
    return '%d <i>M€</i>' % v


def datestr(d):
    if not d:
        return '<span style="color:var(--faint)">non daté</span>'
    y, m = d.split('-')[0], d.split('-')[1] if '-' in d else None
    return (MOIS[int(m)] + ' ' if m else '') + y


def source_title(nom_src, meur, nat):
    r = BY.get(nom_src, {})
    lib = (r.get('encours_libelle') or '').strip()
    src = (r.get('source_nom') or '').strip()
    t = lib or ('%s M€' % meur)
    if src:
        t += ' · ' + src
    return re.sub(r'\s+', ' ', t).replace('"', '&quot;')[:300]


def row(i, nom_src, disp, meur, nat, right, own_col):
    s = slug_of(nom_src, disp)
    team = '<a href="/f/%s">%s</a>' % (s, disp) if s else disp
    r = BY.get(nom_src, {})
    if own_col:
        if right == 'INDEP':
            cell = '<span class="tag ind">Indépendant</span>'
        elif right is None:
            cell = '<span class="tag nc">Non communiqué</span>'
        else:
            cell = right
    else:
        cell = right if right and right != 'INDEP' else (
            '<span class="tag ind">Indépendant</span>' if right == 'INDEP'
            else '<span class="tag nc">Non communiqué</span>')
    return ('<tr class="%s" data-ind="%d"><td class="pos">%d</td><td class="team">%s</td>'
            '<td class="aum" title="%s">%s</td><td class="nat">%s</td><td class="own">%s</td>'
            '<td class="lastop">%s</td></tr>') % (
        'pod' if i <= 3 else '', 1 if right == 'INDEP' else 0, i, team,
        source_title(nom_src, meur, nat), fmt_meur(meur),
        NAT.get(nat, '<span style="color:var(--faint)">n.p.</span>'),
        cell, datestr(r.get('date')))


def table(rows, head_own, own_col):
    out = ['<table>', '<thead><tr><th>#</th><th>%s</th><th class="rt">Encours</th>'
           '<th>Nature</th><th>%s</th><th>Chiffre publié</th></tr></thead><tbody>'
           % ('Groupe' if own_col else 'Cabinet', head_own)]
    for i, (ns, disp, meur, nat, right) in enumerate(rows, 1):
        out.append(row(i, ns, disp, meur, nat, right, own_col))
    out += ['</tbody>', '</table>']
    return '\n      '.join(out)


nb_ind = sum(1 for r in CABINETS if r[4] == 'INDEP')
ecartes_html = ' '.join(
    '<b>%s</b> (%s) : %s.' % (n, v, why) for n, v, why in ECARTES)

BLOC = """<!-- LIGUE-CGP:START -->
  <section class="league" id="ligue-cgp">
    <div class="ah"><div><p class="eyebrow2">Saison 2026 · nouveau classement</p><h2 class="disp2">La Ligue des CGP.</h2></div>
    <a class="linkbtn" href="#cgp">Voir les 3 056 cabinets recensés ↓</a></div>
    <p class="lsub2">Vous voulez savoir qui pèse quoi dans la gestion de patrimoine française, et surtout <b>qui appartient à qui</b>. C'est devenu la question la plus difficile du marché : en cinq ans, la quasi-totalité des cabinets de taille intermédiaire est passée sous le contrôle d'un consolidateur, lui-même détenu par un fonds. Nous avons donc reconstitué les deux étages. Sur %d cabinets classés, <b>%d sont encore indépendants</b>.</p>
  <section class="league-t">
    <div class="lh"><h2 class="disp">Les groupes et les consolidateurs</h2><p class="lsub">Encours au niveau du groupe, et actionnaire de référence derrière l'enseigne</p></div>
      %s
  </section>

  <section class="league-t" id="lcgp-cab">
    <div class="lh"><h2 class="disp">Les cabinets</h2><p class="lsub">Encours du cabinet lui-même, et son adossement réel. Survolez un encours pour voir la source exacte.</p></div>
    <div class="filt">
      <button class="on" data-f="tous">Les 50 cabinets</button>
      <button data-f="indep">Indépendants seulement</button>
      <span id="lcgpCount"></span>
    </div>
      %s
  </section>

    <div class="metho">
      <p><b>Méthodologie.</b> Chaque ligne reprend un chiffre <b>publié</b> par le cabinet lui-même ou par la presse professionnelle, jamais une estimation. La colonne Nature dit ce que le chiffre mesure vraiment : <b>sous gestion</b> (le cabinet gère), <b>conseillés</b> (le cabinet conseille sans gérer), <b>groupe</b> (périmètre consolidé). Confondre les trois est l'erreur la plus courante des palmarès du secteur, et elle change les classements du tout au tout. La date est celle de la publication du chiffre, pas celle de la mise à jour de cette page. Le classement ne vaut pas recommandation : il mesure une taille déclarée, rien d'autre.</p>
      <p style="margin-top:10px"><b>Écartés du classement, et pourquoi.</b> %s</p>
      <p style="margin-top:10px"><b>Votre encours n'est pas là, ou il a changé ?</b> <a href="mailto:louis@exit.club?subject=Ligue%%20des%%20CGP%%20·%%20mon%%20encours" style="color:var(--accent)">Envoyez-le avec sa source</a>, il est vérifié puis publié. Les cabinets à <b>fiche vérifiée</b> voient leur encours actualisé automatiquement à chaque publication.</p>
    </div>
  </section>

<script>
(function(){
  var s=document.getElementById('lcgp-cab'); if(!s) return;
  var rows=s.querySelectorAll('tbody tr'), btns=s.querySelectorAll('.filt button'), c=document.getElementById('lcgpCount');
  function apply(f){
    var n=0;
    rows.forEach(function(tr){
      var keep = (f==='tous') || tr.dataset.ind==='1';
      tr.classList.toggle('hid', !keep);
      if(keep) n++;
    });
    c.textContent = (f==='indep') ? n+' cabinets sans fonds ni consolidateur au capital' : '';
  }
  btns.forEach(function(b){ b.addEventListener('click', function(){
    btns.forEach(function(x){x.classList.remove('on')}); b.classList.add('on'); apply(b.dataset.f);
  })});
})();
</script>
<!-- LIGUE-CGP:END -->""" % (len(CABINETS), nb_ind,
                            table(GROUPES, 'Actionnaire de référence', True),
                            table(CABINETS, 'Indépendance', False),
                            ecartes_html)

new = re.sub(r'<!-- LIGUE-CGP:START -->.*?<!-- LIGUE-CGP:END -->', lambda m: BLOC, H, flags=re.S)
assert new != H, 'marqueurs introuvables'
open('ecosysteme.html', 'w', encoding='utf-8').write(new)
sans = [d for ns, d, mu, na, r in GROUPES + CABINETS if not slug_of(ns, d)]
print('Ligue des CGP : %d groupes + %d cabinets, %d indépendants, %d écartés'
      % (len(GROUPES), len(CABINETS), nb_ind, len(ECARTES)))
print('sans fiche liée (%d) : %s' % (len(sans), ', '.join(sans)))
