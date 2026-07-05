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


def main():
    """Função principal."""
    print("\n" + "🎯" * 30)
    print("🤖 Astra AI ASSISTANT - HELLO WORLD")
    print("🎯" * 30)
    
    print("\n📖 Este script demonstra o componente básico do Astra:")
    print("   1. AI Engine - Motor de IA unificado")

    input("\n▶️  Pressione ENTER para começar...")

    # Executar exemplo
    exemplo_ai_engine()

    # Final
    print("\n\n" + "✨" * 30)
    print("🎉 Exemplo concluído!")
    print("✨" * 30)

    print("\n📚 Próximos passos:")
    print("   1. Leia docs/guides/01_getting_started.md")
    print("   2. Configure config/ai_config.yaml")
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



