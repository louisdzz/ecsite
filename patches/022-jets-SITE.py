# Ecosysteme: verticale Aviation d'affaires et plateforme /jets
#
# 1. cree la page /jets : les disponibilites en direct des operateurs,
#    alimentee par l'API /api/dispos de exit-club-app, avec repli statique
# 2. ouvre le bloc "Apres la cession" sous les 14 categories financieres,
#    avec la categorie Aviation d'affaires (ancre jets)
# 3. cree les 7 fiches operateurs au format standard, blocs en attente
#
# Les verbatims du bloc 3 sont volontairement absents : aucun corpus
# WhatsApp jets n'existe encore. Les questions, elles, sont sourcees metier.
import base64, io, os, sys

err = []


def esc(t):
    return t.replace("'", "&#x27;")


# ============================================================ 1. la page /jets
JETS_B64 = (
    "PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImZyIj4KPGhlYWQ+CjxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KPG1ldGEgbmFt"
    "ZT0idmlld3BvcnQiIGNvbnRlbnQ9IndpZHRoPWRldmljZS13aWR0aCwgaW5pdGlhbC1zY2FsZT0xLjAiPgo8dGl0bGU+SmV0"
    "cyBkJiN4Mjc7YWZmYWlyZXMgOiBsZXMgZGlzcG9uaWJpbGl0w6lzIGVuIGRpcmVjdCB8IEwmI3gyNzvDiWNvc3lzdMOobWUg"
    "ZGUgbCYjeDI3O0V4aXQ8L3RpdGxlPgo8bWV0YSBuYW1lPSJkZXNjcmlwdGlvbiIgY29udGVudD0iTGVzIGRpc3BvbmliaWxp"
    "dMOpcyBlbiBkaXJlY3QgZGVzIG9ww6lyYXRldXJzIGRlIGpldHMgZCYjeDI3O2FmZmFpcmVzIHLDqWbDqXJlbmPDqXMgZGFu"
    "cyBMJiN4Mjc7w4ljb3N5c3TDqG1lIGRlIGwmI3gyNztFeGl0IDogZW1wdHkgbGVncywgdm9scyDDoCBsYSBkZW1hbmRlLCBw"
    "YXJ0cyBmcmFjdGlvbm7DqWVzLiBEw6lwYXJ0LCBhcnJpdsOpZSwgYXBwYXJlaWwsIHBsYWNlcywgcHJpeC4iPgo8bGluayBy"
    "ZWw9ImNhbm9uaWNhbCIgaHJlZj0iaHR0cHM6Ly93d3cuZXhpdC5jbHViL2pldHMiPgo8bWV0YSBwcm9wZXJ0eT0ib2c6dGl0"
    "bGUiIGNvbnRlbnQ9IkpldHMgZCYjeDI3O2FmZmFpcmVzIMK3IEwmI3gyNzvDiWNvc3lzdMOobWUgZGUgbCYjeDI3O0V4aXQi"
    "Pgo8bWV0YSBwcm9wZXJ0eT0ib2c6ZGVzY3JpcHRpb24iIGNvbnRlbnQ9IlBsdXNpZXVycyBvcMOpcmF0ZXVycywgdW5lIHNl"
    "dWxlIHBhZ2UsIGxlcyBkaXNwb25pYmlsaXTDqXMgZW4gZGlyZWN0LiI+CjxtZXRhIHByb3BlcnR5PSJvZzp1cmwiIGNvbnRl"
    "bnQ9Imh0dHBzOi8vd3d3LmV4aXQuY2x1Yi9qZXRzIj4KPHN0eWxlPgpAaW1wb3J0IHVybCgnaHR0cHM6Ly9mb250cy5nb29n"
    "bGVhcGlzLmNvbS9jc3MyP2ZhbWlseT1GcmF1bmNlczppdGFsLG9wc3osd2dodEAwLDkuLjE0NCwzMDA7MCw5Li4xNDQsNDAw"
    "OzAsOS4uMTQ0LDUwMDsxLDkuLjE0NCwzMDA7MSw5Li4xNDQsNDAwJmZhbWlseT1JbnRlcjp3Z2h0QDQwMDs1MDA7NjAwJmRp"
    "c3BsYXk9c3dhcCcpOwo6cm9vdHstLXBhcGVyOiNGN0YzRTQ7LS1pbms6IzJBMzUxQTstLWFjY2VudDojNDc2MjFFOy0tbXV0"
    "ZWQ6IzZGNzg1NDstLWZhaW50OiM5OEEwN0U7LS1saW5lOiNEREQ2QkM7LS1jYXJkOiNGQ0ZBRjB9Cip7Ym94LXNpemluZzpi"
    "b3JkZXItYm94O21hcmdpbjowO3BhZGRpbmc6MH0KYm9keXtiYWNrZ3JvdW5kOnZhcigtLXBhcGVyKTtjb2xvcjp2YXIoLS1p"
    "bmspO2ZvbnQtZmFtaWx5OidJbnRlcicsQXJpYWwsc2Fucy1zZXJpZjtsaW5lLWhlaWdodDoxLjU7LXdlYmtpdC1mb250LXNt"
    "b290aGluZzphbnRpYWxpYXNlZH0KLmRpc3B7Zm9udC1mYW1pbHk6J0ZyYXVuY2VzJyxHZW9yZ2lhLHNlcmlmO2ZvbnQtdmFy"
    "aWF0aW9uLXNldHRpbmdzOiJvcHN6IiAxNDQ7Zm9udC13ZWlnaHQ6MzAwO2xldHRlci1zcGFjaW5nOi0uMDFlbX0KLndyYXB7"
    "bWF4LXdpZHRoOjEwMDBweDttYXJnaW46MCBhdXRvO3BhZGRpbmc6MCA0MHB4fQoudG9we2Rpc3BsYXk6ZmxleDthbGlnbi1p"
    "dGVtczpjZW50ZXI7anVzdGlmeS1jb250ZW50OnNwYWNlLWJldHdlZW47cGFkZGluZzoyNnB4IDB9Ci5tYXJre2ZvbnQtZmFt"
    "aWx5OidGcmF1bmNlcycsR2VvcmdpYSxzZXJpZjtmb250LXNpemU6MjFweDt0ZXh0LWRlY29yYXRpb246bm9uZTtjb2xvcjp2"
    "YXIoLS1pbmspfQoubWFyayBpe2ZvbnQtc3R5bGU6aXRhbGljfS5tYXJrIGJ7Zm9udC13ZWlnaHQ6NjAwfQoudG9wbmF2e2Rp"
    "c3BsYXk6ZmxleDtnYXA6MThweDthbGlnbi1pdGVtczpjZW50ZXI7Zm9udC1zaXplOjEzLjVweH0KLnRvcG5hdiBhe2NvbG9y"
    "OnZhcigtLW11dGVkKTt0ZXh0LWRlY29yYXRpb246bm9uZX0KLnRvcG5hdiBhLmJ0bi1we2JhY2tncm91bmQ6dmFyKC0taW5r"
    "KTtjb2xvcjp2YXIoLS1wYXBlcik7cGFkZGluZzo5cHggMThweDtib3JkZXItcmFkaXVzOjk5OXB4O2ZvbnQtd2VpZ2h0OjYw"
    "MH0KLmNydW1ie2ZvbnQtc2l6ZToxMi41cHg7Y29sb3I6dmFyKC0tZmFpbnQpO3BhZGRpbmc6NnB4IDAgMH0KLmNydW1iIGF7"
    "Y29sb3I6dmFyKC0tbXV0ZWQpO3RleHQtZGVjb3JhdGlvbjpub25lfQouaGVyb3twYWRkaW5nOjI2cHggMCA2cHg7bWF4LXdp"
    "ZHRoOjY4MHB4fQoub3Zlcntmb250LXNpemU6MTJweDtsZXR0ZXItc3BhY2luZzouMjZlbTt0ZXh0LXRyYW5zZm9ybTp1cHBl"
    "cmNhc2U7Y29sb3I6dmFyKC0tZmFpbnQpO21hcmdpbjowIDAgMTRweH0KaDEuZGlzcHtmb250LXNpemU6NDZweDtsaW5lLWhl"
    "aWdodDoxLjAyfQoubGVkZXtmb250LXNpemU6MTUuNXB4O2NvbG9yOnZhcigtLW11dGVkKTttYXJnaW46MTZweCAwIDA7bGlu"
    "ZS1oZWlnaHQ6MS42fQouYm9hcmR7YmFja2dyb3VuZDp2YXIoLS1jYXJkKTtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUp"
    "O2JvcmRlci1yYWRpdXM6MThweDttYXJnaW46MzBweCAwIDA7b3ZlcmZsb3c6aGlkZGVufQouYmhlYWR7ZGlzcGxheTpmbGV4"
    "O2dhcDoxNHB4O2FsaWduLWl0ZW1zOmNlbnRlcjtqdXN0aWZ5LWNvbnRlbnQ6c3BhY2UtYmV0d2VlbjtmbGV4LXdyYXA6d3Jh"
    "cDtwYWRkaW5nOjE2cHggMjBweDtib3JkZXItYm90dG9tOjFweCBzb2xpZCB2YXIoLS1saW5lKX0KLmZpbHRlcnN7ZGlzcGxh"
    "eTpmbGV4O2dhcDoxMHB4O2ZsZXgtd3JhcDp3cmFwO2ZsZXg6MTttaW4td2lkdGg6MH0KLmZpbHRlcnMgaW5wdXQsLmZpbHRl"
    "cnMgc2VsZWN0e2ZvbnQtc2l6ZToxNHB4O2ZvbnQtZmFtaWx5OidJbnRlcicsQXJpYWwsc2Fucy1zZXJpZjtwYWRkaW5nOjEw"
    "cHggMTRweDtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpO2JvcmRlci1yYWRpdXM6OTk5cHg7YmFja2dyb3VuZDp2YXIo"
    "LS1wYXBlcik7Y29sb3I6dmFyKC0taW5rKTtvdXRsaW5lOm5vbmV9Ci5maWx0ZXJzIGlucHV0e2ZsZXg6MTttaW4td2lkdGg6"
    "MjAwcHh9Ci5maWx0ZXJzIGlucHV0OmZvY3VzLC5maWx0ZXJzIHNlbGVjdDpmb2N1c3tib3JkZXItY29sb3I6dmFyKC0tYWNj"
    "ZW50KX0KLmZyZXNoe2ZvbnQtc2l6ZToxMi41cHg7Y29sb3I6dmFyKC0tZmFpbnQpO3doaXRlLXNwYWNlOm5vd3JhcH0KLmZy"
    "ZXNoIGJ7Y29sb3I6dmFyKC0taW5rKTtmb250LXdlaWdodDo2MDB9Ci5mcmVzaC5rb3tjb2xvcjojOEE0QjMyfQoucm93c3tk"
    "aXNwbGF5OmJsb2NrfQoucm93e2Rpc3BsYXk6Z3JpZDtncmlkLXRlbXBsYXRlLWNvbHVtbnM6MTA0cHggMWZyIDEyNHB4IDEy"
    "NHB4IDU4cHggMTAwcHggMTE2cHg7Z2FwOjE0cHg7YWxpZ24taXRlbXM6Y2VudGVyO3BhZGRpbmc6MTRweCAyMHB4O2JvcmRl"
    "ci1ib3R0b206MXB4IHNvbGlkIHZhcigtLWxpbmUpO2ZvbnQtc2l6ZToxNHB4fQoucm93Omxhc3QtY2hpbGR7Ym9yZGVyLWJv"
    "dHRvbTowfQoucm93LmhpZGRlbntkaXNwbGF5Om5vbmV9Ci5yaGVhZHtmb250LXNpemU6MTEuNXB4O2xldHRlci1zcGFjaW5n"
    "Oi4xZW07dGV4dC10cmFuc2Zvcm06dXBwZXJjYXNlO2NvbG9yOnZhcigtLWZhaW50KTtiYWNrZ3JvdW5kOiNGMkVGRTB9Ci5y"
    "aGVhZCAubnVte3RleHQtYWxpZ246cmlnaHR9Ci5kYXRlIGJ7ZGlzcGxheTpibG9jaztmb250LXdlaWdodDo2MDB9Ci5kYXRl"
    "IHNwYW57Zm9udC1zaXplOjEyLjVweDtjb2xvcjp2YXIoLS1mYWludCl9Ci5sZWcgYntmb250LXdlaWdodDo2MDB9Ci5sZWcg"
    "LnRhZ3tkaXNwbGF5OmlubGluZS1ibG9jazttYXJnaW4tdG9wOjVweH0KLmxlZyAubnR7ZGlzcGxheTpibG9jaztmb250LXNp"
    "emU6MTIuNXB4O2NvbG9yOnZhcigtLWZhaW50KTttYXJnaW4tdG9wOjRweH0KLm9wIGF7Y29sb3I6aW5oZXJpdDt0ZXh0LWRl"
    "Y29yYXRpb246bm9uZTtib3JkZXItYm90dG9tOjFweCBkb3R0ZWQgdmFyKC0tbGluZSl9Ci5vcCBhOmhvdmVye2NvbG9yOnZh"
    "cigtLWFjY2VudCl9Ci5vcCBzcGFue2Rpc3BsYXk6YmxvY2s7Zm9udC1zaXplOjEyLjVweDtjb2xvcjp2YXIoLS1mYWludCk7"
    "bWFyZ2luLXRvcDoycHh9Ci5udW17dGV4dC1hbGlnbjpyaWdodDtmb250LXZhcmlhbnQtbnVtZXJpYzp0YWJ1bGFyLW51bXN9"
    "Ci50YWd7ZGlzcGxheTppbmxpbmUtYmxvY2s7Zm9udC1zaXplOjExcHg7bGV0dGVyLXNwYWNpbmc6LjA4ZW07dGV4dC10cmFu"
    "c2Zvcm06dXBwZXJjYXNlO2NvbG9yOnZhcigtLWFjY2VudCk7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtib3JkZXIt"
    "cmFkaXVzOjk5OXB4O3BhZGRpbmc6M3B4IDlweDtiYWNrZ3JvdW5kOnZhcigtLXBhcGVyKX0KLmFza3tjb2xvcjp2YXIoLS1m"
    "YWludCk7Zm9udC1zdHlsZTppdGFsaWN9Ci5nb3tkaXNwbGF5OmlubGluZS1mbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6"
    "NnB4O2ZvbnQtc2l6ZToxM3B4O2ZvbnQtd2VpZ2h0OjYwMDtjb2xvcjp2YXIoLS1pbmspO2JvcmRlcjoxcHggc29saWQgdmFy"
    "KC0tbGluZSk7Ym9yZGVyLXJhZGl1czo5OTlweDtwYWRkaW5nOjhweCAxNHB4O3RleHQtZGVjb3JhdGlvbjpub25lO2JhY2tn"
    "cm91bmQ6dmFyKC0tcGFwZXIpO3doaXRlLXNwYWNlOm5vd3JhcH0KLmdvOmhvdmVye2JvcmRlci1jb2xvcjp2YXIoLS1hY2Nl"
    "bnQpO2NvbG9yOnZhcigtLWFjY2VudCl9Ci5zdGF0ZXtwYWRkaW5nOjM0cHggMjBweDt0ZXh0LWFsaWduOmNlbnRlcjtmb250"
    "LXNpemU6MTRweDtjb2xvcjp2YXIoLS1tdXRlZCk7bGluZS1oZWlnaHQ6MS42fQouc3RhdGUgYXtjb2xvcjp2YXIoLS1hY2Nl"
    "bnQpfQouc2VjdHttYXJnaW46NDRweCAwIDA7cGFkZGluZy10b3A6MzBweDtib3JkZXItdG9wOjFweCBzb2xpZCB2YXIoLS1s"
    "aW5lKX0KLmt7Zm9udC1zaXplOjExLjVweDtsZXR0ZXItc3BhY2luZzouMTZlbTt0ZXh0LXRyYW5zZm9ybTp1cHBlcmNhc2U7"
    "Y29sb3I6dmFyKC0tZmFpbnQpO21hcmdpbi1ib3R0b206MTJweH0KaDIuZGlzcHtmb250LXNpemU6MzBweDtsaW5lLWhlaWdo"
    "dDoxLjF9Ci5zZWN0IHAubGVhZHtmb250LXNpemU6MTQuNXB4O2NvbG9yOnZhcigtLW11dGVkKTttYXJnaW4tdG9wOjEycHg7"
    "bWF4LXdpZHRoOjY2MHB4O2xpbmUtaGVpZ2h0OjEuNn0KLm9wc3tsaXN0LXN0eWxlOm5vbmU7ZGlzcGxheTpncmlkO2dyaWQt"
    "dGVtcGxhdGUtY29sdW1uczpyZXBlYXQoYXV0by1maWxsLG1pbm1heCgyMzBweCwxZnIpKTtnYXA6MCAyNnB4O21hcmdpbi10"
    "b3A6MThweH0KLm9wcyBsaXtib3JkZXItYm90dG9tOjFweCBzb2xpZCB2YXIoLS1saW5lKTtwYWRkaW5nOjExcHggMH0KLm9w"
    "cyBhe2NvbG9yOmluaGVyaXQ7dGV4dC1kZWNvcmF0aW9uOm5vbmU7Zm9udC1zaXplOjE0LjVweDtkaXNwbGF5OmJsb2NrfQou"
    "b3BzIGE6aG92ZXJ7Y29sb3I6dmFyKC0tYWNjZW50KX0KLm9wcyBzbWFsbHtkaXNwbGF5OmJsb2NrO2ZvbnQtc2l6ZToxMi41"
    "cHg7Y29sb3I6dmFyKC0tZmFpbnQpO21hcmdpbi10b3A6MnB4fQoucXN7bWFyZ2luLXRvcDoxOHB4O2Rpc3BsYXk6Z3JpZDtn"
    "YXA6MTRweH0KLnFxe2JhY2tncm91bmQ6dmFyKC0tY2FyZCk7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtib3JkZXIt"
    "cmFkaXVzOjE0cHg7cGFkZGluZzoxNnB4IDE4cHg7Zm9udC1zaXplOjE0LjVweDtsaW5lLWhlaWdodDoxLjU1fQouZ2Fwe21h"
    "cmdpbjo0NHB4IDAgMDtiYWNrZ3JvdW5kOnZhcigtLWNhcmQpO2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVy"
    "LXJhZGl1czoxOHB4O3BhZGRpbmc6MjhweH0KLmdhcCBwLmJpZ3tmb250LXNpemU6MTlweDtsaW5lLWhlaWdodDoxLjM1fQou"
    "Z2FwIHAuYmlnIGVte2ZvbnQtc3R5bGU6aXRhbGljO2NvbG9yOnZhcigtLWFjY2VudCl9Ci5nYXAgcC5zbWFsbHtmb250LXNp"
    "emU6MTMuNXB4O2NvbG9yOnZhcigtLW11dGVkKTttYXJnaW4tdG9wOjEycHg7bGluZS1oZWlnaHQ6MS42O21heC13aWR0aDo2"
    "ODBweH0KLmJ0bnN7ZGlzcGxheTpmbGV4O2dhcDoxMHB4O2ZsZXgtd3JhcDp3cmFwO21hcmdpbi10b3A6MjBweH0KLmJ0bntm"
    "b250LXNpemU6MTRweDtmb250LXdlaWdodDo2MDA7cGFkZGluZzoxMnB4IDIycHg7Ym9yZGVyLXJhZGl1czo5OTlweDt0ZXh0"
    "LWRlY29yYXRpb246bm9uZTtkaXNwbGF5OmlubGluZS1ibG9ja30KLmJ0bi1pbnZ7YmFja2dyb3VuZDp2YXIoLS1pbmspO2Nv"
    "bG9yOnZhcigtLXBhcGVyKX0KLmJ0bi1saW5le2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Y29sb3I6dmFyKC0taW5r"
    "KX0KLmZvb3R7Ym9yZGVyLXRvcDoxcHggc29saWQgdmFyKC0tbGluZSk7bWFyZ2luLXRvcDo0OHB4O3BhZGRpbmc6MjJweCAw"
    "IDQwcHg7Zm9udC1zaXplOjEycHg7Y29sb3I6dmFyKC0tZmFpbnQpO2Rpc3BsYXk6ZmxleDtqdXN0aWZ5LWNvbnRlbnQ6c3Bh"
    "Y2UtYmV0d2VlbjtmbGV4LXdyYXA6d3JhcDtnYXA6OHB4fQouZm9vdCBhe2NvbG9yOnZhcigtLW11dGVkKTt0ZXh0LWRlY29y"
    "YXRpb246bm9uZX0KLm5vdGV7bWFyZ2luLXRvcDoyNnB4O2ZvbnQtc2l6ZToxMnB4O2NvbG9yOnZhcigtLWZhaW50KTtsaW5l"
    "LWhlaWdodDoxLjV9CkBtZWRpYShtYXgtd2lkdGg6ODYwcHgpewoud3JhcHtwYWRkaW5nOjAgMjBweH0KaDEuZGlzcHtmb250"
    "LXNpemU6MzRweH0KLnJvd3tncmlkLXRlbXBsYXRlLWNvbHVtbnM6MWZyIDFmcjtnYXA6OHB4IDE0cHg7cGFkZGluZzoxNnB4"
    "IDE2cHh9Ci5yaGVhZHtkaXNwbGF5Om5vbmV9Ci5yb3c+KnttaW4td2lkdGg6MH0KLnJvdyAubGVne2dyaWQtY29sdW1uOjEv"
    "MztvcmRlcjoxfQoucm93IC5kYXRle29yZGVyOjJ9Ci5yb3cgLm9we29yZGVyOjN9Ci5yb3cgLmFwe29yZGVyOjR9Ci5yb3cg"
    "LnBse29yZGVyOjU7dGV4dC1hbGlnbjpsZWZ0fQoucm93IC5wcntvcmRlcjo2O3RleHQtYWxpZ246bGVmdH0KLnJvdyAuYWN7"
    "Z3JpZC1jb2x1bW46MS8zO29yZGVyOjc7bWFyZ2luLXRvcDo2cHh9Ci5udW17dGV4dC1hbGlnbjpsZWZ0fQp9Cjwvc3R5bGU+"
    "CjwvaGVhZD4KPGJvZHk+CjxkaXYgY2xhc3M9IndyYXAiPgoKICA8ZGl2IGNsYXNzPSJ0b3AiPgogICAgPGEgY2xhc3M9Im1h"
    "cmsiIGhyZWY9Ii8iPjxpPmV4aXQ8L2k+PGI+LmNsdWI8L2I+PC9hPgogICAgPGRpdiBjbGFzcz0idG9wbmF2Ij4KICAgICAg"
    "PGEgaHJlZj0iL2Vjb3N5c3RlbWUiPkwmI3gyNzvDiWNvc3lzdMOobWU8L2E+CiAgICAgIDxhIGNsYXNzPSJidG4tcCIgaHJl"
    "Zj0iaHR0cHM6Ly90YWxseS5zby9yL3dBRE5aTiIgdGFyZ2V0PSJfYmxhbmsiIHJlbD0ibm9vcGVuZXIiPlJlam9pbmRyZTwv"
    "YT4KICAgIDwvZGl2PgogIDwvZGl2PgoKICA8ZGl2IGNsYXNzPSJjcnVtYiI+PGEgaHJlZj0iL2Vjb3N5c3RlbWUiPkwmI3gy"
    "NzvDiWNvc3lzdMOobWUgZGUgbCYjeDI3O0V4aXQ8L2E+IMK3IDxhIGhyZWY9Ii9lY29zeXN0ZW1lI2pldHMiPkF2aWF0aW9u"
    "IGQmI3gyNzthZmZhaXJlczwvYT48L2Rpdj4KCiAgPHNlY3Rpb24gY2xhc3M9Imhlcm8iPgogICAgPHAgY2xhc3M9Im92ZXIi"
    "PkF2aWF0aW9uIGQmI3gyNzthZmZhaXJlczwvcD4KICAgIDxoMSBjbGFzcz0iZGlzcCI+TGVzIGRpc3BvbmliaWxpdMOpcyBl"
    "biBkaXJlY3QuPC9oMT4KICAgIDxwIGNsYXNzPSJsZWRlIj5QbHVzaWV1cnMgb3DDqXJhdGV1cnMsIHVuZSBzZXVsZSBwYWdl"
    "LiBMZXMgcGxhY2VzIGVuY29yZSBvdXZlcnRlcyBzdXIgbGVzIHZvbHMgZMOpasOgIHByb2dyYW1tw6lzLCBsZXMgdm9scyDD"
    "oCBsYSBkZW1hbmRlIGV0IGxlcyBwYXJ0cyBkaXNwb25pYmxlcywgYXZlYyBsZSBkw6lwYXJ0LCBsJiN4Mjc7YXJyaXbDqWUs"
    "IGwmI3gyNzthcHBhcmVpbCBldCBsZSBwcml4IHF1YW5kIGxhIG1haXNvbiBsJiN4Mjc7YWZmaWNoZS48L3A+CiAgPC9zZWN0"
    "aW9uPgoKICA8ZGl2IGNsYXNzPSJib2FyZCI+CiAgICA8ZGl2IGNsYXNzPSJiaGVhZCI+CiAgICAgIDxkaXYgY2xhc3M9ImZp"
    "bHRlcnMiPgogICAgICAgIDxpbnB1dCBpZD0icSIgdHlwZT0ic2VhcmNoIiBwbGFjZWhvbGRlcj0iRMOpcGFydCwgYXJyaXbD"
    "qWUsIG9ww6lyYXRldXIsIGFwcGFyZWls4oCmIiBhdXRvY29tcGxldGU9Im9mZiI+CiAgICAgICAgPHNlbGVjdCBpZD0idHlw"
    "ZSI+CiAgICAgICAgICA8b3B0aW9uIHZhbHVlPSIiPlRvdXMgbGVzIHR5cGVzPC9vcHRpb24+CiAgICAgICAgICA8b3B0aW9u"
    "IHZhbHVlPSJFbXB0eSBsZWciPkVtcHR5IGxlZzwvb3B0aW9uPgogICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iVm9sIMOgIGxh"
    "IGRlbWFuZGUiPlZvbCDDoCBsYSBkZW1hbmRlPC9vcHRpb24+CiAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJQYXJ0IGZyYWN0"
    "aW9ubsOpZSI+UGFydCBmcmFjdGlvbm7DqWU8L29wdGlvbj4KICAgICAgICA8L3NlbGVjdD4KICAgICAgPC9kaXY+CiAgICAg"
    "IDxkaXYgY2xhc3M9ImZyZXNoIiBpZD0iZnJlc2giPkNoYXJnZW1lbnQgZGVzIGRpc3BvbmliaWxpdMOpc+KApjwvZGl2Pgog"
    "ICAgPC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJyb3dzIiBpZD0icm93cyI+CiAgICAgIDxkaXYgY2xhc3M9InJvdyByaGVhZCI+"
    "CiAgICAgICAgPGRpdj5Ew6lwYXJ0PC9kaXY+CiAgICAgICAgPGRpdj5UcmFqZXQ8L2Rpdj4KICAgICAgICA8ZGl2Pk9ww6ly"
    "YXRldXI8L2Rpdj4KICAgICAgICA8ZGl2PkFwcGFyZWlsPC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0ibnVtIj5QbGFjZXM8"
    "L2Rpdj4KICAgICAgICA8ZGl2IGNsYXNzPSJudW0iPlByaXg8L2Rpdj4KICAgICAgICA8ZGl2PjwvZGl2PgogICAgICA8L2Rp"
    "dj4KICAgIDwvZGl2PgogICAgPGRpdiBjbGFzcz0ic3RhdGUiIGlkPSJzdGF0ZSI+Q2hhcmdlbWVudCBkZXMgZGlzcG9uaWJp"
    "bGl0w6lz4oCmPC9kaXY+CiAgPC9kaXY+CgogIDxzZWN0aW9uIGNsYXNzPSJzZWN0Ij4KICAgIDxkaXYgY2xhc3M9ImsiPkxl"
    "cyBvcMOpcmF0ZXVycyByw6lmw6lyZW5jw6lzPC9kaXY+CiAgICA8aDIgY2xhc3M9ImRpc3AiPlNlcHQgbWFpc29ucywgdW4g"
    "c3RhbmRhcmQgY29tbXVuLjwvaDI+CiAgICA8cCBjbGFzcz0ibGVhZCI+Q2hhcXVlIG1haXNvbiBlc3QgcsOpZsOpcmVuY8Op"
    "ZSBncmF0dWl0ZW1lbnQgZXQgc29uIHByb2ZpbCBwb3NlIGxlcyBtw6ptZXMgcXVlc3Rpb25zIHF1ZSBsZXMgdHJlaXplIGF1"
    "dHJlcyBjYXTDqWdvcmllcyBkZSBsJiN4Mjc7w4ljb3N5c3TDqG1lLiBMZSByw6lmw6lyZW5jZW1lbnQgbmUgdmF1dCBwYXMg"
    "cmVjb21tYW5kYXRpb24gOiBpbCBzJiN4Mjc7YWdpdCBkJiN4Mjc7dW4gcmVjZW5zZW1lbnQgZHUgbWFyY2jDqS48L3A+CiAg"
    "ICA8dWwgY2xhc3M9Im9wcyIgaWQ9Im9wcyI+PC91bD4KICA8L3NlY3Rpb24+CgogIDxzZWN0aW9uIGNsYXNzPSJzZWN0Ij4K"
    "ICAgIDxkaXYgY2xhc3M9ImsiPkxlcyBxdWVzdGlvbnMgZGVzIGV4aXRlcnM8L2Rpdj4KICAgIDxoMiBjbGFzcz0iZGlzcCI+"
    "Q2UgcXVlIGxlcyBmb25kYXRldXJzIGRlbWFuZGVudCB2cmFpbWVudC48L2gyPgogICAgPHAgY2xhc3M9ImxlYWQiPkNlcyB0"
    "cm9pcyBxdWVzdGlvbnMgc29udCBwb3PDqWVzIMOgIGNoYXF1ZSBtYWlzb24gZGUgbGEgY2F0w6lnb3JpZS4gTGVzIHLDqXBv"
    "bnNlcyBwdWJsacOpZXMgc29udCBjZWxsZXMgZGUgbGEgbWFpc29uLCBtb3QgcG91ciBtb3QuPC9wPgogICAgPGRpdiBjbGFz"
    "cz0icXMiPgogICAgICA8ZGl2IGNsYXNzPSJxcSI+TGUgcHJpeCByw6llbCBkJiN4Mjc7dW4gUGFyaXMtTmljZSBhbGxlci1y"
    "ZXRvdXIgZGFucyBsYSBqb3VybsOpZSwgdG91dCBjb21wcmlzLCBwb3NpdGlvbm5lbWVudCBldCB0ZW1wcyBkJiN4Mjc7YXR0"
    "ZW50ZSBpbmNsdXMuPC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9InFxIj5MJiN4Mjc7YXBwYXJlaWwgcsOpc2VydsOpIG4mI3gy"
    "Nztlc3QgcGFzIGRpc3BvbmlibGUgbGUgbWF0aW4gZHUgZMOpcGFydCA6IGNlIHF1aSBzZSBwYXNzZSwgZXQgcXVpIHBhaWUg"
    "bCYjeDI3O8OpY2FydC48L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0icXEiPlN1ciB1bmUgY2FydGUgZCYjeDI3O2hldXJlcyBv"
    "dSB1bmUgcGFydCBmcmFjdGlvbm7DqWUsIGNlIHF1aSBlc3QgcsOpY3Vww6lyw6kgZW4gY2FzIGQmI3gyNzthcnLDqnQgYXUg"
    "Ym91dCBkJiN4Mjc7dW4gYW4uPC9kaXY+CiAgICA8L2Rpdj4KICA8L3NlY3Rpb24+CgogIDxkaXYgY2xhc3M9ImdhcCI+CiAg"
    "ICA8cCBjbGFzcz0iYmlnIj5Wb3VzIMOqdGVzIG9ww6lyYXRldXIgb3UgY291cnRpZXIgPyA8ZW0+Vm9zIGRpc3BvbmliaWxp"
    "dMOpcyBzJiN4Mjc7YWZmaWNoZW50IGljaS48L2VtPjwvcD4KICAgIDxwIGNsYXNzPSJzbWFsbCI+TGVzIGZvbmRhdGV1cnMg"
    "cXVpIGNvbnN1bHRlbnQgY2V0dGUgcGFnZSB2aWVubmVudCBkZSB2ZW5kcmUgbGV1ciBzb2Npw6l0w6kuIElscyBjaGVyY2hl"
    "bnQgdW4gZMOpcGFydCBkYW5zIGxlcyBqb3VycyBxdWkgdmllbm5lbnQsIGV0IGlscyBjb21wYXJlbnQgYXZhbnQgZCYjeDI3"
    "O8OpY3JpcmUuIEVudm95ZXotbm91cyB2b3MgZGlzcG9uaWJpbGl0w6lzIGV0IGVsbGVzIGFwcGFyYWlzc2VudCBzdXIgY2V0"
    "dGUgcGFnZSwgYXZlYyB1biBsaWVuIGRpcmVjdCB2ZXJzIHZvdHJlIGRldmlzLjwvcD4KICAgIDxkaXYgY2xhc3M9ImJ0bnMi"
    "PgogICAgICA8YSBjbGFzcz0iYnRuIGJ0bi1pbnYiIGhyZWY9Im1haWx0bzpsb3Vpc0BleGl0LmNsdWI/c3ViamVjdD1KZXRz"
    "JTIwJUMyJUI3JTIwcHVibGllciUyMG1lcyUyMGRpc3BvbmliaWxpdCVDMyVBOXMmYW1wO2JvZHk9T3AlQzMlQTlyYXRldXIl"
    "MjAlM0ElMEFUeXBlJTIwKGVtcHR5JTIwbGVnJTIwJTJGJTIwdm9sJTIwJUMzJUEwJTIwbGElMjBkZW1hbmRlJTIwJTJGJTIw"
    "cGFydCUyMGZyYWN0aW9ubiVDMyVBOWUpJTIwJTNBJTBBRCVDMyVBOXBhcnQlMjAlM0ElMEFBcnJpdiVDMyVBOWUlMjAlM0El"
    "MEFEYXRlJTIwZXQlMjBoZXVyZSUyMCUzQSUwQUFwcGFyZWlsJTIwJTNBJTBBUGxhY2VzJTIwJTNBJTBBUHJpeCUyMChvdSUy"
    "MCVDMiVBQiUyMHN1ciUyMGRlbWFuZGUlMjAlQzIlQkIpJTIwJTNBJTBBTGllbiUyMGRlJTIwZGV2aXMlMjAlM0EiPlB1Ymxp"
    "ZXIgbWVzIGRpc3BvbmliaWxpdMOpcyDihpI8L2E+CiAgICAgIDxhIGNsYXNzPSJidG4gYnRuLWxpbmUiIGhyZWY9Ii9yZWZl"
    "cmVuY2VtZW50P2NhdD1qZXRzJmFtcDtkZW1hbmRlPXJlZmVyZW5jZXIiPk1lIGZhaXJlIHLDqWbDqXJlbmNlciwgYyYjeDI3"
    "O2VzdCBncmF0dWl0PC9hPgogICAgICA8YSBjbGFzcz0iYnRuIGJ0bi1saW5lIiBocmVmPSIvZmljaGUtdmVyaWZpZWU/Y2F0"
    "PWpldHMiPkZhaXJlIHbDqXJpZmllciBtb24gcHJvZmlsPC9hPgogICAgPC9kaXY+CiAgPC9kaXY+CgogIDxwIGNsYXNzPSJu"
    "b3RlIj5MZXMgZGlzcG9uaWJpbGl0w6lzIGFmZmljaMOpZXMgc29udCBkw6ljbGFyw6llcyBwYXIgbGVzIG1haXNvbnMgZXQg"
    "cGV1dmVudCBwYXJ0aXIgw6AgdG91dCBtb21lbnQuIEwmI3gyNztFeGl0IENsdWIgbiYjeDI3O2VzdCBuaSB0cmFuc3BvcnRl"
    "dXIgYcOpcmllbiwgbmkgY291cnRpZXIsIG5pIGludGVybcOpZGlhaXJlIMOgIGxhIHLDqXNlcnZhdGlvbiA6IGxhIHJlbGF0"
    "aW9uIGNvbnRyYWN0dWVsbGUsIGxlIHByaXggZXQgbCYjeDI3O2V4w6ljdXRpb24gZHUgdm9sIHJlbMOodmVudCBleGNsdXNp"
    "dmVtZW50IGRlIGxhIG1haXNvbiBjaG9pc2llLjwvcD4KCiAgPGRpdiBjbGFzcz0iZm9vdCI+CiAgICA8ZGl2PkV4aXQgQ2x1"
    "YiDCtyBMJiN4Mjc7w4ljb3N5c3TDqG1lIGRlIGwmI3gyNztFeGl0IMK3IEF2aWF0aW9uIGQmI3gyNzthZmZhaXJlcyDCtyBQ"
    "YXJpczwvZGl2PgogICAgPGRpdj48YSBocmVmPSIvZWNvc3lzdGVtZSI+TCYjeDI3O8OJY29zeXN0w6htZTwvYT4gwrcgPGEg"
    "aHJlZj0iL3JlZmVyZW5jZW1lbnQiPlNlIHLDqWbDqXJlbmNlcjwvYT4gwrcgPGEgaHJlZj0ibWFpbHRvOmxvdWlzQGV4aXQu"
    "Y2x1Yj9zdWJqZWN0PUpldHMlMjAlQzIlQjclMjByZW1hcnF1ZSI+VW4gYnVnLCB1bmUgcmVtYXJxdWUgPyDDiWNyaXZlei1t"
    "b2k8L2E+PC9kaXY+CiAgPC9kaXY+Cgo8L2Rpdj4KCjxzY3JpcHQ+CihmdW5jdGlvbigpewogICd1c2Ugc3RyaWN0JzsKCiAg"
    "LyogTGVzIG1haXNvbnMgcmVmZXJlbmNlZXMuIExlIHRhYmxlYXUgZHUgaGF1dCBlc3QgYWxpbWVudGUgcGFyIGwnQVBJIDsK"
    "ICAgICBjZXR0ZSBsaXN0ZS1jaSBlc3Qgc3RhdGlxdWUgZXQgc2VydCBkZSByZXBsaSBwZXJtYW5lbnQgOiBsYSBwYWdlIGdh"
    "cmRlCiAgICAgdG91am91cnMgdW5lIHZhbGV1ciBtZW1lIHNpIGwnQVBJIHRvbWJlLiAqLwogIHZhciBPUFMgPSBbCiAgICBb"
    "J2ZsZXhqZXQnLCdGbGV4amV0JywnUHJvcHJpw6l0w6kgZnJhY3Rpb25uw6llIGV0IGNhcnRlcyBkJiN4Mjc7aGV1cmVzJ10s"
    "CiAgICBbJ3Zpc3RhamV0JywnVmlzdGFKZXQnLCdBYm9ubmVtZW50IGVuIGhldXJlcyBzdXIgZmxvdHRlIGV4cGxvaXTDqWUg"
    "ZW4gcHJvcHJlJ10sCiAgICBbJ25ldGpldHMnLCdOZXRKZXRzJywnUHJvcHJpw6l0w6kgZnJhY3Rpb25uw6llLCBjYXJ0ZXMg"
    "ZCYjeDI3O2hldXJlcywgbG9jYXRpb24nXSwKICAgIFsnbHVuYWpldHMnLCdMdW5hSmV0cycsJ0NvdXJ0aWVyLCBtaXNlIGVu"
    "IGNvbmN1cnJlbmNlIGRlcyBvcMOpcmF0ZXVycyddLAogICAgWydnbG9iZWFpcicsJ0dsb2JlQWlyJywnQ291cnQtY291cnJp"
    "ZXIgZXVyb3DDqWVuLCB0YXJpZnMgcHVibGnDqXMnXSwKICAgIFsnZmx5dmljdG9yJywnRmx5IFZpY3RvcicsJ1BsYWNlIGRl"
    "IG1hcmNow6ksIGRldmlzIGRlIHBsdXNpZXVycyBvcMOpcmF0ZXVycyddLAogICAgWydhc3RvbmpldCcsJ0FzdG9uamV0Jywn"
    "TG9jYXRpb24sIGdlc3Rpb24gZXQgdmVudGUgZCYjeDI3O2FwcGFyZWlscyddCiAgXTsKCiAgdmFyIEFQSSA9ICdodHRwczov"
    "L2V4aXQtY2x1Yi1hcHAudmVyY2VsLmFwcC9hcGkvZGlzcG9zP3ZlcnRpY2FsZT1KZXRzJzsKICB2YXIgTU9JUyA9IFsnJywn"
    "amFudi4nLCdmw6l2ci4nLCdtYXJzJywnYXZyLicsJ21haScsJ2p1aW4nLCdqdWlsLicsJ2Fvw7t0Jywnc2VwdC4nLCdvY3Qu"
    "Jywnbm92LicsJ2TDqWMuJ107CgogIHZhciBlbFJvd3MgPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgncm93cycpOwogIHZh"
    "ciBlbFN0YXRlID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ3N0YXRlJyk7CiAgdmFyIGVsRnJlc2ggPSBkb2N1bWVudC5n"
    "ZXRFbGVtZW50QnlJZCgnZnJlc2gnKTsKICB2YXIgZWxRID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ3EnKTsKICB2YXIg"
    "ZWxUeXBlID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ3R5cGUnKTsKICB2YXIgZWxPcHMgPSBkb2N1bWVudC5nZXRFbGVt"
    "ZW50QnlJZCgnb3BzJyk7CgogIGZ1bmN0aW9uIGVzYyhzKXsgdmFyIGQgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdkaXYn"
    "KTsgZC50ZXh0Q29udGVudCA9IHMgPT0gbnVsbCA/ICcnIDogU3RyaW5nKHMpOyByZXR1cm4gZC5pbm5lckhUTUw7IH0KCiAg"
    "ZnVuY3Rpb24gbm9ybShzKXsKICAgIHJldHVybiBTdHJpbmcocyB8fCAnJykubm9ybWFsaXplKCdORkQnKS5yZXBsYWNlKC9b"
    "zIAtza9dL2csJycpCiAgICAgIC50b0xvd2VyQ2FzZSgpLnJlcGxhY2UoL1teYS16MC05XS9nLCcnKTsKICB9CgogIC8qIEwn"
    "aGV1cmUgZXN0IGx1ZSB0ZWxsZSBxdSdlbGxlIGVzdCBkZWNsYXJlZSBkYW5zIGxhIGNoYWluZSBJU08sIHNhbnMKICAgICBw"
    "YXNzZXIgcGFyIERhdGUgOiB1biBkZXBhcnQgYW5ub25jZSBhIDloMzAgbG9jYWxlIHJlc3RlIDloMzAsIHF1ZWwgcXVlCiAg"
    "ICAgc29pdCBsZSBmdXNlYXUgZHUgdmlzaXRldXIuICovCiAgZnVuY3Rpb24gam91cihpc28pewogICAgdmFyIG0gPSBTdHJp"
    "bmcoaXNvIHx8ICcnKS5tYXRjaCgvXihcZHs0fSktKFxkezJ9KS0oXGR7Mn0pKD86VChcZHsyfSk6KFxkezJ9KSk/Lyk7CiAg"
    "ICBpZiAoIW0pIHJldHVybiB7IGo6JycsIGg6JycgfTsKICAgIHZhciBqID0gU3RyaW5nKE51bWJlcihtWzNdKSkgKyAnICcg"
    "KyBNT0lTW051bWJlcihtWzJdKV07CiAgICB2YXIgaCA9IG1bNF0gPyAobVs0XSArICdoJyArIG1bNV0pIDogJ2hvcmFpcmUg"
    "w6AgY29uZmlybWVyJzsKICAgIHJldHVybiB7IGo6aiwgaDpoIH07CiAgfQoKICBmdW5jdGlvbiBldXJvcyhuKXsKICAgIHJl"
    "dHVybiBTdHJpbmcoTWF0aC5yb3VuZChuKSkucmVwbGFjZSgvXEIoPz0oXGR7M30pKyg/IVxkKSkvZywgJ+KArycpICsgJyDi"
    "gqwnOwogIH0KCiAgLyogTGVzIG9wZXJhdGV1cnMgOiByZW5kdSBpbW1lZGlhdCwgc2FucyBkZXBlbmRyZSBkdSByZXNlYXUu"
    "ICovCiAgZWxPcHMuaW5uZXJIVE1MID0gT1BTLm1hcChmdW5jdGlvbihvKXsKICAgIHJldHVybiAnPGxpPjxhIGhyZWY9Ii9m"
    "Lycrb1swXSsnIj4nK29bMV0rJzxzbWFsbD4nK29bMl0rJzwvc21hbGw+PC9hPjwvbGk+JzsKICB9KS5qb2luKCcnKTsKCiAg"
    "dmFyIGxpZ25lcyA9IFtdOwoKICBmdW5jdGlvbiBsaWduZShkKXsKICAgIHZhciB0ID0gam91cihkLmRhdGUpOwogICAgdmFy"
    "IG9wID0gZC5zbHVnCiAgICAgID8gJzxhIGhyZWY9Ii9mLycrZXNjKGQuc2x1ZykrJyI+Jytlc2MoZC5vcGVyYXRldXIpKyc8"
    "L2E+JwogICAgICA6IGVzYyhkLm9wZXJhdGV1cik7CiAgICB2YXIgcHJpeCA9IChkLnByaXggIT0gbnVsbCkKICAgICAgPyBl"
    "dXJvcyhkLnByaXgpCiAgICAgIDogJzxzcGFuIGNsYXNzPSJhc2siPnN1ciBkZW1hbmRlPC9zcGFuPic7CiAgICB2YXIgbGll"
    "biA9IGQubGllbgogICAgICA/ICc8YSBjbGFzcz0iZ28iIGhyZWY9IicrZXNjKGQubGllbikrJyIgdGFyZ2V0PSJfYmxhbmsi"
    "IHJlbD0ibm9vcGVuZXIgbm9mb2xsb3ciPkRlbWFuZGVyIOKGkjwvYT4nCiAgICAgIDogJzxhIGNsYXNzPSJnbyIgaHJlZj0i"
    "bWFpbHRvOmxvdWlzQGV4aXQuY2x1Yj9zdWJqZWN0PScrZW5jb2RlVVJJQ29tcG9uZW50KCdKZXRzIMK3ICcgKyAoZC5yZWYg"
    "fHwgKGQuZGVwYXJ0ICsgJyDihpIgJyArIGQuYXJyaXZlZSkpKSsnIj5EZW1hbmRlciDihpI8L2E+JzsKICAgIHJldHVybiAn"
    "PGRpdiBjbGFzcz0icm93Ij4nCiAgICAgICsgJzxkaXYgY2xhc3M9ImRhdGUiPjxiPicrZXNjKHQuaikrJzwvYj48c3Bhbj4n"
    "K2VzYyh0LmgpKyc8L3NwYW4+PC9kaXY+JwogICAgICArICc8ZGl2IGNsYXNzPSJsZWciPjxiPicrZXNjKGQuZGVwYXJ0IHx8"
    "ICcnKSsnIOKGkiAnK2VzYyhkLmFycml2ZWUgfHwgJycpKyc8L2I+JwogICAgICArICAgKGQudHlwZSA/ICc8c3BhbiBjbGFz"
    "cz0idGFnIj4nK2VzYyhkLnR5cGUpKyc8L3NwYW4+JyA6ICcnKQogICAgICArICAgKGQubm90ZXMgPyAnPHNwYW4gY2xhc3M9"
    "Im50Ij4nK2VzYyhkLm5vdGVzKSsnPC9zcGFuPicgOiAnJykKICAgICAgKyAgICc8L2Rpdj4nCiAgICAgICsgJzxkaXYgY2xh"
    "c3M9Im9wIj4nK29wKyc8L2Rpdj4nCiAgICAgICsgJzxkaXYgY2xhc3M9ImFwIj4nK2VzYyhkLmFwcGFyZWlsIHx8ICcnKSsn"
    "PC9kaXY+JwogICAgICArICc8ZGl2IGNsYXNzPSJudW0gcGwiPicrKGQucGxhY2VzICE9IG51bGwgPyBlc2MoZC5wbGFjZXMp"
    "IDogJzxzcGFuIGNsYXNzPSJhc2siPm4uYy48L3NwYW4+JykrJzwvZGl2PicKICAgICAgKyAnPGRpdiBjbGFzcz0ibnVtIHBy"
    "Ij4nK3ByaXgrJzwvZGl2PicKICAgICAgKyAnPGRpdiBjbGFzcz0iYWMiPicrbGllbisnPC9kaXY+JwogICAgICArICc8L2Rp"
    "dj4nOwogIH0KCiAgZnVuY3Rpb24gZmlsdHJlKCl7CiAgICB2YXIgdiA9IG5vcm0oZWxRLnZhbHVlLnRyaW0oKSk7CiAgICB2"
    "YXIgdCA9IGVsVHlwZS52YWx1ZTsKICAgIHZhciB2dXMgPSAwOwogICAgbGlnbmVzLmZvckVhY2goZnVuY3Rpb24obyl7CiAg"
    "ICAgIHZhciBvayA9ICghdiB8fCBvLm4uaW5kZXhPZih2KSA+IC0xKSAmJiAoIXQgfHwgby5kLnR5cGUgPT09IHQpOwogICAg"
    "ICBvLmVsLmNsYXNzTGlzdC50b2dnbGUoJ2hpZGRlbicsICFvayk7CiAgICAgIGlmIChvaykgdnVzKys7CiAgICB9KTsKICAg"
    "IGlmICghbGlnbmVzLmxlbmd0aCkgcmV0dXJuOwogICAgZWxTdGF0ZS5zdHlsZS5kaXNwbGF5ID0gdnVzID8gJ25vbmUnIDog"
    "J2Jsb2NrJzsKICAgIGlmICghdnVzKSBlbFN0YXRlLnRleHRDb250ZW50ID0gJ0F1Y3VuZSBkaXNwb25pYmlsaXTDqSBuZSBj"
    "b3JyZXNwb25kIMOgIGNldHRlIHJlY2hlcmNoZS4nOwogIH0KCiAgZnVuY3Rpb24gdmlkZShtc2csIGtvKXsKICAgIGVsU3Rh"
    "dGUuc3R5bGUuZGlzcGxheSA9ICdibG9jayc7CiAgICBlbFN0YXRlLmlubmVySFRNTCA9IG1zZzsKICAgIGVsRnJlc2gudGV4"
    "dENvbnRlbnQgPSBrbyA/ICdUYWJsZWF1IG1vbWVudGFuw6ltZW50IGluZGlzcG9uaWJsZScgOiAnQXVjdW5lIGRpc3Bvbmli"
    "aWxpdMOpIHB1Ymxpw6llJzsKICAgIGlmIChrbykgZWxGcmVzaC5jbGFzc05hbWUgPSAnZnJlc2gga28nOwogIH0KCiAgZmV0"
    "Y2goQVBJLCB7IGNhY2hlOiAnbm8tc3RvcmUnIH0pCiAgICAudGhlbihmdW5jdGlvbihyKXsgaWYgKCFyLm9rKSB0aHJvdyBu"
    "ZXcgRXJyb3Ioci5zdGF0dXMpOyByZXR1cm4gci5qc29uKCk7IH0pCiAgICAudGhlbihmdW5jdGlvbihkYXRhKXsKICAgICAg"
    "dmFyIGQgPSAoZGF0YSAmJiBkYXRhLmRpc3BvcykgfHwgW107CiAgICAgIGlmICghZC5sZW5ndGgpIHsKICAgICAgICB2aWRl"
    "KCdBdWN1bmUgZGlzcG9uaWJpbGl0w6kgcHVibGnDqWUgcG91ciBs4oCZaW5zdGFudC4gTGVzIHNlcHQgbWFpc29ucyByw6lm"
    "w6lyZW5jw6llcyBjaS1kZXNzb3VzIHLDqXBvbmRlbnQgYXV4IGRlbWFuZGVzIGF1IGNhcyBwYXIgY2FzLCBldCBjZXR0ZSBw"
    "YWdlIHNlIHJlbXBsaXQgZMOocyBxdeKAmXVuZSBwbGFjZSBz4oCZb3V2cmUuJywgZmFsc2UpOwogICAgICAgIHJldHVybjsK"
    "ICAgICAgfQogICAgICBlbFJvd3MuaW5zZXJ0QWRqYWNlbnRIVE1MKCdiZWZvcmVlbmQnLCBkLm1hcChsaWduZSkuam9pbign"
    "JykpOwogICAgICB2YXIgZWxzID0gZWxSb3dzLnF1ZXJ5U2VsZWN0b3JBbGwoJy5yb3c6bm90KC5yaGVhZCknKTsKICAgICAg"
    "bGlnbmVzID0gZC5tYXAoZnVuY3Rpb24obywgaSl7CiAgICAgICAgcmV0dXJuIHsgZDpvLCBlbDplbHNbaV0sIG46bm9ybShb"
    "by5kZXBhcnQsby5hcnJpdmVlLG8ub3BlcmF0ZXVyLG8uYXBwYXJlaWwsby50eXBlLG8ucmVmXS5qb2luKCcgJykpIH07CiAg"
    "ICAgIH0pOwogICAgICBlbFN0YXRlLnN0eWxlLmRpc3BsYXkgPSAnbm9uZSc7CiAgICAgIGVsRnJlc2guaW5uZXJIVE1MID0g"
    "JzxiPicgKyBkLmxlbmd0aCArICc8L2I+ICcgKyAoZC5sZW5ndGggPiAxID8gJ2Rpc3BvbmliaWxpdMOpcycgOiAnZGlzcG9u"
    "aWJpbGl0w6knKTsKICAgICAgZWxRLmFkZEV2ZW50TGlzdGVuZXIoJ2lucHV0JywgZmlsdHJlKTsKICAgICAgZWxUeXBlLmFk"
    "ZEV2ZW50TGlzdGVuZXIoJ2NoYW5nZScsIGZpbHRyZSk7CiAgICB9KQogICAgLmNhdGNoKGZ1bmN0aW9uKCl7CiAgICAgIHZp"
    "ZGUoJ0xlcyBkaXNwb25pYmlsaXTDqXMgbmUgc2UgY2hhcmdlbnQgcGFzIHBvdXIgbGUgbW9tZW50LiBMZXMgc2VwdCBtYWlz"
    "b25zIHLDqWbDqXJlbmPDqWVzIGNpLWRlc3NvdXMgcmVzdGVudCBqb2lnbmFibGVzLCBldCA8YSBocmVmPSJtYWlsdG86bG91"
    "aXNAZXhpdC5jbHViP3N1YmplY3Q9SmV0cyUyMCVDMiVCNyUyMHVuZSUyMGRlbWFuZGUiPnVuZSBkZW1hbmRlIG5vdXMgYXJy"
    "aXZlIGRpcmVjdGVtZW50PC9hPi4nLCB0cnVlKTsKICAgIH0pOwp9KSgpOwo8L3NjcmlwdD4KPC9ib2R5Pgo8L2h0bWw+Cg=="
)
JETS = base64.b64decode(JETS_B64).decode("utf-8")

