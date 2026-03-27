"""
🤖 JARVIS Services Package
Содержит все компоненты для голосового ассистента JARVIS
"""

from __future__ import annotations

from .emotional_tts import EmotionalTTS, JARVISEmotion, get_emotional_tts
from .personality_engine import JARVISPersonalityEngine, PersonalityTrait, get_personality_engine
from .autonomy_engine import AutonomyEngine, AutonomyLevel, ActionType, get_autonomy_engine
from .enhanced_voice_service import EnhancedVoiceJarvisService, create_enhanced_jarvis_service
from .autonomous_jarvis import AutonomousJarvisService, create_autonomous_jarvis_service

__all__ = [
    # Emotional TTS
    "EmotionalTTS",
    "JARVISEmotion", 
    "get_emotional_tts",
    
    # Personality Engine
    "JARVISPersonalityEngine",
    "PersonalityTrait",
    "get_personality_engine",
    
    # Autonomy Engine
    "AutonomyEngine",
    "AutonomyLevel",
    "ActionType",
    "get_autonomy_engine",
    
    # Services
    "EnhancedVoiceJarvisService",
    "create_enhanced_jarvis_service",
    "AutonomousJarvisService", 
    "create_autonomous_jarvis_service",
]
