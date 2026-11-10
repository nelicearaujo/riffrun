import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from level import Level
from objects import BoneBatEnemy, Platform
from player import Player
from settings import PLAYER_JUMP, PLAYER_SPEED, GROUND_Y
from undead import NecromancerEnemy, ZombieEnemy


class UndeadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_players_have_equal_standing_height_and_jump(self):
        for phase in (1, 2, 3):
            player = Player(100, 100, phase)
            self.assertEqual(player.jump_strength, PLAYER_JUMP)
            self.assertEqual(player.frames[0].get_bounding_rect().height, 96)

    def test_necromancer_flees_without_leaving_ground(self):
        caster = NecromancerEnemy(4100, 3700, 4500)
        player = Player(4000, 570, 3)
        for _ in range(26):
            caster.update(player)
        self.assertGreater(caster.x, 4100)
        self.assertEqual(caster.direction, 1)
        first_step = caster.frame()
        for _ in range(7):
            caster.update(player)
        self.assertIsNot(caster.frame(), first_step)
        for _ in range(200):
            caster.update(player)
        self.assertLessEqual(caster.rect.right, 4500)
        self.assertEqual(caster.rect.bottom, GROUND_Y)

    def test_phase_three_platforms_remain_reachable_with_normal_jump(self):
        level = Level(3)
        player = Player(0, 0, 3)
        player.handle_input = lambda: None
        previous_support = {670: 420, 2190: 1920, 2390: 2190}
        for target in (p for p in level.platforms if p.kind != "ground"):
            support_x = previous_support.get(target.rect.x)
            if support_x is not None:
                support = next(p for p in level.platforms if p.rect.x == support_x)
                player.rect.bottomright = (support.rect.right - 2, support.rect.top)
            else:
                player.rect.bottomleft = (target.rect.left - 120, GROUND_Y)
            player.pos.update(player.rect.topleft)
            player.vel.update(PLAYER_SPEED, player.jump_strength)
            player.on_ground = False
            landed = False
            for _ in range(70):
                if player.rect.centerx >= target.rect.left + 35:
                    player.vel.x = 0
                player.update(level.platforms)
                if player.on_ground:
                    landed = player.rect.bottom == target.rect.top
                    break
            self.assertTrue(landed, str(target.rect))

    def test_summons_enter_level_and_are_limited(self):
        level = Level(3)
        caster = next(e for e in level.enemies if isinstance(e, NecromancerEnemy))
        player = Player(caster.rect.x - 200, 570, 3)
        for _ in range(1500):
            level.update(player)
        self.assertEqual(len(caster.summons), caster.MAX_SUMMONS)
        self.assertTrue(all(z in level.enemies for z in caster.summons))
        self.assertTrue(all(caster.min_x <= z.rect.left and z.rect.right <= caster.max_x
                            for z in caster.summons))

    def test_two_necromancers_draw_books_after_detecting_player(self):
        casters = [e for e in Level(3).enemies if isinstance(e, NecromancerEnemy)]
        self.assertEqual(len(casters), 2)
        for caster in casters:
            self.assertIs(caster.frame(), caster.frames[0])
            player = Player(caster.rect.x - 200, 570, 3)
            caster.update(player)
            self.assertTrue(caster.alerted)
            for _ in range(24):
                caster.update(player)
            self.assertIs(caster.frame(), caster.frames[2])

    def test_zombie_does_not_flip_repeatedly_chasing_across_gap(self):
        zombie = ZombieEnemy(2590 - 40, 1800, 2600)
        player = Player(2790, 570, 3)
        positions, directions = [], []
        for _ in range(30):
            zombie.update(player)
            positions.append(zombie.x)
            directions.append(zombie.direction)
        self.assertEqual(len(set(directions)), 1)
        self.assertTrue(all(a > b for a, b in zip(positions, positions[1:])))

    def test_repositioned_arch_leaves_gap_jump_clear(self):
        level = Level(3)
        player = Player(2580, 570, 3)
        player.handle_input = lambda: None
        player.vel.update(PLAYER_SPEED, PLAYER_JUMP)
        for _ in range(60):
            player.update(level.platforms)
            if player.on_ground:
                break
        self.assertTrue(player.on_ground)
        self.assertGreater(player.rect.right, 2780)
        self.assertEqual(player.rect.bottom, GROUND_Y)

    def test_all_ground_gaps_have_an_unobstructed_takeoff(self):
        level = Level(3)
        floors = [p for p in level.platforms if p.kind == "ground"]
        for start, target in zip(floors, floors[1:]):
            player = Player(start.rect.right - 20, GROUND_Y - 70, 3)
            player.handle_input = lambda: None
            player.vel.update(PLAYER_SPEED, PLAYER_JUMP)
            for _ in range(65):
                player.update(level.platforms)
                if player.on_ground:
                    break
            self.assertTrue(player.on_ground)
            self.assertGreater(player.rect.right, target.rect.left)
            self.assertEqual(player.rect.bottom, GROUND_Y)

    def test_phase_three_platforms_block_head_and_sides(self):
        platform = Platform(100, 480, 180, 40)
        player = Player(150, 530, 3)
        player.handle_input = lambda: None
        player.vel.y = PLAYER_JUMP
        player.update([platform])
        self.assertEqual(player.rect.top, platform.rect.bottom)
        self.assertEqual(player.vel.y, 0)
        player.rect.topleft = (50, 470)
        player.pos.update(player.rect.topleft)
        player.vel.update(5, 0)
        player.update([platform])
        self.assertEqual(player.rect.right, platform.rect.left)

    def test_necromancer_telegraphs_then_shoots_without_homing(self):
        caster = NecromancerEnemy(2300, 1800, 2600)
        caster.alerted = True
        caster.spell_cooldown = 0
        player = Player(2050, 570, 3)
        caster.update(player)
        self.assertEqual(caster.spell_timer, 36)
        self.assertFalse(caster.projectiles)
        caster.draw(pygame.display.get_surface(), 1800)
        target = caster.spell_target.copy()
        player.rect.x = 2500
        for _ in range(36):
            caster.update(player)
        self.assertEqual(len(caster.projectiles), 1)
        projectile = caster.projectiles[0]
        expected = (target - projectile["pos"]).normalize() * 4.5
        self.assertAlmostEqual((projectile["velocity"] - expected).length(), 0)
        previous = projectile["pos"].copy()
        caster.update(player)
        self.assertNotEqual(projectile["pos"], previous)
        caster.draw(pygame.display.get_surface(), 1800)

    def test_damage_interrupts_spell_and_death_clears_projectiles(self):
        caster = NecromancerEnemy(2300, 1800, 2600)
        caster.spell_timer = 1
        caster.take_hit()
        caster.update(Player(2050, 570, 3))
        self.assertEqual(caster.spell_timer, 0)
        self.assertFalse(caster.projectiles)
        caster.health = 1
        caster.hurt_timer = 0
        caster.projectiles.append({})
        caster.take_hit()
        self.assertFalse(caster.projectiles)

    def test_three_separate_hits_kill_caster_and_stop_summoning(self):
        caster = NecromancerEnemy(4200, 3700, 4500)
        player = Player(4000, 570, 3)
        for health in (2, 1, 0):
            caster.take_hit()
            caster.take_hit()
            self.assertEqual(caster.health, health)
            for _ in range(23):
                caster.update(player)
        self.assertFalse(caster.alive)
        for _ in range(400):
            caster.update(player)
        self.assertFalse(caster.pending_summons)

    def test_death_interrupts_an_active_invocation(self):
        caster = NecromancerEnemy(4200, 3700, 4500)
        caster.health = 1
        caster.cast_timer = 1
        caster.take_hit()
        caster.update(Player(4000, 570, 3))
        self.assertFalse(caster.pending_summons)

    def test_zombie_emerges_then_telegraphs_a_melee_attack(self):
        zombie = ZombieEnemy(4000, 3700, 4500, emerging=True)
        player = Player(4065, 570, 3)
        self.assertFalse(zombie.can_damage)
        for _ in range(45):
            zombie.update(player)
        self.assertTrue(zombie.can_damage)
        zombie.update(player)
        self.assertIsNone(zombie.get_attack_rect())
        for _ in range(19):
            zombie.update(player)
        self.assertIsNotNone(zombie.get_attack_rect())
        self.assertTrue(zombie.get_attack_rect().colliderect(player.rect))

    def test_bat_bone_has_visible_shape_and_updates(self):
        bat = BoneBatEnemy(200, 200, 100, 500)
        bat.shoot(Player(400, 570, 3))
        start = bat.projectiles[0]["rect"].center
        bat.update_projectiles()
        self.assertNotEqual(start, bat.projectiles[0]["rect"].center)
        self.assertGreater(pygame.mask.from_surface(bat.bone_sprite).count(), 0)
        bat.draw(pygame.display.get_surface(), 0)
