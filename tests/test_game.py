import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from level import Level
from objects import Enemy, FlyingEnemy, Guitar, Platform
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
        self.assertEqual(
            guitar.rect,
            pygame.Rect(120, 340, 28, 42)
        )

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
        platform = Platform(
            40, 500, 180, 30,
            "platform", "amp"
        )

        self.assertEqual(
            platform.rect,
            pygame.Rect(40, 500, 180, 30)
        )
        self.assertEqual(platform.kind, "platform")
        self.assertEqual(platform.style, "amp")

def test_flying_enemy_moves_and_takes_damage(self):
    enemy = FlyingEnemy(
        100, 400, 50, 300
    )

    initial_position = enemy.rect.topleft
    enemy.update()

    self.assertNotEqual(
        enemy.rect.topleft,
        initial_position
    )

    self.assertTrue(enemy.alive)
    enemy.take_hit()
    self.assertFalse(enemy.alive)


class LevelTests(unittest.TestCase):

    def test_final_microphones_are_supported_and_clear_of_platforms(self):
        for phase in (1, 2, 3):
            level = Level(phase)
            goal = level.goal
            self.assertEqual(goal.rect.size, goal._image.get_size())
            self.assertTrue(any(p.rect.top == goal.rect.bottom
                                and p.rect.left <= goal.rect.centerx <= p.rect.right
                                for p in level.platforms))
            self.assertFalse(any(goal.rect.colliderect(p.rect) for p in level.platforms))
            player = Player(goal.rect.x, goal.rect.bottom - 70, phase)
            self.assertTrue(player.rect.colliderect(goal.rect))

    def test_all_phases_have_ten_collectibles_with_their_phase_identity(self):
        for phase in (1, 2, 3):
            level = Level(phase)
            self.assertEqual(len(level.guitars), 10)
            self.assertTrue(all(item.phase_number == phase for item in level.guitars))
            for item in level.guitars:
                self.assertFalse(any(hazard.hits(item.rect) for hazard in level.hazards))

    # NOVO TESTE 1
    # Verifica se existe espaço suficiente para
    # o personagem caminhar abaixo das plataformas.
    def test_floating_platforms_leave_room_to_walk_below(self):

        # Hitbox do personagem: 70 pixels
        # Margem de segurança: 10 pixels
        minimum_clearance = 70 + 10

        for phase in (1, 2, 3):
            level = Level(phase)

            ground = [
                p for p in level.platforms
                if p.kind == "ground"
            ]

            floating = [
                p for p in level.platforms
                if p.kind != "ground"
            ]

            for platform in floating:
                for floor in ground:

                    # Verifica se a plataforma suspensa
                    # está horizontalmente sobre o chão.
                    if (
                        platform.rect.left < floor.rect.right
                        and platform.rect.right > floor.rect.left
                    ):
                        clearance = (
                            floor.rect.top - platform.rect.bottom
                        )

                        self.assertGreaterEqual(
                            clearance,
                            minimum_clearance,
                            f"Fase {phase}: plataforma em "
                            f"{platform.rect.topleft} "
                            f"deixa apenas {clearance} px livres"
                        )

    # NOVO TESTE 2
    # Verifica se alguma mini guitarra está
    # posicionada dentro de uma plataforma.
    def test_collectibles_do_not_overlap_solid_platforms(self):

        for phase in (1, 2, 3):
            level = Level(phase)

            for guitar in level.guitars:
                for platform in level.platforms:

                    self.assertFalse(
                        guitar.rect.colliderect(platform.rect),
                        f"Fase {phase}: coletável em "
                        f"{guitar.rect.topleft} "
                        f"intersecta plataforma em "
                        f"{platform.rect.topleft}"
                    )

    def test_phase_one_has_expected_collectibles_enemies_and_goal(self):
        level = Level(1)

        self.assertEqual(len(level.guitars), 10)
        self.assertEqual(len(level.enemies), 9)
        self.assertEqual(
            level.goal.rect.midbottom,
            (4995, 640)
        )

        self.assertTrue(
            any(
                platform.kind == "ground"
                for platform in level.platforms
            )
        )

    def test_phase_two_has_its_own_level_layout(self):
        phase_one = Level(1)
        phase_two = Level(2)

        self.assertEqual(len(phase_two.guitars), 10)
        self.assertEqual(len(phase_two.enemies), 0)
        self.assertEqual(len(phase_two.hazards), 9)

        self.assertNotEqual(
            [
                platform.rect.topleft
                for platform in phase_one.platforms
            ],
            [
                platform.rect.topleft
                for platform in phase_two.platforms
            ]
        )

    def test_update_advances_enemy_positions(self):
        level = Level(1)

        initial_position = level.enemies[0].rect.x

        level.update()

        self.assertNotEqual(
            level.enemies[0].rect.x,
            initial_position
        )


class PlayerTests(unittest.TestCase):

    def test_player_cannot_walk_past_right_edge_of_level(self):
        from settings import LEVEL_WIDTH
        player = Player(LEVEL_WIDTH - 10, 500)
        player.handle_input = lambda: None
        player.vel.x = 5
        player.update([])
        self.assertEqual(player.rect.right, LEVEL_WIDTH)
        self.assertEqual(player.pos.x, player.rect.x)

    def setUp(self):
        self.player = Player(120, 500)

    def test_attack_hitbox_is_active_only_during_attack_window(self):
        self.player.start_attack()

        self.assertIsNone(
            self.player.get_attack_rect()
        )

        self.player.attack_timer = 10
        attack_rect = self.player.get_attack_rect()

        self.assertIsNotNone(attack_rect)

        self.assertGreater(
            attack_rect.left,
            self.player.rect.right - 4
        )

    def test_damage_reduces_health_once_during_invulnerability(self):
        self.player.take_damage()
        self.player.take_damage()

        self.assertEqual(self.player.health, 2)
        self.assertEqual(
            self.player.invulnerability,
            80
        )

    def test_update_lands_on_platform(self):
        platform = Platform(80, 570, 240, 30)

        self.player.rect.topleft = (120, 490)
        self.player.pos.update(
            self.player.rect.topleft
        )
        self.player.vel.update(0, 10)

        self.player.handle_input = lambda: None

        self.player.update([platform])

        self.assertTrue(self.player.on_ground)

        self.assertEqual(
            self.player.rect.bottom,
            platform.rect.top
        )

        self.assertEqual(self.player.vel.y, 0)


if __name__ == "__main__":
    unittest.main()
