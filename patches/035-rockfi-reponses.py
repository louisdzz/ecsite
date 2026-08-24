# Ecosysteme: la fiche RockFi publie les reponses de la maison
#
# Germain Michou-Tonning (Directeur General) a repondu au questionnaire le
# 14/08/2026, attestation d'habilitation cochee. Le patch publie mot pour
# mot : statuts (CIF + courtier, ORIAS 23004556, Anacofi-CIF), mode MIF 2,
# modele economique, grille par tranche (1,2 % -> 0,5 %), les trois
# reponses aux questions des membres, le chiffre assume (20 points de
# base, millesime 2026) et les cinq reponses de l'interview sans filtre.
# Le CTA "repondre aux questions" devient un lien vers le site de la
# maison, et le compteur familles s'aligne sur leur propre declaration
# (1 200). Plus aucun "interview sans filtre a venir" sur la page.
import io, sys

F = "f/rockfi.html"
s = io.open(F, encoding="utf-8").read()
o = s

if "Réponse de RockFi · 14 août 2026" in s:
    print("existe deja : reponses publiees, rien a faire")
    sys.exit(0)

err = []
plan = []


def sub(a, b, n=1):
    plan.append(("R", a, b, n))


def inserer_apres_q(frag, texte):
    # insere la reponse dans le .etq de l'interview, apres le </div> du .q
    plan.append(("I", frag, texte, 1))


P = ('<p style="flex:1 1 100%;margin-top:8px;font-size:14px;'
     'color:var(--ink);line-height:1.65">')
RP = ('<div class="rep" style="display:block">'
      '<span class="chip-source">Réponse de RockFi · 14 août 2026</span>'
      '<p style="margin-top:8px;font-size:14px;color:var(--ink);'
      'line-height:1.65">')

# ------------------------------------------------ bloc 1 : etiquette
sub('association professionnelle).</small></div>'
    '<span class="chip-attente">Interview sans filtre à venir</span>',
    'association professionnelle).</small></div>'
    '<span class="chip-source">CIF · Courtier en assurance · '
    'ORIAS 23004556 · Anacofi-CIF</span>')
sub('remis sur pièces.</small></div>'
    '<span class="chip-attente">Interview sans filtre à venir</span>',
    'remis sur pièces.</small></div>'
    '<span class="chip-source">Les deux, selon la mission</span>')
sub('refusées ou restituées au client.</small></div>'
    '<span class="chip-attente">Interview sans filtre à venir</span></div>',
    'refusées ou restituées au client.</small></div>'
    '<span class="chip-source">Honoraires directs · clean shares à prix '
    'coûtant</span>'
    + P + 'Notre modèle tient en un principe : le client nous paie '
    'directement, en toute transparence. Un honoraire fixe, connu à '
    'l’avance, en général 1 % des encours et dégressif. C’est ce que nous '
    'appelons le Pacte de Transparence. En contrepartie, les produits que '
    'nous sélectionnons ne nous rémunèrent pas. Nous privilégions les '
    'parts clean shares, à prix coûtant, sans rétrocommission. Notre '
    'intérêt est donc parfaitement aligné avec celui du client : nous '
    'recommandons ce qui est le plus performant pour lui, pas ce qui nous '
    'rapporte le plus.</p></div>')

# ------------------------------------------------ bloc 2 : la grille
A = '<td class="pend">interview sans filtre à venir</td>' * 3 + '</tr>'


def ligne(rec, tout):
    return ('<td class="pend">non communiqué</td><td><b>' + rec
            + '</b></td><td>' + tout + '</td></tr>')


sub('<td class="deal">&lt; 2 M€</td>' + A,
    '<td class="deal">&lt; 2 M€</td>' + ligne('1,2 %', 'non communiqué'))
sub('<td class="deal">2 – 5 M€</td>' + A,
    '<td class="deal">2 – 5 M€</td>' + ligne('1 %', 'non communiqué'))
