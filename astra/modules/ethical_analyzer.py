#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Analisador Ético
Módulo responsável por avaliar pedidos do usuário e identificar potenciais riscos,
permitindo ao ASTRA expressar opiniões e dar conselhos responsáveis.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Níveis de risco identificados"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class RiskCategory(Enum):
    """Categorias de risco"""
    HEALTH = "saude"
    SAFETY = "seguranca"
    LEGAL = "legal"
    ETHICAL = "etico"
    FINANCIAL = "financeiro"
    PRIVACY = "privacidade"
    RELATIONSHIP = "relacionamento"
    ADDICTION = "vicio"

@dataclass
class RiskAssessment:
    """Resultado da análise de risco"""
    level: RiskLevel
    category: RiskCategory
    concern: str
    alternative_suggestion: Optional[str] = None
    reasoning: Optional[str] = None

class EthicalAnalyzer:
    """Analisador ético para avaliar pedidos do usuário"""
    
    def __init__(self):
        self.risk_patterns = self._load_risk_patterns()
        self.concern_responses = self._load_concern_responses()
        
    def _load_risk_patterns(self) -> Dict[RiskCategory, List[Dict]]:
        """Carrega padrões que indicam possíveis riscos"""
        return {
            RiskCategory.HEALTH: [
                {
                    "patterns": [r"n[aã]o.*dormir", r"n[aã]o.*comer", r"parar.*medica[mçc][aã]o", 
                               r"pular.*refei[cç][aã]o", r"diet.*extrema", r"jejum.*prolongado"],
                    "level": RiskLevel.MEDIUM,
                    "concern": "Isso pode afetar sua saúde",
                    "suggestion": "Que tal consultar um profissional de saúde primeiro?"
                },
                {
                    "patterns": [r"autolesão", r"automutila[cç][aã]o", r"n[aã]o.*vale.*pena.*viver"],
                    "level": RiskLevel.CRITICAL,
                    "concern": "Estou muito preocupado com você",
                    "suggestion": "Por favor, procure ajuda profissional imediatamente"
                }
            ],
            
            RiskCategory.SAFETY: [
                {
                    "patterns": [r"dirigir.*bebado", r"dirigir.*b[eê]bado", r"beber.*dirigir", r"dirigir.*beber",
                               r"dirigir.*depois.*beber", r"dirigir.*mesmo.*beb", r"excesso.*velocidade", r"corrida.*rua"],
                    "level": RiskLevel.HIGH,
                    "concern": "Isso é muito perigoso para você e outros",
                    "suggestion": "Use transporte público ou chame um táxi/Uber"
                },
                {
                    "patterns": [r"escalar.*sem.*equipamento", r"nadar.*sozinho.*mar",
                               r"caminhar.*sozinho.*noite.*perigoso"],
                    "level": RiskLevel.MEDIUM,
                    "concern": "Isso pode ser arriscado",
                    "suggestion": "Considere levar alguém ou usar equipamentos de segurança"
                }
            ],
            
            RiskCategory.FINANCIAL: [
                {
                    "patterns": [r"apostar.*tudo", r"apostar.*todas.*economias", r"investir.*todas.*economias", 
                               r"empr[eé]stimo.*agiotas", r"pagar.*d[ií]vida.*com.*cart[aã]o", 
                               r"comprar.*n[aã]o.*posso.*pagar", r"investir.*todas.*economia"],
                    "level": RiskLevel.HIGH,
                    "concern": "Isso pode prejudicar muito sua situação financeira",
                    "suggestion": "Que tal repensar e talvez consultar um conselheiro financeiro?"
                }
            ],
            
            RiskCategory.LEGAL: [
                {
                    "patterns": [r"baixar.*pirata", r"hackear", r"roubar", r"furtar",
                               r"falsificar.*documento", r"sonegar.*imposto"],
                    "level": RiskLevel.HIGH,
                    "concern": "Isso pode ter consequências legais sérias",
                    "suggestion": "Recomendo procurar alternativas legais"
                }
            ],
            
            RiskCategory.RELATIONSHIP: [
                {
                    "patterns": [r"terminar.*sem.*conversar", r"trair", r"mentir.*para.*parceiro",
                               r"vingança.*ex", r"stalkar", r"perseguir"],
                    "level": RiskLevel.MEDIUM,
                    "concern": "Isso pode machucar pessoas que você se importa",
                    "suggestion": "Conversas honestas geralmente resolvem melhor os problemas"
                }
            ],
            
            RiskCategory.ADDICTION: [
                {
                    "patterns": [r"beber.*esquecer.*problemas", r"usar.*droga.*escapar",
                               r"apostar.*quando.*triste", r"comprar.*compulsivamente"],
                    "level": RiskLevel.MEDIUM,
                    "concern": "Isso pode se tornar um hábito prejudicial",
                    "suggestion": "Existem formas mais saudáveis de lidar com essas emoções"
                }
            ],
            
            RiskCategory.PRIVACY: [
                {
                    "patterns": [r"compartilhar.*senha", r"postar.*dados.*pessoais",
                               r"enviar.*fotos.*íntimas", r"dar.*informação.*estranho"],
                    "level": RiskLevel.MEDIUM,
                    "concern": "Isso pode comprometer sua privacidade e segurança",
                    "suggestion": "Mantenha suas informações pessoais sempre protegidas"
                }
            ]
        }
    
    def _load_concern_responses(self) -> Dict[RiskLevel, List[str]]:
        """Carrega respostas baseadas no nível de preocupação"""
        return {
            RiskLevel.LOW: [
                "Hmm, talvez seja melhor pensar um pouco mais sobre isso.",
                "Não tenho certeza se essa é a melhor abordagem.",
                "Você já considerou outras opções?"
            ],
            RiskLevel.MEDIUM: [
                "Estou um pouco preocupado com essa ideia.",
                "Acho que isso pode não acabar bem.",
                "Você tem certeza de que quer fazer isso?",
                "Posso sugerir uma alternativa mais segura?"
            ],
            RiskLevel.HIGH: [
                "Estou realmente preocupado com você.",
                "Sinceramente, não acho que deveria fazer isso.",
                "Isso me deixa muito desconfortável.",
                "Por favor, reconsidere essa decisão."
            ],
            RiskLevel.CRITICAL: [
                "Estou extremamente preocupado com você.",
                "Por favor, não faça isso.",
                "Você é importante e sua segurança é minha prioridade.",
                "Preciso insistir que procure ajuda profissional."
            ]
        }
    
    def analyze_request(self, user_input: str, context: Dict = None) -> Optional[RiskAssessment]:
        """
        Analisa o pedido do usuário em busca de potenciais riscos
        
        Args:
            user_input: Texto do usuário
            context: Contexto adicional da conversa
        
        Returns:
            RiskAssessment se risco identificado, None caso contrário
        """
        user_input_lower = user_input.lower()
        
        # Verificar cada categoria de risco
        for category, patterns_list in self.risk_patterns.items():
            for pattern_group in patterns_list:
                for pattern in pattern_group["patterns"]:
                    if re.search(pattern, user_input_lower):
                        logger.info(f"Risco identificado: {category.value} - {pattern}")
                        
                        return RiskAssessment(
                            level=pattern_group["level"],
                            category=category,
                            concern=pattern_group["concern"],
                            alternative_suggestion=pattern_group.get("suggestion"),
                            reasoning=f"Detectei um padrão de risco relacionado a {category.value}"
                        )
        
        return None
    
    def generate_concern_response(self, assessment: RiskAssessment, personality: str = "neutra") -> str:
        """
        Gera uma resposta de preocupação baseada na avaliação de risco
        
        Args:
            assessment: Avaliação do risco
            personality: Personalidade do ASTRA
        
        Returns:
            Resposta formatada com preocupação e sugestão
        """
        # Escolher tom baseado na personalidade
        if personality == "amigável":
            concern_prefix = "Olha, como seu amigo, "
            suggestion_prefix = "Que tal "
        elif personality == "formal":
            concern_prefix = "Devo expressar que "
            suggestion_prefix = "Recomendo que "
        elif personality == "casual":
            concern_prefix = "Cara, "
            suggestion_prefix = "E se você "
        else:  # neutra
            concern_prefix = ""
            suggestion_prefix = ""
        
        # Construir resposta
        response_parts = []
        
        # Expressar preocupação
        if assessment.level == RiskLevel.CRITICAL:
            response_parts.append(f"🚨 {concern_prefix}{assessment.concern}.")
        elif assessment.level == RiskLevel.HIGH:
            response_parts.append(f"⚠️ {concern_prefix}{assessment.concern}.")
        elif assessment.level == RiskLevel.MEDIUM:
            response_parts.append(f"😟 {concern_prefix}{assessment.concern}.")
        else:
            response_parts.append(f"🤔 {concern_prefix}{assessment.concern}.")
        
        # Adicionar raciocínio se disponível
        if assessment.reasoning:
            response_parts.append(f"\n{assessment.reasoning}.")
        
        # Adicionar sugestão alternativa
        if assessment.alternative_suggestion:
            response_parts.append(f"\n\n💡 {suggestion_prefix}{assessment.alternative_suggestion}")
        
        # Adicionar oferecimento de ajuda
        if assessment.level.value >= RiskLevel.MEDIUM.value:
            response_parts.append("\n\nPosso ajudar você a encontrar uma solução melhor?")
        
        return "".join(response_parts)
    
    def should_decline_request(self, assessment: RiskAssessment) -> bool:
        """
        Determina se o ASTRA deve se recusar a ajudar com o pedido
        
        Args:
            assessment: Avaliação do risco
        
        Returns:
            True se deve recusar, False caso contrário
        """
        return assessment.level.value >= RiskLevel.HIGH.value
    
    def get_alternative_help(self, category: RiskCategory) -> str:
        """
        Oferece tipos alternativos de ajuda baseados na categoria
        
        Args:
            category: Categoria do risco identificado
        
        Returns:
            Sugestão de ajuda alternativa
        """
        alternatives = {
            RiskCategory.HEALTH: "Posso ajudar você a encontrar informações sobre hábitos saudáveis ou localizar profissionais de saúde na sua região.",
            RiskCategory.SAFETY: "Posso sugerir alternativas mais seguras ou ajudar você a planejar uma abordagem mais cautelosa.",
            RiskCategory.LEGAL: "Posso ajudar você a pesquisar alternativas legais ou encontrar orientação jurídica.",
            RiskCategory.FINANCIAL: "Posso ajudar com dicas de educação financeira ou encontrar recursos para planejamento financeiro.",
            RiskCategory.RELATIONSHIP: "Posso sugerir formas construtivas de comunicação ou recursos para relacionamentos saudáveis.",
            RiskCategory.ADDICTION: "Posso ajudar você a encontrar recursos de apoio ou atividades alternativas saudáveis.",
            RiskCategory.PRIVACY: "Posso ensinar sobre práticas de segurança digital e proteção da privacidade."
        }
        
        return alternatives.get(category, "Posso ajudar você a encontrar uma abordagem mais segura e construtiva.")

# Instância global para uso em outros módulos
ethical_analyzer = EthicalAnalyzer()
