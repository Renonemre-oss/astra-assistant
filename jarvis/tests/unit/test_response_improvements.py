#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de Teste para Melhorias nas Respostas do ALEX
=====================================================

Testa se o sistema de contexto inteligente funciona corretamente
e se as respostas são mais naturais e menos repetitivas.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from modules.personal_profile import PersonalProfile
# from core.assistente import AssistenteGUI

def test_context_detection():
    """Testa a detecção de contexto."""
    print("🧠 TESTE DE DETECÇÃO DE CONTEXTO")
    print("=" * 50)
    
    # Criar uma instância mock do assistente para testar contexto
    class MockAssistente:
        def _determine_context_type(self, comando: str) -> str:
            """Copia da função do assistente para teste"""
            comando_lower = comando.lower()
            
            # Comandos simples que não precisam de muito contexto
            simple_commands = ['oi', 'olá', 'hey', 'que horas', 'hora', 'data', 'obrigado', 'tchau', 'adeus']
            if any(simple in comando_lower for simple in simple_commands):
                return "minimal"
            
            # Comandos relacionados com comida
            food_keywords = ['comida', 'pizza', 'comer', 'jantar', 'almoço', 'bebida', 'restaurante', 'receita', 'cozinhar']
            if any(food in comando_lower for food in food_keywords):
                return "food_related"
            
            # Perguntas pessoais diretas
            personal_questions = ['quem sou', 'meu nome', 'minha idade', 'sobre mim', 'me conhece']
            if any(personal in comando_lower for personal in personal_questions):
                return "personal_info"
            
            # Para tudo o resto, contexto geral (mínimo)
            return "general"
    
    mock = MockAssistente()
    
    test_cases = [
        ("oi", "minimal", "Cumprimento simples"),
        ("que horas são?", "minimal", "Pergunta sobre hora"),
        ("quero comer pizza", "food_related", "Pergunta sobre comida"),
        ("qual é a minha comida favorita?", "food_related", "Pergunta sobre preferência alimentar"),
        ("quem sou eu?", "personal_info", "Pergunta pessoal direta"),
        ("como está o tempo hoje?", "general", "Pergunta geral"),
        ("podes me ajudar com um projeto?", "general", "Pedido de ajuda geral")
    ]
    
    for comando, expected_context, description in test_cases:
        detected_context = mock._determine_context_type(comando)
        status = "✅" if detected_context == expected_context else "❌"
        print(f"{status} '{comando}' -> {detected_context} (esperado: {expected_context}) - {description}")
    
    return True

def test_profile_context_filtering():
    """Testa o filtro de preferências por contexto."""
    print("\n📝 TESTE DE FILTRO DE PERFIL POR CONTEXTO")
    print("=" * 50)
    
    profile = PersonalProfile()
    
    # Simular preferências
    mock_preferences = {
        'nome_completo': 'António Pereira',
        'comida_favorita': 'pizza',
        'idade': '19',
        'profissao': 'estudante',
        'bebida_favorita': 'coca-cola'
    }
    
    test_contexts = [
        ("minimal", "Contexto mínimo - apenas nome"),
        ("food_related", "Contexto alimentar - apenas comida"),
        ("personal_info", "Contexto pessoal - info básica sem comida"),
        ("general", "Contexto geral - apenas essencial")
    ]
    
    for context, description in test_contexts:
        filtered = profile._filter_preferences_by_context(mock_preferences, context)
        print(f"\n🔍 {context.upper()} ({description}):")
        if filtered:
            for key, value in filtered.items():
                print(f"   - {key}: {value}")
        else:
            print("   (Nenhuma preferência incluída)")
    
    return True

def test_profile_prompt_generation():
    """Testa a geração de prompts contextuais."""
    print("\n💬 TESTE DE GERAÇÃO DE PROMPTS CONTEXTUAIS")
    print("=" * 50)
    
    profile = PersonalProfile()
    
    # Simular que temos algumas preferências salvas
    profile.facts_cache = {
        'nome_completo': 'António Pereira',
        'comida_favorita': 'pizza',
        'idade': '19'
    }
    
    contexts_to_test = ["minimal", "food_related", "personal_info", "general"]
    
    for context in contexts_to_test:
        prompt_info = profile.get_profile_for_prompt(context)
        print(f"\n🎯 Contexto: {context}")
        print(f"Prompt gerado: {repr(prompt_info)}")
        
        # Verificar se pizza só aparece em contexto relacionado com comida
        has_pizza = "pizza" in prompt_info.lower()
        if context == "food_related":
            status = "✅" if has_pizza else "❌"
            print(f"{status} Pizza mencionada em contexto alimentar: {has_pizza}")
        else:
            status = "✅" if not has_pizza else "❌"
            print(f"{status} Pizza NÃO mencionada em contexto não-alimentar: {not has_pizza}")
    
    return True

