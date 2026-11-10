import pygame
from scoring import RunScore
from undead import NecromancerEnemy, ZombieEnemy

from settings import *
from hazards import SpikeStrip, FireJet, draw_lava
from objects import (
    Platform,
    Guitar,
    Enemy,
    SpiderEnemy,
    FlyingEnemy,
    CloudEnemy,
    BoneBatEnemy,
    HeavyEnemy,
    GoalInstrument,
)
class Level:
    def __init__(self, phase_number=1):
        self.phase_number = phase_number
        self.run_score = RunScore()
        self.platforms = []
        self.guitars = []
        self.enemies = []
        self.hazards = []
        self.hazard_tick = 0
        self.checkpoint = (120, 500)
        self.rest_platforms = []
        self.goal = GoalInstrument(4960, GROUND_Y - 90)

        self.build_level()

    def build_level(self):
        if self.phase_number == 2:
            self.build_lava_level()
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

        # Dez baixos distribuídos entre o chão e as plataformas.
        guitar_positions = [
            (470, 470), (720, 400), (1165, 470), (1440, 380),
            (1970, 470), (2470, 310), (2960, 460), (3250, 370),
            (3950, 440), (4780, 440),
        ]

        for x, y in guitar_positions:
            self.guitars.append(
                Guitar(x, y, self.phase_number)
            )

        # INIMIGOS DA FASE

        self.enemies = [
            # Inimigos terrestres
            *[SpiderEnemy(x, GROUND_Y, start, end)
              for x, (start, end) in zip(
                  (720, 1240, 2050, 3100, 4010, 4820), ground_segments)],

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
        self.goal = GoalInstrument(5100, GROUND_Y - 90)
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
            (1120, 479, 80, 81, "grave_crate"),
            (1390, 478, 80, 82, "grave_skull"),
            (1920, 490, 190, 66, "grave_moss"),
            (2190, 440, 170, 44, "grave_platform"),
            (2390, 400, 160, 86, "grave_arch"),
            (2910, 510, 180, 47, "grave_platform"),
            (3250, 478, 80, 82, "grave_skull"),
            (3880, 490, 160, 55, "grave_moss"),
            (4820, 470, 220, 86, "grave_arch"),
        ]
        for x, y, width, height, style in floating:
            self.platforms.append(Platform(x, y, width, height, "platform", style))

        guitar_positions = [
            (470, 464), (720, 404), (1146, 433), (1416, 432),
            (1970, 444), (2470, 354), (2960, 464), (3276, 432),
            (3950, 444), (4860, 424),
        ]
        for x, y in guitar_positions:
            self.guitars.append(Guitar(x, y, self.phase_number))

        self.enemies = [
            *[ZombieEnemy(x, start, end) for x, (start, end) in zip(
                (720, 1240, 2050, 3100, 4010, 4820), ground_segments)],
            # Morcegos ósseos da fase 3
            BoneBatEnemy(
                1450, 480,
                1350, 1750
            ),
            BoneBatEnemy(
                3300, 490,
                3150, 3500
            ),
            NecromancerEnemy(2300, 1800, 2600),
            NecromancerEnemy(4270, 3700, 4500),
        ]

    def build_lava_level(self):
        # Saltos sobem no maximo 90 px; os vãos ficam abaixo de 170 px.
        route = [
            (0, 590, 340), (450, 520, 180), (750, 450, 150),
            (1030, 510, 260), (1310, 430, 150), (1580, 510, 320),
            (2030, 440, 150), (2320, 370, 140), (2590, 460, 260),
            (2880, 390, 150), (3160, 490, 320), (3620, 410, 150),
            (3910, 470, 260), (4200, 390, 140), (4480, 460, 260),
            (4780, 550, 420),
        ]
        for index, (x, y, width) in enumerate(route):
            platform = Platform(x, y, width, 30, "platform", "highway_platform2")
            self.platforms.append(platform)
            if index in (0, 5, 10, 15):
                self.rest_platforms.append(platform)
            if index in (1, 2, 4, 5, 7, 9, 10, 11, 13, 15):
                self.guitars.append(Guitar(x + width // 2 - 14, y - 65, self.phase_number))

        self.hazards = [
            SpikeStrip(1130, 510), SpikeStrip(2690, 460),
            SpikeStrip(4010, 470), SpikeStrip(4580, 460),
            FireJet(695, 260, 0), FireJet(1960, 300, 75),
            FireJet(2820, 330, 140), FireJet(3540, 300, 35),
            FireJet(4710, 270, 100),
        ]
        self.goal = GoalInstrument(5050, 550 - 90)

    def handle_hazards(self, player):
        """Retorna o tipo de dano para o controlador tocar o efeito adequado."""
        if self.phase_number != 2:
            return None
        for platform in self.rest_platforms:
            if (player.on_ground and player.rect.bottom == platform.rect.top
                    and platform.rect.left <= player.rect.centerx <= platform.rect.right):
                self.checkpoint = (platform.rect.left + 65,
                                   platform.rect.top - player.rect.height)

        if player.rect.bottom >= GROUND_Y:
            previous_health = player.health
            player.take_damage()
            player.pos.update(*self.checkpoint)
            player.rect.topleft = self.checkpoint
            player.vel.update(0, 0)
            player.on_ground = False
            return "fall" if player.health < previous_health else None

        if any(hazard.hits(player.rect) for hazard in self.hazards):
            previous_health = player.health
            player.take_damage()
            if player.health < previous_health:
                return "hurt"
        return None

    def update(self, player=None):
        self.hazard_tick += 1
        for hazard in self.hazards:
            if isinstance(hazard, FireJet):
                hazard.update(self.hazard_tick)
        for enemy in self.enemies[:]:
            if isinstance(
                    enemy,
                    (FlyingEnemy, HeavyEnemy, NecromancerEnemy, ZombieEnemy)
            ):
                enemy.update(player)
            else:
                enemy.update()
            if isinstance(enemy, NecromancerEnemy):
                self.enemies.extend(enemy.pending_summons)
                enemy.pending_summons.clear()
        # Evita acumular corpos de invocações durante partidas longas.
        self.enemies = [e for e in self.enemies if not (
            isinstance(e, ZombieEnemy) and not e.alive and getattr(e, "death_timer", 0) == 0)]

    def draw(self, screen, camera_x):
        if self.phase_number == 2:
            draw_lava(screen, camera_x, self.hazard_tick)
        for platform in self.platforms:
            platform.draw(screen, camera_x)

        for hazard in self.hazards:
            hazard.draw(screen, camera_x)

        if self.phase_number == 2:
            for platform in self.rest_platforms[1:-1]:
                x = platform.rect.left + 65 - camera_x
                y = platform.rect.top
                active = self.checkpoint[0] == platform.rect.left + 65
                color = (110, 235, 170) if active else (230, 200, 100)
                pygame.draw.line(screen, color, (x, y), (x, y - 48), 3)
                pygame.draw.polygon(screen, color,
                                    [(x, y - 48), (x + 25, y - 39), (x, y - 30)])

        for guitar in self.guitars:
            guitar.draw(screen, camera_x)

        for enemy in self.enemies:
            enemy.draw(screen, camera_x)

        self.goal.draw(screen, camera_x)
