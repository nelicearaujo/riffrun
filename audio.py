from pathlib import Path

import pygame


# Diretórios de áudio
BASE_DIR = Path(__file__).resolve().parent

SOUNDS_DIR = BASE_DIR / "assets" / "sounds"
SFX_DIR = SOUNDS_DIR / "sfx"
BOSS_INTRO_END = pygame.USEREVENT + 2


# Músicas das fases
TRACKS = {
    "menu": SOUNDS_DIR / "menu.ogg",
    1: SOUNDS_DIR / "fase1.ogg",
    2: SOUNDS_DIR / "fase2.ogg",
    3: SOUNDS_DIR / "fase3.ogg",
    "boss_intro": SOUNDS_DIR / "intro_fase_final.ogg",
    4: SOUNDS_DIR / "fase_final.ogg",
    "ending": SOUNDS_DIR / "musica_final.ogg",
}


# Efeitos sonoros
SOUND_EFFECTS = {
    "menu_click": "menu_click.wav",
    "jump": "jump.wav",
    "attack": "attack.wav",
    "hurt": "hurt.wav",
    "enemy_hit": "enemy_hit.wav",
    "fall": "fall.wav",
    "collect": "collect.wav",
    "victory": "victory.wav",
}


class AudioManager:

    def __init__(self):

        self.current_phase = None
        self.muted = False
        self.boss_intro_started_at = None
        self._boss_intro_duration_ms = None
        self._boss_intro_finished = False
        self._boss_intro_seek_ms = 0

        # Volumes independentes
        self.music_volume = 0.35
        self.sfx_volume = 0.60

        self.available = pygame.mixer.get_init() is not None

        # Armazena os efeitos carregados
        self.sounds = {}

        if self.available:

            pygame.mixer.set_num_channels(16)

            pygame.mixer.music.set_volume(
                self.music_volume
            )

            self.load_sound_effects()

    # CARREGAMENTO DOS EFEITOS

    def boss_intro_duration_ms(self):
        if self._boss_intro_duration_ms is None:
            if self.available:
                sound = pygame.mixer.Sound(str(TRACKS["boss_intro"]))
                self._boss_intro_duration_ms = round(sound.get_length() * 1000)
            else:
                self._boss_intro_duration_ms = 3204
        return self._boss_intro_duration_ms

    def boss_intro_elapsed_ms(self):
        if self.boss_intro_started_at is None:
            return 0
        duration = self.boss_intro_duration_ms()
        if self._boss_intro_finished:
            return duration
        if self.available and not self.muted and self.current_phase == "boss_intro":
            # Só avança quando o mixer realmente começa a reproduzir.
            position = max(0, pygame.mixer.music.get_pos())
            return min(duration - 1, position + self._boss_intro_seek_ms)
        return max(0, pygame.time.get_ticks() - self.boss_intro_started_at)

    def start_boss_intro(self):
        self.boss_intro_started_at = pygame.time.get_ticks()
        self._boss_intro_finished = False
        self._boss_intro_seek_ms = 0
        self.current_phase = None
        self.set_phase("boss_intro")

    def finish_boss_intro(self):
        if self.current_phase == "boss_intro":
            # A música da luta já está na fila; não a interrompe ou reinicia.
            self.current_phase = 4

    def handle_music_event(self, event):
        if event.type != BOSS_INTRO_END or self.current_phase != "boss_intro" or self.muted:
            return False
        self._boss_intro_finished = True
        pygame.mixer.music.set_endevent()
        return True

    def load_sound_effects(self):

        for name, filename in SOUND_EFFECTS.items():

            sound_path = SFX_DIR / filename

            if not sound_path.exists():
                print(
                    f"Efeito sonoro não encontrado: "
                    f"{sound_path}"
                )
                continue

            try:

                sound = pygame.mixer.Sound(
                    str(sound_path)
                )

                sound.set_volume(self.sfx_volume)

                self.sounds[name] = sound

            except pygame.error as error:

                print(
                    f"Erro ao carregar {filename}: {error}"
                )

    # REPRODUÇÃO DE EFEITOS

    def play_sfx(self, name):

        if not self.available or self.muted:
            return

        sound = self.sounds.get(name)

        if sound is None:
            return

        sound.play()

    # MÚSICAS DAS FASES

    def set_phase(self, phase):

        if phase == self.current_phase:
            return

        self.current_phase = phase

        if not self.available:
            return

        pygame.mixer.music.set_endevent()
        pygame.mixer.music.stop()

        if phase is None or self.muted:
            return

        self.play_music(phase)

    def play_music(self, phase):

        if not self.available:
            return

        music_path = TRACKS.get(phase)

        if music_path is None:
            return

        if not music_path.exists():

            print(
                f"Música não encontrada: {music_path}"
            )
            return

        try:

            pygame.mixer.music.load(
                str(music_path)
            )

            pygame.mixer.music.set_volume(
                self.music_volume
            )

            if phase == "boss_intro":
                elapsed = self._boss_intro_seek_ms
                if elapsed >= self.boss_intro_duration_ms():
                    self.current_phase = 4
                    self._boss_intro_finished = True
                    self.play_music(4)
                    return
                pygame.mixer.music.set_endevent(BOSS_INTRO_END)
                pygame.mixer.music.play(loops=0, start=elapsed / 1000, fade_ms=0)
                pygame.mixer.music.queue(str(TRACKS[4]), loops=-1)
            else:
                pygame.mixer.music.play(loops=-1, fade_ms=400)

        except pygame.error as error:

            print(
                f"Erro ao reproduzir música: {error}"
            )

    # SILENCIAR ÁUDIO

    def toggle_mute(self):

        intro_position = self.boss_intro_elapsed_ms() if self.current_phase == "boss_intro" else None
        self.muted = not self.muted

        if not self.available:
            return self.muted

        if self.muted:

            pygame.mixer.music.set_endevent()
            pygame.mixer.music.stop()
            pygame.mixer.stop()

        elif self.current_phase is not None:

            if intro_position is not None:
                self._boss_intro_seek_ms = intro_position
            self.play_music(self.current_phase)

        return self.muted

    # CONTROLE DE VOLUME

    def set_volume(self, volume):

        self.music_volume = max(
            0.0,
            min(1.0, volume)
        )

        if self.available:

            pygame.mixer.music.set_volume(
                self.music_volume
            )

    def set_sfx_volume(self, volume):

        self.sfx_volume = max(
            0.0,
            min(1.0, volume)
        )

        for sound in self.sounds.values():

            sound.set_volume(
                self.sfx_volume
            )
