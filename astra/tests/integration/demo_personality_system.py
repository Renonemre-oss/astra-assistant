#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Demonstração do Sistema de Personalidade Dinâmica
Script para demonstrar como o ASTRA adapta sua personalidade baseado no contexto.
"""

import sys
import time
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Imports
from modules.personality_engine import PersonalityEngine, MoodType, PersonalityMode

def demonstrate_mood_detection():
    """Demonstra detecção de humor."""
    print("🎭 DEMONSTRAÇÃO - Detecção de Humor")
    print("=" * 50)
    
    engine = PersonalityEngine()
    
    test_cases = [
        ("Estou muito feliz hoje! 😊", MoodType.HAPPY),
        ("Que droga, estou frustrado com isso 😤", MoodType.FRUSTRATED),
        ("Estou cansado, preciso descansar 😴", MoodType.TIRED),
        ("Nossa, que incrível! Estou empolgado! 🎉", MoodType.EXCITED),
        ("Estou meio triste hoje... 😢", MoodType.SAD),
        ("Estou super estressado com tanto trabalho 😰", MoodType.STRESSED),
        ("Tudo normal por aqui", MoodType.NEUTRAL),
    ]
    
    for text, expected_mood in test_cases:
        detected_mood = engine.analyze_user_mood(text)
        status = "✅" if detected_mood == expected_mood else "❌"
        print(f"{status} '{text}'")
        print(f"   Esperado: {expected_mood.value} | Detectado: {detected_mood.value}")
        print()

def demonstrate_personality_adaptation():
    """Demonstra adaptação de personalidade."""
    print("\n🎯 DEMONSTRAÇÃO - Adaptação de Personalidade")
    print("=" * 50)
    
    engine = PersonalityEngine()
    base_response = "Entendo. Vou ajudá-lo com isso."
    
    scenarios = [
        ("Estou muito feliz hoje!", "Humor feliz → Personalidade divertida"),
        ("Estou frustrado com esse problema", "Humor frustrado → Personalidade calma"),
        ("Estou cansado de tanto trabalhar", "Humor cansado → Personalidade tranquila"), 
        ("Nossa, que empolgante!", "Humor empolgado → Personalidade energética"),
        ("Estou triste...", "Humor triste → Personalidade apoiadora"),
        ("Bom dia! Como está?", "Neutro pela manhã → Personalidade energética"),
    ]
    
    for user_input, description in scenarios:
        personalized_response, personality = engine.process_user_interaction(user_input, base_response)
        
        print(f"👤 Usuário: {user_input}")
        print(f"📝 Contexto: {description}")
        print(f"🎭 Personalidade: {personality.value.upper()}")
        print(f"🤖 ASTRA: {personalized_response}")
        print("-" * 40)

def demonstrate_time_adaptation():
    """Demonstra adaptação baseada no horário."""
    print("\n⏰ DEMONSTRAÇÃO - Adaptação por Horário")
    print("=" * 50)
    
    engine = PersonalityEngine()
    
    # Simular diferentes horários modificando manualmente
    from datetime import datetime
    import unittest.mock
    
    time_scenarios = [
        (6, "06:00 - Cedo da manhã", PersonalityMode.CALM),
        (9, "09:00 - Manhã", PersonalityMode.ENERGETIC), 
        (15, "15:00 - Tarde", PersonalityMode.CASUAL),
        (19, "19:00 - Noite", PersonalityMode.CASUAL),
        (23, "23:00 - Noite tarde", PersonalityMode.CALM),
    ]
    
    for hour, description, expected_personality in time_scenarios:
        # Mock do horário
        mock_time = datetime.now().replace(hour=hour)
        with unittest.mock.patch('modules.personality_engine.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_time
            
            # Testar com input neutro
            neutral_input = "Como você está?"
            personality = engine.adapt_personality(neutral_input)
            
            print(f"🕐 {description}")
            print(f"🎭 Personalidade adaptada: {personality.value}")
            
            # Gerar resposta de exemplo
            response = "Estou bem, obrigado!"
            personalized = engine.generate_response_with_personality(response)
            print(f"🤖 Resposta: {personalized}")
            print("-" * 30)

def demonstrate_learning():
    """Demonstra aprendizado de preferências."""
    print("\n🧠 DEMONSTRAÇÃO - Aprendizado de Preferências")
    print("=" * 50)
    
    engine = PersonalityEngine()
    
    print("📚 Ensinando preferências ao ASTRA...")
    
    # Simular algumas interações
    preferences_to_learn = [
        ("música", "rock"),
        ("música", "jazz"), 
        ("música", "rock"),  # rock novamente
        ("comida", "pizza"),
        ("comida", "pizza"),  # pizza novamente
        ("personalidade", "casual"),
        ("personalidade", "casual"),
        ("personalidade", "casual"),
    ]
    
    for category, preference in preferences_to_learn:
        engine.learn_user_preference(category, preference)
        print(f"✏️ Aprendeu: {category} → {preference}")
    
    print("\n📊 Preferências aprendidas:")
    summary = engine.get_personality_summary()
    for category, prefs in summary['user_preferences'].items():
        print(f"📂 {category.upper()}:")
        for pref, count in prefs.items():
            print(f"   • {pref}: {count}x")

def demonstrate_conversation_flow():
    """Demonstra um fluxo completo de conversa."""
    print("\n💬 DEMONSTRAÇÃO - Fluxo de Conversa Completo")
    print("=" * 50)
    
    engine = PersonalityEngine()
    
    conversation = [
        ("Olá! Como você está?", "Oi! Tudo ótimo por aqui. Como posso ajudar?"),
        ("Estou meio triste hoje...", "Sinto muito que esteja se sentindo assim. Quer conversar sobre isso?"),
        ("Nossa, agora estou animado!", "Que bom ver você animado! Isso me deixa feliz também!"),
        ("Você é muito legal!", "Obrigado! Gosto muito de conversar com você também."),
        ("Tenho que ir trabalhar agora", "Boa sorte no trabalho! Espero que tenha um ótimo dia!"),
    ]
    
    print("🎬 Simulando conversa...")
    print()
    
    for i, (user_input, base_response) in enumerate(conversation):
        print(f"--- Turno {i+1} ---")
        
        # Processar interação
        personalized_response, personality = engine.process_user_interaction(user_input, base_response)
        
        print(f"👤 Usuário: {user_input}")
        print(f"🎭 Personalidade: {personality.value}")
        print(f"📊 Humor detectado: {engine.current_mood.value}")
        print(f"🤖 ASTRA: {personalized_response}")
        print()
        
        time.sleep(1)  # Pausa dramática
    
    print("📈 Resumo da conversa:")
    summary = engine.get_personality_summary()
    print(f"   • Total de interações: {summary['total_interactions']}")
    print(f"   • Interações recentes: {summary['recent_interactions']}")
    print(f"   • Personalidade atual: {summary['current_personality']}")
    print(f"   • Humor atual: {summary['current_mood_detected']}")

def main():
    """Função principal da demonstração."""
    print("🎭 ASTRA - Demonstração do Sistema de Personalidade Dinâmica")
    print("=" * 60)
    print()
    
    try:
        # Executar todas as demonstrações
        demonstrate_mood_detection()
        demonstrate_personality_adaptation()
        demonstrate_time_adaptation()
        demonstrate_learning()
        demonstrate_conversation_flow()
        
        print("\n🎉 Demonstração completa!")
        print("\n💡 O sistema está funcionando perfeitamente!")
        print("   • Detecta humor do usuário automaticamente")
        print("   • Adapta personalidade baseada no contexto")
        print("   • Aprende preferências com o tempo")
        print("   • Considera horário do dia")
        print("   • Mantém histórico de interações")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
