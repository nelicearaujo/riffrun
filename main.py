
import os
import json
import sys
from pathlib import Path

import pygame

from audio import AudioManager
from hud import Hud
from victory import VictoryScreen
from level import Level
from boss import BossArena
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
    BASE_DIR / "assets" / "images" / "visualFase1.png"
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

HOME_BACKGROUND_PATH = (
    BASE_DIR / "assets" / "images" / "menu_inicial.png"
)

home_background = load_background(HOME_BACKGROUND_PATH)

PHASE_MENU_PATH = (
    BASE_DIR / "assets" / "images" / "menu_fases.png"
)

phase_menu_background = load_background(PHASE_MENU_PATH)

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

        if not isinstance(progress, dict):
            return 1

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

hud = Hud()
victory_screen = VictoryScreen()
defeat_screen = VictoryScreen(defeated=True)


def draw_hud(screen, player, phase_number):
    hud.draw(screen, player, phase_number)


# MENU - FASES

def menu_card_rects():
    """Áreas clicáveis sobre os cards da imagem."""

    return [
        pygame.Rect(100, 194, 356, 433),
        pygame.Rect(474, 194, 336, 433),
        pygame.Rect(826, 194, 359, 433),
    ]

def draw_map_menu(screen, selected_phase, unlocked_phases):
    """Desenha a seleção de fases usando a imagem personalizada."""

    if phase_menu_background is not None:
        screen.blit(phase_menu_background, (0, 0))
    else:
        screen.fill((12, 18, 30))

    cards = menu_card_rects()
    mouse_pos = pygame.mouse.get_pos()

    lock_font = pygame.font.SysFont(
        "consolas",
        27,
        bold=True
    )

    for index, rect in enumerate(cards):

        unlocked = index < unlocked_phases
        selected = index == selected_phase
        hovered = rect.collidepoint(mouse_pos)

        # Escurece as fases ainda bloqueadas.
        if not unlocked:

            overlay = pygame.Surface(
                rect.size,
                pygame.SRCALPHA
            )

            overlay.fill((0, 0, 0, 145))

            screen.blit(
                overlay,
                rect.topleft
            )

            label = lock_font.render(
                "BLOQUEADA",
                True,
                (225, 220, 220)
            )

            label_rect = label.get_rect(
                center=rect.center
            )

            screen.blit(label, label_rect)

        # Destaca a fase selecionada.
        elif selected or hovered:

            pygame.draw.rect(
                screen,
                (255, 220, 135),
                rect.inflate(-8, -8),
                3,
                border_radius=8
            )
def home_button_rects():
    """
    Áreas clicáveis dos botões da imagem inicial.

    Coordenadas ajustadas para 1280x720.
    """

    return {
        "play": pygame.Rect(480, 308, 320, 65),
        "options": pygame.Rect(492, 387, 296, 60),
        "credits": pygame.Rect(492, 458, 296, 60),
        "quit": pygame.Rect(492, 529, 296, 60),
    }

def draw_info_panel(screen, title, lines):
    """Desenha um painel informativo sobre o menu inicial."""

    draw_home(screen)

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill((0, 0, 0, 185))

    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(
        WIDTH // 2 - 290,
        HEIGHT // 2 - 190,
        580,
        380
    )

    pygame.draw.rect(
        screen,
        (19, 25, 39),
        panel,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (200, 75, 65),
        panel,
        3,
        border_radius=12
    )

    title_font = pygame.font.SysFont(
        "consolas",
        42,
        bold=True
    )

    text_font = pygame.font.SysFont(
        "consolas",
        23
    )

    title_image = title_font.render(
        title,
        True,
        (245, 235, 225)
    )

    screen.blit(
        title_image,
        title_image.get_rect(
            centerx=panel.centerx,
            top=panel.y + 32
        )
    )

    for index, line in enumerate(lines):

        text_image = text_font.render(
            line,
            True,
            (220, 225, 235)
        )

        screen.blit(
            text_image,
            text_image.get_rect(
                centerx=panel.centerx,
                top=panel.y + 120 + index * 42
            )
        )

    hint = text_font.render(
        "ESC - VOLTAR",
        True,
        (235, 155, 110)
    )

    screen.blit(
        hint,
        hint.get_rect(
            centerx=panel.centerx,
            bottom=panel.bottom - 22
        )
    )

