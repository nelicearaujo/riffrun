
import os
import json
import sys
from pathlib import Path

import pygame

from audio import AudioManager
from level import Level
from player import Player
from settings import *


# INICIALIZAÇÃO

pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

clock = pygame.time.Clock()
audio = AudioManager()

font = pygame.font.SysFont("arialblack", 27, bold=True)
small_font = pygame.font.SysFont("arial", 19, bold=True)
big_font = pygame.font.SysFont("arialblack", 60, bold=True)
menu_title_font = pygame.font.SysFont("arialblack", 52, bold=True)
menu_number_font = pygame.font.SysFont("arialblack", 64, bold=True)


# ARQUIVOS E IMAGENS

BASE_DIR = Path(__file__).resolve().parent

BACKGROUND_PATH = (
    BASE_DIR / "assets" / "images" / "metal_storm_stage.png"
)

PHASE2_BACKGROUND_PATH = (
    BASE_DIR / "assets" / "images" / "visualFase2.png"
)

PHASE3_BACKGROUND_PATH = (
    BASE_DIR / "assets" / "images" / "visualFase3.png"
)


def load_background(path):
    try:
        image = pygame.image.load(str(path)).convert()
        return pygame.transform.smoothscale(
            image, (WIDTH, HEIGHT)
        )
    except (pygame.error, FileNotFoundError):
        return None


stage_background = load_background(BACKGROUND_PATH)
phase2_background = load_background(PHASE2_BACKGROUND_PATH)
phase3_background = load_background(PHASE3_BACKGROUND_PATH)


# CONFIGURAÇÃO DAS FASES

PHASES = (
    {
        "title": "TEMPESTADE DE AÇO",
        "subtitle": "O palco desperta",
        "accent": (225, 157, 48),
    },
    {
        "title": "AC/DC // HIGHWAY",
        "subtitle": "A estrada ferve sob o palco",
        "accent": (224, 65, 48),
    },
    {
        "title": "ÚLTIMO BIS",
        "subtitle": "A nota final espera",
        "accent": (194, 74, 72),
    },
)

NODE_CENTERS = (
    (215, 506),
    (619, 424),
    (1017, 304),
)

PROGRESS_PATH = BASE_DIR / "progress.json"


# SALVAMENTO DO PROGRESSO

def load_unlocked_phases():
    try:
        progress = json.loads(
            PROGRESS_PATH.read_text(encoding="utf-8")
        )

        return max(
            1,
            min(3, int(progress.get("unlocked_phases", 1)))
        )

    except (OSError, ValueError, TypeError):
        return 1


def save_unlocked_phases(unlocked_phases):
    try:
        PROGRESS_PATH.write_text(
            json.dumps(
                {"unlocked_phases": unlocked_phases},
                indent=2
            ),
            encoding="utf-8",
        )

    except OSError:
        print("Não foi possível salvar o progresso.")


# CENÁRIO

def draw_background(screen, camera_x, phase_number=1):

    if phase_number == 3 and phase3_background:
        background = phase3_background
    elif phase_number == 2 and phase2_background:
        background = phase2_background
    else:
        background = stage_background

    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill((9, 13, 25))

    phase_tints = (
        (0, 0, 0),
        (42, 8, 8),
        (7, 28, 35),
    )

    tint = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    tint.fill(
        (*phase_tints[phase_number - 1], 24)
    )

    screen.blit(tint, (0, 0))

    # Parallax do cenário
    parallax = int(camera_x * 0.22)
    spacing = 310

    for i in range(-1, 7):

        x = i * spacing - (parallax % spacing)

        pygame.draw.rect(
            screen,
            (11, 17, 28),
            (x, 515, 14, 125)
        )

        pygame.draw.rect(
            screen,
            (43, 53, 66),
            (x + 3, 515, 3, 125)
        )

        pygame.draw.line(
            screen,
            (35, 45, 58),
            (x, 530),
            (x + 118, 640),
            4
        )

        pygame.draw.line(
            screen,
            (20, 28, 41),
            (x + 118, 530),
            (x, 640),
            4
        )

    haze = pygame.Surface(
        (WIDTH, 110),
        pygame.SRCALPHA
    )

    haze.fill((24, 37, 58, 38))

    screen.blit(haze, (0, 530))


