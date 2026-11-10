"""HUD desenhado a partir da arte fornecida em hud.png."""
from pathlib import Path

import pygame

from settings import COLLECTIBLES_PER_PHASE, WIDTH


class Hud:
    PANEL = pygame.Rect(50, 241, 671, 228)
    HELP = pygame.Rect(856, 316, 1253, 86)
    HEARTS = ((292, 312, 40, 37), (338, 312, 40, 37), (383, 312, 40, 37))
    SCALE = 365 / 671

    def __init__(self):
        path = Path(__file__).resolve().parent / "assets" / "images" / "hud.png"
        sheet = pygame.image.load(str(path)).convert_alpha()
        self.panels = []
        for health in range(4):
            panel = sheet.subsurface(self.PANEL).copy()
            for heart in self.HEARTS[health:]:
                area = pygame.Rect(heart).move(-self.PANEL.x, -self.PANEL.y)
                panel.fill((65, 65, 75, 255), area, special_flags=pygame.BLEND_RGBA_MULT)
            self.panels.append(pygame.transform.smoothscale(panel, (365, 124)))
        self.controls = pygame.transform.smoothscale(sheet.subsurface(self.HELP), (860, 59))
        self.font = pygame.font.SysFont("consolas", 19, bold=True)

    def panel_point(self, x, y):
        return (16 + round((x - self.PANEL.x) * self.SCALE),
                16 + round((y - self.PANEL.y) * self.SCALE))

    def draw(self, screen, player, phase_number):
        screen.blit(self.panels[max(0, min(3, player.health))], (16, 16))
        phase = self.font.render(str(phase_number), True, (240, 245, 250))
        counter = "—" if phase_number == 4 else f"{player.score:02d}/{COLLECTIBLES_PER_PHASE}"
        score = self.font.render(counter,
                                 True, (240, 245, 250))
        screen.blit(phase, self.panel_point(562, 317))
        screen.blit(score, self.panel_point(340, 383))
        screen.blit(self.controls, (WIDTH - 16 - self.controls.get_width(), 24))
