#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal
Database Manager - Gerenciamento de Base de Dados (SQLite ou MySQL)

Este módulo fornece funcionalidades para:
- Conectar ao SQLite (padrão, local) ou MySQL (ex.: Railway) via DATABASE_URL
- Criar tabelas necessárias
- Salvar/recuperar conversas
- Gerenciar histórico de interações

Para usar MySQL, define a variável de ambiente DATABASE_URL, por exemplo:
    DATABASE_URL=mysql://user:password@host:port/database
Sem DATABASE_URL, usa SQLite local (comportamento anterior).
"""

import sqlite3
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, unquote

logger = logging.getLogger(__name__)

try:
    import pymysql
    import pymysql.cursors

    PYMYSQL_AVAILABLE = True
    _DB_ERRORS = (sqlite3.Error, pymysql.MySQLError)
except ImportError:
    pymysql = None
    PYMYSQL_AVAILABLE = False
    _DB_ERRORS = (sqlite3.Error,)


def _default_database_url() -> Optional[str]:
    """Lê o DATABASE_URL do ambiente (MYSQL_URL é o alias usado pelo Railway)."""
    return os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")


@dataclass
class DatabaseConfig:
    """Configuração da base de dados (SQLite por padrão, MySQL via DATABASE_URL)"""
    database_path: str = "ASTRA_assistant.db"
    database_url: Optional[str] = field(default_factory=_default_database_url)

    @property
    def engine(self) -> str:
        """'mysql' se houver DATABASE_URL mysql://, caso contrário 'sqlite'."""
        # Bases em memória são sempre SQLite (usado nos testes)
        if self.database_path == ":memory:":
            return "sqlite"
        if self.database_url and self.database_url.startswith("mysql"):
            return "mysql"
        return "sqlite"

    def get_full_path(self) -> Path:
        """Retorna o caminho completo do arquivo da base de dados SQLite"""
        if os.path.isabs(self.database_path):
            return Path(self.database_path)
        else:
            # Por padrão, salva na pasta database do projeto
            return Path(__file__).parent / self.database_path

    def get_mysql_params(self) -> Dict[str, Any]:
        """Extrai os parâmetros de conexão do DATABASE_URL mysql://"""
        parsed = urlparse(self.database_url)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 3306,
            "user": unquote(parsed.username or "root"),
            "password": unquote(parsed.password or ""),
            "database": parsed.path.lstrip("/") or "astra",
        }


