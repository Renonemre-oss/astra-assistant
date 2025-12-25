#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste rápido do sistema de preferências do ALEX
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database_manager import DatabaseManager, DatabaseConfig
import json

def test_preferences():
        print("🧪 TESTE DO SISTEMA DE PREFERÊNCIAS")
        print("=" * 50)
        
        # 1. Testar database
        try:
            config = DatabaseConfig()
            db = DatabaseManager(config)
            
            if db.connect():
                print("✅ Base de dados conectada")
                
                # Testar inserção manual
                db.cursor.execute("""
                    INSERT INTO user_preferences (preference_key, preference_value, data_type)
                    VALUES ('comida_favorita_teste', 'pizza', 'string')
                    ON DUPLICATE KEY UPDATE preference_value = VALUES(preference_value)
                """)
                
                # Verificar se foi inserido
                db.cursor.execute("SELECT * FROM user_preferences WHERE preference_key = 'comida_favorita_teste'")
                result = db.cursor.fetchone()
                
                if result:
                    print(f"✅ Teste BD bem-sucedido: {result}")
                else:
                    print("❌ Falha no teste BD")
                    
                db.disconnect()
            else:
                print("❌ Falha na conexão BD")
                
        except Exception as e:
            print(f"❌ Erro BD: {e}")
        
        # 2. Testar ficheiro local
        try:
            facts_file = Path(__file__).parent / "data" / "personal_facts.json"
            facts_file.parent.mkdir(exist_ok=True)
            
            # Criar dados de teste
            test_facts = {"comida_favorita": "pizza", "cor_favorita": "azul"}
            
            with open(facts_file, 'w', encoding='utf-8') as f:
                json.dump(test_facts, f, indent=2, ensure_ascii=False)
            
            # Ler de volta
            with open(facts_file, 'r', encoding='utf-8') as f:
                loaded_facts = json.load(f)
                
            print(f"✅ Ficheiro local: {loaded_facts}")
            
        except Exception as e:
            print(f"❌ Erro ficheiro local: {e}")
        
        # 3. Testar pattern matching
        print("\n🔍 TESTE DE PATTERNS:")
        
        test_phrases = [
            "a minha comida favorita e pizza",
            "minha comida favorita e pizza", 
            "A minha comida favorita é pizza",
            "qual a minha comida favorita",
            "lembras te da minha comida favorita"
        ]
        
        patterns = {
            'declaracao': ["minha comida favorita e", "a minha comida favorita e"],
            'consulta': ["qual a minha comida favorita", "lembras te da minha comida favorita"]
        }
        
        for phrase in test_phrases:
            phrase_lower = phrase.lower()
            print(f"\n📝 Frase: '{phrase}'")
            
            # Teste declaração
            for pattern in patterns['declaracao']:
                if pattern in phrase_lower:
                    valor = phrase_lower.split(pattern, 1)[1].strip(" .!?:;\n\t")
                    print(f"   ✅ Pattern declaração '{pattern}' → valor: '{valor}'")
                    break
            
            # Teste consulta
            for pattern in patterns['consulta']:
                if pattern in phrase_lower:
                    print(f"   ✅ Pattern consulta '{pattern}' reconhecido")
                    break

if __name__ == "__main__":
    try:
        test_preferences()
        input("\nPressione Enter para sair...")
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        print("Execute primeiro: python setup_database.py")
        input("\nPressione Enter para sair...")
