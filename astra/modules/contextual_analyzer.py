#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal
Sistema de Análise Contextual Avançada

Sistema inteligente para análise contextual avançada que melhora a identificação
de utilizadores através de padrões comportamentais, temporais e linguísticos.
"""

import json
import logging
import re
from datetime import datetime, time, timedelta
from typing import Dict, Optional, List, Any, Tuple, Set
from pathlib import Path
import calendar

logger = logging.getLogger(__name__)

class ContextualAnalyzer:
    """
    Analisador contextual avançado.
    Analisa padrões comportamentais, temporais e linguísticos para identificação de utilizadores.
    """
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/contextual_analysis")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Padrões contextuais por utilizador
        self.user_patterns = {}
        
        # Base de conhecimento contextual
        self.context_knowledge = {
            'time_patterns': {},      # Padrões de horário
            'day_patterns': {},       # Padrões de dia da semana
            'topic_preferences': {},  # Tópicos favoritos por utilizador
            'language_patterns': {},  # Padrões linguísticos
            'emotional_patterns': {}, # Padrões emocionais
            'location_references': {} # Referências de localização
        }
        
        # Carregar dados existentes
        self._load_contextual_data()
        
        # Inicializar detectores especializados
        self._init_detectors()
    
    def _init_detectors(self):
        """Inicializa detectores especializados."""
        
        # Padrões de tópicos
        self.topic_patterns = {
            'trabalho': [
                r'\b(?:trabalho|job|emprego|escritório|reunião|projeto|cliente|chefe|colega|empresa)\b',
                r'\b(?:trabalhar|estudar|programar|desenvolver|gestão|marketing|vendas)\b'
            ],
            'família': [
                r'\b(?:família|filhos|pais|mãe|pai|esposa|marido|irmão|irmã|avô|avó)\b',
                r'\b(?:casa|família|crianças|bebé|casamento|aniversário|natal|férias)\b'
            ],
            'entretenimento': [
                r'\b(?:filme|série|música|jogo|livro|cinema|televisão|netflix|youtube)\b',
                r'\b(?:diversão|relaxar|férias|fim de semana|festa|praia|viagem)\b'
            ],
            'desporto': [
                r'\b(?:futebol|ténis|corrida|ginásio|exercício|treino|jogo|equipa)\b',
                r'\b(?:benfica|porto|sporting|champions|liga|mundial|euro)\b'
            ],
            'saúde': [
                r'\b(?:médico|hospital|clínica|medicamento|tratamento|consulta|exame)\b',
                r'\b(?:doente|dor|febre|gripe|covid|vacina|saúde|bem-estar)\b'
            ],
            'tecnologia': [
                r'\b(?:computador|software|app|aplicação|internet|smartphone|tablet)\b',
                r'\b(?:programar|código|bug|update|download|cloud|ai|inteligência)\b'
            ]
        }
        
        # Padrões emocionais
        self.emotion_patterns = {
            'alegria': [
                r'\b(?:feliz|alegre|contente|bem|ótimo|excelente|fantástico|maravilhoso)\b',
                r'[!]{2,}|😊|😄|😃|🎉|❤️'
            ],
            'tristeza': [
                r'\b(?:triste|deprimido|mal|péssimo|horrível|terrível|chateado)\b',
                r'😢|😭|💔|😞'
            ],
            'raiva': [
                r'\b(?:irritado|zangado|furioso|indignado|revoltado)\b',
                r'😠|😡|🤬'
            ],
            'stress': [
                r'\b(?:stressado|ansioso|nervoso|preocupado|cansado|exausto)\b',
                r'😰|😨|😩'
            ],
            'surpresa': [
                r'\b(?:surpreendido|chocado|impressionado|uau|nossa)\b',
                r'😱|😲|🤯'
            ]
        }
        
        # Padrões de formalidade
        self.formality_patterns = {
            'formal': [
                r'\b(?:senhor|senhora|doutor|doutora|professor|professora)\b',
                r'\b(?:por favor|se faz favor|agradeço|cordialmente|atenciosamente)\b'
            ],
            'informal': [
                r'\b(?:olá|oi|hey|malta|pessoal|galera)\b',
                r'\b(?:fixe|bacana|brutal|tipo|assim|pronto)\b'
            ],
            'muito_informal': [
                r'\b(?:yo|sup|wtf|lol|omg|fds)\b',
                r'[!]{3,}|\?\?\?+|\.\.\.{3,}'
            ]
        }
    
    def analyze_context(self, text: str, user_id: str = None, timestamp: datetime = None) -> Dict[str, Any]:
        """
        Analisa contexto completo de um texto.
        
        Args:
            text: Texto a analisar
            user_id: ID do utilizador (opcional)
            timestamp: Timestamp da mensagem (opcional)
            
        Returns:
            Dicionário com análise contextual completa
        """
        timestamp = timestamp or datetime.now()
        
        analysis = {
            'timestamp': timestamp.isoformat(),
            'text_length': len(text),
            'word_count': len(text.split()),
            
            # Análises básicas
            'topics': self._detect_topics(text),
            'emotions': self._detect_emotions(text),
            'formality': self._detect_formality(text),
            'language_features': self._analyze_language_features(text),
            
            # Análises temporais
            'time_context': self._analyze_time_context(timestamp),
            
            # Análises comportamentais
            'behavioral_indicators': self._detect_behavioral_patterns(text),
            
            # Referências pessoais
            'personal_references': self._detect_personal_references(text),
            
            # Localização
            'location_references': self._detect_location_references(text)
        }
        
        # Atualizar padrões do utilizador se fornecido
        if user_id:
            self._update_user_patterns(user_id, analysis)
        
        return analysis
    
    def _detect_topics(self, text: str) -> Dict[str, float]:
        """Detecta tópicos principais no texto."""
        text_lower = text.lower()
        topic_scores = {}
        
        for topic, patterns in self.topic_patterns.items():
            score = 0.0
            matches = 0
            
            for pattern in patterns:
                found_matches = re.findall(pattern, text_lower)
                matches += len(found_matches)
                score += len(found_matches) * 0.5
            
            if score > 0:
                # Normalizar pela quantidade de palavras
                topic_scores[topic] = min(1.0, score / max(1, len(text.split()) * 0.1))
        
        return topic_scores
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detecta emoções no texto."""
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0.0
            
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches) * 0.3
            
            if score > 0:
                emotion_scores[emotion] = min(1.0, score)
        
        return emotion_scores
    
    def _detect_formality(self, text: str) -> Dict[str, float]:
        """Detecta nível de formalidade."""
        text_lower = text.lower()
        formality_scores = {}
        
        for level, patterns in self.formality_patterns.items():
            score = 0.0
            
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches) * 0.4
            
            if score > 0:
                formality_scores[level] = min(1.0, score)
        
        return formality_scores
    
    def _analyze_language_features(self, text: str) -> Dict[str, Any]:
        """Analisa características linguísticas."""
        words = text.split()
        
        features = {
            'avg_word_length': sum(len(word) for word in words) / max(1, len(words)),
            'sentence_count': len(re.findall(r'[.!?]+', text)),
            'question_count': text.count('?'),
            'exclamation_count': text.count('!'),
            'comma_count': text.count(','),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / max(1, len(text)),
            'digit_count': sum(1 for c in text if c.isdigit()),
            'emoji_count': len(re.findall(r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F1E0-\U0001F1FF]', text))
        }
        
        return features
    
    def _analyze_time_context(self, timestamp: datetime) -> Dict[str, Any]:
        """Analisa contexto temporal."""
        return {
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'day_name': calendar.day_name[timestamp.weekday()],
            'is_weekend': timestamp.weekday() >= 5,
            'is_morning': 6 <= timestamp.hour < 12,
            'is_afternoon': 12 <= timestamp.hour < 18,
            'is_evening': 18 <= timestamp.hour < 22,
            'is_night': timestamp.hour >= 22 or timestamp.hour < 6,
            'month': timestamp.month,
            'season': self._get_season(timestamp.month)
        }
    
    def _get_season(self, month: int) -> str:
        """Determina a estação do ano."""
        if month in [12, 1, 2]:
            return 'inverno'
        elif month in [3, 4, 5]:
            return 'primavera'
        elif month in [6, 7, 8]:
            return 'verão'
        else:
            return 'outono'
    
    def _detect_behavioral_patterns(self, text: str) -> Dict[str, Any]:
        """Detecta padrões comportamentais."""
        patterns = {
            'asks_questions': '?' in text,
            'uses_greetings': bool(re.search(r'\b(?:olá|oi|bom dia|boa tarde|boa noite|hey)\b', text.lower())),
            'uses_farewells': bool(re.search(r'\b(?:tchau|adeus|até logo|bye|see you)\b', text.lower())),
            'uses_politeness': bool(re.search(r'\b(?:por favor|obrigado|obrigada|desculpa|com licença)\b', text.lower())),
            'uses_slang': bool(re.search(r'\b(?:fixe|bacana|brutal|bestial|porreiro)\b', text.lower())),
            'makes_jokes': bool(re.search(r'\b(?:ahah|hehe|lol|piada|engraçado|hilário)\b', text.lower())),
            'expresses_urgency': bool(re.search(r'\b(?:urgente|rápido|depressa|já|agora)\b', text.lower())),
            'uses_repetition': len(re.findall(r'\b(\w+)\s+\1\b', text.lower())) > 0
        }
        
        return patterns
    
    def _detect_personal_references(self, text: str) -> List[str]:
        """Detecta referências pessoais."""
        references = []
        text_lower = text.lower()
        
        # Família
        family_patterns = [
            r'\b(?:minha?|meu) (?:mãe|pai|irmã|irmão|filho|filha|esposa|marido|namorada|namorado)\b',
            r'\b(?:filhos|pais|família|esposa|marido)\b'
        ]
        
        for pattern in family_patterns:
            matches = re.findall(pattern, text_lower)
            references.extend(matches)
        
        # Trabalho
        work_patterns = [
            r'\b(?:minha?|meu) (?:trabalho|emprego|empresa|chefe|colega)\b',
            r'\b(?:trabalho|emprego|empresa)\b'
        ]
        
        for pattern in work_patterns:
            matches = re.findall(pattern, text_lower)
            references.extend(matches)
        
        return list(set(references))
    
    def _detect_location_references(self, text: str) -> List[str]:
        """Detecta referências de localização."""
        locations = []
        
        # Cidades portuguesas comuns
        portuguese_cities = [
            'lisboa', 'porto', 'coimbra', 'braga', 'aveiro', 'viseu', 'faro', 'setúbal',
            'évora', 'funchal', 'angra', 'leiria', 'santarém', 'beja', 'castelo branco',
            'guarda', 'portalegre', 'vila real', 'bragança', 'viana do castelo'
        ]
        
        text_lower = text.lower()
        
        for city in portuguese_cities:
            if city in text_lower:
                locations.append(city.title())
        
        # Padrões de localização
        location_patterns = [
            r'\b(?:em|de|para|vou a|estou em|vivo em|moro em) ([A-Z][a-záàâãéèêíïóôõöúçñ]+)\b'
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            locations.extend(matches)
        
        return list(set(locations))
    
    def _update_user_patterns(self, user_id: str, analysis: Dict[str, Any]) -> None:
        """Atualiza padrões contextuais do utilizador."""
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = {
                'topic_frequencies': {},
                'emotion_frequencies': {},
                'formality_levels': {},
                'time_preferences': [],
                'behavioral_traits': {},
                'language_features': [],
                'total_messages': 0
            }
        
        patterns = self.user_patterns[user_id]
        patterns['total_messages'] += 1
        
        # Atualizar frequências de tópicos
        for topic, score in analysis['topics'].items():
            if topic not in patterns['topic_frequencies']:
                patterns['topic_frequencies'][topic] = []
            patterns['topic_frequencies'][topic].append(score)
        
        # Atualizar emoções
        for emotion, score in analysis['emotions'].items():
            if emotion not in patterns['emotion_frequencies']:
                patterns['emotion_frequencies'][emotion] = []
            patterns['emotion_frequencies'][emotion].append(score)
        
        # Atualizar formalidade
        for level, score in analysis['formality'].items():
            if level not in patterns['formality_levels']:
                patterns['formality_levels'][level] = []
            patterns['formality_levels'][level].append(score)
        
        # Atualizar preferências temporais
        patterns['time_preferences'].append(analysis['time_context'])
        
        # Manter apenas os últimos 100 registos
        for key in ['time_preferences']:
            if len(patterns[key]) > 100:
                patterns[key] = patterns[key][-100:]
        
        # Atualizar características linguísticas
        patterns['language_features'].append(analysis['language_features'])
        if len(patterns['language_features']) > 50:
            patterns['language_features'] = patterns['language_features'][-50:]
        
        # Guardar dados
        self._save_contextual_data()
    
    def get_user_context_score(self, user_id: str, current_analysis: Dict[str, Any]) -> float:
        """
        Calcula pontuação de contexto para um utilizador.
        
        Args:
            user_id: ID do utilizador
            current_analysis: Análise do texto atual
            
        Returns:
            Pontuação de contexto (0.0 a 1.0)
        """
        if user_id not in self.user_patterns:
            return 0.0
        
        patterns = self.user_patterns[user_id]
        total_score = 0.0
        weight_sum = 0.0
        
        # Pontuação de tópicos
        topic_score = self._calculate_topic_similarity(patterns['topic_frequencies'], current_analysis['topics'])
        total_score += topic_score * 0.3
        weight_sum += 0.3
        
        # Pontuação emocional
        emotion_score = self._calculate_emotion_similarity(patterns['emotion_frequencies'], current_analysis['emotions'])
        total_score += emotion_score * 0.2
        weight_sum += 0.2
        
        # Pontuação temporal
        time_score = self._calculate_time_similarity(patterns['time_preferences'], current_analysis['time_context'])
        total_score += time_score * 0.2
        weight_sum += 0.2
        
        # Pontuação linguística
        lang_score = self._calculate_language_similarity(patterns['language_features'], current_analysis['language_features'])
        total_score += lang_score * 0.3
        weight_sum += 0.3
        
        return total_score / weight_sum if weight_sum > 0 else 0.0
    
    def _calculate_topic_similarity(self, user_topics: Dict, current_topics: Dict) -> float:
        """Calcula similaridade de tópicos."""
        if not user_topics or not current_topics:
            return 0.0
        
        similarity = 0.0
        count = 0
        
        for topic, current_score in current_topics.items():
            if topic in user_topics:
                avg_user_score = sum(user_topics[topic]) / len(user_topics[topic])
                similarity += min(current_score, avg_user_score)
                count += 1
        
        return similarity / max(1, count)
    
    def _calculate_emotion_similarity(self, user_emotions: Dict, current_emotions: Dict) -> float:
        """Calcula similaridade emocional."""
        if not user_emotions or not current_emotions:
            return 0.0
        
        similarity = 0.0
        count = 0
        
        for emotion, current_score in current_emotions.items():
            if emotion in user_emotions:
                avg_user_score = sum(user_emotions[emotion]) / len(user_emotions[emotion])
                similarity += min(current_score, avg_user_score)
                count += 1
        
        return similarity / max(1, count)
    
    def _calculate_time_similarity(self, user_time_prefs: List, current_time: Dict) -> float:
        """Calcula similaridade temporal."""
        if not user_time_prefs:
            return 0.0
        
        # Calcular frequências de horário do utilizador
        hour_freq = {}
        day_freq = {}
        
        for time_data in user_time_prefs:
            hour = time_data['hour']
            day = time_data['day_of_week']
            
            hour_freq[hour] = hour_freq.get(hour, 0) + 1
            day_freq[day] = day_freq.get(day, 0) + 1
        
        # Calcular similaridade
        similarity = 0.0
        
        # Similaridade de horário
        current_hour = current_time['hour']
        hour_score = hour_freq.get(current_hour, 0) / len(user_time_prefs)
        similarity += hour_score * 0.6
        
        # Similaridade de dia da semana
        current_day = current_time['day_of_week']
        day_score = day_freq.get(current_day, 0) / len(user_time_prefs)
        similarity += day_score * 0.4
        
        return similarity
    
    def _calculate_language_similarity(self, user_features: List, current_features: Dict) -> float:
        """Calcula similaridade linguística."""
        if not user_features:
            return 0.0
        
        # Calcular médias das características do utilizador
        avg_features = {}
        for feature_name in current_features.keys():
            values = [f.get(feature_name, 0) for f in user_features if feature_name in f]
            if values:
                avg_features[feature_name] = sum(values) / len(values)
        
        # Calcular similaridade
        similarity = 0.0
        count = 0
        
        for feature_name, current_value in current_features.items():
            if feature_name in avg_features:
                avg_value = avg_features[feature_name]
                if avg_value > 0:
                    # Usar similaridade relativa
                    diff = abs(current_value - avg_value) / max(avg_value, current_value)
                    similarity += max(0, 1 - diff)
                    count += 1
        
        return similarity / max(1, count)
    
    def _save_contextual_data(self) -> None:
        """Guarda dados contextuais no disco."""
        try:
            data_file = self.data_dir / "contextual_patterns.json"
            
            # Converter dados para formato serializável
            serializable_data = {}
            for user_id, patterns in self.user_patterns.items():
                serializable_data[user_id] = {
                    'topic_frequencies': patterns['topic_frequencies'],
                    'emotion_frequencies': patterns['emotion_frequencies'],
                    'formality_levels': patterns['formality_levels'],
                    'time_preferences': patterns['time_preferences'][-50:],  # Manter apenas os últimos 50
                    'language_features': patterns['language_features'][-50:],  # Manter apenas os últimos 50
                    'total_messages': patterns['total_messages']
                }
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erro ao guardar dados contextuais: {e}")
    
    def _load_contextual_data(self) -> None:
        """Carrega dados contextuais do disco."""
        try:
            data_file = self.data_dir / "contextual_patterns.json"
            
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    self.user_patterns = json.load(f)
                    
                logger.info(f"Dados contextuais carregados para {len(self.user_patterns)} utilizadores")
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados contextuais: {e}")
    
    def get_contextual_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas contextuais."""
        stats = {
            'total_users': len(self.user_patterns),
            'users': {}
        }
        
        for user_id, patterns in self.user_patterns.items():
            user_stats = {
                'total_messages': patterns['total_messages'],
                'top_topics': {},
                'dominant_emotions': {},
                'formality_preference': {},
                'most_active_hours': []
            }
            
            # Top tópicos
            for topic, scores in patterns['topic_frequencies'].items():
                if scores:
                    user_stats['top_topics'][topic] = sum(scores) / len(scores)
            
            # Emoções dominantes
            for emotion, scores in patterns['emotion_frequencies'].items():
                if scores:
                    user_stats['dominant_emotions'][emotion] = sum(scores) / len(scores)
            
            # Horas mais ativas
            if patterns['time_preferences']:
                hours = [tp['hour'] for tp in patterns['time_preferences']]
                hour_counts = {}
                for hour in hours:
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                
                # Top 3 horas
                sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
                user_stats['most_active_hours'] = sorted_hours[:3]
            
            stats['users'][user_id] = user_stats
        
        return stats
    
    def analyze_user_context(self, text: str, user_ids: List[str]) -> Dict[str, float]:
        """
        Analisa o contexto do texto e retorna pontuações para cada utilizador.
        
        Args:
            text: Texto a analisar
            user_ids: Lista de IDs de utilizadores a considerar
            
        Returns:
            Dicionário com pontuações de contexto para cada utilizador
        """
        # Analisar o texto atual
        current_analysis = self.analyze_context(text)
        
        # Calcular pontuações para cada utilizador
        user_scores = {}
        for user_id in user_ids:
            score = self.get_user_context_score(user_id, current_analysis)
            if score > 0:
                user_scores[user_id] = score
        
        return user_scores
    
    def update_user_behavior(self, user_id: str, text: str, user_info: Dict[str, Any]) -> None:
        """
        Atualiza comportamento e padrões do utilizador.
        
        Args:
            user_id: ID do utilizador
            text: Texto da mensagem
            user_info: Informações adicionais do utilizador
        """
        # Analisar o contexto do texto
        analysis = self.analyze_context(text, user_id)
        
        # A análise já atualiza os padrões do utilizador através do _update_user_patterns
        # Podemos adicionar informações extras aqui se necessário
        
        if user_id in self.user_patterns:
            patterns = self.user_patterns[user_id]
            
            # Adicionar informações do perfil se disponíveis
            if 'name' in user_info and user_info['name']:
                patterns['user_name'] = user_info['name']
            
            if 'profession' in user_info and user_info['profession']:
                patterns['profession'] = user_info['profession']
            
            if 'location' in user_info and user_info['location']:
                patterns['location'] = user_info['location']
            
            if 'interests' in user_info and user_info['interests']:
                patterns['interests'] = user_info['interests']
            
            if 'relationships' in user_info and user_info['relationships']:
                patterns['relationships'] = user_info['relationships']
    
    def extract_behavioral_patterns(self, text: str) -> Dict[str, Any]:
        """
        Extrai padrões comportamentais de um texto.
        
        Args:
            text: Texto a analisar
            
        Returns:
            Dicionário com padrões comportamentais
        """
        analysis = self.analyze_context(text)
        
        return {
            'topics': analysis['topics'],
            'emotions': analysis['emotions'],
            'formality': analysis['formality'],
            'behavioral_indicators': analysis['behavioral_indicators'],
            'language_features': analysis['language_features'],
            'personal_references': analysis['personal_references'],
            'location_references': analysis['location_references']
        }
    
    def get_behavioral_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas comportamentais do sistema.
        
        Returns:
            Estatísticas comportamentais
        """
        stats = self.get_contextual_stats()
        
        # Adicionar estatísticas gerais
        total_behaviors = sum(patterns['total_messages'] for patterns in self.user_patterns.values())
        stats['total_behaviors_analyzed'] = total_behaviors
        
        # Adicionar informações sobre métodos de análise disponíveis
        stats['analysis_methods'] = {
            'topic_detection': True,
            'emotion_analysis': True,
            'formality_detection': True,
            'time_analysis': True,
            'behavioral_patterns': True,
            'language_features': True
        }
        
        return stats

