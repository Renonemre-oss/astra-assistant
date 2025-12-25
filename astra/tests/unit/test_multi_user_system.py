#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TESTE DO SISTEMA MULTI-UTILIZADOR
Teste completo do sistema de identificação de múltiplos utilizadores.
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.multi_user_manager import MultiUserManager
from modules.user_commands import UserCommands

def test_basic_user_identification():
    """Teste básico de identificação de utilizadores."""
    print("🧪 TESTE DE IDENTIFICAÇÃO BÁSICA DE UTILIZADORES")
    print("=" * 60)
    
    multi_user = MultiUserManager()
    
    # Cenários de teste
    scenarios = [
        {
            'text': 'Olá, eu sou o António e trabalho como programador.',
            'expected_name': 'António'
        },
        {
            'text': 'Oi, chamo-me Maria e sou professora em Lisboa.',
            'expected_name': 'Maria'
        },
        {
            'text': 'Como estás? Aqui é o Pedro.',
            'expected_name': 'Pedro'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 Cenário {i}: '{scenario['text']}'")
        
        result = multi_user.process_input(scenario['text'])
        
        print(f"   Utilizador identificado: {result['user_name']}")
        print(f"   Confiança: {result['confidence']:.2f}")
        print(f"   ID: {result['user_id'][:8]}...")
        
        if result['user_name'] == scenario['expected_name']:
            print("   ✅ PASSOU")
        else:
            print("   ❌ FALHOU")

def test_user_switching():
    """Teste de mudança entre utilizadores."""
    print("\n🧪 TESTE DE MUDANÇA ENTRE UTILIZADORES")
    print("=" * 60)
    
    multi_user = MultiUserManager()
    user_commands = UserCommands(multi_user)
    
    # Criar utilizadores iniciais
    multi_user.process_input("Eu sou o João e gosto de futebol.")
    multi_user.process_input("Chamo-me Ana e trabalho como médica.")
    
    print("✅ Utilizadores iniciais criados")
    
    # Teste de comando de listagem
    print("\n1. Testando listagem de utilizadores:")
    list_result = user_commands.process_command("listar utilizadores")
    print(f"   Resultado: {list_result['success']}")
    print(f"   Mensagem: {list_result['message']}")
    
    # Teste de mudança manual
    print("\n2. Testando mudança manual:")
    switch_result = user_commands.process_command("mudar para a Ana")
    print(f"   Resultado: {switch_result['success']}")
    print(f"   Mensagem: {switch_result['message']}")
    
    # Teste de identificação atual
    print("\n3. Testando identificação atual:")
    who_result = user_commands.process_command("quem sou eu")
    print(f"   Resultado: {who_result['success']}")
    print(f"   Mensagem: {who_result['message']}")

def test_conversation_continuity():
    """Teste de continuidade da conversa entre utilizadores."""
    print("\n🧪 TESTE DE CONTINUIDADE DE CONVERSA")
    print("=" * 60)
    
    multi_user = MultiUserManager()
    
    # Simular conversa do João
    print("\n👤 João inicia conversa:")
    messages_joao = [
        "Olá, eu sou o João.",
        "Trabalho como engenheiro em Porto.",
        "Gosto muito de programar.",
    ]
    
    for msg in messages_joao:
        result = multi_user.process_input(msg)
        print(f"   '{msg}' -> {result['user_name']} (conf: {result['confidence']:.2f})")
    
    # Simular mudança para Maria (sem identificação explícita)
    print("\n👤 Maria continua conversa:")
    messages_maria = [
        "Oi! Eu sou a Maria e sou professora.",
        "Vivo em Lisboa há 5 anos.",
        "Adoro ler livros.",
    ]
    
    for msg in messages_maria:
        result = multi_user.process_input(msg)
        print(f"   '{msg}' -> {result['user_name']} (conf: {result['confidence']:.2f})")
    
    # Voltar ao João (usando vocabulário/estilo familiar)
    print("\n👤 João volta à conversa:")
    messages_joao_return = [
        "Já acabei de programar.",
        "O trabalho de engenheiro está difícil.",
        "Como está o tempo no Porto?",
    ]
    
    for msg in messages_joao_return:
        result = multi_user.process_input(msg)
        print(f"   '{msg}' -> {result['user_name']} (conf: {result['confidence']:.2f})")

def test_user_pattern_learning():
    """Teste de aprendizagem de padrões de utilizador."""
    print("\n🧪 TESTE DE APRENDIZAGEM DE PADRÕES")
    print("=" * 60)
    
    multi_user = MultiUserManager()
    
    # Simular várias interações do António
    antonio_messages = [
        "Eu sou o António e trabalho como designer.",
        "Adoro usar exclamações!",
        "Sempre uso pontos de exclamação!",
        "É fantástico trabalhar com design!",
        "Que bom dia hoje!"
    ]
    
    print("🎯 António estabelece padrão (muitas exclamações):")
    for msg in antonio_messages:
        result = multi_user.process_input(msg)
        print(f"   '{msg}'")
    
    # Simular várias interações da Sofia
    sofia_messages = [
        "Chamo-me Sofia e sou contabilista.",
        "Prefiro escrever sem muita pontuação",
        "Trabalho com números todos os dias",
        "É uma profissão que exige precisão",
        "Gosto de manter as coisas simples"
    ]
    
    print("\n🎯 Sofia estabelece padrão (sem exclamações, mais formal):")
    for msg in sofia_messages:
        result = multi_user.process_input(msg)
        print(f"   '{msg}'")
    
    # Teste de reconhecimento baseado em padrões
    print("\n🧠 Teste de reconhecimento por padrões:")
    test_messages = [
        "Que projeto fantástico! Adorei trabalhar nisso!",  # Estilo do António
        "Preciso revisar os números com cuidado",           # Estilo da Sofia
        "Incrível! Que design maravilhoso!"                # Estilo do António
    ]
    
    for msg in test_messages:
        result = multi_user.process_input(msg)
        print(f"   '{msg}' -> {result['user_name']} (conf: {result['confidence']:.2f})")

def test_contextual_identification():
    """Teste de identificação contextual."""
    print("\n🧪 TESTE DE IDENTIFICAÇÃO CONTEXTUAL")
    print("=" * 60)
    
    multi_user = MultiUserManager()
    
    # Estabelecer utilizadores com contextos específicos
    multi_user.process_input("Eu sou o Miguel e trabalho como médico em Coimbra.")
    multi_user.process_input("Chamo-me Carla e sou advogada no Porto.")
    
    # Testes contextuais
    contextual_tests = [
        {
            'text': "Hoje tive uma cirurgia complicada no hospital.",
            'expected': 'Miguel',  # Contexto médico
        },
        {
            'text': "Preciso preparar o caso para tribunal amanhã.",
            'expected': 'Carla',   # Contexto jurídico
        },
        {
            'text': "Como está o tempo em Coimbra hoje?",
            'expected': 'Miguel',  # Contexto de localização
        },
        {
            'text': "O trânsito no Porto está horrível.",
            'expected': 'Carla',   # Contexto de localização
        }
    ]
    
    for i, test in enumerate(contextual_tests, 1):
        print(f"\n🎯 Teste {i}: '{test['text']}'")
        result = multi_user.process_input(test['text'])
        
        print(f"   Esperado: {test['expected']}")
        print(f"   Identificado: {result['user_name']} (conf: {result['confidence']:.2f})")
        
        if result['user_name'] == test['expected']:
            print("   ✅ PASSOU")
        else:
            print("   ❌ FALHOU")

def test_command_system():
    """Teste completo do sistema de comandos."""
    print("\n🧪 TESTE DO SISTEMA DE COMANDOS")
    print("=" * 60)
    
    multi_user = MultiUserManager()
    user_commands = UserCommands(multi_user)
    
    # Criar alguns utilizadores
    multi_user.process_input("Eu sou o Admin e controlo o sistema.")
    
    commands_to_test = [
        "criar utilizador Teste",
        "listar utilizadores",
        "mudar para o Teste",
        "quem sou eu",
        "mudar para Admin",
        "apagar utilizador Teste",
        "listar utilizadores"
    ]
    
    for i, cmd in enumerate(commands_to_test, 1):
        print(f"\n🎯 Comando {i}: '{cmd}'")
        result = user_commands.process_command(cmd)
        
        if result['is_command']:
            print(f"   Tipo: {result['command_type']}")
            print(f"   Sucesso: {result['success']}")
            print(f"   Mensagem: {result['message']}")
        else:
            print("   ❌ Comando não reconhecido")

def test_full_scenario():
    """Teste de cenário completo - família usando o assistente."""
    print("\n🧪 TESTE DE CENÁRIO COMPLETO - FAMÍLIA")
    print("=" * 60)
    
    multi_user = MultiUserManager()
    user_commands = UserCommands(multi_user)
    
    print("👨‍👩‍👧‍👦 Família começa a usar o assistente...")
    
    # Pai usa primeiro
    print("\n👨 Pai:")
    pai_messages = [
        "Olá! Eu sou o Carlos e trabalho como gestor.",
        "Vivo em Lisboa com a minha família.",
        "Gosto de ver futebol nos fins de semana."
    ]
    
    for msg in pai_messages:
        result = multi_user.process_input(msg)
        print(f"   '{msg}' -> Identificado como: {result['user_name']}")
    
    # Mãe usa depois
    print("\n👩 Mãe:")
    mae_messages = [
        "Oi, chamo-me Isabel e sou enfermeira.",
        "Trabalho no hospital de Lisboa.",
        "Adoro cozinhar para a família."
    ]
    
    for msg in mae_messages:
        result = multi_user.process_input(msg)
        print(f"   '{msg}' -> Identificado como: {result['user_name']}")
    
    # Filha usa
    print("\n👧 Filha:")
    filha_messages = [
        "Eu sou a Beatriz e tenho 16 anos!",
        "Estou no secundário e adoro música!",
        "Quero estudar design gráfico!"
    ]
    
    for msg in filha_messages:
        result = multi_user.process_input(msg)
        print(f"   '{msg}' -> Identificado como: {result['user_name']}")
    
    # Teste de reconhecimento automático
    print("\n🧠 Teste de reconhecimento automático:")
    auto_tests = [
        "O jogo do Benfica foi fantástico!",      # Estilo do pai
        "Preciso comprar ingredientes para o jantar.",  # Estilo da mãe  
        "Esta música é incrível! Adoro!!!"       # Estilo da filha
    ]
    
    for msg in auto_tests:
        result = multi_user.process_input(msg)
        print(f"   '{msg}' -> {result['user_name']} (conf: {result['confidence']:.2f})")
    
    # Ver estado final
    print("\n📊 Estado final do sistema:")
    list_result = user_commands.process_command("listar utilizadores")
    print(list_result['message'])

if __name__ == "__main__":
    print("🎯 TESTE COMPLETO DO SISTEMA MULTI-UTILIZADOR")
    print("=" * 70)
    
    try:
        test_basic_user_identification()
        test_user_switching()
        test_conversation_continuity()
        test_user_pattern_learning()
        test_contextual_identification()
        test_command_system()
        test_full_scenario()
        
        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES DO SISTEMA MULTI-UTILIZADOR CONCLUÍDOS!")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {e}")
        import traceback
        traceback.print_exc()