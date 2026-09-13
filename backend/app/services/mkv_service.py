import json
import os
import subprocess
from typing import Any, Dict, List, Optional
from ..config import MKVMERGE_PATH
from ..iso_languages import get_language_name

# Cache mapping: file_path -> (mtime, parsed_data)
_INFO_CACHE: Dict[str, tuple[float, Dict[str, Any]]] = {}

class MKVService:
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Run `mkvmerge -J` on the video file and return structured track & container info."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        mtime = os.path.getmtime(file_path)
        if file_path in _INFO_CACHE:
            cached_mtime, cached_data = _INFO_CACHE[file_path]
            if cached_mtime == mtime:
                return cached_data

        cmd = [MKVMERGE_PATH, "-J", file_path]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8"
            )
            raw_data = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"mkvmerge failed to parse {file_path}: {e.stderr or e.stdout}")
        except Exception as e:
            raise RuntimeError(f"Error parsing file info for {file_path}: {str(e)}")

        parsed_info = MKVService._format_raw_info(file_path, raw_data)
        _INFO_CACHE[file_path] = (mtime, parsed_info)
        return parsed_info

    @staticmethod
    def _format_raw_info(file_path: str, raw: Dict[str, Any]) -> Dict[str, Any]:
        file_size = os.path.getsize(file_path)
        container = raw.get("container", {})
        tracks_raw = raw.get("tracks", [])
        attachments_raw = raw.get("attachments", [])
        chapters_raw = raw.get("chapters", [])

        videos: List[Dict[str, Any]] = []
        audios: List[Dict[str, Any]] = []
        subtitles: List[Dict[str, Any]] = []

        for t in tracks_raw:
            props = t.get("properties", {})
            t_type = t.get("type")
            lang_code = props.get("language", "und")
            lang_name = get_language_name(lang_code, "Undetermined")

            track_item = {
                "id": t.get("id"),
                "type": t_type,
                "codec": t.get("codec"),
                "track_name": props.get("track_name", ""),
                "language": lang_code,
                "language_name": lang_name,
                "is_default": bool(props.get("default_track", False)),
                "is_forced": bool(props.get("forced_track", False)),
                "is_enabled": bool(props.get("enabled_track", True)),
                "uid": props.get("uid", -1),
            }

            if t_type == "video":
                track_item["width"] = props.get("pixel_dimensions", "x").split("x")[0] if "pixel_dimensions" in props else None
                track_item["height"] = props.get("pixel_dimensions", "x").split("x")[-1] if "pixel_dimensions" in props else None
                track_item["display_dimensions"] = props.get("display_dimensions")
                videos.append(track_item)
            elif t_type == "audio":
                track_item["channels"] = props.get("audio_channels")
                track_item["sampling_frequency"] = props.get("audio_sampling_frequency")
                audios.append(track_item)
            elif t_type == "subtitles":
                subtitles.append(track_item)

        attachments = [
            {
                "id": a.get("id"),
                "file_name": a.get("file_name", "unnamed"),
                "content_type": a.get("content_type", ""),
                "size": a.get("size", 0),
                "description": a.get("description", "")
            }
            for a in attachments_raw
        ]

        return {
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "file_size": file_size,
            "container_type": container.get("type", "matroska"),
            "recognized": container.get("recognized", True),
            "supported": container.get("supported", True),
            "videos": videos,
            "audios": audios,
            "subtitles": subtitles,
            "attachments": attachments,
            "has_chapters": len(chapters_raw) > 0,
            "chapters_count": len(chapters_raw),
        }
