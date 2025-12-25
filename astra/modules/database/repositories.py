#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Database Repositories
Repository pattern implementation for clean database abstraction

This module provides repository classes that encapsulate database operations
and provide a consistent interface for data access across the application.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .models import (
    Conversation,
    Message,
    Person,
    UserPreference,
    UserProfile,
    VoiceInteraction,
)

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository with common functionality."""

    def __init__(self, session: Session):
        self.session = session

    def commit(self):
        """Commit current transaction."""
        try:
            self.session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Database commit error: {e}")
            self.session.rollback()
            raise

    def rollback(self):
        """Rollback current transaction."""
        self.session.rollback()

    def close(self):
        """Close the session."""
        self.session.close()


class ConversationRepository(BaseRepository):
    """Repository for conversation operations."""

    def create_conversation(
        self,
        session_id: str,
        title: str = "Nova Conversa",
        personality: str = "neutra",
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            session_id=session_id,
            title=title,
            personality=personality,
            user_id=user_id,
            metadata=metadata,
        )
        
        self.session.add(conversation)
        self.commit()
        
        logger.info(f"Created conversation {conversation.id} for session {session_id}")
        return conversation

    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID."""
        return self.session.query(Conversation).filter_by(id=conversation_id).first()

    def get_conversation_by_session(self, session_id: str) -> Optional[Conversation]:
        """Get conversation by session ID."""
        return self.session.query(Conversation).filter_by(session_id=session_id).first()

    def get_user_conversations(
        self, user_id: str, limit: int = 50, include_inactive: bool = False
    ) -> List[Conversation]:
        """Get conversations for a specific user."""
        query = self.session.query(Conversation).filter_by(user_id=user_id)
        
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        return query.order_by(desc(Conversation.updated_at)).limit(limit).all()

    def get_recent_conversations(self, days: int = 7, limit: int = 20) -> List[Conversation]:
        """Get recent conversations across all users."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return (
            self.session.query(Conversation)
            .filter(Conversation.updated_at >= cutoff_date)
            .filter_by(is_active=True)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .all()
        )

    def update_conversation(
        self, conversation_id: int, **kwargs
    ) -> Optional[Conversation]:
        """Update conversation fields."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None

        for key, value in kwargs.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)

        self.commit()
        return conversation

    def deactivate_conversation(self, conversation_id: int) -> bool:
        """Mark conversation as inactive."""
        result = self.update_conversation(conversation_id, is_active=False)
        return result is not None


class MessageRepository(BaseRepository):
    """Repository for message operations."""

    def add_message(
        self,
        conversation_id: int,
        message_type: str,
        content: str,
        response_time: Optional[float] = None,
        model_used: Optional[str] = None,
        confidence_score: Optional[float] = None,
        intent_classified: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Add a new message to conversation."""
        message = Message(
            conversation_id=conversation_id,
            message_type=message_type,
            content=content,
            response_time=response_time,
            model_used=model_used,
            confidence_score=confidence_score,
            intent_classified=intent_classified,
            metadata=metadata,
        )

        self.session.add(message)
        self.commit()

        logger.debug(f"Added {message_type} message to conversation {conversation_id}")
        return message

    def get_conversation_messages(
        self, conversation_id: int, limit: int = 100
    ) -> List[Message]:
        """Get messages for a conversation."""
        return (
            self.session.query(Message)
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
            .all()
        )

    def get_recent_messages(
        self, user_id: str, days: int = 1, limit: int = 50
    ) -> List[Message]:
        """Get recent messages for a user across all conversations."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return (
            self.session.query(Message)
            .join(Conversation)
            .filter(Conversation.user_id == user_id)
            .filter(Message.created_at >= cutoff_date)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .all()
        )

    def search_messages(
        self, 
        search_term: str, 
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Message]:
        """Search messages by content."""
        query = self.session.query(Message).filter(
            Message.content.contains(search_term)
        )
        
        if user_id:
            query = query.join(Conversation).filter(Conversation.user_id == user_id)
        
        return query.order_by(desc(Message.created_at)).limit(limit).all()

    def get_message_stats(self, user_id: str) -> Dict[str, Any]:
        """Get message statistics for a user."""
        stats = (
            self.session.query(
                func.count(Message.id).label("total_messages"),
                func.avg(Message.response_time).label("avg_response_time"),
                func.count(Message.id).filter(Message.message_type == "user").label("user_messages"),
                func.count(Message.id).filter(Message.message_type == "assistant").label("assistant_messages"),
            )
            .join(Conversation)
            .filter(Conversation.user_id == user_id)
            .first()
        )

        return {
            "total_messages": stats.total_messages or 0,
            "avg_response_time": float(stats.avg_response_time or 0),
            "user_messages": stats.user_messages or 0,
            "assistant_messages": stats.assistant_messages or 0,
        }


