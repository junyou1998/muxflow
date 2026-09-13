from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.config_manager import ConfigManager
from ..iso_languages import get_all_languages_list

router = APIRouter(prefix="/api/presets", tags=["presets"])

class PresetCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    settings: Dict[str, Any]

class PresetUpdateRequest(BaseModel):
    name: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

@router.get("")
def get_presets():
    return ConfigManager.get_presets()

@router.post("")
def create_preset(req: PresetCreateRequest):
    return ConfigManager.create_preset(req.name, req.settings, req.description or "")

@router.put("/{preset_id}")
def update_preset(preset_id: str, req: PresetUpdateRequest):
    res = ConfigManager.update_preset(preset_id, req.name, req.settings)
    if not res:
        raise HTTPException(status_code=404, detail="Preset not found")
    return res

@router.delete("/{preset_id}")
def delete_preset(preset_id: str):
    success = ConfigManager.delete_preset(preset_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete preset (default or not found)")
    return {"status": "deleted"}

@router.get("/settings/app")
def get_app_settings():
    return ConfigManager.get_settings()

@router.post("/settings/app")
def save_app_settings(settings: Dict[str, Any]):
    ConfigManager.save_settings(settings)
    return {"status": "saved"}

@router.get("/languages")
def get_languages():
    return get_all_languages_list()
