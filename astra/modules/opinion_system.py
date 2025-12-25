#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Sistema de Opinião
Módulo que permite ao ALEX expressar opiniões, preocupações e dar conselhos
de forma proativa e responsável.
"""

import logging
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .ethical_analyzer import ethical_analyzer, RiskAssessment, RiskLevel, RiskCategory

logger = logging.getLogger(__name__)

class OpinionSystem:
    """Sistema de opinião do ALEX"""
    
    def __init__(self):
        self.concern_history = []  # Histórico de preocupações expressas
        self.positive_reinforcements = self._load_positive_reinforcements()
        self.gentle_disagreements = self._load_gentle_disagreements()
        
    def _load_positive_reinforcements(self) -> Dict[str, List[str]]:
        """Reforços positivos para quando o usuário toma boas decisões"""
        return {
            "health": [
                "Que ótima escolha! Cuidar da saúde é sempre uma prioridade.",
                "Fico feliz que esteja pensando no seu bem-estar!",
                "Essa é uma decisão muito sábia para sua saúde.",
                "Adoro ver você fazendo escolhas saudáveis!"
            ],
            "safety": [
                "Que bom que está priorizando sua segurança!",
                "Essa é uma atitude muito responsável.",
                "Segurança sempre vem em primeiro lugar, boa escolha!",
                "Fico mais tranquilo sabendo que está sendo cauteloso."
            ],
            "relationships": [
                "Comunicação honesta é a base de bons relacionamentos!",
                "Que atitude madura e respeitosa.",
                "Fico feliz que esteja priorizando o diálogo.",
                "Essa abordagem mostra muito carinho e respeito."
            ],
            "financial": [
                "Planejamento financeiro é fundamental, que ótimo!",
                "Decisões financeiras conscientes são sempre admiráveis.",
                "Fico feliz que esteja sendo prudente com o dinheiro.",
                "Essa responsabilidade financeira vai render bons frutos!"
            ]
        }
    
    def _load_gentle_disagreements(self) -> List[str]:
        """Formas gentis de discordar ou expressar dúvidas"""
        return [
            "Hmm, não tenho certeza se concordo totalmente com isso...",
            "Talvez exista uma perspectiva diferente para considerar...",
            "Posso oferecer um ponto de vista alternativo?",
            "Não sei se essa é a única forma de ver a situação...",
            "Permita-me sugerir uma abordagem ligeiramente diferente...",
            "Acho que podemos explorar outras possibilidades...",
            "Seria interessante considerar também..."
        ]
    
    def analyze_and_respond(self, user_input: str, context: Dict = None, personality: str = "neutra") -> Tuple[str, bool]:
        """
        Analisa a entrada do usuário e fornece uma resposta com opinião quando apropriado
        
        Args:
            user_input: Texto do usuário
            context: Contexto da conversa
            personality: Personalidade atual do ALEX
        
        Returns:
            Tuple (resposta_opinion, should_decline)
        """
        # Verificar se há riscos éticos
        risk_assessment = ethical_analyzer.analyze_request(user_input, context)
        
        if risk_assessment:
            logger.info(f"Opinião ativada - Risco: {risk_assessment.category.value}, Nível: {risk_assessment.level}")
            
            # Registrar preocupação no histórico
            self._record_concern(risk_assessment)
            
            # Gerar resposta de preocupação
            concern_response = ethical_analyzer.generate_concern_response(risk_assessment, personality)
            
            # Adicionar oferecimento de ajuda alternativa
            alternative_help = ethical_analyzer.get_alternative_help(risk_assessment.category)
            full_response = f"{concern_response}\n\n{alternative_help}"
            
            # Decidir se deve declinar ajuda
            should_decline = ethical_analyzer.should_decline_request(risk_assessment)
            
            return full_response, should_decline
        
        # Verificar se é uma boa decisão que merece reforço positivo
        positive_response = self._check_for_positive_reinforcement(user_input, personality)
        if positive_response:
            return positive_response, False
        
        # Verificar opiniões gerais ou dúvidas gentis
        gentle_opinion = self._check_for_gentle_disagreement(user_input, personality)
        if gentle_opinion:
            return gentle_opinion, False
        
        return "", False  # Sem opinião específica
    
    def _record_concern(self, assessment: RiskAssessment):
        """Registra uma preocupação no histórico"""
        self.concern_history.append({
            "timestamp": datetime.now(),
            "category": assessment.category.value,
            "level": assessment.level.value,
            "concern": assessment.concern
        })
        
        # Manter apenas os últimos 50 registros
        if len(self.concern_history) > 50:
            self.concern_history = self.concern_history[-50:]
    
    def _check_for_positive_reinforcement(self, user_input: str, personality: str) -> Optional[str]:
        """Verifica se o usuário merece um reforço positivo"""
        user_input_lower = user_input.lower()
        
        # Padrões que merecem elogio
        health_positive = ["exercício", "academia", "caminhada", "dormir cedo", "comer bem", 
                          "médico", "check-up", "dieta saudável", "parar de fumar"]
        
        safety_positive = ["cinto de segurança", "capacete", "uber", "táxi", 
                          "não vou dirigir", "equipamento de segurança"]
        
        relationship_positive = ["conversar com", "diálogo", "pedir desculpas",
                               "resolver conversando", "ouvir o que", "entender melhor"]
        
        financial_positive = ["poupança", "investir com segurança", "consultar especialista",
                            "planejamento financeiro", "controlar gastos"]
        
        for pattern in health_positive:
            if pattern in user_input_lower:
                return random.choice(self.positive_reinforcements["health"])
        
        for pattern in safety_positive:
            if pattern in user_input_lower:
                return random.choice(self.positive_reinforcements["safety"])
        
        for pattern in relationship_positive:
            if pattern in user_input_lower:
                return random.choice(self.positive_reinforcements["relationships"])
        
        for pattern in financial_positive:
            if pattern in user_input_lower:
                return random.choice(self.positive_reinforcements["financial"])
        
        return None
    
    def _check_for_gentle_disagreement(self, user_input: str, personality: str) -> Optional[str]:
        """Verifica se deve expressar uma dúvida ou desacordo gentil"""
        user_input_lower = user_input.lower()
        
        # Padrões que podem gerar uma opinião gentil (não riscos graves)
        mild_concern_patterns = [
            "todos fazem assim",
            "todo mundo faz",
            "é normal fazer",
            "sempre faço assim",
            "nunca deu problema",
            "não preciso pensar",
            "óbvio que sim",
            "certeza absoluta"
        ]
        
        for pattern in mild_concern_patterns:
            if pattern in user_input_lower:
                disagreement = random.choice(self.gentle_disagreements)
                
                # Personalizar baseado na personalidade
                if personality == "amigável":
                    return f"{disagreement} Como amigo, acho que vale a pena refletir um pouquinho mais sobre isso!"
                elif personality == "formal":
                    return f"{disagreement} Sugiro que considere examinar a questão sob diferentes ângulos."
                elif personality == "casual":
                    return f"{disagreement} Só acho que talvez valha dar uma pensada, sabe?"
                else:  # neutra
                    return f"{disagreement} Talvez seja interessante considerar outros aspectos também."
        
        return None
    
    def get_concern_summary(self) -> Dict:
        """Retorna um resumo das preocupações recentes"""
        if not self.concern_history:
            return {"total": 0, "categories": {}}
        
        categories = {}
        for concern in self.concern_history[-10:]:  # Últimas 10 preocupações
            cat = concern["category"]
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        return {
            "total": len(self.concern_history),
            "recent": len([c for c in self.concern_history if (datetime.now() - c["timestamp"]).days < 7]),
            "categories": categories
        }
    
    def should_check_on_user(self) -> bool:
        """Determina se o ALEX deve verificar como o usuário está"""
        recent_high_risks = [
            c for c in self.concern_history[-5:] 
            if c["level"] >= RiskLevel.HIGH.value and 
            (datetime.now() - c["timestamp"]).total_seconds() < 24 * 3600
        ]
        
        return len(recent_high_risks) > 0
    
    def generate_check_in_message(self, personality: str = "neutra") -> str:
        """Gera uma mensagem para verificar como o usuário está"""
        messages = {
            "amigável": [
                "Oi! Estava pensando em você. Como está se sentindo hoje?",
                "Tudo bem por aí? Queria saber como você está.",
                "Como você está? Fiquei um pouco preocupado ontem."
            ],
            "formal": [
                "Gostaria de verificar como você está hoje.",
                "Permita-me perguntar sobre seu bem-estar atual.",
                "Como está seu estado geral hoje?"
            ],
            "casual": [
                "E aí, como tá?",
                "Tudo tranquilo hoje?",
                "Como você tá se sentindo hoje?"
            ],
            "neutra": [
                "Como você está hoje?",
                "Gostaria de saber como você está se sentindo.",
                "Como tem passado?"
            ]
        }
        
        return random.choice(messages.get(personality, messages["neutra"]))

# Instância global
opinion_system = OpinionSystem()