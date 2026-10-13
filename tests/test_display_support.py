import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))

from display_support import (
    MAP_CAPTURE_PROFILES,
    RESOLUTION_DIMENSIONS,
    calculate_map_scale,
    calculate_capture_region,
    configure_tk_scaling,
    get_game_capture_region,
    scale_pixels,
)


class DisplaySupportTests(unittest.TestCase):
    def test_tk_scaling_tracks_monitor_dpi(self):
        class TkStub:
            def __init__(self):
                self.calls = []

            def call(self, *args):
                self.calls.append(args)

        class RootStub:
            def __init__(self):
                self.tk = TkStub()

            def winfo_id(self):
                return 1

        root = RootStub()
        with patch('display_support.get_window_dpi', side_effect=(96, 144, 192)):
            scales = [configure_tk_scaling(root) for _ in range(3)]

        self.assertEqual(scales, [1.0, 1.5, 2.0])
        self.assertEqual(
            [call[2] for call in root.tk.calls],
            [96 / 72, 144 / 72, 192 / 72],
        )

    def test_each_profile_crop_fits_its_client(self):
        self.assertEqual(set(MAP_CAPTURE_PROFILES), set(RESOLUTION_DIMENSIONS))
        for resolution, profile in MAP_CAPTURE_PROFILES.items():
            width, height = RESOLUTION_DIMENSIONS[resolution]
            self.assertLessEqual(profile[0] + profile[2], width)
            self.assertLessEqual(profile[1] + profile[3], height)

    def test_game_crop_translates_from_client_to_screen(self):
        self.assertEqual(
            get_game_capture_region((640, 360, 2560, 1440), '5'),
            (2595, 1195, 605, 605),
        )

    def test_wrong_client_resolution_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'requires 2560x1440'):
            get_game_capture_region((0, 0, 3840, 2160), '5')

    def test_crop_outside_client_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'outside the game client'):
            calculate_capture_region(
                (0, 0, 2560, 1440),
                (2500, 1400, 100, 100),
                (2560, 1440),
            )

    def test_pixel_sizes_follow_dpi_scale(self):
        self.assertEqual([scale_pixels(10, scale) for scale in (1.0, 1.5, 2.0)], [10, 15, 20])
        self.assertEqual(scale_pixels(15, 1.5), 23)

    def test_scale_uses_high_confidence_vertical_labels(self):
        matches = [(1, 612, 0.5933), (5, 612, 0.8282), (7, 782, 0.9051)]
        self.assertAlmostEqual(calculate_map_scale(matches, 250), 250 / 85)

    def test_scale_rejects_missing_or_duplicate_labels(self):
        with self.assertRaisesRegex(ValueError, 'two distinct map grid labels'):
            calculate_map_scale([(1, 612, 0.5), (5, 612, 0.8)], 250)


if __name__ == '__main__':
    unittest.main()