class VoiceInteractionRepository(BaseRepository):
    """Repository for voice interaction operations."""

    def add_voice_interaction(
        self,
        conversation_id: int,
        audio_duration: Optional[float] = None,
        recognition_confidence: Optional[float] = None,
        tts_enabled: bool = True,
        voice_command: bool = False,
        voice_pattern_data: Optional[Dict[str, Any]] = None,
        user_identified: Optional[str] = None,
        identification_confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VoiceInteraction:
        """Add voice interaction data."""
        interaction = VoiceInteraction(
            conversation_id=conversation_id,
            audio_duration=audio_duration,
            recognition_confidence=recognition_confidence,
            tts_enabled=tts_enabled,
            voice_command=voice_command,
            voice_pattern_data=voice_pattern_data,
            user_identified=user_identified,
            identification_confidence=identification_confidence,
            metadata=metadata,
        )

        self.session.add(interaction)
        self.commit()

        return interaction

    def get_voice_stats(self, user_id: str) -> Dict[str, Any]:
        """Get voice interaction statistics."""
        stats = (
            self.session.query(
                func.count(VoiceInteraction.id).label("total_interactions"),
                func.avg(VoiceInteraction.audio_duration).label("avg_duration"),
                func.avg(VoiceInteraction.recognition_confidence).label("avg_recognition"),
                func.avg(VoiceInteraction.identification_confidence).label("avg_identification"),
            )
            .join(Conversation)
            .filter(Conversation.user_id == user_id)
            .first()
        )

        return {
            "total_voice_interactions": stats.total_interactions or 0,
            "avg_audio_duration": float(stats.avg_duration or 0),
            "avg_recognition_confidence": float(stats.avg_recognition or 0),
            "avg_identification_confidence": float(stats.avg_identification or 0),
        }


class UserPreferenceRepository(BaseRepository):
    """Repository for user preference operations."""

    def set_preference(
        self,
        user_id: str,
        key: str,
        value: Any,
        data_type: str = "string",
        category: Optional[str] = None,
    ) -> UserPreference:
        """Set or update a user preference."""
        # Convert value to string for storage
        if data_type == "json":
            string_value = json.dumps(value)
        else:
            string_value = str(value)

        # Check if preference exists
        existing = (
            self.session.query(UserPreference)
            .filter_by(user_id=user_id, preference_key=key)
            .first()
        )

        if existing:
            existing.preference_value = string_value
            existing.data_type = data_type
            existing.category = category
            preference = existing
        else:
            preference = UserPreference(
                user_id=user_id,
                preference_key=key,
                preference_value=string_value,
                data_type=data_type,
                category=category,
            )
            self.session.add(preference)

        self.commit()
        return preference

    def get_preference(self, user_id: str, key: str) -> Optional[Any]:
        """Get a user preference value."""
        preference = (
            self.session.query(UserPreference)
            .filter_by(user_id=user_id, preference_key=key)
            .first()
        )

        return preference.get_typed_value() if preference else None

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get all preferences for a user."""
        preferences = (
            self.session.query(UserPreference)
            .filter_by(user_id=user_id)
            .all()
        )

        return {pref.preference_key: pref.get_typed_value() for pref in preferences}

    def get_preferences_by_category(self, user_id: str, category: str) -> Dict[str, Any]:
        """Get preferences by category."""
        preferences = (
            self.session.query(UserPreference)
            .filter_by(user_id=user_id, category=category)
            .all()
        )

        return {pref.preference_key: pref.get_typed_value() for pref in preferences}

    def delete_preference(self, user_id: str, key: str) -> bool:
        """Delete a user preference."""
        deleted = (
            self.session.query(UserPreference)
            .filter_by(user_id=user_id, preference_key=key)
            .delete()
        )

        self.commit()
        return deleted > 0


class PersonRepository(BaseRepository):
    """Repository for people management operations."""

    def add_person(
        self,
        user_id: str,
        name: str,
        **kwargs
    ) -> Person:
        """Add a new person."""
        person = Person(user_id=user_id, name=name, **kwargs)
        self.session.add(person)
        self.commit()

        logger.info(f"Added person '{name}' for user {user_id}")
        return person

    def get_person(self, person_id: int) -> Optional[Person]:
        """Get person by ID."""
        return self.session.query(Person).filter_by(id=person_id).first()

    def get_user_people(self, user_id: str) -> List[Person]:
        """Get all people for a user."""
        return (
            self.session.query(Person)
            .filter_by(user_id=user_id)
            .order_by(Person.name)
            .all()
        )

    def search_people(self, user_id: str, search_term: str) -> List[Person]:
        """Search people by name or nickname."""
        return (
            self.session.query(Person)
            .filter_by(user_id=user_id)
            .filter(
                or_(
                    Person.name.contains(search_term),
                    Person.nickname.contains(search_term),
                )
            )
            .order_by(Person.name)
            .all()
        )

    def get_people_by_relationship(self, user_id: str, relationship: str) -> List[Person]:
        """Get people by relationship type."""
        return (
            self.session.query(Person)
            .filter_by(user_id=user_id, relationship=relationship)
            .order_by(Person.name)
            .all()
        )

    def update_person(self, person_id: int, **kwargs) -> Optional[Person]:
        """Update person information."""
        person = self.get_person(person_id)
        if not person:
            return None

        for key, value in kwargs.items():
            if hasattr(person, key):
                setattr(person, key, value)

        # Update interaction tracking
        if "last_interaction" not in kwargs:
            person.last_interaction = datetime.now()
        
        person.interaction_count += 1

        self.commit()
        return person

    def delete_person(self, person_id: int) -> bool:
        """Delete a person."""
        deleted = self.session.query(Person).filter_by(id=person_id).delete()
        self.commit()
        return deleted > 0

    def get_recent_interactions(self, user_id: str, days: int = 30) -> List[Person]:
        """Get people with recent interactions."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return (
            self.session.query(Person)
            .filter_by(user_id=user_id)
            .filter(Person.last_interaction >= cutoff_date)
            .order_by(desc(Person.last_interaction))
            .all()
        )


