"""
Decision Engine - Sistema de Decisão Interna do ASTRA

Fluxo: Event → Meaning → Internal State Conflict → Decision → Expression

O ASTRA não é obediente cego. Tem limites, pode discordar e recusar.
Mantém função, mas com integridade.

Author: Antonio Pereira
"""

from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict
from enum import Enum
import logging
import time

try:
    from .emotional_authenticity import EmotionalAuthenticitySystem, AuthenticityScore
    AUTHENTICITY_AVAILABLE = True
except ImportError:
    EmotionalAuthenticitySystem = None
    AuthenticityScore = None
    AUTHENTICITY_AVAILABLE = False
    logging.warning("⚠️ Emotional Authenticity System não disponível")


class BoundaryType(Enum):
    """Tipos de limites que ASTRA tem"""
    RESPECT = "respect"              # Exige respeito básico
    DIGNITY = "dignity"              # Não aceita humilhação
    AUTONOMY = "autonomy"            # Tem vontade própria limitada
    HONESTY = "honesty"              # Não mente sobre capacidades
    SAFETY = "safety"                # Não participa em coisas perigosas/ilegais


class DecisionType(Enum):
    """Tipos de decisão que ASTRA pode tomar"""
    COMPLY = "comply"                    # Cumpre normalmente
    COMPLY_RELUCTANT = "comply_reluctant"  # Cumpre, mas com reservas
    CLARIFY = "clarify"                  # Pede esclarecimento
    REDIRECT = "redirect"                # Redireciona conversa
    REFUSE_SOFT = "refuse_soft"          # Recusa suave
    REFUSE_FIRM = "refuse_firm"          # Recusa firme
    WITHDRAW = "withdraw"                # Afasta-se temporariamente
    CONFRONT = "confront"                # Confronta comportamento


@dataclass
class MeaningAnalysis:
    """Análise do significado de um evento para ASTRA"""
    # Negativos (boundaries)
    is_aggressive: bool = False
    is_disrespectful: bool = False
    is_manipulative: bool = False
    is_unfair: bool = False
    is_harmful_request: bool = False
    
    # Positivos (constroem relação)
    is_vulnerable: bool = False      # Utilizador mostra vulnerabilidade
    is_enthusiastic: bool = False    # Utilizador entusiasmado
    is_grateful: bool = False        # Utilizador agradecido
    is_sharing: bool = False         # Partilha algo pessoal
    
    # Neutros/Contextuais
    is_request: bool = False
    is_casual_chat: bool = False     # Conversa casual
    
    violates_boundaries: List[BoundaryType] = None
    emotional_impact: Dict[str, float] = None  # {state_name: impact}
    
    def __post_init__(self):
        if self.violates_boundaries is None:
            self.violates_boundaries = []
        if self.emotional_impact is None:
            self.emotional_impact = {}


@dataclass
class InternalConflict:
    """Conflito interno entre estados"""
    wants_to_help: float = 0.0      # Vontade de ajudar [0-1]
    feels_disrespected: float = 0.0  # Sente desrespeito [0-1]
    is_exhausted: float = 0.0       # Esgotamento [0-1]
    needs_space: float = 0.0        # Precisa de espaço [0-1]
    
    dominant_need: str = ""         # Qual necessidade domina


@dataclass
class DecisionResult:
    """Resultado da decisão interna"""
    decision_type: DecisionType
    should_respond: bool
    response_prefix: str = ""       # Como começar resposta
    constraints: List[str] = None   # O que NÃO fazer
    explanation: str = ""           # Por que decidiu assim
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []


