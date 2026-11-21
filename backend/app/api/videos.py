import os
from collections import defaultdict
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.mkv_service import MKVService

router = APIRouter(prefix="/api/videos", tags=["videos"])

class InspectRequest(BaseModel):
    file_path: str

class BatchTracksRequest(BaseModel):
    file_paths: List[str]

@router.post("/inspect")
def inspect_video(req: InspectRequest):
    try:
        info = MKVService.get_file_info(req.file_path)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze_tracks")
def analyze_batch_tracks(req: BatchTracksRequest):
    """
    Analyzes all tracks across the provided videos to aggregate bulk setting options.
    Returns:
    - distinct audio track IDs, languages, track names (for "Only Keep Those Audios")
    - distinct subtitle track IDs, languages, track names (for "Only Keep Those Subtitles")
    - bulk old track summaries for "Modify Old Tracks" tab (video, audio, subtitle tracks)
    """
    if not req.file_paths:
        return {
            "audios": {"ids": [], "languages": [], "names": []},
            "subtitles": {"ids": [], "languages": [], "names": []},
            "bulk_tracks": {"videos": [], "audios": [], "subtitles": []},
            "total_files": 0,
            "layout_groups": [],
        }

    audio_ids = set()
    audio_langs = set()
    audio_names = set()

    sub_ids = set()
    sub_langs = set()
    sub_names = set()

    # Group tracks by (type, n-th track of that type) across videos, so a file with an
    # extra audio track doesn't shift every later track out of alignment.
    # e.g. { "audios": { 0: [(file, track), ...], 1: [...] } }
    grouped_tracks = {
        "videos": defaultdict(list),
        "audios": defaultdict(list),
        "subtitles": defaultdict(list),
    }
    layout_groups: Dict[str, List[str]] = {}
    analyzed_files: List[str] = []

    for path in req.file_paths:
        try:
            info = MKVService.get_file_info(path)
        except Exception:
            continue
        analyzed_files.append(path)
        layout = " ".join(
            ["V"] * len(info["videos"]) + ["A"] * len(info["audios"]) + ["S"] * len(info["subtitles"])
        )
        layout_groups.setdefault(layout, []).append(os.path.basename(path))

        for idx, v in enumerate(info["videos"]):
            grouped_tracks["videos"][idx].append((path, v))
        for idx, a in enumerate(info["audios"]):
            audio_ids.add(f"Track {int(a['id']):02d}")
            if a.get("language_name") and a["language_name"] != "Undetermined":
                audio_langs.add(a["language_name"])
            if a.get("track_name"):
                audio_names.add(a["track_name"])
            grouped_tracks["audios"][idx].append((path, a))
        for idx, s in enumerate(info["subtitles"]):
            sub_ids.add(f"Track {int(s['id']):02d}")
            if s.get("language_name") and s["language_name"] != "Undetermined":
                sub_langs.add(s["language_name"])
            if s.get("track_name"):
                sub_names.add(s["track_name"])
            elif s.get("language_ietf") in ["zh-Hant", "zh-TW", "zh-HK"]:
                sub_names.add("繁中")
            elif s.get("language_ietf") in ["zh-Hans", "zh-CN", "zh-SG"]:
                sub_names.add("簡中")
            grouped_tracks["subtitles"][idx].append((path, s))

    total_files = len(analyzed_files)

    def summarize_tracks(type_key: str, track_dict):
        res = []
        for idx in sorted(track_dict):
            entries = track_dict[idx]
            tracks = [t for _, t in entries]
            present = {f for f, _ in entries}
            first = tracks[0]

            def distinct(getter):
                seen = []
                for t in tracks:
                    val = getter(t) or ""
                    if val not in seen:
                        seen.append(val)
                return seen

            names = distinct(lambda t: t.get("track_name"))
            langs = distinct(lambda t: t.get("language_ietf") or t.get("language"))
            lang_names = distinct(lambda t: t.get("language_name"))
            codecs = distinct(lambda t: t.get("codec"))
            defaults = {bool(t.get("is_default")) for t in tracks}
            forceds = {bool(t.get("is_forced")) for t in tracks}

            res.append({
                "id": f"{type_key}:{idx}",
                "index": idx,
                "real_ids": sorted({int(t["id"]) for t in tracks}),
                "file_count": len(present),
                "total_files": total_files,
                "missing_files": [os.path.basename(f) for f in analyzed_files if f not in present],
                "track_name": names[0] if len(names) == 1 else "[Old]",
                "language": langs[0] if len(langs) == 1 else "[Old]",
                "language_name": lang_names[0] if len(lang_names) == 1 else "[Old]",
                "language_ietf": first.get("language_ietf", ""),
                "distinct_names": names,
                "distinct_languages": lang_names,
                "is_default": 1 if len(defaults) > 1 else (2 if True in defaults else 0),
                "is_forced": 1 if len(forceds) > 1 else (2 if True in forceds else 0),
                "is_enabled": True,
                "codec": codecs[0] if len(codecs) == 1 else " / ".join(c for c in codecs if c),
            })
        return res

    return {
        "audios": {
            "ids": sorted(list(audio_ids)),
            "languages": sorted(list(audio_langs)),
            "names": sorted(list(audio_names)),
        },
        "subtitles": {
            "ids": sorted(list(sub_ids)),
            "languages": sorted(list(sub_langs)),
            "names": sorted(list(sub_names)),
        },
        "bulk_tracks": {
            "videos": summarize_tracks("video", grouped_tracks["videos"]),
            "audios": summarize_tracks("audio", grouped_tracks["audios"]),
            "subtitles": summarize_tracks("subtitle", grouped_tracks["subtitles"]),
        },
        "total_files": total_files,
        "layout_groups": [
            {"layout": layout, "count": len(files), "files": files}
            for layout, files in sorted(layout_groups.items(), key=lambda x: -len(x[1]))
        ],
    }
