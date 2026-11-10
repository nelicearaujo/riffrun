"""Resultado da tentativa sobre a arte de vitória."""
from pathlib import Path

import pygame

from settings import WIDTH, HEIGHT, COLLECTIBLES_PER_PHASE


class VictoryScreen:
    def __init__(self, defeated=False):
        self.defeated = defeated
        filename = "derrota.png" if defeated else "vitoria.png"
        path = Path(__file__).resolve().parent / "assets" / "images" / filename
        image = pygame.image.load(str(path)).convert_alpha()
        self.scale = min(WIDTH * 0.75 / image.get_width(), HEIGHT * 0.80 / image.get_height())
        self.image = pygame.transform.smoothscale(image, (
            round(image.get_width() * self.scale), round(image.get_height() * self.scale)))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.value_font = pygame.font.SysFont("consolas", round(44 * self.scale), bold=True)
        self.small_font = pygame.font.SysFont("consolas", round(27 * self.scale), bold=True)
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 140))
        self.final_image = None
        if not defeated:
            path = Path(__file__).resolve().parent / "assets/images/final.png"
            self.final_image = pygame.transform.smoothscale(
                pygame.image.load(str(path)).convert(), (WIDTH, HEIGHT))

    def point(self, x, y):
        return self.rect.x + round(x * self.scale), self.rect.y + round(y * self.scale)

    def draw(self, screen, result, phase_number):
        if phase_number == 4 and not self.defeated:
            screen.blit(self.final_image, (0, 0))
            hint = self.small_font.render("ENTER: FASES  |  R: NOVO DUELO", True, (235, 235, 245))
            screen.blit(hint, hint.get_rect(midbottom=(WIDTH // 2, HEIGHT - 16)))
            return
        screen.blit(self.overlay, (0, 0))
        screen.blit(self.image, self.rect)
        for value, y in ((result.time_text, 650),
                         ("—" if phase_number == 4 else f"{result.riffs:02d}/{COLLECTIBLES_PER_PHASE}", 720),
                         (f"{result.total:,}".replace(",", "."), 794)):
            text = self.value_font.render(value, True, (255, 226, 157))
            screen.blit(text, text.get_rect(midright=self.point(1100, y)))
        detail = (f"RIFFS: {result.riff_points}  |  SEM BÔNUS DE CONCLUSÃO" if self.defeated
                  else f"RIFFS: {result.riff_points}  +  BÔNUS TEMPO: {result.time_bonus}")
        bonus = self.small_font.render(
            detail,
            True, (225, 232, 240))
        screen.blit(bonus, bonus.get_rect(center=self.point(768, 552)))
        if self.defeated:
            controls = "R: TENTAR NOVAMENTE  |  ESC: FASES"
        elif phase_number < 4:
            controls = "ENTER: PRÓXIMA FASE  |  R: REPETIR  |  M: FASES"
        else:
            controls = "ENTER: FASES  |  R: REPETIR"
        hint = self.small_font.render(controls, True, (235, 235, 240))
        screen.blit(hint, hint.get_rect(center=self.point(768, 935)))
        status = f"FASE {phase_number + 1} LIBERADA" if phase_number < 3 else "TODAS AS FASES CONCLUÍDAS"
        if phase_number == 3:
            status = "GUSTAVO AGUARDA NO PALCO FINAL"
        elif phase_number == 4:
            status = "GUSTAVO DERROTADO — O PALCO É SEU!"
        if self.defeated:
            status = f"FASE {phase_number}  |  MAIS UMA TENTATIVA!"
        text = self.small_font.render(status, True, (135, 235, 185))
        screen.blit(text, text.get_rect(center=self.point(768, 585)))
