import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from boss import BossArena, GustavoBoss
from player import Player
from settings import GROUND_Y, WIDTH, HEIGHT, PLAYER_SPEED, PLAYER_JUMP


class BossTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((WIDTH, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_stage_changes_at_health_thresholds(self):
        boss = GustavoBoss()
        for health, stage in ((12, 1), (9, 1), (8, 2), (5, 2), (4, 3), (1, 3)):
            boss.health = health
            self.assertEqual(boss.stage, stage)

    def test_health_frame_fits_below_fighters_without_covering_their_feet(self):
        arena = BossArena()
        for bar in arena.health_bars:
            rect = bar.get_rect(midbottom=(WIDTH // 2, HEIGHT - 3))
            self.assertGreater(rect.top, GROUND_Y)
            self.assertLessEqual(rect.bottom, HEIGHT)

    def test_player_can_jump_over_boss_without_body_contact(self):
        arena = BossArena()
        boss = arena.boss
        boss.rect.x = 1000
        player = Player(880, GROUND_Y - 70, 1)
        player.handle_input = lambda: None
        player.vel.update(PLAYER_SPEED, PLAYER_JUMP)
        for _ in range(43):
            player.update(arena.platforms)
            self.assertFalse(player.rect.colliderect(boss.rect))
        self.assertGreater(player.rect.left, boss.rect.right)

    def test_intro_walks_in_then_holds_pose_before_releasing_combat(self):
        boss = GustavoBoss()
        player = Player(80, GROUND_Y - 70, 1)
        self.assertGreater(boss.rect.left, WIDTH)
        previous_x = boss.x
        for _ in range(boss.INTRO_WALK):
            boss.update(player)
            self.assertLess(boss.x, previous_x)
            previous_x = boss.x
            self.assertFalse(boss.can_damage)
            self.assertIsNone(boss.get_attack_rect())
        self.assertEqual(boss.rect.x, 1000)
        for _ in range(boss.INTRO_POSE + boss.INTRO_FIGHT - 1):
            boss.update(player)
            self.assertEqual(boss.rect.x, 1000)
            self.assertFalse(boss.can_damage)
            boss.take_hit()
            self.assertEqual(boss.health, boss.MAX_HEALTH)
        boss.update(player)
        self.assertEqual(boss.intro_timer, 0)
        self.assertTrue(boss.can_damage)

    def test_intro_and_damage_invulnerability_prevent_extra_hits(self):
        boss = GustavoBoss()
        boss.take_hit()
        self.assertEqual(boss.health, 12)
        boss.intro_timer = 0
        boss.take_hit()
        boss.take_hit()
        self.assertEqual(boss.health, 11)

    def test_microphone_is_announced_before_damage(self):
        boss = GustavoBoss()
        boss.intro_timer = boss.cooldown = 0
        player = Player(800, 570, 1)
        boss.update(player)
        self.assertEqual(boss.state, "windup_mic")
        self.assertIsNone(boss.get_attack_rect())
        for _ in range(36):
            boss.update(player)
        self.assertIsNotNone(boss.get_attack_rect())

    def test_stage_two_launches_moving_equipment(self):
        boss = GustavoBoss()
        boss.intro_timer = boss.cooldown = 0
        boss.health = 8
        player = Player(300, 570, 1)
        boss.update(player)
        self.assertEqual(boss.state, "windup_throw")
        self.assertFalse(boss.projectiles)
        for _ in range(42):
            boss.update(player)
        self.assertEqual(len(boss.projectiles), 1)
        position = boss.projectiles[0]["pos"].copy()
        boss.update(player)
        self.assertNotEqual(boss.projectiles[0]["pos"], position)

    def test_projectile_creates_animated_impact_when_hitting_floor(self):
        boss = GustavoBoss()
        boss.intro_timer = 0
        rect = pygame.Rect(400, GROUND_Y - 25, 30, 34)
        boss.projectiles.append({"rect": rect, "pos": pygame.Vector2(rect.center),
                                 "velocity": pygame.Vector2(0, 2), "lifetime": 100})
        boss.update()
        self.assertFalse(boss.projectiles)
        self.assertEqual(len(boss.impacts), 1)
        boss.draw(pygame.display.get_surface())
        for _ in range(16):
            boss.update()
        self.assertFalse(boss.impacts)

    def test_final_stage_uses_both_attacks(self):
        boss = GustavoBoss()
        boss.health = 4
        boss.intro_timer = boss.cooldown = 0
        player = Player(300, 570, 1)
        boss.update(player)
        self.assertEqual(boss.state, "windup_mic")
        boss.timer = boss.cooldown = 0
        boss.update(player)
        self.assertEqual(boss.state, "windup_throw")

    def test_rain_marks_locations_before_drops_and_keeps_safe_corridors(self):
        boss = GustavoBoss()
        boss.health = 8
        boss.intro_timer = boss.cooldown = 0
        boss.attack_count = 2
        player = Player(500, 570, 1)
        boss.update(player)
        self.assertEqual(boss.state, "windup_rain")
        for _ in range(48):
            boss.update(player)
        self.assertEqual(len(boss.falling_marks), 4)
        self.assertFalse(boss.projectiles)
        xs = [m["x"] for m in boss.falling_marks]
        self.assertTrue(all(b - a >= 200 for a, b in zip(xs, xs[1:])))
        for _ in range(44):
            boss.update(player)
        self.assertFalse(boss.projectiles)
        boss.update(player)
        self.assertEqual(boss.projectiles[0]["kind"], "falling")
        self.assertLess(boss.projectiles[0]["rect"].bottom, 0)
        for _ in range(120):
            boss.update(None)
        self.assertFalse(boss.projectiles)
        self.assertFalse(boss.falling_marks)

    def test_ground_wave_can_be_jumped_and_does_not_sink_into_floor(self):
        arena = BossArena()
        boss = arena.boss
        boss.health = 4
        boss.intro_timer = boss.cooldown = 0
        boss.attack_count = 3
        boss.rect.x = 700
        boss.x = 700
        player = Player(500, 570, 1)
        boss.update(player)
        self.assertEqual(boss.state, "windup_wave")
        for _ in range(40):
            boss.update(player)
        wave = boss.projectiles[0]
        self.assertEqual(wave["kind"], "ground_wave")
        initial_y = wave["pos"].y
        player.handle_input = lambda: None
        player.vel.y = PLAYER_JUMP
        for _ in range(43):
            player.update(arena.platforms)
            boss.update(None)
            self.assertEqual(wave["pos"].y, initial_y)
            self.assertFalse(player.rect.colliderect(wave["rect"]))

    def test_interrupting_rain_cancels_pending_drops_and_recovery_allows_contact(self):
        boss = GustavoBoss()
        boss.intro_timer = 0
        boss.start_rain()
        boss.take_hit()
        self.assertFalse(boss.falling_marks)
        for _ in range(100):
            boss.update(None)
        self.assertFalse(boss.projectiles)
        boss.state = "recover"
        self.assertFalse(boss.can_damage)
        boss.state = "idle"
        self.assertTrue(boss.can_damage)

    def test_flames_warn_then_hurt_only_at_edges(self):
        arena = BossArena()
        arena.boss.health = 4
        player = Player(40, GROUND_Y - 70, 1)
        arena.update(player)
        self.assertFalse(arena.flames_active)
        for _ in range(45):
            arena.update(player)
        self.assertTrue(arena.flames_active)
        self.assertEqual(arena.handle_hazards(player), "hurt")
        player.rect.x = 500
        self.assertIsNone(arena.handle_hazards(player))

    def test_boss_defeat_clears_attacks_and_finishes_fall(self):
        boss = GustavoBoss()
        boss.intro_timer = 0
        boss.health = 1
        boss.take_hit()
        self.assertFalse(boss.alive)
        self.assertIsNone(boss.get_attack_rect())
        for _ in range(60):
            boss.update()
        self.assertEqual(boss.death_timer, 0)

    def test_arena_has_solid_floor_and_bounds_and_draws_each_stage(self):
        arena = BossArena()
        player = Player(WIDTH - 60, GROUND_Y - 80, 1)
        player.handle_input = lambda: None
        player.vel.y = 12
        player.update(arena.platforms)
        arena.update(player)
        self.assertEqual(player.rect.bottom, GROUND_Y)
        player.rect.x = WIDTH + 10
        arena.update(player)
        self.assertLess(player.rect.right, WIDTH)
        for health in (12, 8, 4):
            arena.boss.health = health
            arena.update(player)
            arena.draw_background(pygame.display.get_surface())
            arena.draw(pygame.display.get_surface())
