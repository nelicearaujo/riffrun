from pathlib import Path

import pygame

from settings import *


PHASE3_SPRITESHEET_PATH = (
    Path(__file__).resolve().parent
    / "assets"
    / "images"
    / "metal_vocalist_phase3_spritesheet.png"
)
PHASE2_SPRITESHEET_PATH = (
    Path(__file__).resolve().parent
    / "assets"
    / "images"
    / "metal_vocalist_phase2_spritesheet.png"
)
PHASE1_SPRITESHEET_PATH = (
    Path(__file__).resolve().parent
    / "assets"
    / "images"
    / "metal_vocalist_phase1_spritesheet.png"
)
FRAME_CANVAS_SIZE = (110, 108)

FINAL_SPRITESHEET_PATH = Path(__file__).resolve().parent / "assets/images/personagem_fase_final.png"
FINAL_FRAME_RECTS = (
    (87, 15, 154, 329), (442, 12, 161, 332),
    (798, 24, 191, 320), (1151, 24, 219, 322),
    (52, 407, 235, 297), (452, 409, 184, 295),
    (756, 374, 269, 256), (1109, 392, 281, 307),
    (41, 783, 267, 295), (383, 778, 305, 300),
    (763, 773, 246, 304), (1158, 727, 222, 350),
)

# Recortes do spritesheet do personagem da FASE 1.
# Cada tupla representa (x, y, largura, altura).

PHASE1_FRAME_RECTS = (
    # 0 - Parado
    (55, 19, 140, 335),

    # 1 a 7 - Caminhando
    (392, 19, 155, 335),
    (554, 19, 122, 335),
    (702, 19, 166, 335),
    (900, 19, 148, 335),
    (1048, 19, 145, 335),
    (1193, 19, 151, 335),
    (1346, 19, 165, 335),

    # 8 e 9 - Pulando
    (1083, 360, 196, 340),
    (1299, 360, 187, 340),

    # 10 e 11 - Caindo
    (1083, 360, 196, 340),
    (1299, 360, 187, 340),

    # 12 a 14 - Atacando
    (29, 360, 230, 340),
    (264, 360, 271, 340),
    (753, 360, 250, 340),

    # 15 - Recebendo dano
    (207, 700, 190, 290),
    (630, 850, 330, 120),
)

# A folha da FASE 3 tem poses com espaçamento irregular. As caixas abaixo
# isolam cada personagem sem capturar partes da pose vizinha.
PHASE3_FRAME_RECTS = (
    (0, 0, 280, 330), (400, 0, 240, 330),
    (640, 0, 240, 330), (880, 0, 240, 330),
    (400, 0, 240, 330), (640, 0, 240, 330),
    (880, 0, 240, 330), (1080, 0, 240, 330),
    (1200, 330, 336, 340), (1200, 330, 336, 340),
    (930, 330, 280, 340), (930, 330, 280, 340),
    (0, 330, 380, 340), (400, 330, 280, 340),
    (650, 330, 270, 340), (230, 670, 245, 320),
    (770, 860, 310, 115),
)

PHASE2_FRAME_RECTS = (
    (75, 40, 175, 300), (284, 40, 160, 300),
    (501, 40, 170, 300), (697, 40, 176, 300),
    (905, 40, 175, 300), (1126, 41, 151, 299),
    (1319, 41, 163, 299), (697, 40, 176, 300),
    (1286, 369, 200, 266), (1066, 385, 173, 258),
    (1066, 385, 173, 258), (1286, 369, 200, 266),
    (44, 394, 274, 288), (280, 403, 234, 280),
    (512, 424, 207, 258), (234, 720, 188, 273),
    (634, 874, 325, 116),
)


