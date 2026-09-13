import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.iso_languages import get_language_code, get_language_name
from app.services.job_generator import JobGenerator
from app.api.files import natural_sort_key

class TestMKVGenerator(unittest.TestCase):
    def test_iso_languages(self):
        self.assertEqual(get_language_code("Japanese"), "jpn")
        self.assertEqual(get_language_code("English"), "eng")
        self.assertEqual(get_language_name("chi"), "Chinese")
        self.assertEqual(get_language_name("jpn"), "Japanese")

    def test_natural_sort(self):
        files = ["Ep 10.mkv", "Ep 1.mkv", "Ep 2.mkv", "Ep 20.mkv"]
        sorted_files = sorted(files, key=natural_sort_key)
        self.assertEqual(sorted_files, ["Ep 1.mkv", "Ep 2.mkv", "Ep 10.mkv", "Ep 20.mkv"])

    def test_crc_cleaning(self):
        filename = "MyMovie [A1B2C3D4].mkv"
        cleaned = JobGenerator.clean_old_crc(filename)
        self.assertEqual(cleaned, "MyMovie.mkv")

        filename2 = "Show S01E01 [12345678].mp4"
        cleaned2 = JobGenerator.clean_old_crc(filename2)
        self.assertEqual(cleaned2, "Show S01E01.mp4")

    def test_build_mkvmerge_cmd(self):
        fake_source_info = {
            "videos": [{"id": 0, "codec": "AVC/H.264"}],
            "audios": [{"id": 1, "codec": "AAC", "language": "jpn", "language_name": "Japanese", "track_name": "Orig"}],
            "subtitles": [{"id": 2, "codec": "SubRip/SRT", "language": "eng", "language_name": "English", "track_name": "Sub"}],
            "attachments": [],
        }

        job_config = {
            "source_video": "/storage/video.mkv",
            "output_dir": "/storage/out",
            "video_fps": "23.976p",
            "subtitles": [
                {
                    "file_path": "/storage/sub_tc.srt",
                    "track_name": "Traditional Chinese",
                    "language": "chi",
                    "delay": 500,
                    "is_default": True,
                    "is_forced": False,
                }
            ],
            "audios": [
                {
                    "file_path": "/storage/audio_commentary.m4a",
                    "track_name": "Commentary",
                    "language": "eng",
                    "delay": 0,
                    "is_default": False,
                    "is_forced": False,
                }
            ],
            "old_tracks_modifications": {
                "1": {
                    "is_enabled": True,
                    "track_name": "Japanese Stereo",
                    "language": "Japanese",
                    "is_default": 2,
                    "is_forced": 0,
                }
            },
            "chapter_discard_old": False,
            "attachments_discard_old": False,
        }

        cmd = JobGenerator._build_mkvmerge_cmd(
            job_config=job_config,
            source_info=fake_source_info,
            source_path="/storage/video.mkv",
            output_path="/storage/out/video.mkv"
        )

        self.assertIn("-o", cmd)
        self.assertIn("/storage/out/video.mkv", cmd)
        self.assertIn("--default-duration", cmd)
        self.assertIn("0:23.976p", cmd)
        self.assertIn("--track-name", cmd)
        self.assertIn("1:Japanese Stereo", cmd)
        self.assertIn("/storage/sub_tc.srt", cmd)
        self.assertIn("/storage/audio_commentary.m4a", cmd)
        self.assertIn("--sync", cmd)
        self.assertIn("0:500", cmd)
        print("Generated mkvmerge cmd successfully:", " ".join(cmd))

    from unittest.mock import patch

    @patch("app.services.job_generator.MKVService.get_file_info")
    def test_overwrite_safety_guard(self, mock_info):
        mock_info.return_value = {
            "videos": [{"id": 0, "codec": "AVC/H.264"}],
            "audios": [{"id": 1, "codec": "AAC", "language": "und", "language_name": "Undetermined", "track_name": ""}],
            "subtitles": [],
            "attachments": [],
        }

        # Case 1: Same directory, overwrite_source=False -> output MUST be _muxed.mkv
        job_config_no_overwrite = {
            "source_video": "/storage/my_video.mkv",
            "output_dir": "/storage",
            "overwrite_source": False,
            "video_fps": "24p",  # force mkvmerge
        }
        job1 = JobGenerator.generate_job(job_config_no_overwrite)
        self.assertEqual(job1["output_path"], "/storage/my_video_muxed.mkv")
        self.assertFalse(job1["is_overwrite"])
        self.assertIsNone(job1["temp_output_path"])

        # Case 2: Same directory, overwrite_source=True -> output is original name, uses temp file
        job_config_overwrite = {
            "source_video": "/storage/my_video.mkv",
            "output_dir": "/storage",
            "overwrite_source": True,
            "video_fps": "24p",
        }
        job2 = JobGenerator.generate_job(job_config_overwrite)
        self.assertEqual(job2["output_path"], "/storage/my_video.mkv")
        self.assertTrue(job2["is_overwrite"])
        self.assertEqual(job2["temp_output_path"], "/storage/my_video#temp_mux.mkv")

if __name__ == "__main__":
    unittest.main()
