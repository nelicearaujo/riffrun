import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from objects import BoneBatEnemy, Enemy, HeavyEnemy, SpiderEnemy
from level import Level
from player import Player


class AnimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_damage_immediately_changes_pose_and_interrupts_attack(self):
        for phase in (1, 2, 3, 4):
            player = Player(100, 200, phase)
            player.start_attack()
            player.take_damage()
            self.assertIs(player.image, player.frames[player.animations["hurt"][0]])
            self.assertIsNone(player.get_attack_rect())
            player.start_attack()
            self.assertEqual(player.attack_timer, 0)
            canvas = pygame.Surface((1280, 720), pygame.SRCALPHA)
            player.draw(canvas, 0)
            self.assertGreater(pygame.mask.from_surface(canvas).count(), 0)

    def test_player_defeat_uses_fallen_pose_and_keeps_falling(self):
        for phase in (1, 2, 3, 4):
            player = Player(100, 200, phase)
            player.health = 1
            player.take_damage()
            for _ in range(30):
                player.update([])
            self.assertGreater(player.rect.y, 200)
            self.assertIs(player.image, player.frames[16])
            self.assertIsNone(player.get_attack_rect())

    def test_bat_draws_every_pose_in_both_directions(self):
        bat = BoneBatEnemy(100, 200, 50, 300)
        self.assertEqual(len(bat.frames), 6)
        for direction in (-1, 1):
            bat.direction = direction
            for state in ("patrol", "dive", "return"):
                bat.state = state
                for _ in range(40):
                    bat.update()
                    bat.draw(pygame.display.get_surface(), 0)
                    self.assertIn(bat.animation_index, range(6))

    def test_defeated_enemies_fall_and_expire(self):
        for enemy in (Enemy(100, 200, 50, 300),
                      SpiderEnemy(100, 250, 50, 300),
                      BoneBatEnemy(100, 200, 50, 300),
                      HeavyEnemy(100, 200, 50, 300)):
            while enemy.alive:
                enemy.take_hit()
            start_y = enemy.defeat_pos.y
            for _ in range(30):
                enemy.update()
                enemy.draw(pygame.display.get_surface(), 0)
            self.assertGreater(enemy.defeat_pos.y, start_y)
            for _ in range(30):
                enemy.update()
            self.assertEqual(enemy.death_timer, 0)

    def test_spiders_patrol_the_full_ground_segment_and_turn_at_edges(self):
        level = Level(1)
        spiders = [e for e in level.enemies if isinstance(e, SpiderEnemy)]
        floors = [p for p in level.platforms if p.kind == "ground"]
        self.assertEqual(len(spiders), len(floors))
        for spider, floor in zip(spiders, floors):
            positions = []
            for _ in range(1600):
                spider.update()
                positions.append(spider.rect.x)
                self.assertGreaterEqual(spider.rect.left, floor.rect.left)
                self.assertLessEqual(spider.rect.right, floor.rect.right)
                self.assertEqual(spider.rect.bottom, floor.rect.top)
            self.assertEqual(min(positions), floor.rect.left)
            self.assertEqual(max(positions), floor.rect.right - spider.rect.width)
            self.assertFalse(hasattr(spider, "projectiles"))
