"""Pontuação e tempo ativo de uma tentativa de fase."""
from dataclasses import dataclass

from settings import COLLECTIBLES_PER_PHASE

POINTS_PER_RIFF = 1000
TIME_LIMIT_SECONDS = 180
TIME_POINTS_PER_SECOND = 10


@dataclass(frozen=True)
class RunResult:
    elapsed_ms: int
    riffs: int
    riff_points: int
    time_bonus: int

    @property
    def total(self):
        return self.riff_points + self.time_bonus

    @property
    def time_text(self):
        seconds = self.elapsed_ms // 1000
        return f"{seconds // 60:02d}:{seconds % 60:02d}"


class RunScore:
    def __init__(self):
        self.elapsed_ms = 0
        self.result = None

    def advance(self, milliseconds):
        if self.result is None:
            self.elapsed_ms += max(0, milliseconds)

    def finish(self, riffs, completed=True):
        if self.result is None:
            riffs = max(0, min(COLLECTIBLES_PER_PHASE, riffs))
            remaining_ms = max(0, TIME_LIMIT_SECONDS * 1000 - self.elapsed_ms)
            self.result = RunResult(
                self.elapsed_ms, riffs, riffs * POINTS_PER_RIFF,
                remaining_ms * TIME_POINTS_PER_SECOND // 1000 if completed else 0,
            )
        return self.result
