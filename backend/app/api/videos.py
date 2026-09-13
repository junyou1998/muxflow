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
        }

    audio_ids = set()
    audio_langs = set()
    audio_names = set()

    sub_ids = set()
    sub_langs = set()
    sub_names = set()

    # Track by track_id across videos for bulk modification
    # e.g. { "video": { "0": [track_obj, ...], "1": [...] } }
    grouped_tracks = {
        "videos": defaultdict(list),
        "audios": defaultdict(list),
        "subtitles": defaultdict(list),
    }

    for path in req.file_paths:
        try:
            info = MKVService.get_file_info(path)
            for v in info["videos"]:
                grouped_tracks["videos"][str(v["id"])].append(v)
            for a in info["audios"]:
                t_id = f"Track {int(a['id']):02d}"
                audio_ids.add(t_id)
                if a.get("language_name") and a["language_name"] != "Undetermined":
                    audio_langs.add(a["language_name"])
                if a.get("track_name"):
                    audio_names.add(a["track_name"])
                grouped_tracks["audios"][str(a["id"])].append(a)
            for s in info["subtitles"]:
                t_id = f"Track {int(s['id']):02d}"
                sub_ids.add(t_id)
                if s.get("language_name") and s["language_name"] != "Undetermined":
                    sub_langs.add(s["language_name"])
                if s.get("track_name"):
                    sub_names.add(s["track_name"])
                grouped_tracks["subtitles"][str(s["id"])].append(s)
        except Exception:
            continue

    def summarize_tracks(track_dict):
        res = []
        for t_id, t_list in sorted(track_dict.items(), key=lambda x: int(x[0])):
            first = t_list[0]
            # Check if all files have the same properties
            same_name = all(x.get("track_name") == first.get("track_name") for x in t_list)
            same_lang = all(x.get("language") == first.get("language") for x in t_list)
            same_default = all(x.get("is_default") == first.get("is_default") for x in t_list)
            same_forced = all(x.get("is_forced") == first.get("is_forced") for x in t_list)

            res.append({
                "id": t_id,
                "track_name": first.get("track_name") if same_name else "[Old]",
                "language": first.get("language") if same_lang else "[Old]",
                "language_name": first.get("language_name") if same_lang else "[Old]",
                "is_default": 2 if same_default and first.get("is_default") else (0 if same_default and not first.get("is_default") else 1),
                "is_forced": 2 if same_forced and first.get("is_forced") else (0 if same_forced and not first.get("is_forced") else 1),
                "is_enabled": True,
                "codec": first.get("codec", ""),
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
            "videos": summarize_tracks(grouped_tracks["videos"]),
            "audios": summarize_tracks(grouped_tracks["audios"]),
            "subtitles": summarize_tracks(grouped_tracks["subtitles"]),
        }
    }