# HUD

def draw_hud(screen, player, phase_number):

    shadow = pygame.Rect(20, 20, 326, 92)
    panel = pygame.Rect(16, 16, 326, 92)

    pygame.draw.rect(
        screen, (3, 6, 12), shadow, border_radius=5
    )

    pygame.draw.rect(
        screen, (18, 24, 34), panel, border_radius=5
    )

    pygame.draw.rect(
        screen, (91, 111, 128), panel, 3, border_radius=5
    )

    accent = PHASES[phase_number - 1]["accent"]

    pygame.draw.line(
        screen,
        accent,
        (28, 57),
        (330, 57),
        2
    )

    for x in (27, 331):
        for y in (27, 97):

            pygame.draw.circle(
                screen, (154, 169, 177), (x, y), 3
            )

            pygame.draw.circle(
                screen, (44, 52, 61), (x, y), 1
            )

    life_text = font.render(
        f"ENERGIA  {player.health}",
        True,
        (224, 233, 238)
    )

    score_text = font.render(
        f"RIFFS  {player.score:02d}/15",
        True,
        (231, 169, 62)
    )

    phase_text = small_font.render(
        f"FASE {phase_number}",
        True,
        accent
    )

    screen.blit(life_text, (39, 25))
    screen.blit(phase_text, (251, 29))
    screen.blit(score_text, (39, 64))


# MENU - MAPA DE CAMPANHA

def menu_card_rects():

    return [
        pygame.Rect(
            center_x - 59,
            center_y - 59,
            118,
            118
        )
        for center_x, center_y in NODE_CENTERS
    ]


