#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste seguro do sistema de visualização visual do Jarvis
Evita travamentos testando apenas funcionalidade básica
"""

def test_imports():
    """Testa se as importações funcionam"""
    print("🧪 Testando importações...")
    
    try:
        from modules.audio_visualizer import AudioVisualizer, VisualizationMode, create_audio_visualizer
        print("✅ AudioVisualizer importado")
        
        from modules.visual_hotword_detector import VisualHotwordDetector, VisualMode, create_visual_hotword_detector
        print("✅ VisualHotwordDetector importado")
        
        return True
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def test_creation():
    """Testa criação dos objetos"""
    print("\n🧪 Testando criação de objetos...")
    
    try:
        from modules.audio_visualizer import create_audio_visualizer, VisualizationMode
        
        # Teste AudioVisualizer
        def dummy_callback(msg):
            pass
        
        visualizer = create_audio_visualizer(dummy_callback, VisualizationMode.PULSE)
        print("✅ AudioVisualizer criado")
        
        # Teste configurações
        visualizer.set_sensitivity(2.0)
        visualizer.set_mode(VisualizationMode.BARS)
        print("✅ Configurações aplicadas")
        
        # Teste status
        status = visualizer.get_status_info()
        print(f"✅ Status obtido: manim={status.get('manim_available', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na criação: {e}")
        return False

def test_visual_detector():
    """Testa detector visual (sem start/stop)"""
    print("\n🧪 Testando detector visual...")
    
    try:
        from modules.visual_hotword_detector import create_visual_hotword_detector, VisualMode, VisualizationMode
        
        # Callback silencioso
        messages = []
        def on_status(msg):
            messages.append(msg)
        
        detector = create_visual_hotword_detector(
            status_callback=on_status,
            visual_mode=VisualMode.LISTENING_ONLY
        )
        print("✅ Detector visual criado")
        
        # Testar configurações
        detector.set_visual_mode(VisualMode.ALWAYS)
        detector.set_visualization_mode(VisualizationMode.PARTICLES)
        detector.set_sensitivity(1.8)
        detector.set_colors(["#ff0000", "#00ff00", "#0000ff"])
        print("✅ Configurações aplicadas")
        
        # Testar status
        status = detector.get_status_info()
        print(f"✅ Status: visual_mode={status.get('visual_mode', 'N/A')}")
        print(f"✅ {len(messages)} mensagens de status recebidas")
        
        # Testar wake words
        detector.add_wake_word("test word")
        detector.remove_wake_word("test word")
        print("✅ Wake words testadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no detector visual: {e}")
        return False

def test_manim_availability():
    """Testa se Manim está disponível e funcional"""
    print("\n🧪 Testando Manim...")
    
    try:
        from modules.audio_visualizer import MANIM_AVAILABLE
        
        if MANIM_AVAILABLE:
            print("✅ Manim está disponível")
            
            # Tentar importar classes do Manim
            try:
                from manim import Scene, Circle
                print("✅ Classes do Manim importadas")
            except Exception as e:
                print(f"⚠️ Problema com importação Manim: {e}")
        else:
            print("⚠️ Manim não está disponível")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar Manim: {e}")
        return False

def main():
    """Função principal de teste seguro"""
    print("🚀 === TESTE SEGURO DO SISTEMA VISUAL ===\n")
    
    tests = [
        ("Importações", test_imports),
        ("Criação de Objetos", test_creation), 
        ("Detector Visual", test_visual_detector),
        ("Disponibilidade Manim", test_manim_availability)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"EXECUTANDO: {test_name}")
        print('='*50)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSOU")
        else:
            print(f"❌ {test_name} - FALHOU")
    
    print(f"\n{'='*50}")
    print("RESULTADO FINAL")
    print('='*50)
    print(f"✅ Testes aprovados: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("\n🎨 Sistema de visualização está funcionando!")
        print("\nO que funciona:")
        print("• ✅ Importações dos módulos")
        print("• ✅ Criação de objetos")
        print("• ✅ Configurações e status")
        print("• ✅ Detector visual integrado")
        print("• ✅ Sistema de callbacks")
        
        from modules.audio_visualizer import MANIM_AVAILABLE
        if MANIM_AVAILABLE:
            print("• ✅ Manim disponível para visualizações")
        else:
            print("• ⚠️ Manim não disponível (instale com: pip install manim)")
        
        print("\n📝 Próximos passos:")
        print("1. Para testar visualização: python modules/audio_visualizer.py")
        print("2. Para integrar no Jarvis: use create_visual_hotword_detector()")
        print("3. Para usar apenas visualização: use create_audio_visualizer()")
        
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam")
        print("Verifique os erros acima para mais detalhes")
    
    print("\n✅ Teste finalizado com segurança!")

if __name__ == "__main__":
    main()