if os.path.exists("jets.html"):
    print("ECHEC jets.html existe deja")
    sys.exit(1)
io.open("jets.html", "w", encoding="utf-8").write(JETS)
j = io.open("jets.html", encoding="utf-8").read()
for balise, att in (
    ("<!DOCTYPE html>", 1),
    ('<link rel="canonical" href="https://www.exit.club/jets">', 1),
    ("exit-club-app.vercel.app/api/dispos?verticale=Jets", 1),
    ('id="rows"', 1),
    ('id="state"', 1),
    ('id="fresh"', 1),
    ("var OPS = [", 1),
    ("</html>", 1),
):
    if j.count(balise) != att:
        err.append("jets.html : %d occurrence(s) de %s au lieu de %d"
                   % (j.count(balise), balise[:44], att))
if len(j) < 15000:
    err.append("jets.html trop court : %d octets" % len(j))
if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)
print("ok jets.html cree (%d octets)" % len(j))

# ================================================== 2. le gabarit de fiche jets
T = io.open("f/spiko.html", encoding="utf-8").read()


def cut(t, a, b, neuf, nom):
    i = t.find(a)
    jj = t.find(b, i + 1)
    if i < 0 or jj < 0:
        err.append("ancre absente : " + nom)
        return t
    return t[:i] + neuf + t[jj + len(b):]


