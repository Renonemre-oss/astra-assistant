#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Assistente Pessoal
Database Manager - Gerenciamento de Base de Dados SQLite

Este módulo fornece funcionalidades para:
- Conectar ao SQLite
- Criar tabelas necessárias
- Salvar/recuperar conversas
- Gerenciar histórico de interações
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import os
from dataclasses import dataclass
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Configuração da base de dados SQLite"""
    database_path: str = "alex_assistant.db"
    
    def get_full_path(self) -> Path:
        """Retorna o caminho completo do arquivo da base de dados"""
        if os.path.isabs(self.database_path):
            return Path(self.database_path)
        else:
            # Por padrão, salva na pasta database do projeto
            return Path(__file__).parent / self.database_path

class DatabaseManager:
    """
    Gerenciador de base de dados SQLite para o assistente ALEX
    """
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.connection = None
        self.cursor = None
        
    def connect(self) -> bool:
        """
        Estabelece conexão com SQLite
        
        Returns:
            bool: True se conectou com sucesso, False caso contrário
        """
        try:
            db_path = self.config.get_full_path()
            
            # Criar diretório se não existir
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(
                str(db_path),
                check_same_thread=False,  # Permite uso em threads
                timeout=30.0  # Timeout em segundos
            )
            
            # Configurar SQLite para retornar dicionários
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            
            # Habilitar chaves estrangeiras
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            logger.info(f"✅ Conectado ao SQLite: {db_path}")
            
            # Criar tabelas se não existirem
            self._create_tables()
            
            return True
                
        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao conectar ao SQLite: {e}")
            return False
    
    def disconnect(self):
        """
        Fecha a conexão com SQLite
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
                logger.info("🔐 Conexão SQLite fechada")
        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao fechar conexão: {e}")
    
    def _create_tables(self):
        """
        Cria todas as tabelas necessárias
        """
        tables = {
            'conversations': """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    title TEXT DEFAULT 'Nova Conversa',
                    personality TEXT DEFAULT 'neutra',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    metadata TEXT DEFAULT NULL
                )
            """,
            
            'messages': """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    message_type TEXT NOT NULL CHECK(message_type IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    response_time REAL DEFAULT NULL,
                    token_count INTEGER DEFAULT NULL,
                    model_used TEXT DEFAULT NULL,
                    metadata TEXT DEFAULT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """,
            
            'voice_interactions': """
                CREATE TABLE IF NOT EXISTS voice_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    audio_duration REAL DEFAULT NULL,
                    recognition_confidence REAL DEFAULT NULL,
                    tts_enabled BOOLEAN DEFAULT 1,
                    voice_command BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT DEFAULT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """,
            
            'user_preferences': """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_key TEXT NOT NULL UNIQUE,
                    preference_value TEXT NOT NULL,
                    data_type TEXT DEFAULT 'string' CHECK(data_type IN ('string', 'integer', 'float', 'boolean', 'json')),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """,
            
            'people': """
                CREATE TABLE IF NOT EXISTS people (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    nickname TEXT DEFAULT NULL,
                    relationship TEXT DEFAULT NULL,
                    age INTEGER DEFAULT NULL,
                    gender TEXT DEFAULT NULL CHECK(gender IN ('masculino', 'feminino', 'não-binário', 'outro', 'prefere_nao_dizer')),
                    sexuality TEXT DEFAULT NULL,
                    personality_traits TEXT DEFAULT NULL,
                    interests TEXT DEFAULT NULL,
                    favorite_foods TEXT DEFAULT NULL,
                    favorite_music TEXT DEFAULT NULL,
                    favorite_movies TEXT DEFAULT NULL,
                    favorite_activities TEXT DEFAULT NULL,
                    dislikes TEXT DEFAULT NULL,
                    profession TEXT DEFAULT NULL,
                    birthday DATE DEFAULT NULL,
                    contact_info TEXT DEFAULT NULL,
                    notes TEXT DEFAULT NULL,
                    importance_level TEXT DEFAULT 'média' CHECK(importance_level IN ('baixa', 'média', 'alta', 'muito_alta')),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """
        }
        
        for table_name, create_query in tables.items():
            try:
                self.cursor.execute(create_query)
                self.connection.commit()
                logger.info(f"✅ Tabela '{table_name}' verificada/criada")
            except sqlite3.Error as e:
                logger.error(f"❌ Erro ao criar tabela '{table_name}': {e}")
                raise
    
    def create_conversation(self, session_id: str, title: str = "Nova Conversa", 
                          personality: str = "neutra", metadata: Dict = None) -> Optional[int]:
        """
        Cria uma nova conversa
        
        Args:
            session_id: ID único da sessão
            title: Título da conversa
            personality: Personalidade do assistente
            metadata: Metadados adicionais
        
        Returns:
            int: ID da conversa criada ou None se houver erro
        """
        try:
            query = """
                INSERT INTO conversations (session_id, title, personality, metadata)
                VALUES (?, ?, ?, ?)
            """
            
            data = (
                session_id,
                title,
                personality,
                json.dumps(metadata) if metadata else None
            )
            
            self.cursor.execute(query, data)
            self.connection.commit()
            conversation_id = self.cursor.lastrowid
            
            logger.info(f"📝 Nova conversa criada: ID={conversation_id}, Session={session_id}")
            return conversation_id
            
        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao criar conversa: {e}")
            return None
    
    def get_conversation_by_session(self, session_id: str) -> Optional[Dict]:
        """
        Obtém conversa por session_id
        
        Args:
            session_id: ID da sessão
        
        Returns:
            Dict: Dados da conversa ou None se não encontrada
        """
        try:
            query = "SELECT * FROM conversations WHERE session_id = ?"
            self.cursor.execute(query, (session_id,))
            result = self.cursor.fetchone()
            
            if result:
                # Converter sqlite3.Row para dict
                result = dict(result)
                if result.get('metadata'):
                    result['metadata'] = json.loads(result['metadata'])
            
            return result
            
        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao buscar conversa: {e}")
            return None
    
    def save_message(self, conversation_id: int, message_type: str, content: str,
                    response_time: float = None, model_used: str = None, 
                    metadata: Dict = None) -> Optional[int]:
        """
        Salva uma mensagem na conversa
        
        Args:
            conversation_id: ID da conversa
            message_type: 'user', 'assistant' ou 'system'
            content: Conteúdo da mensagem
            response_time: Tempo de resposta em segundos
            model_used: Modelo usado para gerar resposta
            metadata: Metadados adicionais
        
        Returns:
            int: ID da mensagem salva ou None se houver erro
        """
        try:
            query = """
                INSERT INTO messages (conversation_id, message_type, content, response_time, model_used, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            data = (
                conversation_id,
                message_type,
                content,
                response_time,
                model_used,
                json.dumps(metadata) if metadata else None
            )
            
            self.cursor.execute(query, data)
            self.connection.commit()
            message_id = self.cursor.lastrowid
            
            # Atualizar timestamp da conversa
            self._update_conversation_timestamp(conversation_id)
            
            logger.debug(f"💬 Mensagem salva: ID={message_id}, Tipo={message_type}")
            return message_id
            
        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao salvar mensagem: {e}")
            return None
    
    def get_conversation_history(self, conversation_id: int, limit: int = 50) -> List[Dict]:
        """
        Obtém o histórico de mensagens de uma conversa
        
        Args:
            conversation_id: ID da conversa
            limit: Limite de mensagens a retornar
        
        Returns:
            List[Dict]: Lista de mensagens
        """
        try:
            query = """
                SELECT * FROM messages 
                WHERE conversation_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """
            
            self.cursor.execute(query, (conversation_id, limit))
            messages = [dict(row) for row in self.cursor.fetchall()]
            
            # Processar metadados JSON
            for message in messages:
                if message.get('metadata'):
                    message['metadata'] = json.loads(message['metadata'])
            
            return list(reversed(messages))  # Retornar em ordem cronológica
            
        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao buscar histórico: {e}")
            return []
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """
        Obtém conversas recentes
        
        Args:
            limit: Número de conversas a retornar
        
        Returns:
            List[Dict]: Lista de conversas
        """
        try:
            query = """
                SELECT c.*, COUNT(m.id) as message_count
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.is_active = 1
                GROUP BY c.id
                ORDER BY c.updated_at DESC
                LIMIT ?
            """
            
            self.cursor.execute(query, (limit,))
            conversations = [dict(row) for row in self.cursor.fetchall()]
            
            # Processar metadados JSON
            for conv in conversations:
                if conv.get('metadata'):
                    conv['metadata'] = json.loads(conv['metadata'])
            
            return conversations
            
        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao buscar conversas recentes: {e}")
            return []
    
    def _update_conversation_timestamp(self, conversation_id: int):
        """
        Atualiza o timestamp de última atividade da conversa
        
        Args:
            conversation_id: ID da conversa
        """
        try:
            query = "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            self.cursor.execute(query, (conversation_id,))
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao atualizar timestamp da conversa: {e}")
    
    def search_messages(self, search_term: str, limit: int = 20) -> List[Dict]:
        """
        Busca mensagens por conteúdo
        
        Args:
            search_term: Termo de busca
            limit: Limite de resultados
        
        Returns:
            List[Dict]: Lista de mensagens encontradas
        """
        try:
            query = """
                SELECT m.*, c.title as conversation_title
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE m.content LIKE ?
                ORDER BY m.timestamp DESC
                LIMIT ?
            """
            
            # Usar LIKE com wildcards para busca simples
            search_pattern = f"%{search_term}%"
            self.cursor.execute(query, (search_pattern, limit))
            results = [dict(row) for row in self.cursor.fetchall()]
            
            # Processar metadados JSON
            for result in results:
                if result.get('metadata'):
                    result['metadata'] = json.loads(result['metadata'])
            
            return results
            
        except sqlite3.Error as e:
            logger.error(f"❌ Erro na busca: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de uso
        
        Returns:
            Dict: Estatísticas diversas
        """
        try:
            stats = {}
            
            # Total de conversas
            self.cursor.execute("SELECT COUNT(*) as count FROM conversations WHERE is_active = 1")
            stats['total_conversations'] = dict(self.cursor.fetchone())['count']
            
            # Total de mensagens
            self.cursor.execute("SELECT COUNT(*) as count FROM messages")
            stats['total_messages'] = dict(self.cursor.fetchone())['count']
            
            # Mensagens por tipo
            self.cursor.execute("""
                SELECT message_type, COUNT(*) as count 
                FROM messages 
                GROUP BY message_type
            """)
            stats['messages_by_type'] = {dict(row)['message_type']: dict(row)['count'] for row in self.cursor.fetchall()}
            
            # Personalidades mais usadas
            self.cursor.execute("""
                SELECT personality, COUNT(*) as count 
                FROM conversations 
                WHERE is_active = 1
                GROUP BY personality 
                ORDER BY count DESC
            """)
            stats['personalities'] = {dict(row)['personality']: dict(row)['count'] for row in self.cursor.fetchall()}
            
            return stats
            
        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

# Função auxiliar para gerar session_id único
def generate_session_id() -> str:
    """
    Gera um ID único para a sessão
    
    Returns:
        str: Session ID único
    """
    import uuid
    return f"alex_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"