def draw_home(screen):
    """Desenha o menu inicial."""

    if home_background is not None:
        screen.blit(home_background, (0, 0))
    else:
        screen.fill((12, 18, 30))

    # Destaca discretamente o botão sob o mouse.
    mouse_pos = pygame.mouse.get_pos()

    for rect in home_button_rects().values():

        if rect.collidepoint(mouse_pos):

            highlight_rect = rect.inflate(-6, -6)

            highlight = pygame.Surface(
                highlight_rect.size,
                pygame.SRCALPHA
            )

            pygame.draw.rect(
                highlight,
                (255, 255, 255, 28),
                highlight.get_rect(),
                border_radius=18
            )

            screen.blit(highlight, highlight_rect.topleft)

            break

def draw_menu(screen, selected_phase, unlocked_phases):
    draw_map_menu(
        screen,
        selected_phase,
        unlocked_phases
    )


# REINICIAR FASE

def reset_game(phase_number):

    if phase_number == 4:
        player = Player(80, GROUND_Y - 70, 4)
        arena = BossArena(audio.boss_intro_duration_ms())
        audio.start_boss_intro()
        return player, arena, False, False

    player = Player(120, 500, phase_number)
    level = Level(phase_number)

    return player, level, False, False


# ESTADO INICIAL

player, level, victory, game_over = reset_game(1)

phase_number = 1
selected_phase = 0

unlocked_phases = load_unlocked_phases()

screen_mode = "home"
running = True

# Inimigos atingidos durante o ataque atual
enemies_hit_this_attack = set()

# LOOP PRINCIPAL