TOC = """<nav class="toc">
    <a href="#etiquette">Prix et facturation</a>
    <a href="#grille">Les tarifs</a>
    <a href="#questions">Les questions des exiters</a>
    <a href="#chiffre">Le chiffre assume</a>
    <a href="#interview">L&#x27;interview sans filtre</a>
  </nav>"""
TOC = TOC.replace("Le chiffre assume", "Le chiffre assum\u00e9")

REPERES = ('<div class="card"><div class="k">Rep\u00e8res</div>@@REPERES@@'
           '<p style="margin-top:10px">\u00c9l\u00e9ments indicatifs, '
           '\u00e0 confirmer par la maison : le prix \u00e0 l&#x27;heure tout '
           'compris, l&#x27;exploitant de l&#x27;appareil, les statuts et le '
           'sort des sommes avanc\u00e9es rel\u00e8vent des blocs ci-dessous.'
           '</p>@@LIENS@@</div>')

BLOCS = """
  <section class="sect" id="etiquette">
    <div class="k">Bloc 1 &middot; Prix et facturation</div>
    <h2>Prix et facturation.</h2>
    <p class="lead">Les chiffres sont ceux d&eacute;clar&eacute;s par la maison.</p>
    <div class="card" style="margin-top:16px">
      <div class="etq"><div class="q">Qui op&egrave;re l&#x27;appareil<small>Certificat de transporteur a&eacute;rien, pays d&#x27;immatriculation, et nom de l&#x27;exploitant quand ce n&#x27;est pas la maison elle-m&ecirc;me.</small></div><span class="chip-attente">Interview sans filtre &agrave; venir</span></div>
      <div class="etq"><div class="q">Ce que contient le prix &agrave; l&#x27;heure<small>Heure de vol, carburant, redevances, taxes, restauration, positionnement, temps d&#x27;attente : ce qui est dedans et ce qui s&#x27;ajoute.</small></div><span class="chip-attente">Interview sans filtre &agrave; venir</span></div>
      <div class="etq"><div class="q">O&ugrave; dorment les sommes avanc&eacute;es<small>Cartes d&#x27;heures, parts fractionn&eacute;es, d&eacute;p&ocirc;ts : o&ugrave; l&#x27;argent du client est log&eacute;, et ce qui se passe en cas de d&eacute;faut.</small></div><span class="chip-attente">Interview sans filtre &agrave; venir</span></div>
    </div>
  </section>

  <section class="sect" id="grille">
    <div class="k">Bloc 2 &middot; La grille</div>
    <h2>Les tarifs.</h2>
    <p class="lead">Communiqu&eacute;e par la maison en fourchettes, publi&eacute;e apr&egrave;s sa validation, remise &agrave; jour chaque ann&eacute;e.</p>
    <div class="card" style="margin-top:16px">
      <div style="overflow-x:auto"><table class="grille" style="min-width:560px">
        <tr><th>Segment</th><th>Prix &agrave; l&#x27;heure</th><th>Positionnement</th><th>D&eacute;lai de mise &agrave; disposition</th></tr>
        <tr><td class="deal">L&eacute;ger, 4 &agrave; 6 places</td><td class="pend">interview sans filtre &agrave; venir</td><td class="pend">interview sans filtre &agrave; venir</td><td class="pend">interview sans filtre &agrave; venir</td></tr>
        <tr><td class="deal">Midsize, 7 &agrave; 9 places</td><td class="pend">interview sans filtre &agrave; venir</td><td class="pend">interview sans filtre &agrave; venir</td><td class="pend">interview sans filtre &agrave; venir</td></tr>
        <tr><td class="deal">Long-courrier, 12 places et plus</td><td class="pend">interview sans filtre &agrave; venir</td><td class="pend">interview sans filtre &agrave; venir</td><td class="pend">interview sans filtre &agrave; venir</td></tr>
      </table></div>
      <p style="margin-top:12px;font-size:12.5px;color:var(--faint)">La ligne qui compte : le prix tout compris au d&eacute;part de Paris, positionnement et attente inclus.</p>
    </div>
  </section>

  <section class="sect" id="questions">
    <div class="k">Bloc 3 &middot; Les questions des exiters</div>
    <h2>Ce que les fondateurs demandent vraiment.</h2>
    <div class="qa">
      <p class="qq">Le prix r&eacute;el d&#x27;un Paris-Nice aller-retour dans la journ&eacute;e, tout compris, positionnement et temps d&#x27;attente inclus.</p>
      <div class="rep"><span class="chip-attente">R&eacute;ponse de {NOM} &middot; interview sans filtre &agrave; venir</span></div>
    </div>
    <div class="qa">
      <p class="qq">L&#x27;appareil r&eacute;serv&eacute; n&#x27;est pas disponible le matin du d&eacute;part : ce qui se passe, et qui paie l&#x27;&eacute;cart.</p>
      <div class="rep"><span class="chip-attente">R&eacute;ponse de {NOM} &middot; interview sans filtre &agrave; venir</span></div>
    </div>
    <div class="qa">
      <p class="qq">Sur une carte d&#x27;heures ou une part fractionn&eacute;e, ce qui est r&eacute;cup&eacute;r&eacute; en cas d&#x27;arr&ecirc;t au bout d&#x27;un an.</p>
      <div class="rep"><span class="chip-attente">R&eacute;ponse de {NOM} &middot; interview sans filtre &agrave; venir</span></div>
    </div>
  </section>

  <section class="sect" id="chiffre">
    <div class="k">Bloc 4 &middot; Le chiffre assum&eacute;</div>
    <h2>Un seul KPI, v&eacute;rifiable, remis &agrave; jour chaque ann&eacute;e.</h2>
    <div class="card" style="margin-top:16px">
      <div class="bigstat">
        <span class="n">&mdash;</span>
        <span class="l">pourcentage de vols partis avec l&#x27;appareil initialement pr&eacute;vu, sur douze mois.</span>
      </div>
      <p style="margin-top:12px"><span class="chip-attente">Communiqu&eacute; par la maison &middot; mill&eacute;sime 2026</span></p>
    </div>
  </section>

  <section class="sect" id="interview">
    <div class="k">Bloc 5 &middot; L&#x27;interview sans filtre</div>
    <h2>L&#x27;interview sans filtre.</h2>
    <p class="lead">Extraits :</p>
    <div class="card" style="margin-top:16px">
      <div class="etq"><div class="q">&laquo; Votre taux de vols r&eacute;alis&eacute;s avec l&#x27;appareil initialement pr&eacute;vu, sur les douze derniers mois ? &raquo;</div></div>
      <div class="etq"><div class="q">&laquo; Un client doit d&eacute;coller de Paris dans quatre heures. Vous lui trouvez quoi, et &agrave; quel prix ? &raquo;</div></div>
      <div class="etq"><div class="q">&laquo; L&#x27;appareil de votre flotte que vous ne prendriez pas pour un Paris-New York ? &raquo;</div></div>
    </div>
  </section>

  """

