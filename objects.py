from pathlib import Path
from functools import lru_cache
import pygame


def begin_defeat(enemy, image):
    enemy.death_timer = 55
    enemy.defeat_image = image.copy()
    enemy.defeat_pos = pygame.Vector2(enemy.rect.center)
    enemy.defeat_velocity = pygame.Vector2(-2 * getattr(enemy, "direction", 1), -5)


def update_defeat(enemy):
    if getattr(enemy, "death_timer", 0) > 0:
        enemy.death_timer -= 1
        enemy.defeat_velocity.y += 0.65
        enemy.defeat_pos += enemy.defeat_velocity


def draw_defeat(enemy, screen, camera_x):
    if getattr(enemy, "death_timer", 0) <= 0:
        return
    image = pygame.transform.rotate(enemy.defeat_image,
                                    max(0, 47 - enemy.death_timer) * 3)
    if enemy.death_timer > 47:
        image.fill((255, 120, 120, 255), special_flags=pygame.BLEND_RGBA_MULT)
    if enemy.death_timer < 15:
        image.set_alpha(enemy.death_timer * 17)
    screen.blit(image, image.get_rect(center=(round(enemy.defeat_pos.x - camera_x),
                                             round(enemy.defeat_pos.y))))


@lru_cache(maxsize=4)
def collectible_frame(index):
    """Recorta guitarra, microfone, bateria e baixo sem dividir instrumentos."""
    path = Path(__file__).resolve().parent / "assets" / "images" / "coletaveis_atlas.png"
    sheet = pygame.image.load(str(path)).convert_alpha()
    width, height = sheet.get_size()
    edges = (0, 0.29, 0.46, 0.77, 1)
    left, right = round(edges[index] * width), round(edges[index + 1] * width)
    frame = sheet.subsurface((left, 0, right - left, height))
    bounds = frame.get_bounding_rect(min_alpha=10)
    if not bounds.width or not bounds.height:
        raise ValueError(f"Coletável vazio no índice {index}")
    return frame.subsurface(bounds).copy()

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

def load_cloud_frames():
    """Carrega as animações da nuvem de relâmpagos."""

    path = (
        Path(__file__).resolve().parent
        / "assets"
        / "images"
        / "nuvem_relampago_atlas.png"
    )

    sheet = pygame.image.load(str(path)).convert_alpha()

    # Recortes: x, y, largura, altura.
    # Cinco poses de voo e uma de ataque.
    frame_rects = [
        (0, 0, 305, 320),
        (305, 0, 300, 320),
        (605, 0, 290, 320),
        (895, 0, 305, 320),
        (1200, 0, 336, 320),
        (305, 340, 310, 290),
    ]

    frames = []

    for rect in frame_rects:
        frame = sheet.subsurface(rect).copy()

        bounds = frame.get_bounding_rect(min_alpha=10)

        if bounds.width == 0 or bounds.height == 0:
            raise ValueError(
                f"Recorte vazio no spritesheet da nuvem: {rect}"
            )

        frame = frame.subsurface(bounds).copy()

        # Mantém a proporção original da nuvem.
        scale = min(
            112 / frame.get_width(),
            96 / frame.get_height()
        )

        new_size = (
            max(1, round(frame.get_width() * scale)),
            max(1, round(frame.get_height() * scale))
        )

        frame = pygame.transform.scale(frame, new_size)

        canvas = pygame.Surface((112, 96), pygame.SRCALPHA)

        canvas.blit(
            frame,
            frame.get_rect(center=(56, 48))
        )

        frames.append(canvas)

    return frames