sub('<td class="deal">5 – 15 M€</td>' + A,
    '<td class="deal">5 – 15 M€</td>'
    + ligne('0,8 %', '≈ 31 000 € pour 5 M€ (détail au bloc 3)'))
sub('<td class="deal">15 – 50 M€</td>' + A,
    '<td class="deal">15 – 50 M€</td>' + ligne('0,6 %', 'non communiqué'))
sub('<td class="deal">50 M€ et plus</td>' + A,
    '<td class="deal">50 M€ et plus</td>' + ligne('0,5 %', 'non communiqué'))
sub('pas un pourcentage vague.</p>',
    'pas un pourcentage vague. Grille communiquée par la maison le '
    '14 août 2026 : honoraires récurrents dégressifs, calculés sur les '
    'actifs financiers gérés ; le taux sur le reste du patrimoine se '
    'négocie au cas par cas.</p>')

# ------------------------------------------------ bloc 3 : les questions
REPCHIP = ('<div class="rep"><span class="chip-attente">Réponse de RockFi '
           '· interview sans filtre à venir</span></div>')
sub('dans la communauté.</p>\n      ' + REPCHIP,
    'dans la communauté.</p>\n      ' + RP
    + 'Notre reporting consolidé affiche, par ligne et au global : la '
    'performance nette, le TER de chaque support et le TER consolidé du '
    'portefeuille, ainsi que la matrice de corrélation entre lignes. Le '
    'client voit le coût total réel (assureur + RockFi + société de '
    'gestion) et la structure de risque de son allocation, pas seulement '
    'la performance brute. Nous pouvons réaliser une démo de notre '
    'interface lors d’une visio.</p></div>')
sub('jamais obtenue.</p>\n      ' + REPCHIP,
    'jamais obtenue.</p>\n      ' + RP
    + 'Tout dépend de la structure du patrimoine. Nous nous rémunérons '
    'sur les actifs financiers placés et gérés chez nous, et le taux sur '
    'le reste du patrimoine (immobilier, autres actifs) se négocie au cas '
    'par cas.<br><br>Exemple concret sur 5 M€ : pour 2 M€ d’actifs '
    'financiers placés et gérés chez nous, l’honoraire est d’environ '
    '0,80 %, soit 16 000 € par an. Sur les 3 M€ restants (immobilier ou '
    'autres), un taux négocié autour de 0,50 %, soit 15 000 € par an. '
    'Soit un coût conseil d’environ 31 000 € par an tout compris, connu à '
    'l’avance et dégressif selon les montants confiés.</p></div>')
sub('distribué au retail.</p>\n      ' + REPCHIP,
    'distribué au retail.</p>\n      ' + RP
    + 'Nous disposons de contrats dédiés avec Generali et CNP en France, '
    'ainsi qu’avec des assureurs luxembourgeois comme Utmost, qui nous '
    'permettent de loger des allocations en parts clean shares '
    'directement dans le contrat. Pas de structure feeder intercalée, pas '
    'de passe-plat qui prélève une couche de frais : le support est '
    'accessible à prix coûtant, et la seule rémunération sur l’allocation '
    'reste notre honoraire de conseil prélevé sous forme de frais de '
    'gestion sur le contrat, connu du client. Les frais d’enveloppe sont '
    'ceux de l’assureur, affichés en toute transparence.</p></div>')

# ------------------------------------------------ bloc 4 : le chiffre
sub('<span class="n">— %</span>', '<span class="n">20 pb</span>')
sub('<span class="chip-attente">Communiqué par la maison · millésime '
    '2026</span>',
    '<span class="chip-source">Communiqué par la maison · millésime '
    '2026</span>')

# ------------------------------------------------ bloc 5 : l'interview
inserer_apres_q('30 secondes. Interdits : sur-mesure',
    'RockFi est un nouvel acteur de la gestion privée, créé en 2024. '
    'Nous sommes le conseil principal du patrimoine de nos clients : pas '
    'nécessairement l’endroit où sont logés tous les encours, mais '
    'l’interlocuteur qui a leur confiance et une vision globale de leur '
    'situation. Une équipe pour moitié issue de la banque privée, pour '
    'moitié de la tech, au service de 1 200 familles.')