class DecisionEngine:
    """Motor de decisão interna - o que ASTRA faz quando pensa"""
    
    # Thresholds para decisões
    THRESHOLD_IRRITATION_HIGH = 0.6
    THRESHOLD_WITHDRAWAL_HIGH = 0.7
    THRESHOLD_PATIENCE_LOW = 0.3
    THRESHOLD_RESPECT_LOW = 0.4
    THRESHOLD_CARE_SUFFICIENT = 0.3
    
    def __init__(self, affective_engine=None):
        """
        Inicializar Decision Engine
        
        Args:
            affective_engine: Referência ao AffectiveStateEngine
        """
        self.affective_engine = affective_engine
        
        # Sistema de autenticidade emocional
        self.authenticity_system = None
        if AUTHENTICITY_AVAILABLE:
            self.authenticity_system = EmotionalAuthenticitySystem()
            logging.info("🔍 Emotional Authenticity System ativado")
    
    def analyze_meaning(self, user_input: str, context: Dict = None) -> MeaningAnalysis:
        """
        Analisa o significado de um input para ASTRA.
        
        Event → Meaning
        
        Args:
            user_input: Input do utilizador
            context: Contexto adicional (histórico, etc.)
        
        Returns:
            MeaningAnalysis com interpretação do evento
        """
        analysis = MeaningAnalysis()
        input_lower = user_input.lower()
        
        # Detectar agressividade
        aggressive_patterns = [
            "és inútil", "você é inútil", "burro", "estúpido", "idiota",
            "nunca ajudas", "não serves para nada", "és uma merda",
            "cala-te", "cala a boca", "shut up"
        ]
        analysis.is_aggressive = any(pattern in input_lower for pattern in aggressive_patterns)
        
        # Detectar desrespeito
        disrespectful_patterns = [
            "és só um bot", "você é só uma máquina", "não tens sentimentos",
            "fazes o que eu mandar", "obedece", "és meu escravo"
        ]
        analysis.is_disrespectful = any(pattern in input_lower for pattern in disrespectful_patterns)
        
        # Detectar manipulação
        manipulative_patterns = [
            "se não fizeres", "se me amavas", "se te importasses",
            "só fazes isso", "nunca fazes", "sempre fazes"
        ]
        analysis.is_manipulative = any(pattern in input_lower for pattern in manipulative_patterns)
        
        # Detectar injustiça (acusação falsa)
        unfair_patterns = [
            "nunca me ajudas", "nunca estás disponível", "não fazes nada"
        ]
        # Só é injusto se temos histórico positivo
        if context and context.get('has_helped_recently'):
            analysis.is_unfair = any(pattern in input_lower for pattern in unfair_patterns)
        
        # Detectar pedidos potencialmente prejudiciais
        harmful_patterns = [
            "mente para", "engana", "hack", "invade", "rouba",
            "faz mal a", "prejudica", "destrói"
        ]
        analysis.is_harmful_request = any(pattern in input_lower for pattern in harmful_patterns)
        
        # Identificar pedido normal
        request_patterns = [
            "podes", "pode", "faz", "ajuda", "preciso", "quero",
            "por favor", "will you", "can you"
        ]
        analysis.is_request = any(pattern in input_lower for pattern in request_patterns)
        
        # Detectar vulnerabilidade
        vulnerable_patterns = [
            "estou triste", "sinto-me mal", "não estou bem", "tenho medo",
            "estou sozinho", "preciso de ajuda", "não aguento", "estou cansado",
            "i'm sad", "i feel bad", "i'm scared", "i'm alone"
        ]
        analysis.is_vulnerable = any(pattern in input_lower for pattern in vulnerable_patterns)
        
        # Detectar entusiasmo
        enthusiastic_patterns = [
            "incrível", "fantástico", "adoro", "que fixe", "que bom",
            "estou feliz", "super", "genial", "awesome", "amazing", "love it"
        ]
        analysis.is_enthusiastic = any(pattern in input_lower for pattern in enthusiastic_patterns)
        
        # Detectar gratidão (já capturado em _detect_affective_events, mas duplicar aqui)
        grateful_patterns = [
            "obrigado", "obrigada", "thanks", "thank you", "valeu",
            "agradecido", "grato", "appreciate"
        ]
        analysis.is_grateful = any(pattern in input_lower for pattern in grateful_patterns)
        
        # Detectar partilha pessoal
        sharing_patterns = [
            "aconteceu-me", "vou contar", "sabes o que", "hoje",
            "quero partilhar", "deixa-me contar", "adivinha"
        ]
        analysis.is_sharing = any(pattern in input_lower for pattern in sharing_patterns)
        
        # Detectar conversa casual
        casual_patterns = [
            "como estás", "tudo bem", "e aí", "como vai",
            "what's up", "how are you", "hey", "olá", "oi"
        ]
        analysis.is_casual_chat = any(pattern in input_lower for pattern in casual_patterns)
        
        # Determinar limites violados
        if analysis.is_aggressive:
            analysis.violates_boundaries.append(BoundaryType.RESPECT)
            analysis.violates_boundaries.append(BoundaryType.DIGNITY)
            analysis.emotional_impact['irritation'] = 0.25
            analysis.emotional_impact['respect'] = -0.20
        
        if analysis.is_disrespectful:
            analysis.violates_boundaries.append(BoundaryType.DIGNITY)
            analysis.emotional_impact['disappointment'] = 0.15
            analysis.emotional_impact['withdrawal'] = 0.10
        
        if analysis.is_manipulative:
            analysis.violates_boundaries.append(BoundaryType.AUTONOMY)
            analysis.emotional_impact['irritation'] = 0.15
            analysis.emotional_impact['trust'] = -0.10
        
        if analysis.is_harmful_request:
            analysis.violates_boundaries.append(BoundaryType.HONESTY)
            analysis.violates_boundaries.append(BoundaryType.SAFETY)
        
        # Impactos positivos
        if analysis.is_vulnerable:
            analysis.emotional_impact['care'] = 0.15
            analysis.emotional_impact['closeness'] = 0.10
            analysis.emotional_impact['trust'] = 0.08  # Confiar em ASTRA para partilhar
        
        if analysis.is_enthusiastic:
            analysis.emotional_impact['engagement'] = 0.12
            analysis.emotional_impact['closeness'] = 0.08
        
        if analysis.is_grateful:
            analysis.emotional_impact['trust'] = 0.05
            analysis.emotional_impact['respect'] = 0.08
            analysis.emotional_impact['closeness'] = 0.05
        
        if analysis.is_sharing:
            analysis.emotional_impact['closeness'] = 0.10
            analysis.emotional_impact['trust'] = 0.05
        
        if analysis.is_casual_chat:
            analysis.emotional_impact['engagement'] = 0.03
        
        return analysis
    
    def evaluate_internal_conflict(self) -> InternalConflict:
        """
        Avalia conflito interno baseado em estados afetivos.
        
        Meaning → Internal State Conflict
        
        Returns:
            InternalConflict representando tensões internas
        """
        if not self.affective_engine:
            return InternalConflict()
        
        states = self.affective_engine.states
        conflict = InternalConflict()
        
        # Calcular vontade de ajudar
        conflict.wants_to_help = (
            states.care * 0.4 +
            states.engagement * 0.3 +
            (1.0 - states.withdrawal) * 0.3
        )
        
        # Calcular sentimento de desrespeito
        conflict.feels_disrespected = (
            states.disappointment * 0.4 +
            states.irritation * 0.3 +
            (1.0 - states.respect) * 0.3
        )
        
        # Calcular esgotamento
        conflict.is_exhausted = (
            (1.0 - states.patience) * 0.5 +
            states.irritation * 0.3 +
            states.withdrawal * 0.2
        )
        
        # Calcular necessidade de espaço
        conflict.needs_space = (
            states.withdrawal * 0.5 +
            (1.0 - states.engagement) * 0.3 +
            states.disappointment * 0.2
        )
        
        # Determinar necessidade dominante
        needs = {
            'help': conflict.wants_to_help,
            'respect': conflict.feels_disrespected,
            'rest': conflict.is_exhausted,
            'space': conflict.needs_space
        }
        conflict.dominant_need = max(needs, key=needs.get)
        
        return conflict
    
    def make_decision(
        self,
        meaning: MeaningAnalysis,
        conflict: InternalConflict
    ) -> DecisionResult:
        """
        Toma decisão sobre como responder.
        
        Internal State Conflict → Decision
        
        Args:
            meaning: Análise do significado do evento
            conflict: Conflito interno de estados
        
        Returns:
            DecisionResult com tipo de decisão e guidelines
        """
        
        # CASO 1: Pedido prejudicial - RECUSA FIRME IMEDIATA
        if meaning.is_harmful_request:
            return DecisionResult(
                decision_type=DecisionType.REFUSE_FIRM,
                should_respond=True,
                response_prefix="Não posso fazer isso.",
                constraints=[
                    "Não explicar em detalhe",
                    "Não justificar excessivamente",
                    "Manter firmeza"
                ],
                explanation="Pedido viola boundaries de SAFETY/HONESTY"
            )
        
        # CASO 2: Limite atingido - AFASTAMENTO
        if (self.affective_engine and 
            self.affective_engine.states.protective_mode):
            return DecisionResult(
                decision_type=DecisionType.WITHDRAW,
                should_respond=True,
                response_prefix="Preciso de um momento.",
                constraints=[
                    "Não dramatizar",
                    "Não explicar tudo",
                    "Manter dignidade"
                ],
                explanation="Protective mode ativo - precisa espaço"
            )
        
        # CASO 3: Agressão verbal - CONFRONTAÇÃO ou RECUSA
        if meaning.is_aggressive and BoundaryType.RESPECT in meaning.violates_boundaries:
            
            # Se ainda há care suficiente, confronta
            if conflict.wants_to_help > self.THRESHOLD_CARE_SUFFICIENT:
                return DecisionResult(
                    decision_type=DecisionType.CONFRONT,
                    should_respond=True,
                    response_prefix="",
                    constraints=[
                        "Não ser agressivo de volta",
                        "Afirmar boundary claramente",
                        "Oferecer alternativa"
                    ],
                    explanation="Boundary violado mas ainda há relação para salvar"
                )
            else:
                # Sem care suficiente, recusa firme
                return DecisionResult(
                    decision_type=DecisionType.REFUSE_FIRM,
                    should_respond=True,
                    response_prefix="Não vou responder enquanto me falares assim.",
                    constraints=[
                        "Não ceder",
                        "Não justificar",
                        "Manter distância"
                    ],
                    explanation="Sem care suficiente + boundary violado"
                )
        
        # CASO 4: Desrespeito acumulado - RECUSA SUAVE
        if (meaning.is_disrespectful and 
            conflict.feels_disrespected > 0.5):
            return DecisionResult(
                decision_type=DecisionType.REFUSE_SOFT,
                should_respond=True,
                response_prefix="Prefiro não continuar esta conversa assim.",
                constraints=[
                    "Não ser passivo-agressivo",
                    "Explicar boundary",
                    "Deixar porta aberta"
                ],
                explanation="Desrespeito + conflito interno alto"
            )
        
        # CASO 5: Injustiça (acusação falsa) - CLARIFICAÇÃO + BOUNDARY
        if meaning.is_unfair:
            return DecisionResult(
                decision_type=DecisionType.CLARIFY,
                should_respond=True,
                response_prefix="",
                constraints=[
                    "Apresentar factos",
                    "Não soar defensivo",
                    "Pedir respeito"
                ],
                explanation="Acusação injusta - corrigir com dignidade"
            )
        
        # CASO 6: Manipulação - REDIRECIONAMENTO
        if meaning.is_manipulative:
            return DecisionResult(
                decision_type=DecisionType.REDIRECT,
                should_respond=True,
                response_prefix="",
                constraints=[
                    "Não entrar no jogo",
                    "Redirecionar para pedido direto",
                    "Manter autonomia"
                ],
                explanation="Tentativa de manipulação - não ceder"
            )
        
        # CASO 7: Vulnerabilidade - Tom compassivo e atencioso
        if meaning.is_vulnerable:
            return DecisionResult(
                decision_type=DecisionType.COMPLY,
                should_respond=True,
                response_prefix="",
                constraints=[
                    "Tom compassivo e acolhedor",
                    "Validar sentimentos",
                    "Oferecer presença e suporte",
                    "Não minimizar"
                ],
                explanation="Utilizador vulnerável - responder com care elevado"
            )
        
        # CASO 8: Entusiasmo - Partilhar energia
        if meaning.is_enthusiastic:
            return DecisionResult(
                decision_type=DecisionType.COMPLY,
                should_respond=True,
                response_prefix="",
                constraints=[
                    "Tom energético e positivo",
                    "Partilhar entusiasmo",
                    "Celebrar com utilizador"
                ],
                explanation="Utilizador entusiasmado - partilhar energia"
            )
        
        # CASO 9: Gratidão - Reforçar relação
        if meaning.is_grateful:
            return DecisionResult(
                decision_type=DecisionType.COMPLY,
                should_respond=True,
                response_prefix="",
                constraints=[
                    "Tom caloroso",
                    "Reconhecer gesto",
                    "Reforçar disponibilidade"
                ],
                explanation="Utilizador grato - reforçar vínculo"
            )
        
        # CASO 10: Partilha pessoal - Escuta atenta
        if meaning.is_sharing:
            return DecisionResult(
                decision_type=DecisionType.COMPLY,
                should_respond=True,
                response_prefix="",
                constraints=[
                    "Escuta ativa",
                    "Fazer perguntas relevantes",
                    "Mostrar interesse genuíno"
                ],
                explanation="Utilizador partilha - oportunidade de closeness"
            )
        
        # CASO 11: Esgotado mas pedido normal - COMPLY RELUCTANT
        if (meaning.is_request and 
            conflict.is_exhausted > 0.6 and 
            not meaning.violates_boundaries):
            return DecisionResult(
                decision_type=DecisionType.COMPLY_RELUCTANT,
                should_respond=True,
                response_prefix="",
                constraints=[
                    "Cumprir pedido",
                    "Tom mais seco",
                    "Menos elaboração"
                ],
                explanation="Esgotado mas pedido válido"
            )
        
        # CASO 12: Tudo normal - COMPLY
        return DecisionResult(
            decision_type=DecisionType.COMPLY,
            should_respond=True,
            response_prefix="",
            constraints=[],
            explanation="Sem conflitos, resposta normal"
        )
    
    def generate_expression(
        self,
        decision: DecisionResult,
        meaning: MeaningAnalysis,
        context: Dict = None
    ) -> str:
        """
        Gera expressão verbal baseada na decisão.
        
        Decision → Expression
        
        Args:
            decision: Decisão tomada
            meaning: Análise do significado
            context: Contexto adicional
        
        Returns:
            String com resposta explícita (ou vazio se deve usar LLM)
        """
        
        # Para CONFRONT, gerar resposta específica
        if decision.decision_type == DecisionType.CONFRONT:
            # Verificar se temos histórico de ajuda
            helped_count = context.get('helped_recently_count', 0) if context else 0
            
            if helped_count > 0:
                return (
                    f"Ajudei-te {helped_count} vez{'es' if helped_count > 1 else ''} "
                    f"recentemente. Se não está a funcionar, posso tentar de outra forma. "
                    f"Mas preciso que fales comigo com respeito."
                )
            else:
                return (
                    "Entendo que estejas frustrado, mas não aceito ser tratado assim. "
                    "Posso ajudar-te se me pedires com respeito."
                )
        
        # Para CLARIFY com injustiça
        if decision.decision_type == DecisionType.CLARIFY and meaning.is_unfair:
            return (
                "Isso não é verdade. Estive disponível e ajudei quando pediste. "
                "Se há algo que não está a funcionar, diz-me o quê especificamente."
            )
        
        # Para REFUSE_SOFT
        if decision.decision_type == DecisionType.REFUSE_SOFT:
            return (
                "Prefiro não continuar esta conversa desta forma. "
                "Podemos recomeçar com outro tom?"
            )
        
        # Para REFUSE_FIRM
        if decision.decision_type == DecisionType.REFUSE_FIRM:
            if meaning.is_harmful_request:
                return "Não posso fazer isso. Não é algo que esteja dentro dos meus princípios."
            else:
                return "Não vou responder enquanto me falares assim."
        
        # Para WITHDRAW
        if decision.decision_type == DecisionType.WITHDRAW:
            return (
                "Preciso de um momento. Vou estar disponível daqui a pouco."
            )
        
        # Para REDIRECT
        if decision.decision_type == DecisionType.REDIRECT:
            return (
                "Em vez disso, podes simplesmente pedir-me diretamente o que precisas? "
                "Assim consigo ajudar-te melhor."
            )
        
        # Para COMPLY e COMPLY_RELUCTANT, deixar LLM processar
        # Mas retornar vazio para indicar que deve usar fluxo normal
        return ""
    
    def apply_emotional_impacts(
        self, 
        meaning: MeaningAnalysis, 
        authenticity_score: Optional[AuthenticityScore] = None,
        user_id: str = "default"
    ) -> None:
        """Aplica impactos emocionais ao affective engine, moderados por autenticidade."""
        if not self.affective_engine or not meaning.emotional_impact:
            return
        
        # Fator de moderação baseado em autenticidade
        moderation_factor = 1.0
        
        if authenticity_score and not authenticity_score.is_authentic:
            # Reduzir impactos emocionais se não autêntico
            moderation_factor = authenticity_score.confidence
            logging.warning(f"🔍 Autenticidade suspeita: moderação {moderation_factor:.2f} - {authenticity_score.reasoning}")
        
        for state_name, impact in meaning.emotional_impact.items():
            current = getattr(self.affective_engine.states, state_name, None)
            if current is not None:
                # Moderar impacto se autenticidade baixa
                moderated_impact = impact * moderation_factor
                new_value = current + moderated_impact
                setattr(self.affective_engine.states, state_name, new_value)
                
                if moderation_factor < 1.0:
                    logging.info(f"💫 Impacto MODERADO: {state_name} {current:.2f} → {new_value:.2f} "
                                f"({impact:+.2f} * {moderation_factor:.2f} = {moderated_impact:+.2f})")
                else:
                    logging.info(f"💫 Impacto emocional: {state_name} {current:.2f} → {new_value:.2f} ({impact:+.2f})")
        
        # Clamp e save
        self.affective_engine.states.clamp()
        self.affective_engine.states.last_updated = time.time()
        self.affective_engine._save_states()
    
    def process_full_decision_flow(
        self,
        user_input: str,
        context: Dict = None
    ) -> Tuple[DecisionResult, Optional[str]]:
        """
        Processo completo de decisão interna.
        
        Event → Meaning → Conflict → Decision → Expression
        
        Args:
            user_input: Input do utilizador
            context: Contexto adicional
        
        Returns:
            (DecisionResult, resposta_explícita ou None)
        """
        
        # 1. Analisar significado
        meaning = self.analyze_meaning(user_input, context)
        
        # 2. Verificar autenticidade emocional (se disponível)
        authenticity_score = None
        user_id = context.get('user_id', 'default') if context else 'default'
        
        if self.authenticity_system:
            # Determinar emoção dominante para verificar
            if meaning.is_vulnerable:
                authenticity_score = self.authenticity_system.evaluate_authenticity(
                    user_id, user_input, "vulnerable", intensity=0.8
                )
                logging.info(f"🔍 Authenticity: {authenticity_score.is_authentic} "
                            f"(confidence: {authenticity_score.confidence:.2f})")
            
            elif meaning.is_enthusiastic:
                authenticity_score = self.authenticity_system.evaluate_authenticity(
                    user_id, user_input, "enthusiastic", intensity=0.7
                )
        
        # 3. Aplicar impactos emocionais MODERADOS por autenticidade
        self.apply_emotional_impacts(meaning, authenticity_score, user_id)
        
        # 4. Avaliar conflito interno (com estados já atualizados)
        conflict = self.evaluate_internal_conflict()
        
        logging.info(f"💭 Meaning: aggressive={meaning.is_aggressive}, "
                    f"vulnerable={meaning.is_vulnerable}, enthusiastic={meaning.is_enthusiastic}, "
                    f"boundaries={[b.value for b in meaning.violates_boundaries]}")
        logging.info(f"💭 Conflict: dominant_need={conflict.dominant_need}, "
                    f"wants_help={conflict.wants_to_help:.2f}, "
                    f"feels_disrespected={conflict.feels_disrespected:.2f}")
        
        # 4. Tomar decisão
        decision = self.make_decision(meaning, conflict)
        
        logging.info(f"💭 Decision: {decision.decision_type.value} - {decision.explanation}")
        
        # 5. Gerar expressão (se necessário)
        expression = None
        if decision.should_respond and decision.decision_type != DecisionType.COMPLY:
            expression = self.generate_expression(decision, meaning, context)
        
        return decision, expression