# DDL por engine: MySQL exige VARCHAR para colunas UNIQUE e usa AUTO_INCREMENT
_TABLES_SQLITE = {
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
    """,
}

_TABLES_MYSQL = {
    'conversations': """
        CREATE TABLE IF NOT EXISTS conversations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            title VARCHAR(255) DEFAULT 'Nova Conversa',
            personality VARCHAR(64) DEFAULT 'neutra',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            metadata TEXT DEFAULT NULL
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    """,
    'messages': """
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            conversation_id INT NOT NULL,
            message_type VARCHAR(16) NOT NULL CHECK(message_type IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            response_time DOUBLE DEFAULT NULL,
            token_count INT DEFAULT NULL,
            model_used VARCHAR(128) DEFAULT NULL,
            metadata TEXT DEFAULT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    """,
    'voice_interactions': """
        CREATE TABLE IF NOT EXISTS voice_interactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            conversation_id INT NOT NULL,
            audio_duration DOUBLE DEFAULT NULL,
            recognition_confidence DOUBLE DEFAULT NULL,
            tts_enabled BOOLEAN DEFAULT 1,
            voice_command BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT DEFAULT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    """,
    'user_preferences': """
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INT AUTO_INCREMENT PRIMARY KEY,
            preference_key VARCHAR(255) NOT NULL UNIQUE,
            preference_value TEXT NOT NULL,
            data_type VARCHAR(16) DEFAULT 'string' CHECK(data_type IN ('string', 'integer', 'float', 'boolean', 'json')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    """,
    'people': """
        CREATE TABLE IF NOT EXISTS people (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            nickname VARCHAR(255) DEFAULT NULL,
            relationship VARCHAR(128) DEFAULT NULL,
            age INT DEFAULT NULL,
            gender VARCHAR(32) DEFAULT NULL CHECK(gender IN ('masculino', 'feminino', 'não-binário', 'outro', 'prefere_nao_dizer')),
            sexuality VARCHAR(64) DEFAULT NULL,
            personality_traits TEXT DEFAULT NULL,
            interests TEXT DEFAULT NULL,
            favorite_foods TEXT DEFAULT NULL,
            favorite_music TEXT DEFAULT NULL,
            favorite_movies TEXT DEFAULT NULL,
            favorite_activities TEXT DEFAULT NULL,
            dislikes TEXT DEFAULT NULL,
            profession VARCHAR(128) DEFAULT NULL,
            birthday DATE DEFAULT NULL,
            contact_info TEXT DEFAULT NULL,
            notes TEXT DEFAULT NULL,
            importance_level VARCHAR(16) DEFAULT 'média' CHECK(importance_level IN ('baixa', 'média', 'alta', 'muito_alta')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    """,
}


class DatabaseManager:
    """
    Gerenciador de base de dados para o assistente ASTRA.

    Usa SQLite local por padrão; se DATABASE_URL (mysql://...) estiver
    definido, liga ao MySQL (ex.: Railway) com fallback para SQLite
    quando a ligação remota falha.
    """

    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.connection = None
        self.cursor = None
        self.engine = self.config.engine

    def connect(self) -> bool:
        """
        Estabelece conexão com a base de dados.

        Returns:
            bool: True se conectou com sucesso, False caso contrário
        """
        if self.engine == "mysql":
            if self._connect_mysql():
                return True
            logger.warning("A recorrer ao SQLite local como fallback.")
            self.engine = "sqlite"
        return self._connect_sqlite()

    def _connect_mysql(self) -> bool:
        """Liga ao MySQL definido em DATABASE_URL (ex.: Railway)."""
        if not PYMYSQL_AVAILABLE:
            logger.error(
                "DATABASE_URL mysql:// definido mas o PyMySQL não está instalado. "
                "Usa: pip install pymysql"
            )
            return False
        try:
            params = self.config.get_mysql_params()
            self.connection = pymysql.connect(
                cursorclass=pymysql.cursors.DictCursor,
                charset="utf8mb4",
                connect_timeout=10,
                autocommit=False,
                **params,
            )
            self.cursor = self.connection.cursor()
            logger.info(
                f"✅ Conectado ao MySQL: {params['host']}:{params['port']}/{params['database']}"
            )
            self._create_tables()
            return True
        except pymysql.MySQLError as e:
            logger.error(f"Erro ao conectar ao MySQL: {e}")
            self.connection = None
            self.cursor = None
            return False

    def _connect_sqlite(self) -> bool:
        """Liga ao SQLite local."""
        try:
            if self.config.database_path == ":memory:":
                db_path = ":memory:"
            else:
                full_path = self.config.get_full_path()
                # Criar diretório se não existir
                full_path.parent.mkdir(parents=True, exist_ok=True)
                db_path = str(full_path)

            self.connection = sqlite3.connect(
                db_path,
                check_same_thread=False,  # Permite uso em threads
                timeout=30.0  # Timeout em segundos
            )

            # Configurar SQLite para retornar dicionários
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()

            # Habilitar chaves estrangeiras
            self.cursor.execute("PRAGMA foreign_keys = ON")

            logger.info(f"Conectado ao SQLite: {db_path}")

            # Criar tabelas se não existirem
            self._create_tables()

            return True

        except sqlite3.Error as e:
            logger.error(f"Erro ao conectar ao SQLite: {e}")
            return False

    def disconnect(self):
        """
        Fecha a conexão com a base de dados
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
                logger.info("Conexão com a base de dados fechada")
        except _DB_ERRORS as e:
            logger.error(f"Erro ao fechar conexão: {e}")

    def _execute(self, query: str, params: tuple = ()):
        """Executa uma query, adaptando o placeholder ao engine ativo."""
        if self.engine == "mysql":
            query = query.replace("?", "%s")
        self.cursor.execute(query, params)

    def _row_to_dict(self, row) -> Optional[Dict]:
        """Normaliza uma linha (sqlite3.Row ou dict do PyMySQL) para dict."""
        if row is None:
            return None
        return dict(row)

    def _create_tables(self):
        """
        Cria todas as tabelas necessárias
        """
        tables = _TABLES_MYSQL if self.engine == "mysql" else _TABLES_SQLITE

        for table_name, create_query in tables.items():
            try:
                self.cursor.execute(create_query)
                self.connection.commit()
                logger.debug(f"Tabela '{table_name}' verificada/criada")
            except _DB_ERRORS as e:
                logger.error(f"Erro ao criar tabela '{table_name}': {e}")
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

            self._execute(query, data)
            self.connection.commit()
            conversation_id = self.cursor.lastrowid

            logger.info(f"Nova conversa criada: ID={conversation_id}, Session={session_id}")
            return conversation_id

        except _DB_ERRORS as e:
            logger.error(f"Erro ao criar conversa: {e}")
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
            self._execute(query, (session_id,))
            result = self._row_to_dict(self.cursor.fetchone())

            if result and result.get('metadata'):
                result['metadata'] = json.loads(result['metadata'])

            return result

        except _DB_ERRORS as e:
            logger.error(f"Erro ao buscar conversa: {e}")
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

            self._execute(query, data)
            self.connection.commit()
            message_id = self.cursor.lastrowid

            # Atualizar timestamp da conversa
            self._update_conversation_timestamp(conversation_id)

            logger.debug(f"Mensagem salva: ID={message_id}, Tipo={message_type}")
            return message_id

        except _DB_ERRORS as e:
            logger.error(f"Erro ao salvar mensagem: {e}")
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

            self._execute(query, (conversation_id, limit))
            messages = [self._row_to_dict(row) for row in self.cursor.fetchall()]

            # Processar metadados JSON
            for message in messages:
                if message.get('metadata'):
                    message['metadata'] = json.loads(message['metadata'])

            return list(reversed(messages))  # Retornar em ordem cronológica

        except _DB_ERRORS as e:
            logger.error(f"Erro ao buscar histórico: {e}")
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

            self._execute(query, (limit,))
            conversations = [self._row_to_dict(row) for row in self.cursor.fetchall()]

            # Processar metadados JSON
            for conv in conversations:
                if conv.get('metadata'):
                    conv['metadata'] = json.loads(conv['metadata'])

            return conversations

        except _DB_ERRORS as e:
            logger.error(f"Erro ao buscar conversas recentes: {e}")
            return []

    def _update_conversation_timestamp(self, conversation_id: int):
        """
        Atualiza o timestamp de última atividade da conversa

        Args:
            conversation_id: ID da conversa
        """
        try:
            query = "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            self._execute(query, (conversation_id,))
            self.connection.commit()
        except _DB_ERRORS as e:
            logger.error(f"Erro ao atualizar timestamp da conversa: {e}")

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
            self._execute(query, (search_pattern, limit))
            results = [self._row_to_dict(row) for row in self.cursor.fetchall()]

            # Processar metadados JSON
            for result in results:
                if result.get('metadata'):
                    result['metadata'] = json.loads(result['metadata'])

            return results

        except _DB_ERRORS as e:
            logger.error(f"Erro na busca: {e}")
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
            self._execute("SELECT COUNT(*) as count FROM conversations WHERE is_active = 1")
            stats['total_conversations'] = self._row_to_dict(self.cursor.fetchone())['count']

            # Total de mensagens
            self._execute("SELECT COUNT(*) as count FROM messages")
            stats['total_messages'] = self._row_to_dict(self.cursor.fetchone())['count']

            # Mensagens por tipo
            self._execute("""
                SELECT message_type, COUNT(*) as count
                FROM messages
                GROUP BY message_type
            """)
            stats['messages_by_type'] = {
                row['message_type']: row['count']
                for row in map(self._row_to_dict, self.cursor.fetchall())
            }

            # Personalidades mais usadas
            self._execute("""
                SELECT personality, COUNT(*) as count
                FROM conversations
                WHERE is_active = 1
                GROUP BY personality
                ORDER BY count DESC
            """)
            stats['personalities'] = {
                row['personality']: row['count']
                for row in map(self._row_to_dict, self.cursor.fetchall())
            }

            return stats

        except _DB_ERRORS as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
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
    return f"ASTRA_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
