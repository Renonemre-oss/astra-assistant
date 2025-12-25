#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NeedsPredictor - Sistema de previsão de necessidades baseado em ML.
Utiliza histórico comportamental para antecipar necessidades do usuário.
"""

import json
import logging
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Prediction:
    """Classe para representar uma previsão"""
    need_type: str
    confidence: float
    time_window: str  # "next_hour", "today", "this_week"
    description: str
    suggested_actions: List[str]
    metadata: Dict[str, Any]

@dataclass
class ContextualFeature:
    """Classe para features contextuais"""
    name: str
    value: Any
    weight: float
    description: str

class NeedsPredictor:
    """Sistema de previsão de necessidades usando análise preditiva."""
    
    def __init__(self, db_path: str = "data/behavioral_data.db"):
        self.db_path = Path(db_path)
        self.behavioral_analyzer = None  # Será injetado posteriormente
        
        # Cache de previsões
        self.cached_predictions: Dict[str, List[Prediction]] = {}
        self.last_prediction: Optional[datetime] = None
        
        # Configurações do modelo
        self.prediction_threshold = 0.6
        self.max_predictions = 10
        
        # Pesos para diferentes features
        self.feature_weights = {
            "time_pattern": 0.8,
            "command_frequency": 0.7,
            "day_pattern": 0.6,
            "sequence_pattern": 0.5,
            "session_duration": 0.4
        }
        
    def set_behavioral_analyzer(self, analyzer):
        """Define o analisador comportamental para usar suas análises."""
        self.behavioral_analyzer = analyzer
        
    def predict_needs(self, user_id: str = "default", horizon: str = "next_hour") -> List[Prediction]:
        """Prediz necessidades do usuário baseado em padrões históricos."""
        if not self.behavioral_analyzer:
            logger.warning("BehavioralAnalyzer não configurado")
            return []
            
        predictions = []
        current_context = self._get_current_context(user_id)
        
        # Diferentes tipos de previsão
        predictions.extend(self._predict_command_needs(user_id, horizon, current_context))
        predictions.extend(self._predict_information_needs(user_id, horizon, current_context))
        predictions.extend(self._predict_routine_needs(user_id, horizon, current_context))
        predictions.extend(self._predict_maintenance_needs(user_id, horizon, current_context))
        
        # Filtrar e ordenar por confiança
        predictions = [p for p in predictions if p.confidence >= self.prediction_threshold]
        predictions.sort(key=lambda x: x.confidence, reverse=True)
        
        # Cache das previsões
        self.cached_predictions[user_id] = predictions[:self.max_predictions]
        self.last_prediction = datetime.now()
        
        return self.cached_predictions[user_id]
        
    def _get_current_context(self, user_id: str) -> Dict[str, Any]:
        """Obtém o contexto atual do usuário."""
        now = datetime.now()
        context = {
            "hour": now.hour,
            "day_of_week": now.weekday(),
            "time_of_day": self._get_time_of_day(now.hour),
            "is_weekend": now.weekday() >= 5,
            "date": now.date().isoformat()
        }
        
        # Adicionar padrões comportamentais recentes
        if self.behavioral_analyzer:
            patterns = self.behavioral_analyzer.cached_patterns.get(user_id, [])
            context["active_patterns"] = [p.pattern_type for p in patterns if p.confidence > 0.7]
            
        return context
        
    def _get_time_of_day(self, hour: int) -> str:
        """Determina período do dia."""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon" 
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"
            
    def _predict_command_needs(self, user_id: str, horizon: str, context: Dict[str, Any]) -> List[Prediction]:
        """Prediz comandos que o usuário provavelmente usará."""
        predictions = []
        
        # Buscar histórico de comandos similares ao contexto atual
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT cu.command, COUNT(*) as usage_count, 
                       AVG(cu.execution_time_ms) as avg_time,
                       SUM(CASE WHEN cu.success THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
                FROM command_usage cu
                JOIN user_sessions us ON date(cu.timestamp) = date(us.timestamp)
                WHERE cu.user_id = ? 
                AND us.time_of_day = ?
                AND us.day_of_week = ?
                AND cu.timestamp > datetime('now', '-30 days')
                GROUP BY cu.command
                ORDER BY usage_count DESC
                LIMIT 5
            """, (user_id, context["time_of_day"], context["day_of_week"]))
            
            command_data = cursor.fetchall()
            
        for command, usage_count, avg_time, success_rate in command_data:
            if usage_count >= 3:  # Mínimo de uso histórico
                # Calcular confiança baseada em frequência e contexto
                base_confidence = min(0.9, (usage_count / 30) * 0.8)  # Normalizado para 30 dias
                context_bonus = 0.1 if success_rate > 80 else -0.1
                confidence = max(0.0, base_confidence + context_bonus)
                
                if confidence >= self.prediction_threshold:
                    suggestions = [f"Executar '{command}'"]
                    if avg_time > 2000:  # Comando lento
                        suggestions.append("Considere executar em background")
                        
                    predictions.append(Prediction(
                        need_type="command_usage",
                        confidence=confidence,
                        time_window=horizon,
                        description=f"Provável uso do comando '{command}'",
                        suggested_actions=suggestions,
                        metadata={
                            "command": command,
                            "historical_usage": usage_count,
                            "avg_execution_time": avg_time,
                            "success_rate": success_rate
                        }
                    ))
                    
        return predictions
        
    def _predict_information_needs(self, user_id: str, horizon: str, context: Dict[str, Any]) -> List[Prediction]:
        """Prediz necessidades de informação (clima, notícias, etc.)."""
        predictions = []
        now = datetime.now()
        
        # Previsão de clima (manhãs e antes de sair)
        if context["time_of_day"] == "morning" or (context["hour"] >= 7 and context["hour"] <= 9):
            predictions.append(Prediction(
                need_type="weather_info",
                confidence=0.8,
                time_window="next_hour",
                description="Provável consulta ao clima matinal",
                suggested_actions=["Mostrar clima atual", "Exibir previsão do dia"],
                metadata={"trigger": "morning_routine"}
            ))
            
        # Previsão de notícias (horários regulares)
        if context["time_of_day"] in ["morning", "afternoon"] and not context["is_weekend"]:
            predictions.append(Prediction(
                need_type="news_info",
                confidence=0.7,
                time_window=horizon,
                description="Provável interesse em notícias",
                suggested_actions=["Resumir principais notícias", "Filtrar notícias por interesse"],
                metadata={"trigger": "work_day_routine"}
            ))
            
        # Previsão de agenda (início do dia e da semana)
        if (context["time_of_day"] == "morning") or (context["day_of_week"] == 0):  # Segunda-feira
            predictions.append(Prediction(
                need_type="schedule_info",
                confidence=0.75,
                time_window="today",
                description="Provável consulta à agenda",
                suggested_actions=["Mostrar compromissos do dia", "Destacar próximos eventos"],
                metadata={"trigger": "daily_planning"}
            ))
            
        return predictions
        
    def _predict_routine_needs(self, user_id: str, horizon: str, context: Dict[str, Any]) -> List[Prediction]:
        """Prediz necessidades baseadas em rotinas identificadas."""
        predictions = []
        
        if not self.behavioral_analyzer:
            return predictions
            
        patterns = self.behavioral_analyzer.cached_patterns.get(user_id, [])
        
        for pattern in patterns:
            if pattern.pattern_type == "time_preference" and pattern.confidence > 0.8:
                preferred_time = pattern.metadata.get("time_period")
                if preferred_time == context["time_of_day"]:
                    predictions.append(Prediction(
                        need_type="routine_activation",
                        confidence=pattern.confidence * 0.9,
                        time_window=horizon,
                        description=f"Horário de alta atividade: {preferred_time}",
                        suggested_actions=[
                            "Preparar sistemas para alta demanda",
                            "Sugerir tarefas pendentes",
                            "Otimizar performance"
                        ],
                        metadata={
                            "routine_type": "time_based",
                            "trigger_time": preferred_time
                        }
                    ))
                    
            elif pattern.pattern_type == "command_sequence" and pattern.confidence > 0.7:
                first_cmd = pattern.metadata.get("first_command")
                second_cmd = pattern.metadata.get("second_command")
                
                predictions.append(Prediction(
                    need_type="sequence_completion",
                    confidence=pattern.confidence * 0.8,
                    time_window="immediate",
                    description=f"Após '{first_cmd}', usuário tipicamente executa '{second_cmd}'",
                    suggested_actions=[
                        f"Preparar comando '{second_cmd}'",
                        "Sugerir próximo passo automaticamente"
                    ],
                    metadata={
                        "sequence": [first_cmd, second_cmd],
                        "trigger_command": first_cmd
                    }
                ))
                
        return predictions
        
    def _predict_maintenance_needs(self, user_id: str, horizon: str, context: Dict[str, Any]) -> List[Prediction]:
        """Prediz necessidades de manutenção do sistema."""
        predictions = []
        
        # Verificar se há comandos com baixa taxa de sucesso
        if self.behavioral_analyzer:
            patterns = self.behavioral_analyzer.cached_patterns.get(user_id, [])
            
            for pattern in patterns:
                if pattern.pattern_type == "problematic_command":
                    command = pattern.metadata.get("command")
                    success_rate = pattern.metadata.get("success_rate", 0)
                    
                    predictions.append(Prediction(
                        need_type="system_maintenance",
                        confidence=0.8,
                        time_window="this_week",
                        description=f"Comando '{command}' precisa de manutenção ({success_rate:.1f}% sucesso)",
                        suggested_actions=[
                            f"Diagnosticar problemas em '{command}'",
                            "Verificar dependências",
                            "Atualizar documentação"
                        ],
                        metadata={
                            "maintenance_type": "command_optimization",
                            "problem_command": command,
                            "success_rate": success_rate
                        }
                    ))
                    
        # Manutenção periódica baseada em uso
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as session_count, AVG(duration_minutes) as avg_duration
                FROM user_sessions
                WHERE user_id = ? AND timestamp > datetime('now', '-7 days')
            """, (user_id,))
            
            result = cursor.fetchone()
            
        if result:
            session_count, avg_duration = result
            
            # Alta atividade = necessidade de otimização
            if session_count > 20:  # Mais de 20 sessões por semana
                predictions.append(Prediction(
                    need_type="performance_optimization",
                    confidence=0.6,
                    time_window="this_week",
                    description="Alta atividade detectada - otimização recomendada",
                    suggested_actions=[
                        "Limpar cache antigo",
                        "Otimizar banco de dados",
                        "Verificar performance"
                    ],
                    metadata={
                        "weekly_sessions": session_count,
                        "avg_session_duration": avg_duration
                    }
                ))
                
        return predictions
        
    def get_prediction_summary(self, user_id: str = "default") -> str:
        """Gera resumo textual das previsões."""
        predictions = self.cached_predictions.get(user_id, [])
        if not predictions:
            predictions = self.predict_needs(user_id)
            
        if not predictions:
            return "Não há previsões disponíveis no momento."
            
        summary = f"🔮 **Previsões de Necessidades**\n\n"
        summary += f"• Total de previsões: {len(predictions)}\n"
        summary += f"• Última análise: {self.last_prediction.strftime('%H:%M:%S') if self.last_prediction else 'N/A'}\n\n"
        
        # Agrupar por tipo
        by_type = defaultdict(list)
        for pred in predictions:
            by_type[pred.need_type].append(pred)
            
        for need_type, type_predictions in by_type.items():
            summary += f"**{need_type.replace('_', ' ').title()}:**\n"
            for pred in type_predictions[:3]:  # Mostrar apenas top 3 por tipo
                summary += f"• {pred.description} (confiança: {pred.confidence:.1%})\n"
                if pred.suggested_actions:
                    summary += f"  → {pred.suggested_actions[0]}\n"
            summary += "\n"
            
        return summary
        
    def get_immediate_suggestions(self, user_id: str = "default") -> List[str]:
        """Retorna sugestões imediatas baseadas nas previsões."""
        predictions = self.cached_predictions.get(user_id, [])
        if not predictions:
            return []
            
        suggestions = []
        for pred in predictions:
            if pred.time_window in ["immediate", "next_hour"] and pred.confidence > 0.7:
                suggestions.extend(pred.suggested_actions[:2])  # Máximo 2 por previsão
                
        return suggestions[:5]  # Máximo 5 sugestões
        
    def learn_from_feedback(self, user_id: str, prediction_id: str, was_useful: bool):
        """Aprende com feedback do usuário sobre as previsões."""
        # Este método pode ser expandido para implementar aprendizado online
        # Por enquanto, apenas log do feedback
        logger.info(f"Feedback recebido: {prediction_id} = {'útil' if was_useful else 'inútil'}")
        
        # TODO: Implementar ajuste de pesos baseado no feedback
        # TODO: Salvar feedback no banco de dados para análise futura