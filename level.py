from settings import *
from objects import (
    Platform,
    Guitar,
    Enemy,
    FlyingEnemy,
    CloudEnemy,
    BoneBatEnemy,
    HeavyEnemy,
    GoalInstrument,
)
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
        if self.phase_number == 3:
            self.build_graveyard_level()
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
                Platform(
                    start,
                    GROUND_Y,
                    end - start,
                    HEIGHT - GROUND_Y,
                    "ground",
                    "metal"
                )
            )

        # Plataformas suspensas como equipamentos e estruturas de palco.
        floating = [
            (420, 520, 170, 30, "metal_platform2"),
            (670, 450, 150, 30, "metal_platform"),
            (1120, 520, 180, 30, "metal_bottom"),
            (1390, 430, 170, 48, "metal_platform2"),
            (1920, 520, 190, 30, "metal_platform"),
            (2190, 440, 170, 30, "metal_platform2"),
            (2420, 360, 160, 32, "metal_small"),
            (2910, 510, 180, 30, "metal_platform"),
            (3200, 420, 170, 54, "metal_bottom"),
            (3880, 490, 160, 28, "metal_platform"),
            (4740, 490, 160, 58, "metal_platform2"),
        ]

        for x, y, w, h, style in floating:
            self.platforms.append(Platform(x, y, w, h, "platform", style))

        # Mini guitarras
        guitar_positions = [
            (470, 470), (720, 400), (1165, 470), (1440, 380),
            (1970, 470), (2240, 390), (2470, 310), (2960, 460),
            (3250, 370), (3950, 440),(4780, 440),
            (600, 590),(1050, 590), (2050, 590), (3350, 590)
        ]

        for x, y in guitar_positions:
            self.guitars.append(Guitar(x, y))

        # INIMIGOS DA FASE

        self.enemies = [
            # Inimigos terrestres
            Enemy(720, 594, 600, 840),
            Enemy(1240, 594, 1080, 1580),
            Enemy(2050, 594, 1880, 2500),
            Enemy(3100, 594, 2860, 3460),
            Enemy(4010, 594, 3760, 4430),
            Enemy(4820, 594, 4700, 5120),

            # Nuvens de relâmpagos da fase 1
            CloudEnemy(
                1450, 480,
                1350, 1750
            ),

            CloudEnemy(
                3300, 490,
                3150, 3500
            ),

            # Robô Roadie
            HeavyEnemy(
                4270,
                548,
                # Patrulha
                4220,
                4410,
                # Investida
                4050,
                4500
            ),
        ]

    def build_graveyard_level(self):
        ground_segments = [
            (0, 850), (1000, 1650), (1800, 2600),
            (2780, 3550), (3700, 4500), (4660, 5200),
        ]
        for start, end in ground_segments:
            self.platforms.append(
                Platform(start, GROUND_Y, end - start, HEIGHT - GROUND_Y, "ground", "grave")
            )

        floating = [
            (420, 510, 170, 45, "grave_platform"),
            (670, 450, 150, 52, "grave_moss"),
            (1120, 450, 96, 109, "grave_crate"),
            (1390, 455, 90, 105, "grave_skull"),
            (1920, 490, 190, 66, "grave_moss"),
            (2190, 440, 170, 44, "grave_platform"),
            (2420, 400, 220, 86, "grave_arch"),
            (2910, 510, 180, 47, "grave_platform"),
            (3200, 445, 95, 110, "grave_skull"),
            (3880, 490, 160, 55, "grave_moss"),
            (4740, 470, 220, 86, "grave_arch"),
        ]
        for x, y, width, height, style in floating:
            self.platforms.append(Platform(x, y, width, height, "platform", style))

        guitar_positions = [
            (470, 450), (720, 400), (1165, 390), (1440, 380),
            (1970, 425), (2240, 390), (2470, 310), (2960, 460),
            (3250, 370), (3950, 440), (4780, 415),
            (600, 590), (1050, 590), (2050, 590), (3350, 590),
        ]
        for x, y in guitar_positions:
            self.guitars.append(Guitar(x, y))

        self.enemies = [
            Enemy(720, 594, 600, 840),
            Enemy(1240, 594, 1080, 1580),
            Enemy(2050, 594, 1880, 2500),
            Enemy(3100, 594, 2860, 3460),
            Enemy(4010, 594, 3760, 4430),
            Enemy(4820, 594, 4700, 5120),
            # Morcegos ósseos da fase 3
            BoneBatEnemy(
                1450, 480,
                1350, 1750
            ),
            BoneBatEnemy(
                3300, 490,
                3150, 3500
            ),            HeavyEnemy(4270, 548, 4220, 4410, 4050, 4500),
        ]

    def build_highway_level(self):
        ground_segments = [
            (0, 760), (900, 1510), (1650, 2350),
            (2490, 3200), (3340, 4100), (4230, 5200),
        ]
        for start, end in ground_segments:
            self.platforms.append(
                Platform(start, GROUND_Y, end - start, HEIGHT - GROUND_Y, "ground", "highway")
            )

        floating = [
            (280, 500, 170, 53, "highway_platform"), (560, 430, 180, 59, "highway_platform2"),
            (810, 510, 120, 38, "highway_bottom"), (1010, 380, 190, 117, "highway_arch"),
            (1260, 390, 160, 50, "highway_platform"), (1510, 500, 130, 41, "highway_hazard"),
            (1780, 430, 200, 66, "highway_platform2"), (2100, 350, 160, 99, "highway_arch"),
            (2350, 450, 70, 92, "highway_lightning"), (2620, 430, 180, 59, "highway_platform2"),
            (2900, 350, 160, 99, "highway_arch"), (3190, 450, 70, 78, "highway_bars"),
            (3470, 430, 180, 59, "highway_platform2"), (3750, 340, 170, 105, "highway_arch"),
            (4070, 450, 70, 84, "highway_crate"), (4330, 420, 180, 59, "highway_platform2"),
            (4640, 340, 160, 99, "highway_arch"), (4900, 430, 60, 123, "highway_pillar"),
        ]
        for x, y, width, height, style in floating:
            self.platforms.append(Platform(x, y, width, height, "platform", style))

        guitar_positions = [
            (335, 450), (620, 380), (855, 460), (1060, 330), (1300, 340),
            (1550, 450), (1820, 350), (2140, 300), (2670, 380), (2940, 300),
            (3510, 360), (3790, 290), (4380, 370), (4690, 290), (4950, 380),
        ]
        for x, y in guitar_positions:
            self.guitars.append(Guitar(x, y))

        self.enemies = [
            Enemy(580, 594, 460, 720), Enemy(1200, 594, 1020, 1430),
            Enemy(1880, 594, 1720, 2260), Enemy(2750, 594, 2580, 3100),
            Enemy(3600, 594, 3420, 4000), Enemy(4450, 594, 4300, 4780),
        ]

    def update(self, player=None):
        for enemy in self.enemies:
            if isinstance(
                    enemy,
                    (FlyingEnemy, HeavyEnemy)
            ):
                enemy.update(player)
            else:
                enemy.update()

    def draw(self, screen, camera_x):
        for platform in self.platforms:
            platform.draw(screen, camera_x)

        for guitar in self.guitars:
            guitar.draw(screen, camera_x)

        for enemy in self.enemies:
            enemy.draw(screen, camera_x)

        self.goal.draw(screen, camera_x)