def load_cloud_effects():
    """
    Carrega os efeitos especiais da nuvem:
    - Projétil elétrico
    - Quatro quadros da animação de derrota
    """

    path = (
        Path(__file__).resolve().parent
        / "assets"
        / "images"
        / "nuvem_relampago_atlas.png"
    )

    sheet = pygame.image.load(str(path)).convert_alpha()

    def crop_effect(rect, max_width, max_height):
        image = sheet.subsurface(rect).copy()

        bounds = image.get_bounding_rect(min_alpha=10)

        if bounds.width == 0 or bounds.height == 0:
            raise ValueError(f"Efeito vazio: {rect}")

        image = image.subsurface(bounds).copy()

        scale = min(
            max_width / image.get_width(),
            max_height / image.get_height()
        )

        size = (
            max(1, round(image.get_width() * scale)),
            max(1, round(image.get_height() * scale))
        )

        return pygame.transform.scale(image, size)

    # Raio da terceira linha do spritesheet.
    lightning = crop_effect(
        (890, 630, 205, 115),
        42,
        25
    )

    # Sequência de desaparecimento da quarta linha.
    death_rects = [
        (0, 750, 310, 274),
        (350, 750, 380, 274),
        (740, 750, 280, 274),
        (1020, 750, 260, 274),
    ]

    death_frames = [
        crop_effect(rect, 112, 96)
        for rect in death_rects
    ]

    return lightning, death_frames

def load_bone_bat_frames():
    """Seis poses completas do atlas exclusivo do morcego ósseo."""
    path = Path(__file__).resolve().parent / "assets" / "images" / "morcego_osseo_fase3_atlas.png"
    sheet = pygame.image.load(str(path)).convert_alpha()
    rects = ((12, 459, 325, 156), (347, 495, 318, 159),
             (676, 485, 314, 170), (1022, 459, 331, 191),
             (1380, 509, 296, 162), (1741, 520, 417, 151))
    frames = []
    scale = 125 / 417
    for rect in rects:
        frame = sheet.subsurface(rect).copy()
        frame = pygame.transform.smoothscale(frame, (round(rect[2] * scale), round(rect[3] * scale)))
        canvas = pygame.Surface((132, 96), pygame.SRCALPHA)
        canvas.blit(frame, frame.get_rect(center=(66, 48)))
        frames.append(canvas)
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
    "ground": (22, 101, 2130, 203),
    "grave_platform": (47, 396, 500, 119),
    "grave_moss": (577, 396, 432, 120),
    "grave_arch": (1058, 395, 490, 246),
    "grave_skull": (1601, 427, 176, 181),
    "grave_crate": (1790, 426, 178, 180),
    "grave_pillar": (1977, 396, 152, 244),
}

PHASE2_PLATFORM_ATLAS_PATH = (
    Path(__file__).resolve().parent
    / "assets"
    / "images"
    / "fase2_platforms_atlas.png"
)

PHASE2_ATLAS_RECTS = {
    "highway_ground": (16, 90, 2140, 190),
    "highway_platform": (17, 349, 480, 153),
    "highway_platform2": (544, 347, 480, 156),
    "highway_bottom": (18, 522, 480, 136),
    "highway_hazard": (543, 522, 480, 118),
    "highway_arch": (1053, 347, 494, 301),
    "highway_lightning": (1570, 431, 150, 165),
    "highway_bars": (1724, 431, 148, 165),
    "highway_crate": (1880, 431, 148, 165),
    "highway_pillar": (2042, 396, 114, 215),
}

PHASE1_PLATFORM_ATLAS_PATH = (
    Path(__file__).resolve().parent
    / "assets"
    / "images"
    / "fase1_plataforms_atlas.png"
)

PHASE1_ATLAS_RECTS = {
    "metal_ground": (22, 85, 2133, 191),
    "metal_platform": (40, 374, 477, 127),
    "metal_platform2": (572, 373, 537, 127),
    "metal_arch": (1150, 373, 474, 259),
    "metal_bottom": (40, 563, 421, 98),
    "metal_speaker": (518, 559, 392, 73),
    "metal_small": (907, 559, 189, 78),
    "metal_block": (1670, 430, 170, 148),
    "metal_lightning": (1839, 430, 140, 148),
    "metal_hazard": (2010, 447, 141, 90),
}

