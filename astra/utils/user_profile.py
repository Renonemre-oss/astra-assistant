#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal
Módulo de Perfil do Utilizador

Gere o perfil do utilizador principal para personalizar a experiência
e evitar criar múltiplas entradas para a mesma pessoa.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from config import CONFIG, DATABASE_AVAILABLE

logger = logging.getLogger(__name__)

class UserProfile:
    """
    Gerenciador do perfil do utilizador principal.
    Mantém informações consistentes sobre quem está a usar o assistente.
    """
    
    def __init__(self, database_manager=None):
        self.db_manager = database_manager
        self.profile_file = CONFIG["facts_file"].parent / "user_profile.json"
        self.current_profile = None
        
        # Carregar perfil existente
        self._load_profile()
    
    def _load_profile(self) -> None:
        """Carrega o perfil do utilizador."""
        try:
            if self.profile_file.exists():
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    self.current_profile = json.load(f)
                    logger.info(f"Perfil carregado: {self.current_profile.get('name', 'Utilizador')}")
            else:
                self.current_profile = None
                logger.info("Nenhum perfil de utilizador encontrado")
        except Exception as e:
            logger.error(f"Erro ao carregar perfil: {e}")
            self.current_profile = None
    
    def has_profile(self) -> bool:
        """Verifica se já existe um perfil configurado."""
        return self.current_profile is not None and self.current_profile.get('name')
    
    def get_profile(self) -> Optional[Dict]:
        """Obtém o perfil atual do utilizador."""
        return self.current_profile.copy() if self.current_profile else None
    
    def create_or_update_profile(self, user_data: Dict) -> bool:
        """
        Cria ou atualiza o perfil do utilizador.
        
        Args:
            user_data: Dicionário com dados do utilizador
            
        Returns:
            True se foi guardado com sucesso
        """
        try:
            if not self.current_profile:
                # Criar novo perfil
                self.current_profile = {
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'conversation_count': 0
                }
            else:
                # Atualizar perfil existente
                self.current_profile['updated_at'] = datetime.now().isoformat()
            
            # Atualizar dados
            for key, value in user_data.items():
                if value is not None:
                    self.current_profile[key] = value
            
            # Incrementar contador de conversas se não for a criação inicial
            if 'conversation_count' in self.current_profile:
                self.current_profile['conversation_count'] += 1
            
            # Guardar no ficheiro
            self._save_profile()
            
            # Tentar guardar na base de dados se disponível
            if DATABASE_AVAILABLE and self.db_manager:
                self._save_profile_to_db()
            
            logger.info(f"Perfil atualizado para: {self.current_profile.get('name', 'Utilizador')}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar/atualizar perfil: {e}")
            return False
    
    def _save_profile(self) -> None:
        """Guarda o perfil no ficheiro local."""
        try:
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_profile, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao guardar perfil: {e}")
            raise
    
    def _save_profile_to_db(self) -> bool:
        """Guarda o perfil na base de dados."""
        try:
            # Verificar se já existe um perfil na BD
            query_check = "SELECT id FROM user_preferences WHERE preference_key = 'main_user_profile'"
            self.db_manager.cursor.execute(query_check)
            existing = self.db_manager.cursor.fetchone()
            
            profile_json = json.dumps(self.current_profile, ensure_ascii=False)
            
            if existing:
                # Atualizar perfil existente
                query_update = """
                    UPDATE user_preferences 
                    SET preference_value = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE preference_key = 'main_user_profile'
                """
                self.db_manager.cursor.execute(query_update, (profile_json,))
            else:
                # Criar novo perfil
                query_insert = """
                    INSERT INTO user_preferences (preference_key, preference_value) 
                    VALUES ('main_user_profile', %s)
                """
                self.db_manager.cursor.execute(query_insert, (profile_json,))
            
            logger.info("Perfil guardado na base de dados")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao guardar perfil na BD: {e}")
            return False
    
    def detect_user_from_input(self, text: str) -> Optional[Dict]:
        """
        Detecta informações sobre o utilizador a partir do input.
        
        Args:
            text: Texto do utilizador
            
        Returns:
            Dicionário com informações detectadas ou None
        """
        text_lower = text.lower()
        detected_info = {}
        
        # Padrões para detectar o nome do utilizador
        name_patterns = [
            r'(?:eu sou|chamo-me|meu nome é|me chamo) ([A-Z][a-záàâãéèêíïóôõöúçñ]+)',
            r'(?:sou (?:o|a)) ([A-Z][a-záàâãéèêíïóôõöúçñ]+)',
        ]
        
        import re
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                detected_info['name'] = match.group(1).title()
                break
        
        # Padrões para detectar idade
        age_patterns = [
            r'(?:tenho|eu tenho) (\d+) anos',
            r'(?:minha idade é|idade) (\d+)',
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    age = int(match.group(1))
                    if 1 <= age <= 120:
                        detected_info['age'] = age
                        break
                except ValueError:
                    continue
        
        # Padrões para detectar profissão
        profession_patterns = [
            r'(?:trabalho como|sou|profissão|trabalho de) ([a-záàâãéèêíïóôõöúçñ\s]+)',
            r'(?:eu sou) ([a-záàâãéèêíïóôõöúçñ]+) (?:de profissão)',
        ]
        
        for pattern in profession_patterns:
            match = re.search(pattern, text_lower)
            if match:
                profession = match.group(1).strip()
                if len(profession) > 2:
                    detected_info['profession'] = profession
                    break
        
        # Padrões para detectar localização
        location_patterns = [
            r'(?:vivo em|moro em|sou de) ([A-Z][a-záàâãéèêíïóôõöúçñ\s]+)',
            r'(?:cidade|local) ([A-Z][a-záàâãéèêíïóôõöúçñ\s]+)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if len(location) > 2:
                    detected_info['location'] = location
                    break
        
        return detected_info if detected_info else None
    
    def get_greeting_context(self) -> str:
        """Gera contexto personalizado para saudações."""
        if not self.has_profile():
            return ""
        
        profile = self.get_profile()
        context_parts = []
        
        if profile.get('name'):
            context_parts.append(f"Nome do utilizador: {profile['name']}")
        
        if profile.get('age'):
            context_parts.append(f"Idade: {profile['age']} anos")
        
        if profile.get('profession'):
            context_parts.append(f"Profissão: {profile['profession']}")
        
        if profile.get('location'):
            context_parts.append(f"Local: {profile['location']}")
        
        if profile.get('conversation_count'):
            context_parts.append(f"Número de conversas: {profile['conversation_count']}")
        
        if context_parts:
            return "PERFIL DO UTILIZADOR:\n" + "\n".join(context_parts) + "\n\nUse estas informações para personalizar a conversa.\n"
        
        return ""
    
    def should_ask_for_profile(self, conversation_count: int = 0) -> bool:
        """
        Determina se deve pedir informações do perfil do utilizador.
        
        Args:
            conversation_count: Número de mensagens na conversa atual
            
        Returns:
            True se deve perguntar sobre o perfil
        """
        # Se já tem perfil, não precisa perguntar
        if self.has_profile():
            return False
        
        # Perguntar após algumas interações para não ser intrusivo
        return conversation_count >= 3
    
    def get_profile_questions(self) -> list:
        """Retorna lista de perguntas para construir o perfil."""
        questions = [
            "Como posso chamar-te? Qual é o teu nome?",
            "Gostaria de saber um pouco mais sobre ti para personalizar as nossas conversas. Qual é a tua profissão?",
            "Em que cidade vives?",
            "Há algo específico que gostas que eu saiba sobre ti?"
        ]
        return questions
