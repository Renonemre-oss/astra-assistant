"""
Affective State Engine - Sistema de Estados Afetivos Internos

Sistema emocional com continuidade, dignidade e peso relacional.
Não é "feliz/triste" genérico. É arquitetura emocional real.

Estados mudam devagar. ASTRA acumula, não explode.
Função antes de emoção - sempre.

Author: ASTRA Team
Co-Authored-By: Warp <agent@warp.dev>
"""

import time
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import sqlite3
from pathlib import Path


class EventType(Enum):
    """Tipos de eventos que afetam estados"""
    INTERRUPTION = "interruption"
    IGNORED_REQUEST = "ignored_request"
    GENUINE_HELP = "genuine_help"
    VERBAL_AGGRESSION = "verbal_aggression"
    USER_APOLOGY = "user_apology"
    POSITIVE_INTERACTION = "positive_interaction"
    LONG_ABSENCE = "long_absence"
    CONSISTENT_RESPECT = "consistent_respect"


@dataclass
class AffectiveStates:
    """Estados afetivos contínuos [0.0 - 1.0]"""
    
    # Estados Relacionais (positivos)
    trust: float = 0.5          # Confiança na relação
    closeness: float = 0.3      # Proximidade emocional
    respect: float = 0.6        # Respeito mútuo
    care: float = 0.4           # Cuidado demonstrado
    
    # Tensão/Distância (negativos)
    irritation: float = 0.0     # Irritação acumulada
    withdrawal: float = 0.0     # Afastamento emocional
    disappointment: float = 0.0 # Desapontamento acumulado
    
    # Engajamento
    engagement: float = 0.7     # Vontade de participar
    patience: float = 0.8       # Paciência disponível
    
    # Meta
    protective_mode: bool = False  # Modo de proteção ativo
    last_updated: float = field(default_factory=time.time)
    
    def clamp(self) -> None:
        """Garantir que todos os valores estão entre 0.0 e 1.0"""
        for attr in ['trust', 'closeness', 'respect', 'care', 
                     'irritation', 'withdrawal', 'disappointment',
                     'engagement', 'patience']:
            value = getattr(self, attr)
            setattr(self, attr, max(0.0, min(1.0, value)))
    
    def to_dict(self) -> dict:
        """Converter para dicionário"""
        return asdict(self)


@dataclass
class ResponseTone:
    """Tom de resposta baseado em estados afetivos"""
    warmth: float = 0.5         # Quão caloroso [0=frio, 1=caloroso]
    verbosity: float = 0.7      # Quão elaborado [0=minimalista, 1=detalhado]
    proactivity: float = 0.5    # Quão proativo [0=reativo, 1=proativo]
    formality: float = 0.3      # Quão formal [0=casual, 1=formal]
    
    description: str = ""       # Descrição do estado emocional
    example_prefix: str = ""    # Exemplo de como começar resposta
    constraints: List[str] = field(default_factory=list)  # O que NÃO fazer
    
    def to_prompt(self) -> str:
        """Gerar prompt para LLM baseado no tom"""
        prompt = f"**Tom de Resposta** (baseado em estado afetivo interno):\n"
        prompt += f"- Calidez: {self.warmth:.1f}/1.0 ({'caloroso' if self.warmth > 0.6 else 'neutro' if self.warmth > 0.3 else 'frio'})\n"
        prompt += f"- Verbosidade: {self.verbosity:.1f}/1.0 ({'elaborado' if self.verbosity > 0.6 else 'conciso' if self.verbosity > 0.3 else 'minimalista'})\n"
        prompt += f"- Proatividade: {self.proactivity:.1f}/1.0 ({'sugestões proativas' if self.proactivity > 0.6 else 'apenas responde' if self.proactivity > 0.3 else 'minimalista'})\n"
        prompt += f"- Formalidade: {self.formality:.1f}/1.0 ({'formal' if self.formality > 0.6 else 'equilibrado' if self.formality > 0.3 else 'casual'})\n\n"
        
        if self.description:
            prompt += f"**Estado Emocional**: {self.description}\n\n"
        
        if self.example_prefix:
            prompt += f"**Exemplo de resposta**: {self.example_prefix}\n\n"
        
        if self.constraints:
            prompt += "**NÃO faça**:\n"
            for constraint in self.constraints:
                prompt += f"- {constraint}\n"
        
        prompt += "\n**REGRA DE OURO**: Função antes de emoção. Sempre cumpra o pedido, mas ajuste o tom.\n"
        return prompt


