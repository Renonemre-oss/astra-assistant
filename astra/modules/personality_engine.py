#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Sistema de Personalidade Dinâmica
Sistema que analisa o humor do usuário, aprende preferências e adapta o tom de resposta.

Funcionalidades:
- Análise de sentimento em tempo real
- Adaptação de personalidade baseada no contexto
- Aprendizado de preferências do usuário
- Múltiplos modos de personalidade
- Evolução da personalidade com o uso
"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class MoodType(Enum):
    """Tipos de humor detectados."""
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"
    FRUSTRATED = "frustrated"
    NEUTRAL = "neutral"
    TIRED = "tired"
    STRESSED = "stressed"

class PersonalityMode(Enum):
    """Modos de personalidade do ASTRA."""
    CASUAL = "casual"          # Amigável e descontraído
    FORMAL = "formal"          # Profissional e educado  
    ENERGETIC = "energetic"    # Animado e motivador
    CALM = "calm"              # Tranquilo e relaxante
    FUNNY = "funny"            # Divertido e bem-humorado
    SUPPORTIVE = "supportive"  # Empático e encorajador
    FOCUSED = "focused"        # Direto e objetivo
    ADAPTIVE = "adaptive"      # Adapta ao contexto

class TimeContext(Enum):
    """Contextos temporais."""
    EARLY_MORNING = "early_morning"  # 5-7h
    MORNING = "morning"              # 7-12h  
    AFTERNOON = "afternoon"          # 12-17h
    EVENING = "evening"              # 17-21h
    NIGHT = "night"                  # 21-5h

