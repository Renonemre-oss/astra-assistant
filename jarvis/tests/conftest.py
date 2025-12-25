#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/JARVIS - PyTest Configuration
Fixtures and configuration for all tests
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ================================
# FIXTURES - BASIC
# ================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return "Olá! Como posso ajudar você hoje?"


@pytest.fixture
def sample_conversation():
    """Sample conversation history."""
    return [
        {"role": "user", "content": "Olá!"},
        {"role": "assistant", "content": "Olá! Como posso ajudar?"},
        {"role": "user", "content": "Como você está?"},
        {"role": "assistant", "content": "Estou bem, obrigado por perguntar!"}
    ]


# ================================
# FIXTURES - PERSONALITY
# ================================

@pytest.fixture
def personality_engine():
    """Create PersonalityEngine instance."""
    from modules.personality_engine import PersonalityEngine
    return PersonalityEngine(data_dir="test_data/personality")


@pytest.fixture
def sample_mood_texts():
    """Sample texts for mood detection."""
    return {
        "happy": "Estou muito feliz hoje! Tudo está ótimo! 😊",
        "sad": "Estou triste e chateado 😢",
        "excited": "Uau! Isso é incrível!! 🎉",
        "frustrated": "Estou muito irritado com isso 😠",
        "tired": "Estou tão cansado... 😴",
        "stressed": "Estou muito estressado com tudo 😰",
        "neutral": "Hoje é um dia normal."
    }


# ================================
# FIXTURES - MEMORY
# ================================

@pytest.fixture
def memory_system():
    """Create MemorySystem instance."""
    from modules.memory_system import MemorySystem
    return MemorySystem(data_dir="test_data/memory")


@pytest.fixture
def sample_memories():
    """Sample memories for testing."""
    return [
        {
            "content": "O usuário gosta de pizza",
            "type": "semantic",
            "importance": "medium",
            "tags": ["comida", "preferência"]
        },
        {
            "content": "Reunião importante às 14h",
            "type": "episodic",
            "importance": "high",
            "tags": ["trabalho", "compromisso"]
        },
        {
            "content": "O usuário estava feliz ontem",
            "type": "emotional",
            "importance": "low",
            "tags": ["emoção", "humor"]
        }
    ]


# ================================
# FIXTURES - COMPANION
# ================================

@pytest.fixture
def companion_engine():
    """Create CompanionEngine instance."""
    from modules.companion_engine import CompanionEngine
    return CompanionEngine(data_dir="test_data/companion")


# ================================
# FIXTURES - DATABASE
# ================================

@pytest.fixture
def database_manager():
    """Create DatabaseManager instance with test database."""
    from modules.database.database_manager import DatabaseManager, DatabaseConfig
    
    config = DatabaseConfig(database_path=":memory:")  # In-memory database
    db = DatabaseManager(config)
    db.connect()
    
    yield db
    
    db.disconnect()


@pytest.fixture
def sample_user_data():
    """Sample user data for database testing."""
    return {
        "name": "João Silva",
        "age": 30,
        "email": "joao@example.com",
        "preferences": {"theme": "dark", "language": "pt"}
    }


# ================================
# FIXTURES - CONTEXTUAL ANALYZER
# ================================

@pytest.fixture
def contextual_analyzer():
    """Create ContextualAnalyzer instance."""
    from modules.contextual_analyzer import ContextualAnalyzer
    return ContextualAnalyzer(data_dir=Path("test_data/contextual"))


@pytest.fixture
def sample_contexts():
    """Sample contexts for testing."""
    return {
        "work": "Tenho uma reunião importante com o chefe sobre o projeto.",
        "family": "Vou jantar com minha mãe e meu irmão hoje à noite.",
        "entertainment": "Assisti um filme incrível no Netflix ontem.",
        "sports": "O Benfica ganhou o jogo de futebol!",
        "health": "Fui ao médico fazer um check-up.",
        "technology": "Estou programando um novo aplicativo em Python."
    }


# ================================
# FIXTURES - MULTI-USER
# ================================

@pytest.fixture
def multi_user_manager():
    """Create MultiUserManager instance."""
    from modules.multi_user_manager import MultiUserManager
    return MultiUserManager()


@pytest.fixture
def sample_users():
    """Sample users for testing."""
    return [
        {
            "id": "user1",
            "name": "João",
            "common_words": ["programação", "código", "python"],
            "typical_phrases": ["bom dia", "tudo bem"]
        },
        {
            "id": "user2",
            "name": "Maria",
            "common_words": ["design", "arte", "criativo"],
            "typical_phrases": ["olá", "como vai"]
        }
    ]


# ================================
# FIXTURES - API
# ================================

@pytest.fixture
def api_integration_hub():
    """Create ApiIntegrationHub instance."""
    from api.api_integration_hub import ApiIntegrationHub
    return ApiIntegrationHub()


# ================================
# FIXTURES - ERROR HANDLING
# ================================

@pytest.fixture
def error_handler():
    """Create ErrorHandler instance."""
    from utils.error_handler import ErrorHandler
    return ErrorHandler()


# ================================
# PYTEST CONFIGURATION
# ================================

def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )


# ================================
# CLEANUP
# ================================

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Cleanup test data after each test."""
    yield
    
    # Cleanup test directories
    test_dirs = [
        "test_data/personality",
        "test_data/memory",
        "test_data/companion",
        "test_data/contextual"
    ]
    
    for test_dir in test_dirs:
        path = Path(test_dir)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