def load_character_frames_from_rects(sheet_path, frame_rects):
    sheet = pygame.image.load(str(sheet_path))
    if pygame.display.get_surface():
        sheet = sheet.convert_alpha()

    cropped_frames = []
    for rect in frame_rects:
        frame = sheet.subsurface(rect).copy()
        # Elimina fragmentos de poses vizinhas que entram no recorte.
        mask = pygame.mask.from_surface(frame, threshold=127).connected_component()
        frame.blit(mask.to_surface(setcolor=(255, 255, 255, 255),
                                   unsetcolor=(255, 255, 255, 0)),
                   (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        bounds = frame.get_bounding_rect(min_alpha=10)
        cropped_frames.append(frame.subsurface(bounds).copy())

    # A pose parada usa a mesma altura nas três fases.
    scale = 96 / cropped_frames[0].get_height()
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

def load_phase1_character_frames():
    """Carrega as animações do vocalista da fase 1."""

    return load_character_frames_from_rects(
        PHASE1_SPRITESHEET_PATH,
        PHASE1_FRAME_RECTS,
    )

def load_phase2_character_frames():
    """Carrega as poses do vocalista exclusivo da FASE 2."""
    return load_character_frames_from_rects(
        PHASE2_SPRITESHEET_PATH,
        PHASE2_FRAME_RECTS,
    )


def load_phase3_character_frames():
    """Carrega as poses do vocalista exclusivo da FASE 3."""
    return load_character_frames_from_rects(
        PHASE3_SPRITESHEET_PATH,
        PHASE3_FRAME_RECTS,
    )


def load_final_character_frames():
    frames = load_character_frames_from_rects(FINAL_SPRITESHEET_PATH, FINAL_FRAME_RECTS)
    # A folha não tem pose deitada; deriva a queda da própria pose de dano.
    fallen = pygame.transform.rotate(frames[10], -90)
    fallen = fallen.subsurface(fallen.get_bounding_rect(min_alpha=10)).copy()
    canvas = pygame.Surface(FRAME_CANVAS_SIZE, pygame.SRCALPHA)
    canvas.blit(fallen, fallen.get_rect(midbottom=(55, 104)))
    frames.extend([frames[10]] * (16 - len(frames)))
    frames.append(canvas)
    return frames


def style_acdc_frames(frames):
    styled_frames = []
    for frame in frames:
        styled = frame.copy()
        for y in range(52, 90):
            for x in range(styled.get_width()):
                red, green, blue, alpha = styled.get_at((x, y))
                if alpha and red < 90 and green < 90 and blue < 90:
                    styled.set_at(
                        (x, y),
                        (max(24, red // 2), max(38, green // 2 + 20), min(150, blue + 50), alpha),
                    )
        styled_frames.append(styled)
    return styled_frames


class Player(pygame.sprite.Sprite):
    PHASE1_ANIMATIONS = {
        "idle": (0,),
        "walk": (1, 2, 3, 4, 5, 6, 7),
        "jump": (8, 9),
        "fall": (10, 11),
        "attack": (12, 13, 14),
        "hurt": (15,),
    }

    PHASE3_ANIMATIONS = {
        "idle": (0,),
        "walk": (1, 2, 3, 7),
        "jump": (8, 9),
        "fall": (10, 11),
        "attack": (12, 13, 14),
        "hurt": (15,),
    }

    PHASE2_ANIMATIONS = {
        "idle": (0,),
        "walk": (1, 2, 3, 7),
        "jump": (8, 9),
        "fall": (10, 11),
        "attack": (12, 13, 14),
        "hurt": (15,),
    }

    FINAL_ANIMATIONS = {
        "idle": (0, 1),
        "walk": (2, 3, 4, 5),
        "jump": (6,),
        "fall": (7,),
        "attack": (8, 9, 8),
        "hurt": (10,),
    }

    FRAME_SPEEDS = {
        "idle": 14,
        "walk": 7,
        "jump": 8,
        "fall": 9,
        "attack": 6,
        "hurt": 20,
    }

    def __init__(self, x, y, phase_number=1):
        super().__init__()

        self.phase_number = phase_number

        if phase_number == 1:
            self.frames = load_phase1_character_frames()
            self.animations = self.PHASE1_ANIMATIONS

        elif phase_number == 2:
            self.frames = load_phase2_character_frames()
            self.animations = self.PHASE2_ANIMATIONS

        elif phase_number == 3:
            self.frames = load_phase3_character_frames()
            self.animations = self.PHASE3_ANIMATIONS

        elif phase_number == 4:
            self.frames = load_final_character_frames()
            self.animations = self.FINAL_ANIMATIONS

        else:
            self.frames = load_phase1_character_frames()
            self.animations = self.PHASE1_ANIMATIONS

        self.image = self.frames[0]

        # A hitbox continua compacta e independente das poses mais abertas.
        self.rect = pygame.Rect(x, y, 48, 70)
        self.pos = pygame.Vector2(self.rect.x, self.rect.y)
        self.vel = pygame.Vector2(0, 0)

        self.on_ground = False
        self.facing = 1
        self.jump_strength = PLAYER_JUMP
        self.health = 3
        self.score = 0

        self.attack_timer = 0
        self.attack_cooldown = 20
        self.invulnerability = 0
        self.death_tick = 0
        self.death_velocity = 0

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
            self.vel.y = self.jump_strength
            self.on_ground = False

    def start_attack(self):
        if self.health > 0 and self.invulnerability <= 62 and self.attack_timer <= 0:
            self.attack_timer = self.attack_cooldown
            self.animation_state = "attack"
            self.animation_tick = 0
            self.animation_index = 0

    def get_attack_rect(self):
        if self.health <= 0 or self.invulnerability > 62:
            return None
        elapsed = self.attack_cooldown - self.attack_timer
        if self.attack_timer > 0 and 5 <= elapsed <= 12:
            if self.facing == 1:
                return pygame.Rect(self.rect.right - 3, self.rect.centery - 22, 62, 44)
            return pygame.Rect(self.rect.left - 59, self.rect.centery - 22, 62, 44)
        return None

    def take_damage(self):
        if self.health > 0 and self.invulnerability <= 0:
            self.health -= 1
            self.invulnerability = 80
            self.vel.y = -8
            self.animation_state = "hurt"
            self.animation_tick = 0
            self.animation_index = 0
            self.attack_timer = 0
            self.image = self.frames[self.animations["hurt"][0]]
            if self.health <= 0:
                self.death_velocity = -6

    def update_death(self, platforms):
        self.death_tick += 1
        self.animation_state = "dead"
        if self.death_tick < 10:
            self.image = self.frames[self.animations["hurt"][0]]
        else:
            self.image = self.frames[16] if len(self.frames) > 16 else self.frames[15]
        previous_bottom = self.rect.bottom
        self.death_velocity = min(18, self.death_velocity + GRAVITY)
        self.pos.y += self.death_velocity
        self.rect.y = round(self.pos.y)
        for platform in platforms:
            if (self.death_velocity >= 0 and previous_bottom <= platform.rect.top <= self.rect.bottom
                    and self.rect.right > platform.rect.left and self.rect.left < platform.rect.right):
                self.rect.bottom = platform.rect.top
                self.pos.y = self.rect.y
                self.death_velocity = 0
                break

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

        frames = self.animations[self.animation_state]
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
        if self.health <= 0:
            self.update_death(platforms)
            return
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

        if self.rect.right > LEVEL_WIDTH:
            self.rect.right = LEVEL_WIDTH
            self.pos.x = self.rect.x

        self.update_animation()

    def draw(self, screen, camera_x):
        if self.health > 0 and 0 < self.invulnerability <= 62 and (self.invulnerability // 5) % 2 == 0:
            return

        draw_rect = self.rect.move(-camera_x, 0)
        image = self.image if self.facing == 1 else pygame.transform.flip(
            self.image, True, False
        )
        visible_bounds = image.get_bounding_rect(min_alpha=10)
        sprite_rect = image.get_rect()
        sprite_rect.centerx = draw_rect.centerx
        sprite_rect.y = draw_rect.bottom - visible_bounds.bottom
        if self.phase_number == 3:
            sprite_rect.y += 3
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

    def draw_acdc_details(self, screen, sprite_rect):
        cap_y = sprite_rect.y + 14
        cap_center_x = sprite_rect.centerx
        pygame.draw.polygon(screen, (38, 38, 39), [
            (cap_center_x - 19, cap_y + 9), (cap_center_x - 13, cap_y),
            (cap_center_x + 10, cap_y - 1), (cap_center_x + 19, cap_y + 8),
            (cap_center_x + 9, cap_y + 13), (cap_center_x - 11, cap_y + 13),
        ])
        pygame.draw.line(screen, (87, 84, 78), (cap_center_x - 13, cap_y + 2),
                         (cap_center_x + 10, cap_y + 1), 3)
        bill_direction = self.facing
        pygame.draw.polygon(screen, (29, 29, 30), [
            (cap_center_x + bill_direction * 5, cap_y + 9),
            (cap_center_x + bill_direction * 22, cap_y + 11),
            (cap_center_x + bill_direction * 13, cap_y + 15),
        ])

        if self.animation_state in ("idle", "hurt"):
            hand_x = sprite_rect.centerx + self.facing * 24
            hand_y = sprite_rect.y + 56
            microphone_x = hand_x + self.facing * 8
            microphone_y = hand_y - 17
            pygame.draw.line(screen, (55, 57, 58), (hand_x, hand_y),
                             (microphone_x, microphone_y), 3)
            pygame.draw.circle(screen, (170, 174, 169), (microphone_x, microphone_y - 3), 5)
            pygame.draw.circle(screen, (43, 45, 46), (microphone_x, microphone_y - 3), 3)
