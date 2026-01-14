#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal
Teste Completo do Sistema de Pessoas

Script para demonstrar o funcionamento automático do sistema de reconhecimento
e armazenamento de informações sobre pessoas.
"""

import sys
import os
import logging

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.people_manager import PeopleManager
from database.database_manager import DatabaseManager, DatabaseConfig
from ..config import DATABASE_AVAILABLE

# Configurar logging mais limpo para o teste
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

def test_complete_people_system():
    """Teste completo do sistema de gestão de pessoas."""
    print("\n🎯 TESTE COMPLETO DO SISTEMA DE PESSOAS")
    print("=" * 50)
    
    # Inicializar o sistema
    db_manager = None
    if DATABASE_AVAILABLE:
        try:
            db_config = DatabaseConfig()
            db_manager = DatabaseManager(db_config)
            if db_manager.connect():
                print("✅ Base de dados conectada")
            else:
                print("⚠️ Usando modo local")
                db_manager = None
        except:
            print("⚠️ Erro na base de dados, usando modo local")
            db_manager = None
    
    people_manager = PeopleManager(db_manager)
    
    # Cenários de teste
    test_scenarios = [
        {
            "name": "Apresentação de família",
            "text": "A minha irmã Ana tem 25 anos e trabalha como professora. Ela gosta muito de ler livros e ouvir música clássica.",
            "expected": "Deve reconhecer Ana como irmã, idade 25, profissão professora, gostos de leitura e música clássica"
        },
        {
            "name": "Informação sobre amigo",
            "text": "O meu amigo João é muito engraçado e adora jogar futebol. A comida favorita dele é lasanha.",
            "expected": "Deve reconhecer João como amigo, personalidade engraçada, gosta de futebol, comida favorita lasanha"
        },
        {
            "name": "Informação sobre colega",
            "text": "A minha colega Sofia é super inteligente e está sempre a beber café. Ela é engenheira de software.",
            "expected": "Deve reconhecer Sofia como colega, inteligente, bebe café, engenheira de software"
        },
        {
            "name": "Pergunta sobre pessoa conhecida",
            "text": "Como é a Ana?",
            "expected": "Deve dar informações sobre a Ana previamente registada"
        },
        {
            "name": "Pergunta sobre gostos",
            "text": "O que gosta o João?",
            "expected": "Deve listar os gostos do João"
        }
    ]
    
    print(f"\n🧪 Executando {len(test_scenarios)} cenários de teste...\n")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"📝 Teste {i}: {scenario['name']}")
        print(f"Entrada: '{scenario['text']}'")
        print(f"Esperado: {scenario['expected']}")
        
        # Processar o texto
        result = people_manager.process_user_input(scenario['text'])
        
        print("Resultado:")
        if result['response_suggestions']:
            print(f"  💬 Resposta: {result['response_suggestions'][0]}")
        if result['actions_performed']:
            print(f"  ✅ Ações: {', '.join(result['actions_performed'])}")
        if result['people_mentioned']:
            people_names = [p.get('name') or p.get('relationship') for p in result['people_mentioned'][:3]]
            print(f"  👥 Pessoas detetadas: {', '.join(filter(None, people_names))}")
        
        print("-" * 40)
    
    # Mostrar resumo das pessoas conhecidas
    print("\n👥 RESUMO DE PESSOAS CONHECIDAS:")
    all_people = people_manager.get_all_people()
    
    if all_people:
        for person in all_people[:5]:  # Mostrar as primeiras 5
            name = person.get('name', 'Pessoa sem nome')
            relationship = person.get('relationship', 'N/A')
            age = f", {person['age']} anos" if person.get('age') else ""
            profession = f", {person['profession']}" if person.get('profession') else ""
            print(f"  • {name} (Relação: {relationship}{age}{profession})")
    else:
        print("  Nenhuma pessoa registada ainda.")
    
    # Teste de contexto para conversas
    print("\n🔄 TESTE DE CONTEXTO PARA CONVERSAS:")
    context = people_manager.get_context_for_conversation(['Ana', 'João'])
    if context:
        print("Contexto gerado:")
        print(context)
    else:
        print("Nenhum contexto gerado.")
    
    print("\n✅ Teste completo finalizado!")
    
    if db_manager:
        db_manager.disconnect()


if __name__ == "__main__":
    test_complete_people_system()