_phase3_platform_atlas = None
_phase2_platform_atlas = None
_phase1_platform_atlas = None

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

def load_phase1_platform_atlas():
    global _phase1_platform_atlas
    if _phase1_platform_atlas is None:
        _phase1_platform_atlas = pygame.image.load(
            str(PHASE1_PLATFORM_ATLAS_PATH)
        )
        if pygame.display.get_surface():
            _phase1_platform_atlas = (
                _phase1_platform_atlas.convert_alpha()
            )
    return _phase1_platform_atlas

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
        # Não desenha objetos fora da câmera
        if (
                r.right < -80
                or r.left > screen.get_width() + 80
        ):
            return
        # CHÃO
        if self.kind == "ground":

            if self.style == "metal":

                self.draw_phase1_atlas_sprite(
                    screen,
                    r,
                    "metal_ground"
                )
            elif self.style == "grave":
                self.draw_grave_ground(
                    screen,
                    r
                )
            elif self.style == "highway":
                self.draw_phase2_atlas_sprite(
                    screen,
                    r,
                    "highway_ground"
                )
            else:
                self.draw_ground(
                    screen,
                    r
                )
        # PLATAFORMAS DA FASE 1
        elif self.style.startswith("metal_"):

            self.draw_phase1_atlas_sprite(
                screen,
                r,
                self.style
            )
        # PLATAFORMAS DA FASE 3
        elif self.style.startswith("grave"):
            self.draw_grave_obstacle(
                screen,
                r
            )
        # PLATAFORMAS DA FASE 2
        elif self.style.startswith("highway"):
            self.draw_phase2_atlas_sprite(
                screen,
                r,
                self.style
            )
        # PLATAFORMAS ANTIGAS
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

    def draw_atlas_sprite(self, screen, r, atlas, source_rect):
        # Recorta o elemento do atlas.
        source = atlas.subsurface(source_rect).copy()
        # Identifica a região realmente visível.
        bounds = source.get_bounding_rect(min_alpha=20)

        if bounds.width == 0 or bounds.height == 0:
            return
        # Remove as margens transparentes.
        source = source.subsurface(bounds).copy()
        # Ajusta a imagem ao retângulo de colisão.
        sprite = pygame.transform.scale(
            source,
            (r.width, r.height)
        )
        # Imagem e colisão começam na mesma posição.
        screen.blit(sprite, r.topleft)

    def draw_phase3_atlas_sprite(self, screen, r, sprite_name):
        atlas = load_phase3_platform_atlas()
        source_rect = PHASE3_ATLAS_RECTS[sprite_name]
        self.draw_atlas_sprite(
            screen,
            r,
            atlas,
            source_rect
        )

    def draw_phase2_atlas_sprite(self, screen, r, sprite_name):
        atlas = load_phase2_platform_atlas()
        source_rect = PHASE2_ATLAS_RECTS[sprite_name]
        self.draw_atlas_sprite(
            screen,
            r,
            atlas,
            source_rect
        )

    def draw_phase1_atlas_sprite(
            self,
            screen,
            r,
            sprite_name
    ):
        atlas = load_phase1_platform_atlas()
        source_rect = PHASE1_ATLAS_RECTS[sprite_name]

        # Recorta o elemento original
        source = atlas.subsurface(
            source_rect
        ).copy()

        # Remove as margens transparentes
        bounds = source.get_bounding_rect(
            min_alpha=20
        )
        if bounds.width == 0 or bounds.height == 0:
            return
        source = source.subsurface(
            bounds
        ).copy()

        # Mantém a proporção original do sprite
        original_width = source.get_width()
        original_height = source.get_height()
        scale = r.width / original_width
        scaled_height = max(
            1,
            round(original_height * scale)
        )

        # O chão acompanha a altura da colisão
        if sprite_name == "metal_ground":
            scaled_height = r.height
        sprite = pygame.transform.scale(
            source,
            (
                r.width,
                scaled_height
            )
        )

        # A superfície superior coincide com a colisão
        destination = sprite.get_rect(
            midtop=r.midtop
        )
        screen.blit(
            sprite,
            destination
        )

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

    _sprites = None

    def __init__(self, x, y, phase_number=1):
        super().__init__()

        self.rect = pygame.Rect(x, y, 28, 42)
        self.collected = False
        self.phase_number = phase_number

        if Guitar._sprites is None:
            Guitar._sprites = self.load_sprites()

    @staticmethod
    def load_sprites():
        """Carrega os quatro instrumentos do spritesheet."""

        sprites = []
        for index in range(4):
            frame = collectible_frame(index)
            max_width, max_height = (80, 76) if index == 2 else (56, 72)
            scale = min(
                max_width / frame.get_width(),
                max_height / frame.get_height()
            )
            new_size = (
                max(1, round(frame.get_width() * scale)),
                max(1, round(frame.get_height() * scale))
            )
            frame = pygame.transform.smoothscale(frame, new_size)
            sprites.append(frame)
        return sprites

    def draw(self, screen, camera_x):
        if self.collected:
            return
        sprite_index = {
            1: 3,
            2: 0,
            3: 2
        }.get(self.phase_number, 0)
        image = self._sprites[sprite_index]
        draw_rect = image.get_rect(
            midbottom=(self.rect.centerx, self.rect.bottom + 4)
        )

        draw_rect.x -= camera_x
        screen.blit(image, draw_rect)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, min_x, max_x):
        super().__init__()
        self.rect = pygame.Rect(x, y, 46, 46)
        self.x = float(x)
        self.speed = 2
        self.min_x = min_x
        self.max_x = max_x
        self.alive = True

    def take_hit(self):
        if not self.alive:
            return
        image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        original_rect = self.rect
        self.rect = image.get_rect()
        self.draw(image, 0)
        self.rect = original_rect
        self.alive = False
        begin_defeat(self, image)

    def update(self):
        if not self.alive:
            update_defeat(self)
            return

        self.x += self.speed
        if self.x <= self.min_x or self.x + self.rect.width >= self.max_x:
            self.speed *= -1
            self.x += self.speed

        self.rect.x = round(self.x)

    def draw(self, screen, camera_x):
        if not self.alive:
            draw_defeat(self, screen, camera_x)
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