LIENS = ('<p style="margin-top:10px;font-size:13px"><a href="%s" '
         'target="_blank" rel="noopener nofollow">Site officiel</a></p>')

CAT_OLD = "Tr\u00e9sorerie &amp; mon\u00e9taire"
CAT_NEW = "Aviation d&#x27;affaires"

G = T
for a, b, n, nom in (
    (CAT_OLD, CAT_NEW, 6, "nom de categorie"),
    ("#treso", "#jets", 3, "ancre de categorie"),
    ("cat=treso", "cat=jets", 3, "parametre de categorie"),
    ("R\u00e9mun\u00e9ration et frais, tarifs", "Prix et facturation, tarifs", 1,
     "meta description"),
):
    if G.count(a) != n:
        err.append("gabarit : %d occurrence(s) de %s au lieu de %d"
                   % (G.count(a), a[:40], n))
    else:
        G = G.replace(a, b)

G = cut(G, '<nav class="toc">', "</nav>", TOC, "sommaire")
G = cut(G, '<div class="card"><div class="k">Rep\u00e8res</div>', '<div class="gap">',
        REPERES + BLOCS + '<div class="gap">', "reperes et blocs")

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

for balise, att in (
    ('<nav class="toc">', 1),
    ('<section class="sect"', 5),
    ("chip-attente", 8),
    ("@@REPERES@@", 1),
    ("@@LIENS@@", 1),
    ("{NOM}", 3),
    (CAT_NEW, 6),
    ("#jets", 3),
    ("cat=jets", 3),
    ("Tr\u00e9sorerie", 0),
    ("treso", 0),
    ('class="verb"', 0),
):
    if G.count(balise) != att:
        print("ECHEC gabarit : %d occurrence(s) de %s au lieu de %d"
              % (G.count(balise), str(balise)[:40], att))
        sys.exit(1)
