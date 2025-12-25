#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA/Astra - Personality Engine Tests
Comprehensive unit tests for the personality system
"""

import pytest
from datetime import datetime
from modules.personality_engine import (
    PersonalityEngine,
    MoodType,
    PersonalityMode,
    TimeContext
)


class TestPersonalityEngine:
    """Test suite for PersonalityEngine."""
    
    def test_initialization(self, personality_engine):
        """Test PersonalityEngine initialization."""
        assert personality_engine is not None
        assert personality_engine.current_mood == MoodType.NEUTRAL
        assert personality_engine.current_personality == PersonalityMode.ADAPTIVE
        
    def test_mood_detection_happy(self, personality_engine, sample_mood_texts):
        """Test detection of happy mood."""
        mood = personality_engine.analyze_user_mood(sample_mood_texts["happy"])
        assert mood == MoodType.HAPPY
        
    def test_mood_detection_sad(self, personality_engine, sample_mood_texts):
        """Test detection of sad mood."""
        mood = personality_engine.analyze_user_mood(sample_mood_texts["sad"])
        assert mood == MoodType.SAD
        
    def test_mood_detection_excited(self, personality_engine, sample_mood_texts):
        """Test detection of excited mood."""
        mood = personality_engine.analyze_user_mood(sample_mood_texts["excited"])
        assert mood == MoodType.EXCITED
        
    def test_mood_detection_frustrated(self, personality_engine, sample_mood_texts):
        """Test detection of frustrated mood."""
        mood = personality_engine.analyze_user_mood(sample_mood_texts["frustrated"])
        assert mood == MoodType.FRUSTRATED
        
    def test_mood_detection_tired(self, personality_engine, sample_mood_texts):
        """Test detection of tired mood."""
        mood = personality_engine.analyze_user_mood(sample_mood_texts["tired"])
        assert mood == MoodType.TIRED
        
    def test_mood_detection_stressed(self, personality_engine, sample_mood_texts):
        """Test detection of stressed mood."""
        mood = personality_engine.analyze_user_mood(sample_mood_texts["stressed"])
        assert mood == MoodType.STRESSED
        
    def test_mood_detection_neutral(self, personality_engine, sample_mood_texts):
        """Test detection of neutral mood."""
        mood = personality_engine.analyze_user_mood(sample_mood_texts["neutral"])
        assert mood == MoodType.NEUTRAL
        
    def test_time_context_morning(self, personality_engine):
        """Test time context detection for morning."""
        # Mock datetime to test different times would require freezegun
        # For now, just test that the method works
        context = personality_engine.get_time_context()
        assert isinstance(context, TimeContext)
        
    def test_personality_mode_change(self, personality_engine):
        """Test changing personality mode."""
        personality_engine.set_personality_mode(PersonalityMode.FORMAL)
        assert personality_engine.current_personality == PersonalityMode.FORMAL
        
    def test_personality_templates(self, personality_engine):
        """Test that personality templates are loaded."""
        templates = personality_engine.personality_templates
        assert PersonalityMode.CASUAL in templates
        assert PersonalityMode.FORMAL in templates
        assert "greeting" in templates[PersonalityMode.CASUAL]
        
    def test_adapt_to_mood_happy(self, personality_engine):
        """Test personality adaptation to happy mood."""
        result = personality_engine.adapt_to_mood(MoodType.HAPPY)
        # Should suggest energetic or casual personality
        assert result["suggested_personality"] in [
            PersonalityMode.ENERGETIC,
            PersonalityMode.CASUAL
        ]
        
    def test_adapt_to_mood_sad(self, personality_engine):
        """Test personality adaptation to sad mood."""
        result = personality_engine.adapt_to_mood(MoodType.SAD)
        # Should suggest supportive or calm personality
        assert result["suggested_personality"] in [
            PersonalityMode.SUPPORTIVE,
            PersonalityMode.CALM
        ]
        
    def test_get_greeting(self, personality_engine):
        """Test getting greeting based on personality."""
        personality_engine.set_personality_mode(PersonalityMode.CASUAL)
        greeting = personality_engine.get_greeting()
        assert isinstance(greeting, str)
        assert len(greeting) > 0
        
    def test_update_user_preferences(self, personality_engine):
        """Test updating user preferences."""
        personality_engine.update_user_preferences("favorite_color", "blue")
        assert personality_engine.user_preferences.get("favorite_color") == "blue"
        
    def test_conversation_history_tracking(self, personality_engine):
        """Test conversation history tracking."""
        personality_engine.add_to_conversation_history("user", "Olá!")
        personality_engine.add_to_conversation_history("assistant", "Olá! Como posso ajudar?")
        
        assert len(personality_engine.conversation_history) == 2
        assert personality_engine.conversation_history[0]["role"] == "user"
        
    def test_interaction_stats(self, personality_engine):
        """Test interaction statistics tracking."""
        personality_engine.record_interaction("greeting", success=True)
        personality_engine.record_interaction("question", success=True)
        
        stats = personality_engine.get_interaction_stats()
        assert stats["total_interactions"] >= 2
        
    def test_save_and_load_user_data(self, personality_engine, temp_dir):
        """Test saving and loading user data."""
        personality_engine.data_dir = temp_dir / "personality"
        personality_engine.user_preferences = {"test_key": "test_value"}
        
        personality_engine.save_user_data()
        
        # Create new instance and load
        new_engine = PersonalityEngine(data_dir=str(temp_dir / "personality"))
        assert new_engine.user_preferences.get("test_key") == "test_value"
        
    def test_mood_pattern_detection(self, personality_engine):
        """Test mood pattern detection from multiple interactions."""
        moods = [
            "Estou feliz!",
            "Que dia maravilhoso!",
            "Tudo está ótimo!"
        ]
        
        detected_moods = [personality_engine.analyze_user_mood(m) for m in moods]
        # Most should be happy
        assert detected_moods.count(MoodType.HAPPY) >= 2
        
    def test_empty_text_handling(self, personality_engine):
        """Test handling of empty text."""
        mood = personality_engine.analyze_user_mood("")
        assert mood == MoodType.NEUTRAL
        
    def test_very_long_text(self, personality_engine):
        """Test handling of very long text."""
        long_text = "Estou feliz! " * 1000
        mood = personality_engine.analyze_user_mood(long_text)
        assert mood == MoodType.HAPPY
        
    def test_mixed_emotions(self, personality_engine):
        """Test handling of mixed emotions."""
        mixed_text = "Estou feliz mas também um pouco triste e cansado"
        mood = personality_engine.analyze_user_mood(mixed_text)
        # Should detect one of the emotions
        assert mood in [MoodType.HAPPY, MoodType.SAD, MoodType.TIRED]
        
    @pytest.mark.parametrize("mode", list(PersonalityMode))
    def test_all_personality_modes(self, personality_engine, mode):
        """Test that all personality modes can be set."""
        personality_engine.set_personality_mode(mode)
        assert personality_engine.current_personality == mode
        
    def test_context_aware_response(self, personality_engine):
        """Test context-aware response generation."""
        personality_engine.set_personality_mode(PersonalityMode.CASUAL)
        response = personality_engine.generate_contextual_response(
            user_input="Como você está?",
            mood=MoodType.HAPPY
        )
        assert isinstance(response, str)
        assert len(response) > 0