class SpiderEnemy(Enemy):
    """Aranha de contato que percorre um trecho inteiro de chão."""

    @staticmethod
    @lru_cache(maxsize=1)
    def load_frames():
        path = Path(__file__).resolve().parent / "assets" / "images" / "aranha_fase1.png"
        sheet = pygame.image.load(str(path)).convert_alpha()
        frames = []
        for index in range(4):
            left = round(index * sheet.get_width() / 4)
            right = round((index + 1) * sheet.get_width() / 4)
            frame = sheet.subsurface((left, 0, right - left, sheet.get_height()))
            frame = frame.subsurface(frame.get_bounding_rect(min_alpha=20)).copy()
            scale = min(96 / frame.get_width(), 54 / frame.get_height())
            frame = pygame.transform.smoothscale(
                frame, (round(frame.get_width() * scale), round(frame.get_height() * scale)))
            canvas = pygame.Surface((96, 54), pygame.SRCALPHA)
            canvas.blit(frame, frame.get_rect(midbottom=(48, 54)))
            frames.append(canvas)
        return frames

    def __init__(self, x, ground_y, min_x, max_x):
        super().__init__(x, ground_y - 50, min_x, max_x)
        self.rect.size = (96, 50)
        self.x = float(max(min_x, min(x, max_x - self.rect.width)))
        self.rect.x = round(self.x)
        self.speed = 1.6
        self.direction = -1
        self.animation_tick = 0
        self.frames = self.load_frames()

    def update(self):
        if not self.alive:
            update_defeat(self)
            return
        self.animation_tick += 1
        self.x += self.speed * self.direction
        if self.x <= self.min_x:
            self.x = float(self.min_x)
            self.direction = 1
        elif self.x >= self.max_x - self.rect.width:
            self.x = float(self.max_x - self.rect.width)
            self.direction = -1
        self.rect.x = round(self.x)

    def current_frame(self):
        frame = self.frames[(self.animation_tick // 7) % len(self.frames)]
        # O atlas original está olhando para a esquerda.
        return pygame.transform.flip(frame, True, False) if self.direction > 0 else frame

    def take_hit(self):
        if self.alive:
            self.alive = False
            begin_defeat(self, self.current_frame())

    def draw(self, screen, camera_x):
        if not self.alive:
            draw_defeat(self, screen, camera_x)
            return
        frame = self.current_frame()
        screen.blit(frame, frame.get_rect(midbottom=(self.rect.centerx - camera_x,
                                                      self.rect.bottom)))


class GoalInstrument:

    _image = None

    def __init__(self, x, y):
        if GoalInstrument._image is None:
            GoalInstrument._image = self.load_image()
        # O argumento ancora a base; desenho e área de coleta são iguais.
        self.rect = self._image.get_rect(midbottom=(x + 35, y + 90))

    @staticmethod
    def load_image():
        image = collectible_frame(1)
        scale = min(
            95 / image.get_width(),
            115 / image.get_height()
        )
        size = (
            max(1, round(image.get_width() * scale)),
            max(1, round(image.get_height() * scale))
        )

        return pygame.transform.scale(image, size)

    def draw(self, screen, camera_x):
        image = self._image
        draw_rect = self.rect.move(-camera_x, 0)
        screen.blit(image, draw_rect)

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
        self.hurt_timer = 0

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
            update_defeat(self)
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= 1

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
        self.hurt_timer = 16

        if self.health <= 0:

            self.alive = False
            self.projectiles.clear()
            image = self.frames[min(6, len(self.frames) - 1)]
            if self.direction < 0:
                image = pygame.transform.flip(image, True, False)
            begin_defeat(self, image)

    # ANIMAÇÃO

    def update_animation(self):

        self.animation_tick += 1

        if self.hurt_timer > 0:
            self.animation_index = min(6, len(self.frames) - 1)

        elif self.state == "dive":

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
            draw_defeat(self, screen, camera_x)
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

class BoneBatEnemy(FlyingEnemy):
    """
    Morcego ósseo da fase 3.

    Mantém as mecânicas do FlyingEnemy:
    - Patrulha aérea
    - Detecção do jogador
    - Investida
    - Disparo de projéteis
    """

    def __init__(self, x, y, min_x, max_x):
        super().__init__(x, y, min_x, max_x)
        self.frames = load_bone_bat_frames()
        # Um pouco mais rápido para aumentar o desafio.
        self.speed = 2.6
        # Distância de detecção.
        self.detection_range = 300
        # Velocidade dos disparos.
        self.projectile_speed = 5.5
        self.bone_sprite = pygame.Surface((34, 18), pygame.SRCALPHA)
        # Osso com haste e duas articulações, em vez de um losango.
        for color, radius, thickness in (((65, 55, 58), 5, 9),
                                         ((230, 221, 195), 3, 5)):
            pygame.draw.line(self.bone_sprite, color, (7, 9), (27, 9), thickness)
            for x in (5, 28):
                for y in (5, 12):
                    pygame.draw.circle(self.bone_sprite, color, (x, y), radius)
        pygame.draw.line(self.bone_sprite, (255, 247, 220), (9, 7), (24, 7), 2)

    def shoot(self, player):
        super().shoot(player)
        projectile = self.projectiles[-1]
        center = projectile["rect"].center
        projectile["rect"].size = (24, 12)
        projectile["rect"].center = center

    def draw(self, screen, camera_x):

        if not self.alive:
            draw_defeat(self, screen, camera_x)
            return

        # Desenha o morcego.
        frame = self.frames[self.animation_index]

        if self.direction < 0:
            frame = pygame.transform.flip(
                frame,
                True,
                False
            )

        draw_rect = frame.get_rect(
            center=self.rect.center
        )

        draw_rect.x -= camera_x
        screen.blit(frame, draw_rect)

        # O osso gira em torno do próprio centro durante o voo.
        for projectile in self.projectiles:
            angle = -pygame.Vector2(projectile["velocity"]).as_polar()[1]
            angle += (120 - projectile["lifetime"]) * 12
            image = pygame.transform.rotate(self.bone_sprite, angle)
            center = (projectile["rect"].centerx - camera_x, projectile["rect"].centery)
            screen.blit(image, image.get_rect(center=center))

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
            (192, 192)
        )

    # ATUALIZAÇÃO

    def update(self, player=None):
        if not self.alive:
            update_defeat(self)
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
        self.animation_index = 6

        # Interrompe a investida
        self.state = "patrol"

        if self.health <= 0:

            self.alive = False

            image = self.frames[7]
            if self.direction < 0:
                image = pygame.transform.flip(image, True, False)
            begin_defeat(self, image)

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
            draw_defeat(self, screen, camera_x)
            return

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

class CloudEnemy(FlyingEnemy):
    """
    Nuvem elétrica da fase 1.

    Mecânicas:
    - Patrulha aérea
    - Detecção do jogador
    - Investida
    - Disparo elétrico
    - Animação de derrota
    """

    def __init__(self, x, y, min_x, max_x):
        super().__init__(x, y, min_x, max_x)

        self.frames = load_cloud_frames()

        self.lightning_sprite, self.death_frames = load_cloud_effects()

        # Movimento da nuvem.
        self.speed = 1.8

        # A nuvem detecta o jogador a uma distância maior.
        self.detection_range = 320

        # Os relâmpagos são mais rápidos.
        self.projectile_speed = 6.5

        # Animação de derrota.
        self.death_timer = 0
        self.death_duration = 32

    def take_hit(self):
        """Recebe dano e inicia a animação de desaparecimento."""

        if not self.alive:
            return

        super().take_hit()

        if not self.alive:
            self.death_timer = self.death_duration

    def update(self, player=None):
        """Atualiza o comportamento ou a animação de derrota."""

        if not self.alive:

            if self.death_timer > 0:
                self.death_timer -= 1

            return

        super().update(player)

    def draw(self, screen, camera_x):
        """Desenha a nuvem, os efeitos e os relâmpagos."""

        # Animação de desaparecimento.
        if not self.alive:

            if self.death_timer <= 0:
                return

            progress = 1 - (
                self.death_timer / self.death_duration
            )

            index = min(
                int(progress * len(self.death_frames)),
                len(self.death_frames) - 1
            )

            frame = self.death_frames[index]

            rect = frame.get_rect(
                center=self.rect.center
            )

            rect.x -= camera_x

            screen.blit(frame, rect)

            return

        # Animação normal.
        frame = self.frames[self.animation_index]

        if self.direction < 0:
            frame = pygame.transform.flip(
                frame,
                True,
                False
            )

        draw_rect = frame.get_rect(
            center=self.rect.center
        )

        draw_rect.x -= camera_x

        screen.blit(frame, draw_rect)

        # Desenha os disparos elétricos.
        for projectile in self.projectiles:

            lightning = self.lightning_sprite

            # O disparo acompanha a direção horizontal.
            if projectile["velocity"].x < 0:
                lightning = pygame.transform.flip(
                    lightning,
                    True,
                    False
                )

            rect = lightning.get_rect(
                center=projectile["rect"].center
            )

            rect.x -= camera_x

            screen.blit(lightning, rect)
