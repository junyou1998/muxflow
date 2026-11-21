import os
import re
from typing import Any, Dict, List, Optional, Tuple
from ..config import MKVMERGE_PATH, MKVPROPEDIT_PATH
from ..iso_languages import get_language_code
from .mkv_service import MKVService

CRC_REGEX = re.compile(r"\[[0-9A-Fa-f]{8}\]")

TYPE_KEYS = (("video", "videos"), ("audio", "audios"), ("subtitle", "subtitles"))
ZH_HANT_TAGS = ("zh-Hant", "zh-TW", "zh-HK")
ZH_HANS_TAGS = ("zh-Hans", "zh-CN", "zh-SG")


def _is_keep(value: Any) -> bool:
    """A modification value that means "leave the existing property alone"."""
    return value in (None, "", "[Old]")


def _flag_value(value: Any) -> Optional[bool]:
    """Normalize tri-state flags: True/2 -> set, False/0 -> clear, anything else -> keep."""
    if value is True or value == 2:
        return True
    if value is False or value == 0:
        return False
    return None


def _track_matches_lang(track: Dict[str, Any], wanted: str) -> bool:
    wanted = wanted.strip().lower()
    if not wanted:
        return True
    candidates = [track.get("language"), track.get("language_ietf"), track.get("language_name")]
    if any(c and str(c).lower() == wanted for c in candidates):
        return True
    try:
        code = get_language_code(wanted, None)
    except Exception:
        code = None
    return bool(code) and str(track.get("language") or "").lower() == str(code).lower()


def _track_display_name(track: Dict[str, Any]) -> str:
    if track.get("track_name"):
        return track["track_name"]
    ietf = track.get("language_ietf")
    if ietf in ZH_HANT_TAGS:
        return "繁中"
    if ietf in ZH_HANS_TAGS:
        return "簡中"
    return ""


