# ================================
# GAME_DEV.PY - Developer Mode & Cheats
# ================================

import pygame
import math
from settings import *
from minion import Minion


class DevMode:
    """
    Handle developer mode: cheats, debug info, dev panel.
    Semua fitur developer tools ada disini.
    """

    def __init__(self, game):
        self.game = game
        self.enabled = False
        self.panel_open = False
        self.show_debug = False

    # ═══════════════════════════════════════
    # HOTKEY HANDLING
    # ═══════════════════════════════════════

    def handle_hotkey(self, key):
        """
        Handle F1-F12 dan cheat keys.
        Return True kalau key di-handle.
        """
        # ─── TOGGLE KEYS (selalu aktif) ───
        if key == pygame.K_F1:
            self.enabled = not self.enabled
            status = "ON" if self.enabled else "OFF"
            print(f"[DEV MODE] {status}")
            return True

        if key == pygame.K_F2:
            self.panel_open = not self.panel_open
            return True

        if key == pygame.K_F3:
            self.show_debug = not self.show_debug
            return True

        # ─── CHEAT KEYS (hanya jika dev mode ON) ───
        if not self.enabled or self.game.state != "playing":
            return False

        # Gold cheats
        if key == pygame.K_F5:
            self.game.gold += 500
            print(f"[CHEAT] +500 Gold | Total: {self.game.gold}")
            return True
        elif key == pygame.K_F6:
            self.game.gold += 2000
            print(f"[CHEAT] +2000 Gold | Total: {self.game.gold}")
            return True
        elif key == pygame.K_F7:
            self.game.gold += 10000
            print(f"[CHEAT] +10000 Gold | Total: {self.game.gold}")
            return True
        elif key == pygame.K_F8:
            self.game.ai.gold += 2000
            print(f"[CHEAT] AI +2000 Gold | AI Total: {self.game.ai.gold}")
            return True

        # Gameplay cheats
        elif key == pygame.K_F9:
            self.game.wave_timer = 0
            print(f"[CHEAT] Skip to next wave!")
            return True

        elif key == pygame.K_F10:
            count = 0
            for t in self.game.towers:
                if t.team == "blue" and t.is_player_built:
                    while t.can_upgrade():
                        if t.level == 1:
                            t.upgrade("cannon")
                        else:
                            t.upgrade()
                        count += 1
            print(f"[CHEAT] Upgraded {count} tower levels!")
            return True

        elif key == pygame.K_F11:
            while self.game.blue_base.level < MAX_NEXUS_LEVEL:
                self.game.blue_base.upgrade()
            self.game.blue_base.hp = self.game.blue_base.max_hp
            print(f"[CHEAT] Blue Castle MAX Level!")
            return True

        elif key == pygame.K_F12:
            for h in self.game.heroes:
                while h.level < MAX_HERO_LEVEL:
                    h.upgrade()
                h.hp = h.max_hp
            print(f"[CHEAT] All heroes MAX level & full HP!")
            return True

        # Combat cheats
        elif key == pygame.K_k:
            count = 0
            for m in self.game.minions:
                if m.team == "red" and m.alive:
                    m.take_damage(99999, "blue")
                    count += 1
            for t in self.game.towers:
                if t.team == "red" and t.alive:
                    t.take_damage(99999, "blue")
                    count += 1
            print(f"[CHEAT] Killed {count} enemies!")
            return True

        elif key == pygame.K_t:
            for lane in ["top", "mid", "bot"]:
                lane_path = self.game.map_renderer.get_lane_path(lane)
                for _ in range(5):
                    self.game.minions.append(Minion(
                        "goblin", "red", lane,
                        self.game.red_base.level, lane_path))
            print(f"[CHEAT] Spawned test wave!")
            return True

        elif key == pygame.K_b:
            lane_path = self.game.map_renderer.get_lane_path("mid")
            self.game.minions.append(Minion(
                "troll", "red", "mid",
                5, lane_path))
            print(f"[CHEAT] Spawned test boss!")
            return True

        elif key == pygame.K_h and pygame.key.get_mods() & pygame.KMOD_SHIFT:
            self.game.blue_base.hp = self.game.blue_base.max_hp
            for t in self.game.towers:
                if t.team == "blue":
                    t.hp = t.max_hp
            for h in self.game.heroes:
                if h.alive:
                    h.hp = h.max_hp
            print(f"[CHEAT] Full heal all blue units!")
            return True

        elif key == pygame.K_g:
            if not hasattr(self, '_god_mode'):
                self._god_mode = False
            self._god_mode = not self._god_mode
            if self._god_mode:
                self.game.blue_base.max_hp = 999999
                self.game.blue_base.hp = 999999
                print(f"[CHEAT] GOD MODE ON - Castle invincible!")
            else:
                self.game.blue_base._apply_level_stats()
                print(f"[CHEAT] GOD MODE OFF")
            return True

        elif key == pygame.K_v:
            self.game.red_base.hp = 1
            self.game.red_base.take_damage(1, "blue")
            print(f"[CHEAT] Instant Victory!")
            return True

        elif key == pygame.K_l:
            self.game.blue_base.hp = 1
            self.game.blue_base.take_damage(1, "red")
            print(f"[CHEAT] Instant Defeat!")
            return True

        # ─── BOSS DEBUG ───
        elif key == pygame.K_F4:
            # Print boss status
            red_towers = sum(1 for t in self.game.towers
                             if t.team == "red" and t.alive)
            red_slots = sum(1 for s in self.game.build_slots_red
                            if s['taken'])
            print(f"[BOSS DEBUG]")
            print(f"  Wave: {self.game.wave_number}")
            print(f"  Red towers alive: {red_towers}")
            print(f"  Red slots taken: {red_slots}")
            print(f"  Total red defense: {red_towers + red_slots}")
            print(f"  Active boss: {self.game.active_boss}")
            print(f"  True boss spawned: {self.game.true_boss_spawned}")
            print(f"  Unlocked bosses: {self.game.unlocked_bosses}")
            # Controller debug juga
            if hasattr(self.game, 'controller_mgr') and \
                    self.game.controller_mgr:
                self.game.controller_mgr.rescan()
                self.game.controller_mgr.debug_print()
            return True

        return False
    # ═══════════════════════════════════════
    # DRAWING
    # ═══════════════════════════════════════

    def draw(self, surface):
        """Draw semua dev UI"""
        self._draw_indicator(surface)
        self._draw_panel(surface)
        self._draw_debug_info(surface)

    def _draw_indicator(self, surface):
        """Small badge di corner kalau dev mode ON"""
        if not self.enabled:
            return

        pulse = math.sin(self.game.animation_time * 0.1) * 0.3 + 0.7

        ind_font = pygame.font.Font(None, 18)
        text = ind_font.render("🔧 DEV MODE", True, (0, 255, 100))
        text_rect = text.get_rect()

        bg_rect = text_rect.inflate(16, 8)
        bg_rect.topleft = (10, 10)

        bg = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bg, (0, 40, 20, int(200 * pulse)),
                         (0, 0, bg_rect.width, bg_rect.height),
                         border_radius=4)
        pygame.draw.rect(bg, (0, 255, 100, int(255 * pulse)),
                         (0, 0, bg_rect.width, bg_rect.height),
                         2, border_radius=4)
        surface.blit(bg, bg_rect.topleft)

        text_rect.center = bg_rect.center
        surface.blit(text, text_rect)

    def _draw_panel(self, surface):
        """Full dev control panel"""
        if not self.panel_open:
            return

        panel_w = 320
        panel_h = 500
        px = SCREEN_WIDTH - panel_w - 10
        py = 100

        # Shadow
        shadow = pygame.Surface((panel_w + 10, panel_h + 10),
                                pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 180),
                         (5, 5, panel_w, panel_h),
                         border_radius=8)
        surface.blit(shadow, (px - 5, py - 5))

        # Background
        pygame.draw.rect(surface, (20, 25, 40),
                         (px, py, panel_w, panel_h),
                         border_radius=8)
        pygame.draw.rect(surface, (0, 255, 100),
                         (px, py, panel_w, panel_h),
                         2, border_radius=8)

        # Title
        title_font = pygame.font.Font(None, 28)
        title = title_font.render("🔧 DEV PANEL", True, (0, 255, 100))
        surface.blit(title, (px + 15, py + 12))

        # Status
        status_font = pygame.font.Font(None, 16)
        status_text = "DEV MODE: ON" if self.enabled else "DEV MODE: OFF"
        status_color = (100, 255, 100) if self.enabled else (255, 100, 100)
        status = status_font.render(status_text, True, status_color)
        surface.blit(status, (px + 15, py + 40))

        pygame.draw.line(surface, (60, 80, 100),
                         (px + 10, py + 60),
                         (px + panel_w - 10, py + 60), 1)

        # Cheat list
        cheats = [
            ("═══ HOTKEYS ═══", (255, 200, 50), True),
            ("F1 - Toggle Dev Mode", (255, 255, 255), False),
            ("F2 - Toggle This Panel", (255, 255, 255), False),
            ("F3 - Toggle Debug Info", (255, 255, 255), False),
            ("", None, False),
            ("═══ GOLD (need dev) ═══", (255, 200, 50), True),
            ("F5 - +500 Gold", (100, 255, 100), False),
            ("F6 - +2000 Gold", (100, 255, 100), False),
            ("F7 - +10000 Gold", (100, 255, 100), False),
            ("F8 - AI +2000 Gold", (255, 150, 150), False),
            ("", None, False),
            ("═══ GAMEPLAY ═══", (255, 200, 50), True),
            ("F9 - Skip Wave", (150, 200, 255), False),
            ("F10 - Max All Towers", (150, 200, 255), False),
            ("F11 - Max Castle", (150, 200, 255), False),
            ("F12 - Max All Heroes", (150, 200, 255), False),
            ("", None, False),
            ("═══ COMBAT ═══", (255, 200, 50), True),
            ("K - Kill All Enemies", (255, 100, 100), False),
            ("T - Spawn Test Wave", (255, 150, 100), False),
            ("B - Spawn Boss (Troll)", (255, 100, 200), False),
            ("Shift+H - Heal All Blue", (100, 255, 200), False),
            ("G - Toggle God Mode", (255, 255, 100), False),
            ("", None, False),
            ("═══ WIN/LOSE ═══", (255, 200, 50), True),
            ("V - Instant Victory", (100, 255, 100), False),
            ("L - Instant Defeat", (255, 100, 100), False),
        ]

        y = py + 75
        line_font = pygame.font.Font(None, 15)
        header_font = pygame.font.Font(None, 16)

        for text, color, is_header in cheats:
            if not text:
                y += 6
                continue

            font = header_font if is_header else line_font
            text_surf = font.render(text, True, color)
            surface.blit(text_surf, (px + 15, y))
            y += 15

    def _draw_debug_info(self, surface):
        """Debug info overlay (bottom-left)"""
        if not self.show_debug:
            return

        g = self.game
        info_lines = [
            f"FPS: {int(pygame.time.Clock().get_fps())}",
            f"Minions: {len(g.minions)}",
            f"Towers: {len(g.towers)}",
            f"Heroes (Blue): {len(g.heroes)}",
            f"Heroes (Red): {len(g.ai.heroes)}",
            f"Bullets: {sum(len(t.bullets) for t in g.towers)}",
            f"Effects: {len(g.effects.floating_texts)} texts, "
            f"{len(g.effects.particles)} particles",
            f"Wave: {g.wave_number}",
            f"Player Gold: {g.gold}",
            f"AI Gold: {g.ai.gold}",
            f"Kills: {g.total_kills}",
            f"Max Combo: {g.max_combo}",
            f"State: {g.state}",
            f"Blue Castle HP: {g.blue_base.hp}/{g.blue_base.max_hp}",
            f"Red Castle HP: {g.red_base.hp}/{g.red_base.max_hp}",
        ]

        box_w = 260
        box_h = len(info_lines) * 16 + 20
        box_x = 10
        box_y = SCREEN_HEIGHT - box_h - 10

        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(bg, (0, 0, 0, 180),
                         (0, 0, box_w, box_h),
                         border_radius=5)
        pygame.draw.rect(bg, (0, 255, 100, 200),
                         (0, 0, box_w, box_h),
                         1, border_radius=5)
        surface.blit(bg, (box_x, box_y))

        title_font = pygame.font.Font(None, 16)
        title = title_font.render("🔧 DEBUG INFO", True, (0, 255, 100))
        surface.blit(title, (box_x + 8, box_y + 5))

        info_font = pygame.font.Font(None, 14)
        for i, line in enumerate(info_lines):
            text = info_font.render(line, True, (200, 255, 200))
            surface.blit(text, (box_x + 8, box_y + 22 + i * 16))