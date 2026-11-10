"""Arena final e os três estágios do duelo contra Gustavo."""
import math
from functools import lru_cache
from pathlib import Path

import pygame

from objects import Platform, begin_defeat, update_defeat, draw_defeat
from scoring import RunScore
from settings import WIDTH, HEIGHT, GROUND_Y, FPS


@lru_cache(maxsize=1)
def boss_frames():
    sheet = pygame.image.load(str(Path(__file__).resolve().parent / "assets/images/chefe_final.png")).convert_alpha()
    rects = ((80, 20, 208, 415), (405, 34, 259, 401), (775, 35, 168, 400),
             (1051, 57, 313, 376), (1418, 136, 341, 299), (26, 509, 332, 348),
             (392, 497, 298, 360), (714, 488, 342, 369),
             (1112, 503, 264, 350), (1429, 582, 293, 259))
    scale = 104 / 415
    return [pygame.transform.smoothscale(sheet.subsurface(rect),
            (round(rect[2] * scale), round(rect[3] * scale))) for rect in rects]


@lru_cache(maxsize=1)
def boss_attack_frames():
    path = Path(__file__).resolve().parent / "assets/images/ataques_chefe_final.png"
    sheet = pygame.image.load(str(path)).convert_alpha()
    families = {}
    for name, top, bottom, size in (("wave", 0, 256, (110, 90)),
                                    ("microphone", 256, 480, (72, 56)),
                                    ("flame", 480, 752, (100, 145)),
                                    ("impact", 752, 1024, (100, 90))):
        crops = []
        for column in range(3):
            frame = sheet.subsurface((column * 512, top, 512, bottom - top))
            frame = frame.subsurface(frame.get_bounding_rect(min_alpha=200 if name == "flame" else 20)).copy()
            crops.append(frame)
        if name == "flame":
            families[name] = []
            for index, frame in enumerate(crops):
                height = 40 if index == 0 else 135
                width = round(frame.get_width() * height / frame.get_height())
                families[name].append(pygame.transform.smoothscale(frame, (width, height)))
            continue
        scale = min(size[0] / max(f.get_width() for f in crops),
                    size[1] / max(f.get_height() for f in crops))
        families[name] = [pygame.transform.smoothscale(frame,
            (max(1, round(frame.get_width() * scale)), max(1, round(frame.get_height() * scale))))
            for frame in crops]
    return families