def _track_matches_rule(track: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    if not _track_matches_lang(track, str(rule.get("match_language") or "")):
        return False
    wanted_name = str(rule.get("match_name") or "").strip().lower()
    if wanted_name and wanted_name not in _track_display_name(track).lower():
        return False
    return True


class JobGenerator:
    @staticmethod
    def clean_old_crc(filename: str) -> str:
        """Remove [XXXXXXXX] CRC from filename."""
        name, ext = os.path.splitext(filename)
        cleaned_name = CRC_REGEX.sub("", name).strip()
        return cleaned_name + ext

    @staticmethod
    def resolve_track_mods(job_config: Dict[str, Any], source_info: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Translate batch-level track modifications into per-file modifications keyed by
        this file's real mkvmerge track ID.

        Two sources, applied in order (later wins per field):
        1. `old_tracks_modifications`: keyed by "<type>:<n>" = the n-th (0-based) track
           of that type in each file, so files with different layouts still line up by
           "2nd audio track" rather than by global track ID. Plain numeric keys are
           legacy global IDs and only apply to a track of the same ID.
        2. `track_rules`: match by type / language / name, e.g. "every jpn audio track".
        """
        resolved: Dict[str, Dict[str, Any]] = {}

        def merge(track_id: str, mod: Dict[str, Any]) -> None:
            target = resolved.setdefault(track_id, {})
            for field in ("track_name", "language"):
                if not _is_keep(mod.get(field)):
                    target[field] = mod[field]
            for field in ("is_default", "is_forced"):
                flag = _flag_value(mod.get(field))
                if flag is not None:
                    target[field] = flag
            if mod.get("is_enabled") in (False, 0):
                target["is_enabled"] = False

        mods = job_config.get("old_tracks_modifications") or {}
        for type_key, list_key in TYPE_KEYS:
            for index, track in enumerate(source_info.get(list_key, [])):
                t_id = str(track["id"])
                if t_id in mods:
                    merge(t_id, mods[t_id])
                key = f"{type_key}:{index}"
                if key in mods:
                    merge(t_id, mods[key])

        for rule in job_config.get("track_rules") or []:
            if not rule or rule.get("enabled") is False:
                continue
            rule_type = rule.get("track_type") or "any"
            for type_key, list_key in TYPE_KEYS:
                if type_key == "video" and rule_type != "video":
                    continue
                if rule_type not in ("any", type_key):
                    continue
                for track in source_info.get(list_key, []):
                    if _track_matches_rule(track, rule):
                        merge(str(track["id"]), {
                            "track_name": rule.get("set_name"),
                            "language": rule.get("set_language"),
                            "is_default": rule.get("set_default"),
                            "is_forced": rule.get("set_forced"),
                            "is_enabled": False if rule.get("remove") else True,
                        })

        return {t_id: mod for t_id, mod in resolved.items() if mod}

    @staticmethod
    def can_use_mkvpropedit(job_config: Dict[str, Any], source_info: Dict[str, Any]) -> bool:
        """
        Check if the job can be done via mkvpropedit (in-place modification) instead of full remuxing.
        Only possible if:
        1. User checked `use_mkvpropedit`
        2. Input container is Matroska (.mkv)
        3. No new external audio/subtitles/videos are being added
        4. No old tracks are being deleted (disabled)
        5. No fps/duration change or track deletion/filtering
        """
        if not job_config.get("use_mkvpropedit", False):
            return False
        
        # Check container
        source_path = job_config.get("source_video")
        if not source_path.lower().endswith(".mkv"):
            return False

        # If any new tracks are added, must use mkvmerge
        if job_config.get("subtitles") or job_config.get("audios"):
            return False

        # If only_keep filters are active and exclude any tracks
        if job_config.get("only_keep_audios_enabled") or job_config.get("only_keep_subtitles_enabled"):
            return False

        # Check if old tracks were disabled (deleted)
        resolved = JobGenerator.resolve_track_mods(job_config, source_info)
        if any(mod.get("is_enabled") is False for mod in resolved.values()):
            return False

        if job_config.get("video_fps") and job_config.get("video_fps") != "Default":
            return False

        return True

    @staticmethod
    def generate_job(job_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate execution command and metadata for a single video file.
        Returns:
        {
            "tool": "mkvmerge" | "mkvpropedit",
            "cmd": List[str],
            "source_path": str,
            "output_path": str,
            "temp_output_path": Optional[str],
            "is_overwrite": bool,
            "add_crc": bool,
            "remove_old_crc": bool,
        }
        """
        source_path = job_config["source_video"]
        source_dir = os.path.dirname(source_path)
        source_name = os.path.basename(source_path)
        
        # Fetch or get cached source info
        source_info = MKVService.get_file_info(source_path)

        # Determine output file path
        output_dir = job_config.get("output_dir") or source_dir
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError:
            pass

        is_overwrite = job_config.get("overwrite_source", False)
        remove_old_crc = job_config.get("remove_old_crc", False)
        add_crc = job_config.get("add_crc", False)

        final_filename = source_name
        if remove_old_crc:
            final_filename = JobGenerator.clean_old_crc(final_filename)

        # Output extension is always .mkv
        name_no_ext = os.path.splitext(final_filename)[0]
        final_filename = f"{name_no_ext}.mkv"

        final_output_path = os.path.join(output_dir, final_filename)
        is_same_file = (os.path.abspath(source_path) == os.path.abspath(final_output_path))

        # SAFETY GUARD: If destination is the same file as source, and overwrite is NOT explicitly enabled,
        # never overwrite original! Append _muxed to filename instead to protect source file.
        if is_same_file and not is_overwrite:
            final_filename = f"{name_no_ext}_muxed.mkv"
            final_output_path = os.path.join(output_dir, final_filename)
            is_same_file = False

        # Check if we can use mkvpropedit
        if JobGenerator.can_use_mkvpropedit(job_config, source_info):
            cmd = JobGenerator._build_mkvpropedit_cmd(job_config, source_info, source_path)
            return {
                "tool": "mkvpropedit",
                "cmd": cmd,
                "source_path": source_path,
                "output_path": source_path, # In-place
                "temp_output_path": None,
                "is_overwrite": False,
                "add_crc": add_crc,
                "remove_old_crc": remove_old_crc,
            }
        else:
            # Need mkvmerge
            temp_output_path = None
            if is_overwrite and is_same_file:
                # Temporary output file for safe atomic replacement
                temp_output_path = os.path.join(output_dir, f"{name_no_ext}#temp_mux.mkv")
                actual_target = temp_output_path
            else:
                actual_target = final_output_path

            cmd = JobGenerator._build_mkvmerge_cmd(job_config, source_info, source_path, actual_target)
            return {
                "tool": "mkvmerge",
                "cmd": cmd,
                "source_path": source_path,
                "output_path": final_output_path,
                "temp_output_path": temp_output_path,
                "is_overwrite": bool(is_overwrite and is_same_file),
                "add_crc": add_crc,
                "remove_old_crc": remove_old_crc,
            }

    @staticmethod
    def _build_mkvpropedit_cmd(
        job_config: Dict[str, Any],
        source_info: Dict[str, Any],
        source_path: str
    ) -> List[str]:
        cmd = [MKVPROPEDIT_PATH, source_path]
        old_mods = JobGenerator.resolve_track_mods(job_config, source_info)

        # Track property modifications
        for track in source_info["videos"] + source_info["audios"] + source_info["subtitles"]:
            t_id = str(track["id"])
            if t_id in old_mods:
                mod = old_mods[t_id]
                # mkvpropedit uses 1-based track numbers: track:<id+1>
                track_selector = f"track:{int(t_id) + 1}"

                if "track_name" in mod:
                    cmd.extend(["--edit", track_selector, "--set", f"name={mod['track_name']}"])
                if "language" in mod:
                    lang_code = get_language_code(mod["language"], mod["language"])
                    cmd.extend(["--edit", track_selector, "--set", f"language={lang_code}"])
                if "is_default" in mod:
                    cmd.extend(["--edit", track_selector, "--set", f"flag-default={1 if mod['is_default'] else 0}"])
                if "is_forced" in mod:
                    cmd.extend(["--edit", track_selector, "--set", f"flag-forced={1 if mod['is_forced'] else 0}"])

        # Chapters
        if job_config.get("chapter_file"):
            cmd.extend(["--chapters", job_config["chapter_file"]])
        elif job_config.get("chapter_discard_old"):
            cmd.extend(["--chapters", ""])

        # Attachments
        if job_config.get("attachments_discard_old"):
            cmd.extend(["--delete-attachment", "all"])
        
        for att in job_config.get("attachments", []):
            cmd.extend(["--add-attachment", att["file_path"]])

        return cmd

    @staticmethod
    def _build_mkvmerge_cmd(
        job_config: Dict[str, Any],
        source_info: Dict[str, Any],
        source_path: str,
        output_path: str
    ) -> List[str]:
        cmd = [MKVMERGE_PATH, "-o", output_path]

        # 1. Video FPS / duration
        fps = job_config.get("video_fps")
        if fps and fps != "Default":
            # For track 0 or video track ID
            video_id = source_info["videos"][0]["id"] if source_info["videos"] else 0
            cmd.extend(["--default-duration", f"{video_id}:{fps}"])

        # 2. Old tracks options (language, name, default, forced)
        old_mods = JobGenerator.resolve_track_mods(job_config, source_info)
        for track in source_info["videos"] + source_info["audios"] + source_info["subtitles"]:
            t_id = str(track["id"])
            if t_id in old_mods:
                mod = old_mods[t_id]
                if "track_name" in mod:
                    cmd.extend(["--track-name", f"{t_id}:{mod['track_name']}"])
                if "language" in mod:
                    lang_code = get_language_code(mod["language"], mod["language"])
                    cmd.extend(["--language", f"{t_id}:{lang_code}"])
                if "is_default" in mod:
                    cmd.extend(["--default-track-flag", f"{t_id}:{'yes' if mod['is_default'] else 'no'}"])
                if "is_forced" in mod:
                    cmd.extend(["--forced-display-flag", f"{t_id}:{'yes' if mod['is_forced'] else 'no'}"])

        # 3. Track filtering: Which old tracks to keep?
        # Videos: keep all enabled
        enabled_video_ids = [
            str(v["id"]) for v in source_info["videos"]
            if old_mods.get(str(v["id"]), {}).get("is_enabled", True) is not False
        ]
        if enabled_video_ids:
            cmd.extend(["-d", ",".join(enabled_video_ids)])
        else:
            cmd.append("-D")

        # Audios: filter by old_mods and only_keep_audios
        enabled_audio_ids = []
        for a in source_info["audios"]:
            a_id = str(a["id"])
            if old_mods.get(a_id, {}).get("is_enabled", True) is False:
                continue
            if job_config.get("only_keep_audios_enabled"):
                keep_ids = job_config.get("only_keep_audios_ids", [])
                keep_langs = job_config.get("only_keep_audios_langs", [])
                keep_names = job_config.get("only_keep_audios_names", [])
                
                match = False
                if a_id in keep_ids or f"Track {int(a_id):02d}" in keep_ids:
                    match = True
                if a.get("language_name") in keep_langs or a.get("language") in keep_langs:
                    match = True
                if a.get("track_name") and a["track_name"] in keep_names:
                    match = True
                if not match:
                    continue
            enabled_audio_ids.append(a_id)

        if enabled_audio_ids:
            cmd.extend(["-a", ",".join(enabled_audio_ids)])
        else:
            cmd.append("-A")

        # Subtitles: filter by old_mods and only_keep_subtitles
        enabled_sub_ids = []
        for s in source_info["subtitles"]:
            s_id = str(s["id"])
            if old_mods.get(s_id, {}).get("is_enabled", True) is False:
                continue
            if job_config.get("only_keep_subtitles_enabled"):
                keep_ids = job_config.get("only_keep_subtitles_ids", [])
                keep_langs = job_config.get("only_keep_subtitles_langs", [])
                keep_names = job_config.get("only_keep_subtitles_names", [])
                
                match = False
                if s_id in keep_ids or f"Track {int(s_id):02d}" in keep_ids:
                    match = True
                if s.get("language_name") in keep_langs or s.get("language") in keep_langs or s.get("language_ietf") in keep_langs:
                    match = True
                if s.get("track_name") and s["track_name"] in keep_names:
                    match = True
                if not s.get("track_name") and ("繁中" in keep_names and s.get("language_ietf") in ["zh-Hant", "zh-TW", "zh-HK"]):
                    match = True
                if not s.get("track_name") and ("簡中" in keep_names and s.get("language_ietf") in ["zh-Hans", "zh-CN", "zh-SG"]):
                    match = True
                if not match:
                    continue
            enabled_sub_ids.append(s_id)

        if enabled_sub_ids:
            cmd.extend(["-s", ",".join(enabled_sub_ids)])
        else:
            cmd.append("-S")

        # 4. Global default audio/sub override
        if job_config.get("make_audio_default_enabled"):
            target = job_config.get("make_audio_default_target")
            for a_id in enabled_audio_ids:
                # Find matching track
                track = next((x for x in source_info["audios"] if str(x["id"]) == a_id), None)
                if not track:
                    continue
                match = (target == f"Track {int(a_id):02d}") or (target == track.get("language_name")) or (target == track.get("track_name")) or (target == track.get("language_ietf")) or (target == track.get("language"))
                if match:
                    cmd.extend(["--default-track-flag", f"{a_id}:yes"])
                else:
                    cmd.extend(["--default-track-flag", f"{a_id}:no"])

        if job_config.get("make_subtitle_default_enabled"):
            target = job_config.get("make_subtitle_default_target")
            for s_id in enabled_sub_ids:
                track = next((x for x in source_info["subtitles"] if str(x["id"]) == s_id), None)
                if not track:
                    continue
                match = (
                    (target == f"Track {int(s_id):02d}") or
                    (target == track.get("language_name")) or
                    (target == track.get("track_name")) or
                    (target == track.get("language_ietf")) or
                    (target == track.get("language")) or
                    (not track.get("track_name") and target == "繁中" and track.get("language_ietf") in ["zh-Hant", "zh-TW", "zh-HK"]) or
                    (not track.get("track_name") and target == "簡中" and track.get("language_ietf") in ["zh-Hans", "zh-CN", "zh-SG"])
                )
                if match:
                    cmd.extend(["--default-track-flag", f"{s_id}:yes"])
                else:
                    cmd.extend(["--default-track-flag", f"{s_id}:no"])

        # Old chapters & attachments
        if job_config.get("chapter_discard_old"):
            cmd.append("--no-chapters")
        if job_config.get("attachments_discard_old"):
            cmd.append("--no-attachments")

        # Append source video
        cmd.append(source_path)

        # 5. Add external chapters
        if job_config.get("chapter_file"):
            cmd.extend(["--chapters", job_config["chapter_file"]])

        # 6. Add external audio tracks
        external_files_count = 0
        track_order: List[str] = [f"0:{v_id}" for v_id in enabled_video_ids]

        for audio in job_config.get("audios", []):
            external_files_count += 1
            file_idx = external_files_count
            
            if audio.get("track_name"):
                cmd.extend(["--track-name", f"0:{audio['track_name']}"])
            if audio.get("language"):
                lang_code = get_language_code(audio["language"], audio["language"])
                cmd.extend(["--language", f"0:{lang_code}"])
            if audio.get("delay") and float(audio["delay"]) != 0.0:
                cmd.extend(["--sync", f"0:{int(float(audio['delay']))}"])
            if audio.get("is_default"):
                cmd.extend(["--default-track-flag", "0:yes"])
            else:
                cmd.extend(["--default-track-flag", "0:no"])
            if audio.get("is_forced"):
                cmd.extend(["--forced-display-flag", "0:yes"])
            else:
                cmd.extend(["--forced-display-flag", "0:no"])
            
            cmd.append(audio["file_path"])
            track_order.append(f"{file_idx}:0")

        # 7. Add external subtitles
        for sub in job_config.get("subtitles", []):
            external_files_count += 1
            file_idx = external_files_count
            
            if sub.get("track_name"):
                cmd.extend(["--track-name", f"0:{sub['track_name']}"])
            if sub.get("language"):
                lang_code = get_language_code(sub["language"], sub["language"])
                cmd.extend(["--language", f"0:{lang_code}"])
            if sub.get("delay") and float(sub["delay"]) != 0.0:
                cmd.extend(["--sync", f"0:{int(float(sub['delay']))}"])
            if sub.get("is_default"):
                cmd.extend(["--default-track-flag", "0:yes"])
            else:
                cmd.extend(["--default-track-flag", "0:no"])
            if sub.get("is_forced"):
                cmd.extend(["--forced-display-flag", "0:yes"])
            else:
                cmd.extend(["--forced-display-flag", "0:no"])

            cmd.append(sub["file_path"])
            track_order.append(f"{file_idx}:0")

        # 8. Add attachments
        existing_att_names = {a["file_name"] for a in source_info.get("attachments", [])}
        for att in job_config.get("attachments", []):
            att_path = att["file_path"]
            att_name = os.path.basename(att_path)
            # Check duplicate
            if not job_config.get("attachments_discard_old") and not job_config.get("attachments_allow_duplicates"):
                if att_name in existing_att_names:
                    continue
            cmd.extend(["--attach-file", att_path])

        # 9. Track order
        if track_order:
            cmd.extend(["--track-order", ",".join(track_order)])

        return cmd
