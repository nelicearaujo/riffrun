from pathlib import Path
import pygame


def load_enemy_frames(filename, frame_size):

    path = (
        Path(__file__).resolve().parent
        / "assets"
        / "images"
        / filename
    )

    sheet = pygame.image.load(str(path)).convert_alpha()

    sheet_width, sheet_height = sheet.get_size()

    frames = []

    for row in range(2):
        for col in range(4):

            left = round(col * sheet_width / 4)
            right = round((col + 1) * sheet_width / 4)

            top = round(row * sheet_height / 2)
            bottom = round((row + 1) * sheet_height / 2)

            frame = sheet.subsurface(
                (
                    left,
                    top,
                    right - left,
                    bottom - top
                )
            ).copy()

            frame = pygame.transform.scale(
                frame,
                frame_size
            )

            frames.append(frame)

    return frames


STEEL_DARK = (20, 27, 36)
STEEL = (54, 66, 78)
STEEL_LIGHT = (117, 132, 142)
CYAN = (100, 210, 231)
AMBER = (225, 157, 48)

GRAVE_STONE_DARK = (12, 17, 29)
GRAVE_STONE = (37, 48, 67)
GRAVE_STONE_MID = (57, 70, 91)
GRAVE_STONE_LIGHT = (111, 125, 145)
GRAVE_MOSS = (57, 75, 48)

PHASE3_PLATFORM_ATLAS_PATH = (
    Path(__file__).resolve().parent
    / "assets"
    / "images"
    / "fase3_platforms_atlas.png"
)

PHASE3_ATLAS_RECTS = {
    "ground": (20, 94, 2005, 195),
    "grave_platform": (40, 374, 465, 122),
    "grave_moss": (550, 373, 405, 140),
    "grave_arch": (980, 365, 590, 230),
    "grave_skull": (1595, 385, 185, 215),
    "grave_crate": (1785, 385, 190, 215),
    "grave_pillar": (1968, 360, 160, 240),
}

PHASE2_PLATFORM_ATLAS_PATH = (
    Path(__file__).resolve().parent
    / "assets"
    / "images"
    / "fase2_platforms_atlas.png"
)

PHASE2_ATLAS_RECTS = {
    "highway_ground": (18, 87, 2012, 180),
    "highway_platform": (17, 332, 452, 142),
    "highway_platform2": (516, 332, 445, 146),
    "highway_bottom": (17, 500, 452, 145),
    "highway_hazard": (516, 500, 455, 145),
    "highway_arch": (1000, 332, 455, 280),
    "highway_lightning": (1484, 409, 128, 168),
    "highway_bars": (1617, 409, 150, 168),
    "highway_crate": (1772, 409, 140, 168),
    "highway_pillar": (1940, 378, 100, 205),
}

_phase3_platform_atlas = None
_phase2_platform_atlas = None


def load_phase3_platform_atlas():
    global _phase3_platform_atlas
    if _phase3_platform_atlas is None:
        _phase3_platform_atlas = pygame.image.load(
            str(PHASE3_PLATFORM_ATLAS_PATH)
        )
        if pygame.display.get_surface():
            _phase3_platform_atlas = _phase3_platform_atlas.convert_alpha()
    return _phase3_platform_atlas


def load_phase2_platform_atlas():
    global _phase2_platform_atlas
    if _phase2_platform_atlas is None:
        _phase2_platform_atlas = pygame.image.load(
            str(PHASE2_PLATFORM_ATLAS_PATH)
        )
        if pygame.display.get_surface():
            _phase2_platform_atlas = _phase2_platform_atlas.convert_alpha()
    return _phase2_platform_atlas