@lru_cache(maxsize=1)
def boss_interface_images():
    directory = Path(__file__).resolve().parent / "assets/images"
    source = pygame.image.load(str(directory / "barra_vida_chefe_final.png")).convert_alpha()
    bounds = source.get_bounding_rect(min_alpha=20)
    # A moldura inteira cabe abaixo do piso, sem cobrir os pés dos lutadores.
    scale = 380 / bounds.width
    size = (380, round(bounds.height * scale))
    bars = []
    for health in range(GustavoBoss.MAX_HEALTH + 1):
        panel = source.subsurface(bounds).copy()
        # Preenche apenas o interior preto, preservando a moldura e o nome da arte.
        field = pygame.Rect(230 - bounds.x, 361 - bounds.y, 1710, 100)
        filled_width = round(field.width * health / GustavoBoss.MAX_HEALTH)
        if filled_width:
            for row in range(field.height):
                color = (225 - row * 65 // field.height, 65 - row * 35 // field.height, 42)
                pygame.draw.line(panel, color, (field.x, field.y + row),
                                 (field.x + filled_width - 1, field.y + row))
        bars.append(pygame.transform.smoothscale(panel, size))

    words = pygame.image.load(str(directory / "palavras_batalha.png")).convert_alpha()
    banners = []
    for row, max_width, max_height in ((0, 600, 155), (1, 420, 135)):
        frame = words.subsurface((0, row * 512, words.get_width(), 512))
        frame = frame.subsurface(frame.get_bounding_rect(min_alpha=20)).copy()
        ratio = min(max_width / frame.get_width(), max_height / frame.get_height())
        banners.append(pygame.transform.smoothscale(frame,
                       (round(frame.get_width() * ratio), round(frame.get_height() * ratio))))
    return bars, banners


class GustavoBoss:
    MAX_HEALTH = 12
    INTRO_WALK = 80
    INTRO_POSE = 65
    INTRO_FIGHT = 35

    def __init__(self, intro_duration_ms=3000):
        self.rect = pygame.Rect(1320, GROUND_Y - 78, 48, 78)
        self.x = float(self.rect.x)
        self.direction = -1
        self.health = self.MAX_HEALTH
        self.alive = True
        self.intro_duration_ms = intro_duration_ms
        self.intro_elapsed_ms = 0
        self.intro_frames = max(3, round(intro_duration_ms * FPS / 1000))
        self.INTRO_WALK = max(1, round(self.intro_frames * 80 / 180))
        self.INTRO_POSE = max(1, round(self.intro_frames * 65 / 180))
        self.INTRO_FIGHT = self.intro_frames - self.INTRO_WALK - self.INTRO_POSE
        self.intro_timer = self.intro_frames
        self.hurt_timer = 0
        self.tick = 0
        self.state = "idle"
        self.timer = 0
        self.cooldown = 65
        self.attack_count = 0
        self.projectiles = []
        self.frames = boss_frames()
        self.target = pygame.Vector2()
        self.walking = False
        self.attack_frames = boss_attack_frames()
        self.impacts = []
        self.falling_marks = []
        self.ground_wave_frames = [pygame.transform.smoothscale(frame,
            (round(frame.get_width() * 44 / frame.get_height()), 44))
            for frame in self.attack_frames["wave"]]

    def start_rain(self):
        # Quedas espaçadas e posições fixas deixam corredores para desviar.
        positions = (220, 470, 790, 1060) if self.attack_count % 2 else (300, 550, 880, 1110)
        self.falling_marks = [{"x": x, "delay": 45 + index * 14}
                              for index, x in enumerate(positions)]

    def remove_falling_mark(self, projectile):
        mark = projectile.get("drop_marker")
        if mark in self.falling_marks:
            self.falling_marks.remove(mark)

    def on_projectile_hit(self, projectile):
        self.impacts.append({"pos": projectile["rect"].center, "age": 0})
        self.remove_falling_mark(projectile)

    @property
    def stage(self):
        return 1 if self.health > 8 else (2 if self.health > 4 else 3)

    @property
    def can_damage(self):
        return (self.intro_timer == 0 and self.alive
                and self.state not in ("recover", "hurt"))

    def get_attack_rect(self):
        if self.state == "microphone" and self.timer > 3 and self.alive:
            x = self.rect.right - 5 if self.direction > 0 else self.rect.left - 75
            return pygame.Rect(x, self.rect.y + 15, 80, 65)
        return None

    def take_hit(self):
        if not self.alive or self.intro_timer or self.hurt_timer:
            return
        self.health -= 1
        self.impacts.append({"pos": self.rect.center, "age": 0})
        self.hurt_timer = 24
        self.state = "hurt"
        self.falling_marks = [mark for mark in self.falling_marks if mark["delay"] <= 0]
        self.timer = 20
        self.cooldown = 45
        if self.health <= 0:
            self.alive = False
            self.projectiles.clear()
            self.falling_marks.clear()
            image = self.frames[9]
            if self.direction < 0:
                image = pygame.transform.flip(image, True, False)
            begin_defeat(self, image)

    def update(self, player=None, intro_elapsed_ms=None):
        if not self.alive:
            update_defeat(self)
            return
        self.tick += 1
        self.walking = False
        for impact in self.impacts:
            impact["age"] += 1
        self.impacts = [impact for impact in self.impacts if impact["age"] < 15]
        for mark in self.falling_marks:
            if mark["delay"] > 0:
                mark["delay"] -= 1
                if mark["delay"] == 0:
                    rect = pygame.Rect(0, 0, 28, 34)
                    rect.center = (mark["x"], -30)
                    self.projectiles.append({"rect": rect, "pos": pygame.Vector2(rect.center),
                        "velocity": pygame.Vector2(0, 11), "lifetime": 140,
                        "kind": "falling", "drop_marker": mark})
        for projectile in self.projectiles[:]:
            ground_wave = projectile.get("kind") == "ground_wave"
            if not ground_wave:
                projectile["velocity"].y += 0.12
            projectile["pos"] += projectile["velocity"]
            projectile["rect"].center = (round(projectile["pos"].x), round(projectile["pos"].y))
            projectile["lifetime"] -= 1
            if not ground_wave and projectile["rect"].bottom >= GROUND_Y:
                self.impacts.append({"pos": (projectile["rect"].centerx, GROUND_Y - 18), "age": 0})
                self.projectiles.remove(projectile)
                self.remove_falling_mark(projectile)
            elif (projectile["lifetime"] <= 0 or projectile["rect"].top > HEIGHT
                  or projectile["rect"].right < -60 or projectile["rect"].left > WIDTH + 60):
                self.projectiles.remove(projectile)
                self.remove_falling_mark(projectile)
        if self.intro_timer:
            self.intro_elapsed_ms = (self.intro_elapsed_ms + 1000 / FPS
                                     if intro_elapsed_ms is None else intro_elapsed_ms)
            elapsed_frames = min(self.intro_frames, round(self.intro_elapsed_ms * FPS / 1000))
            self.intro_timer = max(1, self.intro_frames - elapsed_frames)
            if self.intro_elapsed_ms + 0.001 >= self.intro_duration_ms:
                self.intro_timer = 0
            progress = min(1, elapsed_frames / self.INTRO_WALK)
            self.x = 1320 - 320 * progress
            self.rect.x = round(self.x)
            if self.intro_timer >= self.INTRO_POSE + self.INTRO_FIGHT:
                self.walking = True
            return
        if self.hurt_timer:
            self.hurt_timer -= 1
        if self.timer:
            self.timer -= 1
            if self.state == "microphone":
                self.x += self.direction * (7 if self.stage == 3 else 5)
                self.x = max(65, min(WIDTH - 125, self.x))
                self.rect.x = round(self.x)
            if not self.timer:
                if self.state == "windup_mic":
                    self.state, self.timer = "microphone", 18
                elif self.state == "windup_rain":
                    self.start_rain()
                    self.state, self.timer = "rain", 150
                elif self.state == "rain":
                    self.state, self.timer = "recover", 65
                elif self.state == "windup_wave":
                    origin = pygame.Vector2(self.rect.centerx + self.direction * 60, GROUND_Y - 20)
                    rect = pygame.Rect(0, 0, 44, 32)
                    rect.center = (round(origin.x), round(origin.y))
                    self.projectiles.append({"rect": rect, "pos": origin,
                        "velocity": pygame.Vector2(self.direction * 7, 0),
                        "lifetime": 140, "kind": "ground_wave"})
                    self.state, self.timer = "recover", 48
                elif self.state == "microphone":
                    self.state, self.timer = "recover", 32
                elif self.state == "windup_throw":
                    origin = pygame.Vector2(self.rect.centerx, self.rect.y + 15)
                    flight = 65
                    velocity = (self.target - origin) / flight
                    velocity.y -= 0.12 * (flight + 1) / 2
                    rect = pygame.Rect(0, 0, 30, 34)
                    rect.center = (round(origin.x), round(origin.y))
                    self.projectiles.append({"rect": rect, "pos": origin,
                                             "velocity": velocity, "lifetime": 140})
                    self.state, self.timer = "recover", 35
                else:
                    self.state = "idle"
            return
        if player is None:
            return
        distance = player.rect.centerx - self.rect.centerx
        self.direction = 1 if distance > 0 else -1
        self.cooldown = max(0, self.cooldown - 1)
        if not self.cooldown:
            self.attack_count += 1
            throwing = self.stage == 2 or (self.stage == 3 and self.attack_count % 2 == 0)
            if self.stage >= 2 and self.attack_count % 3 == 0:
                self.state, self.timer = "windup_rain", 48
            elif self.stage == 3 and self.attack_count % 4 == 0:
                self.state, self.timer = "windup_wave", 40
            else:
                self.state = "windup_throw" if throwing else "windup_mic"
                self.timer = 42 if throwing else 36
            self.target = pygame.Vector2(player.rect.centerx, GROUND_Y - 25)
            self.cooldown = 55 if self.stage == 3 else 80
        elif abs(distance) > 100:
            self.walking = True
            self.x += self.direction * (2.4 if self.stage == 3 else 1.6)
            self.x = max(65, min(WIDTH - 125, self.x))
            self.rect.x = round(self.x)

    def draw(self, screen, camera_x=0):
        if not self.alive:
            draw_defeat(self, screen, 0)
            return
        index = 0
        if self.intro_timer:
            if self.intro_timer > self.INTRO_POSE + self.INTRO_FIGHT:
                index = 1 + (self.tick // 8) % 2
            elif self.intro_timer > self.INTRO_FIGHT:
                index = 7
        elif self.hurt_timer:
            index = 8
        elif self.state == "microphone":
            index = 5
        elif self.state in ("windup_rain", "rain"):
            index = 7
        elif self.state == "recover":
            index = 4
        elif self.state.startswith("windup"):
            index = 6 if self.state == "windup_throw" else 4
        elif self.walking:
            index = 1 + (self.tick // 8) % 2
        image = self.frames[index]
        if self.direction < 0:
            image = pygame.transform.flip(image, True, False)
        if self.hurt_timer and self.tick % 4 < 2:
            image = image.copy()
            image.fill((255, 150, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(image, image.get_rect(midbottom=self.rect.midbottom))
        if self.state.startswith("windup"):
            pygame.draw.circle(screen, (255, 200, 90), (self.rect.centerx, self.rect.y - 36), 6, 2)
        attack = self.get_attack_rect()
        if attack:
            frame = self.attack_frames["wave"][min(2, (18 - self.timer) // 5)]
            if self.direction < 0:
                frame = pygame.transform.flip(frame, True, False)
            screen.blit(frame, frame.get_rect(center=attack.center))
        if self.state == "windup_throw":
            pygame.draw.ellipse(screen, (235, 100, 70), (self.target.x - 28, GROUND_Y - 8, 56, 12), 2)
        for mark in self.falling_marks:
            color = (255, 210, 100) if mark["delay"] > 0 else (255, 100, 60)
            pygame.draw.ellipse(screen, color, (mark["x"] - 30, GROUND_Y - 9, 60, 14), 2)
            pygame.draw.line(screen, color, (mark["x"] - 8, GROUND_Y - 25),
                             (mark["x"] + 8, GROUND_Y - 25), 2)
        for projectile in self.projectiles:
            age = 140 - projectile["lifetime"]
            if projectile.get("kind") == "ground_wave":
                image = self.ground_wave_frames[(age // 5) % 3]
            else:
                image = self.attack_frames["microphone"][(age // 5) % 3]
            if projectile["velocity"].x < 0:
                image = pygame.transform.flip(image, True, False)
            if projectile.get("kind") != "ground_wave":
                image = pygame.transform.rotate(image, age * 7)
            screen.blit(image, image.get_rect(center=projectile["rect"].center))
        for impact in self.impacts:
            image = self.attack_frames["impact"][min(2, impact["age"] // 5)]
            screen.blit(image, image.get_rect(center=impact["pos"]))


class BossArena:
    def __init__(self, intro_duration_ms=3000):
        self.run_score = RunScore()
        self.platforms = [Platform(0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y, "ground")]
        self.guitars = []
        self.goal = None
        self.boss = GustavoBoss(intro_duration_ms)
        self.enemies = [self.boss]
        self.tick = 0
        self.stage_tick = 0
        self.current_stage = 1
        path = Path(__file__).resolve().parent / "assets/images/palco_final.png"
        self.background = pygame.transform.smoothscale(pygame.image.load(str(path)).convert(), (WIDTH, HEIGHT))
        floor_path = Path(__file__).resolve().parent / "assets/images/chao_fase_final.png"
        floor = pygame.image.load(str(floor_path)).convert_alpha()
        floor = floor.subsurface(floor.get_bounding_rect(min_alpha=20)).copy()
        self.floor_image = pygame.transform.smoothscale(floor,
            (WIDTH, round(floor.get_height() * WIDTH / floor.get_width())))
        self.health_bars, self.intro_banners = boss_interface_images()

    @property
    def flames_active(self):
        return (self.boss.alive and self.boss.stage == 3 and self.current_stage == 3
                and self.stage_tick % 180 >= 45)

    def update(self, player=None, intro_elapsed_ms=None):
        self.tick += 1
        self.boss.update(player, intro_elapsed_ms)
        if self.current_stage != self.boss.stage:
            self.current_stage = self.boss.stage
            self.stage_tick = 0
        else:
            self.stage_tick += 1
        if player is not None:
            player.rect.x = max(24, min(WIDTH - player.rect.width - 24, player.rect.x))
            player.pos.x = player.rect.x

    def handle_hazards(self, player):
        if self.flames_active and (player.rect.left < 110 or player.rect.right > WIDTH - 110):
            if player.rect.bottom > GROUND_Y - 135:
                previous = player.health
                player.take_damage()
                return "hurt" if player.health < previous else None
        return None

    def draw_background(self, screen):
        screen.blit(self.background, (0, 0))
        effects = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        stage = self.boss.stage
        if stage >= 2:
            effects.fill((155, 5, 15, 30 if stage == 2 else 55))
        for index, x in enumerate((330, 470, 810, 950)):
            target = x + round(math.sin(self.tick / 70 + index) * 150)
            color = (255, 225, 150, 24) if stage == 1 else (255, 55, 60, 35)
            pygame.draw.polygon(effects, color, [(x, 82), (target - 110, GROUND_Y), (target + 110, GROUND_Y)])
        period = 85 if stage == 3 else 220
        if self.tick % period < (7 if stage == 3 else 3):
            points = [(670, 140), (610, 230), (655, 220), (570, 340), (620, 320), (530, 440)]
            pygame.draw.lines(effects, (205, 170, 255, 210), False, points, 3)
            pygame.draw.rect(effects, (215, 195, 255, 22), (0, 0, WIDTH, HEIGHT))
        screen.blit(effects, (0, 0))

    def draw(self, screen, camera_x=0):
        screen.blit(self.floor_image, (0, GROUND_Y))
        if self.boss.stage == 3 and self.boss.alive:
            for x in (65, WIDTH - 65):
                if self.flames_active:
                    frame = self.boss.attack_frames["flame"][1 + (self.tick // 6) % 2]
                    screen.blit(frame, frame.get_rect(midbottom=(x, GROUND_Y)))
                else:
                    frame = self.boss.attack_frames["flame"][0].copy()
                    frame.set_alpha(100 + (self.tick // 6) % 2 * 80)
                    screen.blit(frame, frame.get_rect(midbottom=(x, GROUND_Y)))
        self.boss.draw(screen)
        bar = self.health_bars[max(0, min(self.boss.MAX_HEALTH, self.boss.health))]
        screen.blit(bar, bar.get_rect(midbottom=(WIDTH // 2, HEIGHT - 3)))
        if self.boss.intro_timer:
            banner = self.intro_banners[0 if self.boss.intro_timer > self.boss.INTRO_FIGHT else 1]
            screen.blit(banner, banner.get_rect(center=(WIDTH // 2, 260)))
