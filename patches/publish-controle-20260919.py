#!/usr/bin/env python3
# Corriger les formulaires de l'annuaire et le contraste Finary
# 17 metiers pris en charge et maison conservee depuis les fiches EXILLIUM et QCP.
import base64, hashlib, json, zlib
from pathlib import Path
PATCHES=json.loads(zlib.decompress(base64.b64decode('eNrdlllvGkkQx78K4nWdpO/uWikPPgTBSXzGHBPloasPwJkB4sEHXu133xrbSQjEKz+u1hI0Zobqrv/8/lX1+a/2wi8n7T9b7TwNk/TqJl1N8zSl15NlVbZ3Wu15GZurILJzMjphjDOZMe4ZKmmzy5EnaSyCi6BV1lyn5GNWkE1IAELyaIIwTahZum1C2WSl48zwqCBCxpiZsdEz77wNJjlrMr28tJxbnuiumJM3XJiAjNMmTagw8bNxqinc589ccG52Wk9Lu7e/O/7xOri7Ce/OFijUH/13Hw6+DY9uQtVf+cHF+LDqLMNBPcYBXN+ako0G5ar4dHuDco95+u5kPB+vxzrpwm3sljd4qfdG8mxRzD6OcdZf0m9XftjhxfCj+yC+36PeP3eO02GxGA0fPo+L4/e71aBTFVVnQee6P9mHH/ftT3fX93c/zvW1r0K3w0JVTh72mu5WowG/PV7tLXB2RHnc1d/j35rdMTZ7hONFfHc4wSqW4fKXHN+2v+y0PnOlhCQNH5f2h/1D1pwHVz3TK89WlOM9ysOS9ix7+6NfNTvv1b2qc0lnqcKKX8cBb+67i4P+fe9yPj0dHNFexX2vqznSOX5cm95OfdVnodnja0f4QefhTL3up+n4sJwUVTHxQ9pz1cTfzLn5zbYOvW55HeTZBLt3T98dHMz392o13y+a84aqc12I/qo3fkt5f/l7p/WT/6uU01WahVSl2XIT/yBDThYgeKJUBY7KRI4uspACMNDe2cy951GgY9Jj8EEEi0rnFNAYv4Y/aOGSyIER3hAYgY8JbBA5onWgWLKWPGQ8qMhBRy6jRB8RyHIguQ+b+Gtr9E7r8b19NpzcFsND9mFwdIPDPXpAh3VxvnvT6xKg3ZIVw/7qRZBtPfRigsNd2+vyG6wJpm4D7MXLgH8GgJfB/i9g3L/ErOoRcGuV2mk9vjd4l+ndXhlmZ/e/KDX8OD2eHnYer50uRwKWdMLJqLojBdx4NOx/9cOzMg570/+YRbZwzm/S3bQsp9fVJstUS4k6zxMYGXwyynA0LIGWAiCidIQelXmmYozEppFKxsADlWQLknm1XspZYskrbnT0qLkDtCFaa5MUhKuTEEQT03rGQgSrqXn4QHgHoaRDk7dKObOKMH5a2ifiwc5UuvqPT/miPzq/uPt43u8fPZbv5eVoeAoFUU8lb/Vdn6drlR8czYtPvEzdssZuyfH07W90+hYWmxIpsq9IPmGy3GStVFL0D3jk1AWNAgcWogNGX1I+DnPMklFWGThVCenWJMrGZqW90Kgs85hIWR2UJNWZQRYNtVQvqbeBiNT7NBNJUN9k5H+BDCH+ptsZ9tDtmmVbon7n4OLJrCPRYSeD32O3IdHdSO5uSePrOi3rNynM61W9pLr4pvLTej57E/3Sv76kT2uSJWUzJM0sB0QgDQzLDIUwThJjTENQUccgWWDWRmMVyZhj0JoxZxmINckUA5ocLGJKDCx1fiE9MaUommSIKqNxwQEYkodTfIZZ2KCz9SkJh2lTMkWDgYCdVrPKpr1RK+QvTraeX1+FVL8q5+N5vZk1l4HSRi1Z0ii5AKowgGQwzslOSXBQmp6/F6icFRCT4WSQDFEwMNzptay9VYE5nzP1F5MNOq1JS+mZiF6DlI4GLIXaW6IwgiQILfUijCQ0DWJMbWZtyJXC7rSaVfLnsp7Nrv30amvc0xI4j8EYngUgC9SujLLaRkl2j456HUdGs16Q0dDYZ60LlLONPGZPf+vjnjBkfzKL1Zh1JCfJhNwyI0FnxlmOBEhIKSgSK2cRhXDU5lzIVG8UTZJbBpBNNlyqJqfjc36JQlMlhrr4jbt/Ps7/a4bPcusXC6J1LWOqy6yxYvRReA8hoKTqLVxQNPYFLRQBLBNN8wRWkEDzS36YOxLN6SqZdYcyp50iH0prSbZsqPpLT84zwqoINPonqpVUC5DIJQEzkiDUGxgFlzRBsS1WHTgiFZh7JuMv/wDUJcwl')))
ready=[]
for item in PATCHES:
    path=Path(item['path'])
    assert not path.is_absolute() and '..' not in path.parts
    old=path.read_bytes() if path.exists() else b''
    sha=hashlib.sha256(old).hexdigest() if path.exists() else None
    if sha==item['new']:continue
    if sha!=item['old']:raise SystemExit('Fichier modifie depuis preparation : '+str(path))
    new=old
    for start,end,replacement in reversed(item['changes']):
        new=new[:start]+base64.b64decode(replacement)+new[end:]
    assert hashlib.sha256(new).hexdigest()==item['new']
    ready.append((path,new))
for path,new in ready:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(new)
print(len(ready),'fichiers mis a jour')