inserer_apres_q('Il a 8 M€. Convainquez-le',
    'Il a raison sur l’essentiel : les ETF font mieux que 9 gérants sur '
    '10 sur la durée, et nous sommes les premiers à le dire. C’est le '
    'cœur de notre allocation, d’où notre partenariat exclusif avec '
    'BlackRock. S’il gère lui-même et s’y retrouve, nous ne cherchons pas '
    'à l’en dissuader. Mais à 8 M€, la performance des lignes ne '
    'représente qu’une part du sujet.<br><br>Le reste tient à '
    'l’accompagnement : arbitrer quand les marchés décrochent et que '
    'l’émotion prend le dessus, structurer la transmission alors que '
    '5 000 milliards d’euros vont changer de mains en France dans les '
    'quinze prochaines années, organiser la protection de ses proches et '
    'gérer la fiscalité. Gérer ses ETF seul est tout à fait possible. '
    'Préparer la transmission du fruit d’une vie l’est beaucoup moins. '
    'C’est un sujet trop important pour être traité seul, et c’est '
    'précisément là que nous sommes utiles.')
inserer_apres_q('votre propre cuisine ? »</div>',
    'Oui. Nos allocations personnelles reposent sur les mêmes ETF et '
    'clean shares, logés dans les mêmes contrats que ceux de nos clients, '
    'honoraire inclus. Nous ne recommandons pas de produits que nous '
    'refuserions de détenir nous-mêmes. Le véritable test n’est pas de '
    'montrer un portefeuille, mais d’assumer un conseil dont chaque ligne '
    'se justifie.')
inserer_apres_q('refusez de toucher ? »</div>',
    'Trois exemples concrets. 1. Les produits structurés dont l’upfront '
    'dépasse 4 % : au-delà, le coût pour le client n’est plus justifiable '
    'au regard de ce qu’il apporte. 2. Les SCPI, dont le modèle repose '
    'largement sur des commissions de souscription élevées et une '
    'liquidité que nous jugeons trop incertaine pour le patrimoine de nos '
    'clients. 3. Et les cryptoactifs, que nous n’intégrons pas dans nos '
    'allocations conseillées.')
inserer_apres_q('juste le cash ? »</div>',
    'Nous connaissons bien ce moment : une grande partie de nos clients '
    'sont des dirigeants qui viennent de céder tout ou partie de leur '
    'entreprise. Le produit de la cession n’est que la partie visible. '
    'L’enjeu réel se situe dans l’après : redonner une direction au '
    'patrimoine, structurer ce que l’on transmet, ce que l’on '
    'réinvestit, ce que l’on souhaite faire de cette nouvelle étape. Nos '
    'banquiers, issus du front office de la banque privée, ont déjà '
    'accompagné ces situations et savent en reconnaître les signaux. Ils '
    's’appuient sur notre équipe d’ingénierie patrimoniale pour '
    'structurer les réponses concrètes, puis le réemploi, la '
    'transmission, la fiscalité, la protection des proches. Prendre le '
    'temps de la discussion : l’accompagnement se fait sur plusieurs '
    'mois d’échange et de réflexion.<br><br>Nous restons lucides : nous '
    'ne sommes pas « psychologues », et nous ne prétendons pas apporter '
    'seuls toutes les réponses dont une personne peut avoir besoin à ce '
    'moment de sa vie. C’est précisément là qu’intervient la force de '
    'notre réseau et de l’interprofessionnalité : quand un besoin sort '
    'de notre champ, nous avons les bons confrères à recommander. '
    'Accompagner, ce n’est pas tout faire soi-même, c’est s’assurer que '
    'le client est entre les bonnes mains.')

# ------------------------------------------------ hero, gap, footer, meta
sub('Mise à jour juin 2026', 'Mise à jour août 2026')
sub('<b>~1 500</b><span>familles accompagnées</span>',
    '<b>1 200</b><span>familles accompagnées</span>')
