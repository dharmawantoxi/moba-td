"""CEK PEMASANGAN PAKET — taruh di folder game (sejajar main.py), lalu:
      python cek_paket.py

Memeriksa apakah towers/, minions/, map_components/ sudah terpasang
benar setelah penggabungan file. Tidak mengubah apa pun.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

PKGS = {
    'towers': ['archer_tower', 'cannon_tower', 'ice_tower',
               'mage_tower', 'base_renderer'],
    'minions': ['goblin', 'orc', 'troll', 'undead', 'dark_rider',
                'base_renderer'],
    'map_components': ['palettes', 'themes', 'generators',
                       'static_renderer', 'dynamic_renderer',
                       'decoration_renderer', 'shop_renderer'],
}

print("=" * 70)
print("CEK PEMASANGAN PAKET")
print("folder:", HERE)
print("=" * 70)

problems = []

for pkg, mods in PKGS.items():
    d = os.path.join(HERE, pkg)
    print("\n[%s]" % pkg)
    if not os.path.isdir(d):
        print("   folder tidak ada — dilewati")
        continue

    has_bundle = os.path.exists(os.path.join(d, '_bundle.py'))
    ip = os.path.join(d, '__init__.py')
    has_init = os.path.exists(ip)
    init_txt = ''
    if has_init:
        init_txt = open(ip, encoding='utf-8', errors='replace').read()
    has_alias = '_install_aliases' in init_txt

    leftovers = [m + '.py' for m in mods
                 if os.path.exists(os.path.join(d, m + '.py'))]
    pyc = os.path.isdir(os.path.join(d, '__pycache__'))

    print("   _bundle.py            :", "ADA" if has_bundle else "TIDAK ADA")
    print("   __init__.py           :", "ADA" if has_init else "TIDAK ADA")
    print("   __init__ punya alias  :",
          "YA" if has_alias else "TIDAK  <-- MASIH VERSI LAMA")
    print("   file lama tersisa     :",
          len(leftovers), leftovers if leftovers else '')
    print("   __pycache__           :",
          "ADA  <-- HAPUS" if pyc else "bersih")

    if has_bundle and not has_alias:
        problems.append(
            "%s/__init__.py masih versi LAMA — timpa dengan yang dari "
            "patch" % pkg)
    if not has_bundle:
        problems.append("%s/_bundle.py belum disalin" % pkg)
    if pyc:
        problems.append("hapus %s/__pycache__" % pkg)

print("\n" + "=" * 70)
print("UJI IMPOR NYATA")
print("=" * 70)
sys.path.insert(0, HERE)
try:
    import pygame
    pygame.init()
    pygame.display.set_mode((100, 100))
except Exception as e:
    print("  pygame gagal:", repr(e)[:60])

CHECKS = [
    ("from map_components.palettes import *",
     "from map_components.palettes import *"),
    ("from map_components.themes import get_theme",
     "from map_components.themes import get_theme"),
    ("from map_components.static_renderer import StaticRenderer",
     "from map_components.static_renderer import StaticRenderer"),
    ("from towers.archer_tower import draw_archer",
     "from towers.archer_tower import draw_archer"),
    ("from minions.goblin import draw_goblin",
     "from minions.goblin import draw_goblin"),
    ("from minions.base_renderer import cached_minion_draw",
     "from minions.base_renderer import cached_minion_draw"),
    ("from towers import render_tower",
     "from towers import render_tower"),
    ("from minions import render_minion",
     "from minions import render_minion"),
    ("import map_renderer", "import map_renderer"),
]
ok = 0
for label, stmt in CHECKS:
    try:
        exec(stmt, {})
        print("  OK    ", label)
        ok += 1
    except Exception as e:
        print("  GAGAL ", label)
        print("          ", repr(e)[:80])
        problems.append("impor gagal: " + label)

print("\n  berhasil: %d / %d" % (ok, len(CHECKS)))

print("\n" + "=" * 70)
if problems:
    print("MASALAH DITEMUKAN:")
    seen = set()
    for p in problems:
        if p not in seen:
            seen.add(p)
            print("  -", p)
else:
    print("SEMUA BERES")
print("=" * 70)
