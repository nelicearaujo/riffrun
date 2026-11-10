import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from audio import AudioManager, TRACKS, BOSS_INTRO_END
from boss import BossArena


class BossAudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def manager(self):
        with patch.object(AudioManager, "load_sound_effects"):
            return AudioManager()

    def test_animation_uses_actual_audio_duration_even_with_irregular_frames(self):
        manager = self.manager()
        duration = manager.boss_intro_duration_ms()
        self.assertGreater(duration, 3200)
        self.assertLess(duration, 3210)
        arena = BossArena(duration)
        for elapsed in (0, 127, 800, 1490, 2600, duration - 1):
            arena.update(intro_elapsed_ms=elapsed)
            self.assertGreater(arena.boss.intro_timer, 0)
            self.assertFalse(arena.boss.can_damage)
        arena.update(intro_elapsed_ms=duration)
        self.assertEqual(arena.boss.intro_timer, 0)
        self.assertEqual(arena.boss.rect.x, 1000)

    def test_intro_plays_once_and_queues_loop_without_restarting_transition(self):
        manager = self.manager()
        with patch("audio.pygame.mixer.music") as music:
            manager.start_boss_intro()
            music.load.assert_called_with(str(TRACKS["boss_intro"]))
            self.assertEqual(music.play.call_args.kwargs["loops"], 0)
            music.queue.assert_called_once_with(str(TRACKS[4]), loops=-1)
            manager.finish_boss_intro()
            manager.set_phase(4)
            self.assertEqual(music.load.call_count, 1)
            self.assertEqual(music.play.call_count, 1)

    def test_muted_intro_still_finishes_and_unmute_plays_fight(self):
        manager = self.manager()
        manager.muted = True
        with patch("audio.pygame.mixer.music") as music:
            manager.start_boss_intro()
            music.play.assert_not_called()
            manager.finish_boss_intro()
            manager.toggle_mute()
            music.load.assert_called_with(str(TRACKS[4]))
            self.assertEqual(music.play.call_args.kwargs["loops"], -1)

    def test_unmuting_during_intro_seeks_instead_of_restarting(self):
        manager = self.manager()
        with patch("audio.pygame.mixer.music") as music:
            music.get_pos.return_value = 0
            manager.start_boss_intro()
            manager.toggle_mute()
            with patch.object(manager, "boss_intro_elapsed_ms", return_value=1500):
                manager.toggle_mute()
            self.assertEqual(music.play.call_args.kwargs["start"], 1.5)
            music.queue.assert_called_with(str(TRACKS[4]), loops=-1)

    def test_loading_delay_cannot_advance_intro_before_audio_starts(self):
        manager = self.manager()
        with patch("audio.pygame.mixer.music") as music:
            music.get_pos.return_value = -1
            manager.start_boss_intro()
            with patch("audio.pygame.time.get_ticks", return_value=999999):
                self.assertEqual(manager.boss_intro_elapsed_ms(), 0)
            music.get_pos.return_value = manager.boss_intro_duration_ms() + 500
            self.assertLess(manager.boss_intro_elapsed_ms(), manager.boss_intro_duration_ms())
            self.assertTrue(manager.handle_music_event(pygame.event.Event(BOSS_INTRO_END)))
            self.assertEqual(manager.boss_intro_elapsed_ms(), manager.boss_intro_duration_ms())
