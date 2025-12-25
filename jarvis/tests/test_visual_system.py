#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste simples do sistema de visualização visual do Astra
"""

import time
import signal
import sys

def signal_handler(sig, frame):
    """Handler para Ctrl+C"""
    print('\n\n🛑 Interrompido pelo usuário')
    if 'detector' in globals():
        try:
            detector.shutdown()
        except:
            pass
    print('✅ Teste finalizado')
    sys.exit(0)

# Configurar handler para Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

def test_basic_functionality():
    """Teste básico de funcionalidade"""
    print("🧪 === TESTE BÁSICO DO SISTEMA VISUAL ===")
    
    try:
        # Importar módulos
        from modules.visual_hotword_detector import create_visual_hotword_detector, VisualMode, VisualizationMode
        print("✅ Importações OK")
        
        # Criar detector
        def on_status(message):
            print(f"📢 {message}")
        
        global detector
        detector = create_visual_hotword_detector(
            status_callback=on_status,
            visual_mode=VisualMode.LISTENING_ONLY,
            visualization_mode=VisualizationMode.PULSE
        )
        print("✅ Detector criado")
        
        # Testar status
        status = detector.get_status_info()
        print(f"✅ Status obtido: visual_mode={status.get('visual_mode', 'N/A')}")
        
        # Testar configurações
        detector.set_sensitivity(2.0)
        detector.set_visualization_mode(VisualizationMode.BARS)
        print("✅ Configurações aplicadas")
        
        print("\n🎯 Teste básico concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste básico: {e}")
        return False

def test_start_stop():
    """Teste de start/stop rápido"""
    print("\n🧪 === TESTE START/STOP RÁPIDO ===")
    
    try:
        from modules.visual_hotword_detector import create_visual_hotword_detector
        
        detector = create_visual_hotword_detector()
        print("✅ Detector criado")
        
        # Start rápido
        success = detector.start_listening()
        if success:
            print("✅ Start listening OK")
            time.sleep(0.5)  # Apenas meio segundo
            
            detector.stop_listening()
            print("✅ Stop listening OK")
        else:
            print("⚠️ Não foi possível iniciar escuta")
        
        detector.shutdown()
        print("✅ Shutdown OK")
        
        print("🎯 Teste start/stop concluído!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste start/stop: {e}")
        return False

def test_audio_visualizer_only():
    """Teste apenas do AudioVisualizer"""
    print("\n🧪 === TESTE AUDIO VISUALIZER ISOLADO ===")
    
    try:
        from modules.audio_visualizer import create_audio_visualizer, VisualizationMode
        
        def on_status(message):
            print(f"🎨 {message}")
        
        visualizer = create_audio_visualizer(on_status, VisualizationMode.PULSE)
        print("✅ Visualizer criado")
        
        # Testar modos
        for mode in [VisualizationMode.PULSE, VisualizationMode.BARS, VisualizationMode.PARTICLES]:
            visualizer.set_mode(mode)
            print(f"✅ Modo {mode.value} OK")
        
        # Testar configurações
        visualizer.set_sensitivity(1.5)
        visualizer.set_colors(["#ff0000", "#00ff00", "#0000ff"])
        print("✅ Configurações aplicadas")
        
        # Testar status
        status = visualizer.get_status_info()
        print(f"✅ Status: is_active={status.get('is_active', False)}, manim_available={status.get('manim_available', False)}")
        
        print("🎯 Teste AudioVisualizer concluído!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste AudioVisualizer: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 === INICIANDO TESTES DO SISTEMA VISUAL ===\n")
    
    tests_passed = 0
    total_tests = 3
    
    # Teste 1: Funcionalidade básica
    if test_basic_functionality():
        tests_passed += 1
    
    # Teste 2: AudioVisualizer isolado
    if test_audio_visualizer_only():
        tests_passed += 1
    
    # Teste 3: Start/Stop (mais sensível)
    if test_start_stop():
        tests_passed += 1
    
    # Resultado final
    print(f"\n📊 === RESULTADO DOS TESTES ===")
    print(f"✅ Testes aprovados: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\n🎨 Sistema de visualização está funcionando corretamente!")
        print("\nPróximos passos:")
        print("1. Execute: python modules/audio_visualizer.py")
        print("2. Execute: python modules/visual_hotword_detector.py")
        print("3. Integre no seu launcher principal do Astra")
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
    
    print("\n🏁 Fim dos testes")

if __name__ == "__main__":
    main()
