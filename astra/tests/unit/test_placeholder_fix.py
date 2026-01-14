#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de Teste para Verificar Correção de Placeholders
========================================================

Este script testa se a função substituir_placeholders está 
funcionando corretamente para resolver o problema do 
ASTRA responder com "[hora atual]" em vez da hora real.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
from utils.text_processor import substituir_placeholders, formatar_resposta

def test_placeholder_substitution():
    """Testa a substituição de placeholders."""
    print("🔧 TESTE DE CORREÇÃO DE PLACEHOLDERS")
    print("=" * 50)
    
    # Casos de teste baseados no problema real
    test_cases = [
        "Olá António! 😉 Claro, sem problemas. São [hora atual]. Espero que tenhas um bom dia! 😊",
        "A hora atual é [hora atual].",
        "Hoje é [data atual] e são [hora atual].",
        "Data completa: [data completa]",
        "Sem placeholders neste texto.",
        "[hora atual] - [data atual] - [data e hora atual]"
    ]
    
    print(f"⏰ Hora de teste: {datetime.now().strftime('%H:%M:%S')}")
    print(f"📅 Data de teste: {datetime.now().strftime('%d/%m/%Y')}")
    print()
    
    for i, text in enumerate(test_cases, 1):
        print(f"📝 Teste {i}:")
        print(f"  Original:    '{text}'")
        
        # Testar substituição direta
        result_direct = substituir_placeholders(text)
        print(f"  Substituído: '{result_direct}'")
        
        # Testar através de formatar_resposta (como no sistema real)
        result_format = formatar_resposta(text)
        print(f"  Formatado:   '{result_format}'")
        
        # Verificar se placeholders foram removidos
        has_placeholders = "[" in result_format and "]" in result_format
        status = "❌ FALHOU" if has_placeholders else "✅ OK"
        print(f"  Status:      {status}")
        print()

def test_ollama_response_simulation():
    """Simula resposta do Ollama com placeholders."""
    print("🤖 SIMULAÇÃO DE RESPOSTA DO OLLAMA")
    print("=" * 50)
    
    # Simular resposta típica do Ollama como vista no histórico
    ollama_responses = [
        "Olá António! 😉 Claro, sem problemas. São [hora atual]. Espero que tenhas um bom dia! 😊",
        "Olá António! 😉 Claro, sem problemas. São [hora atual]. Espero que tennom um bom dia! 😊 \n\nAproveitando, já comeu pizza hoje? 😉",
        "A hora agora é [hora atual]. Tens mais alguma pergunta?"
    ]
    
    for i, response in enumerate(ollama_responses, 1):
        print(f"🔄 Simulação {i}:")
        print(f"  Ollama diz:  '{response[:60]}...'")
        
        # Processar como o sistema real faz
        processed = formatar_resposta(response)
        print(f"  ASTRA mostra: '{processed[:60]}...'")
        
        # Verificar se ainda tem placeholder
        has_placeholder = "[hora atual]" in processed
        status = "❌ PLACEHOLDER AINDA EXISTE" if has_placeholder else "✅ PLACEHOLDER SUBSTITUÍDO"
        print(f"  Resultado:   {status}")
        print()

def test_edge_cases():
    """Testa casos especiais."""
    print("🧪 TESTE DE CASOS ESPECIAIS")
    print("=" * 50)
    
    edge_cases = [
        "",  # Texto vazio
        "   ",  # Apenas espaços
        "[hora atual",  # Placeholder incompleto
        "hora atual]",  # Placeholder incompleto
        "[[hora atual]]",  # Placeholder duplo
        "[HORA ATUAL]",  # Maiúsculas
        "[hora  atual]",  # Espaços extras
        "São [hora atual] e 30 segundos",  # Com texto adicional
    ]
    
    for i, text in enumerate(edge_cases, 1):
        print(f"🔍 Caso {i}: '{text}'")
        try:
            result = substituir_placeholders(text)
            print(f"   Resultado: '{result}'")
            print(f"   Status:    ✅ OK")
        except Exception as e:
            print(f"   Erro:      ❌ {e}")
        print()

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE PLACEHOLDER...")
    print()
    
    # Executar testes
    test_placeholder_substitution()
    test_ollama_response_simulation() 
    test_edge_cases()
    
    print("🏁 TESTES CONCLUÍDOS!")
    print()
    print("💡 COMO TESTAR NO ASTRA REAL:")
    print("1. Execute o ASTRA normalmente")
    print("2. Pergunte: 'que horas são?'")
    print("3. Se responder com hora real em vez de '[hora atual]', funcionou!")
    print()
    print("🔧 SE AINDA NÃO FUNCIONAR:")
    print("- Verifique se text_processor.py foi atualizado")
    print("- Reinicie o ASTRA completamente")
    print("- Verifique os logs para confirmar que substituição aconteceu")
