import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.services.job_generator import JobGenerator

# A: video / jpn audio / chi subtitle  (3 tracks)
FILE_A = {
    "videos": [{"id": 0, "codec": "HEVC"}],
    "audios": [{"id": 1, "codec": "FLAC", "language": "jpn", "language_name": "Japanese", "track_name": ""}],
    "subtitles": [{"id": 2, "codec": "ASS", "language": "chi", "language_ietf": "zh-Hant", "language_name": "Chinese", "track_name": ""}],
    "attachments": [],
}
# B: video / jpn audio / eng audio / chi subtitle  (4 tracks)
FILE_B = {
    "videos": [{"id": 0, "codec": "HEVC"}],
    "audios": [
        {"id": 1, "codec": "FLAC", "language": "jpn", "language_name": "Japanese", "track_name": ""},
        {"id": 2, "codec": "AAC", "language": "eng", "language_name": "English", "track_name": "Commentary"},
    ],
    "subtitles": [{"id": 3, "codec": "ASS", "language": "chi", "language_ietf": "zh-Hant", "language_name": "Chinese", "track_name": ""}],
    "attachments": [],
}


def mkvmerge(job, info):
    return JobGenerator._build_mkvmerge_cmd(job, info, "/s/x.mkv", "/o/x.mkv")


class TestPositionalMatching(unittest.TestCase):
    def test_nth_subtitle_lines_up_across_layouts(self):
        job = {"old_tracks_modifications": {"subtitle:0": {"track_name": "繁中"}}}
        self.assertEqual(JobGenerator.resolve_track_mods(job, FILE_A), {"2": {"track_name": "繁中"}})
        self.assertEqual(JobGenerator.resolve_track_mods(job, FILE_B), {"3": {"track_name": "繁中"}})

    def test_removing_second_audio_does_not_touch_other_file_subtitle(self):
        job = {"old_tracks_modifications": {"audio:1": {"is_enabled": False}}}
        cmd_a = mkvmerge(job, FILE_A)
        cmd_b = mkvmerge(job, FILE_B)
        # A has no 2nd audio: everything kept
        self.assertIn("-a", cmd_a); self.assertEqual(cmd_a[cmd_a.index("-a") + 1], "1")
        self.assertIn("-s", cmd_a); self.assertEqual(cmd_a[cmd_a.index("-s") + 1], "2")
        # B drops only the English audio
        self.assertEqual(cmd_b[cmd_b.index("-a") + 1], "1")
        self.assertEqual(cmd_b[cmd_b.index("-s") + 1], "3")

    def test_untouched_fields_emit_nothing(self):
        job = {"old_tracks_modifications": {"audio:0": {"is_enabled": True, "track_name": "", "language": "[Old]", "is_default": None, "is_forced": 1}}}
        self.assertEqual(JobGenerator.resolve_track_mods(job, FILE_B), {})
        cmd = mkvmerge(job, FILE_B)
        self.assertNotIn("--default-track-flag", cmd)
        self.assertNotIn("--track-name", cmd)

    def test_legacy_numeric_keys_still_work(self):
        job = {"old_tracks_modifications": {"1": {"track_name": "Japanese", "is_default": 2, "is_forced": 0}}}
        self.assertEqual(
            JobGenerator.resolve_track_mods(job, FILE_A),
            {"1": {"track_name": "Japanese", "is_default": True, "is_forced": False}},
        )


class TestTrackRules(unittest.TestCase):
    def test_rule_matches_by_language_in_every_layout(self):
        job = {"track_rules": [
            {"track_type": "audio", "match_language": "Japanese", "set_name": "日語", "set_default": True},
            {"track_type": "audio", "match_language": "eng", "remove": True},
        ]}
        cmd_b = mkvmerge(job, FILE_B)
        self.assertIn("1:日語", cmd_b)
        self.assertIn("1:yes", cmd_b)
        self.assertEqual(cmd_b[cmd_b.index("-a") + 1], "1")
        cmd_a = mkvmerge(job, FILE_A)
        self.assertIn("1:日語", cmd_a)
        self.assertEqual(cmd_a[cmd_a.index("-s") + 1], "2")

    def test_rule_name_contains_and_type_filter(self):
        job = {"track_rules": [{"track_type": "subtitle", "match_name": "comment", "remove": True}]}
        self.assertEqual(JobGenerator.resolve_track_mods(job, FILE_B), {})
        job["track_rules"][0]["track_type"] = "any"
        self.assertEqual(JobGenerator.resolve_track_mods(job, FILE_B), {"2": {"is_enabled": False}})

    def test_rule_matches_zh_hant_display_name(self):
        job = {"track_rules": [{"track_type": "subtitle", "match_name": "繁中", "set_default": True}]}
        self.assertEqual(JobGenerator.resolve_track_mods(job, FILE_B), {"3": {"is_default": True}})

    def test_disabled_rule_ignored_and_rule_overrides_positional(self):
        job = {
            "old_tracks_modifications": {"audio:0": {"track_name": "A"}},
            "track_rules": [
                {"enabled": False, "track_type": "audio", "set_name": "X"},
                {"track_type": "audio", "match_language": "jpn", "set_name": "B"},
            ],
        }
        self.assertEqual(JobGenerator.resolve_track_mods(job, FILE_A)["1"]["track_name"], "B")

    def test_removal_rule_blocks_mkvpropedit(self):
        job = {"use_mkvpropedit": True, "source_video": "/s/x.mkv",
               "track_rules": [{"track_type": "audio", "match_language": "eng", "remove": True}]}
        self.assertFalse(JobGenerator.can_use_mkvpropedit(job, FILE_B))
        self.assertTrue(JobGenerator.can_use_mkvpropedit(job, FILE_A))

    def test_mkvpropedit_uses_resolved_mods(self):
        job = {"track_rules": [{"track_type": "subtitle", "match_language": "chi", "set_forced": False}]}
        cmd = JobGenerator._build_mkvpropedit_cmd(job, FILE_B, "/s/x.mkv")
        self.assertIn("track:4", cmd)
        self.assertIn("flag-forced=0", cmd)


class TestBatchAnalysis(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("app.api.videos.MKVService.get_file_info")
    def test_groups_by_type_position_with_coverage(self, mock_info):
        mock_info.side_effect = lambda p: FILE_A if p.endswith("a.mkv") else FILE_B
        res = self.client.post("/api/videos/analyze_tracks", json={"file_paths": ["/v/a.mkv", "/v/b.mkv"]})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        audios = data["bulk_tracks"]["audios"]
        subs = data["bulk_tracks"]["subtitles"]
        self.assertEqual([a["id"] for a in audios], ["audio:0", "audio:1"])
        self.assertEqual(audios[1]["file_count"], 1)
        self.assertEqual(audios[1]["missing_files"], ["a.mkv"])
        # The subtitle is one group even though its real ID differs (2 vs 3)
        self.assertEqual(len(subs), 1)
        self.assertEqual(subs[0]["id"], "subtitle:0")
        self.assertEqual(subs[0]["real_ids"], [2, 3])
        self.assertEqual(subs[0]["file_count"], 2)
        self.assertEqual(data["total_files"], 2)
        self.assertEqual(len(data["layout_groups"]), 2)
        self.assertEqual([t["type"] for t in data["file_tracks"]["/v/b.mkv"]], ["video", "audio", "audio", "subtitle"])
        self.assertEqual(data["file_tracks"]["/v/a.mkv"][2]["language"], "zh-Hant")


if __name__ == "__main__":
    unittest.main()
