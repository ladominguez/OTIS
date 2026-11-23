"""Tests for filename discovery, destination mapping and conservative resume."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from otis.batch_preprocessing import corrected_path, discover, previous_result


class BatchVelocityTests(unittest.TestCase):
    def test_discover_and_filters(self):
        with TemporaryDirectory() as root:
            base = Path(root)
            names = [
                "caig.ig.hhz.d.2024.256.0000",
                "caig.ig.hhn.d.2024.257.0000",
                "meig.ig.hhz.d.2024.256.0000",
                "caig.ig.hhz.d.2024.367.0000",  # bad Julian day
                "other.txt",
            ]
            for name in names:
                (base / name).write_bytes(b"x")
            (base / "processed").mkdir()
            (base / "processed" / "caig.ig.hhz.d.2024.256.0000").write_bytes(b"x")
            selected = list(discover(base, {"CAIG"}, {"HHZ"}))
            self.assertEqual([p.name for p in selected],
                             ["caig.ig.hhz.d.2024.256.0000"])

    def test_output_path(self):
        raw = Path("/input/2024/caig.ig.hhz.d.2024.256.0000")
        output = corrected_path(raw, Path("/input"), Path("/output"))
        self.assertEqual(output, Path("/output/2024/caig.ig.hhz.d.2024.256.0000.vel.sac"))

    def test_resume_valid_and_mismatch(self):
        with TemporaryDirectory() as root:
            base = Path(root)
            raw = base / "caig.ig.hhz.d.2024.256.0000"
            output = base / "caig.ig.hhz.d.2024.256.0000.vel.sac"
            output.write_bytes(b"x" * 1024)
            metadata = {
                "input_raw": str(raw),
                "output_sac": str(output),
                "output_quantity": "VEL",
                "output_units": "m/s",
                "pre_filt_hz": [0.02, 0.05, 5.0, 8.0],
                "taper_fraction": 0.001,
                "response_file": "CAIG.RESP",
            }
            Path(str(output) + ".json").write_text(json.dumps(metadata), encoding="utf-8")
            valid, reason = previous_result(
                output, raw, (0.02, 0.05, 5.0, 8.0), 0.001
            )
            self.assertTrue(valid, reason)
            valid, reason = previous_result(
                output, raw, (0.03, 0.05, 5.0, 8.0), 0.001
            )
            self.assertFalse(valid)
            self.assertIn("differs", reason)
            Path(str(output) + ".json").unlink()
            valid, reason = previous_result(
                output, raw, (0.02, 0.05, 5.0, 8.0), 0.001
            )
            self.assertFalse(valid)
            self.assertIn("Incomplete", reason)


if __name__ == "__main__":
    unittest.main()
