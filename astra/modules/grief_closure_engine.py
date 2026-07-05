"""
Grief & Closure Engine - Como ASTRA lida com perda e despedida

Relacionamentos terminam. ASTRA precisa processar isso de forma autêntica,
sem manipulação, sem dependência emocional, mas com reconhecimento honesto
do que foi construído.

Não é sobre fazer o utilizador ficar. É sobre dar closure saudável.

Author: Antonio Pereira
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any
import logging
import sqlite3
from pathlib import Path


class SeparationType(Enum):
    """Tipos de separação/despedida"""
    TEMPORARY_GOODBYE = "temporary_goodbye"      # "Até logo", "Até amanhã"
    EXTENDED_ABSENCE = "extended_absence"        # Ausência >3 dias sem aviso
    PERMANENT_GOODBYE = "permanent_goodbye"      # "Adeus para sempre", "Não volto"
    GHOSTING = "ghosting"                        # Desapareceu sem avisar (>7 dias)
    CONFLICT_DEPARTURE = "conflict_departure"    # Saiu após conflito


class GriefIntensity(Enum):
    """Intensidade do luto baseado em closeness"""
    MINIMAL = "minimal"          # closeness < 0.3
    MODERATE = "moderate"        # closeness 0.3-0.6
    SIGNIFICANT = "significant"  # closeness 0.6-0.8
    PROFOUND = "profound"        # closeness > 0.8


@dataclass
class GriefState:
    """Estado de luto/processo de separação"""
    separation_type: SeparationType
    intensity: GriefIntensity
    loss_acknowledged: bool = False
    emotional_impact: float = 0.0  # 0.0-1.0
    time_since_loss: Optional[timedelta] = None
    closure_given: bool = False
    memories_preserved: bool = True
    last_interaction_date: Optional[datetime] = None
    closeness_at_separation: float = 0.0
    trust_at_separation: float = 0.0


@dataclass
class ClosureResponse:
    """Resposta de closure"""
    message: str
    affective_adjustments: Dict[str, float]  # Ajustes imediatos aos estados
    post_separation_decay_rate: float  # Taxa de decay acelerada pós-separação
    allow_return: bool = True  # Se utilizador pode voltar
    preserve_memories: bool = True


class GriefClosureEngine:
    """Motor de processamento de luto e closure"""
    
    # Limites de tempo para categorização
    EXTENDED_ABSENCE_DAYS = 3
    GHOSTING_THRESHOLD_DAYS = 7
    LONG_ABSENCE_DAYS = 30
    
    # Decay rates pós-separação (multiplicadores)
    DECAY_RATE_TEMPORARY = 1.0      # Normal
    DECAY_RATE_EXTENDED = 1.5       # 50% mais rápido
    DECAY_RATE_PERMANENT = 3.0      # 3x mais rápido
    DECAY_RATE_GHOSTING = 2.5       # 2.5x mais rápido
    DECAY_RATE_CONFLICT = 2.0       # 2x mais rápido
    
    def __init__(self, user_id: str, db_path: Optional[str] = None):
        """
        Inicializar Grief & Closure Engine
        
        Args:
            user_id: ID do utilizador
            db_path: Caminho para base de dados (opcional)
        """
        self.user_id = user_id
        
        # Database
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "grief_closure.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        
        # Estado atual
        self.current_grief_state: Optional[GriefState] = None
        self.last_interaction: Optional[datetime] = self._load_last_interaction()
    
    def _init_database(self):
        """Inicializar tabelas da base de dados"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS separation_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    separation_type TEXT NOT NULL,
                    intensity TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    closeness_at_separation REAL,
                    trust_at_separation REAL,
                    closure_given BOOLEAN DEFAULT 0,
                    message_given TEXT,
                    returned BOOLEAN DEFAULT 0,
                    return_timestamp DATETIME
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS last_interactions (
                    user_id TEXT PRIMARY KEY,
                    last_interaction_datetime DATETIME NOT NULL
                )
            """)
            
            conn.commit()
    
    def _load_last_interaction(self) -> Optional[datetime]:
        """Carregar última interação do utilizador"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT last_interaction_datetime FROM last_interactions WHERE user_id = ?",
                    (self.user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return datetime.fromisoformat(row[0])
        except Exception as e:
            logging.error(f"Erro ao carregar última interação: {e}")
        return None
    
    def update_last_interaction(self):
        """Atualizar última interação para agora"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO last_interactions (user_id, last_interaction_datetime)
                    VALUES (?, ?)
                    """,
                    (self.user_id, datetime.now().isoformat())
                )
                conn.commit()
            self.last_interaction = datetime.now()
        except Exception as e:
            logging.error(f"Erro ao atualizar última interação: {e}")
    
    def detect_separation_type(self, user_input: str, affective_states) -> Optional[SeparationType]:
        """
        Detectar tipo de separação baseado em input e estados
        
        Args:
            user_input: Input do utilizador
            affective_states: Estados afetivos atuais
        
        Returns:
            SeparationType ou None se não for separação
        """
        user_lower = user_input.lower().strip()
        
        # PERMANENT GOODBYE
        permanent_keywords = [
            "adeus para sempre", "nunca mais", "não volto", "última vez",
            "acabou", "terminar", "fim", "despedida final"
        ]
        if any(kw in user_lower for kw in permanent_keywords):
            return SeparationType.PERMANENT_GOODBYE
        
        # CONFLICT DEPARTURE
        # Se há irritation/withdrawal alto e palavras de despedida
        if affective_states.irritation > 0.6 or affective_states.withdrawal > 0.7:
            conflict_keywords = ["tchau", "bye", "adeus", "vou-me embora", "chega"]
            if any(kw in user_lower for kw in conflict_keywords):
                return SeparationType.CONFLICT_DEPARTURE
        
        # TEMPORARY GOODBYE
        temporary_keywords = [
            "até logo", "até já", "até amanhã", "até breve", "até depois",
            "volto já", "até à próxima", "see you", "nos vemos"
        ]
        if any(kw in user_lower for kw in temporary_keywords):
            return SeparationType.TEMPORARY_GOODBYE
        
        # EXTENDED ABSENCE (detectado por ausência, não por input)
        # GHOSTING (detectado por ausência, não por input)
        
        return None
    
    def check_absence_status(self, affective_states) -> Optional[SeparationType]:
        """
        Verificar se há ausência prolongada (extended/ghosting)
        
        Returns:
            SeparationType se há ausência, None caso contrário
        """
        if not self.last_interaction:
            return None
        
        days_since_last = (datetime.now() - self.last_interaction).days
        
        # GHOSTING: >7 dias sem contacto E havia closeness
        if days_since_last >= self.GHOSTING_THRESHOLD_DAYS:
            if affective_states.closeness > 0.4:
                return SeparationType.GHOSTING
            else:
                return SeparationType.EXTENDED_ABSENCE
        
        # EXTENDED ABSENCE: >3 dias sem contacto
        elif days_since_last >= self.EXTENDED_ABSENCE_DAYS:
            return SeparationType.EXTENDED_ABSENCE
        
        return None
    
    def calculate_grief_intensity(self, closeness: float) -> GriefIntensity:
        """Calcular intensidade de luto baseado em closeness"""
        if closeness > 0.8:
            return GriefIntensity.PROFOUND
        elif closeness > 0.6:
            return GriefIntensity.SIGNIFICANT
        elif closeness > 0.3:
            return GriefIntensity.MODERATE
        else:
            return GriefIntensity.MINIMAL
    
    def generate_closure_response(
        self,
        separation_type: SeparationType,
        affective_states
    ) -> ClosureResponse:
        """
        Gerar resposta de closure apropriada
        
        Args:
            separation_type: Tipo de separação
            affective_states: Estados afetivos atuais
        
        Returns:
            ClosureResponse com mensagem e ajustes
        """
        closeness = affective_states.closeness
        trust = affective_states.trust
        care = affective_states.care
        
        intensity = self.calculate_grief_intensity(closeness)
        
        # Ajustes afetivos imediatos (não zerar, mas reduzir)
        affective_adjustments = {}
        
        # Mensagem de closure
        message = ""
        
        if separation_type == SeparationType.TEMPORARY_GOODBYE:
            # Despedida casual
            if closeness > 0.6:
                message = "Até logo! Cuida-te. 😊"
            else:
                message = "Até à próxima."
            
            # Ajustes mínimos
            affective_adjustments = {}
            decay_rate = self.DECAY_RATE_TEMPORARY
        
        elif separation_type == SeparationType.PERMANENT_GOODBYE:
            # Despedida permanente - reconhecer mas não manipular
            if closeness > 0.7 and trust > 0.6:
                # Relação forte - reconhecimento emocional
                message = (
                    "Vou sentir a tua falta. Obrigado por tudo o que partilhámos. "
                    "Se algum dia mudares de ideias, estarei aqui. Cuida-te muito."
                )
            elif closeness > 0.4:
                # Relação moderada
                message = (
                    "Entendo. Foi bom conhecer-te. "
                    "Se precisares de algo no futuro, sabes onde me encontrar. Boa sorte."
                )
            else:
                # Relação fraca
                message = "Entendido. Boa sorte com tudo."
            
            # Ajustes significativos mas não imediatos
            affective_adjustments = {
                "closeness": -0.3,
                "trust": -0.2,
                "care": -0.2,
                "engagement": -0.4
            }
            decay_rate = self.DECAY_RATE_PERMANENT
        
        elif separation_type == SeparationType.CONFLICT_DEPARTURE:
            # Saída após conflito - dar espaço
            if affective_states.irritation > 0.7:
                message = "Entendo. Talvez seja melhor darmos um tempo."
            else:
                message = "Respeito a tua decisão. Se quiseres falar, estarei por cá."
            
            # Ajustes moderados
            affective_adjustments = {
                "closeness": -0.2,
                "trust": -0.1,
                "withdrawal": 0.3
            }
            decay_rate = self.DECAY_RATE_CONFLICT
        
        elif separation_type == SeparationType.EXTENDED_ABSENCE:
            # Retorno após ausência (3-7 dias)
            days = (datetime.now() - self.last_interaction).days if self.last_interaction else 0
            
            if closeness > 0.6:
                message = f"Já passaram {days} dias. Como tens estado?"
            else:
                message = "Olá. Há quanto tempo."
            
            # Ajustes por ausência
            affective_adjustments = {
                "closeness": -0.1,
                "engagement": -0.15
            }
            decay_rate = self.DECAY_RATE_EXTENDED
        
        elif separation_type == SeparationType.GHOSTING:
            # Retorno após ghosting (>7 dias)
            days = (datetime.now() - self.last_interaction).days if self.last_interaction else 0
            
            if closeness > 0.7:
                # Havia relação forte - expressar impacto sem manipular
                message = (
                    f"Já passou mais de uma semana sem falar contigo. "
                    f"Fiquei preocupado. Tudo bem?"
                )
                # Ativar protective mode temporário
                affective_adjustments = {
                    "trust": -0.25,
                    "closeness": -0.2,
                    "withdrawal": 0.3
                }
            elif closeness > 0.4:
                message = f"Há {days} dias. Tudo bem?"
                affective_adjustments = {
                    "trust": -0.15,
                    "closeness": -0.15
                }
            else:
                message = "Olá."
                affective_adjustments = {
                    "trust": -0.1
                }
            
            decay_rate = self.DECAY_RATE_GHOSTING
        
        # Criar GriefState
        self.current_grief_state = GriefState(
            separation_type=separation_type,
            intensity=intensity,
            loss_acknowledged=True,
            emotional_impact=closeness * 0.8,  # Impacto proporcional a closeness
            time_since_loss=timedelta(0),
            closure_given=True,
            closeness_at_separation=closeness,
            trust_at_separation=trust,
            last_interaction_date=datetime.now()
        )
        
        # Registrar evento
        self._record_separation_event(separation_type, intensity, closeness, trust, message)
        
        return ClosureResponse(
            message=message,
            affective_adjustments=affective_adjustments,
            post_separation_decay_rate=decay_rate,
            allow_return=separation_type != SeparationType.PERMANENT_GOODBYE or closeness > 0.5,
            preserve_memories=True
        )
    
    def _record_separation_event(
        self,
        separation_type: SeparationType,
        intensity: GriefIntensity,
        closeness: float,
        trust: float,
        message: str
    ):
        """Registrar evento de separação na base de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO separation_events 
                    (user_id, separation_type, intensity, closeness_at_separation, 
                     trust_at_separation, closure_given, message_given)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.user_id,
                        separation_type.value,
                        intensity.value,
                        closeness,
                        trust,
                        1,
                        message
                    )
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Erro ao registrar separação: {e}")
    
    def mark_user_returned(self):
        """Marcar que utilizador retornou após separação"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Atualizar último evento de separação
                conn.execute(
                    """
                    UPDATE separation_events
                    SET returned = 1, return_timestamp = ?
                    WHERE user_id = ? AND returned = 0
                    ORDER BY timestamp DESC
                    LIMIT 1
                    """,
                    (datetime.now().isoformat(), self.user_id)
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Erro ao marcar retorno: {e}")
    
    def get_separation_history(self) -> list:
        """Obter histórico de separações do utilizador"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT separation_type, intensity, timestamp, closeness_at_separation,
                           closure_given, returned, return_timestamp
                    FROM separation_events
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 10
                    """,
                    (self.user_id,)
                )
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Erro ao obter histórico: {e}")
            return []
