import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from level import Level
from objects import Enemy, Guitar, Platform
from player import Player


def setUpModule():
    pygame.init()
    pygame.display.set_mode((1, 1))


def tearDownModule():
    pygame.quit()


class ObjectsTests(unittest.TestCase):
    def test_guitar_starts_uncollected_with_expected_hitbox(self):
        guitar = Guitar(120, 340)

        self.assertFalse(guitar.collected)
        self.assertEqual(guitar.rect, pygame.Rect(120, 340, 28, 42))

    def test_enemy_moves_inside_patrol_range_and_can_be_defeated(self):
        enemy = Enemy(100, 594, 100, 150)

        enemy.update()
        self.assertGreaterEqual(enemy.rect.left, enemy.min_x)
        self.assertLessEqual(enemy.rect.right, enemy.max_x)

        enemy.alive = False
        previous_position = enemy.rect.x
        enemy.update()
        self.assertEqual(enemy.rect.x, previous_position)

    def test_platform_preserves_geometry_and_style(self):
        platform = Platform(40, 500, 180, 30, "platform", "amp")

        self.assertEqual(platform.rect, pygame.Rect(40, 500, 180, 30))
        self.assertEqual(platform.kind, "platform")
        self.assertEqual(platform.style, "amp")


class LevelTests(unittest.TestCase):
    def test_phase_one_has_expected_collectibles_enemies_and_goal(self):
        level = Level(1)

        self.assertEqual(len(level.guitars), 15)
        self.assertEqual(len(level.enemies), 6)
        self.assertEqual(level.goal.rect.topleft, (4960, 520))
        self.assertTrue(any(platform.kind == "ground" for platform in level.platforms))

    def test_phase_two_has_its_own_level_layout(self):
        phase_one = Level(1)
        phase_two = Level(2)

        self.assertEqual(len(phase_two.guitars), 15)
        self.assertEqual(len(phase_two.enemies), 6)
        self.assertNotEqual(
            [platform.rect.topleft for platform in phase_one.platforms],
            [platform.rect.topleft for platform in phase_two.platforms],
        )

    def test_update_advances_enemy_positions(self):
        level = Level(1)
        initial_position = level.enemies[0].rect.x

        level.update()

        self.assertNotEqual(level.enemies[0].rect.x, initial_position)


class PlayerTests(unittest.TestCase):
    def setUp(self):
        self.player = Player(120, 500)

    def test_attack_hitbox_is_active_only_during_attack_window(self):
        self.player.start_attack()
        self.assertIsNone(self.player.get_attack_rect())

        self.player.attack_timer = 10
        attack_rect = self.player.get_attack_rect()

        self.assertIsNotNone(attack_rect)
        self.assertGreater(attack_rect.left, self.player.rect.right - 4)

    def test_damage_reduces_health_once_during_invulnerability(self):
        self.player.take_damage()
        self.player.take_damage()

        self.assertEqual(self.player.health, 2)
        self.assertEqual(self.player.invulnerability, 80)

    def test_update_lands_on_platform(self):
        platform = Platform(80, 570, 240, 30)
        self.player.rect.topleft = (120, 490)
        self.player.pos.update(self.player.rect.topleft)
        self.player.vel.update(0, 10)
        self.player.handle_input = lambda: None

        self.player.update([platform])

        self.assertTrue(self.player.on_ground)
        self.assertEqual(self.player.rect.bottom, platform.rect.top)
        self.assertEqual(self.player.vel.y, 0)


if __name__ == "__main__":
    unittest.main()