def draw_map_menu(screen, selected_phase, unlocked_phases):

    top_color = (7, 11, 20)
    bottom_color = (18, 27, 42)

    # Fundo em degradê
    for y in range(HEIGHT):

        blend = y / HEIGHT

        color = tuple(
            round(
                top_color[i] * (1 - blend)
                + bottom_color[i] * blend
            )
            for i in range(3)
        )

        pygame.draw.line(
            screen, color, (0, y), (WIDTH, y)
        )

    pygame.draw.rect(
        screen,
        (3, 5, 10),
        (22, 20, WIDTH - 44, HEIGHT - 40),
        border_radius=7
    )

    pygame.draw.rect(
        screen,
        (49, 57, 70),
        (28, 26, WIDTH - 56, HEIGHT - 52),
        2,
        border_radius=5
    )

    map_rect = pygame.Rect(
        48, 150, WIDTH - 96, 458
    )

    pygame.draw.rect(
        screen, (10, 28, 43), map_rect, border_radius=4
    )

    pygame.draw.rect(
        screen, (39, 74, 91), map_rect, 2, border_radius=4
    )

    # Textura da água
    for y in range(map_rect.top + 18, map_rect.bottom - 8, 24):

        for x in range(
            map_rect.left + (y % 37),
            map_rect.right,
            92
        ):

            pygame.draw.line(
                screen,
                (16, 54, 70),
                (x, y),
                (x + 34, y - 7),
                2
            )

            pygame.draw.line(
                screen,
                (14, 43, 60),
                (x + 8, y + 6),
                (x + 48, y + 1),
                1
            )

    for x in range(
        map_rect.left + 35,
        map_rect.right,
        92
    ):

        pygame.draw.line(
            screen,
            (19, 47, 61),
            (x, map_rect.top),
            (x + 130, map_rect.bottom),
            1
        )

    # Ilha do mapa
    island = [
        (89, 530),
        (111, 286),
        (242, 203),
        (408, 175),
        (566, 218),
        (707, 184),
        (900, 205),
        (1091, 260),
        (1192, 431),
        (1154, 548),
        (893, 564),
        (659, 541),
        (432, 568),
        (220, 551),
    ]

    pygame.draw.polygon(
        screen, (18, 27, 33), island
    )

    pygame.draw.polygon(
        screen, (68, 48, 54), island, 4
    )

    pygame.draw.lines(
        screen,
        (112, 43, 47),
        False,
        island + [island[0]],
        2
    )

    # Montanhas
    mountains = (
        [
            (142, 377),
            (224, 242),
            (295, 371),
            (351, 267),
            (420, 407),
        ],
        [
            (424, 364),
            (510, 227),
            (595, 371),
            (687, 238),
            (782, 403),
        ],
        [
            (795, 354),
            (878, 246),
            (956, 369),
            (1047, 281),
            (1148, 426),
        ],
    )

    for points in mountains:

        pygame.draw.polygon(
            screen, (27, 37, 43), points
        )

        pygame.draw.lines(
            screen,
            (74, 82, 87),
            False,
            points,
            2
        )

    # Estruturas industriais
    buildings = (
        (180, 405, 55, 88),
        (330, 371, 39, 122),
        (870, 386, 48, 106),
        (1080, 373, 58, 105),
    )

    for x, y, w, h in buildings:

        pygame.draw.rect(
            screen,
            (12, 18, 25),
            (x, y, w, h)
        )

        pygame.draw.rect(
            screen,
            (74, 79, 83),
            (x, y, w, 3)
        )

        for window_y in range(
            y + 17,
            y + h - 8,
            22
        ):

            pygame.draw.rect(
                screen,
                (161, 68, 48),
                (x + 9, window_y, 6, 5)
            )

            pygame.draw.rect(
                screen,
                (161, 68, 48),
                (x + w - 15, window_y, 6, 5)
            )

    # Caminho entre as fases
    route = [
        (215, 506),
        (400, 455),
        (619, 424),
        (823, 389),
        (1017, 304),
    ]

    pygame.draw.lines(
        screen, (51, 14, 24), False, route, 42
    )

    pygame.draw.lines(
        screen, (116, 34, 42), False, route, 28
    )

    pygame.draw.lines(
        screen, (212, 77, 48), False, route, 14
    )

    pygame.draw.lines(
        screen, (245, 157, 69), False, route, 4
    )

    for x, y in route[1:-1]:

        pygame.draw.circle(
            screen, (145, 49, 46), (x, y), 11, 2
        )

    # Símbolo elétrico
    bolt = [
        (706, 238),
        (729, 238),
        (710, 272),
        (733, 272),
        (691, 326),
        (702, 283),
        (681, 283),
    ]

    pygame.draw.polygon(
        screen, (115, 35, 43), bolt
    )

    pygame.draw.lines(
        screen,
        (237, 145, 67),
        False,
        bolt + [bolt[0]],
        3
    )

    # Nós das três fases
    for index, (center_x, center_y) in enumerate(NODE_CENTERS):

        phase = PHASES[index]

        unlocked = index < unlocked_phases
        selected = index == selected_phase

        accent = (
            phase["accent"]
            if unlocked
            else (81, 91, 101)
        )

        if selected:

            glow = pygame.Surface(
                (170, 170),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                glow,
                (*accent, 48),
                (85, 85),
                64
            )

            screen.blit(
                glow,
                (center_x - 85, center_y - 85)
            )

            pygame.draw.circle(
                screen,
                (222, 141, 57),
                (center_x, center_y),
                59,
                2
            )

        pygame.draw.circle(
            screen,
            (4, 7, 12),
            (center_x + 4, center_y + 7),
            49
        )

        pygame.draw.circle(
            screen,
            (31, 38, 46),
            (center_x, center_y),
            47
        )

        pygame.draw.circle(
            screen,
            accent,
            (center_x, center_y),
            42,
            3
        )

        pygame.draw.circle(
            screen,
            (15, 21, 28),
            (center_x, center_y),
            35
        )

        number = menu_number_font.render(
            str(index + 1),
            True,
            accent
        )

        screen.blit(
            number,
            number.get_rect(
                center=(center_x, center_y - 2)
            )
        )

        if not unlocked:

            pygame.draw.rect(
                screen,
                (90, 101, 109),
                (center_x - 11, center_y + 19, 22, 17),
                2,
                border_radius=3
            )

            pygame.draw.arc(
                screen,
                (90, 101, 109),
                (center_x - 7, center_y + 7, 14, 21),
                0.1,
                3.05,
                2
            )

        elif index + 1 < unlocked_phases:

            pygame.draw.line(
                screen,
                (103, 205, 166),
                (center_x - 14, center_y + 2),
                (center_x - 3, center_y + 13),
                4
            )

            pygame.draw.line(
                screen,
                (103, 205, 166),
                (center_x - 3, center_y + 13),
                (center_x + 17, center_y - 12),
                4
            )

        label = small_font.render(
            f"FASE {index + 1}  //  {phase['title']}",
            True,
            accent
        )

        label_bg = pygame.Rect(
            center_x - label.get_width() // 2 - 8,
            center_y + 58,
            label.get_width() + 16,
            27
        )

        pygame.draw.rect(
            screen,
            (7, 12, 18),
            label_bg,
            border_radius=3
        )

        pygame.draw.rect(
            screen,
            (51, 62, 71),
            label_bg,
            1,
            border_radius=3
        )

        screen.blit(
            label,
            label.get_rect(center=label_bg.center)
        )

    eyebrow = small_font.render(
        "RIFF RUN  //  MAPA DE CAMPANHA",
        True,
        (137, 157, 168)
    )

    title = menu_title_font.render(
        "ESCOLHA SEU CAMINHO",
        True,
        (226, 231, 226)
    )

    subtitle = small_font.render(
        "Uma rota. Três palcos. Nenhum retorno.",
        True,
        (174, 139, 111)
    )

    screen.blit(
        eyebrow,
        (
            WIDTH // 2 - eyebrow.get_width() // 2,
            38
        )
    )

    screen.blit(
        title,
        (
            WIDTH // 2 - title.get_width() // 2,
            58
        )
    )

    screen.blit(
        subtitle,
        (
            WIDTH // 2 - subtitle.get_width() // 2,
            116
        )
    )

    hint = small_font.render(
        "SETAS: SELECIONAR  |  ENTER: JOGAR  |  ESC: SAIR",
        True,
        (193, 202, 204)
    )

    hint_panel = pygame.Rect(
        WIDTH // 2 - hint.get_width() // 2 - 18,
        649,
        hint.get_width() + 36,
        42
    )

    pygame.draw.rect(
        screen,
        (10, 16, 24),
        hint_panel,
        border_radius=4
    )

    pygame.draw.rect(
        screen,
        (92, 72, 65),
        hint_panel,
        2,
        border_radius=4
    )

    screen.blit(
        hint,
        (hint_panel.x + 18, hint_panel.y + 10)
    )


