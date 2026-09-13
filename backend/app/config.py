import os
from pathlib import Path

# Paths configuration
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = os.path.join(BASE_DIR.parent, "frontend")

# In Docker, Unraid mounts shares to /storage and app config to /config
STORAGE_DIR = os.environ.get("STORAGE_DIR", "/storage")
CONFIG_DIR = os.environ.get("CONFIG_DIR", os.path.join(BASE_DIR.parent, "config"))

# If /storage does not exist (e.g. running locally), fallback to user's home or current dir
if not os.path.exists(STORAGE_DIR):
    STORAGE_DIR = str(Path.home())

os.makedirs(CONFIG_DIR, exist_ok=True)

CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, "settings.json")
PRESETS_FILE_PATH = os.path.join(CONFIG_DIR, "presets.json")
LOGS_DIR = os.path.join(CONFIG_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Tool paths
MKVMERGE_PATH = os.environ.get("MKVMERGE_PATH", "mkvmerge")
MKVPROPEDIT_PATH = os.environ.get("MKVPROPEDIT_PATH", "mkvpropedit")

# Supported extensions
DEFAULT_VIDEO_EXTENSIONS = ["mkv", "mp4", "avi", "ts", "m2ts", "mov", "webm", "flv", "wmv"]
DEFAULT_SUBTITLE_EXTENSIONS = ["srt", "ass", "ssa", "sup", "vtt", "sub", "idx"]
DEFAULT_AUDIO_EXTENSIONS = ["aac", "ac3", "eac3", "flac", "dts", "m4a", "mp3", "opus", "wav", "thd", "mka"]
DEFAULT_CHAPTER_EXTENSIONS = ["xml", "txt"]
DEFAULT_ATTACHMENT_EXTENSIONS = ["ttf", "otf", "jpg", "jpeg", "png", "xml", "txt"]

DEFAULT_FPS_OPTIONS = [
    "Default",
    "23.976p",
    "24p",
    "25p",
    "29.97p",
    "30p",
    "50p",
    "59.94p",
    "60p"
]