while running:

    frame_ms = clock.tick(FPS)

    # EVENTOS

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
            continue

        if audio.handle_music_event(event):
            continue

        # Controle de áudio disponível em qualquer tela
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_v
        ):
            audio.toggle_mute()
            continue
        # EVENTOS DA TELA INICIAL

        if screen_mode == "home":

            if event.type == pygame.KEYDOWN:

                if event.key in (
                    pygame.K_RETURN,
                    pygame.K_KP_ENTER
                ):
                    screen_mode = "menu"

                elif event.key == pygame.K_ESCAPE:
                    running = False

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                buttons = home_button_rects()

                if any(rect.collidepoint(event.pos) for rect in buttons.values()):
                    audio.play_sfx("menu_click")

                if buttons["play"].collidepoint(event.pos):
                    screen_mode = "menu"

                elif buttons["options"].collidepoint(event.pos):
                    screen_mode = "options"

                elif buttons["credits"].collidepoint(event.pos):
                    screen_mode = "credits"

                elif buttons["quit"].collidepoint(event.pos):
                    pygame.time.wait(60)
                    running = False

            continue

        # EVENTOS DAS OPÇÕES E CRÉDITOS

        if screen_mode in ("options", "credits"):

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):
                screen_mode = "home"

            continue

        # EVENTOS DO MENU

        if screen_mode == "menu":

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_b:
                    phase_number = 4
                    player, level, victory, game_over = reset_game(phase_number)
                    enemies_hit_this_attack.clear()
                    screen_mode = "playing"

                elif event.key == pygame.K_ESCAPE:
                    screen_mode = "home"

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

                        audio.play_sfx("menu_click")
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

        elif screen_mode == "playing":

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
                        pygame.K_RETURN,
                        pygame.K_KP_ENTER
                    )
                ):

                    audio.play_sfx("menu_click")
                    if phase_number < 4:
                        phase_number += 1
                        selected_phase = min(phase_number - 1, len(PHASES) - 1)
                        player, level, victory, game_over = reset_game(phase_number)
                        enemies_hit_this_attack.clear()
                    else:
                        screen_mode = "menu"
                        selected_phase = len(PHASES) - 1

                elif victory and event.key == pygame.K_m:
                    screen_mode = "menu"
                    selected_phase = min(phase_number, len(PHASES) - 1)

            # Mouse: ataque
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not victory
                and not game_over
                and not (phase_number == 4 and level.boss.intro_timer > 0)
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

        arena_intro = phase_number == 4 and level.boss.intro_timer > 0
        if not arena_intro:
            level.run_score.advance(frame_ms)

        was_on_ground = player.on_ground

        if arena_intro:
            player.vel.update(0, 0)
            player.on_ground = True
            player.update_animation()
        else:
            player.update(level.platforms)

        if (
            was_on_ground
            and not player.on_ground
            and player.vel.y < 0
            and player.invulnerability == 0
        ):

            audio.play_sfx("jump")

        # INIMIGOS

        if phase_number == 4:
            level.update(player, intro_elapsed_ms=audio.boss_intro_elapsed_ms())
        else:
            level.update(player)

        hazard_sound = level.handle_hazards(player)
        if hazard_sound:
            audio.play_sfx(hazard_sound)

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
                    if hasattr(enemy, "on_projectile_hit"):
                        enemy.on_projectile_hit(projectile)
                    enemy.projectiles.remove(projectile)

                    if player.health < previous_health:
                        audio.play_sfx("hurt")

        # DANO AO JOGADOR

        for enemy in level.enemies:

            if (
                enemy.alive
                and getattr(enemy, "can_damage", True)
                and (player.rect.colliderect(enemy.rect)
                     or (hasattr(enemy, "get_attack_rect")
                         and enemy.get_attack_rect() is not None
                         and player.rect.colliderect(enemy.get_attack_rect())))
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
            level.run_score.finish(player.score, completed=False)

        # VITÓRIA

        if (
            not game_over
            and ((phase_number == 4 and not level.boss.alive and level.boss.death_timer <= 0)
                 or (phase_number != 4 and player.rect.colliderect(level.goal.rect)))
        ):

            audio.play_sfx("victory")
            level.run_score.finish(player.score)

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

    if screen_mode == "playing" and game_over:
        player.update_death(level.platforms)

    # MÚSICA DE FUNDO

    if (
        screen_mode == "playing"
        and not victory
        and not game_over
    ):

        if phase_number == 4:
            if level.boss.intro_timer == 0:
                audio.finish_boss_intro()
            audio.set_phase("boss_intro" if level.boss.intro_timer else 4)
        else:
            audio.set_phase(phase_number)

    elif screen_mode == "playing" and victory and phase_number == 4:

        audio.set_phase("ending")

    elif screen_mode in ("home", "menu", "options", "credits"):

        audio.set_phase("menu")

    else:

        audio.set_phase(None)

    # DESENHO DA TELA

    if screen_mode == "home":

        draw_home(screen)

    elif screen_mode == "options":

        draw_info_panel(
            screen,
            "OPCOES",
            [
                "V - ATIVAR/DESATIVAR SOM",
                "ESC - VOLTAR",
            ]
        )

    elif screen_mode == "credits":

        draw_info_panel(
            screen,
            "CREDITOS",
            [
                "RIFF RUN",
                "Desenvolvimento: Equipe Riff Run",
                "Projeto academico",
                "Programacao para Jogos",
            ]
        )

    elif screen_mode == "menu":

        draw_menu(
            screen,
            selected_phase,
            unlocked_phases
        )

    elif screen_mode == "playing":

        camera_x = (
            player.rect.centerx - WIDTH // 2

        )

        camera_x = (
            player.rect.centerx - WIDTH // 2
        )

        camera_x = max(
            0,
            min(camera_x, LEVEL_WIDTH - WIDTH)
        )

        if phase_number == 4:
            camera_x = 0
            level.draw_background(screen)
        else:
            draw_background(screen, camera_x, phase_number)

        level.draw(screen, camera_x)
        player.draw(screen, camera_x)

        draw_hud(
            screen,
            player,
            phase_number
        )

        # TELA DE VITÓRIA

        if victory:
            victory_screen.draw(screen, level.run_score.result, phase_number)

        # TELA DE GAME OVER

        if game_over and player.death_tick >= 50:
            defeat_screen.draw(screen, level.run_score.result, phase_number)

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
