#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Sistema de Memória Inteligente
Sistema avançado de memória que simula a memória humana com diferentes tipos:
- Memória Episódica: Eventos específicos e experiências
- Memória Semântica: Conhecimento geral e fatos
- Memória de Trabalho: Contexto atual da conversa
- Reconhecimento de Padrões: Tendências e hábitos do usuário

Funcionalidades:
- Armazenamento inteligente de informações
- Recuperação contextual de memórias
- Análise de padrões comportamentais
- Aprendizado contínuo sobre o usuário
- Associações automáticas entre conceitos
"""

import logging
import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
from pathlib import Path
from collections import defaultdict, Counter
import re
import math

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Tipos de memória do sistema."""
    EPISODIC = "episodic"      # Eventos específicos
    SEMANTIC = "semantic"      # Conhecimento geral
    PROCEDURAL = "procedural"  # Como fazer coisas
    WORKING = "working"        # Contexto atual
    EMOTIONAL = "emotional"    # Memórias emocionais

class MemoryImportance(Enum):
    """Níveis de importância da memória."""
    CRITICAL = "critical"      # 5 - Muito importante
    HIGH = "high"             # 4 - Importante  
    MEDIUM = "medium"         # 3 - Moderada
    LOW = "low"               # 2 - Baixa
    TRIVIAL = "trivial"       # 1 - Trivial

