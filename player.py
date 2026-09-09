from pathlib import Path

import pygame

from settings import *


SPRITESHEET_PATH = (
    Path(__file__).resolve().parent
    / "assets"
    / "images"
    / "metal_vocalist_spritesheet_final.png"
)
SPRITE_GRID = 4
FRAME_CANVAS_SIZE = (110, 108)


def load_character_frames():
    """Divide a folha 4x4 e mantém a mesma escala em todos os quadros."""
    sheet = pygame.image.load(str(SPRITESHEET_PATH))
    if pygame.display.get_surface():
        sheet = sheet.convert_alpha()

    sheet_width, sheet_height = sheet.get_size()
    cropped_frames = []

    for row in range(SPRITE_GRID):
        top = round(row * sheet_height / SPRITE_GRID)
        bottom = round((row + 1) * sheet_height / SPRITE_GRID)
        for column in range(SPRITE_GRID):
            left = round(column * sheet_width / SPRITE_GRID)
            right = round((column + 1) * sheet_width / SPRITE_GRID)
            frame = sheet.subsurface((left, top, right - left, bottom - top)).copy()
            bounds = frame.get_bounding_rect(min_alpha=10)
            cropped_frames.append(frame.subsurface(bounds).copy())

    max_height = max(frame.get_height() for frame in cropped_frames)
    # A altura governa a escala para que ataques largos não encolham o personagem.
    scale = 98 / max_height
    frames = []

    for cropped in cropped_frames:
        scaled_size = (
            max(1, round(cropped.get_width() * scale)),
            max(1, round(cropped.get_height() * scale)),
        )
        scaled = pygame.transform.scale(cropped, scaled_size)
        canvas = pygame.Surface(FRAME_CANVAS_SIZE, pygame.SRCALPHA)
        destination = scaled.get_rect(
            midbottom=(FRAME_CANVAS_SIZE[0] // 2, FRAME_CANVAS_SIZE[1] - 4)
        )
        canvas.blit(scaled, destination)
        frames.append(canvas)

    return frames


class Player(pygame.sprite.Sprite):
    ANIMATIONS = {
        "idle": (0, 1, 2, 3),
        "walk": (4, 5, 6, 7),
        "jump": (8, 9),
        "fall": (10, 11),
        "attack": (12, 13, 14),
        "hurt": (15,),
    }

    FRAME_SPEEDS = {
        "idle": 14,
        "walk": 7,
        "jump": 8,
        "fall": 9,
        "attack": 6,
        "hurt": 20,
    }

    def __init__(self, x, y):
        super().__init__()

        self.frames = load_character_frames()
        self.image = self.frames[0]

        # A hitbox continua compacta e independente das poses mais abertas.
        self.rect = pygame.Rect(x, y, 48, 70)
        self.pos = pygame.Vector2(self.rect.x, self.rect.y)
        self.vel = pygame.Vector2(0, 0)

        self.on_ground = False
        self.facing = 1
        self.health = 3
        self.score = 0

        self.attack_timer = 0
        self.attack_cooldown = 20
        self.invulnerability = 0

        self.animation_state = "idle"
        self.animation_tick = 0
        self.animation_index = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()

        self.vel.x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel.x = -PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel.x = PLAYER_SPEED
            self.facing = 1

        if (
            keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
        ) and self.on_ground:
            self.vel.y = PLAYER_JUMP
            self.on_ground = False

    def start_attack(self):
        if self.attack_timer <= 0:
            self.attack_timer = self.attack_cooldown
            self.animation_state = "attack"
            self.animation_tick = 0
            self.animation_index = 0

    def get_attack_rect(self):
        elapsed = self.attack_cooldown - self.attack_timer
        if self.attack_timer > 0 and 5 <= elapsed <= 12:
            if self.facing == 1:
                return pygame.Rect(self.rect.right - 3, self.rect.centery - 22, 62, 44)
            return pygame.Rect(self.rect.left - 59, self.rect.centery - 22, 62, 44)
        return None

    def take_damage(self):
        if self.invulnerability <= 0:
            self.health -= 1
            self.invulnerability = 80
            self.vel.y = -8
            self.animation_state = "hurt"
            self.animation_tick = 0
            self.animation_index = 0

    def choose_animation_state(self):
        if self.invulnerability > 62:
            return "hurt"
        if self.attack_timer > 0:
            return "attack"
        if not self.on_ground:
            return "jump" if self.vel.y < 0 else "fall"
        if abs(self.vel.x) > 0.1:
            return "walk"
        return "idle"

    def update_animation(self):
        new_state = self.choose_animation_state()
        if new_state != self.animation_state:
            self.animation_state = new_state
            self.animation_tick = 0
            self.animation_index = 0

        frames = self.ANIMATIONS[self.animation_state]
        if self.animation_state == "attack":
            elapsed = self.attack_cooldown - self.attack_timer
            self.animation_index = min(len(frames) - 1, elapsed // 6)
        else:
            self.animation_tick += 1
            if self.animation_tick >= self.FRAME_SPEEDS[self.animation_state]:
                self.animation_tick = 0
                self.animation_index = (self.animation_index + 1) % len(frames)

        self.image = self.frames[frames[self.animation_index]]

    def update(self, platforms):
        self.handle_input()

        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.invulnerability > 0:
            self.invulnerability -= 1

        self.vel.y += GRAVITY
        if self.vel.y > 18:
            self.vel.y = 18

        self.pos.x += self.vel.x
        self.rect.x = round(self.pos.x)

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel.x < 0:
                    self.rect.left = platform.rect.right
                self.pos.x = self.rect.x

        self.pos.y += self.vel.y
        self.rect.y = round(self.pos.y)
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel.y = 0
                self.pos.y = self.rect.y

        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.x

        self.update_animation()

    def draw(self, screen, camera_x):
        if self.invulnerability > 0 and (self.invulnerability // 5) % 2 == 0:
            return

        draw_rect = self.rect.move(-camera_x, 0)
        image = self.image if self.facing == 1 else pygame.transform.flip(
            self.image, True, False
        )
        sprite_rect = image.get_rect(midbottom=(draw_rect.centerx, draw_rect.bottom + 4))
        screen.blit(image, sprite_rect)

        attack_rect = self.get_attack_rect()
        if attack_rect:
            attack_draw = attack_rect.move(-camera_x, 0)
            arc_rect = pygame.Rect(attack_draw)
            arc_rect.inflate_ip(-12, -4)
            if self.facing == 1:
                pygame.draw.arc(screen, (92, 205, 231), arc_rect, -1.15, 1.15, 5)
                pygame.draw.arc(screen, (232, 239, 231), arc_rect, -1.0, 1.0, 2)
            else:
                pygame.draw.arc(screen, (92, 205, 231), arc_rect, 2.0, 4.3, 5)
                pygame.draw.arc(screen, (232, 239, 231), arc_rect, 2.15, 4.15, 2)