print("ok gabarit de fiche construit (%d octets)" % len(G))

# ============================================================ 3. les 7 maisons
M = [
    ("Flexjet", "flexjet", "https://www.flexjet.com",
     "Propri\u00e9t\u00e9 fractionn\u00e9e et cartes d'heures, sur une flotte "
     "annonc\u00e9e par la maison \u00e0 plus de 340 appareils, dont Praetor 600 "
     "et Gulfstream G650. Base europ\u00e9enne \u00e0 Londres, pr\u00e9sence "
     "\u00e0 Paris."),
    ("VistaJet", "vistajet", "https://www.vistajet.com",
     "Abonnement en heures de vol sur une flotte mondiale exploit\u00e9e en "
     "propre, sans propri\u00e9t\u00e9 d'appareil pour le client."),
    ("NetJets", "netjets", "https://www.netjets.com",
     "Propri\u00e9t\u00e9 fractionn\u00e9e, cartes d'heures et location, sur "
     "l'une des plus grandes flottes priv\u00e9es au monde. Le groupe appartient "
     "\u00e0 Berkshire Hathaway."),
    ("LunaJets", "lunajets", "https://www.lunajets.com",
     "Courtier suisse d'affr\u00e8tement, qui met les op\u00e9rateurs en "
     "concurrence trajet par trajet, vols de repositionnement compris."),
    ("GlobeAir", "globeair", "https://www.globeair.com",
     "Op\u00e9rateur autrichien sp\u00e9cialis\u00e9 sur les courts-courriers "
     "europ\u00e9ens, avec r\u00e9servation en ligne et tarifs publi\u00e9s."),
    ("Fly Victor", "flyvictor", "https://www.flyvictor.com",
     "Place de march\u00e9 britannique d'affr\u00e8tement, qui affiche pour un "
     "m\u00eame trajet les devis de plusieurs op\u00e9rateurs. La maison se "
     "pr\u00e9sente sous la marque Victor."),
    ("Astonjet", "astonjet", "https://astonjet.com",
     "Location, gestion et vente d'appareils, avec des bureaux \u00e0 Paris, "
     "Malte, Duba\u00ef et Kuala Lumpur. Segments annonc\u00e9s : Dassault, "
     "Gulfstream, Embraer, Cessna, Pilatus."),
]

