from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from ..services.jarvis.personality_engine import JARVISPersonalityEngine, PersonalityTrait, ResponseStyle

router = APIRouter(tags=["jarvis-personality"])

# Singleton instance for demo purposes, in production this would be user-specific
_personality_engine = JARVISPersonalityEngine()

class TraitUpdate(BaseModel):
    trait_id: str
    value: float

class StyleUpdate(BaseModel):
    style: str

@router.get("/traits")
async def get_traits() -> Dict[str, float]:
    """Получить текущие черты личности"""
    return {
        trait.value: value 
        for trait, value in _personality_engine.traits.items()
    }

@router.post("/traits/update")
async def update_trait(update: TraitUpdate) -> Dict[str, Any]:
    """Обновить конкретную черту личности"""
    try:
        trait = PersonalityTrait(update.trait_id)
        _personality_engine.traits[trait] = update.value / 100.0
        return {"status": "success", "trait": update.trait_id, "new_value": update.value}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid trait ID: {update.trait_id}")

@router.get("/style")
async def get_style() -> Dict[str, str]:
    """Получить текущий стиль общения"""
    profile = await _personality_engine.get_user_profile("sir")
    return {"style": str(profile["preferences"].get("response_style", "formal"))}

@router.post("/style/update")
async def update_style(update: StyleUpdate) -> Dict[str, str]:
    """Обновить стиль общения"""
    try:
        style = ResponseStyle(update.style)
        _personality_engine.set_style("sir", style)
        return {"status": "success", "style": update.style}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid style: {update.style}")

@router.get("/profile")
async def get_profile() -> Dict[str, Any]:
    """Получить профиль пользователя и настройки JARVIS"""
    return await _personality_engine.get_user_profile("sir")
