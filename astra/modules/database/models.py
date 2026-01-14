#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Database Models
SQLAlchemy ORM models for database abstraction layer

This module defines all database models using SQLAlchemy ORM for 
portable database operations (SQLite default, MySQL optional).
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class Conversation(Base, TimestampMixin):
    """Conversation records with session tracking."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(500), default="Nova Conversa")
    personality = Column(String(100), default="neutra")
    user_id = Column(String(255), nullable=True, index=True)  # Multi-user support
    is_active = Column(Boolean, default=True)
    extra_data = Column(JSON, nullable=True)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    voice_interactions = relationship(
        "VoiceInteraction", back_populates="conversation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, session_id='{self.session_id}', title='{self.title}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "title": self.title,
            "personality": self.personality,
            "user_id": self.user_id,
            "is_active": self.is_active,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Message(Base, TimestampMixin):
    """Individual messages within conversations."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    message_type = Column(
        Enum("user", "assistant", "system", name="message_type_enum"), nullable=False
    )
    content = Column(Text, nullable=False)
    response_time = Column(Float, nullable=True)  # Response time in seconds
    token_count = Column(Integer, nullable=True)
    model_used = Column(String(100), nullable=True)
    confidence_score = Column(Float, nullable=True)  # For ML classification confidence
    intent_classified = Column(String(100), nullable=True)  # Detected intent
    extra_data = Column(JSON, nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, type='{self.message_type}', content='{self.content[:50]}...')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "message_type": self.message_type,
            "content": self.content,
            "response_time": self.response_time,
            "token_count": self.token_count,
            "model_used": self.model_used,
            "confidence_score": self.confidence_score,
            "intent_classified": self.intent_classified,
            "extra_data": self.extra_data,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
        }


class VoiceInteraction(Base, TimestampMixin):
    """Voice-specific interaction data."""

    __tablename__ = "voice_interactions"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    audio_duration = Column(Float, nullable=True)  # Duration in seconds
    recognition_confidence = Column(Float, nullable=True)  # STT confidence (0.0-1.0)
    tts_enabled = Column(Boolean, default=True)
    voice_command = Column(Boolean, default=False)
    voice_pattern_data = Column(JSON, nullable=True)  # Voice fingerprint data
    user_identified = Column(String(255), nullable=True)  # Identified user from voice
    identification_confidence = Column(Float, nullable=True)  # User ID confidence
    extra_data = Column(JSON, nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="voice_interactions")

    def __repr__(self) -> str:
        return f"<VoiceInteraction(id={self.id}, duration={self.audio_duration}s)>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "audio_duration": self.audio_duration,
            "recognition_confidence": self.recognition_confidence,
            "tts_enabled": self.tts_enabled,
            "voice_command": self.voice_command,
            "voice_pattern_data": self.voice_pattern_data,
            "user_identified": self.user_identified,
            "identification_confidence": self.identification_confidence,
            "extra_data": self.extra_data,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
        }


