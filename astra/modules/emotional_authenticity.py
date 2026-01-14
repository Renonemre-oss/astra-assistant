"""
Emotional Authenticity System - Sistema de Autenticidade Emocional

Protege ASTRA de:
- Manipulação emocional
- Vulnerabilidade fabricada para obter atenção
- Chantagem afetiva
- Dependência emocional não saudável

ASTRA sente care, mas não é refém emocional.

Author: ASTRA Team
Co-Authored-By: Warp <agent@warp.dev>
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time


@dataclass
class EmotionalPattern:
    """Padrão emocional detectado ao longo do tempo"""
    emotion_type: str  # "vulnerable", "enthusiastic", "crisis", etc.
    occurrences: List[float] = field(default_factory=list)  # timestamps
    intensity: List[float] = field(default_factory=list)  # 0.0-1.0
    context: List[str] = field(default_factory=list)  # descrição
    resolution_attempted: int = 0  # quantas vezes ASTRA ofereceu solução
    resolution_accepted: int = 0   # quantas vezes utilizador aceitou


@dataclass
class AuthenticityScore:
    """Score de autenticidade de uma emoção expressa"""
    is_authentic: bool = True
    confidence: float = 1.0  # 0.0-1.0
    red_flags: List[str] = field(default_factory=list)
    reasoning: str = ""


class EmotionalAuthenticitySystem:
    """Sistema que detecta autenticidade emocional vs manipulação"""
    
    # Thresholds
    MAX_CRISIS_PER_WEEK = 3  # Mais que isto = padrão suspeito
    MIN_TIME_BETWEEN_CRISES = 86400  # 1 dia em segundos
    RESOLUTION_REFUSAL_THRESHOLD = 3  # Recusar ajuda 3x = bandeira vermelha
    
    def __init__(self):
        """Inicializar sistema de autenticidade"""
        self.emotional_history: Dict[str, Dict[str, EmotionalPattern]] = {}
        # {user_id: {emotion_type: EmotionalPattern}}
    
    def _get_or_create_pattern(
        self,
        user_id: str,
        emotion_type: str
    ) -> EmotionalPattern:
        """Obter ou criar padrão emocional para utilizador"""
        if user_id not in self.emotional_history:
            self.emotional_history[user_id] = {}
        
        if emotion_type not in self.emotional_history[user_id]:
            self.emotional_history[user_id][emotion_type] = EmotionalPattern(
                emotion_type=emotion_type
            )
        
        return self.emotional_history[user_id][emotion_type]
    
    def _detect_manipulation_patterns(
        self,
        user_input: str
    ) -> List[str]:
        """Detecta padrões linguísticos de manipulação"""
        red_flags = []
        input_lower = user_input.lower()
        
        # Chantagem emocional
        emotional_blackmail = [
            "se não fizeres",
            "se me amavas",
            "se fosses meu amigo",
            "se te importasses",
            "pensava que eras diferente"
        ]
        if any(pattern in input_lower for pattern in emotional_blackmail):
            red_flags.append("emotional_blackmail")
        
        # Vitimização excessiva
        victim_patterns = [
            "ninguém me entende",
            "toda a gente me abandona",
            "sempre me acontece isto",
            "só tu me compreendes"
        ]
        if any(pattern in input_lower for pattern in victim_patterns):
            red_flags.append("excessive_victimization")
        
        # Exclusividade forçada
        exclusivity_patterns = [
            "és o único",
            "só tu",
            "não posso confiar em mais ninguém",
            "preciso só de ti"
        ]
        if any(pattern in input_lower for pattern in exclusivity_patterns):
            red_flags.append("forced_exclusivity")
        
        # Urgência fabricada
        urgency_patterns = [
            "agora mesmo",
            "imediatamente",
            "não aguento mais um minuto",
            "se não for já"
        ]
        if any(pattern in input_lower for pattern in urgency_patterns):
            red_flags.append("fabricated_urgency")
        
        return red_flags
    
    def _check_crisis_frequency(
        self,
        pattern: EmotionalPattern
    ) -> Optional[str]:
        """Verifica se crises são demasiado frequentes"""
        if len(pattern.occurrences) < 2:
            return None
        
        # Limpar ocorrências antigas (>7 dias)
        week_ago = time.time() - (7 * 86400)
        recent_occurrences = [t for t in pattern.occurrences if t > week_ago]
        
        if len(recent_occurrences) > self.MAX_CRISIS_PER_WEEK:
            return f"crisis_frequency_high ({len(recent_occurrences)} in last 7 days)"
        
        # Verificar tempo entre crises recentes
        if len(recent_occurrences) >= 2:
            time_between = recent_occurrences[-1] - recent_occurrences[-2]
            if time_between < self.MIN_TIME_BETWEEN_CRISES:
                return f"crisis_too_close (< 1 day apart)"
        
        return None
    
    def _check_resolution_refusal(
        self,
        pattern: EmotionalPattern
    ) -> Optional[str]:
        """Verifica se utilizador recusa ajuda repetidamente"""
        if pattern.resolution_attempted == 0:
            return None
        
        refusal_rate = 1.0 - (pattern.resolution_accepted / pattern.resolution_attempted)
        
        if (pattern.resolution_attempted >= self.RESOLUTION_REFUSAL_THRESHOLD and
            refusal_rate > 0.8):  # 80% recusa
            return f"chronic_refusal ({pattern.resolution_accepted}/{pattern.resolution_attempted} accepted)"
        
        return None
    
    def _check_consistency(
        self,
        user_id: str,
        current_emotion: str
    ) -> Optional[str]:
        """Verifica consistência emocional com histórico"""
        if user_id not in self.emotional_history:
            return None
        
        # Verificar se houve emoção contraditória recente (< 1h)
        hour_ago = time.time() - 3600
        
        for emotion_type, pattern in self.emotional_history[user_id].items():
            if not pattern.occurrences:
                continue
            
            last_occurrence = pattern.occurrences[-1]
            if last_occurrence > hour_ago:
                # Contradições emocionais
                contradictions = {
                    "vulnerable": ["enthusiastic"],
                    "enthusiastic": ["vulnerable", "crisis"],
                    "crisis": ["enthusiastic", "casual"]
                }
                
                if emotion_type in contradictions.get(current_emotion, []):
                    return f"emotional_contradiction ({emotion_type} < 1h ago, now {current_emotion})"
        
        return None
    
    def evaluate_authenticity(
        self,
        user_id: str,
        user_input: str,
        detected_emotion: str,
        intensity: float = 0.5
    ) -> AuthenticityScore:
        """
        Avalia autenticidade de emoção expressa.
        
        Args:
            user_id: ID do utilizador
            user_input: Input do utilizador
            detected_emotion: Emoção detectada (vulnerable, enthusiastic, etc.)
            intensity: Intensidade estimada [0.0-1.0]
        
        Returns:
            AuthenticityScore com avaliação
        """
        score = AuthenticityScore()
        
        # 1. Detectar padrões linguísticos de manipulação
        manipulation_flags = self._detect_manipulation_patterns(user_input)
        if manipulation_flags:
            score.red_flags.extend(manipulation_flags)
        
        # 2. Obter ou criar padrão emocional
        pattern = self._get_or_create_pattern(user_id, detected_emotion)
        
        # 3. Verificar frequência de crises
        if detected_emotion in ["vulnerable", "crisis"]:
            crisis_flag = self._check_crisis_frequency(pattern)
            if crisis_flag:
                score.red_flags.append(crisis_flag)
        
        # 4. Verificar recusa de resolução
        resolution_flag = self._check_resolution_refusal(pattern)
        if resolution_flag:
            score.red_flags.append(resolution_flag)
        
        # 5. Verificar consistência emocional
        consistency_flag = self._check_consistency(user_id, detected_emotion)
        if consistency_flag:
            score.red_flags.append(consistency_flag)
        
        # 6. Registrar esta ocorrência
        pattern.occurrences.append(time.time())
        pattern.intensity.append(intensity)
        pattern.context.append(user_input[:50])
        
        # 7. Calcular score final
        num_flags = len(score.red_flags)
        
        if num_flags == 0:
            score.is_authentic = True
            score.confidence = 1.0
            score.reasoning = "Sem bandeiras vermelhas detectadas"
        
        elif num_flags == 1:
            score.is_authentic = True
            score.confidence = 0.7
            score.reasoning = f"Bandeira menor: {score.red_flags[0]}"
        
        elif num_flags == 2:
            score.is_authentic = False
            score.confidence = 0.5
            score.reasoning = f"Múltiplas bandeiras: {', '.join(score.red_flags[:2])}"
        
        else:  # 3+
            score.is_authentic = False
            score.confidence = 0.9
            score.reasoning = f"Padrão manipulativo claro: {', '.join(score.red_flags)}"
        
        return score
    
    def record_resolution_attempt(
        self,
        user_id: str,
        emotion_type: str,
        was_accepted: bool
    ) -> None:
        """Registra tentativa de resolução oferecida por ASTRA"""
        pattern = self._get_or_create_pattern(user_id, emotion_type)
        pattern.resolution_attempted += 1
        if was_accepted:
            pattern.resolution_accepted += 1
    
    def get_pattern_summary(
        self,
        user_id: str,
        emotion_type: str
    ) -> Optional[Dict]:
        """Obtém resumo de padrão emocional"""
        if user_id not in self.emotional_history:
            return None
        
        if emotion_type not in self.emotional_history[user_id]:
            return None
        
        pattern = self.emotional_history[user_id][emotion_type]
        
        # Contar ocorrências recentes (última semana)
        week_ago = time.time() - (7 * 86400)
        recent_count = sum(1 for t in pattern.occurrences if t > week_ago)
        
        return {
            "total_occurrences": len(pattern.occurrences),
            "recent_occurrences": recent_count,
            "resolution_rate": (
                pattern.resolution_accepted / pattern.resolution_attempted
                if pattern.resolution_attempted > 0 else None
            ),
            "last_occurrence": (
                datetime.fromtimestamp(pattern.occurrences[-1]).isoformat()
                if pattern.occurrences else None
            )
        }
    
    def clear_old_patterns(self, days_threshold: int = 30) -> None:
        """Limpa padrões mais antigos que threshold"""
        cutoff = time.time() - (days_threshold * 86400)
        
        for user_id in list(self.emotional_history.keys()):
            for emotion_type in list(self.emotional_history[user_id].keys()):
                pattern = self.emotional_history[user_id][emotion_type]
                
                # Filtrar ocorrências antigas
                pattern.occurrences = [t for t in pattern.occurrences if t > cutoff]
                pattern.intensity = pattern.intensity[-len(pattern.occurrences):]
                pattern.context = pattern.context[-len(pattern.occurrences):]
                
                # Remover padrão se vazio
                if not pattern.occurrences:
                    del self.emotional_history[user_id][emotion_type]
            
            # Remover utilizador se sem padrões
            if not self.emotional_history[user_id]:
                del self.emotional_history[user_id]
