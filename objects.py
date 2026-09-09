import pygame


STEEL_DARK = (20, 27, 36)
STEEL = (54, 66, 78)
STEEL_LIGHT = (117, 132, 142)
CYAN = (100, 210, 231)
AMBER = (225, 157, 48)


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
            self.draw_ground(screen, r)
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
