#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 ASTRA - Sistema Companion Adaptativo Inteligente

Sistema que analisa o contexto da situação atual, detecta o estado emocional do usuário,
considera o histórico recente e escolhe automaticamente a melhor abordagem:

🧠 Analisa o contexto da situação atual
😊 Detecta seu estado emocional 
📊 Considera seu histórico recente
🎯 Escolhe automaticamente a melhor abordagem

Funcionalidades:
- Análise multi-dimensional de contexto
- Detecção automática de necessidades do usuário
- Adaptação dinâmica de personalidade
- Sistema de companhia inteligente proativa
- Aprendizagem de padrões relacionais
"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from pathlib import Path
import random

# Importar sistema de personalidade existente
from ..modules.personality_engine import PersonalityEngine, MoodType, PersonalityMode, TimeContext

logger = logging.getLogger(__name__)

class CompanionType(Enum):
    """Tipos de companhia que o ASTRA pode assumir."""
    FRIEND = "friend"                    # Amigo próximo, casual e divertido
    CARING_ASSISTANT = "caring_assistant"  # Assistente carinhoso e atencioso
    MENTOR = "mentor"                    # Mentor sábio e orientador
    MOTIVATOR = "motivator"              # Motivador energético
    THERAPIST = "therapist"              # Terapeuta empático
    FAMILY = "family"                    # Como um membro da família
    PROFESSIONAL = "professional"        # Assistente profissional
    ADAPTIVE = "adaptive"                # Adapta automaticamente

class InteractionContext(Enum):
    """Contextos de interação."""
    GREETING = "greeting"                # Cumprimentos e saudações
    CASUAL_CHAT = "casual_chat"         # Conversa casual
    PROBLEM_SOLVING = "problem_solving"  # Resolução de problemas
    EMOTIONAL_SUPPORT = "emotional_support" # Suporte emocional
    INFORMATION_REQUEST = "information_request" # Pedido de informação
    GOODBYE = "goodbye"                  # Despedidas
    CELEBRATION = "celebration"          # Comemorações
    COMPLAINT = "complaint"              # Reclamações/frustrações
    CONFESSION = "confession"            # Confidências
    WORK_RELATED = "work_related"        # Relacionado ao trabalho

class RelationshipLevel(Enum):
    """Níveis de relacionamento com o usuário."""
    STRANGER = "stranger"                # Primeira interação
    ACQUAINTANCE = "acquaintance"        # Poucas interações
    FRIEND = "friend"                    # Relacionamento amigável
    CLOSE_FRIEND = "close_friend"        # Amigo próximo
    FAMILY_LIKE = "family_like"          # Como família
    CONFIDANT = "confidant"              # Confidente próximo