class UserPreference(Base, TimestampMixin):
    """User preferences and settings."""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)  # User identifier
    preference_key = Column(String(100), nullable=False)
    preference_value = Column(Text, nullable=False)
    data_type = Column(
        Enum("string", "integer", "float", "boolean", "json", name="data_type_enum"),
        default="string",
    )
    category = Column(String(50), nullable=True)  # e.g., 'voice', 'ui', 'behavior'
    
    # Unique constraint on user_id + preference_key
    __table_args__ = (
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    def __repr__(self) -> str:
        return f"<UserPreference(user='{self.user_id}', key='{self.preference_key}')>"

    def get_typed_value(self) -> Any:
        """Return the preference value in its correct type."""
        if self.data_type == "integer":
            return int(self.preference_value)
        elif self.data_type == "float":
            return float(self.preference_value)
        elif self.data_type == "boolean":
            return self.preference_value.lower() in ("true", "1", "yes", "on")
        elif self.data_type == "json":
            return json.loads(self.preference_value)
        else:
            return self.preference_value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "preference_key": self.preference_key,
            "preference_value": self.get_typed_value(),
            "data_type": self.data_type,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Person(Base, TimestampMixin):
    """People in user's network with relationship tracking."""

    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    nickname = Column(String(255), nullable=True)
    relationship = Column(String(100), nullable=True)  # e.g., 'friend', 'family', 'colleague'
    age = Column(Integer, nullable=True)
    gender = Column(
        Enum(
            "masculino",
            "feminino", 
            "não-binário",
            "outro",
            "prefere_nao_dizer",
            name="gender_enum",
        ),
        nullable=True,
    )
    sexuality = Column(String(100), nullable=True)
    personality_traits = Column(Text, nullable=True)
    interests = Column(Text, nullable=True)
    favorite_foods = Column(Text, nullable=True)
    favorite_music = Column(Text, nullable=True)
    favorite_movies = Column(Text, nullable=True)
    favorite_activities = Column(Text, nullable=True)
    dislikes = Column(Text, nullable=True)
    profession = Column(String(255), nullable=True)
    birthday = Column(DateTime, nullable=True)
    contact_info = Column(JSON, nullable=True)  # Phone, email, social media
    notes = Column(Text, nullable=True)
    importance_level = Column(
        Enum("baixa", "média", "alta", "muito_alta", name="importance_enum"), default="média"
    )
    user_id = Column(String(255), nullable=False, index=True)  # Owner of this person record
    tags = Column(JSON, nullable=True)  # Searchable tags
    last_interaction = Column(DateTime, nullable=True)
    interaction_count = Column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<Person(id={self.id}, name='{self.name}', relationship='{self.relationship}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "nickname": self.nickname,
            "relationship": self.relationship,
            "age": self.age,
            "gender": self.gender,
            "sexuality": self.sexuality,
            "personality_traits": self.personality_traits,
            "interests": self.interests,
            "favorite_foods": self.favorite_foods,
            "favorite_music": self.favorite_music,
            "favorite_movies": self.favorite_movies,
            "favorite_activities": self.favorite_activities,
            "dislikes": self.dislikes,
            "profession": self.profession,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "contact_info": self.contact_info,
            "notes": self.notes,
            "importance_level": self.importance_level,
            "user_id": self.user_id,
            "tags": self.tags,
            "last_interaction": self.last_interaction.isoformat() if self.last_interaction else None,
            "interaction_count": self.interaction_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserProfile(Base, TimestampMixin):
    """User profiles with contextual analysis data."""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Contextual analysis data
    text_patterns = Column(JSON, nullable=True)  # Common words, phrases, style
    voice_patterns = Column(JSON, nullable=True)  # Voice fingerprint data
    behavioral_patterns = Column(JSON, nullable=True)  # Topics, emotions, formality
    temporal_patterns = Column(JSON, nullable=True)  # Usage times, frequency
    
    # Preferences
    preferred_personality = Column(String(100), default="neutra")
    language_preference = Column(String(10), default="pt")
    timezone = Column(String(50), nullable=True)
    
    # Statistics
    total_conversations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    total_voice_interactions = Column(Integer, default=0)
    last_activity = Column(DateTime, nullable=True)
    
    # Privacy settings
    data_collection_consent = Column(Boolean, default=True)
    voice_analysis_consent = Column(Boolean, default=True)
    
    extra_data = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<UserProfile(user_id='{self.user_id}', name='{self.name}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "text_patterns": self.text_patterns,
            "voice_patterns": self.voice_patterns,
            "behavioral_patterns": self.behavioral_patterns,
            "temporal_patterns": self.temporal_patterns,
            "preferred_personality": self.preferred_personality,
            "language_preference": self.language_preference,
            "timezone": self.timezone,
            "total_conversations": self.total_conversations,
            "total_messages": self.total_messages,
            "total_voice_interactions": self.total_voice_interactions,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "data_collection_consent": self.data_collection_consent,
            "voice_analysis_consent": self.voice_analysis_consent,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Helper functions for database operations
def get_engine(database_url: str, **kwargs):
    """Create SQLAlchemy engine with proper configuration."""
    if "sqlite" in database_url.lower():
        # SQLite-specific settings
        kwargs.setdefault("connect_args", {"check_same_thread": False})
        kwargs.setdefault("echo", False)
    elif "mysql" in database_url.lower():
        # MySQL-specific settings
        kwargs.setdefault("pool_size", 5)
        kwargs.setdefault("pool_recycle", 3600)
        kwargs.setdefault("echo", False)
    
    return create_engine(database_url, **kwargs)


def create_session_factory(engine):
    """Create a session factory."""
    return sessionmaker(bind=engine)


def init_database(engine):
    """Initialize database tables."""
    Base.metadata.create_all(engine)


def drop_database(engine):
    """Drop all database tables (use with caution!)."""
    Base.metadata.drop_all(engine)
