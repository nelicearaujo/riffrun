from pathlib import Path

import pygame


# Diretórios de áudio
BASE_DIR = Path(__file__).resolve().parent

SOUNDS_DIR = BASE_DIR / "assets" / "sounds"
SFX_DIR = SOUNDS_DIR / "sfx"


# Músicas das fases
TRACKS = {
    1: SOUNDS_DIR / "fase1.ogg",
    2: SOUNDS_DIR / "fase2.ogg",
    3: SOUNDS_DIR / "fase3.ogg",
}


# Efeitos sonoros
SOUND_EFFECTS = {
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

            pygame.mixer.music.play(
                loops=-1,
                fade_ms=400
            )

        except pygame.error as error:

            print(
                f"Erro ao reproduzir música: {error}"
            )

    # SILENCIAR ÁUDIO

    def toggle_mute(self):

        self.muted = not self.muted

        if not self.available:
            return self.muted

        if self.muted:

            pygame.mixer.music.stop()
            pygame.mixer.stop()

        elif self.current_phase is not None:

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