sub('Ce profil se remplit avec la maison. <em>Les réponses publiées ici '
    'seront les siennes, mot pour mot.</em>',
    'Ces réponses sont celles de la maison, <em>mot pour mot.</em>')
sub('Vos futurs clients consultent l’Écosystème pour choisir leurs '
    'conseils. Les questions ci-dessus sont les leurs, mot pour mot, '
    'relevées dans les échanges entre nos membres.',
    'Communiquées et signées par Germain Michou-Tonning, Directeur '
    'Général, le 14 août 2026. Les questions sont celles des membres, '
    'mot pour mot, relevées dans leurs échanges.', 0)
sub("Vos futurs clients consultent l'Écosystème pour choisir leurs "
    'conseils. Les questions ci-dessus sont les leurs, mot pour mot, '
    'relevées dans les échanges entre nos membres.',
    'Communiquées et signées par Germain Michou-Tonning, Directeur '
    'Général, le 14 août 2026. Les questions sont celles des membres, '
    'mot pour mot, relevées dans leurs échanges.', 0)
sub('<a class="btn btn-inv" '
    'href="https://tally.so/r/QK94Jk?fiche=rockfi&cat=mfo&maison=RockFi">'
    'Répondre aux questions · 3 min →</a>',
    '<a class="btn btn-inv" href="https://www.rockfi.fr/" target="_blank" '
    'rel="noopener nofollow">Découvrir RockFi →</a>')
sub('Les éléments marqués « interview sans filtre à venir » seront '
    'renseignés par la maison et validés par elle avant publication : '
    'leur absence ne traduit aucun refus de sa part.',
    'Les réponses publiées sur cette page ont été communiquées et '
    'validées par la maison le 14 août 2026, et sont publiées mot pour '
    'mot.')
sub('chiffre assumé : interview sans filtre à venir.',
    'chiffre assumé : les réponses de la maison, mot pour mot.')

# ------------------------------------------------ execution en deux temps
for mode, a, b, n in plan:
    if mode == "R":
        c = s.count(a)
        if n == 0:
            continue  # variante optionnelle, verifiee ensemble plus bas
        if c != n:
            err.append("%d occurrence(s) au lieu de %d : %s"
                       % (c, n, a[:64]))
    else:
        if s.count(a) != 1:
            err.append("ancre interview %d fois : %s"
                       % (s.count(a), a[:64]))

# le paragraphe du gap existe avec apostrophe typo OU droite : exactement 1
gap_variantes = [x for x in plan if x[3] == 0]
if sum(s.count(x[1]) for x in gap_variantes) != 1:
    err.append("paragraphe gap introuvable (0 ou >1 variante)")

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

for mode, a, b, n in plan:
    if mode == "R":
        if n == 0:
            if s.count(a) == 1:
                s = s.replace(a, b, 1)
            continue
        s = s.replace(a, b, 1)
    else:
        i = s.index(a)
        j = s.index('</div></div>', i)
        s = s[:j + 6] + P + b + '</p>' + s[j + 6:]

# ------------------------------------------------ controles de sortie
for balise, att in (
    ("interview sans filtre à venir", 0),
    ("Interview sans filtre à venir", 0),
    ("chip-attente\">", 0),
    ("Réponse de RockFi · 14 août 2026", 3),
    ("ORIAS 23004556", 1),
    ("Anacofi-CIF", 1),
    ("Pacte de Transparence", 1),
    ("20 pb", 1),
    ("1 200", 2),
    ("Michou-Tonning", 1),
    ("tally.so/r/QK94Jk", 0),
    ("rockfi.fr", 4),
    ("non communiqué", 9),
):
    if s.count(balise) != att:
        print("ECHEC %d occurrence(s) de %s au lieu de %d"
              % (s.count(balise), balise[:44], att))
        sys.exit(1)
if len(s) <= len(o):
    print("ECHEC page non agrandie")
    sys.exit(1)

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : les reponses de la maison sont publiees, plus")
print("aucun element en attente sur la page")
