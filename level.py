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
        if self.phase_number == 2:
            self.build_highway_level()
            return

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

    def build_highway_level(self):
        ground_segments = [
            (0, 760), (900, 1510), (1650, 2350),
            (2490, 3200), (3340, 4100), (4230, 5200),
        ]
        for start, end in ground_segments:
            self.platforms.append(
                Platform(start, GROUND_Y, end - start, HEIGHT - GROUND_Y, "ground")
            )

        floating = [
            (280, 520, 170, 58, "amp"), (560, 430, 180, 30, "beam"),
            (810, 510, 120, 54, "case"), (1010, 500, 190, 58, "amp"),
            (1260, 390, 160, 32, "beam"), (1510, 500, 130, 54, "case"),
            (1780, 450, 200, 58, "amp"), (2100, 350, 160, 30, "beam"),
            (2350, 500, 130, 54, "case"), (2620, 430, 180, 58, "amp"),
            (2900, 350, 160, 30, "beam"), (3190, 500, 130, 54, "case"),
            (3470, 440, 180, 58, "amp"), (3750, 350, 170, 30, "beam"),
            (4070, 500, 140, 54, "case"), (4330, 420, 180, 58, "amp"),
            (4640, 340, 160, 30, "beam"), (4900, 500, 140, 54, "case"),
        ]
        for x, y, width, height, style in floating:
            self.platforms.append(Platform(x, y, width, height, "platform", style))

        guitar_positions = [
            (335, 470), (620, 380), (855, 460), (1060, 450), (1300, 340),
            (1550, 450), (1820, 410), (2140, 300), (2670, 390), (2940, 300),
            (3510, 400), (3790, 300), (4380, 380), (4690, 290), (4950, 460),
        ]
        for x, y in guitar_positions:
            self.guitars.append(Guitar(x, y))

        self.enemies = [
            Enemy(580, 594, 460, 720), Enemy(1200, 594, 1020, 1430),
            Enemy(1880, 594, 1720, 2260), Enemy(2750, 594, 2580, 3100),
            Enemy(3600, 594, 3420, 4000), Enemy(4450, 594, 4300, 4780),
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
