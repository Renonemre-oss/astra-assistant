#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TESTE DO SISTEMA DE PESSOAS - VERSÃO CORRIGIDA
Teste simplificado para validar as correções no reconhecimento de pessoas.
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.people_manager import PeopleManager
from database.database_manager import DatabaseManager

def test_simple_people_detection():
    """Teste simples de detecção de pessoas."""
    print("🧪 TESTE SIMPLES DE DETECÇÃO DE PESSOAS")
    print("=" * 50)
    
    # Inicializar o sistema
    people_manager = PeopleManager()
    
    # Casos de teste específicos
    test_cases = [
        {
            'text': 'A minha irmã Ana tem 25 anos e trabalha como professora.',
            'expected_name': 'Ana',
            'expected_relationship': 'irmã'
        },
        {
            'text': 'O meu amigo João é muito engraçado.',
            'expected_name': 'João',
            'expected_relationship': 'amigo'
        },
        {
            'text': 'A minha colega Sofia é engenheira de software.',
            'expected_name': 'Sofia',
            'expected_relationship': 'colega'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Teste {i}: {case['text']}")
        
        # Detectar menções
        mentions = people_manager._detect_people_mentions(case['text'].lower())
        print(f"   Menções detectadas: {mentions}")
        
        # Verificar se detectou corretamente
        found_names = [m.get('name') for m in mentions if m.get('name')]
        found_relations = [m.get('relationship') for m in mentions if m.get('relationship')]
        
        print(f"   Nomes encontrados: {found_names}")
        print(f"   Relacionamentos encontrados: {found_relations}")
        
        # Validar resultados
        name_ok = case['expected_name'] in found_names if case.get('expected_name') else True
        relation_ok = case['expected_relationship'] in found_relations if case.get('expected_relationship') else True
        
        if name_ok and relation_ok:
            print("   ✅ PASSOU")
        else:
            print("   ❌ FALHOU")
    
    print("\n" + "=" * 50)
    print("✅ Teste de detecção concluído!")

def test_information_extraction():
    """Teste de extração de informações."""
    print("\n🧪 TESTE DE EXTRAÇÃO DE INFORMAÇÕES")
    print("=" * 50)
    
    people_manager = PeopleManager()
    
    text = "A minha irmã Ana tem 25 anos e trabalha como professora. Ela gosta muito de ler livros."
    mentions = people_manager._detect_people_mentions(text.lower())
    
    print(f"Texto: {text}")
    print(f"Menções detectadas: {mentions}")
    
    for mention in mentions:
        extracted = people_manager._extract_person_information(text.lower(), mention)
        if extracted:
            print(f"\nInformações extraídas para {mention}:")
            for key, value in extracted.items():
                if value:
                    print(f"  {key}: {value}")
        else:
            print(f"\nNenhuma informação significativa extraída para {mention}")
    
    print("\n" + "=" * 50)
    print("✅ Teste de extração concluído!")

if __name__ == "__main__":
    print("🎯 TESTE DO SISTEMA DE PESSOAS (VERSÃO CORRIGIDA)")
    print("=" * 60)
    
    test_simple_people_detection()
    test_information_extraction()
    
    print("\n✅ Todos os testes concluídos!")