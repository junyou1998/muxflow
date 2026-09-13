import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_languages(self):
        res = self.client.get("/api/presets/languages")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data) > 50)
        # Check Chinese and Japanese are present
        codes = [item["code"] for item in data]
        self.assertIn("chi", codes)
        self.assertIn("jpn", codes)
        self.assertIn("eng", codes)

    def test_get_presets(self):
        res = self.client.get("/api/presets")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data) >= 1)
        self.assertEqual(data[0]["id"], "default")

    def test_files_browse(self):
        res = self.client.get("/api/files/browse")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("current_path", data)
        self.assertIn("directories", data)
        self.assertIn("files", data)

    def test_mux_status(self):
        res = self.client.get("/api/mux/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "idle")
        self.assertEqual(data["total_jobs"], 0)

    from unittest.mock import patch

    @patch("app.services.job_generator.MKVService.get_file_info")
    def test_queue_add_remove_clear(self, mock_info):
        mock_info.return_value = {
            "videos": [{"id": 0, "codec": "AVC/H.264"}],
            "audios": [{"id": 1, "codec": "AAC", "language": "und", "language_name": "Undetermined", "track_name": ""}],
            "subtitles": [],
            "attachments": [],
        }

        # 1. Clear queue initially
        res = self.client.post("/api/mux/clear")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["total_jobs"], 0)

        # 2. Add jobs to queue
        fake_job = {
            "source_video": "/fake/video1.mkv",
            "output_dir": "/tmp/test_mkv_out",
            "video_fps": "Default",
            "old_tracks_modifications": {},
            "subtitles": [],
            "audios": [],
            "chapter_file": None,
            "chapter_discard_old": False,
            "attachments": [],
            "attachments_discard_old": False,
            "attachments_allow_duplicates": False,
            "overwrite_source": False,
            "use_mkvpropedit": False,
            "add_crc": False,
            "remove_old_crc": False,
            "only_keep_audios_enabled": False,
            "only_keep_audios_ids": [],
            "only_keep_audios_langs": [],
            "only_keep_audios_names": [],
            "only_keep_subtitles_enabled": False,
            "only_keep_subtitles_ids": [],
            "only_keep_subtitles_langs": [],
            "only_keep_subtitles_names": [],
            "make_audio_default_enabled": False,
            "make_audio_default_target": "",
            "make_subtitle_default_enabled": False,
            "make_subtitle_default_target": "",
        }
        res = self.client.post("/api/mux/queue/add", json={"jobs": [fake_job, {**fake_job, "source_video": "/fake/video2.mkv"}]})
        self.assertEqual(res.status_code, 200)
        state = res.json()
        self.assertEqual(state["total_jobs"], 2)
        self.assertEqual(state["jobs"][0]["status"], "pending")
        self.assertEqual(state["jobs"][1]["status"], "pending")

        # 3. Remove single job
        res = self.client.delete("/api/mux/queue/0")
        self.assertEqual(res.status_code, 200)
        state = res.json()
        self.assertEqual(state["total_jobs"], 1)
        self.assertEqual(state["jobs"][0]["source_name"], "video2.mkv")

        # 4. Clear queue
        res = self.client.post("/api/mux/clear")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["total_jobs"], 0)

if __name__ == "__main__":
    unittest.main()

