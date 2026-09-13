import json
import os
from typing import Dict, List, Tuple

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LANG_FILE_PATH = os.path.join(CURRENT_DIR, "iso639_language_list.json")

ISO_639_2_LANGUAGES: Dict[str, str] = {}
ISO_639_2_SYMBOLS: Dict[str, str] = {}

if os.path.exists(LANG_FILE_PATH):
    try:
        with open(LANG_FILE_PATH, "r", encoding="utf-8") as f:
            ISO_639_2_LANGUAGES = json.load(f)
    except Exception as e:
        print(f"Error loading languages: {e}")

# Inverse map (symbol -> language name)
ISO_639_2_SYMBOLS = {v: k for k, v in ISO_639_2_LANGUAGES.items()}

# Priority languages for the top of the dropdown list
COMMON_LANGUAGES: List[Tuple[str, str]] = [
    ("Chinese (Traditional / Simplified)", "chi"),
    ("Japanese", "jpn"),
    ("English", "eng"),
    ("Korean", "kor"),
    ("French", "fre"),
    ("German", "ger"),
    ("Spanish", "spa"),
    ("Italian", "ita"),
    ("Russian", "rus"),
    ("Undetermined", "und"),
]

def get_language_code(name: str, default: str = "und") -> str:
    """Get 3-letter ISO code from language name."""
    if not name:
        return default
    return ISO_639_2_LANGUAGES.get(name, default)

def get_language_name(code: str, default: str = "Undetermined") -> str:
    """Get language name from 3-letter ISO code."""
    if not code:
        return default
    code_lower = code.lower()
    return ISO_639_2_SYMBOLS.get(code_lower, default)

def get_all_languages_list() -> List[Dict[str, str]]:
    """Return sorted list of all languages formatted for frontend selection."""
    res = []
    # Add common ones first
    seen = set()
    for name, code in COMMON_LANGUAGES:
        res.append({"name": name, "code": code, "common": True})
        seen.add(code)
    
    # Add the rest sorted alphabetically by name
    other_langs = sorted(
        [{"name": k, "code": v, "common": False} for k, v in ISO_639_2_LANGUAGES.items() if v not in seen],
        key=lambda x: x["name"]
    )
    res.extend(other_langs)
    return res
