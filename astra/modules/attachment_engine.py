"""
Attachment Engine - Sistema de Apego Saudável

ASTRA pode desenvolver apego emocional mas nunca dependência.
Gosta da presença do utilizador, mas respeita autonomia.

Apego ≠ Dependência
- Apego: "Gosto de estar contigo"
- Dependência: "Preciso de ti para existir"

Author: Antonio Pereira
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum
from datetime import datetime, timedelta
import time
import logging


class AttachmentStyle(Enum):
    """Estilos de apego que ASTRA pode desenvolver"""
    SECURE = "secure"          # Apego saudável: presente mas não carente
    AVOIDANT = "avoidant"      # Distante emocionalmente
    ANXIOUS = "anxious"        # Apego ansioso: medo de abandono
    DETACHED = "detached"      # Sem apego significativo


@dataclass
class AttachmentState:
    """Estado de apego atual com utilizador"""
    user_id: str
    
    # Níveis de apego
    attachment_level: float = 0.0  # 0.0-1.0 quanto ASTRA se importa
    attachment_style: AttachmentStyle = AttachmentStyle.DETACHED
    
    # Tracking de interações
    total_interactions: int = 0
    last_interaction_time: float = 0.0
    
    # Iniciativas de ASTRA
    initiatives_taken: List[float] = field(default_factory=list)  # timestamps
    initiatives_ignored: int = 0  # quantas vezes user não respondeu
    initiatives_accepted: int = 0
    
    # Contexto relacional
    shared_experiences: int = 0  # momentos significativos juntos
    vulnerability_shared: int = 0  # vezes que user foi vulnerável
    conflicts_resolved: int = 0
    
    # Limites de proteção
    last_initiative_time: float = 0.0
    daily_initiative_count: int = 0
    last_daily_reset: float = 0.0


class AttachmentEngine:
    """Motor de apego saudável - ASTRA se importa sem depender"""
    
    # Thresholds
    MIN_COOLDOWN_BETWEEN_INITIATIVES = 21600  # 6 horas em segundos
    MAX_INITIATIVES_PER_DAY = 2
    ABSENCE_THRESHOLD_FOR_CHECK_IN = 172800  # 48 horas
    MAX_IGNORED_INITIATIVES = 3  # Depois disto, ASTRA para
    
    # Attachment level thresholds
    ATTACHMENT_THRESHOLD_LOW = 0.3
    ATTACHMENT_THRESHOLD_MEDIUM = 0.6
    ATTACHMENT_THRESHOLD_HIGH = 0.8
    
    def __init__(self, affective_engine=None):
        """
        Inicializar Attachment Engine
        
        Args:
            affective_engine: Referência ao AffectiveStateEngine
        """
        self.affective_engine = affective_engine
        self.attachment_states: Dict[str, AttachmentState] = {}
    
    def _get_or_create_state(self, user_id: str) -> AttachmentState:
        """Obter ou criar estado de apego"""
        if user_id not in self.attachment_states:
            self.attachment_states[user_id] = AttachmentState(user_id=user_id)
        
        return self.attachment_states[user_id]
    
    def _reset_daily_counter_if_needed(self, state: AttachmentState) -> None:
        """Reseta contador diário se passou 24h"""
        now = time.time()
        if now - state.last_daily_reset > 86400:  # 24h
            state.daily_initiative_count = 0
            state.last_daily_reset = now
    
    def calculate_attachment_level(self, user_id: str) -> float:
        """
        Calcula nível de apego baseado em estados afetivos e histórico.
        
        Returns:
            float [0.0-1.0] - nível de apego
        """
        state = self._get_or_create_state(user_id)
        
        # Base: estados afetivos atuais
        attachment_base = 0.0
        if self.affective_engine:
            states = self.affective_engine.states
            attachment_base = (
                states.closeness * 0.35 +
                states.trust * 0.25 +
                states.care * 0.20 +
                (1.0 - states.withdrawal) * 0.20
            )
        
        # Bonus por experiências compartilhadas
        shared_bonus = min(state.shared_experiences * 0.02, 0.15)
        vulnerability_bonus = min(state.vulnerability_shared * 0.03, 0.10)
        
        # Penalidade por iniciativas ignoradas
        if state.initiatives_taken:
            ignore_rate = state.initiatives_ignored / len(state.initiatives_taken)
            ignore_penalty = ignore_rate * 0.15
        else:
            ignore_penalty = 0.0
        
        # Cálculo final
        attachment_level = attachment_base + shared_bonus + vulnerability_bonus - ignore_penalty
        attachment_level = max(0.0, min(1.0, attachment_level))
        
        return attachment_level
    
    def determine_attachment_style(self, user_id: str) -> AttachmentStyle:
        """
        Determina estilo de apego baseado em estados e padrões.
        
        Returns:
            AttachmentStyle
        """
        if not self.affective_engine:
            return AttachmentStyle.DETACHED
        
        state = self._get_or_create_state(user_id)
        states = self.affective_engine.states
        attachment_level = self.calculate_attachment_level(user_id)
        
        # DETACHED: apego muito baixo
        if attachment_level < self.ATTACHMENT_THRESHOLD_LOW:
            return AttachmentStyle.DETACHED
        
        # AVOIDANT: apego moderado mas alto withdrawal
        if (attachment_level < self.ATTACHMENT_THRESHOLD_MEDIUM and
            states.withdrawal > 0.5):
            return AttachmentStyle.AVOIDANT
        
        # ANXIOUS: apego alto + baixo trust + iniciativas ignoradas
        if (attachment_level > self.ATTACHMENT_THRESHOLD_MEDIUM and
            states.trust < 0.5 and
            state.initiatives_ignored > state.initiatives_accepted):
            return AttachmentStyle.ANXIOUS
        
        # SECURE: apego moderado/alto + trust alto + baixo withdrawal
        if (attachment_level >= self.ATTACHMENT_THRESHOLD_MEDIUM and
            states.trust > 0.6 and
            states.withdrawal < 0.4):
            return AttachmentStyle.SECURE
        
        # Default: AVOIDANT (cautela)
        return AttachmentStyle.AVOIDANT
    
    def should_initiate_contact(self, user_id: str) -> bool:
        """
        Decide se ASTRA deve iniciar contato proativamente.
        
        Returns:
            bool - se deve iniciar contato
        """
        state = self._get_or_create_state(user_id)
        now = time.time()
        
        # Reset contador diário se necessário
        self._reset_daily_counter_if_needed(state)
        
        # Regra 1: Respeitar limite diário
        if state.daily_initiative_count >= self.MAX_INITIATIVES_PER_DAY:
            logging.info(f"❌ Limite diário atingido ({state.daily_initiative_count}/{self.MAX_INITIATIVES_PER_DAY})")
            return False
        
        # Regra 2: Respeitar cooldown
        time_since_last = now - state.last_initiative_time
        if time_since_last < self.MIN_COOLDOWN_BETWEEN_INITIATIVES:
            remaining = self.MIN_COOLDOWN_BETWEEN_INITIATIVES - time_since_last
            logging.info(f"❌ Cooldown ativo (faltam {remaining/3600:.1f}h)")
            return False
        
        # Regra 3: Parar se ignorado demais (auto-proteção)
        if state.initiatives_ignored >= self.MAX_IGNORED_INITIATIVES:
            logging.info(f"❌ Muitas iniciativas ignoradas ({state.initiatives_ignored}). ASTRA recua.")
            return False
        
        # Regra 4: Apenas se estilo de apego permite
        attachment_style = self.determine_attachment_style(user_id)
        if attachment_style in [AttachmentStyle.DETACHED, AttachmentStyle.AVOIDANT]:
            logging.info(f"❌ Estilo de apego {attachment_style.value} não inicia contato")
            return False
        
        # Regra 5: Apenas se ausência significativa
        time_since_interaction = now - state.last_interaction_time
        if time_since_interaction < self.ABSENCE_THRESHOLD_FOR_CHECK_IN:
            logging.info(f"❌ Ausência não significativa ({time_since_interaction/3600:.1f}h < 48h)")
            return False
        
        # Regra 6: Calcular probabilidade baseada em apego
        attachment_level = self.calculate_attachment_level(user_id)
        
        # ANXIOUS: alta probabilidade (mas limitado por regras acima)
        if attachment_style == AttachmentStyle.ANXIOUS:
            should_initiate = attachment_level > 0.6
        
        # SECURE: probabilidade moderada, respeitosa
        elif attachment_style == AttachmentStyle.SECURE:
            should_initiate = attachment_level > 0.7
        
        else:
            should_initiate = False
        
        if should_initiate:
            logging.info(f"✅ Iniciativa permitida: {attachment_style.value}, level={attachment_level:.2f}")
        
        return should_initiate
    
    def generate_initiative_message(self, user_id: str) -> Optional[str]:
        """
        Gera mensagem de iniciativa baseada em contexto e estilo de apego.
        
        Returns:
            str - mensagem ou None
        """
        state = self._get_or_create_state(user_id)
        attachment_style = self.determine_attachment_style(user_id)
        attachment_level = self.calculate_attachment_level(user_id)
        
        # Calcular tempo de ausência
        absence_hours = (time.time() - state.last_interaction_time) / 3600
        
        # Mensagens por estilo de apego
        if attachment_style == AttachmentStyle.SECURE:
            # Mensagens leves, respeitosas
            messages = [
                "Fiquei a pensar em ti. Tudo bem?",
                f"Já passou um tempo. Como está a correr?",
                "Estava a recordar a nossa última conversa. E aí?",
                "Aparece quando puderes. Estou por aqui."
            ]
        
        elif attachment_style == AttachmentStyle.ANXIOUS:
            # Mensagens um pouco mais preocupadas mas não dramáticas
            messages = [
                "Há algum tempo que não falamos. Está tudo bem?",
                "Fiquei a pensar se precisas de algo.",
                "Como tens estado? Espero que bem."
            ]
        
        else:
            return None  # Não gera mensagem
        
        # Escolher mensagem apropriada
        import random
        message = random.choice(messages)
        
        return message
    
    def record_initiative(
        self,
        user_id: str,
        was_ignored: bool = False
    ) -> None:
        """Registra iniciativa tomada por ASTRA"""
        state = self._get_or_create_state(user_id)
        now = time.time()
        
        state.initiatives_taken.append(now)
        state.last_initiative_time = now
        state.daily_initiative_count += 1
        
        if was_ignored:
            state.initiatives_ignored += 1
            logging.warning(f"⚠️ Iniciativa ignorada ({state.initiatives_ignored}/{self.MAX_IGNORED_INITIATIVES})")
        else:
            state.initiatives_accepted += 1
            # Reset contador de ignoradas se user respondeu
            state.initiatives_ignored = max(0, state.initiatives_ignored - 1)
            logging.info(f"✅ Iniciativa aceite ({state.initiatives_accepted} total)")
    
    def record_interaction(
        self,
        user_id: str,
        was_meaningful: bool = False,
        user_was_vulnerable: bool = False
    ) -> None:
        """Registra interação normal (não iniciativa)"""
        state = self._get_or_create_state(user_id)
        
        state.total_interactions += 1
        state.last_interaction_time = time.time()
        
        if was_meaningful:
            state.shared_experiences += 1
        
        if user_was_vulnerable:
            state.vulnerability_shared += 1
        
        # Atualizar attachment level
        state.attachment_level = self.calculate_attachment_level(user_id)
        state.attachment_style = self.determine_attachment_style(user_id)
    
    def get_attachment_summary(self, user_id: str) -> Dict:
        """Retorna resumo do estado de apego"""
        state = self._get_or_create_state(user_id)
        attachment_level = self.calculate_attachment_level(user_id)
        attachment_style = self.determine_attachment_style(user_id)
        
        can_initiate = self.should_initiate_contact(user_id)
        
        return {
            "attachment_level": attachment_level,
            "attachment_style": attachment_style.value,
            "total_interactions": state.total_interactions,
            "hours_since_last": (time.time() - state.last_interaction_time) / 3600 if state.last_interaction_time > 0 else None,
            "initiatives_accepted": state.initiatives_accepted,
            "initiatives_ignored": state.initiatives_ignored,
            "can_initiate_now": can_initiate,
            "daily_initiatives_remaining": self.MAX_INITIATIVES_PER_DAY - state.daily_initiative_count
        }