for nom, slug, site, rep in M:
    c = os.path.join("f", slug + ".html")
    if os.path.exists(c):
        err.append("existe deja : " + c)
        continue
    t = G.replace("@@REPERES@@", "<p>" + esc(rep) + "</p>")
    t = t.replace("@@LIENS@@", LIENS % site)
    t = t.replace("{NOM}", nom)
    if t.count("institution=Spiko") != 3:
        err.append("gabarit : parametre institution introuvable")
        break
    t = t.replace("institution=Spiko", "institution=@@INST@@")
    t = t.replace("Spiko", nom).replace("spiko", slug)
    t = t.replace("@@INST@@", nom.replace(" ", "%20"))
    if "Spiko" in t or "spiko" in t or "@@" in t:
        err.append("residu dans " + c)
        continue
    for balise, att in (
        ('<h1 class="disp">%s</h1>' % nom, 1),
        ('rel="canonical" href="https://www.exit.club/f/%s"' % slug, 1),
        ('og:url" content="https://www.exit.club/f/%s"' % slug, 1),
        ('"name": "%s", "url": "https://www.exit.club/f/%s"' % (nom, slug), 1),
        ('<a class="tag" href="/ecosysteme#jets">%s</a>' % CAT_NEW, 1),
        ("chip-attente", 8),
        ('<section class="sect"', 5),
        ("R&eacute;ponse de %s" % nom, 3),
    ):
        if t.count(balise) != att:
            err.append("%s : %d occurrence(s) de %s au lieu de %d"
                       % (c, t.count(balise), str(balise)[:44], att))
    if err:
        continue
    io.open(c, "w", encoding="utf-8").write(t)
    print("ok fiche %s (%d octets)" % (c, len(t)))

