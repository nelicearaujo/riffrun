import unittest

from scoring import RunScore


class ScoringTests(unittest.TestCase):
    def test_defeat_awards_only_collected_riffs_and_freezes_time(self):
        run = RunScore()
        run.advance(25_000)
        result = run.finish(4, completed=False)
        run.advance(5000)
        self.assertEqual(result.total, 4000)
        self.assertEqual(result.time_bonus, 0)
        self.assertEqual(run.elapsed_ms, 25_000)

    def test_riffs_and_time_both_contribute(self):
        run = RunScore()
        run.advance(75_000)
        result = run.finish(8)
        self.assertEqual(result.riff_points, 8000)
        self.assertEqual(result.time_bonus, 1050)
        self.assertEqual(result.total, 9050)
        self.assertEqual(result.time_text, "01:15")

    def test_slow_completions_keep_riff_points_without_negative_bonus(self):
        run = RunScore()
        run.advance(240_000)
        result = run.finish(10)
        self.assertEqual(result.total, 10000)
        self.assertEqual(result.time_bonus, 0)

    def test_result_and_time_freeze_after_finish(self):
        run = RunScore()
        run.advance(20_000)
        result = run.finish(5)
        run.advance(90_000)
        self.assertIs(run.finish(10), result)
        self.assertEqual(run.elapsed_ms, 20_000)
        self.assertEqual(result.riffs, 5)

    def test_new_attempt_starts_from_zero(self):
        previous = RunScore()
        previous.advance(80_000)
        previous.finish(7)
        new = RunScore()
        self.assertEqual(new.elapsed_ms, 0)
        self.assertIsNone(new.result)

    def test_more_riffs_outweigh_small_time_differences(self):
        fast = RunScore()
        fast.advance(60_000)
        collector = RunScore()
        collector.advance(90_000)
        self.assertGreater(collector.finish(10).total, fast.finish(9).total)
