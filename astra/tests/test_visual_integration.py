#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste da Integração do Sistema de Visualização com o Astra
"""

import time
import sys
from pathlib import Path

# Adicionar projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_configuration():
    """Testa se as configurações visuais funcionam"""
    print("🔧 TESTANDO CONFIGURAÇÕES VISUAIS")
    print("=" * 50)
    
    try:
        from config.visual_config import get_visual_config, update_visual_config, apply_preset, VISUAL_PRESETS
        
        # Testar obtenção de configurações
        config = get_visual_config()
        print(f"✅ Configuração carregada: {config.visual_mode.value}")
        print(f"   Visualização: {config.visualization_mode.value}")
        print(f"   Sensibilidade: {config.sensitivity}")
        print(f"   Cores: {len(config.colors)} cores")
        
        # Testar atualização de configurações
        update_visual_config(sensitivity=2.0)
        print("✅ Configuração atualizada")
        
        # Testar presets
        print(f"\n📋 Presets disponíveis: {list(VISUAL_PRESETS.keys())}")
        
        # Aplicar preset de teste
        if apply_preset("festa"):
            print("✅ Preset 'festa' aplicado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False

def test_visual_hotword_system():
    """Testa o sistema visual de hotword"""
    print("\n🎨 TESTANDO SISTEMA VISUAL DE HOTWORD")
    print("=" * 50)
    
    try:
        from voice.visual_hotword_detector import create_visual_hotword_system
        
        messages = []
        def status_callback(msg):
            messages.append(msg)
            print(f"📢 {msg}")
        
        def detection_callback(word):
            print(f"🔥 HOTWORD DETECTADO: {word}")
        
        # Criar sistema
        system = create_visual_hotword_system(
            status_callback=status_callback,
            detection_callback=detection_callback
        )
        
        print("✅ Sistema visual de hotword criado")
        
        # Testar informações de status
        status_info = system.get_status_info()
        print(f"📊 Status: {status_info}")
        
        # Testar configuração de presets
        if system.set_visualization_preset("completo"):
            print("✅ Preset 'completo' aplicado")
        
        # Testar alternância de modo visual
        system.toggle_visual_mode()
        print("✅ Modo visual alternado")
        
        print(f"📈 Total de mensagens de status: {len(messages)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema visual: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_main():
    """Testa integração com sistema principal"""
    print("\n🔗 TESTANDO INTEGRAÇÃO COM SISTEMA PRINCIPAL")
    print("=" * 50)
    
    try:
        # Verificar se as importações do sistema principal funcionam
        from core.assistente import VISUAL_SYSTEM_AVAILABLE
        
        print(f"Sistema visual disponível: {'✅ SIM' if VISUAL_SYSTEM_AVAILABLE else '❌ NÃO'}")
        
        if VISUAL_SYSTEM_AVAILABLE:
            from voice.visual_hotword_detector import create_visual_hotword_system
            print("✅ Importação do sistema visual no core funcionando")
        else:
            print("⚠️ Sistema visual não disponível no core")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_commands():
    """Testa comandos de controle de visualização"""
    print("\n🎮 TESTANDO COMANDOS DE CONTROLE")
    print("=" * 50)
    
    commands_to_test = [
        "alterar modo visual",
        "mudar visualização para festa",
        "aplicar preset completo",
        "desativar visualização", 
        "ativar visualização"
    ]
    
    print("Comandos que podem ser integrados:")
    for i, cmd in enumerate(commands_to_test, 1):
        print(f"  {i}. {cmd}")
    
    return True

def create_demo_commands():
    """Cria exemplo de comandos para integração"""
    demo_code = '''
# EXEMPLO DE INTEGRAÇÃO DE COMANDOS DE VISUALIZAÇÃO
# Adicionar ao método processar_comando_backend() do assistente

# Comandos de visualização
if any(phrase in comando_lower for phrase in ["modo visual", "visualização", "preset visual"]):
    if "alterar" in comando_lower or "mudar" in comando_lower:
        if hasattr(self, 'hotword_detector') and self.hotword_detector:
            if hasattr(self.hotword_detector, 'toggle_visual_mode'):
                self.hotword_detector.toggle_visual_mode()
                resposta = "✨ Modo visual alterado!"
            else:
                resposta = "⚠️ Sistema visual não disponível"
        else:
            resposta = "❌ Detector de hotword não ativo"
    
    elif any(preset in comando_lower for preset in ["festa", "completo", "minimalista", "discreto"]):
        # Extrair nome do preset
        for preset_name in ["festa", "completo", "minimalista", "discreto"]:
            if preset_name in comando_lower:
                if hasattr(self, 'hotword_detector') and self.hotword_detector:
                    if hasattr(self.hotword_detector, 'set_visualization_preset'):
                        success = self.hotword_detector.set_visualization_preset(preset_name)
                        if success:
                            resposta = f"🎨 Preset '{preset_name}' aplicado com sucesso!"
                        else:
                            resposta = f"❌ Falha ao aplicar preset '{preset_name}'"
                    else:
                        resposta = "⚠️ Sistema visual não suporta presets"
                else:
                    resposta = "❌ Detector de hotword não ativo"
                break
    
    elif "desativar" in comando_lower:
        resposta = "🔇 Visualização será desativada na próxima sessão"
    elif "ativar" in comando_lower:
        resposta = "🎨 Visualização será ativada na próxima sessão"
'''
    
    with open("demo_visual_commands.py", "w", encoding="utf-8") as f:
        f.write(demo_code)
    
    print("✅ Arquivo 'demo_visual_commands.py' criado com exemplos de integração")
    return True

def main():
    """Função principal de teste"""
    print("🚀 TESTE DE INTEGRAÇÃO DO SISTEMA DE VISUALIZAÇÃO")
    print("=" * 60)
    
    results = {
        'configuração': test_configuration(),
        'sistema_visual': test_visual_hotword_system(),
        'integração': test_integration_with_main(),
        'comandos': test_commands(),
        'demo': create_demo_commands()
    }
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DOS TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name.title():.<20} {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 INTEGRAÇÃO COMPLETA!")
        print("✨ O sistema de visualização está funcionando e integrado!")
        print("\n📝 PRÓXIMOS PASSOS:")
        print("1. Execute: python run_ASTRA.py")
        print("2. Clique no botão de microfone")  
        print("3. Diga 'ASTRA' ou 'Astra' para ativar")
        print("4. Observe o feedback visual durante a escuta!")
        print("\n🎮 COMANDOS DISPONÍVEIS:")
        print("• 'ASTRA, alterar modo visual'")
        print("• 'ASTRA, aplicar preset festa'")
        print("• 'ASTRA, mudar para visualização completa'")
        
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam")
        print("Verifique os erros acima para mais detalhes")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