# ================================================= 4. le bloc "Apres la cession"
F = "ecosysteme.html"
s = io.open(F, encoding="utf-8").read()
o = s


def sub(a, b, n):
    global s
    cc = s.count(a)
    if cc != n:
        err.append("%d occurrence(s) au lieu de %d : %s" % (cc, n, a[:70]))
        return
    s = s.replace(a, b)


LI = '      <li><a href="/f/%s">%s</a></li>\n'
BLOC = ('  </div>\n\n'
        '  <div class="apres" id="apres">\n'
        '    <div class="apres-h">\n'
        '      <p class="over">Apr\u00e8s la cession</p>\n'
        '      <h2 class="disp">Qui vous sert, une fois l&#x27;argent '
        'encaiss\u00e9.</h2>\n'
        '      <p class="lede">Les quatorze cat\u00e9gories ci-dessus recensent '
        'ceux qui conseillent la vente et le capital. Celles-ci recensent ceux '
        'que les fondateurs appellent apr\u00e8s, sous le m\u00eame standard : '
        'les m\u00eames blocs, les m\u00eames questions, les m\u00eames '
        'chiffres \u00e0 assumer.</p>\n'
        '    </div>\n'
        '    <div class="cats">\n'
        '  <section class="cat" id="jets">\n'
        '    <div class="ch">\n'
        '      <div><h3>Aviation d&#x27;affaires</h3><p class="cdesc">'
        'Propri\u00e9t\u00e9 fractionn\u00e9e, cartes d&#x27;heures, '
        'affr\u00e8tement \u00e0 la demande, vols de repositionnement.</p></div>\n'
        '      <div class="count"><b>7</b> r\u00e9f\u00e9renc\u00e9s</div>\n'
        '    </div>\n'
        '    <p class="platline"><b>Les disponibilit\u00e9s en direct</b> de ces '
        'maisons, sur une seule page<a href="/jets">Ouvrir le tableau des '
        'd\u00e9parts</a></p>\n'
        '    <ul class="firms">\n'
        + "".join(LI % (sl, nm) for nm, sl in
                  sorted([(r[0], r[1]) for r in M], key=lambda r: r[0].lower()))
        + '    </ul>\n'
        '    <div class="cta">\n'
        '      <a class="linkbtn" href="/referencement?cat=jets&demande=referencer">'
        'Vous manquez \u00e0 cette liste ? Faites-vous r\u00e9f\u00e9rencer, '
        'c&#x27;est gratuit \u2192</a>\n'
        '      <a class="linkbtn" href="/fiche-verifiee?cat=jets">Faire '
        'v\u00e9rifier mon profil \u2192</a>\n'
        '    </div>\n'
        '  </section>\n'
        '    </div>\n'
        '  </div>\n\n')

