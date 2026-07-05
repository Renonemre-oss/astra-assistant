#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Astra AI Assistant - Hello World Example
Exemplo mais simples possível de uso do Astra.
"""

import sys
from pathlib import Path

# Adicionar Astra ao path
Astra_path = Path(__file__).parent.parent.parent / "Astra"
sys.path.insert(0, str(Astra_path))

# Importações
from ai import AIEngine
from skills.builtin import WeatherSkill
import yaml


def exemplo_ai_engine():
    """Exemplo básico do AI Engine."""
    print("=" * 60)
    print("🤖 Exemplo 1: AI Engine Básico")
    print("=" * 60)
    
    # Configuração mínima (pode usar Ollama ou mockar)
    config = {
        'default_provider': 'ollama',
        'providers': {
            'ollama': {
                'enabled': True,
                'model': 'dolphin-llama3:8b',
                'url': 'http://localhost:11434',
                'timeout': 30,
                'max_retries': 2
            }
        },
        'fallback_chain': ['ollama'],
        'cache_enabled': False  # Desabilitado para demo
    }
    
    try:
        # Inicializar AI Engine
        print("\n📊 Inicializando AI Engine...")
        engine = AIEngine(config)
        
        # Verificar provedores disponíveis
        available = engine.get_available_providers()
        print(f"✅ Provedores disponíveis: {available}")
        
        # Fazer uma pergunta simples
        print("\n💬 Fazendo pergunta: 'Olá! Como você está?'")
        response = engine.generate(
            prompt="Olá! Como você está?",
            temperature=0.7
        )
        
        if response.success:
            print(f"\n🤖 Resposta:")
            print(f"   {response.content}")
            print(f"\n📈 Metadados:")
            print(f"   Provedor: {response.provider}")
            print(f"   Modelo: {response.model}")
            if response.tokens_used:
                print(f"   Tokens usados: {response.tokens_used}")
        else:
            print(f"\n❌ Erro: {response.error}")
            print("\n💡 Dica: Certifique-se que o Ollama está rodando:")
            print("   1. Instale: https://ollama.ai")
            print("   2. Execute: ollama serve")
            print("   3. Baixe modelo: ollama pull dolphin-llama3:8b")
        
        # Estatísticas
        print(f"\n📊 Estatísticas do Engine:")
        stats = engine.get_stats()
        print(f"   Total de requisições: {stats['total_requests']}")
        print(f"   Cache hits: {stats['cache_hits']}")
        print(f"   Cache misses: {stats['cache_misses']}")
        
    except Exception as e:
        print(f"\n❌ Erro ao executar: {e}")
        print("\n💡 Este exemplo requer Ollama instalado e rodando.")


def exemplo_weather_skill():
    """Exemplo básico de uma Skill."""
    print("\n\n" + "=" * 60)
    print("🌤️  Exemplo 2: Weather Skill")
    print("=" * 60)
    
    try:
        # Criar skill (sem API key = modo demo)
        print("\n📊 Criando Weather Skill...")
        skill = WeatherSkill({
            'default_city': 'Lisboa'
        })
        
        # Ativar skill
        print("⚡ Ativando skill...")
        if skill.activate():
            print(f"✅ Skill ativada: {skill.metadata.name} v{skill.metadata.version}")
        else:
            print(f"❌ Erro ao ativar skill: {skill.last_error}")
            return
        
        # Testar queries
        queries = [
            "Qual o clima hoje?",
            "Como está o tempo em Lisboa?",
            "Vai chover amanhã?",
            "Olá! Como você está?"  # Não deve ser processada
        ]
        
        for query in queries:
            print(f"\n💬 Query: '{query}'")
            
            # Verificar se skill pode processar
            can_handle = skill.can_handle(query, {})
            print(f"   Pode processar: {'✅ Sim' if can_handle else '❌ Não'}")
            
            if can_handle:
                # Executar skill
                response = skill.execute(query, {})
                
                if response.success:
                    print(f"\n   🌡️  Resposta:")
                    for line in response.content.split('\n'):
                        print(f"   {line}")
                    print(f"\n   📊 Fonte: {response.metadata.get('source', 'N/A')}")
                else:
                    print(f"   ❌ Erro: {response.error}")
        
        # Desativar skill
        print("\n🔌 Desativando skill...")
        skill.deactivate()
        
    except Exception as e:
        print(f"\n❌ Erro ao executar: {e}")
        import traceback
        traceback.print_exc()


def exemplo_integracao():
    """Exemplo de integração AI Engine + Skills."""
    print("\n\n" + "=" * 60)
    print("🔗 Exemplo 3: AI Engine + Skills")
    print("=" * 60)
    
    print("\n💡 Este exemplo mostra como integrar o AI Engine com Skills:")
    print("   1. Skill detecta query específica (ex: clima)")
    print("   2. Skill processa e retorna dados estruturados")
    print("   3. AI Engine formata resposta final em linguagem natural")
    print("\n🚧 Implementação completa virá na Fase 2!")


def main():
    """Função principal."""
    print("\n" + "🎯" * 30)
    print("🤖 Astra AI ASSISTANT - HELLO WORLD")
    print("🎯" * 30)
    
    print("\n📖 Este script demonstra os componentes básicos do Astra:")
    print("   1. AI Engine - Motor de IA unificado")
    print("   2. Skills System - Sistema modular de capacidades")
    print("   3. Integração - Como tudo funciona junto")
    
    input("\n▶️  Pressione ENTER para começar...")
    
    # Executar exemplos
    exemplo_ai_engine()
    
    input("\n▶️  Pressione ENTER para continuar...")
    exemplo_weather_skill()
    
    input("\n▶️  Pressione ENTER para ver último exemplo...")
    exemplo_integracao()
    
    # Final
    print("\n\n" + "✨" * 30)
    print("🎉 Exemplos concluídos!")
    print("✨" * 30)
    
    print("\n📚 Próximos passos:")
    print("   1. Leia docs/guides/01_getting_started.md")
    print("   2. Configure config/ai_config.yaml")
    print("   3. Experimente criar sua própria skill!")
    print("\n🆘 Precisa de ajuda? https://github.com/Renonemre-oss/astra-assistant/issues")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Até logo!")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()



