import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from hud import Hud


class HudTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_losing_lives_only_dims_the_lost_hearts(self):
        hud = Hud()
        full = pygame.Surface((1280, 720))
        hud.draw(full, SimpleNamespace(health=3, score=0), 1)
        for health in (0, 1, 2, 3):
            target = pygame.Surface((1280, 720))
            hud.draw(target, SimpleNamespace(health=health, score=0), 1)
            for index, heart in enumerate(hud.HEARTS):
                x, y = hud.panel_point(heart[0] + 20, heart[1] + 14)
                if index < health:
                    self.assertEqual(target.get_at((x, y)), full.get_at((x, y)))
                else:
                    self.assertLess(sum(target.get_at((x, y))[:3]),
                                    sum(full.get_at((x, y))[:3]))

    def test_all_phases_render_counter_and_controls(self):
        hud = Hud()
        for phase in (1, 2, 3):
            before = pygame.Surface((1280, 720))
            after = pygame.Surface((1280, 720))
            hud.draw(before, SimpleNamespace(health=3, score=0), phase)
            hud.draw(after, SimpleNamespace(health=3, score=10), phase)
            self.assertNotEqual(pygame.image.tobytes(before, "RGB"),
                                pygame.image.tobytes(after, "RGB"))
            self.assertEqual(before.get_at((500, 45)), after.get_at((500, 45)))
