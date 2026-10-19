"""Conservative extraction of existing facts for the visual directory profiles.

No network access or editorial enrichment. Empty fields mean that the source
contains no house-specific presentation, not that the house lacks a service.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
try:
    import lxml
    PARSER = 'lxml'
except ImportError:
    PARSER = 'html.parser'

# These sentences are category templates repeated throughout the source corpus.
# They must not be presented as a distinguishing description of one house.
_GENERIC_LEADS = {
    "Conseil en gestion de patrimoine : structuration et placement du patrimoine après la cession.",
    "Fonds de Private Equity & LBO : réinvestissement au capital de sociétés non cotées.",
    "Avocats d'affaires & fiscalistes : structuration juridique et fiscale de la cession (management package, 150-0 B ter, apport-cession, holding).",
    "Fonds de Venture Capital : réinvestissement dans l'innovation et les startups.",
    "Notaire patrimonial : transmission, donation et immobilier patrimonial.",
    "Banque d'affaires : conseil en cession, acquisition et financement.",
    "Banque privée : gestion de fortune bancaire, en France, en Suisse et au Luxembourg.",
    "Multi-Family Office : gestion globale et indépendante de patrimoines familiaux.",
    "Fonds de dette : dette privée, obligataire et solutions de rendement.",
    "Boutique M&A : conseil indépendant en cession et acquisition.",
    "Conseil en cession, acquisition et transmission d’entreprise.",
    "Groupement ou réseau national de cabinets d'expertise comptable et de commissariat aux comptes indépendants.",
    "Cabinet d'expertise comptable et d'audit.",
    "Assurance-vie luxembourgeoise : compagnie d'assurance-vie de droit luxembourgeois.",
}
_BOILERPLATE = re.compile(
    r"interview|à (?:venir|compléter|confirmer|documenter|recueillir|préciser)|"
    r"(?:informations?|éléments) (?:indicati|publi|contrôl|vérifi)|"
    r"communiqué(?:e)? par la maison|millésime|profil (?:référencé|non revendiqué)|"
    r"fiche (?:non revendiquée|non validée)|le référencement|"
    r"vous représentez|complétez la fiche|rejoindre|abonnez|"
    r"ce que les fondateurs|questions? (?:proposées?|à documenter)|"
    r"(?:présentez|précisez|demandez|vérifiez|consulter|retrouver)\b|"
    r"à (?:demander|vérifier|faire préciser)|faire préciser|doit être confirmé|"
    r"dépendent du véhicule ou du produit choisi|"
    r"les 100 qui font|voir le classement|ouverture prochaine|"
    r"les chiffres sont ceux|la colonne qui compte|la ligne qui compte|"
    r"usage typique chez nos membres|pour préparer le premier échange",
    re.I,
)
_SOCIAL_HOSTS = {
    'linkedin.com', 'facebook.com', 'instagram.com', 'youtube.com', 'x.com',
    'twitter.com', 'tally.so', 'notion.so', 'notion.site', 'exit.club',
    'annuaire-entreprises.data.gouv.fr', 'data.inpi.fr', 'orias.fr',
    'google.com', 'google.fr', 'bing.com', 'duckduckgo.com',
}


def _text(node) -> str:
    return re.sub(r"\s+", " ", node.get_text(' ', strip=True)).strip() if node else ''


def _normal(text: str) -> str:
    return text.replace('’', "'").replace('\u00a0', ' ').casefold()


def _informative(text: str, *, lead: bool = False) -> bool:
    if not text or _BOILERPLATE.search(text):
        return False
    if text.strip(' —–-%.,?') == '' or '…' == text.strip():
        return False
    if _normal(text) in {_normal(x) for x in _GENERIC_LEADS}:
        return False
    if lead and (len(text) < 28 or re.match(r'^(?:Agence du réseau|Entité du groupe)\b', text, re.I)):
        return False
    # Contact details, naked links and status lines are not a service description.
    if re.match(r'^(?:https?://|www\.|[^\s@]+@)', text) or ' · LinkedIn' in text:
        return False
    if len(text) > 1400:
        return False
    return True


def _official(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or '').lower().removeprefix('www.')
    return parsed.scheme in {'http', 'https'} and bool(host) and not any(
        host == blocked or host.endswith('.' + blocked) for blocked in _SOCIAL_HOSTS
    )


def extract_profile(path: Path) -> dict | None:
    """Extract existing profile content; return None for redirects and demos.

    category is {label, code}; logo is {src, alt}; facts is at most three
    {label, value} pairs. No description or metric is inferred from a category.
    """
    path = Path(path)
    raw = path.read_text(encoding='utf-8')
    soup = BeautifulSoup(raw, PARSER)
    refresh = soup.find('meta', attrs={'http-equiv': re.compile('refresh', re.I)})
    if refresh or re.search(r'(?:^|[-_])(?:demo|exemple|template|etalon)(?:$|[-_])', path.stem, re.I):
        return None
    h1 = soup.find('h1')
    if not h1:
        return None
    name = _text(h1)
    if re.search(r'fiche (?:d[’\']exemple|exemple|démo|demo)', name, re.I):
        return None
    slug = path.stem

    hero = soup.select_one('.hero') or soup.select_one('.hero-profile') or soup.select_one('.pv-identity')
    category_link = soup.select_one('.hero a.tag, .pv-category')
    if not category_link:
        category_link = next((a for a in soup.select('.crumb a, .breadcrumb a')
                              if a.get('href', '') != '/annuaire' and
                              ('metier=' in a.get('href', '') or '#' in a.get('href', ''))), None)
    category = {'label': _text(category_link), 'code': ''}
    if category_link:
        parsed = urlparse(category_link.get('href', ''))
        category['code'] = parse_qs(parsed.query).get('metier', [''])[0] or parsed.fragment
    if not category['label']:
        title = _text(soup.title)
        parts = title.split(' · ')
        if len(parts) > 1:
            category['label'] = parts[1].split(' | ')[0].strip()

    image = soup.select_one('.profile-visual img, .flogo img, .pv-brand-logo img')
    logo = {'src': image.get('src', ''), 'alt': image.get('alt', '')} if image else {'src': '', 'alt': ''}
    status_node = (hero.select_one('.over, .eyebrow, .pv-status') if hero else None) or soup.select_one('.pv-status')
    status = _text(status_node)

    candidates = []
    # Custom historical profiles place their useful description inside the hero.
    if hero:
        candidates += [p for p in hero.find_all('p')
                       if not set(p.get('class', [])) & {'over', 'eyebrow', 'source', 'risk'}]
    essential = soup.select_one('#profil-essentiel')
    if essential:
        for p in essential.select('p'):
            if p.find_parent(id='chiffre') or p.find_parent(id='contact'):
                continue
            if p.find_parent(class_='qa') or p.find_parent(class_='bigstat'):
                continue
            candidates.append(p)
    if slug in {'hedios', 'searchlight-capital-partners'}:
        candidates += soup.select('.card p, section.sect p')
    # A custom hero's descriptive paragraph is more informative than its slogan.
    candidates.sort(key=lambda p: (bool(set(p.get('class', [])) & {'lede', 'lead'}),))
    lead = next((_text(p) for p in candidates if _informative(_text(p), lead=True)
                 and not (p.find('a') and len(_text(p.find('a'))) >= len(_text(p)) * .65)), '')

    facts = []
    def add_fact(label: str, value: str) -> None:
        label, value = label.strip(), value.strip()
        if not label or not _informative(value) or len(value) > 240:
            return
        if any(x['label'] == label or x['value'] == value for x in facts):
            return
        facts.append({'label': label, 'value': value})

    # Structured, filled-in stats only. An em dash KPI is not an existing fact.
    for stat in soup.select('.stats .stat, .pv-compact-facts > div'):
        value = _text(stat.select_one('b, strong, dt'))
        label = _text(stat.select_one('span, dd'))
        add_fact(label, value)
    for stat in soup.select('.bigstat'):
        add_fact(_text(stat.select_one('.l')), _text(stat.select_one('.n')))
    if lead:
        # Handwritten factual lists are used by EXILLIUM and other custom pages.
        dl_rows = []
        for row in soup.select('dl.facts > div, dl.key-facts > div, dl.keyfacts > div'):
            label, value = _text(row.find('dt')), _text(row.find('dd'))
            if re.search(r'implantations?|langues?|fondation|création|siège|pays|devises?|minimum|ticket', label, re.I):
                dl_rows.insert(0, (label, value))
            else:
                dl_rows.append((label, value))
        for label, value in dl_rows:
            add_fact(label, value)
        # Actual service headings from bespoke cards, not template questions.
        if essential:
            for card in essential.select('.grid .card'):
                add_fact(_text(card.find('h3')), _text(card.find('p')))

    urls = []
    for a in soup.find_all('a', href=True):
        text = _text(a).lower()
        if ('sitel' in a.get('class', []) or 'site officiel' in text or
                'voir leur site' in text or 'site de la maison' in text or 'consulter le site de' in text or
                text.startswith('découvrir ' + name.lower()) or
                ('pv-primary' in a.get('class', []))):
            urls.append(a['href'])
    for script in soup.find_all('script', attrs={'type': 'application/ld+json'}):
        try:
            schema = json.loads(script.string or script.get_text())
        except (ValueError, TypeError):
            continue
        items = schema if isinstance(schema, list) else [schema]
        for item in items:
            if isinstance(item, dict):
                same_as = item.get('sameAs', [])
                urls.extend(same_as if isinstance(same_as, list) else [same_as])
    official_url = next((url for url in urls if isinstance(url, str) and _official(url)), '')
    return dict(name=name, slug=slug, category=category, logo=logo, status=status,
                lead=lead, facts=facts[:3], official_url=official_url)
