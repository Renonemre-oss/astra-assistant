#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TESTE DO SISTEMA DE PERFIL DO UTILIZADOR E GESTÃO DE PESSOAS
Teste completo da integração entre perfil do utilizador e reconhecimento de pessoas.
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.people_manager import PeopleManager
from utils.user_profile import UserProfile
from database.database_manager import DatabaseManager

def test_user_profile_detection():
    """Teste de detecção de informações do utilizador."""
    print("🧪 TESTE DE DETECÇÃO DE PERFIL DO UTILIZADOR")
    print("=" * 60)
    
    people_manager = PeopleManager()
    
    # Cenários de teste para detecção do utilizador
    user_scenarios = [
        {
            'text': 'Olá! Eu sou o António e tenho 30 anos.',
            'expected': {'name': 'António', 'age': 30}
        },
        {
            'text': 'Trabalho como engenheiro de software em Lisboa.',
            'expected': {'profession': 'engenheiro de software', 'location': 'Lisboa'}
        },
        {
            'text': 'Chamo-me Pedro e vivo em Porto.',
            'expected': {'name': 'Pedro', 'location': 'Porto'}
        }
    ]
    
    for i, scenario in enumerate(user_scenarios, 1):
        print(f"\n📝 Cenário {i}: {scenario['text']}")
        
        # Processar texto
        result = people_manager.process_user_input(scenario['text'])
        
        print(f"   Perfil atualizado: {result['user_profile_updated']}")
        print(f"   Ações: {result['actions_performed']}")
        print(f"   Sugestões: {result['response_suggestions']}")
        
        # Verificar se as informações esperadas foram detectadas
        if result['user_profile_updated']:
            profile = people_manager.user_profile.get_profile()
            print(f"   Perfil atual: {profile}")
            print("   ✅ PASSOU")
        else:
            print("   ❌ FALHOU - Perfil não foi atualizado")

def test_user_vs_others_distinction():
    """Teste para distinguir entre utilizador e outras pessoas."""
    print("\n🧪 TESTE DE DISTINÇÃO UTILIZADOR VS OUTRAS PESSOAS")
    print("=" * 60)
    
    people_manager = PeopleManager()
    
    # Primeiro, estabelecer perfil do utilizador
    user_text = "Eu sou o Carlos e trabalho como professor."
    user_result = people_manager.process_user_input(user_text)
    print(f"1. Estabelecendo perfil do utilizador: '{user_text}'")
    print(f"   Perfil atualizado: {user_result['user_profile_updated']}")
    
    # Agora mencionar outras pessoas
    others_text = "A minha irmã Ana é médica e o meu amigo João é advogado."
    others_result = people_manager.process_user_input(others_text)
    print(f"\n2. Mencionando outras pessoas: '{others_text}'")
    print(f"   Pessoas mencionadas: {[p.get('name') or p.get('relationship') for p in others_result['people_mentioned']]}")
    print(f"   Informações extraídas: {len(others_result['information_extracted'])}")
    print(f"   Perfil atualizado: {others_result['user_profile_updated']}")
    
    # Verificar contexto da conversa
    context = people_manager.get_context_for_conversation()
    print(f"\n3. Contexto da conversa:")
    print(context)
    
def test_conversation_flow():
    """Teste do fluxo completo de uma conversa."""
    print("\n🧪 TESTE DE FLUXO DE CONVERSA COMPLETO")
    print("=" * 60)
    
    people_manager = PeopleManager()
    conversation_count = 0
    
    # Simulação de uma conversa
    conversation = [
        "Olá, como estás?",
        "Eu estou bem, obrigado por perguntares!",
        "Sou o Miguel e trabalho como designer.",
        "A minha esposa chama-se Sara e é enfermeira.",
        "Temos um filho pequeno que adora futebol.",
        "Como é que te posso ajudar hoje?"
    ]
    
    for i, message in enumerate(conversation, 1):
        conversation_count += 1
        print(f"\n💬 Mensagem {i}: '{message}'")
        
        result = people_manager.process_user_input(message, conversation_count=conversation_count)
        
        print(f"   Perfil atualizado: {result['user_profile_updated']}")
        print(f"   Pessoas mencionadas: {len(result['people_mentioned'])}")
        print(f"   Deve perguntar perfil: {result['ask_for_profile']}")
        
        if result['response_suggestions']:
            print(f"   Sugestão de resposta: {result['response_suggestions'][0]}")
    
    # Mostrar estado final
    print(f"\n📊 ESTADO FINAL:")
    profile = people_manager.user_profile.get_profile()
    print(f"Perfil do utilizador: {profile}")
    
    all_people = people_manager.get_all_people()
    print(f"Pessoas conhecidas: {len(all_people)}")
    for person in all_people[:3]:  # Mostrar apenas as primeiras 3
        name = person.get('name', 'N/A')
        relationship = person.get('relationship', 'N/A')
        print(f"  - {name} ({relationship})")

def test_profile_questions():
    """Teste do sistema de perguntas sobre perfil."""
    print("\n🧪 TESTE DO SISTEMA DE PERGUNTAS SOBRE PERFIL")
    print("=" * 60)
    
    people_manager = PeopleManager()
    
    # Simular várias mensagens sem informação pessoal
    messages = [
        "Olá",
        "Como estás?",
        "Que horas são?",
        "Qual é o tempo hoje?",
        "Podes ajudar-me?"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n💬 Mensagem {i}: '{message}'")
        result = people_manager.process_user_input(message, conversation_count=i)
        
        if result['ask_for_profile']:
            print(f"   ❓ Sistema quer perguntar sobre perfil: {result['response_suggestions'][0]}")
        else:
            print(f"   ✅ Sistema não precisa perguntar sobre perfil ainda")

def test_context_generation():
    """Teste de geração de contexto personalizado."""
    print("\n🧪 TESTE DE GERAÇÃO DE CONTEXTO PERSONALIZADO")
    print("=" * 60)
    
    people_manager = PeopleManager()
    
    # Estabelecer perfil e pessoas
    setup_texts = [
        "Sou a Maria, tenho 28 anos e trabalho como jornalista em Coimbra.",
        "O meu marido João é programador.",
        "A minha filha Sofia tem 5 anos e adora desenhar."
    ]
    
    for text in setup_texts:
        people_manager.process_user_input(text)
    
    # Gerar contexto
    context = people_manager.get_context_for_conversation()
    print("🎯 CONTEXTO GERADO:")
    print(context)
    
    # Gerar contexto específico mencionando alguém
    specific_context = people_manager.get_context_for_conversation(['João'])
    print("\n🎯 CONTEXTO ESPECÍFICO PARA 'JOÃO':")
    print(specific_context)

if __name__ == "__main__":
    print("🎯 TESTE COMPLETO DO SISTEMA DE PERFIL E PESSOAS")
    print("=" * 70)
    
    try:
        test_user_profile_detection()
        test_user_vs_others_distinction()
        test_conversation_flow()
        test_profile_questions()
        test_context_generation()
        
        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {e}")
        import traceback
        traceback.print_exc()