def draw_menu(screen, selected_phase, unlocked_phases):
    draw_map_menu(
        screen,
        selected_phase,
        unlocked_phases
    )


# REINICIAR FASE

def reset_game(phase_number):

    player = Player(120, 500, phase_number)
    level = Level(phase_number)

    return player, level, False, False


# ESTADO INICIAL

player, level, victory, game_over = reset_game(1)

phase_number = 1
selected_phase = 0

unlocked_phases = load_unlocked_phases()

screen_mode = "menu"
running = True

# Inimigos atingidos durante o ataque atual
enemies_hit_this_attack = set()

# LOOP PRINCIPAL

while running:

    clock.tick(FPS)

    # EVENTOS

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
            continue

        # Controle de áudio disponível em qualquer tela
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_v
        ):
            audio.toggle_mute()
            continue

        # EVENTOS DO MENU

        if screen_mode == "menu":

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key in (
                    pygame.K_UP,
                    pygame.K_w,
                    pygame.K_LEFT,
                    pygame.K_a
                ):

                    selected_phase = (
                        selected_phase - 1
                    ) % len(PHASES)

                elif event.key in (
                    pygame.K_DOWN,
                    pygame.K_s,
                    pygame.K_RIGHT,
                    pygame.K_d
                ):

                    selected_phase = (
                        selected_phase + 1
                    ) % len(PHASES)

                elif event.key in (
                    pygame.K_RETURN,
                    pygame.K_KP_ENTER,
                    pygame.K_SPACE
                ):

                    if selected_phase < unlocked_phases:

                        phase_number = selected_phase + 1

                        (
                            player,
                            level,
                            victory,
                            game_over
                        ) = reset_game(phase_number)

                        screen_mode = "playing"

                elif event.key in (
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3
                ):

                    requested_phase = (
                        event.key - pygame.K_0
                    )

                    if requested_phase <= unlocked_phases:

                        selected_phase = requested_phase - 1
                        phase_number = requested_phase

                        (
                            player,
                            level,
                            victory,
                            game_over
                        ) = reset_game(phase_number)

                        screen_mode = "playing"

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                for index, rect in enumerate(menu_card_rects()):

                    if rect.collidepoint(event.pos):

                        selected_phase = index

                        if index < unlocked_phases:

                            phase_number = index + 1

                            (
                                player,
                                level,
                                victory,
                                game_over
                            ) = reset_game(phase_number)

                            screen_mode = "playing"

                        break

        # EVENTOS DURANTE O JOGO

        else:

            # Teclado
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    screen_mode = "menu"
                    selected_phase = min(
                        phase_number - 1, 2
                    )

                elif (
                    (victory or game_over)
                    and event.key == pygame.K_r
                ):

                    (
                        player,
                        level,
                        victory,
                        game_over
                    ) = reset_game(phase_number)

                elif (
                    victory
                    and event.key in (
                        pygame.K_m,
                        pygame.K_RETURN,
                        pygame.K_KP_ENTER
                    )
                ):

                    screen_mode = "menu"
                    selected_phase = min(
                        phase_number, 2
                    )

            # Mouse: ataque
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not victory
                and not game_over
            ):

                if player.attack_timer <= 0:
                    player.start_attack()

                    # Um novo ataque pode atingir os inimigos novamente
                    enemies_hit_this_attack.clear()

                    audio.play_sfx("attack")

    # ATUALIZAÇÃO DO JOGO

    if (
        screen_mode == "playing"
        and not victory
        and not game_over
    ):

        # MOVIMENTAÇÃO E PULO

        was_on_ground = player.on_ground

        player.update(level.platforms)

        if (
            was_on_ground
            and not player.on_ground
            and player.vel.y < 0
            and player.invulnerability == 0
        ):

            audio.play_sfx("jump")

        # INIMIGOS

        level.update(player)

        # COLETÁVEIS

        for guitar in level.guitars:

            if (
                not guitar.collected
                and player.rect.colliderect(guitar.rect)
            ):

                guitar.collected = True
                player.score += 1

                audio.play_sfx("collect")

        # ATAQUE E COLISÃO COM INIMIGOS

        attack_rect = player.get_attack_rect()

        if attack_rect:

            hit_enemy = False

            for enemy in level.enemies:

                if not enemy.alive:
                    continue

                # Impede múltiplos danos no mesmo ataque
                if enemy in enemies_hit_this_attack:
                    continue

                if attack_rect.colliderect(enemy.rect):

                    enemies_hit_this_attack.add(enemy)

                    # Novos inimigos com resistência
                    if hasattr(enemy, "take_hit"):

                        enemy.take_hit()

                    # Inimigos básicos
                    else:

                        enemy.alive = False

                    hit_enemy = True

            if hit_enemy:
                audio.play_sfx("enemy_hit")

        # COLISÃO COM PROJÉTEIS DOS INIMIGOS

        for enemy in level.enemies:

            if not enemy.alive:
                continue

            # Apenas inimigos com projéteis
            if not hasattr(enemy, "projectiles"):
                continue

            for projectile in enemy.projectiles[:]:

                if player.rect.colliderect(
                        projectile["rect"]
                ):

                    previous_health = player.health

                    player.take_damage()

                    # O projétil desaparece ao atingir
                    enemy.projectiles.remove(projectile)

                    if player.health < previous_health:
                        audio.play_sfx("hurt")

        # DANO AO JOGADOR

        for enemy in level.enemies:

            if (
                enemy.alive
                and player.rect.colliderect(enemy.rect)
            ):

                previous_health = player.health

                player.take_damage()

                if player.health < previous_health:

                    audio.play_sfx("hurt")

        # QUEDA EM BURACOS

        if player.rect.top > HEIGHT + 100:

            audio.play_sfx("fall")

            player.take_damage()

            player.pos.update(120, 500)
            player.rect.topleft = player.pos
            player.vel.update(0, 0)

        # GAME OVER

        if player.health <= 0:

            game_over = True

        # VITÓRIA

        if (
            not game_over
            and player.rect.colliderect(level.goal.rect)
        ):

            audio.play_sfx("victory")

            victory = True

            unlocked_phases = max(
                unlocked_phases,
                min(3, phase_number + 1)
            )

            save_unlocked_phases(unlocked_phases)

            selected_phase = min(
                unlocked_phases - 1,
                2
            )

    # MÚSICA DE FUNDO

    if (
        screen_mode == "playing"
        and not victory
        and not game_over
    ):

        audio.set_phase(phase_number)

    else:

        audio.set_phase(None)

    # DESENHO DA TELA

    if screen_mode == "menu":

        draw_menu(
            screen,
            selected_phase,
            unlocked_phases
        )

    else:

        camera_x = (
            player.rect.centerx - WIDTH // 2
        )

        camera_x = max(
            0,
            min(camera_x, LEVEL_WIDTH - WIDTH)
        )

        draw_background(
            screen,
            camera_x,
            phase_number
        )

        level.draw(screen, camera_x)
        player.draw(screen, camera_x)

        draw_hud(
            screen,
            player,
            phase_number
        )

        # TEXTO DE AJUDA

        help_text = small_font.render(
            "A/D: MOVER  |  ESPAÇO: PULAR  |  "
            "CLIQUE: ATACAR  |  V: SOM  |  ESC: MENU",
            True,
            (218, 226, 231)
        )

        help_x = (
            WIDTH - help_text.get_width() - 22
        )

        help_panel = pygame.Rect(
            help_x - 13,
            16,
            help_text.get_width() + 26,
            34
        )

        help_surface = pygame.Surface(
            help_panel.size,
            pygame.SRCALPHA
        )

        help_surface.fill(
            (7, 12, 20, 165)
        )

        screen.blit(
            help_surface,
            help_panel
        )

        pygame.draw.line(
            screen,
            (225, 157, 48),
            (help_panel.x, help_panel.bottom),
            (help_panel.right, help_panel.bottom),
            2
        )

        screen.blit(
            help_text,
            (help_x, 23)
        )

        # TELA DE VITÓRIA

        if victory:

            overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            overlay.fill((0, 0, 0, 180))

            screen.blit(
                overlay,
                (0, 0)
            )

            title = big_font.render(
                f"FASE {phase_number} CONCLUÍDA!",
                True,
                (230, 169, 60)
            )

            subtitle = font.render(
                f"{PHASES[phase_number - 1]['title']}  "
                f"•  Riffs: {player.score}/15",
                True,
                (240, 240, 240)
            )

            if phase_number < len(PHASES):

                next_text = (
                    f"Fase {phase_number + 1} liberada!"
                )

            else:

                next_text = "Todas as fases liberadas!"

            next_line = small_font.render(
                next_text,
                True,
                (111, 219, 188)
            )

            retry = small_font.render(
                "R: repetir fase  |  "
                "ENTER/M: voltar ao início",
                True,
                (220, 220, 220)
            )

            screen.blit(
                title,
                (
                    WIDTH // 2 - title.get_width() // 2,
                    245
                )
            )

            screen.blit(
                subtitle,
                (
                    WIDTH // 2 - subtitle.get_width() // 2,
                    330
                )
            )

            screen.blit(
                next_line,
                (
                    WIDTH // 2 - next_line.get_width() // 2,
                    375
                )
            )

            screen.blit(
                retry,
                (
                    WIDTH // 2 - retry.get_width() // 2,
                    420
                )
            )

        # TELA DE GAME OVER

        if game_over:

            overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            overlay.fill((0, 0, 0, 190))

            screen.blit(
                overlay,
                (0, 0)
            )

            title = big_font.render(
                "O SOM SE CALOU",
                True,
                (196, 58, 55)
            )

            retry = font.render(
                "R: tentar novamente  |  "
                "ESC: voltar ao início",
                True,
                (240, 240, 240)
            )

            screen.blit(
                title,
                (
                    WIDTH // 2 - title.get_width() // 2,
                    285
                )
            )

            screen.blit(
                retry,
                (
                    WIDTH // 2 - retry.get_width() // 2,
                    380
                )
            )

    # ATUALIZAÇÃO DA JANELA

    pygame.display.flip()

    # Captura de tela opcional para testes
    screenshot_path = os.environ.get(
        "RIFF_RUN_SCREENSHOT"
    )

    if screenshot_path:

        pygame.image.save(
            screen,
            screenshot_path
        )

        running = False


pygame.quit()
sys.exit()
