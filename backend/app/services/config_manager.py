import json
import os
import uuid
from typing import Any, Dict, List, Optional
from ..config import (
    CONFIG_FILE_PATH,
    PRESETS_FILE_PATH,
    STORAGE_DIR,
    DEFAULT_VIDEO_EXTENSIONS,
    DEFAULT_SUBTITLE_EXTENSIONS,
    DEFAULT_AUDIO_EXTENSIONS,
    DEFAULT_CHAPTER_EXTENSIONS,
    DEFAULT_ATTACHMENT_EXTENSIONS,
)

DEFAULT_SETTINGS = {
    "dark_mode": True,
    "default_video_dir": STORAGE_DIR,
    "default_subtitle_dir": STORAGE_DIR,
    "default_audio_dir": STORAGE_DIR,
    "default_output_dir": STORAGE_DIR,
    "favorite_preset_id": "default",
    "video_extensions": DEFAULT_VIDEO_EXTENSIONS,
    "subtitle_extensions": DEFAULT_SUBTITLE_EXTENSIONS,
    "audio_extensions": DEFAULT_AUDIO_EXTENSIONS,
    "chapter_extensions": DEFAULT_CHAPTER_EXTENSIONS,
    "attachment_extensions": DEFAULT_ATTACHMENT_EXTENSIONS,
    "language_priority": ["chi", "jpn", "eng"],
}

DEFAULT_PRESET = {
    "id": "default",
    "name": "Default Preset",
    "description": "Standard MKV muxing preset",
    "created_at": "2024-01-01",
    "settings": {
        "video_fps": "Default",
        "chapter_discard_old": False,
        "attachments_discard_old": False,
        "attachments_allow_duplicates": False,
        "overwrite_source": False,
        "use_mkvpropedit": False,
        "add_crc": False,
        "remove_old_crc": False,
        "abort_on_error": False,
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
}

class ConfigManager:
    @staticmethod
    def get_settings() -> Dict[str, Any]:
        if not os.path.exists(CONFIG_FILE_PATH):
            ConfigManager.save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                # merge defaults in case of missing keys
                res = DEFAULT_SETTINGS.copy()
                res.update(data)
                return res
        except Exception:
            return DEFAULT_SETTINGS.copy()

    @staticmethod
    def save_settings(settings: Dict[str, Any]):
        os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

    @staticmethod
    def get_presets() -> List[Dict[str, Any]]:
        if not os.path.exists(PRESETS_FILE_PATH):
            ConfigManager.save_presets([DEFAULT_PRESET])
            return [DEFAULT_PRESET.copy()]
        try:
            with open(PRESETS_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return [DEFAULT_PRESET.copy()]

    @staticmethod
    def save_presets(presets: List[Dict[str, Any]]):
        os.makedirs(os.path.dirname(PRESETS_FILE_PATH), exist_ok=True)
        with open(PRESETS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(presets, f, indent=2, ensure_ascii=False)

    @staticmethod
    def create_preset(name: str, settings: Dict[str, Any], description: str = "") -> Dict[str, Any]:
        presets = ConfigManager.get_presets()
        new_preset = {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "description": description,
            "settings": settings,
        }
        presets.append(new_preset)
        ConfigManager.save_presets(presets)
        return new_preset

    @staticmethod
    def update_preset(preset_id: str, name: Optional[str] = None, settings: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        presets = ConfigManager.get_presets()
        target = next((p for p in presets if p["id"] == preset_id), None)
        if not target:
            return None
        if name:
            target["name"] = name
        if settings:
            target["settings"] = settings
        ConfigManager.save_presets(presets)
        return target

    @staticmethod
    def delete_preset(preset_id: str) -> bool:
        if preset_id == "default":
            return False
        presets = ConfigManager.get_presets()
        filtered = [p for p in presets if p["id"] != preset_id]
        if len(filtered) != len(presets):
            ConfigManager.save_presets(filtered)
            return True
        return False