class UserProfileRepository(BaseRepository):
    """Repository for user profile operations."""

    def create_profile(self, user_id: str, **kwargs) -> UserProfile:
        """Create a new user profile."""
        profile = UserProfile(user_id=user_id, **kwargs)
        self.session.add(profile)
        self.commit()

        logger.info(f"Created profile for user {user_id}")
        return profile

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile."""
        return self.session.query(UserProfile).filter_by(user_id=user_id).first()

    def get_or_create_profile(self, user_id: str) -> UserProfile:
        """Get existing profile or create a new one."""
        profile = self.get_profile(user_id)
        if not profile:
            profile = self.create_profile(user_id)
        return profile

    def update_profile(self, user_id: str, **kwargs) -> Optional[UserProfile]:
        """Update user profile."""
        profile = self.get_profile(user_id)
        if not profile:
            return None

        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        profile.last_activity = datetime.now()
        self.commit()
        return profile

    def update_patterns(
        self,
        user_id: str,
        text_patterns: Optional[Dict] = None,
        voice_patterns: Optional[Dict] = None,
        behavioral_patterns: Optional[Dict] = None,
        temporal_patterns: Optional[Dict] = None,
    ) -> Optional[UserProfile]:
        """Update user patterns."""
        profile = self.get_or_create_profile(user_id)
        
        if text_patterns:
            profile.text_patterns = text_patterns
        if voice_patterns:
            profile.voice_patterns = voice_patterns
        if behavioral_patterns:
            profile.behavioral_patterns = behavioral_patterns
        if temporal_patterns:
            profile.temporal_patterns = temporal_patterns

        profile.last_activity = datetime.now()
        self.commit()
        return profile

    def increment_stats(
        self,
        user_id: str,
        conversations: int = 0,
        messages: int = 0,
        voice_interactions: int = 0,
    ) -> Optional[UserProfile]:
        """Increment usage statistics."""
        profile = self.get_or_create_profile(user_id)
        
        profile.total_conversations += conversations
        profile.total_messages += messages
        profile.total_voice_interactions += voice_interactions
        profile.last_activity = datetime.now()
        
        self.commit()
        return profile

    def get_all_profiles(self) -> List[UserProfile]:
        """Get all user profiles."""
        return self.session.query(UserProfile).order_by(UserProfile.last_activity.desc()).all()


class RepositoryManager:
    """Manager class for all repositories."""

    def __init__(self, session: Session):
        self.session = session
        self.conversations = ConversationRepository(session)
        self.messages = MessageRepository(session)
        self.voice_interactions = VoiceInteractionRepository(session)
        self.preferences = UserPreferenceRepository(session)
        self.people = PersonRepository(session)
        self.profiles = UserProfileRepository(session)

    def commit(self):
        """Commit all pending changes."""
        try:
            self.session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Repository manager commit error: {e}")
            self.session.rollback()
            raise

    def rollback(self):
        """Rollback all pending changes."""
        self.session.rollback()

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()
