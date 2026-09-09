from settings import *
from objects import Platform, Guitar, Enemy, GoalInstrument

class Level:
    def __init__(self, phase_number=1):
        self.phase_number = phase_number
        self.platforms = []
        self.guitars = []
        self.enemies = []
        self.goal = GoalInstrument(4960, 520)

        self.build_level()

    def build_level(self):
        # Chão dividido em trechos para criar buracos.
        ground_segments = [
            (0, 850),
            (1000, 1650),
            (1800, 2600),
            (2780, 3550),
            (3700, 4500),
            (4660, 5200),
        ]

        for start, end in ground_segments:
            self.platforms.append(
                Platform(start, GROUND_Y, end - start, HEIGHT - GROUND_Y, "ground")
            )

        # Plataformas suspensas como equipamentos e estruturas de palco.
        floating = [
            (420, 520, 170, 58, "amp"),
            (670, 450, 150, 30, "beam"),
            (1120, 520, 180, 54, "case"),
            (1390, 430, 170, 48, "brick"),
            (1920, 520, 190, 58, "brick"),
            (2190, 440, 170, 30, "beam"),
            (2420, 360, 160, 32, "pipe"),
            (2910, 510, 180, 58, "amp"),
            (3200, 420, 170, 54, "case"),
            (3900, 520, 180, 58, "brick"),
            (4180, 430, 160, 30, "pipe"),
            (4740, 490, 160, 58, "amp"),
        ]

        for x, y, w, h, style in floating:
            self.platforms.append(Platform(x, y, w, h, "platform", style))

        # Mini guitarras
        guitar_positions = [
            (470, 470), (720, 400), (1165, 470), (1440, 380),
            (1970, 470), (2240, 390), (2470, 310), (2960, 460),
            (3250, 370), (3950, 470), (4230, 380), (4780, 440),
            (600, 590), (2050, 590), (3350, 590)
        ]

        for x, y in guitar_positions:
            self.guitars.append(Guitar(x, y))

        # Inimigos
        self.enemies = [
            Enemy(720, 594, 600, 840),
            Enemy(1240, 594, 1080, 1580),
            Enemy(2050, 594, 1880, 2500),
            Enemy(3100, 594, 2860, 3460),
            Enemy(4010, 594, 3760, 4430),
            Enemy(4820, 594, 4700, 5120),
        ]

    def update(self):
        for enemy in self.enemies:
            enemy.update()

    def draw(self, screen, camera_x):
        for platform in self.platforms:
            platform.draw(screen, camera_x)

        for guitar in self.guitars:
            guitar.draw(screen, camera_x)

        for enemy in self.enemies:
            enemy.draw(screen, camera_x)

        self.goal.draw(screen, camera_x)
