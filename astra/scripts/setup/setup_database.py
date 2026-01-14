#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal
Setup da Base de Dados SQLite

Script para configurar a base de dados SQLite e criar as tabelas iniciais.
Deve ser executado antes de usar o assistente pela primeira vez.
"""

import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from database.database_manager import DatabaseManager, DatabaseConfig

def print_header():
    """Imprime o cabeçalho do script"""
    print("=" * 60)
    print("🤖 ASTRA - Assistente Pessoal")
    print("   Configuração da Base de Dados SQLite")
    print("=" * 60)
    print()

def get_database_config():
    """
    Obtém configurações da base de dados SQLite do utilizador
    
    Returns:
        DatabaseConfig: Configuração da base de dados
    """
    print("📋 Configuração da Base de Dados SQLite:")
    print("-" * 40)
    
    # Caminho do arquivo da base de dados
    default_path = "ASTRA_assistant.db"
    db_path = input(f"💾 Caminho do arquivo da base de dados [{default_path}]: ").strip()
    if not db_path:
        db_path = default_path
    
    print(f"\nℹ️ A base de dados será criada em: {Path(db_path).absolute()}")
    
    return DatabaseConfig(database_path=db_path)

def test_connection(config: DatabaseConfig):
    """
    Testa a conexão com SQLite
    
    Args:
        config: Configuração da base de dados
    
    Returns:
        bool: True se a conexão foi bem-sucedida
    """
    print("\n🔍 Testando conexão com SQLite...")
    
    try:
        db_manager = DatabaseManager(config)
        if db_manager.connect():
            print("✅ Conexão estabelecida com sucesso!")
            
            # Obter informações da base de dados
            stats = db_manager.get_statistics()
            print(f"📊 Estatísticas iniciais:")
            print(f"   - Conversas: {stats.get('total_conversations', 0)}")
            print(f"   - Mensagens: {stats.get('total_messages', 0)}")
            
            db_manager.disconnect()
            return True
        else:
            print("❌ Falha na conexão com SQLite")
            return False
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def create_config_file(config: DatabaseConfig):
    """
    Cria ficheiro de configuração para o assistente
    
    Args:
        config: Configuração da base de dados
    """
    config_content = f"""# Configuração SQLite para ASTRA Assistente
# Gerado automaticamente pelo setup_database.py

[sqlite]
database_path = {config.database_path}

# Configurações adicionais
check_same_thread = false
timeout = 30.0
foreign_keys = true
"""
    
    config_file = Path(__file__).parent.parent / "config" / "database.ini"
    
    # Criar diretório se não existir
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ Ficheiro de configuração criado: {config_file}")
        
    except Exception as e:
        print(f"❌ Erro ao criar ficheiro de configuração: {e}")

def show_db_instructions():
    """Mostra instruções para usar ferramentas SQLite"""
    print("\n" + "=" * 60)
    print("📊 INSTRUÇÕES PARA VISUALIZAR A BASE DE DADOS")
    print("=" * 60)
    print()
    print("Para visualizar/gerir a base de dados SQLite:")
    print()
    print("1. 🔧 Ferramentas Recomendadas:")
    print("   - DB Browser for SQLite (gratuito)")
    print("   - SQLiteStudio (gratuito)")
    print("   - DBeaver (gratuito)")
    print("   - HeidiSQL (suporta SQLite)")
    print()
    print("2. 📊 Tabelas Criadas:")
    print("   - conversations: Dados das conversas")
    print("   - messages: Mensagens trocadas")
    print("   - voice_interactions: Interações por voz")
    print("   - user_preferences: Preferências do utilizador")
    print("   - people: Informações sobre pessoas")
    print()
    print("3. 🔍 Consultas Úteis:")
    print("   - SELECT * FROM conversations ORDER BY updated_at DESC;")
    print("   - SELECT * FROM messages WHERE message_type = 'user' LIMIT 10;")
    print("   - SELECT COUNT(*) as total FROM messages;")
    print("   - PRAGMA table_info(conversations); -- Informações da tabela")
    print()

def main():
    """Função principal do setup"""
    print_header()
    
    # Verificar se sqlite3 está disponível (faz parte da biblioteca padrão)
    try:
        import sqlite3
        print("✅ SQLite disponível")
    except ImportError:
        print("❌ SQLite não encontrado! (Isto é muito raro)")
        return False
    
    # Obter configuração
    config = get_database_config()
    
    # Testar conexão e criar estrutura
    if test_connection(config):
        print("\n🎉 Base de dados SQLite configurada com sucesso!")
        
        # Criar ficheiro de configuração
        create_config_file(config)
        
        # Mostrar instruções para ferramentas SQLite
        show_db_instructions()
        
        print("\n" + "=" * 60)
        print("✅ SETUP CONCLUÍDO!")
        print("   Pode agora executar: python assistente.py")
        print("=" * 60)
        
        return True
    else:
        print("\n❌ Falha na configuração da base de dados")
        print("   Verifique as configurações e tente novamente")
        return False

if __name__ == "__main__":
    success = main()
    
    input("\nPressione Enter para sair...")
    
    sys.exit(0 if success else 1)
