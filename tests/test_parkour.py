import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from hazards import FireJet, SpikeStrip
from level import Level
from player import Player
from settings import GROUND_Y, PLAYER_SPEED


class ParkourTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_every_jump_is_reachable_with_current_physics(self):
        level = Level(2)
        player = Player(0, 0, 2)
        player.handle_input = lambda: None
        for start, target in zip(level.platforms, level.platforms[1:]):
            player.rect.bottomright = (start.rect.right - 2, start.rect.top)
            player.pos.update(player.rect.topleft)
            player.vel.update(PLAYER_SPEED, player.jump_strength)
            player.on_ground = False
            landed = False
            for _ in range(65):
                if player.rect.centerx >= target.rect.left + 40:
                    player.vel.x = 0
                player.update(level.platforms)
                self.assertFalse(any(
                    hazard.hits(player.rect) for hazard in level.hazards
                    if isinstance(hazard, SpikeStrip)
                ), f"Espinho no salto {start.rect} -> {target.rect}")
                if player.on_ground:
                    landed = player.rect.bottom == target.rect.top
                    break
            self.assertTrue(landed, f"Salto {start.rect} -> {target.rect}")

    def test_lava_returns_player_to_checkpoint_without_repeated_damage(self):
        level = Level(2)
        player = Player(0, 0, 2)
        rest = level.rest_platforms[1]
        player.rect.midbottom = (rest.rect.centerx, rest.rect.top)
        player.on_ground = True
        level.handle_hazards(player)
        for expected in ("fall", None):
            player.rect.bottom = GROUND_Y + 5
            self.assertEqual(level.handle_hazards(player), expected)
            self.assertEqual(player.rect.topleft, level.checkpoint)
        self.assertEqual(player.health, 2)

    def test_fire_warns_before_its_damaging_cycle(self):
        jet = FireJet(600, 300, 0)
        rect = pygame.Rect(590, GROUND_Y - 100, 20, 50)
        jet.update(jet.WARNING + 10)
        self.assertFalse(jet.hits(rect))
        jet.update(200)
        self.assertTrue(jet.hits(jet.rect))
        self.assertFalse(jet.hits(rect))
        jet.update(jet.CYCLE)
        self.assertFalse(jet.hits(rect))

    def test_spikes_can_be_crossed_without_damage(self):
        level = Level(2)
        player = Player(0, 0, 2)
        player.handle_input = lambda: None
        for spike in (h for h in level.hazards if isinstance(h, SpikeStrip)):
            platform = next(p for p in level.platforms
                            if p.rect.top == spike.rect.bottom
                            and p.rect.left <= spike.rect.left < p.rect.right)
            player.rect.bottomleft = (platform.rect.left + 15, platform.rect.top)
            player.pos.update(player.rect.topleft)
            player.vel.update(PLAYER_SPEED, player.jump_strength)
            player.on_ground = False
            for _ in range(65):
                if player.rect.left >= spike.rect.right + 8:
                    player.vel.x = 0
                player.update(level.platforms)
                self.assertFalse(spike.hits(player.rect))
                if player.on_ground:
                    break
            self.assertTrue(player.on_ground)
            self.assertGreater(player.rect.left, spike.rect.right)
            self.assertEqual(player.rect.bottom, platform.rect.top)

    def test_level_draws_with_hazards(self):
        level = Level(2)
        for _ in range(200):
            level.update()
        level.draw(pygame.display.get_surface(), 1600)
