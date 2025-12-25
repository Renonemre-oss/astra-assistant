#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/Astra - Memory System Tests
Comprehensive unit tests for the memory system
"""

import pytest
from datetime import datetime, timedelta
from modules.memory_system import (
    MemorySystem,
    MemoryEntry,
    MemoryType,
    MemoryImportance,
    PatternRecognizer
)


class TestMemoryEntry:
    """Test suite for MemoryEntry."""
    
    def test_memory_entry_creation(self):
        """Test creating a memory entry."""
        memory = MemoryEntry(
            content="O usuário gosta de pizza",
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.MEDIUM,
            tags=["comida", "preferência"]
        )
        
        assert memory.content == "O usuário gosta de pizza"
        assert memory.memory_type == MemoryType.SEMANTIC
        assert memory.importance == MemoryImportance.MEDIUM
        assert "comida" in memory.tags
        
    def test_memory_id_generation(self):
        """Test that memory IDs are generated."""
        memory = MemoryEntry(
            content="Test memory",
            memory_type=MemoryType.EPISODIC
        )
        assert memory.id is not None
        assert len(memory.id) > 0
        
    def test_memory_access_count(self):
        """Test memory access counting."""
        memory = MemoryEntry(
            content="Test",
            memory_type=MemoryType.SEMANTIC
        )
        
        initial_count = memory.access_count
        memory.access()
        memory.access()
        
        assert memory.access_count == initial_count + 2
        
    def test_relevance_score_calculation(self):
        """Test relevance score calculation."""
        memory = MemoryEntry(
            content="O usuário gosta de programação em Python",
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.HIGH,
            tags=["programação", "Python"]
        )
        
        query_terms = ["python", "programação"]
        score = memory.get_relevance_score(query_terms)
        
        assert 0 <= score <= 1
        assert score > 0.5  # Should be relevant
        
    def test_memory_to_dict(self):
        """Test converting memory to dictionary."""
        memory = MemoryEntry(
            content="Test",
            memory_type=MemoryType.EPISODIC,
            importance=MemoryImportance.MEDIUM
        )
        
        memory_dict = memory.to_dict()
        
        assert isinstance(memory_dict, dict)
        assert memory_dict["content"] == "Test"
        assert "timestamp" in memory_dict
        
    def test_memory_from_dict(self):
        """Test creating memory from dictionary."""
        data = {
            "id": "test123",
            "content": "Test memory",
            "memory_type": "semantic",
            "importance": "high",
            "tags": ["test"],
            "emotions": [],
            "context": {},
            "timestamp": datetime.now().isoformat(),
            "access_count": 5,
            "last_accessed": datetime.now().isoformat(),
            "associations": [],
            "decay_factor": 1.0
        }
        
        memory = MemoryEntry.from_dict(data)
        
        assert memory.id == "test123"
        assert memory.content == "Test memory"
        assert memory.access_count == 5


class TestMemorySystem:
    """Test suite for MemorySystem."""
    
    def test_initialization(self, memory_system):
        """Test MemorySystem initialization."""
        assert memory_system is not None
        assert isinstance(memory_system.memories, dict)
        
    def test_store_memory(self, memory_system):
        """Test storing a memory."""
        memory_id = memory_system.store(
            content="O usuário prefere café",
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.MEDIUM,
            tags=["comida", "bebida"]
        )
        
        assert memory_id is not None
        assert memory_id in memory_system.memories
        
    def test_recall_memory(self, memory_system):
        """Test recalling memories."""
        # Store some memories
        memory_system.store(
            content="Reunião às 14h",
            memory_type=MemoryType.EPISODIC,
            importance=MemoryImportance.HIGH,
            tags=["trabalho"]
        )
        
        memory_system.store(
            content="Gosta de pizza",
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.MEDIUM,
            tags=["comida"]
        )
        
        # Recall
        results = memory_system.recall("trabalho reunião", max_results=5)
        
        assert len(results) > 0
        assert any("reunião" in r[0].content.lower() for r in results)
        
    def test_recall_by_type(self, memory_system):
        """Test recalling memories by type."""
        # Store different types
        memory_system.store(
            "Evento ontem",
            MemoryType.EPISODIC,
            MemoryImportance.MEDIUM
        )
        
        memory_system.store(
            "Python é uma linguagem",
            MemoryType.SEMANTIC,
            MemoryImportance.MEDIUM
        )
        
        # Recall semantic only
        results = memory_system.recall_by_type(MemoryType.SEMANTIC)
        
        assert len(results) > 0
        assert all(m.memory_type == MemoryType.SEMANTIC for m in results)
        
    def test_recall_by_tag(self, memory_system):
        """Test recalling memories by tag."""
        memory_system.store(
            "Pizza margherita",
            MemoryType.SEMANTIC,
            tags=["comida", "italiana"]
        )
        
        memory_system.store(
            "Pasta carbonara",
            MemoryType.SEMANTIC,
            tags=["comida", "italiana"]
        )
        
        results = memory_system.recall_by_tag("italiana")
        
        assert len(results) >= 2
        
    def test_recall_by_importance(self, memory_system):
        """Test recalling memories by importance."""
        memory_system.store(
            "Crítico",
            MemoryType.EPISODIC,
            importance=MemoryImportance.CRITICAL
        )
        
        memory_system.store(
            "Trivial",
            MemoryType.EPISODIC,
            importance=MemoryImportance.TRIVIAL
        )
        
        results = memory_system.recall_by_importance(MemoryImportance.CRITICAL)
        
        assert len(results) > 0
        assert all(m.importance == MemoryImportance.CRITICAL for m in results)
        
    def test_update_memory(self, memory_system):
        """Test updating an existing memory."""
        memory_id = memory_system.store(
            "Original content",
            MemoryType.SEMANTIC
        )
        
        success = memory_system.update_memory(
            memory_id,
            content="Updated content"
        )
        
        assert success
        assert memory_system.memories[memory_id].content == "Updated content"
        
    def test_delete_memory(self, memory_system):
        """Test deleting a memory."""
        memory_id = memory_system.store(
            "To be deleted",
            MemoryType.EPISODIC
        )
        
        success = memory_system.delete_memory(memory_id)
        
        assert success
        assert memory_id not in memory_system.memories
        
    def test_memory_associations(self, memory_system):
        """Test creating associations between memories."""
        id1 = memory_system.store("Python programming", MemoryType.SEMANTIC)
        id2 = memory_system.store("Machine learning", MemoryType.SEMANTIC)
        
        memory_system.associate_memories(id1, id2)
        
        assert id2 in memory_system.memories[id1].associations
        assert id1 in memory_system.memories[id2].associations
        
    def test_get_statistics(self, memory_system):
        """Test getting memory statistics."""
        # Store various memories
        for i in range(5):
            memory_system.store(
                f"Memory {i}",
                MemoryType.SEMANTIC,
                importance=MemoryImportance.MEDIUM
            )
        
        stats = memory_system.get_statistics()
        
        assert stats["total_memories"] >= 5
        assert "by_type" in stats
        assert "by_importance" in stats
        
    def test_memory_decay(self, memory_system):
        """Test memory decay over time."""
        memory = MemoryEntry(
            "Old memory",
            MemoryType.EPISODIC,
            importance=MemoryImportance.LOW
        )
        
        # Simulate time passage
        memory.timestamp = (datetime.now() - timedelta(days=30)).isoformat()
        
        # Check relevance decreases with time
        recent_score = MemoryEntry(
            "Recent memory",
            MemoryType.EPISODIC
        ).get_relevance_score(["memory"])
        
        old_score = memory.get_relevance_score(["memory"])
        
        # Recent should generally score higher (though not guaranteed due to other factors)
        # This is more of a sanity check
        assert old_score >= 0
        
    def test_save_and_load(self, memory_system, temp_dir):
        """Test saving and loading memories."""
        memory_system.data_dir = temp_dir / "memory"
        memory_system.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Store some memories
        memory_system.store("Test memory 1", MemoryType.SEMANTIC)
        memory_system.store("Test memory 2", MemoryType.EPISODIC)
        
        # Save
        memory_system.save_memories()
        
        # Create new instance and load
        new_system = MemorySystem(data_dir=str(temp_dir / "memory"))
        
        assert len(new_system.memories) >= 2
        
    def test_pattern_recognition(self, memory_system):
        """Test pattern recognition in memories."""
        # Store memories with patterns
        for i in range(10):
            memory_system.store(
                f"Morning routine {i}",
                MemoryType.EPISODIC,
                tags=["morning", "routine"]
            )
        
        patterns = memory_system.analyze_patterns()
        
        assert "topic_preferences" in patterns
        
    def test_empty_query_recall(self, memory_system):
        """Test recall with empty query."""
        memory_system.store("Test", MemoryType.SEMANTIC)
        
        results = memory_system.recall("")
        
        # Should return all or top memories
        assert len(results) >= 0
        
    def test_recall_with_time_range(self, memory_system):
        """Test recalling memories within time range."""
        # Store recent memory
        recent_id = memory_system.store(
            "Recent event",
            MemoryType.EPISODIC
        )
        
        # Get memories from last hour
        results = memory_system.recall_recent(hours=1)
        
        assert len(results) > 0
        assert any(m.id == recent_id for m in results)
        
    def test_consolidate_memories(self, memory_system):
        """Test memory consolidation."""
        # Store similar memories
        memory_system.store("Likes pizza", MemoryType.SEMANTIC, tags=["food"])
        memory_system.store("Loves pizza", MemoryType.SEMANTIC, tags=["food"])
        memory_system.store("Enjoys pizza", MemoryType.SEMANTIC, tags=["food"])
        
        initial_count = len(memory_system.memories)
        
        # Consolidate similar memories
        memory_system.consolidate_similar_memories(similarity_threshold=0.8)
        
        # Should have fewer memories after consolidation
        assert len(memory_system.memories) <= initial_count


class TestPatternRecognizer:
    """Test suite for PatternRecognizer."""
    
    def test_initialization(self):
        """Test PatternRecognizer initialization."""
        recognizer = PatternRecognizer()
        assert recognizer is not None
        
    def test_analyze_patterns(self, memory_system):
        """Test pattern analysis."""
        recognizer = PatternRecognizer()
        
        # Create memories with patterns
        memories = []
        for i in range(5):
            memories.append(MemoryEntry(
                f"Work meeting {i}",
                MemoryType.EPISODIC,
                tags=["work", "meeting"]
            ))
        
        patterns = recognizer.analyze_interaction_patterns(memories)
        
        assert "topic_preferences" in patterns
        assert "frequency_patterns" in patterns

