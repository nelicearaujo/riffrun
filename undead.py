"""Necromante e mortos invocados da fase 3."""
from functools import lru_cache
from pathlib import Path

import pygame

from objects import begin_defeat, update_defeat, draw_defeat
from settings import GROUND_Y


@lru_cache(maxsize=None)
def undead_frames(necromancer):
    path = Path(__file__).resolve().parent / "assets" / "images"
    filename = "necromante_fase3.png" if (path / "necromante_fase3.png").exists() else "necromante.png"
    sheet = pygame.image.load(str(path / filename)).convert_alpha()
    if necromancer:
        rects = ((1549, 495, 190, 334), (695, 86, 226, 332),
                 (19, 468, 220, 354), (234, 476, 222, 346),
                 (466, 475, 235, 349), (1417, 73, 345, 343),
                 (695, 86, 226, 332), (930, 86, 232, 331))
        scale = 96 / 354
    else:
        rects = ((44, 84, 172, 334), (263, 87, 177, 332),
                 (469, 87, 198, 331), (1162, 86, 260, 330),
                 (686, 658, 239, 192), (932, 497, 279, 348))
        scale = 80 / 334
    frames = []
    for rect in rects:
        image = sheet.subsurface(rect).copy()
        mask = pygame.mask.from_surface(image, 127).connected_component()
        image.blit(mask.to_surface(setcolor=(255, 255, 255, 255),
                                   unsetcolor=(255, 255, 255, 0)),
                   (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        frames.append(pygame.transform.smoothscale(
            image, (round(rect[2] * scale), round(rect[3] * scale))))
    return frames


class ZombieEnemy:
    def __init__(self, x, min_x, max_x, emerging=False):
        self.rect = pygame.Rect(x, GROUND_Y - 70, 40, 70)
        self.x = float(x)
        self.min_x, self.max_x = min_x, max_x
        self.direction = -1
        self.alive = True
        self.health = 1
        self.tick = 0
        self.emerge_timer = 45 if emerging else 0
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.moving = False
        self.frames = undead_frames(False)

    @property
    def can_damage(self):
        return self.emerge_timer == 0

    def frame(self):
        if self.emerge_timer:
            return self.frames[5]
        if self.attack_timer:
            return self.frames[3]
        return self.frames[1 + (self.tick // 10) % 2] if self.moving else self.frames[0]

    def update(self, player=None):
        if not self.alive:
            update_defeat(self)
            return
        self.tick += 1
        self.moving = False
        if self.emerge_timer:
            self.emerge_timer -= 1
            return
        if self.attack_cooldown:
            self.attack_cooldown -= 1
        if self.attack_timer:
            self.attack_timer -= 1
            return
        distance = None if player is None else player.rect.centerx - self.rect.centerx
        chasing = (distance is not None and abs(distance) < 420
                   and self.min_x <= player.rect.centerx <= self.max_x
                   and abs(player.rect.bottom - self.rect.bottom) < 120)
        if chasing:
            if abs(distance) > 8:
                self.direction = 1 if distance > 0 else -1
            if abs(distance) < 85 and abs(player.rect.bottom - self.rect.bottom) < 90:
                if not self.attack_cooldown:
                    self.attack_timer = 38
                    self.attack_cooldown = 90
                return
        self.x += self.direction * 1.2
        self.x = max(self.min_x, min(self.x, self.max_x - self.rect.width))
        if not chasing:
            if self.x <= self.min_x:
                self.direction = 1
            elif self.x >= self.max_x - self.rect.width:
                self.direction = -1
        self.moving = self.rect.x != round(self.x)
        self.rect.x = round(self.x)

    def get_attack_rect(self):
        if self.alive and 10 <= self.attack_timer <= 19:
            x = self.rect.right - 4 if self.direction > 0 else self.rect.left - 32
            return pygame.Rect(x, self.rect.y + 12, 36, 36)
        return None

    def take_hit(self):
        if self.alive:
            self.alive = False
            self.health = 0
            image = self.frames[4]
            if self.direction < 0:
                image = pygame.transform.flip(image, True, False)
            begin_defeat(self, image)

    def draw(self, screen, camera_x):
        if not self.alive:
            draw_defeat(self, screen, camera_x)
            return
        image = self.frame()
        if self.direction < 0:
            image = pygame.transform.flip(image, True, False)
        rect = image.get_rect(midbottom=(self.rect.centerx - camera_x, self.rect.bottom))
        if self.emerge_timer:
            rect.y += round(image.get_height() * self.emerge_timer / 45)
        old_clip = screen.get_clip()
        screen.set_clip(old_clip.clip(pygame.Rect(0, 0, screen.get_width(), GROUND_Y)))
        screen.blit(image, rect)
        screen.set_clip(old_clip)
        if self.attack_timer > 19:
            pygame.draw.circle(screen, (230, 135, 75),
                               (self.rect.centerx - camera_x, self.rect.y - 10), 4)


class NecromancerEnemy:
    MAX_SUMMONS = 4

    def __init__(self, x, min_x, max_x):
        self.rect = pygame.Rect(x, GROUND_Y - 90, 46, 90)
        self.x = float(x)
        self.min_x, self.max_x = min_x, max_x
        self.direction = -1
        self.alive = True
        self.health = 3
        self.hurt_timer = 0
        self.cast_timer = 0
        self.cooldown = 90
        self.tick = 0
        self.alerted = False
        self.moving = False
        self.walk_tick = 0
        self.draw_book_timer = 0
        self.spawn_x = x
        self.summons = []
        self.pending_summons = []
        self.frames = undead_frames(True)
        self.projectiles = []
        self.spell_timer = 0
        self.spell_cooldown = 150
        self.spell_target = pygame.Vector2()

    def frame(self):
        if self.hurt_timer:
            return self.frames[5]
        if self.spell_timer:
            return self.frames[4 if self.spell_timer > 12 else 5]
        if self.cast_timer:
            return self.frames[2 + min(2, (60 - self.cast_timer) // 20)]
        if self.draw_book_timer:
            return self.frames[0 if self.draw_book_timer > 16 else
                               (2 if self.draw_book_timer > 8 else 3)]
        if self.moving:
            return self.frames[6 + (self.walk_tick // 7) % 2]
        return self.frames[2] if self.alerted else self.frames[0]

    def update(self, player=None):
        if not self.alive:
            update_defeat(self)
            return
        self.tick += 1
        self.moving = False
        for projectile in self.projectiles[:]:
            projectile["pos"] += projectile["velocity"]
            projectile["rect"].center = (round(projectile["pos"].x), round(projectile["pos"].y))
            projectile["lifetime"] -= 1
            if projectile["lifetime"] <= 0:
                self.projectiles.remove(projectile)
        self.spell_cooldown = max(0, self.spell_cooldown - 1)
        self.summons = [z for z in self.summons if z.alive]
        if self.hurt_timer:
            self.hurt_timer -= 1
            return
        if self.draw_book_timer:
            self.draw_book_timer -= 1
            return
        if self.spell_timer:
            self.spell_timer -= 1
            if self.spell_timer == 0:
                origin = pygame.Vector2(self.rect.centerx + self.direction * 25, self.rect.y + 28)
                velocity = self.spell_target - origin
                if velocity.length_squared() == 0:
                    velocity = pygame.Vector2(self.direction, 0)
                rect = pygame.Rect(0, 0, 18, 18)
                rect.center = (round(origin.x), round(origin.y))
                self.projectiles.append({"pos": origin, "velocity": velocity.normalize() * 4.5,
                                         "rect": rect, "lifetime": 130})
                self.spell_cooldown = 240
            return
        if self.cast_timer:
            self.cast_timer -= 1
            if self.cast_timer == 0:
                zombie = ZombieEnemy(self.spawn_x, self.min_x, self.max_x, emerging=True)
                self.summons.append(zombie)
                self.pending_summons.append(zombie)
                self.cooldown = 210
            return
        if player is None or abs(player.rect.centerx - self.rect.centerx) > 700:
            return
        if not self.alerted:
            self.alerted = True
            self.draw_book_timer = 24
            return
        distance = player.rect.centerx - self.rect.centerx
        toward_player = 1 if distance > 0 else -1
        self.direction = toward_player
        if not self.spell_cooldown:
            self.spell_target = pygame.Vector2(player.rect.center)
            self.spell_timer = 36
            return
        if abs(distance) < 260:
            previous_x = self.x
            self.x -= toward_player * 2.2
            self.x = max(self.min_x, min(self.x, self.max_x - self.rect.width))
            self.rect.x = round(self.x)
            self.moving = self.x != previous_x
            if self.moving:
                self.direction = -toward_player
                self.walk_tick += 1
        self.cooldown = max(0, self.cooldown - 1)
        if not self.cooldown and len(self.summons) < self.MAX_SUMMONS:
            self.direction = toward_player
            self.moving = False
            self.spawn_x = max(self.min_x, min(player.rect.centerx - toward_player * 110,
                                              self.max_x - 40))
            self.cast_timer = 60

    def take_hit(self):
        if not self.alive or self.hurt_timer:
            return
        self.health -= 1
        self.hurt_timer = 22
        self.cast_timer = 0
        self.spell_timer = 0
        self.spell_cooldown = max(90, self.spell_cooldown)
        self.cooldown = 90
        if self.health <= 0:
            self.alive = False
            self.pending_summons.clear()
            self.projectiles.clear()
            image = self.frames[5]
            if self.direction < 0:
                image = pygame.transform.flip(image, True, False)
            begin_defeat(self, image)

    def draw(self, screen, camera_x):
        if not self.alive:
            draw_defeat(self, screen, camera_x)
            return
        image = self.frame()
        if self.direction < 0:
            image = pygame.transform.flip(image, True, False)
        if self.hurt_timer:
            image = image.copy()
            image.fill((255, 135, 135, 255), special_flags=pygame.BLEND_RGBA_MULT)
        rect = image.get_rect(midbottom=(self.rect.centerx - camera_x, self.rect.bottom))
        screen.blit(image, rect)
        bar = pygame.Rect(self.rect.centerx - camera_x - 28, rect.top - 13, 56, 6)
        pygame.draw.rect(screen, (40, 15, 25), bar)
        pygame.draw.rect(screen, (160, 90, 215), (bar.x, bar.y, round(56 * self.health / 3), 6))
        if self.spell_timer:
            center = (self.rect.centerx - camera_x + self.direction * 25, self.rect.y + 28)
            pygame.draw.circle(screen, (180, 105, 245), center, 6 + (36 - self.spell_timer) // 6, 2)
        for projectile in self.projectiles:
            center = (projectile["rect"].centerx - camera_x, projectile["rect"].centery)
            pygame.draw.circle(screen, (65, 30, 105), center, 12)
            pygame.draw.circle(screen, (175, 95, 235), center, 9)
            pygame.draw.circle(screen, (235, 220, 255), center, 4)
        if self.cast_timer:
            x = self.spawn_x + 20 - camera_x
            pygame.draw.ellipse(screen, (175, 105, 230), (x - 28, GROUND_Y - 8, 56, 12), 2)
            for offset in (-16, 0, 16):
                pygame.draw.line(screen, (130, 85, 180),
                                 (x + offset, GROUND_Y - 5),
                                 (x + offset, GROUND_Y - 16 - self.tick % 12), 2)