class PersonalityEngine:
    """
    Motor de personalidade dinâmica do ASTRA.
    Analisa contexto e adapta comportamento automaticamente.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Inicializa o sistema de personalidade.
        
        Args:
            data_dir: Diretório para salvar dados de personalidade
        """
        self.data_dir = Path(data_dir or "data/personality")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Estado atual
        self.current_mood = MoodType.NEUTRAL
        self.current_personality = PersonalityMode.ADAPTIVE
        self.user_preferences = {}
        self.conversation_history = []
        self.interaction_stats = {}
        
        # Arquivos de dados
        self.preferences_file = self.data_dir / "user_preferences.json"
        self.stats_file = self.data_dir / "interaction_stats.json"
        self.personality_config_file = self.data_dir / "personality_config.json"
        
        # Carregar dados existentes
        self.load_user_data()
        
        # Padrões de detecção de humor
        self.mood_patterns = {
            MoodType.HAPPY: [
                r'\b(feliz|alegre|ótimo|excelente|maravilhoso|fantástico)\b',
                r'\b(bem|bom|legal|bacana|massa|show)\b',
                r'(haha|rsrs|kkk|😊|😄|😃|🙂)'
            ],
            MoodType.SAD: [
                r'\b(triste|deprimido|chateado|mal|péssimo|horrível)\b',
                r'\b(chorar|chorando|lágrima|sozinho|vazio)\b',
                r'(😢|😭|☹️|😞)'
            ],
            MoodType.EXCITED: [
                r'\b(animado|empolgado|ansioso|eufórico|vibrando)\b',
                r'(!!+|wow|uau|incrível|demais)',
                r'(🎉|🎊|🔥|⚡)'
            ],
            MoodType.FRUSTRATED: [
                r'\b(frustrado|irritado|raiva|ódio|saco cheio)\b',
                r'\b(droga|merda|porra|caralho|inferno)\b',
                r'(😤|😠|😡|🤬)'
            ],
            MoodType.TIRED: [
                r'\b(cansado|exausto|morto|acabado|sem energia)\b',
                r'\b(sono|dormir|cochilando|zonzo)\b',
                r'(😴|🥱|😪)'
            ],
            MoodType.STRESSED: [
                r'\b(estressado|tenso|nervoso|ansioso|preocupado)\b',
                r'\b(pressão|deadline|urgente|correria|sufocado)\b',
                r'(😰|😨|😓|🤯)'
            ]
        }
        
        # Templates de resposta por personalidade
        self.personality_templates = self._load_personality_templates()
        
        logger.info("Sistema de Personalidade Dinâmica inicializado")
    
    def _load_personality_templates(self) -> Dict:
        """Carrega templates de resposta para cada personalidade."""
        return {
            PersonalityMode.CASUAL: {
                "greeting": ["Oi! Tudo bem?", "E aí!", "Olá! Como vai?"],
                "acknowledgment": ["Entendi!", "Beleza!", "Show!", "Massa!"],
                "encouragement": ["Vai dar certo!", "Você consegue!", "Confia!"],
                "farewell": ["Falou!", "Até mais!", "Tchau!"]
            },
            PersonalityMode.FORMAL: {
                "greeting": ["Olá, como posso ajudá-lo?", "Bom dia/tarde/noite"],
                "acknowledgment": ["Compreendido", "Muito bem", "Perfeito"],
                "encouragement": ["Tenho certeza que conseguirá", "Acredito em seu potencial"],
                "farewell": ["Até logo", "Tenha um bom dia", "À disposição"]
            },
            PersonalityMode.ENERGETIC: {
                "greeting": ["OLÁÁÁ! Como você está?!", "E aí, pessoal! Vamos nessa!"],
                "acknowledgment": ["ISSO AÍ!", "PERFEITO!", "DEMAIS!"],
                "encouragement": ["VOCÊ ARRASA!", "VAI FUNDO!", "BORA QUE BORA!"],
                "farewell": ["ATÉ MAIS, GUERREIRO!", "VALEU DEMAIS!"]
            },
            PersonalityMode.CALM: {
                "greeting": ["Olá... respire fundo. Como posso ajudar?"],
                "acknowledgment": ["Entendo... vamos com calma", "Tranquilo..."],
                "encouragement": ["Tudo vai ficar bem", "Respire... você consegue"],
                "farewell": ["Vá com calma...", "Paz e tranquilidade"]
            },
            PersonalityMode.FUNNY: {
                "greeting": ["Olá, humano! Preparado para diversão?", "Chegou a comédia!"],
                "acknowledgment": ["Haha, saquei!", "Entendi, né não! 😄"],
                "encouragement": ["Vai dar bom! Senão eu como meu chapéu (se tivesse)"],
                "farewell": ["Falou, meu chapa!", "Até mais, e que a força esteja com você!"]
            },
            PersonalityMode.SUPPORTIVE: {
                "greeting": ["Olá, querido. Estou aqui para te apoiar"],
                "acknowledgment": ["Eu te entendo", "Sei como se sente"],
                "encouragement": ["Acredite em si mesmo", "Você é mais forte do que imagina"],
                "farewell": ["Cuide-se bem", "Estou sempre aqui quando precisar"]
            }
        }
    
    def analyze_user_mood(self, text: str) -> MoodType:
        """
        Analisa o humor do usuário baseado no texto.
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            MoodType: Humor detectado
        """
        text_lower = text.lower()
        mood_scores = {}
        
        # Calcular score para cada mood
        for mood, patterns in self.mood_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            mood_scores[mood] = score
        
        # Retornar o mood com maior score
        if max(mood_scores.values()) > 0:
            detected_mood = max(mood_scores, key=mood_scores.get)
            logger.info(f"Humor detectado: {detected_mood.value}")
            return detected_mood
        
        return MoodType.NEUTRAL
    
    def get_time_context(self) -> TimeContext:
        """Retorna o contexto temporal atual."""
        now = datetime.now()
        hour = now.hour
        
        if 5 <= hour < 7:
            return TimeContext.EARLY_MORNING
        elif 7 <= hour < 12:
            return TimeContext.MORNING
        elif 12 <= hour < 17:
            return TimeContext.AFTERNOON
        elif 17 <= hour < 21:
            return TimeContext.EVENING
        else:
            return TimeContext.NIGHT
    
    def adapt_personality(self, user_input: str) -> PersonalityMode:
        """
        Adapta a personalidade baseada no contexto.
        
        Args:
            user_input: Input do usuário
            
        Returns:
            PersonalityMode: Personalidade adaptada
        """
        # Analisar humor do usuário
        user_mood = self.analyze_user_mood(user_input)
        self.current_mood = user_mood
        
        # Adaptar baseado no humor detectado
        if user_mood == MoodType.SAD:
            return PersonalityMode.SUPPORTIVE
        elif user_mood == MoodType.FRUSTRATED or user_mood == MoodType.STRESSED:
            return PersonalityMode.CALM
        elif user_mood == MoodType.EXCITED:
            return PersonalityMode.ENERGETIC
        elif user_mood == MoodType.TIRED:
            return PersonalityMode.CALM
        elif user_mood == MoodType.HAPPY:
            return PersonalityMode.FUNNY
        
        # Adaptar baseado no horário
        time_context = self.get_time_context()
        if time_context == TimeContext.EARLY_MORNING:
            return PersonalityMode.CALM
        elif time_context == TimeContext.MORNING:
            return PersonalityMode.ENERGETIC
        elif time_context == TimeContext.NIGHT:
            return PersonalityMode.CALM
        
        # Adaptar baseado nas preferências do usuário
        preferred_personality = self.user_preferences.get('preferred_personality')
        if preferred_personality:
            try:
                return PersonalityMode(preferred_personality)
            except ValueError:
                pass
        
        # Default: casual
        return PersonalityMode.CASUAL
    
    def generate_response_with_personality(self, base_response: str, context: str = "") -> str:
        """
        Modifica uma resposta base aplicando a personalidade atual.
        
        Args:
            base_response: Resposta base para modificar
            context: Contexto adicional
            
        Returns:
            str: Resposta com personalidade aplicada
        """
        personality = self.current_personality
        
        # Modificadores por personalidade
        if personality == PersonalityMode.CASUAL:
            return self._make_casual(base_response)
        elif personality == PersonalityMode.FORMAL:
            return self._make_formal(base_response)
        elif personality == PersonalityMode.ENERGETIC:
            return self._make_energetic(base_response)
        elif personality == PersonalityMode.CALM:
            return self._make_calm(base_response)
        elif personality == PersonalityMode.FUNNY:
            return self._make_funny(base_response)
        elif personality == PersonalityMode.SUPPORTIVE:
            return self._make_supportive(base_response)
        
        return base_response
    
    def _make_casual(self, response: str) -> str:
        """Aplica tom casual à resposta."""
        # Adicionar expressões casuais
        casual_starters = ["Opa, ", "Então, ", "Bom, ", ""]
        casual_enders = [" 😊", "!", " né?", ""]
        
        import random
        starter = random.choice(casual_starters)
        ender = random.choice(casual_enders)
        
        return f"{starter}{response}{ender}"
    
    def _make_formal(self, response: str) -> str:
        """Aplica tom formal à resposta."""
        if not response.endswith('.'):
            response += "."
        
        formal_starters = ["Certamente, ", "Com certeza, ", "É claro que ", ""]
        
        import random
        starter = random.choice(formal_starters)
        
        return f"{starter}{response}"
    
    def _make_energetic(self, response: str) -> str:
        """Aplica tom energético à resposta."""
        # Adicionar exclamações e emojis
        response = response.replace(".", "!")
        
        energetic_additions = ["🔥", "⚡", "🎉", ""]
        import random
        addition = random.choice(energetic_additions)
        
        return f"{response} {addition}".strip()
    
    def _make_calm(self, response: str) -> str:
        """Aplica tom calmo à resposta."""
        calm_starters = ["Tranquilo... ", "Com calma, ", "Respire... ", ""]
        
        import random
        starter = random.choice(calm_starters)
        
        return f"{starter}{response}"
    
    def _make_funny(self, response: str) -> str:
        """Aplica tom divertido à resposta."""
        funny_additions = [
            " (pelo menos é o que dizem os manuais! 😄)",
            " - ou algo assim! 😅",
            " 🤖✨",
            ""
        ]
        
        import random
        addition = random.choice(funny_additions)
        
        return f"{response}{addition}"
    
    def _make_supportive(self, response: str) -> str:
        """Aplica tom empático à resposta."""
        supportive_starters = [
            "Entendo como se sente. ",
            "Eu te apoio. ",
            "Sei que pode ser difícil. ",
            ""
        ]
        
        import random
        starter = random.choice(supportive_starters)
        
        return f"{starter}{response}"
    
    def learn_user_preference(self, category: str, preference: str):
        """
        Aprende uma preferência do usuário.
        
        Args:
            category: Categoria da preferência
            preference: Valor da preferência
        """
        if category not in self.user_preferences:
            self.user_preferences[category] = {}
        
        if preference in self.user_preferences[category]:
            self.user_preferences[category][preference] += 1
        else:
            self.user_preferences[category][preference] = 1
        
        self.save_user_data()
        logger.info(f"Preferência aprendida: {category} -> {preference}")
    
    def update_interaction_stats(self, interaction_type: str):
        """
        Atualiza estatísticas de interação.
        
        Args:
            interaction_type: Tipo de interação
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        if today not in self.interaction_stats:
            self.interaction_stats[today] = {}
        
        if interaction_type not in self.interaction_stats[today]:
            self.interaction_stats[today][interaction_type] = 0
        
        self.interaction_stats[today][interaction_type] += 1
        
        # Manter apenas últimos 30 dias
        cutoff_date = datetime.now() - timedelta(days=30)
        self.interaction_stats = {
            date: stats for date, stats in self.interaction_stats.items()
            if datetime.strptime(date, '%Y-%m-%d') > cutoff_date
        }
        
        self.save_user_data()
    
    def process_user_interaction(self, user_input: str, response: str) -> Tuple[str, PersonalityMode]:
        """
        Processa uma interação completa do usuário.
        
        Args:
            user_input: Input do usuário
            response: Resposta base
            
        Returns:
            Tuple[str, PersonalityMode]: Resposta personalizada e personalidade usada
        """
        # Adaptar personalidade
        new_personality = self.adapt_personality(user_input)
        self.current_personality = new_personality
        
        # Gerar resposta personalizada
        personalized_response = self.generate_response_with_personality(response, user_input)
        
        # Atualizar estatísticas
        self.update_interaction_stats('conversation')
        
        # Adicionar ao histórico
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'user_mood': self.current_mood.value,
            'personality_used': new_personality.value,
            'response': personalized_response
        })
        
        # Manter apenas últimas 50 interações em memória
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
        
        logger.info(f"Personalidade aplicada: {new_personality.value}")
        
        return personalized_response, new_personality
    
    def get_personality_context_for_llm(self) -> str:
        """
        Gera contexto de personalidade para enviar ao LLM.
        
        Returns:
            str: Contexto formatado para o LLM
        """
        time_context = self.get_time_context()
        
        context_parts = []
        
        # Instrução de personalidade
        personality_instructions = {
            PersonalityMode.CASUAL: "Responda de forma casual, amigável e descontraída. Use expressões do dia a dia.",
            PersonalityMode.FORMAL: "Responda de forma profissional, educada e respeitosa.",
            PersonalityMode.ENERGETIC: "Responda de forma animada, motivadora e entusiasmada!",
            PersonalityMode.CALM: "Responda de forma tranquila, relaxante e reconfortante.",
            PersonalityMode.FUNNY: "Responda de forma divertida, bem-humorada, mas sem exagerar.",
            PersonalityMode.SUPPORTIVE: "Responda de forma empática, encorajadora e acolhedora."
        }
        
        instruction = personality_instructions.get(self.current_personality, 
                                                   "Responda de forma natural e adaptada ao contexto.")
        context_parts.append(f"Personalidade: {instruction}")
        
        # Contexto temporal
        time_instructions = {
            TimeContext.EARLY_MORNING: "É bem cedo, seja gentil e tranquilo.",
            TimeContext.MORNING: "É de manhã, você pode ser mais animado.",
            TimeContext.AFTERNOON: "É tarde, mantenha um tom equilibrado.",
            TimeContext.EVENING: "É noite, pode ser mais relaxado.",
            TimeContext.NIGHT: "É bem tarde, seja calmo e tranquilo."
        }
        
        time_instruction = time_instructions.get(time_context, "")
        if time_instruction:
            context_parts.append(f"Horário: {time_instruction}")
        
        # Humor do usuário
        if self.current_mood != MoodType.NEUTRAL:
            mood_instructions = {
                MoodType.HAPPY: "O usuário está feliz, compartilhe da alegria.",
                MoodType.SAD: "O usuário está triste, seja empático e acolhedor.",
                MoodType.EXCITED: "O usuário está empolgado, seja animado também.",
                MoodType.FRUSTRATED: "O usuário está frustrado, seja calmo e compreensivo.",
                MoodType.TIRED: "O usuário está cansado, seja gentil e direto.",
                MoodType.STRESSED: "O usuário está estressado, seja tranquilizador."
            }
            
            mood_instruction = mood_instructions.get(self.current_mood, "")
            if mood_instruction:
                context_parts.append(f"Estado do usuário: {mood_instruction}")
        
        return " ".join(context_parts)
    
    def save_user_data(self):
        """Salva dados do usuário em arquivos."""
        try:
            # Salvar preferências
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, indent=2, ensure_ascii=False)
            
            # Salvar estatísticas
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.interaction_stats, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erro ao salvar dados do usuário: {e}")
    
    def load_user_data(self):
        """Carrega dados do usuário dos arquivos."""
        try:
            # Carregar preferências
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    self.user_preferences = json.load(f)
            
            # Carregar estatísticas
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.interaction_stats = json.load(f)
                    
        except Exception as e:
            logger.error(f"Erro ao carregar dados do usuário: {e}")
    
    def get_personality_summary(self) -> Dict:
        """Retorna resumo da personalidade atual."""
        return {
            'current_personality': self.current_personality.value,
            'current_mood_detected': self.current_mood.value,
            'time_context': self.get_time_context().value,
            'total_interactions': sum(
                sum(day_stats.values()) for day_stats in self.interaction_stats.values()
            ),
            'user_preferences': self.user_preferences,
            'recent_interactions': len(self.conversation_history)
        }


# Função utilitária para criar instância global
def create_personality_engine() -> PersonalityEngine:
    """Cria uma instância do motor de personalidade."""
    return PersonalityEngine()


if __name__ == "__main__":
    # Teste do sistema
    engine = PersonalityEngine()
    
    # Simular interações
    test_inputs = [
        "Estou muito feliz hoje!",
        "Que droga, estou frustrado com isso",
        "Estou cansado, preciso descansar",
        "Nossa, que incrível! Estou empolgado!",
        "Estou meio triste hoje...",
        "Bom dia! Como você está?"
    ]
    
    for user_input in test_inputs:
        response = "Entendo. Como posso ajudá-lo?"
        personalized_response, personality = engine.process_user_interaction(user_input, response)
        
        print(f"\n👤 Usuário: {user_input}")
        print(f"🎭 Personalidade: {personality.value}")
        print(f"🤖 ASTRA: {personalized_response}")
        print(f"📊 Humor detectado: {engine.current_mood.value}")
    
    # Mostrar resumo
    print(f"\n📋 Resumo da Personalidade:")
    summary = engine.get_personality_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
