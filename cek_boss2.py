"""CEK BOSS GENERIC v2 — taruh di folder game (sejajar main.py), lalu:
      python cek_boss2.py

Versi 1 gagal mengimpor level_data, jadi bagian terpenting terlewat:
boss_type mana yang SEBENARNYA dipakai game Anda. Versi ini membaca
paket `levels` seperti yang dilakukan game.
"""
import os
import re
import sys
import glob

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

print("=" * 72)
print("DIAGNOSA BOSS GENERIC  v2")
print("folder:", HERE)
print("=" * 72)

# ── 1. dari mana konfigurasi level dibaca ────────────────────────
print("\n[1] Sumber konfigurasi level")
for cand in ('levels/level_data.py', 'level_data.py',
             'levels/__init__.py'):
    p = os.path.join(HERE, cand.replace('/', os.sep))
    if os.path.exists(p):
        txt = open(p, encoding='utf-8', errors='replace').read()
        print("  ADA    %-24s %5d baris  LEVEL_8:%s" %
              (cand, len(txt.split('\n')),
               "ya" if 'LEVEL_8' in txt else "TIDAK"))
    else:
        print("  -      %-24s (tidak ada)" % cand)

ALL_LEVELS = None
for how in ('levels', 'level_data', 'levels.level_data'):
    try:
        m = __import__(how, fromlist=['ALL_LEVELS'])
        if hasattr(m, 'ALL_LEVELS'):
            ALL_LEVELS = m.ALL_LEVELS
            print("  -> berhasil: from %s import ALL_LEVELS (%d level)"
                  % (how, len(ALL_LEVELS)))
            break
    except Exception as e:
        print("  -> gagal %-18s %s" % (how, repr(e)[:44]))

# ── 2. boss_type yang dipakai tiap level ─────────────────────────
print("\n[2] boss_type yang dipakai game, per level")
used = set()
if ALL_LEVELS:
    for c in ALL_LEVELS:
        n = c.get('level_number', '?')
        mb = c.get('mini_bosses', {})
        tb = c.get('true_boss')
        print("  L%-2s mini=%-42s true=%s"
              % (n, str(list(mb.values())), tb))
        used |= set(mb.values())
        if tb:
            used.add(tb)
    print("  total boss_type dipakai:", len(used))
else:
    print("  !! ALL_LEVELS tidak terbaca")

# ── 3. rantai dispatch ───────────────────────────────────────────
print("\n[3] Rantai dispatch di bosses/base_boss.py")
bbp = os.path.join(HERE, 'bosses', 'base_boss.py')
src = open(bbp, encoding='utf-8', errors='replace').read().replace(
    '\r\n', '\n')
lines = src.split('\n')
st = next(i for i, l in enumerate(lines)
          if re.match(r'    def draw\(self, surface\):', l))
en = len(lines)
for i in range(st + 1, len(lines)):
    if re.match(r'    def ', lines[i]):
        en = i
        break
chain = set(re.findall(r'self\.boss_type\s*==\s*"(\w+)"',
                       '\n'.join(lines[st:en])))
print("  cabang:", len(chain))

reg = set()
try:
    from bosses.boss_data import get_all_boss_types
    reg = set(get_all_boss_types().keys())
    print("  terdaftar di boss_data:", len(reg))
except Exception as e:
    print("  boss_data gagal:", repr(e)[:50])

# ── 4. VONIS ─────────────────────────────────────────────────────
print("\n[4] VONIS")
miss = sorted(used - chain)
print("  dipakai game tapi TIDAK punya cabang -> GENERIC:", len(miss))
for m in miss:
    tag = "terdaftar di boss_data" if m in reg else "TIDAK di boss_data"
    print("      -", m, "(%s)" % tag)
if not miss:
    print("      (tidak ada)")

nofile = sorted(used - reg)
if nofile:
    print("  dipakai game tapi tidak ada di boss_data:", nofile)

# ── 5. uji render nyata ──────────────────────────────────────────
print("\n[5] Uji render nyata (boss yang dipakai game)")
try:
    import random
    import pygame
    pygame.init()
    pygame.display.set_mode((800, 600))
    from bosses.base_boss import Boss
    S = 400

    def px(su):
        return sum(1 for y in range(0, S, 3) for x in range(0, S, 3)
                   if su.get_at((x, y))[3] > 0)

    def mk(bt):
        b = Boss(bt)
        b.entrance_timer = 0
        b.alive = True
        b.anim_time = 30
        b.timer = 30
        b.x = b.y = S / 2
        return b

    gen, err = [], []
    for bt in sorted(used or reg):
        try:
            random.seed(7)
            s1 = pygame.Surface((S, S), pygame.SRCALPHA)
            Boss.draw(mk(bt), s1)
            random.seed(7)
            s2 = pygame.Surface((S, S), pygame.SRCALPHA)
            b2 = mk(bt)
            Boss._draw_generic_body(b2, s2, S // 2, S // 2,
                                    b2.boss_class == 'true')
            if px(s1) == px(s2):
                gen.append(bt)
        except Exception as e:
            err.append((bt, repr(e)[:50]))
    print("  diuji  :", len(used or reg))
    print("  GENERIC:", len(gen), gen or '(tidak ada)')
    print("  error  :", len(err))
    for e in err[:10]:
        print("      ", e)
except Exception as e:
    print("  gagal:", repr(e)[:70])

print("\n" + "=" * 72)
print("Kirim seluruh keluaran ini ke saya.")
print("=" * 72)
