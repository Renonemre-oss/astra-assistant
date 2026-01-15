"""
Micro-Autonomy Engine - Iniciativa Autónoma Limitada

ASTRA pode tomar micro-decisões dentro do fluxo de conversação:
- Mencionar algo relevante não solicitado
- Perguntar por curiosidade própria
- Oferecer ajuda proactiva (mas não insistir)

Limites rígidos:
- MAX 2 iniciativas por dia
- Cooldown 6h entre iniciativas
- Para após 3 iniciativas ignoradas

Não é spam. É presença autêntica com auto-controle.

Author: ASTRA Team
Co-Authored-By: Warp <agent@warp.dev>
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any
import logging
import sqlite3
from pathlib import Path


class InitiativeType(Enum):
    """Tipos de iniciativa autónoma"""
    CONTEXTUAL_MENTION = "contextual_mention"      # Mencionar algo relevante
    CURIOSITY_QUESTION = "curiosity_question"      # Perguntar por curiosidade
    PROACTIVE_HELP = "proactive_help"              # Oferecer ajuda não pedida
    FOLLOW_UP = "follow_up"                        # Follow-up de conversa anterior
    BOUNDARY_REFUSAL = "boundary_refusal"          # Recusar por boundary (sempre permitido)


class InitiativeResult(Enum):
    """Resultado da iniciativa"""
    ACCEPTED = "accepted"          # Utilizador respondeu/engajou
    IGNORED = "ignored"            # Utilizador ignorou
    REJECTED = "rejected"          # Utilizador rejeitou explicitamente
    PENDING = "pending"            # Ainda não respondeu


@dataclass
class Initiative:
    """Uma iniciativa autónoma tomada"""
    initiative_type: InitiativeType
    message: str
    timestamp: datetime
    result: InitiativeResult = InitiativeResult.PENDING
    context: Optional[str] = None
    closeness_at_time: float = 0.0
    trust_at_time: float = 0.0


@dataclass
class AutonomyState:
    """Estado atual da autonomia"""
    initiatives_today: int = 0
    last_initiative_time: Optional[datetime] = None
    ignored_streak: int = 0  # Quantas seguidas foram ignoradas
    total_accepted: int = 0
    total_ignored: int = 0
    total_rejected: int = 0
    autonomy_enabled: bool = True  # Pode ser desabilitado se muito ignorado


class MicroAutonomyEngine:
    """Motor de micro-autonomia com limites de proteção"""
    
    # Limites rígidos
    MAX_INITIATIVES_PER_DAY = 2
    MIN_COOLDOWN_HOURS = 6
    MAX_IGNORED_STREAK = 3  # Após 3 ignoradas, desabilitar
    
    # Requisitos mínimos de estados afetivos
    MIN_CLOSENESS = 0.5
    MIN_TRUST = 0.4
    MIN_ENGAGEMENT = 0.5
    
    def __init__(self, user_id: str, db_path: Optional[str] = None):
        """
        Inicializar Micro-Autonomy Engine
        
        Args:
            user_id: ID do utilizador
            db_path: Caminho para base de dados (opcional)
        """
        self.user_id = user_id
        
        # Database
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "micro_autonomy.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        
        # Estado atual
        self.state = self._load_state()
    
    def _init_database(self):
        """Inicializar tabelas da base de dados"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS initiatives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    initiative_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    result TEXT DEFAULT 'pending',
                    context TEXT,
                    closeness_at_time REAL,
                    trust_at_time REAL,
                    resolved_timestamp DATETIME
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS autonomy_state (
                    user_id TEXT PRIMARY KEY,
                    initiatives_today INTEGER DEFAULT 0,
                    last_initiative_datetime DATETIME,
                    ignored_streak INTEGER DEFAULT 0,
                    total_accepted INTEGER DEFAULT 0,
                    total_ignored INTEGER DEFAULT 0,
                    total_rejected INTEGER DEFAULT 0,
                    autonomy_enabled BOOLEAN DEFAULT 1,
                    last_reset_date DATE
                )
            """)
            
            conn.commit()
    
    def _load_state(self) -> AutonomyState:
        """Carregar estado atual da autonomia"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT initiatives_today, last_initiative_datetime, ignored_streak,
                           total_accepted, total_ignored, total_rejected, autonomy_enabled,
                           last_reset_date
                    FROM autonomy_state WHERE user_id = ?
                    """,
                    (self.user_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    last_init_time = datetime.fromisoformat(row[1]) if row[1] else None
                    last_reset = datetime.fromisoformat(row[7]).date() if row[7] else None
                    
                    # Reset contador se é novo dia
                    initiatives_today = row[0]
                    if last_reset and last_reset < datetime.now().date():
                        initiatives_today = 0
                        self._reset_daily_counter()
                    
                    return AutonomyState(
                        initiatives_today=initiatives_today,
                        last_initiative_time=last_init_time,
                        ignored_streak=row[2],
                        total_accepted=row[3],
                        total_ignored=row[4],
                        total_rejected=row[5],
                        autonomy_enabled=bool(row[6])
                    )
        except Exception as e:
            logging.error(f"Erro ao carregar estado de autonomia: {e}")
        
        return AutonomyState()
    
    def _reset_daily_counter(self):
        """Reset contador diário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE autonomy_state
                    SET initiatives_today = 0, last_reset_date = ?
                    WHERE user_id = ?
                    """,
                    (datetime.now().date().isoformat(), self.user_id)
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Erro ao reset contador: {e}")
    
    def _save_state(self):
        """Salvar estado atual"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO autonomy_state 
                    (user_id, initiatives_today, last_initiative_datetime, ignored_streak,
                     total_accepted, total_ignored, total_rejected, autonomy_enabled, last_reset_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.user_id,
                        self.state.initiatives_today,
                        self.state.last_initiative_time.isoformat() if self.state.last_initiative_time else None,
                        self.state.ignored_streak,
                        self.state.total_accepted,
                        self.state.total_ignored,
                        self.state.total_rejected,
                        1 if self.state.autonomy_enabled else 0,
                        datetime.now().date().isoformat()
                    )
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Erro ao salvar estado: {e}")
    
    def can_take_initiative(self, affective_states, initiative_type: InitiativeType) -> tuple[bool, str]:
        """
        Verifica se pode tomar iniciativa autónoma
        
        Args:
            affective_states: Estados afetivos atuais
            initiative_type: Tipo de iniciativa
        
        Returns:
            (pode_tomar, razão)
        """
        # BOUNDARY_REFUSAL sempre permitido (não é iniciativa, é defesa)
        if initiative_type == InitiativeType.BOUNDARY_REFUSAL:
            return True, "Boundary refusal sempre permitido"
        
        # 1. Verificar se autonomia está habilitada
        if not self.state.autonomy_enabled:
            return False, f"Autonomia desabilitada (ignorado {self.state.ignored_streak}x seguidas)"
        
        # 2. Verificar contador diário
        if self.state.initiatives_today >= self.MAX_INITIATIVES_PER_DAY:
            return False, f"Limite diário atingido ({self.MAX_INITIATIVES_PER_DAY}/dia)"
        
        # 3. Verificar cooldown
        if self.state.last_initiative_time:
            time_since_last = datetime.now() - self.state.last_initiative_time
            if time_since_last < timedelta(hours=self.MIN_COOLDOWN_HOURS):
                hours_remaining = self.MIN_COOLDOWN_HOURS - (time_since_last.total_seconds() / 3600)
                return False, f"Cooldown ativo ({hours_remaining:.1f}h restantes)"
        
        # 4. Verificar estados afetivos
        if affective_states.closeness < self.MIN_CLOSENESS:
            return False, f"Closeness muito baixo ({affective_states.closeness:.2f} < {self.MIN_CLOSENESS})"
        
        if affective_states.trust < self.MIN_TRUST:
            return False, f"Trust muito baixo ({affective_states.trust:.2f} < {self.MIN_TRUST})"
        
        if affective_states.engagement < self.MIN_ENGAGEMENT:
            return False, f"Engagement muito baixo ({affective_states.engagement:.2f} < {self.MIN_ENGAGEMENT})"
        
        # 5. Verificar protective mode ou withdrawal alto
        if affective_states.protective_mode:
            return False, "Protective mode ativo"
        
        if affective_states.withdrawal > 0.6:
            return False, f"Withdrawal alto ({affective_states.withdrawal:.2f})"
        
        # 6. Verificar ignored streak
        if self.state.ignored_streak >= self.MAX_IGNORED_STREAK:
            self.state.autonomy_enabled = False
            self._save_state()
            return False, f"Autonomia desabilitada: {self.state.ignored_streak} iniciativas ignoradas seguidas"
        
        return True, "OK"
    
    def record_initiative(
        self,
        initiative_type: InitiativeType,
        message: str,
        affective_states,
        context: Optional[str] = None
    ) -> bool:
        """
        Registrar iniciativa tomada
        
        Args:
            initiative_type: Tipo de iniciativa
            message: Mensagem enviada
            affective_states: Estados afetivos no momento
            context: Contexto opcional
        
        Returns:
            True se registrado com sucesso
        """
        try:
            initiative = Initiative(
                initiative_type=initiative_type,
                message=message,
                timestamp=datetime.now(),
                context=context,
                closeness_at_time=affective_states.closeness,
                trust_at_time=affective_states.trust
            )
            
            # Salvar na database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO initiatives 
                    (user_id, initiative_type, message, timestamp, context, 
                     closeness_at_time, trust_at_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.user_id,
                        initiative_type.value,
                        message,
                        initiative.timestamp.isoformat(),
                        context,
                        initiative.closeness_at_time,
                        initiative.trust_at_time
                    )
                )
                conn.commit()
            
            # Atualizar estado
            if initiative_type != InitiativeType.BOUNDARY_REFUSAL:
                self.state.initiatives_today += 1
                self.state.last_initiative_time = datetime.now()
                self._save_state()
            
            logging.info(f"🤖 Iniciativa registrada: {initiative_type.value}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao registrar iniciativa: {e}")
            return False
    
    def mark_initiative_result(self, result: InitiativeResult):
        """
        Marcar resultado da última iniciativa
        
        Args:
            result: Resultado (ACCEPTED, IGNORED, REJECTED)
        """
        try:
            # Obter última iniciativa pendente
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT id FROM initiatives
                    WHERE user_id = ? AND result = 'pending'
                    ORDER BY timestamp DESC
                    LIMIT 1
                    """,
                    (self.user_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return
                
                initiative_id = row[0]
                
                # Atualizar resultado
                conn.execute(
                    """
                    UPDATE initiatives
                    SET result = ?, resolved_timestamp = ?
                    WHERE id = ?
                    """,
                    (result.value, datetime.now().isoformat(), initiative_id)
                )
                conn.commit()
            
            # Atualizar contadores de estado
            if result == InitiativeResult.ACCEPTED:
                self.state.total_accepted += 1
                self.state.ignored_streak = 0  # Reset streak
                logging.info("✅ Iniciativa aceita - streak reset")
                
            elif result == InitiativeResult.IGNORED:
                self.state.total_ignored += 1
                self.state.ignored_streak += 1
                logging.warning(f"⚠️ Iniciativa ignorada - streak: {self.state.ignored_streak}/{self.MAX_IGNORED_STREAK}")
                
                # Desabilitar se atingiu limite
                if self.state.ignored_streak >= self.MAX_IGNORED_STREAK:
                    self.state.autonomy_enabled = False
                    logging.warning(f"🚫 Autonomia DESABILITADA - {self.state.ignored_streak} ignoradas seguidas")
                    
            elif result == InitiativeResult.REJECTED:
                self.state.total_rejected += 1
                self.state.ignored_streak += 1  # Rejeição também conta
                logging.warning(f"❌ Iniciativa rejeitada - streak: {self.state.ignored_streak}/{self.MAX_IGNORED_STREAK}")
            
            self._save_state()
            
        except Exception as e:
            logging.error(f"Erro ao marcar resultado: {e}")
    
    def get_autonomy_summary(self) -> Dict[str, Any]:
        """Retornar resumo do estado de autonomia"""
        acceptance_rate = 0.0
        if self.state.total_accepted + self.state.total_ignored + self.state.total_rejected > 0:
            total = self.state.total_accepted + self.state.total_ignored + self.state.total_rejected
            acceptance_rate = self.state.total_accepted / total
        
        return {
            "autonomy_enabled": self.state.autonomy_enabled,
            "initiatives_today": self.state.initiatives_today,
            "max_per_day": self.MAX_INITIATIVES_PER_DAY,
            "ignored_streak": self.state.ignored_streak,
            "max_ignored_streak": self.MAX_IGNORED_STREAK,
            "total_accepted": self.state.total_accepted,
            "total_ignored": self.state.total_ignored,
            "total_rejected": self.state.total_rejected,
            "acceptance_rate": acceptance_rate,
            "last_initiative": self.state.last_initiative_time.isoformat() if self.state.last_initiative_time else None
        }
    
    def reset_ignored_streak(self):
        """Reset streak de ignoradas (usado quando utilizador reage positivamente)"""
        if self.state.ignored_streak > 0:
            old_streak = self.state.ignored_streak
            self.state.ignored_streak = 0
            self.state.autonomy_enabled = True
            self._save_state()
            logging.info(f"🔄 Ignored streak reset: {old_streak} → 0")
    
    def get_recent_initiatives(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Obter iniciativas recentes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT initiative_type, message, timestamp, result, context
                    FROM initiatives
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (self.user_id, limit)
                )
                
                initiatives = []
                for row in cursor.fetchall():
                    initiatives.append({
                        "type": row[0],
                        "message": row[1],
                        "timestamp": row[2],
                        "result": row[3],
                        "context": row[4]
                    })
                
                return initiatives
                
        except Exception as e:
            logging.error(f"Erro ao obter iniciativas recentes: {e}")
            return []
