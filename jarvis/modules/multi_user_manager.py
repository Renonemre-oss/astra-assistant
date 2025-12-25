#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Assistente Pessoal
Sistema de Gestão Multi-Utilizador

Sistema avançado para identificar diferentes utilizadores por voz, padrões de texto
e contexto, mantendo perfis separados para cada pessoa.
"""

import json
import logging
import hashlib
import numpy as np
from datetime import datetime
from typing import Dict, Optional, List, Any, Tuple
from pathlib import Path
from config import CONFIG, DATABASE_AVAILABLE
import re

# Configurar logger primeiro
logger = logging.getLogger(__name__)

try:
    from .voice_identification import VoiceIdentification
    VOICE_ID_AVAILABLE = True
except ImportError:
    VOICE_ID_AVAILABLE = False
    logger.warning("Sistema de identificação por voz não disponível")

try:
    from .contextual_analyzer import ContextualAnalyzer
    CONTEXTUAL_ANALYZER_AVAILABLE = True
except ImportError:
    CONTEXTUAL_ANALYZER_AVAILABLE = False
    logger.warning("Analisador contextual não disponível")

class MultiUserManager:
    """
    Gestor de múltiplos utilizadores.
    Identifica quem está a falar através de vários métodos e mantém contexto separado.
    """
    
    def __init__(self, database_manager=None):
        self.db_manager = database_manager
        self.users_file = CONFIG["facts_file"].parent / "users.json"
        self.current_user_id = None
        self.users_data = {}
        self.conversation_history = {}
        
        # Inicializar sistema de identificação por voz
        self.voice_id = VoiceIdentification() if VOICE_ID_AVAILABLE else None
        
        # Inicializar analisador contextual
        self.contextual_analyzer = ContextualAnalyzer() if CONTEXTUAL_ANALYZER_AVAILABLE else None
        
        # Carregar dados existentes
        self._load_users_data()
        
        # Métodos de identificação disponíveis
        self.identification_methods = {
            'voice_pattern': VOICE_ID_AVAILABLE,  # Ativado se bibliotecas estão disponíveis
            'text_pattern': True,                  # Análise de padrões de texto
            'manual_switch': True,                 # Mudança manual de utilizador
            'contextual': True                     # Análise contextual
        }
    
    def _load_users_data(self) -> None:
        """Carrega dados de utilizadores existentes."""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users_data = data.get('users', {})
                    self.conversation_history = data.get('conversation_history', {})
                    logger.info(f"Dados de {len(self.users_data)} utilizadores carregados")
            else:
                self.users_data = {}
                self.conversation_history = {}
                logger.info("Nenhum dado de utilizadores encontrado - iniciando sistema novo")
        except Exception as e:
            logger.error(f"Erro ao carregar dados de utilizadores: {e}")
            self.users_data = {}
            self.conversation_history = {}
    
    def _save_users_data(self) -> None:
        """Guarda dados de utilizadores."""
        try:
            data = {
                'users': self.users_data,
                'conversation_history': self.conversation_history,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Dados de {len(self.users_data)} utilizadores guardados")
        except Exception as e:
            logger.error(f"Erro ao guardar dados de utilizadores: {e}")
    
    def identify_user(self, input_text: str, audio_data: bytes = None, context: str = "") -> Tuple[str, float]:
        """
        Identifica o utilizador baseado em vários fatores.
        
        Args:
            input_text: Texto da entrada
            audio_data: Dados de áudio (para reconhecimento de voz)
            context: Contexto adicional
            
        Returns:
            Tuple[user_id, confidence_score]
        """
        identification_scores = {}
        
        # 1. ANÁLISE DE PADRÕES DE TEXTO
        text_scores = self._analyze_text_patterns(input_text)
        for user_id, score in text_scores.items():
            identification_scores[user_id] = identification_scores.get(user_id, 0) + score * 0.4
        
        # 2. ANÁLISE CONTEXTUAL (quem foi mencionado, etc.)
        context_scores = self._analyze_contextual_clues(input_text, context)
        for user_id, score in context_scores.items():
            identification_scores[user_id] = identification_scores.get(user_id, 0) + score * 0.3
        
        # 3. ANÁLISE DE AUTO-IDENTIFICAÇÃO (frases como "eu sou...")
        self_id_scores = self._analyze_self_identification(input_text)
        for user_id, score in self_id_scores.items():
            identification_scores[user_id] = identification_scores.get(user_id, 0) + score * 0.8
        
        # 4. CONTINUIDADE DA CONVERSA (mesmo utilizador que falou recentemente)
        if self.current_user_id:
            identification_scores[self.current_user_id] = identification_scores.get(self.current_user_id, 0) + 0.2
        
        # 5. ANÁLISE DE VOZ (se disponível)
        if audio_data and self.identification_methods['voice_pattern'] and self.voice_id:
            voice_user_id, voice_confidence = self.voice_id.identify_user_by_voice(audio_data)
            if voice_user_id and voice_confidence > 0.3:
                identification_scores[voice_user_id] = identification_scores.get(voice_user_id, 0) + voice_confidence * 0.8
        
        # 6. ANÁLISE CONTEXTUAL AVANÇADA (se disponível)
        if self.contextual_analyzer and CONTEXTUAL_ANALYZER_AVAILABLE:
            contextual_scores = self.contextual_analyzer.analyze_user_context(
                input_text, 
                list(self.users_data.keys())
            )
            
            for user_id, score in contextual_scores.items():
                if user_id in self.users_data:
                    identification_scores[user_id] = identification_scores.get(user_id, 0) + score * 0.6
        
        # Determinar o utilizador com maior pontuação
        if identification_scores:
            best_user = max(identification_scores.items(), key=lambda x: x[1])
            return best_user
        else:
            # Se não conseguiu identificar, criar novo utilizador ou usar "unknown"
            return self._handle_unknown_user(input_text), 0.1
    
    def _analyze_text_patterns(self, text: str) -> Dict[str, float]:
        """Analisa padrões de texto para identificar utilizador."""
        scores = {}
        
        for user_id, user_data in self.users_data.items():
            score = 0.0
            
            # Analisar vocabulário comum
            user_vocab = set(user_data.get('common_words', []))
            text_words = set(text.lower().split())
            
            if user_vocab and text_words:
                vocab_overlap = len(user_vocab.intersection(text_words)) / len(user_vocab.union(text_words))
                score += vocab_overlap * 0.3
            
            # Analisar frases típicas
            user_phrases = user_data.get('typical_phrases', [])
            for phrase in user_phrases:
                if phrase.lower() in text.lower():
                    score += 0.2
            
            # Analisar estilo de pontuação
            user_punctuation_style = user_data.get('punctuation_style', {})
            current_style = self._analyze_punctuation_style(text)
            
            if user_punctuation_style:
                style_similarity = self._calculate_style_similarity(user_punctuation_style, current_style)
                score += style_similarity * 0.1
            
            if score > 0:
                scores[user_id] = score
        
        return scores
    
    def _analyze_contextual_clues(self, text: str, context: str) -> Dict[str, float]:
        """Analisa pistas contextuais para identificar utilizador."""
        scores = {}
        text_lower = text.lower()
        
        # Procurar por referências a informações pessoais específicas
        for user_id, user_data in self.users_data.items():
            score = 0.0
            
            # Referências a família/relacionamentos específicos desta pessoa
            user_relationships = user_data.get('known_relationships', [])
            for relationship in user_relationships:
                if relationship.lower() in text_lower:
                    score += 0.3
            
            # Referências a profissão
            user_profession = user_data.get('profession', '')
            if user_profession and user_profession.lower() in text_lower:
                score += 0.2
            
            # Referências a localização
            user_location = user_data.get('location', '')
            if user_location and user_location.lower() in text_lower:
                score += 0.2
            
            # Referências a gostos/interesses específicos
            user_interests = user_data.get('interests', [])
            for interest in user_interests:
                if interest.lower() in text_lower:
                    score += 0.1
            
            if score > 0:
                scores[user_id] = score
        
        return scores
    
    def _analyze_self_identification(self, text: str) -> Dict[str, float]:
        """Analisa frases de auto-identificação."""
        scores = {}
        
        # Padrões de auto-identificação
        self_id_patterns = [
            r'(?:eu sou|chamo-me|meu nome é) ([A-Z][a-záàâãéèêíïóôõöúçñ]+)',
            r'sou (?:o|a) ([A-Z][a-záàâãéèêíïóôõöúçñ]+)',
            r'(?:aqui é|fala) (?:o|a) ([A-Z][a-záàâãéèêíïóôõöúçñ]+)',
        ]
        
        for pattern in self_id_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                identified_name = match.group(1).title()
                
                # Procurar utilizador existente com esse nome
                for user_id, user_data in self.users_data.items():
                    if user_data.get('name', '').lower() == identified_name.lower():
                        scores[user_id] = 1.0
                        break
                else:
                    # Nome não encontrado - pode ser novo utilizador
                    new_user_id = self._create_new_user({'name': identified_name})
                    scores[new_user_id] = 1.0
        
        return scores
    
    def _analyze_punctuation_style(self, text: str) -> Dict[str, float]:
        """Analisa estilo de pontuação do texto."""
        style = {}
        
        total_chars = len(text)
        if total_chars == 0:
            return style
        
        # Contar diferentes tipos de pontuação
        punctuation_counts = {
            'periods': text.count('.'),
            'commas': text.count(','),
            'exclamations': text.count('!'),
            'questions': text.count('?'),
            'ellipsis': text.count('...'),
        }
        
        # Calcular frequências relativas
        for punct_type, count in punctuation_counts.items():
            style[punct_type] = count / total_chars if total_chars > 0 else 0
        
        # Análise de maiúsculas/minúsculas
        style['uppercase_ratio'] = sum(1 for c in text if c.isupper()) / total_chars
        style['avg_word_length'] = sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0
        
        return style
    
    def _calculate_style_similarity(self, style1: Dict, style2: Dict) -> float:
        """Calcula similaridade entre dois estilos."""
        if not style1 or not style2:
            return 0.0
        
        # Usar distância euclidiana normalizada
        differences = []
        for key in set(style1.keys()).union(set(style2.keys())):
            val1 = style1.get(key, 0)
            val2 = style2.get(key, 0)
            differences.append((val1 - val2) ** 2)
        
        if not differences:
            return 0.0
        
        distance = sum(differences) ** 0.5
        # Converter distância em similaridade (0-1)
        similarity = max(0, 1 - distance)
        return similarity
    
    def _handle_unknown_user(self, input_text: str) -> str:
        """Lida com utilizador desconhecido."""
        # Tentar extrair nome do texto
        name_patterns = [
            r'(?:eu sou|chamo-me|meu nome é) ([A-Z][a-záàâãéèêíïóôõöúçñ]+)',
            r'sou (?:o|a) ([A-Z][a-záàâãéèêíïóôõöúçñ]+)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, input_text, re.IGNORECASE)
            if match:
                name = match.group(1).title()
                return self._create_new_user({'name': name})
        
        # Se não encontrou nome, criar utilizador genérico
        user_count = len(self.users_data) + 1
        return self._create_new_user({'name': f'Utilizador{user_count}'})
    
    def _create_new_user(self, initial_data: Dict) -> str:
        """Cria novo utilizador."""
        user_id = hashlib.md5(f"{initial_data.get('name', '')}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        self.users_data[user_id] = {
            'name': initial_data.get('name', f'Utilizador{len(self.users_data) + 1}'),
            'created_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'conversation_count': 0,
            'common_words': [],
            'typical_phrases': [],
            'punctuation_style': {},
            'known_relationships': [],
            'interests': [],
            'profession': '',
            'location': '',
            **initial_data
        }
        
        self.conversation_history[user_id] = []
        self._save_users_data()
        
        logger.info(f"Novo utilizador criado: {self.users_data[user_id]['name']} (ID: {user_id})")
        return user_id
    
    def switch_user(self, user_identifier: str) -> bool:
        """
        Muda manualmente para outro utilizador.
        
        Args:
            user_identifier: Nome ou ID do utilizador
            
        Returns:
            True se mudança foi bem-sucedida
        """
        # Procurar por ID
        if user_identifier in self.users_data:
            self.current_user_id = user_identifier
            logger.info(f"Mudança manual para utilizador: {self.users_data[user_identifier]['name']}")
            return True
        
        # Procurar por nome
        for user_id, user_data in self.users_data.items():
            if user_data['name'].lower() == user_identifier.lower():
                self.current_user_id = user_id
                logger.info(f"Mudança manual para utilizador: {user_data['name']}")
                return True
        
        logger.warning(f"Utilizador não encontrado: {user_identifier}")
        return False
    
    def process_input(self, input_text: str, audio_data: bytes = None) -> Dict[str, Any]:
        """
        Processa entrada de utilizador com identificação automática.
        
        Args:
            input_text: Texto da entrada
            audio_data: Dados de áudio opcionais
            
        Returns:
            Dict com informações sobre o utilizador identificado e contexto
        """
        # Identificar utilizador
        user_id, confidence = self.identify_user(input_text, audio_data)
        
        # Atualizar utilizador atual se confiança for suficiente
        if confidence > 0.3:  # Limiar de confiança
            self.current_user_id = user_id
        
        # Atualizar dados do utilizador
        self._update_user_data(user_id, input_text)
        
        # Adicionar à história da conversa
        self._add_to_conversation_history(user_id, input_text)
        
        # Gerar contexto personalizado
        context = self._generate_user_context(user_id)
        
        return {
            'user_id': user_id,
            'user_name': self.users_data[user_id]['name'],
            'confidence': confidence,
            'context': context,
            'is_user_switch': user_id != self.current_user_id,
            'user_data': self.users_data[user_id].copy()
        }
    
    def _update_user_data(self, user_id: str, input_text: str) -> None:
        """Atualiza dados do utilizador baseado na entrada."""
        if user_id not in self.users_data:
            return
        
        user_data = self.users_data[user_id]
        
        # Atualizar timestamp
        user_data['last_seen'] = datetime.now().isoformat()
        user_data['conversation_count'] = user_data.get('conversation_count', 0) + 1
        
        # Atualizar palavras comuns
        words = set(input_text.lower().split())
        common_words = set(user_data.get('common_words', []))
        common_words.update(words)
        user_data['common_words'] = list(common_words)[:100]  # Limitar a 100 palavras
        
        # Atualizar estilo de pontuação
        current_style = self._analyze_punctuation_style(input_text)
        if current_style:
            user_data['punctuation_style'] = current_style
        
        # Detectar e atualizar informações pessoais
        self._extract_personal_info(user_id, input_text)
        
        # Atualizar analisador contextual com novos dados
        if self.contextual_analyzer and CONTEXTUAL_ANALYZER_AVAILABLE:
            self.contextual_analyzer.update_user_behavior(user_id, input_text, {
                'name': user_data.get('name', ''),
                'profession': user_data.get('profession', ''),
                'location': user_data.get('location', ''),
                'interests': user_data.get('interests', []),
                'relationships': user_data.get('known_relationships', [])
            })
        
        self._save_users_data()
    
    def _extract_personal_info(self, user_id: str, text: str) -> None:
        """Extrai informações pessoais do texto."""
        user_data = self.users_data[user_id]
        
        # Extrair profissão
        profession_patterns = [
            r'trabalho como ([a-záàâãéèêíïóôõöúçñ\s]+)',
            r'sou ([a-záàâãéèêíïóôõöúçñ]+) de profissão',
        ]
        
        for pattern in profession_patterns:
            match = re.search(pattern, text.lower())
            if match:
                user_data['profession'] = match.group(1).strip()
                break
        
        # Extrair localização
        location_patterns = [
            r'vivo em ([A-Z][a-záàâãéèêíïóôõöúçñ\s]+)',
            r'moro em ([A-Z][a-záàâãéèêíïóôõöúçñ\s]+)',
            r'sou de ([A-Z][a-záàâãéèêíïóôõöúçñ\s]+)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                user_data['location'] = match.group(1).strip()
                break
        
        # Extrair relacionamentos mencionados
        relationship_patterns = [
            r'(?:minha|meu) ([a-záàâãéèêíïóôõöúçñ]+)',
            r'(?:a|o) minha? ([a-záàâãéèêíïóôõöúçñ]+)',
        ]
        
        relationships = set(user_data.get('known_relationships', []))
        for pattern in relationship_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                relationships.add(match.group(1))
        
        user_data['known_relationships'] = list(relationships)
    
    def _add_to_conversation_history(self, user_id: str, input_text: str) -> None:
        """Adiciona entrada ao histórico da conversa."""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            'timestamp': datetime.now().isoformat(),
            'text': input_text[:200],  # Limitar tamanho
        })
        
        # Manter apenas as últimas 50 entradas por utilizador
        self.conversation_history[user_id] = self.conversation_history[user_id][-50:]
    
    def _generate_user_context(self, user_id: str) -> str:
        """Gera contexto personalizado para o utilizador."""
        if user_id not in self.users_data:
            return ""
        
        user_data = self.users_data[user_id]
        context_parts = []
        
        # Informações básicas
        context_parts.append(f"UTILIZADOR ATUAL: {user_data['name']}")
        
        if user_data.get('profession'):
            context_parts.append(f"Profissão: {user_data['profession']}")
        
        if user_data.get('location'):
            context_parts.append(f"Localização: {user_data['location']}")
        
        # Estatísticas de conversa
        conv_count = user_data.get('conversation_count', 0)
        if conv_count > 0:
            context_parts.append(f"Conversas anteriores: {conv_count}")
        
        # Última interação
        last_seen = user_data.get('last_seen')
        if last_seen:
            context_parts.append(f"Última interação: {last_seen[:10]}")
        
        # Relacionamentos conhecidos
        relationships = user_data.get('known_relationships', [])
        if relationships:
            context_parts.append(f"Relacionamentos mencionados: {', '.join(relationships[:5])}")
        
        return "\n".join(context_parts) + "\n\nPersonalize a resposta para este utilizador específico."
    
    def get_all_users(self) -> List[Dict]:
        """Retorna lista de todos os utilizadores."""
        users_list = []
        for user_id, user_data in self.users_data.items():
            user_info = user_data.copy()
            user_info['user_id'] = user_id
            user_info['is_current'] = user_id == self.current_user_id
            users_list.append(user_info)
        
        # Ordenar por última interação
        users_list.sort(key=lambda x: x.get('last_seen', ''), reverse=True)
        return users_list
    
    def get_current_user(self) -> Optional[Dict]:
        """Retorna dados do utilizador atual."""
        if self.current_user_id and self.current_user_id in self.users_data:
            user_data = self.users_data[self.current_user_id].copy()
            user_data['user_id'] = self.current_user_id
            return user_data
        return None
    
    def delete_user(self, user_id: str) -> bool:
        """Remove utilizador do sistema."""
        if user_id in self.users_data:
            user_name = self.users_data[user_id]['name']
            del self.users_data[user_id]
            
            if user_id in self.conversation_history:
                del self.conversation_history[user_id]
            
            # Remover modelo de voz se existir
            if self.voice_id:
                self.voice_id.delete_user_voice_model(user_id)
            
            if self.current_user_id == user_id:
                self.current_user_id = None
            
            self._save_users_data()
            logger.info(f"Utilizador removido: {user_name} (ID: {user_id})")
            return True
        
        return False
    
    def train_user_voice(self, user_id: str, audio_samples: List[bytes]) -> bool:
        """Treina modelo de voz para utilizador."""
        if not self.voice_id:
            logger.warning("Sistema de identificação por voz não disponível")
            return False
        
        if user_id not in self.users_data:
            logger.error(f"Utilizador {user_id} não existe")
            return False
        
        success = self.voice_id.train_user_voice(user_id, audio_samples)
        if success:
            # Atualizar dados do utilizador
            self.users_data[user_id]['voice_trained'] = True
            self.users_data[user_id]['voice_samples_count'] = len(audio_samples)
            self.users_data[user_id]['voice_trained_at'] = datetime.now().isoformat()
            self._save_users_data()
            
        return success
    
    def add_voice_sample(self, user_id: str, audio_data: bytes) -> bool:
        """Adiciona amostra de voz para utilizador."""
        if not self.voice_id:
            return False
        
        success = self.voice_id.add_voice_sample(user_id, audio_data)
        if success and user_id in self.users_data:
            # Incrementar contador de amostras
            current_count = self.users_data[user_id].get('voice_samples_count', 0)
            self.users_data[user_id]['voice_samples_count'] = current_count + 1
            self.users_data[user_id]['voice_last_sample'] = datetime.now().isoformat()
            self._save_users_data()
        
        return success
    
    def get_voice_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos modelos de voz."""
        if not self.voice_id:
            return {'voice_available': False}
        
        voice_stats = self.voice_id.get_voice_stats()
        voice_stats['voice_available'] = True
        
        # Adicionar informações dos utilizadores
        for user_id, user_data in self.users_data.items():
            if user_id in voice_stats.get('users', {}):
                voice_stats['users'][user_id]['user_name'] = user_data.get('name', 'Unknown')
                voice_stats['users'][user_id]['voice_trained'] = user_data.get('voice_trained', False)
        
        return voice_stats
    
    def get_contextual_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do analisador contextual."""
        if not self.contextual_analyzer:
            return {'contextual_available': False}
        
        contextual_stats = self.contextual_analyzer.get_behavioral_stats()
        contextual_stats['contextual_available'] = True
        
        # Adicionar informações dos utilizadores
        for user_id, user_data in self.users_data.items():
            if user_id in contextual_stats.get('users', {}):
                contextual_stats['users'][user_id]['user_name'] = user_data.get('name', 'Unknown')
        
        return contextual_stats
    
    def analyze_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analisa padrões comportamentais de um utilizador específico."""
        if not self.contextual_analyzer or user_id not in self.users_data:
            return {}
        
        # Obter histórico de conversa do utilizador
        user_history = self.conversation_history.get(user_id, [])
        
        # Extrair textos do histórico
        texts = [entry['text'] for entry in user_history[-20:]]  # Últimas 20 mensagens
        
        if not texts:
            return {}
        
        # Analisar padrões
        combined_text = ' '.join(texts)
        patterns = self.contextual_analyzer.extract_behavioral_patterns(combined_text)
        
        # Adicionar informações do utilizador
        user_data = self.users_data[user_id]
        patterns['user_info'] = {
            'name': user_data.get('name', ''),
            'conversation_count': user_data.get('conversation_count', 0),
            'last_seen': user_data.get('last_seen', ''),
            'profession': user_data.get('profession', ''),
            'location': user_data.get('location', '')
        }
        
        return patterns
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Retorna todas as estatísticas disponíveis do sistema."""
        stats = {
            'total_users': len(self.users_data),
            'current_user': self.get_current_user(),
            'identification_methods': self.identification_methods.copy(),
            'users': self.get_all_users()
        }
        
        # Adicionar estatísticas de voz
        if self.voice_id:
            stats['voice'] = self.get_voice_stats()
        
        # Adicionar estatísticas contextuais
        if self.contextual_analyzer:
            stats['contextual'] = self.get_contextual_stats()
        
        return stats
