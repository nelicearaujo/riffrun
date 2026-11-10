"""Sprites e colisões dos perigos da fase de parkour."""
from functools import lru_cache
from pathlib import Path

import pygame

from settings import GROUND_Y, HEIGHT, WIDTH


@lru_cache(maxsize=None)
def load_hazard_image(name, width):
    path = Path(__file__).resolve().parent / "assets" / "images" / name
    image = pygame.image.load(str(path)).convert_alpha()
    image = image.subsurface(image.get_bounding_rect(min_alpha=20)).copy()
    height = max(1, round(image.get_height() * width / image.get_width()))
    return pygame.transform.scale(image, (width, height))


def sprite_hits(mask, sprite_rect, rect):
    overlap = rect.clip(sprite_rect)
    if not overlap.width or not overlap.height:
        return False
    return mask.overlap(
        pygame.mask.Mask(overlap.size, fill=True),
        (overlap.x - sprite_rect.x, overlap.y - sprite_rect.y),
    ) is not None


class SpikeStrip:
    def __init__(self, x, platform_y, width=64):
        self.image = load_hazard_image("espinhos_fase2.png", width)
        self.rect = self.image.get_rect(bottomleft=(x, platform_y))
        self.mask = pygame.mask.from_surface(self.image)

    def hits(self, rect):
        return sprite_hits(self.mask, self.rect, rect)

    def draw(self, screen, camera_x):
        screen.blit(self.image, self.rect.move(-camera_x, 0))


class FireJet:
    CYCLE = 240
    WARNING = 115
    ERUPTION = 165

    def __init__(self, x, height, offset):
        self.x, self.height, self.offset = x, height, offset
        self.tick = 0
        self.image = load_hazard_image("foguinho_fase2.png", 42)
        self.falling_image = pygame.transform.flip(self.image, False, True)
        self.mask = pygame.mask.from_surface(self.image)
        self.falling_mask = pygame.mask.from_surface(self.falling_image)

    def update(self, tick):
        self.tick = (tick + self.offset) % self.CYCLE

    @property
    def flame_height(self):
        if self.tick < self.ERUPTION:
            return 0
        progress = (self.tick - self.ERUPTION) / (self.CYCLE - self.ERUPTION)
        return round(4 * self.height * progress * (1 - progress))

    @property
    def rect(self):
        return self.image.get_rect(midtop=(self.x, GROUND_Y - self.flame_height))

    @property
    def falling(self):
        return self.tick > (self.ERUPTION + self.CYCLE) // 2

    def hits(self, rect):
        if not self.flame_height:
            return False
        # Só o fogo causa dano, sem uma coluna invisível abaixo dele.
        visible = rect.clip(pygame.Rect(self.x - 30, 0, 60, GROUND_Y))
        mask = self.falling_mask if self.falling else self.mask
        return sprite_hits(mask, self.rect, visible)

    def draw(self, screen, camera_x):
        x = self.x - camera_x
        if self.WARNING <= self.tick < self.ERUPTION:
            pygame.draw.circle(screen, (255, 225, 90), (x, GROUND_Y - 5),
                               6 + (self.tick // 5) % 5, 2)
            pygame.draw.line(screen, (255, 200, 70),
                             (x, GROUND_Y - 32), (x, GROUND_Y - 18), 3)
        if self.flame_height:
            old_clip = screen.get_clip()
            screen.set_clip(old_clip.clip(pygame.Rect(0, 0, WIDTH, GROUND_Y)))
            image = self.falling_image if self.falling else self.image
            screen.blit(image, self.rect.move(-camera_x, 0))
            screen.set_clip(old_clip)


def draw_lava(screen, camera_x, tick):
    tile = load_hazard_image("lava_fase2.png", 640)
    old_clip = screen.get_clip()
    screen.set_clip(old_clip.clip(pygame.Rect(0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y)))
    start_x = -int(camera_x + tick * 0.35) % tile.get_width() - tile.get_width()
    for x in range(start_x, WIDTH, tile.get_width()):
        screen.blit(tile, (x, GROUND_Y - 10))
    screen.set_clip(old_clip)