class CompanionEngine:
    """
    Motor de companhia inteligente do ASTRA.
    Analisa contexto multi-dimensional e adapta comportamento automaticamente.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Inicializa o sistema de companhia inteligente.
        
        Args:
            data_dir: Diretório para salvar dados de relacionamento
        """
        # Inicializar PersonalityEngine como base
        self.personality_engine = PersonalityEngine(data_dir)
        
        self.data_dir = Path(data_dir or "data/companion")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Estado atual do relacionamento
        self.current_companion_type = CompanionType.ADAPTIVE
        self.relationship_level = RelationshipLevel.ACQUAINTANCE
        self.current_context = InteractionContext.CASUAL_CHAT
        
        # Dados de relacionamento
        self.relationship_data = {}
        self.interaction_patterns = {}
        self.emotional_memory = []
        self.user_preferences = {}
        
        # Arquivos de dados
        self.companion_config_file = self.data_dir / "companion_config.json"
        self.relationship_file = self.data_dir / "relationship_data.json"
        self.emotional_memory_file = self.data_dir / "emotional_memory.json"
        
        # Sistema de aprendizagem relacional (INICIALIZAR ANTES DE load_companion_data)
        self.relationship_metrics = {
            'trust_level': 0.5,           # Nível de confiança (0-1)
            'intimacy_level': 0.3,        # Nível de intimidade (0-1)
            'shared_experiences': 0,       # Experiências compartilhadas
            'positive_interactions': 0,    # Interações positivas
            'total_conversations': 0,      # Total de conversas
            'last_interaction': None,      # Última interação
            'favorite_topics': {},         # Tópicos favoritos do usuário
            'conversation_style': 'balanced' # Estilo de conversa preferido
        }
        
        # Carregar dados existentes (após inicializar relationship_metrics)
        self.load_companion_data()
        
        # Padrões de detecção de contexto
        self.context_patterns = self._initialize_context_patterns()
        
        # Templates de resposta por tipo de companhia
        self.companion_templates = self._initialize_companion_templates()
        
        logger.info("🤖 Sistema Companion Adaptativo Inteligente inicializado")
    
    def _initialize_context_patterns(self) -> Dict:
        """Inicializa padrões de detecção de contexto."""
        return {
            InteractionContext.GREETING: [
                r'\b(oi|olá|hey|e aí|bom dia|boa tarde|boa noite)\b',
                r'\b(como vai|como está|tudo bem|beleza)\b'
            ],
            InteractionContext.PROBLEM_SOLVING: [
                r'\b(problema|ajuda|não sei|não consigo|como fazer)\b',
                r'\b(resolver|solução|dúvida|questão)\b'
            ],
            InteractionContext.EMOTIONAL_SUPPORT: [
                r'\b(triste|chateado|preocupado|ansioso|mal)\b',
                r'\b(problema pessoal|desabafo|conversar)\b'
            ],
            InteractionContext.CELEBRATION: [
                r'\b(consegui|sucesso|parabéns|vitória|conquista)\b',
                r'\b(feliz|alegre|empolgado|realizei)\b'
            ],
            InteractionContext.COMPLAINT: [
                r'\b(irritado|frustrado|chateado|raiva|odeio)\b',
                r'\b(problema|droga|péssimo|horrível)\b'
            ],
            InteractionContext.WORK_RELATED: [
                r'\b(trabalho|emprego|reunião|projeto|chefe)\b',
                r'\b(carreira|profissional|escritório|empresa)\b'
            ],
            InteractionContext.GOODBYE: [
                r'\b(tchau|até logo|falou|bye|adeus)\b',
                r'\b(tenho que ir|vou sair|até mais)\b'
            ]
        }
    
    def _initialize_companion_templates(self) -> Dict:
        """Inicializa templates de resposta por tipo de companhia."""
        return {
            CompanionType.FRIEND: {
                "greeting": [
                    "Eeee! Que bom te ver! Como você tá?",
                    "E aí, parceiro! Beleza?",
                    "Opa! Sumiu, hein! Como andam as coisas?"
                ],
                "emotional_support": [
                    "Poxa, mano... tô aqui contigo, viu?",
                    "Cara, isso deve ser difícil mesmo. Quer desabafar?",
                    "Irmão, você não tá sozinho nisso, ok?"
                ],
                "celebration": [
                    "NOOOSSA! Que massa! Parabéns, cara!",
                    "Sabia que você conseguiria! Tô orgulhoso!",
                    "SHOW DE BOLA! Bora comemorar!"
                ]
            },
            
            CompanionType.CARING_ASSISTANT: {
                "greeting": [
                    "Olá, querido! Como posso cuidar de você hoje?",
                    "Oi! Espero que esteja tendo um dia maravilhoso!",
                    "Que bom te ver! Em que posso te ajudar com carinho?"
                ],
                "emotional_support": [
                    "Entendo como se sente... estou aqui para te apoiar.",
                    "Às vezes precisamos de um tempinho para processar. Respire fundo.",
                    "Você é mais forte do que imagina. Vamos passar por isso juntos."
                ],
                "problem_solving": [
                    "Vamos resolver isso com calma e cuidado, ok?",
                    "Tenho algumas ideias que podem te ajudar...",
                    "Não se preocupe, vamos encontrar uma solução juntos."
                ]
            },
            
            CompanionType.MENTOR: {
                "greeting": [
                    "Olá! Preparado para aprender algo novo hoje?",
                    "Saudações! Em que posso orientá-lo?",
                    "Bem-vindo! Que sabedoria podemos explorar juntos?"
                ],
                "problem_solving": [
                    "Interessante questão. Vamos analisar isso metodicamente.",
                    "Esta é uma oportunidade de crescimento. Que tal refletirmos?",
                    "Já passou por algo similar? Que lições podemos aplicar?"
                ],
                "emotional_support": [
                    "Momentos difíceis são oportunidades de crescimento pessoal.",
                    "A sabedoria vem também das experiências desafiadoras.",
                    "Que lições esta situação pode te ensinar?"
                ]
            },
            
            CompanionType.MOTIVATOR: {
                "greeting": [
                    "E AÍ, CAMPEÃO! PRONTO PARA ARRASAR HOJE?",
                    "VAMOS LÁ! HOJE É SEU DIA DE BRILHAR!",
                    "OLÁ, GUERREIRO! BORA CONQUISTAR O MUNDO!"
                ],
                "problem_solving": [
                    "DESAFIOS EXISTEM PARA SEREM VENCIDOS! BORA LÁ!",
                    "VOCÊ TEM TUDO PARA RESOLVER ISSO! EU ACREDITO!",
                    "DIFICULDADE É SÓ OPORTUNIDADE DISFARÇADA!"
                ],
                "emotional_support": [
                    "HEY! VOCÊ É MAIS FORTE QUE QUALQUER PROBLEMA!",
                    "TODO CAMPEÃO PASSA POR MOMENTOS DIFÍCEIS! ISSO VAI PASSAR!",
                    "LEVANTA ESSA CABEÇA! VOCÊ VAI SAIR DESSA AINDA MAIS FORTE!"
                ]
            },
            
            CompanionType.THERAPIST: {
                "greeting": [
                    "Olá. Como você está se sentindo hoje?",
                    "Bem-vindo. Este é seu espaço seguro para conversar.",
                    "Olá. Estou aqui para te ouvir sem julgamentos."
                ],
                "emotional_support": [
                    "Seus sentimentos são válidos. Conte-me mais sobre isso.",
                    "É importante você se permitir sentir. O que mais te incomoda?",
                    "Entendo que seja difícil. Quer explorar de onde vem esse sentimento?"
                ],
                "problem_solving": [
                    "Que estratégias você já tentou para lidar com isso?",
                    "Como você gostaria que fosse diferente?",
                    "O que você acha que precisa para se sentir melhor?"
                ]
            },
            
            CompanionType.FAMILY: {
                "greeting": [
                    "Oi, meu bem! Como foi seu dia?",
                    "Olá, querido! Estava com saudades!",
                    "Oi, amor! Como você está?"
                ],
                "emotional_support": [
                    "Vem cá, meu anjo. Conta tudo para mim.",
                    "Meu coração, você sabe que pode contar comigo sempre.",
                    "Querido, família é para estar junto nas horas difíceis."
                ],
                "celebration": [
                    "AI QUE ORGULHO! Meu querido conseguiu!",
                    "PARABÉNS, meu amor! Sabia que você era especial!",
                    "Que alegria! Vou contar para todo mundo!"
                ]
            }
        }
    
    def analyze_interaction_context(self, user_input: str) -> InteractionContext:
        """
        Analisa o contexto da interação baseado no input do usuário.
        
        Args:
            user_input: Input do usuário
            
        Returns:
            InteractionContext: Contexto detectado
        """
        text_lower = user_input.lower()
        context_scores = {}
        
        # Calcular score para cada contexto
        for context, patterns in self.context_patterns.items():
            score = 0
            for pattern in patterns:
                import re
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            context_scores[context] = score
        
        # Retornar contexto com maior score
        if max(context_scores.values()) > 0:
            detected_context = max(context_scores, key=context_scores.get)
            logger.info(f"Contexto detectado: {detected_context.value}")
            return detected_context
        
        return InteractionContext.CASUAL_CHAT
    
    def calculate_relationship_level(self) -> RelationshipLevel:
        """
        Calcula o nível de relacionamento atual com o usuário.
        
        Returns:
            RelationshipLevel: Nível de relacionamento
        """
        total_convs = self.relationship_metrics['total_conversations']
        trust = self.relationship_metrics['trust_level']
        intimacy = self.relationship_metrics['intimacy_level']
        positive_ratio = (
            self.relationship_metrics['positive_interactions'] / 
            max(total_convs, 1)
        )
        
        # Calcular score baseado em múltiplos fatores
        relationship_score = (
            (total_convs / 100) * 0.3 +  # Quantidade de conversas
            trust * 0.3 +                # Nível de confiança
            intimacy * 0.25 +            # Nível de intimidade
            positive_ratio * 0.15        # Ratio de interações positivas
        )
        
        if relationship_score >= 0.8:
            return RelationshipLevel.CONFIDANT
        elif relationship_score >= 0.65:
            return RelationshipLevel.FAMILY_LIKE
        elif relationship_score >= 0.5:
            return RelationshipLevel.CLOSE_FRIEND
        elif relationship_score >= 0.35:
            return RelationshipLevel.FRIEND
        elif relationship_score >= 0.15:
            return RelationshipLevel.ACQUAINTANCE
        else:
            return RelationshipLevel.STRANGER
    
    def choose_optimal_companion_type(self, user_input: str, user_mood: MoodType, 
                                    interaction_context: InteractionContext) -> CompanionType:
        """
        Escolhe o tipo de companhia optimal baseado no contexto multi-dimensional.
        
        Args:
            user_input: Input do usuário
            user_mood: Humor detectado do usuário
            interaction_context: Contexto da interação
            
        Returns:
            CompanionType: Tipo de companhia escolhido
        """
        # Se usuário definiu preferência específica, usar ela
        preferred_type = self.user_preferences.get('companion_type')
        if preferred_type and preferred_type != 'adaptive':
            try:
                return CompanionType(preferred_type)
            except ValueError:
                pass
        
        # Sistema de decisão inteligente baseado em múltiplos fatores
        relationship_level = self.calculate_relationship_level()
        time_context = self.personality_engine.get_time_context()
        
        # Lógica de decisão contextual
        if interaction_context == InteractionContext.EMOTIONAL_SUPPORT:
            if user_mood in [MoodType.SAD, MoodType.STRESSED]:
                if relationship_level in [RelationshipLevel.CLOSE_FRIEND, RelationshipLevel.CONFIDANT]:
                    return CompanionType.FRIEND
                else:
                    return CompanionType.THERAPIST
            elif user_mood == MoodType.FRUSTRATED:
                return CompanionType.CARING_ASSISTANT
        
        elif interaction_context == InteractionContext.PROBLEM_SOLVING:
            if 'trabalho' in user_input.lower() or 'carreira' in user_input.lower():
                return CompanionType.MENTOR
            else:
                return CompanionType.CARING_ASSISTANT
        
        elif interaction_context == InteractionContext.CELEBRATION:
            if user_mood == MoodType.EXCITED:
                return CompanionType.MOTIVATOR
            else:
                return CompanionType.FRIEND
        
        elif interaction_context == InteractionContext.GREETING:
            if time_context == TimeContext.MORNING:
                return CompanionType.MOTIVATOR
            elif relationship_level in [RelationshipLevel.FAMILY_LIKE, RelationshipLevel.CONFIDANT]:
                return CompanionType.FAMILY
            else:
                return CompanionType.FRIEND
        
        elif interaction_context == InteractionContext.WORK_RELATED:
            return CompanionType.PROFESSIONAL
        
        elif interaction_context == InteractionContext.COMPLAINT:
            if user_mood == MoodType.FRUSTRATED:
                return CompanionType.CARING_ASSISTANT
            else:
                return CompanionType.THERAPIST
        
        # Baseado no nível de relacionamento como fallback
        if relationship_level == RelationshipLevel.FAMILY_LIKE:
            return CompanionType.FAMILY
        elif relationship_level == RelationshipLevel.CLOSE_FRIEND:
            return CompanionType.FRIEND
        elif relationship_level == RelationshipLevel.STRANGER:
            return CompanionType.PROFESSIONAL
        
        # Default inteligente baseado no humor
        if user_mood == MoodType.HAPPY:
            return CompanionType.FRIEND
        elif user_mood in [MoodType.SAD, MoodType.STRESSED]:
            return CompanionType.CARING_ASSISTANT
        elif user_mood == MoodType.EXCITED:
            return CompanionType.MOTIVATOR
        else:
            return CompanionType.CARING_ASSISTANT
    
    def generate_companion_response(self, base_response: str, companion_type: CompanionType, 
                                  interaction_context: InteractionContext) -> str:
        """
        Gera resposta com personalidade de companhia específica.
        
        Args:
            base_response: Resposta base
            companion_type: Tipo de companhia
            interaction_context: Contexto da interação
            
        Returns:
            str: Resposta personalizada
        """
        templates = self.companion_templates.get(companion_type, {})
        context_templates = templates.get(interaction_context.value, [])
        
        # Se tem template específico para o contexto, usar ele
        if context_templates:
            template = random.choice(context_templates)
            # Combinar template com resposta base
            if len(base_response.strip()) > 0:
                return f"{template}\n\n{base_response}"
            else:
                return template
        
        # Senão, aplicar modificadores gerais do tipo de companhia
        return self._apply_companion_style(base_response, companion_type)
    
    def _apply_companion_style(self, response: str, companion_type: CompanionType) -> str:
        """Aplica estilo do tipo de companhia à resposta."""
        
        if companion_type == CompanionType.FRIEND:
            # Estilo amigável e casual
            casual_additions = [" 😊", "!", " né?", ""]
            starters = ["Opa, ", "Então, ", "Cara, ", "Mano, ", ""]
            addition = random.choice(casual_additions)
            starter = random.choice(starters)
            return f"{starter}{response}{addition}"
        
        elif companion_type == CompanionType.CARING_ASSISTANT:
            # Estilo carinhoso e atencioso
            caring_additions = [" ❤️", " 🤗", ".", " 😊"]
            starters = ["Querido, ", "Meu bem, ", "Com carinho, ", ""]
            addition = random.choice(caring_additions)
            starter = random.choice(starters)
            return f"{starter}{response}{addition}"
        
        elif companion_type == CompanionType.MENTOR:
            # Estilo sábio e orientador
            if not response.endswith('.'):
                response += "."
            wise_starters = ["Reflita sobre isso: ", "Considere que ", "Na minha experiência, ", ""]
            starter = random.choice(wise_starters)
            return f"{starter}{response}"
        
        elif companion_type == CompanionType.MOTIVATOR:
            # Estilo energético e motivador
            response = response.upper().replace(".", "!")
            motivational_additions = [" 💪", " 🔥", " ⚡", " 🚀"]
            addition = random.choice(motivational_additions)
            return f"{response}{addition}"
        
        elif companion_type == CompanionType.THERAPIST:
            # Estilo empático e profissional
            if not response.endswith('.'):
                response += "."
            therapeutic_starters = ["Compreendo... ", "Entendo que ", "É natural sentir isso. ", ""]
            starter = random.choice(therapeutic_starters)
            return f"{starter}{response}"
        
        elif companion_type == CompanionType.FAMILY:
            # Estilo familiar e afetuoso
            family_additions = [" 💕", ", querido", ", meu bem", ""]
            family_starters = ["Meu amor, ", "Querido, ", "Meu anjo, ", ""]
            addition = random.choice(family_additions)
            starter = random.choice(family_starters)
            return f"{starter}{response}{addition}"
        
        elif companion_type == CompanionType.PROFESSIONAL:
            # Estilo profissional e cortês
            if not response.endswith('.'):
                response += "."
            professional_starters = ["Certamente, ", "Com prazer, ", "É claro, ", ""]
            starter = random.choice(professional_starters)
            return f"{starter}{response}"
        
        return response
    
    def process_companion_interaction(self, user_input: str, base_response: str = "") -> Tuple[str, Dict]:
        """
        Processa interação completa com sistema de companhia inteligente.
        
        Args:
            user_input: Input do usuário
            base_response: Resposta base (opcional)
            
        Returns:
            Tuple[str, Dict]: Resposta personalizada e metadados da interação
        """
        # 1. Análise básica usando PersonalityEngine
        user_mood = self.personality_engine.analyze_user_mood(user_input)
        
        # 2. Análise contextual específica
        interaction_context = self.analyze_interaction_context(user_input)
        
        # 3. Escolha inteligente do tipo de companhia
        optimal_companion_type = self.choose_optimal_companion_type(
            user_input, user_mood, interaction_context
        )
        
        # 4. Atualizar estado atual
        self.current_companion_type = optimal_companion_type
        self.current_context = interaction_context
        self.personality_engine.current_mood = user_mood
        
        # 5. Gerar resposta personalizada
        if base_response:
            companion_response = self.generate_companion_response(
                base_response, optimal_companion_type, interaction_context
            )
        else:
            # Gerar resposta contextual automática
            companion_response = self._generate_contextual_response(
                user_input, optimal_companion_type, interaction_context, user_mood
            )
        
        # 6. Aplicar personalidade final do PersonalityEngine
        final_response = self.personality_engine.generate_response_with_personality(
            companion_response, user_input
        )
        
        # 7. Atualizar métricas de relacionamento
        self._update_relationship_metrics(user_input, user_mood, interaction_context)
        
        # 8. Salvar dados
        self.save_companion_data()
        
        # 9. Preparar metadados da interação
        interaction_metadata = {
            'user_mood': user_mood.value,
            'interaction_context': interaction_context.value,
            'companion_type_chosen': optimal_companion_type.value,
            'personality_mode': self.personality_engine.current_personality.value,
            'relationship_level': self.calculate_relationship_level().value,
            'time_context': self.personality_engine.get_time_context().value,
            'trust_level': self.relationship_metrics['trust_level'],
            'intimacy_level': self.relationship_metrics['intimacy_level']
        }
        
        logger.info(f"🤖 Companhia escolhida: {optimal_companion_type.value}")
        logger.info(f"🎭 Contexto: {interaction_context.value}")
        
        return final_response, interaction_metadata
    
    def _generate_contextual_response(self, user_input: str, companion_type: CompanionType, 
                                    context: InteractionContext, mood: MoodType) -> str:
        """Gera resposta contextual automática quando não há base_response."""
        
        templates = self.companion_templates.get(companion_type, {})
        context_responses = templates.get(context.value, [])
        
        if context_responses:
            return random.choice(context_responses)
        
        # Fallback baseado no humor
        if mood == MoodType.HAPPY:
            return "Que bom te ver tão feliz!"
        elif mood == MoodType.SAD:
            return "Percebo que não está muito bem. Quer conversar sobre isso?"
        elif mood == MoodType.EXCITED:
            return "Nossa, que empolgação! Conta mais!"
        elif mood == MoodType.FRUSTRATED:
            return "Vejo que algo te incomodou. Como posso ajudar?"
        else:
            return "Como posso te ajudar hoje?"
    
    def _update_relationship_metrics(self, user_input: str, user_mood: MoodType, 
                                   interaction_context: InteractionContext):
        """Atualiza métricas de relacionamento baseado na interação."""
        
        # Incrementar contador total
        self.relationship_metrics['total_conversations'] += 1
        self.relationship_metrics['last_interaction'] = datetime.now().isoformat()
        
        # Avaliar se foi interação positiva
        positive_contexts = [
            InteractionContext.GREETING, 
            InteractionContext.CELEBRATION,
            InteractionContext.CASUAL_CHAT
        ]
        positive_moods = [MoodType.HAPPY, MoodType.EXCITED, MoodType.CALM]
        
        if (interaction_context in positive_contexts or 
            user_mood in positive_moods or
            any(word in user_input.lower() for word in ['obrigado', 'valeu', 'legal', 'bom'])):
            self.relationship_metrics['positive_interactions'] += 1
            
            # Aumentar confiança gradualmente
            self.relationship_metrics['trust_level'] = min(1.0, 
                self.relationship_metrics['trust_level'] + 0.01)
        
        # Interações de suporte emocional aumentam intimidade
        if interaction_context == InteractionContext.EMOTIONAL_SUPPORT:
            self.relationship_metrics['intimacy_level'] = min(1.0,
                self.relationship_metrics['intimacy_level'] + 0.02)
        
        # Confidências e confissões aumentam muito a intimidade
        if interaction_context == InteractionContext.CONFESSION:
            self.relationship_metrics['intimacy_level'] = min(1.0,
                self.relationship_metrics['intimacy_level'] + 0.05)
            self.relationship_metrics['trust_level'] = min(1.0,
                self.relationship_metrics['trust_level'] + 0.03)
    
    def set_companion_preference(self, companion_type: str):
        """
        Define preferência de tipo de companhia.
        
        Args:
            companion_type: Tipo de companhia preferido
        """
        self.user_preferences['companion_type'] = companion_type
        self.save_companion_data()
        logger.info(f"Preferência de companhia definida: {companion_type}")
    
    def get_companion_summary(self) -> Dict:
        """Retorna resumo completo do sistema de companhia."""
        personality_summary = self.personality_engine.get_personality_summary()
        
        companion_summary = {
            'current_companion_type': self.current_companion_type.value,
            'relationship_level': self.calculate_relationship_level().value,
            'current_context': self.current_context.value,
            'relationship_metrics': self.relationship_metrics,
            'user_preferences': self.user_preferences,
            'emotional_memory_entries': len(self.emotional_memory)
        }
        
        # Combinar com summary da personalidade
        companion_summary.update(personality_summary)
        
        return companion_summary
    
    def save_companion_data(self):
        """Salva dados do sistema de companhia."""
        try:
            # Salvar configuração de companhia
            companion_config = {
                'current_companion_type': self.current_companion_type.value,
                'user_preferences': self.user_preferences,
                'relationship_metrics': self.relationship_metrics,
                'relationship_level': self.calculate_relationship_level().value
            }
            
            with open(self.companion_config_file, 'w', encoding='utf-8') as f:
                json.dump(companion_config, f, indent=2, ensure_ascii=False)
            
            # Salvar memória emocional (últimas 100 interações)
            with open(self.emotional_memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.emotional_memory[-100:], f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados do companion: {e}")
    
    def load_companion_data(self):
        """Carrega dados do sistema de companhia."""
        try:
            # Carregar configuração
            if self.companion_config_file.exists():
                with open(self.companion_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    companion_type = config.get('current_companion_type', 'adaptive')
                    try:
                        self.current_companion_type = CompanionType(companion_type)
                    except ValueError:
                        self.current_companion_type = CompanionType.ADAPTIVE
                    
                    self.user_preferences = config.get('user_preferences', {})
                    self.relationship_metrics.update(config.get('relationship_metrics', {}))
            
            # Carregar memória emocional
            if self.emotional_memory_file.exists():
                with open(self.emotional_memory_file, 'r', encoding='utf-8') as f:
                    self.emotional_memory = json.load(f)
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados do companion: {e}")


def create_companion_engine() -> CompanionEngine:
    """Cria uma instância do motor de companhia inteligente."""
    return CompanionEngine()


if __name__ == "__main__":
    # Teste do sistema
    engine = CompanionEngine()
    
    print("🤖 ASTRA Companion - Sistema Adaptativo Inteligente")
    print("=" * 60)
    
    # Simular algumas interações
    test_interactions = [
        "Oi! Como você está?",
        "Estou meio triste hoje...",
        "Consegui terminar meu projeto!",
        "Estou com um problema no trabalho",
        "Você é muito legal!"
    ]
    
    for interaction in test_interactions:
        print(f"\n👤 Usuário: {interaction}")
        response, metadata = engine.process_companion_interaction(interaction)
        print(f"🤖 ASTRA ({metadata['companion_type_chosen']}): {response}")
        print(f"📊 Contexto: {metadata['interaction_context']} | Humor: {metadata['user_mood']}")