def draw_rivet(screen, x, y):
    pygame.draw.circle(screen, STEEL_LIGHT, (x, y), 3)
    pygame.draw.circle(screen, (37, 45, 53), (x, y), 1)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, kind="ground", style="beam"):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        self.kind = kind
        self.style = style

    def draw(self, screen, camera_x):
        r = self.rect.move(-camera_x, 0)
        if r.right < -80 or r.left > screen.get_width() + 80:
            return

        if self.kind == "ground":
            if self.style == "grave":
                self.draw_grave_ground(screen, r)
            elif self.style == "highway":
                self.draw_phase2_atlas_sprite(screen, r, "highway_ground")
            else:
                self.draw_ground(screen, r)
        elif self.style.startswith("grave"):
            self.draw_grave_obstacle(screen, r)
        elif self.style.startswith("highway"):
            self.draw_phase2_atlas_sprite(screen, r, self.style)
        elif self.style == "brick":
            self.draw_bricks(screen, r)
        elif self.style == "case":
            self.draw_case(screen, r)
        elif self.style == "amp":
            self.draw_amp(screen, r)
        elif self.style == "pipe":
            self.draw_pipe(screen, r)
        else:
            self.draw_beam(screen, r)

    def draw_grave_ground(self, screen, r):
        self.draw_phase3_atlas_sprite(screen, r, "ground")

    def draw_grave_obstacle(self, screen, r):
        self.draw_phase3_atlas_sprite(screen, r, self.style)

    def draw_phase3_atlas_sprite(self, screen, r, sprite_name):
        atlas = load_phase3_platform_atlas()
        source_rect = PHASE3_ATLAS_RECTS[sprite_name]
        source = atlas.subsurface(source_rect)
        if sprite_name == "ground":
            bounds = source.get_bounding_rect(min_alpha=10)
            source = source.subsurface(bounds)
        scaled_height = max(1, round(source.get_height() * r.w / source.get_width()))
        sprite = pygame.transform.smoothscale(source, (r.w, scaled_height))
        destination = sprite.get_rect(midtop=(r.centerx, r.top))
        screen.blit(sprite, destination)

    def draw_phase2_atlas_sprite(self, screen, r, sprite_name):
        atlas = load_phase2_platform_atlas()
        source = atlas.subsurface(PHASE2_ATLAS_RECTS[sprite_name])
        if sprite_name == "highway_ground":
            bounds = source.get_bounding_rect(min_alpha=10)
            source = source.subsurface(bounds)
        scaled_height = max(1, round(source.get_height() * r.w / source.get_width()))
        sprite = pygame.transform.smoothscale(source, (r.w, scaled_height))
        screen.blit(sprite, sprite.get_rect(midtop=r.midtop))

    def draw_grave_arch(self, screen, r):
        pygame.draw.rect(screen, GRAVE_STONE_DARK, r)
        pygame.draw.rect(screen, GRAVE_STONE, (r.x, r.y, r.w, 18))
        pygame.draw.rect(screen, GRAVE_STONE_LIGHT, (r.x, r.y, r.w, 4))

        pillar_w = max(14, r.w // 8)
        for x in (r.x + 18, r.right - pillar_w - 18):
            pygame.draw.rect(screen, GRAVE_STONE_MID, (x, r.y + 16, pillar_w, r.h - 16))
            pygame.draw.rect(screen, GRAVE_STONE_LIGHT, (x - 3, r.y + 16, pillar_w + 6, 5))
            pygame.draw.rect(screen, GRAVE_STONE_DARK, (x - 5, r.bottom - 9, pillar_w + 10, 9))

        arch_rect = pygame.Rect(r.x + 28, r.y + 18, r.w - 56, r.h + 8)
        pygame.draw.arc(screen, GRAVE_STONE_MID, arch_rect, 0, 3.14, 8)
        pygame.draw.arc(screen, GRAVE_STONE_LIGHT, arch_rect.inflate(-5, -4), 0, 3.14, 3)

    def draw_grave_skull_block(self, screen, r):
        pygame.draw.rect(screen, GRAVE_STONE_DARK, r, border_radius=5)
        inner = r.inflate(-6, -6)
        pygame.draw.rect(screen, GRAVE_STONE, inner, border_radius=3)
        pygame.draw.rect(screen, GRAVE_STONE_LIGHT, inner, 3, border_radius=3)
        center = inner.center
        pygame.draw.circle(screen, (17, 22, 32), (center[0] - 8, center[1] - 3), 5)
        pygame.draw.circle(screen, (17, 22, 32), (center[0] + 8, center[1] - 3), 5)
        pygame.draw.polygon(screen, (17, 22, 32), [
            (center[0] - 7, center[1] + 5),
            (center[0] + 7, center[1] + 5),
            (center[0], center[1] + 12),
        ])
        pygame.draw.line(screen, GRAVE_STONE_LIGHT,
                         (center[0] - 8, center[1] + 14),
                         (center[0] + 8, center[1] + 14), 2)

    def draw_grave_crate(self, screen, r):
        pygame.draw.rect(screen, GRAVE_STONE_DARK, r, border_radius=4)
        pygame.draw.rect(screen, GRAVE_STONE, r.inflate(-5, -5), border_radius=3)
        pygame.draw.rect(screen, GRAVE_STONE_LIGHT, r.inflate(-5, -5), 3, border_radius=3)
        pygame.draw.line(screen, GRAVE_STONE_MID, r.topleft, r.bottomright, 3)
        pygame.draw.line(screen, GRAVE_STONE_MID, r.topright, r.bottomleft, 3)

    def draw_ground(self, screen, r):
        pygame.draw.rect(screen, (12, 17, 24), r)
        pygame.draw.rect(screen, STEEL, (r.x, r.y, r.w, 16))
        pygame.draw.rect(screen, (151, 159, 158), (r.x, r.y, r.w, 4))
        pygame.draw.line(screen, (7, 11, 17), (r.x, r.y + 16), (r.right, r.y + 16), 3)

        start_x = r.x - (r.x % 72)
        for x in range(start_x, r.right + 72, 72):
            pygame.draw.line(screen, (4, 8, 13), (x, r.y), (x, r.bottom), 3)
            if r.y + 9 < r.bottom:
                draw_rivet(screen, x + 9, r.y + 9)
                draw_rivet(screen, x + 63, r.y + 9)

        # Blocos de concreto rachado sob o deck metálico.
        for row, y in enumerate(range(r.y + 20, r.bottom, 30)):
            shift = 28 if row % 2 else 0
            for x in range(start_x - 72 + shift, r.right + 72, 56):
                block = pygame.Rect(x, y, 53, 27)
                pygame.draw.rect(screen, (45, 42, 45), block)
                pygame.draw.rect(screen, (78, 71, 70), block, 2)
                if (x // 56 + row) % 3 == 0:
                    pygame.draw.line(screen, (20, 21, 26), (x + 30, y + 2), (x + 24, y + 14), 2)
                    pygame.draw.line(screen, (20, 21, 26), (x + 24, y + 14), (x + 34, y + 24), 2)

    def draw_beam(self, screen, r):
        pygame.draw.rect(screen, STEEL_DARK, r)
        pygame.draw.rect(screen, STEEL_LIGHT, (r.x, r.y, r.w, 5))
        pygame.draw.rect(screen, (5, 10, 16), (r.x, r.bottom - 5, r.w, 5))
        for x in range(r.x + 12, r.right - 8, 34):
            pygame.draw.line(screen, (83, 99, 110), (x, r.y + 6), (x + 22, r.bottom - 6), 3)
            pygame.draw.line(screen, (32, 41, 51), (x + 22, r.y + 6), (x, r.bottom - 6), 3)
            draw_rivet(screen, x, r.centery)

    def draw_bricks(self, screen, r):
        pygame.draw.rect(screen, (31, 28, 31), r)
        brick_h = 22
        for row, y in enumerate(range(r.y, r.bottom, brick_h)):
            shift = -24 if row % 2 else 0
            for x in range(r.x + shift, r.right, 48):
                brick = pygame.Rect(x + 2, y + 2, 44, min(18, r.bottom - y - 3))
                pygame.draw.rect(screen, (82, 69, 66), brick)
                pygame.draw.rect(screen, (132, 109, 97), brick, 2)
                pygame.draw.line(screen, (47, 39, 40), (brick.x + 8, brick.bottom - 4), (brick.right - 5, brick.y + 5), 1)
        pygame.draw.line(screen, (187, 165, 143), (r.x, r.y), (r.right, r.y), 4)

    def draw_case(self, screen, r):
        pygame.draw.rect(screen, (17, 23, 30), r)
        pygame.draw.rect(screen, (104, 117, 126), r, 4)
        pygame.draw.line(screen, (46, 58, 67), (r.x, r.centery), (r.right, r.centery), 3)
        for x in (r.x + 8, r.right - 8):
            pygame.draw.rect(screen, (148, 155, 155), (x - 4, r.centery - 6, 8, 12))
            draw_rivet(screen, x, r.y + 8)
            draw_rivet(screen, x, r.bottom - 8)
        pygame.draw.rect(screen, (7, 12, 18), (r.centerx - 14, r.centery - 5, 28, 10))
        pygame.draw.rect(screen, AMBER, (r.centerx - 2, r.centery - 3, 4, 6))

    def draw_amp(self, screen, r):
        pygame.draw.rect(screen, (9, 11, 15), r)
        pygame.draw.rect(screen, (112, 119, 122), r, 4)
        pygame.draw.rect(screen, (25, 29, 33), (r.x + 7, r.y + 8, r.w - 14, r.h - 15))
        speaker_y = r.centery + 3
        for x in range(r.x + 27, r.right - 12, 42):
            pygame.draw.circle(screen, (4, 7, 11), (x, speaker_y), min(15, r.h // 3))
            pygame.draw.circle(screen, (48, 57, 63), (x, speaker_y), min(15, r.h // 3), 3)
            pygame.draw.circle(screen, (13, 19, 25), (x, speaker_y), 5)
        pygame.draw.rect(screen, (51, 55, 55), (r.x + 8, r.y + 5, r.w - 16, 8))
        for x in range(r.x + 18, min(r.right - 8, r.x + 70), 13):
            pygame.draw.circle(screen, AMBER, (x, r.y + 9), 2)

    def draw_pipe(self, screen, r):
        pygame.draw.rect(screen, (38, 51, 62), r, border_radius=r.h // 2)
        pygame.draw.line(screen, (143, 158, 163), (r.x + 12, r.y + 6), (r.right - 12, r.y + 6), 4)
        pygame.draw.line(screen, (13, 21, 29), (r.x + 12, r.bottom - 5), (r.right - 12, r.bottom - 5), 4)
        for x in (r.x + 18, r.right - 18):
            pygame.draw.rect(screen, (74, 87, 96), (x - 7, r.y - 4, 14, r.h + 8))
            pygame.draw.rect(screen, STEEL_LIGHT, (x - 7, r.y - 4, 14, r.h + 8), 2)


class Guitar(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 28, 42)
        self.collected = False

    def draw(self, screen, camera_x):
        if self.collected:
            return

        r = self.rect.move(-camera_x, 0)
        # Mini guitarra angular com brilho elétrico.
        glow = pygame.Surface((52, 60), pygame.SRCALPHA)
        pygame.draw.circle(glow, (85, 207, 235, 45), (26, 30), 22)
        screen.blit(glow, (r.centerx - 26, r.centery - 30))
        pygame.draw.polygon(screen, (30, 36, 45), [
            (r.x + 2, r.y + 31), (r.x + 13, r.y + 19), (r.x + 11, r.y + 34),
            (r.x + 23, r.y + 25), (r.x + 18, r.y + 41), (r.x + 6, r.y + 38)
        ])
        pygame.draw.polygon(screen, (147, 162, 168), [
            (r.x + 3, r.y + 31), (r.x + 13, r.y + 21), (r.x + 11, r.y + 34),
            (r.x + 21, r.y + 27), (r.x + 17, r.y + 39), (r.x + 7, r.y + 37)
        ], 2)
        pygame.draw.line(screen, AMBER, (r.x + 13, r.y + 24), (r.x + 25, r.y + 2), 5)
        pygame.draw.line(screen, (246, 210, 119), (r.x + 13, r.y + 24), (r.x + 25, r.y + 2), 2)
        pygame.draw.circle(screen, CYAN, (r.x + 10, r.y + 31), 3)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, min_x, max_x):
        super().__init__()
        self.rect = pygame.Rect(x, y, 46, 46)
        self.x = float(x)
        self.speed = 2
        self.min_x = min_x
        self.max_x = max_x
        self.alive = True

    def update(self):
        if not self.alive:
            return

        self.x += self.speed
        if self.x <= self.min_x or self.x + self.rect.width >= self.max_x:
            self.speed *= -1
            self.x += self.speed

        self.rect.x = round(self.x)

    def draw(self, screen, camera_x):
        if not self.alive:
            return

        r = self.rect.move(-camera_x, 0)
        # Caixa de som possuída: mantém a hitbox simples, mas combina com o palco.
        pygame.draw.rect(screen, (11, 15, 20), r, border_radius=4)
        pygame.draw.rect(screen, (111, 119, 124), r, 3, border_radius=4)
        pygame.draw.circle(screen, (41, 50, 58), (r.centerx, r.y + 28), 12)
        pygame.draw.circle(screen, (5, 8, 12), (r.centerx, r.y + 28), 6)
        pygame.draw.polygon(screen, (219, 59, 54), [
            (r.x + 8, r.y + 10), (r.x + 18, r.y + 13), (r.x + 9, r.y + 16)
        ])
        pygame.draw.polygon(screen, (219, 59, 54), [
            (r.right - 8, r.y + 10), (r.right - 18, r.y + 13), (r.right - 9, r.y + 16)
        ])
        for x in (r.x + 5, r.right - 5):
            draw_rivet(screen, x, r.y + 5)
            draw_rivet(screen, x, r.bottom - 5)


class GoalInstrument:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 70, 90)

    def draw(self, screen, camera_x):
        r = self.rect.move(-camera_x, 0)
        glow = pygame.Surface((110, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow, (86, 209, 234, 42), (55, 65), 45)
        screen.blit(glow, (r.centerx - 55, r.centery - 60))
        pygame.draw.polygon(screen, (35, 42, 51), [
            (r.x + 5, r.y + 75), (r.x + 29, r.y + 48), (r.x + 24, r.y + 82),
            (r.x + 57, r.y + 59), (r.x + 45, r.y + 88), (r.x + 17, r.y + 86)
        ])
        pygame.draw.polygon(screen, (171, 183, 186), [
            (r.x + 7, r.y + 74), (r.x + 29, r.y + 50), (r.x + 25, r.y + 80),
            (r.x + 54, r.y + 61), (r.x + 43, r.y + 85), (r.x + 18, r.y + 84)
        ], 3)
        pygame.draw.line(screen, (211, 162, 63), (r.x + 30, r.y + 55), (r.x + 58, r.y + 7), 9)
        pygame.draw.line(screen, (241, 211, 129), (r.x + 30, r.y + 55), (r.x + 58, r.y + 7), 3)
        pygame.draw.polygon(screen, (97, 111, 121), [
            (r.x + 53, r.y + 11), (r.x + 62, r.y), (r.x + 67, r.y + 7), (r.x + 59, r.y + 17)
        ])
        pygame.draw.circle(screen, CYAN, (r.x + 26, r.y + 70), 5)


class FlyingEnemy(pygame.sprite.Sprite):
    """
    Morcego guitarrista.

    Comportamentos:
    - Patrulha aérea
    - Flutuação
    - Mergulho contra o jogador
    - Disparo de projéteis
    """

    def __init__(self, x, y, min_x, max_x):
        super().__init__()

        self.rect = pygame.Rect(x, y, 58, 48)

        self.x = float(x)
        self.y = float(y)
        self.base_y = float(y)

        self.min_x = min_x
        self.max_x = max_x

        self.speed = 2.2
        self.direction = 1

        self.health = 1
        self.alive = True

        # Animação
        self.animation_tick = 0
        self.animation_index = 0

        # Flutuação
        self.float_timer = 0

        # Inteligência
        self.state = "patrol"

        self.detection_range = 280
        self.attack_cooldown = 0

        # Mergulho
        self.dive_timer = 0
        self.dive_target = pygame.Vector2(x, y)

        # Projéteis
        self.projectiles = []
        self.projectile_speed = 5

        self.frames = load_enemy_frames(
            "morcego_guitarrista_atlas.png",
            (112, 96)
        )

    # ATUALIZAÇÃO

    def update(self, player=None):

        if not self.alive:
            return

        # Cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Atualiza projéteis
        self.update_projectiles()

        # Patrulha
        if self.state == "patrol":

            self.update_patrol()

            # Detecta jogador
            if player is not None:

                distance_x = abs(
                    player.rect.centerx - self.rect.centerx
                )

                distance_y = abs(
                    player.rect.centery - self.rect.centery
                )

                if (
                    distance_x <= self.detection_range
                    and distance_y <= 260
                    and self.attack_cooldown == 0
                ):

                    self.start_attack(player)

        # Mergulho
        elif self.state == "dive":

            self.update_dive()

        # Retorno
        elif self.state == "return":

            self.update_return()

        self.update_animation()

    # PATRULHA

    def update_patrol(self):

        self.x += self.speed * self.direction

        if self.x <= self.min_x:

            self.x = self.min_x
            self.direction = 1

        elif self.x + self.rect.width >= self.max_x:

            self.x = self.max_x - self.rect.width
            self.direction = -1

        self.float_timer += 0.08

        import math

        floating = math.sin(self.float_timer) * 15

        self.y = self.base_y + floating

        self.rect.topleft = (
            round(self.x),
            round(self.y)
        )

    # DECISÃO DO ATAQUE

    def start_attack(self, player):

        self.attack_cooldown = 150

        # Olha na direção do jogador
        if player.rect.centerx < self.rect.centerx:
            self.direction = -1
        else:
            self.direction = 1

        # Alterna os tipos de ataque
        if not hasattr(self, "attack_count"):
            self.attack_count = 0

        self.attack_count += 1

        if self.attack_count % 2 == 1:

            # Ataque de mergulho
            self.state = "dive"
            self.dive_timer = 35

            self.dive_target = pygame.Vector2(
                player.rect.center
            )

        else:

            # Ataque de projétil
            self.shoot(player)

    # MERGULHO

    def update_dive(self):

        if self.dive_timer <= 0:

            self.state = "return"
            return

        current = pygame.Vector2(
            self.rect.center
        )

        direction = self.dive_target - current

        if direction.length_squared() > 0:

            direction = direction.normalize()

            current += direction * 8

            self.rect.center = (
                round(current.x),
                round(current.y)
            )

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.dive_timer -= 1

        if self.dive_timer <= 0:
            self.state = "return"

    # RETORNAR À ALTURA ORIGINAL

    def update_return(self):

        target_y = self.base_y

        if self.y > target_y:

            self.y -= 4

            if self.y < target_y:
                self.y = target_y

        elif self.y < target_y:

            self.y += 4

            if self.y > target_y:
                self.y = target_y

        self.rect.y = round(self.y)

        if abs(self.y - target_y) < 2:

            self.state = "patrol"

    # PROJÉTEIS

    def shoot(self, player):

        origin = pygame.Vector2(
            self.rect.center
        )

        target = pygame.Vector2(
            player.rect.center
        )

        direction = target - origin

        if direction.length_squared() == 0:
            direction = pygame.Vector2(
                self.direction, 0
            )

        direction = direction.normalize()

        projectile = {
            "pos": origin.copy(),
            "velocity": direction * self.projectile_speed,
            "rect": pygame.Rect(0, 0, 14, 14),
            "lifetime": 120,
        }

        projectile["rect"].center = (
            round(origin.x),
            round(origin.y)
        )

        self.projectiles.append(projectile)

    def update_projectiles(self):

        for projectile in self.projectiles[:]:

            projectile["pos"] += projectile["velocity"]

            projectile["rect"].center = (
                round(projectile["pos"].x),
                round(projectile["pos"].y)
            )

            projectile["lifetime"] -= 1

            if projectile["lifetime"] <= 0:

                self.projectiles.remove(projectile)

    # DANO

    def take_hit(self):

        if not self.alive:
            return

        self.health -= 1

        if self.health <= 0:

            self.alive = False
            self.projectiles.clear()

    # ANIMAÇÃO

    def update_animation(self):

        self.animation_tick += 1

        if self.state == "dive":

            self.animation_index = 4

        elif self.attack_cooldown > 120:

            if self.attack_count % 2 == 0:
                self.animation_index = 5
            else:
                self.animation_index = 4

        elif self.animation_tick >= 9:

            self.animation_tick = 0

            self.animation_index = (
                self.animation_index + 1
            ) % 4

    # DESENHO

    def draw(self, screen, camera_x):

        if not self.alive:
            return

        frame = self.frames[self.animation_index]

        if self.direction < 0:

            frame = pygame.transform.flip(
                frame, True, False
            )

        draw_rect = frame.get_rect(
            center=self.rect.center
        )

        draw_rect.x -= camera_x

        screen.blit(frame, draw_rect)

        # Desenha os projéteis
        for projectile in self.projectiles:

            r = projectile["rect"].move(
                -camera_x, 0
            )

            pygame.draw.circle(
                screen,
                (214, 65, 219),
                r.center,
                8
            )

            pygame.draw.circle(
                screen,
                (255, 152, 255),
                r.center,
                4
            )

class HeavyEnemy(pygame.sprite.Sprite):
    """
    Robô Roadie.

    Inimigo pesado com:
    - 3 pontos de vida
    - Patrulha
    - Detecção do jogador
    - Investida
    - Animação de dano e derrota
    """

    def __init__(
            self,
            x,
            y,
            min_x,
            max_x,
            charge_min_x=None,
            charge_max_x=None
    ):
        super().__init__()

        self.rect = pygame.Rect(x, y, 76, 92)

        self.x = float(x)

        self.min_x = min_x
        self.max_x = max_x

        # Limites separados para a investida
        self.charge_min_x = (
            charge_min_x
            if charge_min_x is not None
            else min_x
        )

        self.charge_max_x = (
            charge_max_x
            if charge_max_x is not None
            else max_x
        )

        self.speed = 1.1
        self.charge_speed = 5.2

        self.direction = 1

        self.health = 3
        self.alive = True

        self.state = "patrol"

        self.detection_range = 240

        self.charge_timer = 0
        self.attack_cooldown = 0

        # Tempo de preparação antes da investida
        self.windup_timer = 0

        # Tempo de recuperação após atacar
        self.recovery_timer = 0

        self.hurt_timer = 0
        self.death_timer = 0

        self.animation_tick = 0
        self.animation_index = 0

        self.frames = load_enemy_frames(
            "robo_roadie_atlas.png",
            (128, 128)
        )

    # ATUALIZAÇÃO

    def update(self, player=None):
        if not self.alive:

            if self.death_timer > 0:
                self.death_timer -= 1

            return

        # Atualiza cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Atualiza animação de dano
        if self.hurt_timer > 0:
            self.hurt_timer -= 1

        # Patrulha
        if self.state == "patrol":
            self.update_patrol()
            if player is not None:
                self.detect_player(player)

        # Preparação
        elif self.state == "windup":
            self.update_windup()

        # Investida
        elif self.state == "charge":
            self.update_charge()

        # Recuperação
        elif self.state == "recovery":
            self.update_recovery()

        self.update_animation()

    # PATRULHA

    def update_patrol(self):

        self.x += self.speed * self.direction

        self.check_patrol_limits()

        self.rect.x = round(self.x)

    def check_patrol_limits(self):

        if self.x <= self.min_x:

            self.x = self.min_x
            self.direction = 1

        elif self.x + self.rect.width >= self.max_x:

            self.x = self.max_x - self.rect.width
            self.direction = -1

    # DETECÇÃO DO JOGADOR

    def detect_player(self, player):

        distance_x = abs(
            player.rect.centerx - self.rect.centerx
        )

        distance_y = abs(
            player.rect.centery - self.rect.centery
        )

        if (
            distance_x <= self.detection_range
            and distance_y <= 100
            and self.attack_cooldown == 0
            and self.hurt_timer == 0
        ):

            self.start_charge(player)

    # INVESTIDA

    def start_charge(self, player):
        # Primeiro entra em preparação
        self.state = "windup"
        # 30 frames = aproximadamente 0,5 segundo
        self.windup_timer = 30
        # Duração da investida
        self.charge_timer = 32
        # Cooldown entre ataques
        self.attack_cooldown = 150
        # Escolhe a direção do jogador
        if player.rect.centerx < self.rect.centerx:
            self.direction = -1

        else:
            self.direction = 1

    def update_charge(self):
        # Avança na direção escolhida
        self.x += (
                self.charge_speed * self.direction
        )

        # Limites seguros da investida
        if self.x <= self.charge_min_x:
            self.x = self.charge_min_x
            self.charge_timer = 0
        elif (
                self.x + self.rect.width
                >= self.charge_max_x
        ):
            self.x = (
                    self.charge_max_x
                    - self.rect.width
            )
            self.charge_timer = 0

        self.rect.x = round(self.x)
        self.charge_timer -= 1

        # Finaliza a investida
        if self.charge_timer <= 0:
            self.state = "recovery"
            self.recovery_timer = 35

    # RECEBER DANO

    def take_hit(self):

        if not self.alive:
            return

        self.health -= 1

        self.hurt_timer = 18

        # Interrompe a investida
        self.state = "patrol"

        if self.health <= 0:

            self.alive = False

            self.death_timer = 35

    # ANIMAÇÃO

    def update_animation(self):
        self.animation_tick += 1

        # Recebendo dano
        if self.hurt_timer > 0:
            self.animation_index = 6

        # Preparando a investida
        elif self.state == "windup":
            self.animation_index = 0

        # Investida
        elif self.state == "charge":
            self.animation_index = 3

        # Recuperação
        elif self.state == "recovery":
            self.animation_index = 1

        # Patrulha
        elif self.animation_tick >= 10:
            self.animation_tick = 0

            if self.animation_index == 0:
                self.animation_index = 2

            else:
                self.animation_index = 0

    # DESENHO

    def draw(self, screen, camera_x):

        if not self.alive:

            if self.death_timer <= 0:
                return

            frame = self.frames[7]

        else:

            frame = self.frames[
                self.animation_index
            ]

        if self.direction < 0:
            frame = pygame.transform.flip(
                frame, True, False
            )

        visible_bounds = frame.get_bounding_rect(min_alpha=10)
        draw_rect = frame.get_rect()
        draw_rect.x = self.rect.centerx - frame.get_width() // 2
        draw_rect.y = self.rect.bottom - visible_bounds.bottom

        draw_rect.x -= camera_x

        screen.blit(frame, draw_rect)

    def update_windup(self):
        self.windup_timer -= 1

        if self.windup_timer <= 0:
            self.state = "charge"

    def update_recovery(self):
        self.recovery_timer -= 1

        if self.recovery_timer <= 0:
            self.state = "patrol"
