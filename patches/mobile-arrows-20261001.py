#!/usr/bin/env python3
# Accueil : fleches SVG pour eviter les emojis sur mobile
# Conserve les textes, liens, couleurs et mise en page.
from pathlib import Path
import hashlib

expected = {
    'index.html': ('1bc8cb6e0cbfefd4c333e02745c641b465b3b64fd64a5e1fdbfacd4b8a329b80', 'bf2e3571ac57eddb542d671b1179bc2f98a523e0328894240484a3f3c273c35c'),
    'assets/home/integration.css': ('cc7bb66aeea4f9e21a626decd0e438107f7af884e4f347d0f0c756c3373121e5', '2923a38c5ff39ab45901a0429e0dfc7069a43093c7e9cd0137bd7a16d840bf9a'),
}
svg = '<svg class="ui-arrow" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 19 19 5M5 5h14v14"/></svg>'
down = svg.replace('M5 19 19 5M5 5h14v14', 'M12 4v16m-6-6 6 6 6-6')
ready = []
for filename, (before, after) in expected.items():
    path = Path(filename)
    old = path.read_bytes()
    digest = hashlib.sha256(old).hexdigest()
    if digest == after:
        continue
    if digest != before:
        raise SystemExit('Fichier modifie depuis preparation : ' + filename)
    text = old.decode('utf-8')
    if filename == 'index.html':
        text = text.replace('↗', svg).replace('↓', down).replace('/assets/home/integration.css?v=20260926', '/assets/home/integration.css?v=20261001')
    else:
        text += '''
/* Vector icons prevent mobile platforms from substituting emoji glyphs. */
.ui-arrow{display:inline-block;width:1.15em;height:1.15em;flex-shrink:0;vertical-align:-.15em}
'''
    new = text.encode('utf-8')
    assert hashlib.sha256(new).hexdigest() == after, filename
    ready.append((path, new))
for path, content in ready:
    path.write_bytes(content)
print(len(ready), 'fichiers corriges')
