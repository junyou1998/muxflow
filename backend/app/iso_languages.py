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

# Known IETF BCP 47 and ISO language mappings
IETF_LANGUAGES: Dict[str, str] = {
    # Traditional Chinese variants
    "zh-hant": "Traditional Chinese (繁體中文)",
    "zh-tw": "Traditional Chinese (繁體台灣)",
    "zh-hk": "Traditional Chinese (繁體香港)",
    "zh-mo": "Traditional Chinese (繁體澳門)",
    "zh-cht": "Traditional Chinese (繁體中文)",

    # Simplified Chinese variants
    "zh-hans": "Simplified Chinese (簡體中文)",
    "zh-cn": "Simplified Chinese (簡體中國)",
    "zh-sg": "Simplified Chinese (簡體新加坡)",
    "zh-chs": "Simplified Chinese (簡體中文)",

    # Generic Chinese
    "zh": "Chinese",
    "chi": "Chinese",
    "zho": "Chinese",

    # Japanese
    "ja": "Japanese",
    "jpn": "Japanese",

    # English
    "en": "English",
    "eng": "English",
    "en-us": "English (US)",
    "en-gb": "English (UK)",

    # Korean
    "ko": "Korean",
    "kor": "Korean",

    # European languages
    "fre": "French",
    "fra": "French",
    "ger": "German",
    "deu": "German",
    "spa": "Spanish",
    "ita": "Italian",
    "rus": "Russian",
    "und": "Undetermined",
}

# Priority languages for the top of the dropdown list
COMMON_LANGUAGES: List[Tuple[str, str]] = [
    ("Chinese - Traditional (繁體中文)", "zh-Hant"),
    ("Chinese - Simplified (簡體中文)", "zh-Hans"),
    ("Chinese - Taiwan (繁體台灣)", "zh-TW"),
    ("Chinese - Hong Kong (繁體香港)", "zh-HK"),
    ("Chinese - General (中文)", "chi"),
    ("Japanese (日本語)", "jpn"),
    ("English (英語)", "eng"),
    ("Korean (韓語)", "kor"),
    ("French (法語)", "fre"),
    ("German (德語)", "ger"),
    ("Spanish (西班牙語)", "spa"),
    ("Italian (義大利語)", "ita"),
    ("Russian (俄語)", "rus"),
    ("Undetermined (未指定)", "und"),
]

def get_language_code(name: str, default: str = "und") -> str:
    """Get language code from language name or code."""
    if not name:
        return default
    name_clean = name.strip()
    name_lower = name_clean.lower()
    for c_name, c_code in COMMON_LANGUAGES:
        if name_lower in [c_name.lower(), c_code.lower()]:
            return c_code
    if name_clean in ISO_639_2_LANGUAGES:
        return ISO_639_2_LANGUAGES[name_clean]
    for code, l_name in IETF_LANGUAGES.items():
        if name_lower in [code.lower(), l_name.lower()]:
            return code
    return ISO_639_2_LANGUAGES.get(name_clean, default)

def get_language_name(code: str, default: str = "Undetermined") -> str:
    """Get language name from IETF tag or ISO 639 code."""
    if not code:
        return default
    code_lower = code.lower().strip()
    if code_lower in IETF_LANGUAGES:
        return IETF_LANGUAGES[code_lower]
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