sub('  </section>\n  </div>\n\n  <section class="actus" id="actualites">',
    '  </section>\n' + BLOC + '  <section class="actus" id="actualites">', 1)

# le style du chapeau de bloc et de la ligne plateforme
sub("</style>",
    ".apres{margin-top:54px;padding-top:40px;border-top:2px solid var(--line)}\n"
    ".apres-h{max-width:680px;margin-bottom:26px}\n"
    ".apres-h h2{font-size:32px;line-height:1.08;margin-top:6px}\n"
    ".apres-h .lede{font-size:15px;color:var(--muted);margin-top:14px;"
    "line-height:1.6}\n"
    ".platline{margin:14px 0 0;font-size:13px;color:var(--muted);display:flex;"
    "gap:10px;flex-wrap:wrap;align-items:baseline}\n"
    ".platline b{color:var(--ink);font-weight:600}\n"
    ".platline a{color:var(--accent);text-decoration:none;"
    "border-bottom:1px solid var(--line)}\n"
    "</style>", 1)

# le sommaire des categories accueille la quinzieme
sub('<a href="#secondaire">Secondaire tech &amp; pr\u00e9-IPO</a></div>',
    '<a href="#secondaire">Secondaire tech &amp; pr\u00e9-IPO</a> '
    '<a href="#jets">Aviation d&#x27;affaires</a></div>', 1)

sub("dans 14 cat\u00e9gories", "dans 15 cat\u00e9gories", 1)
sub("Voir les 14 cat\u00e9gories", "Voir les 15 cat\u00e9gories", 1)
sub("4229", "4236", 3)
sub("4&nbsp;229", "4&nbsp;236", 2)

if err:
    print("ECHEC")
    for e in err:
        print(" - " + e)
    sys.exit(1)

# ==================================================== controles de sortie
import re

slugs = set(re.findall(r'<li><a href="/f/([a-z0-9-]+)">', s))
if len(slugs) != 4236:
    print("ECHEC %d slugs distincts, 4236 attendus" % len(slugs))
    sys.exit(1)
manque = [x for x in slugs if not os.path.exists("f/%s.html" % x)]
if manque:
    print("ECHEC %d lien(s) sans fiche : %s" % (len(manque), manque[:5]))
    sys.exit(1)
if len(re.findall(r'<section class="cat" id="[a-z-]+"', s)) != 15:
    print("ECHEC nombre de categories inattendu")
    sys.exit(1)
for m in re.finditer(r'<section class="cat" id="([a-z-]+)"', s):
    i = m.start()
    c = int(re.search(r'<div class="count"><b>(\d+)</b>', s[i:i + 2600]).group(1))
    n = s[i:s.find("</ul>", i)].count('<li><a href="/f/')
    if c != n:
        print("ECHEC compteur %s : %d affiche pour %d lignes" % (m.group(1), c, n))
        sys.exit(1)
if s.count("4229") or s.count("4&nbsp;229"):
    print("ECHEC ancien total residuel")
    sys.exit(1)
if s.count('id="apres"') != 1 or s.count('href="/jets"') != 1:
    print("ECHEC bloc Apres la cession incomplet")
    sys.exit(1)
if s.count('<div class="cats">') != 2:
    print("ECHEC %d grille(s) de categories au lieu de 2" % s.count('<div class="cats">'))
    sys.exit(1)
if len(s) <= len(o):
    print("ECHEC page non agrandie")
    sys.exit(1)

# ============================================ 5. le sitemap suit l'annuaire
# Regle : le sitemap contient exactement les slugs lies depuis ecosysteme.html.
# Ni les fiches de redirection, ni les etalons internes, ni les fiches mortes.
S = "sitemap.xml"
x = io.open(S, encoding="utf-8").read()
x0 = x

lies = sorted(set(re.findall(r'<li><a href="/f/([a-z0-9-]+)">', s)))
presents = set(re.findall(r"<loc>https://www\.exit\.club/f/([a-z0-9-]+)</loc>", x))
URL = "  <url><loc>https://www.exit.club/f/%s</loc></url>\n"

for mort in sorted(presents - set(lies)):
    if x.count(URL % mort) != 1:
        print("ECHEC sitemap : entree introuvable pour %s" % mort)
        sys.exit(1)
    x = x.replace(URL % mort, "")
    print("ok sitemap : /f/%s retire" % mort)

ajouts = [v for v in lies if v not in presents]
if ajouts:
    if x.count("</urlset>") != 1:
        print("ECHEC sitemap : balise de fin introuvable")
        sys.exit(1)
    x = x.replace("</urlset>", "".join(URL % v for v in ajouts) + "</urlset>")
    print("ok sitemap : %d fiche(s) ajoutee(s)" % len(ajouts))

JETS_URL = "  <url><loc>https://www.exit.club/jets</loc></url>\n"
if JETS_URL not in x:
    ECO = "  <url><loc>https://www.exit.club/ecosysteme</loc></url>\n"
    if x.count(ECO) != 1:
        print("ECHEC sitemap : ancre /ecosysteme introuvable")
        sys.exit(1)
    x = x.replace(ECO, ECO + JETS_URL, 1)
    print("ok sitemap : /jets ajoute")

apres = sorted(set(re.findall(r"<loc>https://www\.exit\.club/f/([a-z0-9-]+)</loc>", x)))
if apres != lies:
    print("ECHEC sitemap : %d entrees pour %d fiches liees" % (len(apres), len(lies)))
    sys.exit(1)
if x.count(JETS_URL) != 1:
    print("ECHEC sitemap : /jets absent ou double")
    sys.exit(1)
if x.count("<urlset") != 1 or x.count("</urlset>") != 1:
    print("ECHEC sitemap : structure cassee")
    sys.exit(1)
if x.count("<url><loc>") != x.count("</loc></url>"):
    print("ECHEC sitemap : balises desappariees")
    sys.exit(1)

io.open(S, "w", encoding="utf-8").write(x)
print("ok %s : %d -> %d octets, %d fiches" % (S, len(x0), len(x), len(apres)))

io.open(F, "w", encoding="utf-8").write(s)
print("ok %s : %d -> %d octets" % (F, len(o), len(s)))
print("controle vert : /jets, bloc Apres la cession, 7 fiches, 15 categories, 4236")