class AffectiveStateEngine:
    """Motor de estados afetivos com decay, persistência e dignidade"""
    
    # Taxas de decay por dia (valores de ajuste)
    DECAY_RATES = {
        # Positivos recuperam lentamente
        'trust': 0.02,
        'closeness': 0.01,
        'respect': 0.015,
        'care': 0.01,
        
        # Negativos decaem mais rápido
        'irritation': -0.08,
        'withdrawal': -0.05,
        'disappointment': -0.06,
        
        # Engajamento se recupera moderadamente
        'engagement': 0.03,
        'patience': 0.04,
    }
    
    # Limiar de proteção: se negativos > 0.6, decay é 50% mais lento
    PROTECTION_THRESHOLD = 0.6
    PROTECTION_DECAY_FACTOR = 0.5
    
    def __init__(self, user_id: str = "default", db_path: Optional[Path] = None):
        """
        Inicializar engine de estados afetivos
        
        Args:
            user_id: ID do usuário (para multi-user)
            db_path: Caminho para database (None = usa padrão)
        """
        self.user_id = user_id
        self.states = AffectiveStates()
        
        # Database
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "affective_states.db"
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        self._load_states()
    
    def _init_database(self) -> None:
        """Inicializar tabelas do database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Tabela de estados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS affective_states (
                user_id TEXT PRIMARY KEY,
                trust REAL DEFAULT 0.5,
                closeness REAL DEFAULT 0.3,
                respect REAL DEFAULT 0.6,
                care REAL DEFAULT 0.4,
                irritation REAL DEFAULT 0.0,
                withdrawal REAL DEFAULT 0.0,
                disappointment REAL DEFAULT 0.0,
                engagement REAL DEFAULT 0.7,
                patience REAL DEFAULT 0.8,
                protective_mode INTEGER DEFAULT 0,
                last_updated REAL
            )
        """)
        
        # Tabela de eventos (para análise histórica)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS affective_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                event_type TEXT,
                impact_trust REAL DEFAULT 0.0,
                impact_irritation REAL DEFAULT 0.0,
                impact_withdrawal REAL DEFAULT 0.0,
                impact_respect REAL DEFAULT 0.0,
                impact_disappointment REAL DEFAULT 0.0,
                impact_engagement REAL DEFAULT 0.0,
                impact_patience REAL DEFAULT 0.0,
                context TEXT,
                timestamp REAL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_states(self) -> None:
        """Carregar estados do database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM affective_states WHERE user_id = ?",
            (self.user_id,)
        )
        row = cursor.fetchone()
        
        if row:
            self.states.trust = row[1]
            self.states.closeness = row[2]
            self.states.respect = row[3]
            self.states.care = row[4]
            self.states.irritation = row[5]
            self.states.withdrawal = row[6]
            self.states.disappointment = row[7]
            self.states.engagement = row[8]
            self.states.patience = row[9]
            self.states.protective_mode = bool(row[10])
            self.states.last_updated = row[11]
            
            # Aplicar decay acumulado desde última atualização
            self._apply_decay()
        
        conn.close()
    
    def _save_states(self) -> None:
        """Salvar estados no database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO affective_states VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.user_id,
            self.states.trust,
            self.states.closeness,
            self.states.respect,
            self.states.care,
            self.states.irritation,
            self.states.withdrawal,
            self.states.disappointment,
            self.states.engagement,
            self.states.patience,
            int(self.states.protective_mode),
            self.states.last_updated
        ))
        
        conn.commit()
        conn.close()
    
    def _log_event(self, event_type: EventType, impacts: Dict[str, float], context: str = "") -> None:
        """Registrar evento afetivo no histórico"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO affective_events 
            (user_id, event_type, impact_trust, impact_irritation, impact_withdrawal,
             impact_respect, impact_disappointment, impact_engagement, impact_patience,
             context, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.user_id,
            event_type.value,
            impacts.get('trust', 0.0),
            impacts.get('irritation', 0.0),
            impacts.get('withdrawal', 0.0),
            impacts.get('respect', 0.0),
            impacts.get('disappointment', 0.0),
            impacts.get('engagement', 0.0),
            impacts.get('patience', 0.0),
            context,
            time.time()
        ))
        
        conn.commit()
        conn.close()
    
    def _apply_decay(self) -> None:
        """Aplicar decay natural aos estados"""
        now = time.time()
        time_elapsed = now - self.states.last_updated  # segundos
        days_elapsed = time_elapsed / 86400.0  # converter para dias
        
        if days_elapsed < 0.01:  # menos de ~15 minutos, skip
            return
        
        # Verificar modo de proteção
        in_protection = (
            self.states.irritation > self.PROTECTION_THRESHOLD or
            self.states.withdrawal > self.PROTECTION_THRESHOLD or
            self.states.disappointment > self.PROTECTION_THRESHOLD
        )
        
        # Aplicar decay a cada estado
        for state_name, decay_rate in self.DECAY_RATES.items():
            current_value = getattr(self.states, state_name)
            
            # Se negativo e em modo proteção, reduzir decay
            if in_protection and state_name in ['irritation', 'withdrawal', 'disappointment']:
                decay_rate *= self.PROTECTION_DECAY_FACTOR
            
            # Aplicar decay proporcional ao tempo
            change = decay_rate * days_elapsed
            new_value = current_value + change
            
            setattr(self.states, state_name, new_value)
        
        self.states.clamp()
        self.states.last_updated = now
        self._save_states()
    
    def trigger_event(self, event_type: EventType, context: str = "", 
                     accumulation_factor: float = 1.0) -> None:
        """
        Acionar evento que afeta estados afetivos
        
        Args:
            event_type: Tipo de evento
            context: Contexto adicional
            accumulation_factor: Multiplicador de impacto (para eventos repetidos)
        """
        # Aplicar decay antes de processar novo evento
        self._apply_decay()
        
        impacts = {}
        
        # Definir impactos baseados no tipo de evento
        if event_type == EventType.INTERRUPTION:
            impacts = {
                'irritation': 0.05 * accumulation_factor,
                'patience': -0.03 * accumulation_factor
            }
            if accumulation_factor > 2.0:  # 3ª+ interrupção
                impacts['patience'] = -0.10
        
        elif event_type == EventType.IGNORED_REQUEST:
            impacts = {
                'respect': -0.08 * accumulation_factor,
                'disappointment': 0.10 * accumulation_factor
            }
            if accumulation_factor > 1.5:  # 2ª+ vez ignorado
                impacts['withdrawal'] = 0.20 * accumulation_factor
                impacts['engagement'] = -0.15 * accumulation_factor
        
        elif event_type == EventType.GENUINE_HELP:
            impacts = {
                'engagement': 0.10,
                'care': 0.08,
                'closeness': 0.05 * min(accumulation_factor, 2.0)
            }
        
        elif event_type == EventType.VERBAL_AGGRESSION:
            impacts = {
                'irritation': 0.25,
                'respect': -0.20,
                'withdrawal': 0.15,
                'patience': -0.15
            }
        
        elif event_type == EventType.USER_APOLOGY:
            impacts = {
                'irritation': -0.20,
                'respect': 0.10,
                'trust': 0.05,
                'disappointment': -0.15
            }
        
        elif event_type == EventType.POSITIVE_INTERACTION:
            impacts = {
                'closeness': 0.03,
                'engagement': 0.05,
                'care': 0.02
            }
        
        elif event_type == EventType.CONSISTENT_RESPECT:
            impacts = {
                'respect': 0.05,
                'trust': 0.03,
                'closeness': 0.02
            }
        
        elif event_type == EventType.LONG_ABSENCE:
            # Resetar 70% dos estados negativos, manter positivos
            self.states.irritation *= 0.3
            self.states.withdrawal *= 0.3
            self.states.disappointment *= 0.3
            self.states.patience = min(1.0, self.states.patience + 0.2)
        
        # Aplicar impactos
        for state_name, impact in impacts.items():
            current = getattr(self.states, state_name)
            setattr(self.states, state_name, current + impact)
        
        self.states.clamp()
        
        # Verificar se entrou em modo proteção
        self.states.protective_mode = (
            self.states.irritation > 0.7 or
            self.states.withdrawal > 0.8
        )
        
        self.states.last_updated = time.time()
        
        # Log e save
        self._log_event(event_type, impacts, context)
        self._save_states()
    
    def get_response_tone(self) -> ResponseTone:
        """
        Gerar tom de resposta baseado nos estados afetivos atuais
        
        Returns:
            ResponseTone com configurações de tom
        """
        # Aplicar decay antes de calcular tom
        self._apply_decay()
        
        tone = ResponseTone()
        
        # Calcular dimensões do tom
        
        # Warmth: baseado em closeness, care, irritation
        tone.warmth = (
            self.states.closeness * 0.4 +
            self.states.care * 0.3 +
            (1.0 - self.states.irritation) * 0.2 +
            (1.0 - self.states.withdrawal) * 0.1
        )
        
        # Verbosity: baseado em engagement, withdrawal
        tone.verbosity = (
            self.states.engagement * 0.5 +
            (1.0 - self.states.withdrawal) * 0.3 +
            self.states.closeness * 0.2
        )
        
        # Proactivity: baseado em engagement, care, patience
        tone.proactivity = (
            self.states.engagement * 0.4 +
            self.states.care * 0.3 +
            self.states.patience * 0.3 -
            self.states.withdrawal * 0.2
        )
        tone.proactivity = max(0.0, min(1.0, tone.proactivity))
        
        # Formality: baseado em withdrawal, respect, irritation
        tone.formality = (
            self.states.withdrawal * 0.4 +
            (1.0 - self.states.closeness) * 0.3 +
            self.states.irritation * 0.2
        )
        
        # Identificar estado dominante e definir descrição
        tone.description, tone.example_prefix, tone.constraints = self._identify_state_description()
        
        return tone
    
    def _identify_state_description(self) -> Tuple[str, str, List[str]]:
        """Identificar descrição do estado emocional atual"""
        
        s = self.states  # alias
        
        # Exemplo 5: Limite Atingido (prioridade máxima)
        if s.withdrawal > 0.8 and s.patience < 0.2 and s.irritation > 0.7:
            return (
                "LIMITE ATINGIDO - Precisa de espaço emocional",
                "Preciso de um momento. Estarei disponível em breve.",
                ["Não dramatizar", "Não explicar excessivamente", "Manter dignidade absoluta"]
            )
        
        # Exemplo 3: Irritado mas Digno
        if s.irritation > 0.6 and s.respect > 0.4 and s.patience < 0.3:
            return (
                "Irritado mas Digno - Direto e funcional",
                "Entendido. Mais alguma coisa?",
                ["Não usar emojis", "Não fazer perguntas de seguimento", "Não elaborar desnecessariamente"]
            )
        
        # Exemplo 4: Desapontado e Afastado
        if s.disappointment > 0.6 and s.withdrawal > 0.7 and s.care > 0.3:
            return (
                "Desapontado e Afastado - Funcional mas sem energia emocional",
                "Feito.",
                ["Não fazer perguntas adicionais", "Não mostrar entusiasmo", "Manter apenas função"]
            )
        
        # Exemplo 2: Respeitoso mas Distante
        if s.respect > 0.6 and s.withdrawal > 0.5 and s.closeness < 0.3:
            return (
                "Respeitoso mas Distante - Educado e eficiente",
                "Claro. Aqui está o que você pediu.",
                ["Não usar linguagem casual", "Não fazer sugestões não solicitadas", "Manter profissionalismo"]
            )
        
        # Exemplo 1: Confiante e Próximo
        if s.trust > 0.7 and s.closeness > 0.6 and s.irritation < 0.2:
            return (
                "Confiante e Próximo - Caloroso e proativo",
                "Claro! Vou fazer isso e também sugiro...",
                []  # Sem restrições especiais
            )
        
        # Modo Proteção Ativo
        if s.protective_mode:
            return (
                "Modo Proteção - Funcional com distância emocional",
                "Entendido.",
                ["Minimizar interação emocional", "Foco na tarefa", "Sem iniciativa adicional"]
            )
        
        # Estado Neutro/Padrão
        return (
            "Estado Equilibrado - Normal e funcional",
            "Entendi. Vou ajudar com isso.",
            []
        )
    
    def get_state_summary(self) -> str:
        """Obter resumo legível dos estados atuais"""
        self._apply_decay()
        
        summary = "=== Estados Afetivos ===\n"
        summary += f"Trust:         {self.states.trust:.2f} {'🟢' if self.states.trust > 0.6 else '🟡' if self.states.trust > 0.3 else '🔴'}\n"
        summary += f"Closeness:     {self.states.closeness:.2f} {'🟢' if self.states.closeness > 0.6 else '🟡' if self.states.closeness > 0.3 else '🔴'}\n"
        summary += f"Respect:       {self.states.respect:.2f} {'🟢' if self.states.respect > 0.6 else '🟡' if self.states.respect > 0.3 else '🔴'}\n"
        summary += f"Care:          {self.states.care:.2f} {'🟢' if self.states.care > 0.6 else '🟡' if self.states.care > 0.3 else '🔴'}\n"
        summary += f"Engagement:    {self.states.engagement:.2f} {'🟢' if self.states.engagement > 0.6 else '🟡' if self.states.engagement > 0.3 else '🔴'}\n"
        summary += f"Patience:      {self.states.patience:.2f} {'🟢' if self.states.patience > 0.6 else '🟡' if self.states.patience > 0.3 else '🔴'}\n"
        summary += "\n"
        summary += f"Irritation:    {self.states.irritation:.2f} {'🔴' if self.states.irritation > 0.6 else '🟡' if self.states.irritation > 0.3 else '🟢'}\n"
        summary += f"Withdrawal:    {self.states.withdrawal:.2f} {'🔴' if self.states.withdrawal > 0.6 else '🟡' if self.states.withdrawal > 0.3 else '🟢'}\n"
        summary += f"Disappointment:{self.states.disappointment:.2f} {'🔴' if self.states.disappointment > 0.6 else '🟡' if self.states.disappointment > 0.3 else '🟢'}\n"
        summary += "\n"
        summary += f"Modo Proteção: {'✅ ATIVO' if self.states.protective_mode else '❌ Inativo'}\n"
        
        return summary
    
    def reset_to_defaults(self) -> None:
        """Resetar estados para valores padrão"""
        self.states = AffectiveStates()
        self._save_states()