class MemoryEntry:
    """Representação de uma entrada de memória."""
    
    def __init__(self, content: str, memory_type: MemoryType, 
                 importance: MemoryImportance = MemoryImportance.MEDIUM,
                 tags: List[str] = None, emotions: List[str] = None,
                 context: Dict = None):
        self.id = self._generate_id(content)
        self.content = content
        self.memory_type = memory_type
        self.importance = importance
        self.tags = tags or []
        
        # 💡 REGRA: Emoção NUNCA armazenada sozinha!
        # Emoções só existem com contexto obrigatório
        self._validate_emotional_memory(emotions, context)
        self.emotions = emotions or []
        self.context = context or {}
        
        self.timestamp = datetime.now().isoformat()
        self.access_count = 0
        self.last_accessed = self.timestamp
        self.associations = []  # IDs de memórias relacionadas
        
        # Decay agressivo para memórias emocionais
        if self.emotions:
            self.decay_factor = 1.0  # Inicia em 1.0
            self.emotional_decay_rate = 0.15  # 15% decay por dia (AGRESSIVO)
        else:
            self.decay_factor = 1.0
            self.emotional_decay_rate = 0.05  # 5% decay por dia (normal)
        
    def _generate_id(self, content: str) -> str:
        """Gera ID único para a memória."""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp_hash = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:4]
        return f"{content_hash}_{timestamp_hash}"
    
    def _validate_emotional_memory(self, emotions: List[str], context: Dict):
        """
        Valida que memórias emocionais SEMPRE têm contexto.
        
        REGRA CRÍTICA: Emoção NUNCA existe sozinha!
        - Precisa de evento (o que aconteceu)
        - Precisa de pessoa (com quem foi)
        - Precisa de contexto temporal (quando foi)
        """
        if not emotions or len(emotions) == 0:
            return  # Sem emoções, sem validação necessária
        
        if not context:
            raise ValueError(
                "❌ ERRO: Memória emocional sem contexto! "
                "Emoções devem estar associadas a evento, pessoa ou contexto temporal."
            )
        
        # Verificar se tem pelo menos UM dos contextos obrigatórios
        required_context_keys = ['event', 'person', 'people', 'temporal_context', 'time_context']
        has_required_context = any(key in context for key in required_context_keys)
        
        if not has_required_context:
            logger.warning(
                f"⚠️ Memória emocional sem contexto adequado. "
                f"Emoções: {emotions}. Contexto: {list(context.keys())}"
            )
            # Adicionar contexto temporal mínimo como fallback
            context['temporal_context'] = datetime.now().isoformat()
    
    def access(self):
        """Marca que a memória foi acessada."""
        self.access_count += 1
        self.last_accessed = datetime.now().isoformat()
        
        # Reforça a memória diferentemente baseado no tipo
        if self.emotions:
            # Emocionais: reforço menor (evita "ressentimento")
            self.decay_factor = min(1.0, self.decay_factor + 0.05)
        else:
            # Normais: reforço padrão
            self.decay_factor = min(1.0, self.decay_factor + 0.1)
    
    def get_relevance_score(self, query_terms: List[str], current_time: datetime = None) -> float:
        """
        Calcula score de relevância da memória para uma query.
        
        Args:
            query_terms: Termos da busca
            current_time: Tempo atual para cálculo de decay
            
        Returns:
            float: Score de relevância (0-1)
        """
        if current_time is None:
            current_time = datetime.now()
        
        # Score base por importância
        importance_scores = {
            MemoryImportance.CRITICAL: 1.0,
            MemoryImportance.HIGH: 0.8,
            MemoryImportance.MEDIUM: 0.6,
            MemoryImportance.LOW: 0.4,
            MemoryImportance.TRIVIAL: 0.2
        }
        base_score = importance_scores[self.importance]
        
        # Score por match de conteúdo
        content_lower = self.content.lower()
        content_score = 0
        for term in query_terms:
            if term.lower() in content_lower:
                content_score += 1
        content_score = min(1.0, content_score / len(query_terms)) if query_terms else 0
        
        # Score por tags
        tag_score = 0
        for term in query_terms:
            for tag in self.tags:
                if term.lower() in tag.lower():
                    tag_score += 1
        tag_score = min(1.0, tag_score / len(self.tags)) if self.tags else 0
        
        # Score temporal com decay diferenciado
        memory_time = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00').replace('+00:00', ''))
        hours_ago = (current_time - memory_time).total_seconds() / 3600
        days_ago = hours_ago / 24
        
        # Aplicar decay acumulado desde criação
        accumulated_decay = self.decay_factor * (1 - self.emotional_decay_rate) ** days_ago
        
        if self.emotions:
            # Memórias emocionais: decay MUITO mais agressivo
            # Meia-vida de ~5 dias (vs 7 dias para memórias normais)
            temporal_score = math.exp(-hours_ago / 120) * accumulated_decay
        else:
            # Memórias normais: decay padrão (7 dias)
            temporal_score = math.exp(-hours_ago / 168) * accumulated_decay
        
        # Score por frequência de acesso
        access_score = min(1.0, self.access_count / 10)  # Normaliza até 10 acessos
        
        # Score final combinado
        final_score = (
            base_score * 0.3 +
            content_score * 0.4 +
            tag_score * 0.1 +
            temporal_score * 0.1 +
            access_score * 0.1
        )
        
        return min(1.0, final_score)
    
    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return {
            'id': self.id,
            'content': self.content,
            'memory_type': self.memory_type.value,
            'importance': self.importance.value,
            'tags': self.tags,
            'emotions': self.emotions,
            'context': self.context,
            'timestamp': self.timestamp,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed,
            'associations': self.associations,
            'decay_factor': self.decay_factor,
            'emotional_decay_rate': getattr(self, 'emotional_decay_rate', 0.05)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryEntry':
        """Cria instância a partir de dicionário."""
        entry = cls(
            content=data['content'],
            memory_type=MemoryType(data['memory_type']),
            importance=MemoryImportance(data['importance']),
            tags=data.get('tags', []),
            emotions=data.get('emotions', []),
            context=data.get('context', {})
        )
        entry.id = data['id']
        entry.timestamp = data['timestamp']
        entry.access_count = data.get('access_count', 0)
        entry.last_accessed = data.get('last_accessed', entry.timestamp)
        entry.associations = data.get('associations', [])
        entry.decay_factor = data.get('decay_factor', 1.0)
        entry.emotional_decay_rate = data.get('emotional_decay_rate', 0.15 if entry.emotions else 0.05)
        return entry

class PatternRecognizer:
    """Sistema de reconhecimento de padrões comportamentais."""
    
    def __init__(self):
        self.patterns = defaultdict(list)
        self.user_habits = {}
        self.temporal_patterns = defaultdict(lambda: defaultdict(int))
    
    def analyze_interaction_patterns(self, memories: List[MemoryEntry]) -> Dict:
        """Analisa padrões nas interações do usuário."""
        patterns_found = {
            'time_preferences': {},
            'topic_preferences': {},
            'emotional_patterns': {},
            'frequency_patterns': {},
            'behavioral_trends': []
        }
        
        # Análise temporal
        hour_activity = defaultdict(int)
        for memory in memories:
            try:
                mem_time = datetime.fromisoformat(memory.timestamp.replace('Z', '+00:00').replace('+00:00', ''))
                hour_activity[mem_time.hour] += 1
            except:
                continue
        
        if hour_activity:
            most_active_hour = max(hour_activity, key=hour_activity.get)
            patterns_found['time_preferences'] = {
                'most_active_hour': most_active_hour,
                'activity_distribution': dict(hour_activity)
            }
        
        # Análise de tópicos
        topic_counter = Counter()
        for memory in memories:
            topic_counter.update(memory.tags)
        
        patterns_found['topic_preferences'] = dict(topic_counter.most_common(10))
        
        # Análise emocional
        emotion_counter = Counter()
        for memory in memories:
            emotion_counter.update(memory.emotions)
        
        patterns_found['emotional_patterns'] = dict(emotion_counter.most_common(5))
        
        # Padrões de frequência
        daily_interactions = defaultdict(int)
        for memory in memories:
            try:
                mem_date = datetime.fromisoformat(memory.timestamp.replace('Z', '+00:00').replace('+00:00', '')).date()
                daily_interactions[str(mem_date)] += 1
            except:
                continue
        
        if daily_interactions:
            avg_daily = sum(daily_interactions.values()) / len(daily_interactions)
            patterns_found['frequency_patterns'] = {
                'avg_daily_interactions': round(avg_daily, 2),
                'most_active_day': max(daily_interactions, key=daily_interactions.get),
                'total_days': len(daily_interactions)
            }
        
        # Tendências comportamentais
        if len(memories) > 10:
            recent_memories = sorted(memories, key=lambda m: m.timestamp, reverse=True)[:10]
            older_memories = memories[:-10] if len(memories) > 20 else []
            
            if older_memories:
                recent_emotions = Counter()
                older_emotions = Counter()
                
                for mem in recent_memories:
                    recent_emotions.update(mem.emotions)
                for mem in older_memories:
                    older_emotions.update(mem.emotions)
                
                # Comparar tendências emocionais
                trends = []
                for emotion in recent_emotions:
                    recent_freq = recent_emotions[emotion] / len(recent_memories)
                    older_freq = older_emotions.get(emotion, 0) / len(older_memories) if older_memories else 0
                    
                    if recent_freq > older_freq * 1.5:
                        trends.append(f"Aumento em {emotion}")
                    elif recent_freq < older_freq * 0.5:
                        trends.append(f"Diminuição em {emotion}")
                
                patterns_found['behavioral_trends'] = trends
        
        return patterns_found

class MemorySystem:
    """
    Sistema principal de memória inteligente do ASTRA.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Inicializa o sistema de memória.
        
        Args:
            data_dir: Diretório para armazenar dados de memória
        """
        self.data_dir = Path(data_dir or "data/memory")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Armazenamento de memórias
        self.memories: Dict[str, MemoryEntry] = {}
        self.memory_index = defaultdict(set)  # Índice para busca rápida
        
        # Sistema de padrões
        self.pattern_recognizer = PatternRecognizer()
        
        # Contexto de trabalho (memória de curto prazo)
        self.working_memory = []
        self.working_memory_size = 10
        
        # Configuração
        self.max_memories = 10000  # Limite de memórias
        self.cleanup_threshold = 0.8  # Limpar quando atingir 80% do limite
        
        # Arquivos de dados
        self.memories_file = self.data_dir / "memories.json"
        self.patterns_file = self.data_dir / "patterns.json"
        self.stats_file = self.data_dir / "memory_stats.json"
        
        # Estatísticas
        self.stats = {
            'total_memories': 0,
            'memories_by_type': defaultdict(int),
            'memories_by_importance': defaultdict(int),
            'total_retrievals': 0,
            'last_cleanup': None
        }
        
        # Carregar dados existentes
        self.load_memories()
        
        logger.info("Sistema de Memória Inteligente inicializado")
    
    def store_memory(self, content: str, memory_type: MemoryType,
                    importance: MemoryImportance = MemoryImportance.MEDIUM,
                    tags: List[str] = None, emotions: List[str] = None,
                    context: Dict = None) -> str:
        """
        Armazena uma nova memória no sistema.
        
        Args:
            content: Conteúdo da memória
            memory_type: Tipo de memória
            importance: Importância da memória
            tags: Tags relacionadas
            emotions: Emoções associadas
            context: Contexto adicional
            
        Returns:
            str: ID da memória armazenada
        """
        # Criar entrada de memória
        memory = MemoryEntry(
            content=content,
            memory_type=memory_type,
            importance=importance,
            tags=tags or [],
            emotions=emotions or [],
            context=context or {}
        )
        
        # Armazenar
        self.memories[memory.id] = memory
        
        # Atualizar índices
        self._update_indexes(memory)
        
        # Adicionar à memória de trabalho se relevante
        if importance != MemoryImportance.TRIVIAL:
            self.working_memory.append(memory.id)
            if len(self.working_memory) > self.working_memory_size:
                self.working_memory.pop(0)
        
        # Atualizar estatísticas
        self.stats['total_memories'] += 1
        self.stats['memories_by_type'][memory_type.value] += 1
        self.stats['memories_by_importance'][importance.value] += 1
        
        # Limpeza automática se necessário
        if len(self.memories) > self.max_memories * self.cleanup_threshold:
            self._cleanup_old_memories()
        
        logger.info(f"Memória armazenada: {memory.id} ({memory_type.value})")
        return memory.id
    
    def retrieve_memories(self, query: str, memory_types: List[MemoryType] = None,
                         max_results: int = 10, min_relevance: float = 0.1) -> List[MemoryEntry]:
        """
        Recupera memórias relevantes para uma query.
        
        Args:
            query: Texto da consulta
            memory_types: Tipos de memória a buscar
            max_results: Máximo de resultados
            min_relevance: Relevância mínima
            
        Returns:
            List[MemoryEntry]: Lista de memórias relevantes
        """
        query_terms = self._extract_terms(query)
        results = []
        
        # Filtrar por tipo se especificado
        candidate_memories = []
        if memory_types:
            for memory in self.memories.values():
                if memory.memory_type in memory_types:
                    candidate_memories.append(memory)
        else:
            candidate_memories = list(self.memories.values())
        
        # Calcular relevância e filtrar
        for memory in candidate_memories:
            relevance = memory.get_relevance_score(query_terms)
            if relevance >= min_relevance:
                memory.access()  # Marcar como acessada
                results.append((memory, relevance))
        
        # Ordenar por relevância
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Atualizar estatísticas
        self.stats['total_retrievals'] += 1
        
        # Retornar apenas as memórias (sem scores)
        return [memory for memory, _ in results[:max_results]]
    
    def store_conversation_turn(self, user_input: str, assistant_response: str,
                               user_emotions: List[str] = None, context: Dict = None) -> Tuple[str, str]:
        """
        Armazena um turno completo de conversa.
        
        Args:
            user_input: Input do usuário
            assistant_response: Resposta do assistente
            user_emotions: Emoções detectadas
            context: Contexto da conversa
            
        Returns:
            Tuple[str, str]: IDs das memórias criadas (usuário, assistente)
        """
        # Extrair tags automaticamente
        user_tags = self._extract_tags(user_input)
        assistant_tags = self._extract_tags(assistant_response)
        
        # Determinar importância baseada em comprimento e emoções
        user_importance = self._determine_importance(user_input, user_emotions)
        assistant_importance = MemoryImportance.MEDIUM
        
        # 💡 Enriquecer contexto se houver emoções (OBRIGATÓRIO!)
        enriched_context = dict(context or {})
        if user_emotions and len(user_emotions) > 0:
            enriched_context = self._enrich_emotional_context(
                user_input, 
                user_emotions, 
                enriched_context
            )
        
        # Armazenar memória do usuário
        user_memory_id = self.store_memory(
            content=f"Usuário disse: {user_input}",
            memory_type=MemoryType.EPISODIC,
            importance=user_importance,
            tags=user_tags,
            emotions=user_emotions or [],
            context=enriched_context
        )
        
        # Armazenar memória do assistente
        assistant_memory_id = self.store_memory(
            content=f"ASTRA respondeu: {assistant_response}",
            memory_type=MemoryType.EPISODIC,
            importance=assistant_importance,
            tags=assistant_tags,
            emotions=[],
            context=context or {}
        )
        
        # Criar associação entre as memórias
        self._create_association(user_memory_id, assistant_memory_id)
        
        return user_memory_id, assistant_memory_id
    
    def store_emotional_memory(self, content: str, emotions: List[str], 
                                event: str, person: str = None, 
                                importance: MemoryImportance = MemoryImportance.HIGH) -> str:
        """
        Armazena uma memória emocional com validação obrigatória de contexto.
        
        💡 USO CORRETO DE MEMÓRIAS EMOCIONAIS:
        - SEMPRE associar emoção a evento específico
        - SEMPRE incluir pessoa envolvida (se aplicável)
        - Decay AGRESSIVO automático para evitar "ressentimento"
        
        Args:
            content: Conteúdo da memória
            emotions: Lista de emoções (ex: ['happy', 'excited'])
            event: Evento específico (OBRIGATÓRIO)
            person: Pessoa envolvida (opcional mas recomendado)
            importance: Importância da memória
            
        Returns:
            str: ID da memória criada
            
        Example:
            >>> memory_system.store_emotional_memory(
            ...     content="Usuário me agradeceu muito",
            ...     emotions=['happy', 'grateful'],
            ...     event="Ajudei com problema urgente",
            ...     person="João"
            ... )
        """
        if not emotions or len(emotions) == 0:
            raise ValueError("❌ Memória emocional precisa de pelo menos uma emoção!")
        
        if not event:
            raise ValueError(
                "❌ Memória emocional DEVE ter evento associado! "
                "Emoção nunca existe sozinha."
            )
        
        # Construir contexto rico obrigatório
        context = {
            'event': event,
            'temporal_context': datetime.now().isoformat(),
            'memory_category': 'emotional'
        }
        
        if person:
            context['person'] = person
        
        # Extrair tags do evento
        tags = self._extract_tags(event)
        tags.extend(['emocional', 'importante'])
        
        logger.info(
            f"💛 Armazenando memória emocional: {emotions} "
            f"| Evento: {event} | Pessoa: {person or 'N/A'}"
        )
        
        return self.store_memory(
            content=content,
            memory_type=MemoryType.EMOTIONAL,
            importance=importance,
            tags=tags,
            emotions=emotions,
            context=context
        )
    
    def learn_fact(self, fact: str, category: str = "geral", 
                   importance: MemoryImportance = MemoryImportance.MEDIUM) -> str:
        """
        Aprende um fato novo (memória semântica).
        
        Args:
            fact: Fato a ser aprendido
            category: Categoria do fato
            importance: Importância do fato
            
        Returns:
            str: ID da memória criada
        """
        tags = [category, "fato", "conhecimento"]
        return self.store_memory(
            content=fact,
            memory_type=MemoryType.SEMANTIC,
            importance=importance,
            tags=tags
        )
    
    def get_relevant_context(self, current_input: str, max_memories: int = 5) -> str:
        """
        Obtém contexto relevante para a conversa atual.
        
        Args:
            current_input: Input atual do usuário
            max_memories: Máximo de memórias para incluir
            
        Returns:
            str: Contexto formatado para o LLM
        """
        # Buscar memórias relevantes
        relevant_memories = self.retrieve_memories(
            query=current_input,
            memory_types=[MemoryType.EPISODIC, MemoryType.SEMANTIC],
            max_results=max_memories,
            min_relevance=0.2
        )
        
        if not relevant_memories:
            return ""
        
        # Formatar contexto
        context_parts = ["Contexto de memórias relevantes:"]
        for memory in relevant_memories:
            # Remover prefixos desnecessários
            content = memory.content
            if content.startswith("Usuário disse: "):
                content = content[15:]
            elif content.startswith("ASTRA respondeu: "):
                content = content[16:]
            
            context_parts.append(f"- {content}")
        
        return "\n".join(context_parts)
    
    def analyze_user_patterns(self) -> Dict:
        """
        Analisa padrões comportamentais do usuário.
        
        Returns:
            Dict: Análise de padrões encontrados
        """
        user_memories = [
            memory for memory in self.memories.values()
            if memory.memory_type == MemoryType.EPISODIC and "Usuário disse:" in memory.content
        ]
        
        return self.pattern_recognizer.analyze_interaction_patterns(user_memories)
    
    def get_memory_summary(self) -> Dict:
        """Retorna resumo do sistema de memória."""
        patterns = self.analyze_user_patterns()
        
        return {
            'total_memories': len(self.memories),
            'memories_by_type': dict(self.stats['memories_by_type']),
            'memories_by_importance': dict(self.stats['memories_by_importance']),
            'working_memory_size': len(self.working_memory),
            'total_retrievals': self.stats['total_retrievals'],
            'user_patterns': patterns,
            'memory_health': self._assess_memory_health()
        }
    
    def _update_indexes(self, memory: MemoryEntry):
        """Atualiza índices de busca."""
        # Índice por tags
        for tag in memory.tags:
            self.memory_index[f"tag:{tag.lower()}"].add(memory.id)
        
        # Índice por tipo
        self.memory_index[f"type:{memory.memory_type.value}"].add(memory.id)
        
        # Índice por importância
        self.memory_index[f"importance:{memory.importance.value}"].add(memory.id)
        
        # Índice por termos do conteúdo
        terms = self._extract_terms(memory.content)
        for term in terms:
            self.memory_index[f"term:{term}"].add(memory.id)
    
    def _extract_terms(self, text: str) -> List[str]:
        """Extrai termos relevantes do texto."""
        # Remover pontuação e converter para minúsculas
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Palavras significativas (filtrar stop words básicas)
        stop_words = {
            'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
            'e', 'ou', 'mas', 'se', 'que', 'de', 'do', 'da',
            'em', 'no', 'na', 'por', 'para', 'com', 'sem',
            'é', 'são', 'foi', 'era', 'está', 'estou', 'estava'
        }
        
        terms = []
        for word in text.split():
            if len(word) > 2 and word not in stop_words:
                terms.append(word)
        
        return terms
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extrai tags automáticas do texto."""
        text_lower = text.lower()
        tags = []
        
        # Tags por categorias
        category_keywords = {
            'tempo': ['tempo', 'clima', 'chuva', 'sol', 'temperatura'],
            'música': ['música', 'canção', 'banda', 'artista', 'tocar'],
            'comida': ['comida', 'comer', 'fome', 'jantar', 'almoço'],
            'trabalho': ['trabalho', 'trabalhar', 'projeto', 'reunião', 'chefe'],
            'saúde': ['saúde', 'médico', 'dor', 'remédio', 'exercício'],
            'família': ['família', 'pai', 'mãe', 'irmão', 'filho'],
            'lazer': ['filme', 'jogo', 'diversão', 'passear', 'viajar'],
            'tecnologia': ['computador', 'celular', 'internet', 'programa']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(category)
        
        # Tags por ações
        if any(word in text_lower for word in ['comprar', 'compra', 'shopping']):
            tags.append('compras')
        if any(word in text_lower for word in ['estudar', 'estudo', 'aprender']):
            tags.append('educação')
        if any(word in text_lower for word in ['problema', 'ajuda', 'dificuldade']):
            tags.append('problema')
        
        return tags
    
    def _determine_importance(self, text: str, emotions: List[str] = None) -> MemoryImportance:
        """Determina importância baseada no conteúdo."""
        # Importância por emocões
        if emotions:
            strong_emotions = ['frustrated', 'excited', 'sad', 'happy']
            if any(emotion in strong_emotions for emotion in emotions):
                return MemoryImportance.HIGH
        
        # Importância por palavras-chave
        text_lower = text.lower()
        critical_keywords = ['urgente', 'importante', 'crítico', 'emergência']
        if any(keyword in text_lower for keyword in critical_keywords):
            return MemoryImportance.CRITICAL
        
        high_keywords = ['problema', 'ajuda', 'preciso', 'quero', 'gostaria']
        if any(keyword in text_lower for keyword in high_keywords):
            return MemoryImportance.HIGH
        
        # Importância por comprimento
        if len(text) > 100:
            return MemoryImportance.MEDIUM
        elif len(text) < 20:
            return MemoryImportance.LOW
        
        return MemoryImportance.MEDIUM
    
    def _create_association(self, memory_id1: str, memory_id2: str):
        """Cria associação entre duas memórias."""
        if memory_id1 in self.memories and memory_id2 in self.memories:
            self.memories[memory_id1].associations.append(memory_id2)
            self.memories[memory_id2].associations.append(memory_id1)
    
    def _cleanup_old_memories(self):
        """Remove memórias antigas e menos importantes."""
        if len(self.memories) <= self.max_memories:
            return
        
        # Ordenar por relevância (considerando idade, acesso, importância)
        current_time = datetime.now()
        memory_scores = []
        
        for memory in self.memories.values():
            # Score baseado em importância, acesso e idade
            importance_score = {
                MemoryImportance.CRITICAL: 5,
                MemoryImportance.HIGH: 4,
                MemoryImportance.MEDIUM: 3,
                MemoryImportance.LOW: 2,
                MemoryImportance.TRIVIAL: 1
            }[memory.importance]
            
            access_score = min(5, memory.access_count)
            
            # Score temporal (memórias recentes são mais importantes)
            try:
                mem_time = datetime.fromisoformat(memory.timestamp.replace('Z', '+00:00').replace('+00:00', ''))
                days_old = (current_time - mem_time).days
                age_score = max(1, 5 - (days_old / 30))  # Decresce ao longo de 30 dias
            except:
                age_score = 1
            
            total_score = (importance_score * 0.5 + access_score * 0.3 + age_score * 0.2) * memory.decay_factor
            memory_scores.append((memory.id, total_score))
        
        # Ordenar por score e manter apenas as melhores
        memory_scores.sort(key=lambda x: x[1], reverse=True)
        memories_to_keep = set(score[0] for score in memory_scores[:self.max_memories])
        
        # Remover memórias de baixo score
        memories_to_remove = set(self.memories.keys()) - memories_to_keep
        for memory_id in memories_to_remove:
            del self.memories[memory_id]
        
        # Limpar índices
        self.memory_index.clear()
        for memory in self.memories.values():
            self._update_indexes(memory)
        
        self.stats['last_cleanup'] = datetime.now().isoformat()
        logger.info(f"Limpeza de memória: {len(memories_to_remove)} memórias removidas")
    
    def _enrich_emotional_context(self, user_input: str, emotions: List[str], 
                                   base_context: Dict) -> Dict:
        """
        Enriquece contexto para memórias emocionais.
        
        Garante que toda emoção tenha:
        - Evento (o que aconteceu)
        - Contexto temporal (quando foi)
        - Pessoa (se identificável)
        """
        enriched = dict(base_context)
        
        # Garantir contexto temporal
        if 'temporal_context' not in enriched and 'time_context' not in enriched:
            enriched['temporal_context'] = datetime.now().isoformat()
        
        # Tentar extrair evento do input se não houver
        if 'event' not in enriched:
            # Usar o próprio input como evento se for suficientemente descritivo
            if len(user_input) > 10:
                enriched['event'] = user_input[:100]  # Limitar tamanho
            else:
                enriched['event'] = f"Conversa com emoção {emotions[0]}"
        
        # Marcar como emocional
        enriched['has_emotions'] = True
        enriched['emotion_count'] = len(emotions)
        
        return enriched
    
    def cleanup_old_emotional_memories(self, days_threshold: int = 7):
        """
        Remove memórias emocionais antigas para evitar "ressentimento".
        
        🚨 Memórias emocionais têm vida útil curta de propósito!
        Isto evita que o ASTRA acumule "bagagem emocional" de bugs ou mal-entendidos.
        
        Args:
            days_threshold: Remover emocionais com mais de X dias
        """
        current_time = datetime.now()
        removed_count = 0
        
        emotional_memories = [
            (mem_id, mem) for mem_id, mem in self.memories.items()
            if mem.emotions and len(mem.emotions) > 0
        ]
        
        for mem_id, memory in emotional_memories:
            try:
                mem_time = datetime.fromisoformat(
                    memory.timestamp.replace('Z', '+00:00').replace('+00:00', '')
                )
                days_old = (current_time - mem_time).days
                
                # Remover emocionais antigas (threshold agressivo)
                if days_old > days_threshold:
                    del self.memories[mem_id]
                    removed_count += 1
                    logger.debug(
                        f"🧼 Removida memória emocional antiga: {mem_id} "
                        f"({days_old} dias, emoções: {memory.emotions})"
                    )
            except Exception as e:
                logger.warning(f"Erro ao processar memória {mem_id}: {e}")
        
        if removed_count > 0:
            # Reconstruir índices
            self.memory_index.clear()
            for memory in self.memories.values():
                self._update_indexes(memory)
            
            logger.info(
                f"✨ Limpeza emocional: {removed_count} memórias removidas "
                f"(threshold: {days_threshold} dias)"
            )
        
        return removed_count
    
    def _assess_memory_health(self) -> Dict:
        """Avalia a 'saúde' do sistema de memória."""
        total_memories = len(self.memories)
        if total_memories == 0:
            return {"status": "empty", "score": 0}
        
        # Distribuição por importância
        importance_distribution = defaultdict(int)
        emotional_count = 0
        for memory in self.memories.values():
            importance_distribution[memory.importance.value] += 1
            if memory.emotions:
                emotional_count += 1
        
        # Score de saúde baseado na distribuição e acesso
        health_score = 0
        total_accesses = sum(memory.access_count for memory in self.memories.values())
        avg_accesses = total_accesses / total_memories if total_memories > 0 else 0
        
        # Bonus por memórias importantes
        important_ratio = (importance_distribution.get('high', 0) + 
                          importance_distribution.get('critical', 0)) / total_memories
        health_score += important_ratio * 50
        
        # Bonus por acesso regular
        if avg_accesses > 1:
            health_score += min(30, avg_accesses * 10)
        
        # Bonus por diversidade de tipos
        type_diversity = len(set(memory.memory_type for memory in self.memories.values()))
        health_score += type_diversity * 5
        
        # PENALIDADE por excesso de memórias emocionais (evita "ressentimento")
        emotional_ratio = emotional_count / total_memories if total_memories > 0 else 0
        if emotional_ratio > 0.3:  # Mais de 30% emocionais é problemático
            health_score -= (emotional_ratio - 0.3) * 100
        
        health_score = max(0, min(100, health_score))
        
        status = "excellent" if health_score > 80 else \
                "good" if health_score > 60 else \
                "fair" if health_score > 40 else \
                "poor"
        
        return {
            "status": status,
            "score": round(health_score, 1),
            "total_memories": total_memories,
            "emotional_memories": emotional_count,
            "emotional_ratio": round(emotional_ratio, 2),
            "avg_accesses": round(avg_accesses, 2),
            "important_ratio": round(important_ratio, 2)
        }
    
    def save_memories(self):
        """Salva memórias em arquivo."""
        try:
            memories_data = {
                memory_id: memory.to_dict()
                for memory_id, memory in self.memories.items()
            }
            
            with open(self.memories_file, 'w', encoding='utf-8') as f:
                json.dump(memories_data, f, indent=2, ensure_ascii=False)
            
            # Salvar estatísticas
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erro ao salvar memórias: {e}")
    
    def load_memories(self):
        """Carrega memórias do arquivo."""
        try:
            if self.memories_file.exists():
                with open(self.memories_file, 'r', encoding='utf-8') as f:
                    memories_data = json.load(f)
                
                for memory_id, memory_dict in memories_data.items():
                    memory = MemoryEntry.from_dict(memory_dict)
                    self.memories[memory_id] = memory
                    self._update_indexes(memory)
                
                logger.info(f"Carregadas {len(self.memories)} memórias")
            
            # Carregar estatísticas
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    saved_stats = json.load(f)
                    self.stats.update(saved_stats)
                    
        except Exception as e:
            logger.error(f"Erro ao carregar memórias: {e}")


# Função utilitária para criar instância global
def create_memory_system() -> MemorySystem:
    """Cria uma instância do sistema de memória."""
    return MemorySystem()


if __name__ == "__main__":
    # Teste do sistema
    memory_system = MemorySystem()
    
    print("🧠 Teste do Sistema de Memória Inteligente")
    print("=" * 50)
    
    # Armazenar algumas memórias de teste
    test_memories = [
        ("Gosto muito de pizza", MemoryType.SEMANTIC, ["comida", "preferência"]),
        ("Tenho reunião amanhã às 14h", MemoryType.EPISODIC, ["trabalho", "compromisso"]),
        ("Meu filme favorito é Matrix", MemoryType.SEMANTIC, ["filme", "preferência"]),
        ("Estou feliz hoje!", MemoryType.EPISODIC, ["emoção"], ["happy"]),
        ("Como se faz café?", MemoryType.PROCEDURAL, ["bebida", "receita"]),
    ]
    
    for content, mem_type, tags, *emotions in test_memories:
        emotions = emotions[0] if emotions else []
        memory_id = memory_system.store_memory(
            content=content,
            memory_type=mem_type,
            tags=tags,
            emotions=emotions
        )
        print(f"✅ Armazenado: {content}")
    
    print("\n🔍 Testando recuperação de memórias:")
    queries = ["pizza", "trabalho", "filme", "feliz", "café"]
    
    for query in queries:
        memories = memory_system.retrieve_memories(query, max_results=3)
        print(f"\n📋 Query: '{query}'")
        for i, memory in enumerate(memories, 1):
            print(f"  {i}. {memory.content}")
    
    # Teste de conversa
    print("\n💬 Teste de armazenamento de conversa:")
    user_id, assistant_id = memory_system.store_conversation_turn(
        user_input="Qual o melhor restaurante de pizza?",
        assistant_response="Recomendo a Pizzaria do João, eles fazem uma pizza margherita excelente!",
        user_emotions=["neutral"],
        context={"topic": "comida", "location": "cidade"}
    )
    
    print(f"✅ Conversa armazenada: {user_id}, {assistant_id}")
    
    # Mostrar resumo
    print("\n📊 Resumo do Sistema de Memória:")
    summary = memory_system.get_memory_summary()
    for key, value in summary.items():
        if key != 'user_patterns':
            print(f"  {key}: {value}")
    
    print("\n🔍 Padrões do usuário:")
    patterns = summary['user_patterns']
    for pattern_type, data in patterns.items():
        if data:
            print(f"  {pattern_type}: {data}")
