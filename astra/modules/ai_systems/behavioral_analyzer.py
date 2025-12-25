#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BehavioralAnalyzer - Sistema de análise comportamental avançado.
Analisa padrões de uso, horários, preferências e comportamentos do usuário.
"""

import json
import logging
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BehaviorPattern:
    """Classe para representar um padrão comportamental"""
    pattern_type: str
    frequency: float
    confidence: float
    description: str
    metadata: Dict[str, Any]

@dataclass  
class UserSession:
    """Classe para representar uma sessão do usuário"""
    timestamp: datetime
    duration_minutes: float
    commands_used: List[str]
    time_of_day: str  # "morning", "afternoon", "evening", "night"
    day_of_week: int  # 0=Monday, 6=Sunday

class BehavioralAnalyzer:
    """Sistema de análise comportamental usando técnicas de ML."""
    
    def __init__(self, db_path: str = "data/behavioral_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar banco de dados
        self._init_database()
        
        # Cache para padrões descobertos
        self.cached_patterns: Dict[str, List[BehaviorPattern]] = {}
        self.last_analysis: Optional[datetime] = None
        
        # Configurações de análise
        self.min_sessions_for_pattern = 5
        self.confidence_threshold = 0.6
        
    def _init_database(self):
        """Inicializa o banco de dados para armazenar dados comportamentais."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    duration_minutes REAL,
                    commands_used TEXT,
                    time_of_day TEXT,
                    day_of_week INTEGER,
                    user_id TEXT DEFAULT 'default'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS command_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT,
                    timestamp DATETIME,
                    execution_time_ms REAL,
                    success BOOLEAN,
                    user_id TEXT DEFAULT 'default'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS behavior_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT,
                    frequency REAL,
                    confidence REAL,
                    description TEXT,
                    metadata TEXT,
                    discovered_at DATETIME,
                    user_id TEXT DEFAULT 'default'
                )
            """)
            
    def log_session(self, duration_minutes: float, commands_used: List[str], user_id: str = "default"):
        """Registra uma sessão do usuário."""
        now = datetime.now()
        time_of_day = self._get_time_of_day(now.hour)
        day_of_week = now.weekday()
        
        session = UserSession(
            timestamp=now,
            duration_minutes=duration_minutes,
            commands_used=commands_used,
            time_of_day=time_of_day,
            day_of_week=day_of_week
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO user_sessions 
                (timestamp, duration_minutes, commands_used, time_of_day, day_of_week, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session.timestamp.isoformat(),
                session.duration_minutes,
                json.dumps(session.commands_used),
                session.time_of_day,
                session.day_of_week,
                user_id
            ))
            
        logger.info(f"Sessão registrada: {duration_minutes:.1f}min, {len(commands_used)} comandos")
        
    def log_command_usage(self, command: str, execution_time_ms: float, success: bool, user_id: str = "default"):
        """Registra o uso de um comando."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO command_usage (command, timestamp, execution_time_ms, success, user_id)
                VALUES (?, ?, ?, ?, ?)
            """, (command, datetime.now().isoformat(), execution_time_ms, success, user_id))
            
    def _get_time_of_day(self, hour: int) -> str:
        """Determina período do dia baseado na hora."""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"
            
    def analyze_usage_patterns(self, user_id: str = "default", days_back: int = 30) -> List[BehaviorPattern]:
        """Analisa padrões de uso do usuário."""
        patterns = []
        
        # Análise temporal
        patterns.extend(self._analyze_time_patterns(user_id, days_back))
        
        # Análise de comandos
        patterns.extend(self._analyze_command_patterns(user_id, days_back))
        
        # Análise de duração de sessões
        patterns.extend(self._analyze_session_duration_patterns(user_id, days_back))
        
        # Análise de sequências
        patterns.extend(self._analyze_command_sequences(user_id, days_back))
        
        # Cache dos padrões
        self.cached_patterns[user_id] = patterns
        self.last_analysis = datetime.now()
        
        # Salvar padrões no banco
        self._save_patterns_to_db(patterns, user_id)
        
        return patterns
        
    def _analyze_time_patterns(self, user_id: str, days_back: int) -> List[BehaviorPattern]:
        """Analisa padrões temporais de uso."""
        patterns = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT time_of_day, day_of_week, COUNT(*) as count
                FROM user_sessions 
                WHERE user_id = ? AND timestamp > datetime('now', '-{} days')
                GROUP BY time_of_day, day_of_week
            """.format(days_back), (user_id,))
            
            time_data = cursor.fetchall()
            
        if len(time_data) < self.min_sessions_for_pattern:
            return patterns
            
        # Análise por período do dia
        time_counts = defaultdict(int)
        total_sessions = 0
        
        for time_of_day, day_of_week, count in time_data:
            time_counts[time_of_day] += count
            total_sessions += count
            
        # Encontrar horários preferenciais
        for time_period, count in time_counts.items():
            frequency = count / total_sessions
            if frequency > 0.3:  # Mais de 30% das sessões
                confidence = min(0.9, frequency * 1.5)
                patterns.append(BehaviorPattern(
                    pattern_type="time_preference",
                    frequency=frequency,
                    confidence=confidence,
                    description=f"Usuário prefere usar o sistema no período: {time_period}",
                    metadata={"time_period": time_period, "usage_count": count}
                ))
                
        # Análise por dia da semana
        day_counts = defaultdict(int)
        for time_of_day, day_of_week, count in time_data:
            day_counts[day_of_week] += count
            
        day_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        for day, count in day_counts.items():
            frequency = count / total_sessions
            if frequency > 0.2:  # Mais de 20% das sessões
                confidence = min(0.8, frequency * 1.2)
                patterns.append(BehaviorPattern(
                    pattern_type="day_preference",
                    frequency=frequency,
                    confidence=confidence,
                    description=f"Maior atividade nas {day_names[day]}s",
                    metadata={"day_of_week": day, "usage_count": count}
                ))
                
        return patterns
        
    def _analyze_command_patterns(self, user_id: str, days_back: int) -> List[BehaviorPattern]:
        """Analisa padrões de uso de comandos."""
        patterns = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT command, COUNT(*) as count, AVG(execution_time_ms) as avg_time,
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
                FROM command_usage 
                WHERE user_id = ? AND timestamp > datetime('now', '-{} days')
                GROUP BY command
                ORDER BY count DESC
            """.format(days_back), (user_id,))
            
            command_data = cursor.fetchall()
            
        if not command_data:
            return patterns
            
        total_commands = sum(count for _, count, _, _ in command_data)
        
        # Comandos mais usados
        for command, count, avg_time, success_rate in command_data[:10]:
            frequency = count / total_commands
            if frequency > 0.05:  # Mais de 5% do uso
                confidence = min(0.9, frequency * 2)
                patterns.append(BehaviorPattern(
                    pattern_type="favorite_command",
                    frequency=frequency,
                    confidence=confidence,
                    description=f"Comando frequente: '{command}' ({frequency:.1%} do uso)",
                    metadata={
                        "command": command,
                        "usage_count": count,
                        "avg_execution_time": avg_time,
                        "success_rate": success_rate
                    }
                ))
                
        # Comandos com baixa taxa de sucesso
        for command, count, avg_time, success_rate in command_data:
            if count >= 5 and success_rate < 70:
                patterns.append(BehaviorPattern(
                    pattern_type="problematic_command",
                    frequency=count / total_commands,
                    confidence=0.8,
                    description=f"Comando '{command}' tem baixa taxa de sucesso ({success_rate:.1f}%)",
                    metadata={
                        "command": command,
                        "success_rate": success_rate,
                        "usage_count": count
                    }
                ))
                
        return patterns
        
    def _analyze_session_duration_patterns(self, user_id: str, days_back: int) -> List[BehaviorPattern]:
        """Analisa padrões de duração das sessões."""
        patterns = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT duration_minutes, time_of_day
                FROM user_sessions 
                WHERE user_id = ? AND timestamp > datetime('now', '-{} days')
            """.format(days_back), (user_id,))
            
            duration_data = cursor.fetchall()
            
        if len(duration_data) < self.min_sessions_for_pattern:
            return patterns
            
        durations = [d[0] for d in duration_data]
        avg_duration = np.mean(durations)
        std_duration = np.std(durations)
        
        # Sessões longas vs curtas
        long_sessions = [d for d in durations if d > avg_duration + std_duration]
        short_sessions = [d for d in durations if d < avg_duration - std_duration]
        
        if len(long_sessions) > len(durations) * 0.1:  # Mais de 10% são sessões longas
            patterns.append(BehaviorPattern(
                pattern_type="session_length",
                frequency=len(long_sessions) / len(durations),
                confidence=0.7,
                description=f"Usuário tem sessões longas (média: {np.mean(long_sessions):.1f}min)",
                metadata={
                    "avg_long_session": np.mean(long_sessions),
                    "long_session_count": len(long_sessions)
                }
            ))
            
        # Padrão de duração por período
        time_durations = defaultdict(list)
        for duration, time_of_day in duration_data:
            time_durations[time_of_day].append(duration)
            
        for time_period, durations_list in time_durations.items():
            if len(durations_list) >= 3:
                avg_time_duration = np.mean(durations_list)
                if avg_time_duration > avg_duration * 1.2:  # 20% acima da média
                    patterns.append(BehaviorPattern(
                        pattern_type="time_duration_preference",
                        frequency=len(durations_list) / len(duration_data),
                        confidence=0.6,
                        description=f"Sessões mais longas no período: {time_period}",
                        metadata={
                            "time_period": time_period,
                            "avg_duration": avg_time_duration
                        }
                    ))
                    
        return patterns
        
    def _analyze_command_sequences(self, user_id: str, days_back: int) -> List[BehaviorPattern]:
        """Analisa sequências comuns de comandos."""
        patterns = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT commands_used 
                FROM user_sessions 
                WHERE user_id = ? AND timestamp > datetime('now', '-{} days')
                AND commands_used IS NOT NULL
            """.format(days_back), (user_id,))
            
            sessions_data = cursor.fetchall()
            
        if len(sessions_data) < self.min_sessions_for_pattern:
            return patterns
            
        # Analisar sequências de 2 comandos
        sequences = []
        for (commands_json,) in sessions_data:
            try:
                commands = json.loads(commands_json)
                if len(commands) >= 2:
                    for i in range(len(commands) - 1):
                        sequences.append((commands[i], commands[i + 1]))
            except (json.JSONDecodeError, TypeError):
                continue
                
        if not sequences:
            return patterns
            
        # Contar sequências mais comuns
        sequence_counts = Counter(sequences)
        total_sequences = len(sequences)
        
        for (cmd1, cmd2), count in sequence_counts.most_common(10):
            frequency = count / total_sequences
            if frequency > 0.1:  # Mais de 10% das sequências
                confidence = min(0.8, frequency * 1.5)
                patterns.append(BehaviorPattern(
                    pattern_type="command_sequence",
                    frequency=frequency,
                    confidence=confidence,
                    description=f"Sequência comum: '{cmd1}' → '{cmd2}'",
                    metadata={
                        "first_command": cmd1,
                        "second_command": cmd2,
                        "occurrence_count": count
                    }
                ))
                
        return patterns
        
    def _save_patterns_to_db(self, patterns: List[BehaviorPattern], user_id: str):
        """Salva os padrões descobertos no banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            # Limpar padrões antigos
            conn.execute("DELETE FROM behavior_patterns WHERE user_id = ?", (user_id,))
            
            # Inserir novos padrões
            for pattern in patterns:
                conn.execute("""
                    INSERT INTO behavior_patterns 
                    (pattern_type, frequency, confidence, description, metadata, discovered_at, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.pattern_type,
                    pattern.frequency,
                    pattern.confidence,
                    pattern.description,
                    json.dumps(pattern.metadata),
                    datetime.now().isoformat(),
                    user_id
                ))
                
    def get_user_insights(self, user_id: str = "default") -> Dict[str, Any]:
        """Gera insights sobre o comportamento do usuário."""
        patterns = self.cached_patterns.get(user_id, [])
        if not patterns:
            patterns = self.analyze_usage_patterns(user_id)
            
        insights = {
            "total_patterns": len(patterns),
            "high_confidence_patterns": len([p for p in patterns if p.confidence > 0.8]),
            "usage_preferences": {},
            "recommendations": [],
            "behavioral_score": 0.0
        }
        
        # Categorizar padrões
        pattern_types = defaultdict(list)
        for pattern in patterns:
            pattern_types[pattern.pattern_type].append(pattern)
            
        # Preferências de uso
        for pattern_type, type_patterns in pattern_types.items():
            if type_patterns:
                best_pattern = max(type_patterns, key=lambda p: p.confidence)
                insights["usage_preferences"][pattern_type] = {
                    "description": best_pattern.description,
                    "confidence": best_pattern.confidence,
                    "frequency": best_pattern.frequency
                }
                
        # Pontuação comportamental (0-100)
        if patterns:
            avg_confidence = np.mean([p.confidence for p in patterns])
            pattern_diversity = len(pattern_types)
            insights["behavioral_score"] = min(100, (avg_confidence * 70) + (pattern_diversity * 5))
            
        # Recomendações baseadas nos padrões
        insights["recommendations"] = self._generate_recommendations(patterns)
        
        return insights
        
    def _generate_recommendations(self, patterns: List[BehaviorPattern]) -> List[str]:
        """Gera recomendações baseadas nos padrões comportamentais."""
        recommendations = []
        
        for pattern in patterns:
            if pattern.pattern_type == "problematic_command" and pattern.confidence > 0.7:
                recommendations.append(f"Considere revisar o uso do comando '{pattern.metadata['command']}' - baixa taxa de sucesso")
                
            elif pattern.pattern_type == "time_preference" and pattern.confidence > 0.8:
                recommendations.append(f"Configure lembretes para o período {pattern.metadata['time_period']} quando você é mais ativo")
                
            elif pattern.pattern_type == "command_sequence" and pattern.confidence > 0.7:
                cmd1, cmd2 = pattern.metadata['first_command'], pattern.metadata['second_command']
                recommendations.append(f"Considere criar um macro para a sequência '{cmd1}' → '{cmd2}'")
                
            elif pattern.pattern_type == "session_length" and pattern.confidence > 0.6:
                recommendations.append("Configure intervalos automáticos para sessões longas")
                
        return recommendations[:5]  # Máximo 5 recomendações
        
    def get_pattern_summary(self, user_id: str = "default") -> str:
        """Gera um resumo textual dos padrões comportamentais."""
        patterns = self.cached_patterns.get(user_id, [])
        if not patterns:
            return "Não há dados suficientes para análise comportamental."
            
        insights = self.get_user_insights(user_id)
        
        summary = f"📊 **Análise Comportamental**\n\n"
        summary += f"• Padrões identificados: {insights['total_patterns']}\n"
        summary += f"• Padrões de alta confiança: {insights['high_confidence_patterns']}\n"
        summary += f"• Pontuação comportamental: {insights['behavioral_score']:.1f}/100\n\n"
        
        if insights["usage_preferences"]:
            summary += "🎯 **Preferências Identificadas:**\n"
            for pref_type, details in insights["usage_preferences"].items():
                summary += f"• {details['description']} (confiança: {details['confidence']:.1%})\n"
                
        if insights["recommendations"]:
            summary += "\n💡 **Recomendações:**\n"
            for rec in insights["recommendations"]:
                summary += f"• {rec}\n"
                
        return summary