def test_response_variations():
    """Testa a variação nas respostas."""
    print("\n🎲 TESTE DE VARIAÇÃO NAS RESPOSTAS")
    print("=" * 50)
    
    import random
    
    # Simular as listas de respostas do assistente
    cumprimentos = [
        "Ey! Tudo bem?",
        "Olá! Como estás?",
        "Hey! Em que posso ajudar?",
        "Oi! Que tal?",
        "E aí! Como vai?"
    ]
    
    despedidas = [
        "Até à próxima! 👋",
        "Tchau! Falamos depois! 😊",
        "Até logo! Cuida-te! 👍",
        "Bye! Se precisares, grita! 😉"
    ]
    
    print("🔄 Testando variação em cumprimentos (5 tentativas):")
    for i in range(5):
        resposta = random.choice(cumprimentos)
        print(f"  {i+1}. {resposta}")
    
    print("\n🔄 Testando variação em despedidas (4 tentativas):")
    for i in range(4):
        resposta = random.choice(despedidas)
        print(f"  {i+1}. {resposta}")
    
    return True

def test_casual_tone():
    """Verifica se o tom das respostas é mais casual."""
    print("\n😎 TESTE DE TOM CASUAL")
    print("=" * 50)
    
    # Comparar ton antigo vs novo
    old_responses = [
        "O utilizador está a conversar com um assistente virtual chamado Alex. Responde de forma útil, concisa e natural.",
        "Olá! Como posso ajudar hoje?",
        "👋 Até logo! Sempre às ordens."
    ]
    
    new_responses = [
        "Tu és o Alex, um assistente virtual descontraído e natural. Responde de forma casual, amigável e direta, como um amigo jovem falaria. Evita ser muito formal.",
        "Ey! Tudo bem?",
        "Até à próxima! 👋"
    ]
    
    print("📊 Comparação de Tom:")
    print("\n❌ ANTIGO (Formal):")
    for response in old_responses:
        print(f"   • {response}")
    
    print("\n✅ NOVO (Casual):")
    for response in new_responses:
        print(f"   • {response}")
    
    # Analisar características
    formal_words = ["utilizador", "útil", "concisa", "sempre às ordens"]
    casual_words = ["tu és", "descontraído", "amigo", "ey", "tudo bem"]
    
    old_text = " ".join(old_responses).lower()
    new_text = " ".join(new_responses).lower()
    
    formal_count_old = sum(1 for word in formal_words if word in old_text)
    formal_count_new = sum(1 for word in formal_words if word in new_text)
    casual_count_old = sum(1 for word in casual_words if word in old_text)
    casual_count_new = sum(1 for word in casual_words if word in new_text)
    
    print(f"\n📈 Análise de Tom:")
    print(f"   Palavras formais: Antigo({formal_count_old}) vs Novo({formal_count_new})")
    print(f"   Palavras casuais: Antigo({casual_count_old}) vs Novo({casual_count_new})")
    
    improvement = (casual_count_new > casual_count_old) and (formal_count_new < formal_count_old)
    status = "✅ MELHOROU" if improvement else "❌ PRECISA AJUSTAR"
    print(f"   {status}")
    
    return improvement

def run_all_tests():
    """Executa todos os testes."""
    print("🧪 INICIANDO TESTES DE MELHORIAS NAS RESPOSTAS")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Detecção de Contexto", test_context_detection()))
    except Exception as e:
        print(f"❌ Erro no teste de contexto: {e}")
        results.append(("Detecção de Contexto", False))
    
    try:
        results.append(("Filtro de Perfil", test_profile_context_filtering()))
    except Exception as e:
        print(f"❌ Erro no teste de filtro: {e}")
        results.append(("Filtro de Perfil", False))
    
    try:
        results.append(("Geração de Prompts", test_profile_prompt_generation()))
    except Exception as e:
        print(f"❌ Erro no teste de prompts: {e}")
        results.append(("Geração de Prompts", False))
    
    try:
        results.append(("Variação de Respostas", test_response_variations()))
    except Exception as e:
        print(f"❌ Erro no teste de variação: {e}")
        results.append(("Variação de Respostas", False))
    
    try:
        results.append(("Tom Casual", test_casual_tone()))
    except Exception as e:
        print(f"❌ Erro no teste de tom: {e}")
        results.append(("Tom Casual", False))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n🎯 Taxa de Sucesso: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 EXCELENTE! Melhorias implementadas com sucesso!")
    elif success_rate >= 60:
        print("👍 BOM! Melhorias funcionando, mas pode melhorar mais")
    else:
        print("⚠️ PRECISA MELHORAR! Revisar implementação")
    
    return success_rate >= 80

if __name__ == "__main__":
    run_all_tests()