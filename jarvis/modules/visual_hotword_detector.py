#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Astra - Visual Hotword Detector
Sistema integrado que combina detecção de hotword com visualização de áudio em tempo real.
Durante o modo de escuta, mostra animações visuais que reagem às vibrações sonoras.

Funcionalidades:
- Detecção de hotword com feedback visual
- Animações que reagem ao áudio em tempo real
- Múltiplos modos de visualização
- Integração transparente com sistema existente
"""

import logging
import threading
import time
from typing import Optional, Callable
from enum import Enum

# Importar módulos do projeto
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from modules.speech.hotword_detector import HotwordDetector, HotwordStatus
    from modules.audio_visualizer import AudioVisualizer, VisualizationMode, create_audio_visualizer
    MODULES_AVAILABLE = True
except ImportError as e:
    logging.error(f"Erro ao importar módulos: {e}")
    MODULES_AVAILABLE = False
    # Define dummy classes se imports falharem
    class VisualizationMode:
        PULSE = "pulse"
        WAVES = "waves"
        PARTICLES = "particles"

# Configure logger
logger = logging.getLogger(__name__)

class VisualMode(Enum):
    """Modos de operação visual."""
    OFF = "off"                    # Sem visualização
    LISTENING_ONLY = "listening"   # Apenas durante escuta
    ALWAYS = "always"              # Sempre ativo
    REACTIVE = "reactive"          # Reativo ao áudio

class VisualHotwordDetector:
    """
    Detector de hotword com visualização integrada.
    Combina detecção de wake words com animações visuais.
    """
    
    def __init__(self, status_callback: Optional[Callable[[str], None]] = None):
        """
        Inicializa o detector visual.
        
        Args:
            status_callback: Função para receber atualizações de status
        """
        self.status_callback = status_callback
        
        # Inicializar configurações primeiro
        self.visual_mode = VisualMode.LISTENING_ONLY
        self.visualization_mode = VisualizationMode.PULSE
        self.is_active = False
        self.detection_callback = None
        
        # Verificar se módulos estão disponíveis
        if not MODULES_AVAILABLE:
            self.set_status("❌ Módulos não disponíveis")
            self.hotword_detector = None
            self.audio_visualizer = None
            return
        
        # Inicializar componentes após configurações
        self.hotword_detector = HotwordDetector(self._on_hotword_status)
        self.audio_visualizer = create_audio_visualizer(self._on_visualizer_status)
        
        self.set_status("🎨 Visual Hotword Detector inicializado")
    
    def set_status(self, message: str):
        """Envia atualização de status."""
        if self.status_callback:
            self.status_callback(f"[VISUAL-HOTWORD] {message}")
        logger.info(f"VisualHotwordDetector: {message}")
    
    def _on_hotword_status(self, message: str):
        """Callback para status do hotword detector."""
        # Verificar se componentes estão inicializados antes de usar
        if hasattr(self, 'audio_visualizer') and self.audio_visualizer:
            # Detectar mudanças de estado para controlar visualização
            if "[HOTWORD-LISTENING]" in message and self.visual_mode in [VisualMode.LISTENING_ONLY, VisualMode.ALWAYS]:
                self._start_visualization()
            elif "[HOTWORD-DETECTED]" in message:
                self._on_detection_visual_feedback()
            elif "[HOTWORD-IDLE]" in message and self.visual_mode == VisualMode.LISTENING_ONLY:
                self._stop_visualization()
        
        # Repassar status
        if self.status_callback:
            self.status_callback(message)
    
    def _on_visualizer_status(self, message: str):
        """Callback para status do visualizador."""
        logger.debug(f"Visualizer: {message}")
    
    def _start_visualization(self):
        """Inicia visualização de áudio."""
        if self.audio_visualizer and not self.audio_visualizer.is_active:
            self.audio_visualizer.start(self.visualization_mode)
            self.set_status("🎨 Visualização ativada")
    
    def _stop_visualization(self):
        """Para visualização de áudio.""" 
        if self.audio_visualizer and self.audio_visualizer.is_active:
            self.audio_visualizer.stop()
            self.set_status("🛑 Visualização parada")
    
    def _on_detection_visual_feedback(self):
        """Feedback visual especial quando hotword é detectado."""
        if self.audio_visualizer and self.audio_visualizer.is_active:
            # Aumentar sensibilidade temporariamente para efeito dramático
            original_sensitivity = self.audio_visualizer.sensitivity
            self.audio_visualizer.set_sensitivity(3.0)
            
            # Restaurar após 2 segundos
            def restore_sensitivity():
                time.sleep(2)
                if self.audio_visualizer:
                    self.audio_visualizer.set_sensitivity(original_sensitivity)
            
            threading.Thread(target=restore_sensitivity, daemon=True).start()
    
    def start_listening(self) -> bool:
        """
        Inicia escuta de hotwords com visualização.
        
        Returns:
            bool: True se iniciado com sucesso
        """
        if not self.hotword_detector:
            self.set_status("❌ Hotword detector não disponível")
            return False
        
        # Configurar callback de detecção
        self.hotword_detector.set_detection_callback(self._on_hotword_detected)
        
        # Iniciar detecção
        success = self.hotword_detector.start_listening()
        
        if success:
            self.is_active = True
            
            # Iniciar visualização se configurado para sempre ativo
            if self.visual_mode == VisualMode.ALWAYS:
                self._start_visualization()
                
            self.set_status("🎙️ Escuta visual ativa")
        
        return success
    
    def stop_listening(self):
        """Para a escuta e visualização."""
        self.is_active = False
        
        # Para hotword detector
        if self.hotword_detector:
            self.hotword_detector.stop_listening()
        
        # Para visualização
        self._stop_visualization()
        
        self.set_status("🛑 Escuta visual parada")
    
    def _on_hotword_detected(self, detected_word: str):
        """Callback interno para detecção de hotword."""
        self.set_status(f"✅ Wake word detectado visualmente: {detected_word}")
        
        # Chamar callback do usuário se definido
        if self.detection_callback:
            try:
                self.detection_callback(detected_word)
            except Exception as e:
                logger.error(f"Erro no callback de detecção: {e}")
    
    def set_detection_callback(self, callback: Callable[[str], None]):
        """
        Define callback para detecção de hotword.
        
        Args:
            callback: Função chamada quando hotword é detectado
        """
        self.detection_callback = callback
    
    def set_visual_mode(self, mode: VisualMode):
        """
        Define o modo visual.
        
        Args:
            mode: Modo de operação visual
        """
        old_mode = self.visual_mode
        self.visual_mode = mode
        
        # Ajustar visualização baseado no novo modo
        if mode == VisualMode.OFF:
            self._stop_visualization()
        elif mode == VisualMode.ALWAYS and self.is_active:
            self._start_visualization()
        elif mode == VisualMode.LISTENING_ONLY and self.hotword_detector and not self.hotword_detector.is_listening:
            self._stop_visualization()
        
        self.set_status(f"🔄 Modo visual: {old_mode.value} → {mode.value}")
    
    def set_visualization_mode(self, mode: VisualizationMode):
        """
        Define o modo de visualização.
        
        Args:
            mode: Modo de visualização Manim
        """
        old_mode = self.visualization_mode
        self.visualization_mode = mode
        
        # Atualizar visualizador se ativo
        if self.audio_visualizer and self.audio_visualizer.is_active:
            self.audio_visualizer.set_mode(mode)
        
        self.set_status(f"🎨 Visualização: {old_mode.value} → {mode.value}")
    
    def set_sensitivity(self, sensitivity: float):
        """
        Ajusta sensibilidade da visualização.
        
        Args:
            sensitivity: Valor de 0.1 a 5.0
        """
        if self.audio_visualizer:
            self.audio_visualizer.set_sensitivity(sensitivity)
            self.set_status(f"🎚️ Sensibilidade visual: {sensitivity}")
    
    def set_colors(self, colors: list):
        """
        Define cores da visualização.
        
        Args:
            colors: Lista de cores em hex
        """
        if self.audio_visualizer:
            self.audio_visualizer.set_colors(colors)
            self.set_status(f"🎨 Cores atualizadas: {len(colors)} cores")
    
    def add_wake_word(self, word: str):
        """
        Adiciona nova wake word.
        
        Args:
            word: Palavra de ativação
        """
        if self.hotword_detector:
            self.hotword_detector.add_wake_word(word)
            self.set_status(f"➕ Wake word adicionada: {word}")
    
    def remove_wake_word(self, word: str):
        """
        Remove wake word.
        
        Args:
            word: Palavra a remover
        """
        if self.hotword_detector:
            self.hotword_detector.remove_wake_word(word)
            self.set_status(f"➖ Wake word removida: {word}")
    
    def get_status_info(self) -> dict:
        """Retorna informações completas de status."""
        status = {
            'is_active': self.is_active,
            'visual_mode': self.visual_mode.value,
            'visualization_mode': self.visualization_mode.value,
            'modules_available': MODULES_AVAILABLE
        }
        
        # Adicionar status do hotword detector
        if self.hotword_detector:
            hotword_status = self.hotword_detector.get_status_info()
            status['hotword'] = hotword_status
        
        # Adicionar status do visualizador
        if self.audio_visualizer:
            visualizer_status = self.audio_visualizer.get_status_info()
            status['visualizer'] = visualizer_status
        
        return status
    
    def shutdown(self):
        """Desliga completamente o sistema."""
        try:
            self.stop_listening()
            
            if self.hotword_detector:
                try:
                    self.hotword_detector.shutdown()
                except:
                    pass  # Ignorar erros no shutdown do hotword
            
            if self.audio_visualizer:
                try:
                    self.audio_visualizer.stop()
                except:
                    pass  # Ignorar erros no shutdown do visualizer
            
            self.set_status("🛑 Sistema visual desligado")
        except Exception as e:
            logger.error(f"Erro durante shutdown: {e}")


# Função utilitária para criar detector visual configurado
def create_visual_hotword_detector(
    status_callback: Optional[Callable[[str], None]] = None,
    visual_mode: VisualMode = VisualMode.LISTENING_ONLY,
    visualization_mode: VisualizationMode = VisualizationMode.PULSE
) -> VisualHotwordDetector:
    """
    Cria detector de hotword visual com configuração padrão.
    
    Args:
        status_callback: Função para status updates
        visual_mode: Modo de operação visual
        visualization_mode: Modo de visualização Manim
        
    Returns:
        VisualHotwordDetector: Instância configurada
    """
    detector = VisualHotwordDetector(status_callback)
    
    if detector.hotword_detector and detector.audio_visualizer:
        detector.set_visual_mode(visual_mode)
        detector.set_visualization_mode(visualization_mode)
        
        # Cores tema Astra
        Astra_colors = ["#00ff41", "#41ff00", "#00ffff", "#0080ff", "#ffffff"]
        detector.set_colors(Astra_colors)
        
        # Sensibilidade padrão
        detector.set_sensitivity(1.5)
    
    return detector


if __name__ == "__main__":
    # Teste do sistema integrado
    def on_status(message):
        print(f"Status: {message}")
    
    def on_detection(word):
        print(f"🎯 WAKE WORD DETECTADO VISUALMENTE: {word}")
    
    print("=== Astra Visual Hotword Detector Test ===")
    print("Sistema integrado de detecção visual de hotword...")
    
    if not MODULES_AVAILABLE:
        print("❌ Módulos não disponíveis. Verifique as importações.")
        exit(1)
    
    # Criar detector visual
    detector = create_visual_hotword_detector(
        status_callback=on_status,
        visual_mode=VisualMode.LISTENING_ONLY,
        visualization_mode=VisualizationMode.PULSE
    )
    
    # Configurar callback de detecção
    detector.set_detection_callback(on_detection)
    
    print("\n🎨 Configuração:")
    print(f"  - Modo Visual: {detector.visual_mode.value}")
    print(f"  - Visualização: {detector.visualization_mode.value}")
    print(f"  - Status: {detector.get_status_info()}")
    
    print("\nIniciando escuta visual...")
    print("Diga 'Astra', 'Alex' ou outra wake word.")
    print("Você verá animações reagindo ao som!")
    print("Pressione Ctrl+C para sair.")
    
    success = detector.start_listening()
    
    if not success:
        print("❌ Falha ao iniciar sistema visual")
        exit(1)
    
    try:
        # Testar diferentes modos visuais
        modes = [VisualizationMode.PULSE, VisualizationMode.CIRCLE_WAVE, 
                VisualizationMode.BARS, VisualizationMode.PARTICLES]
        mode_idx = 0
        
        while True:
            time.sleep(15)  # Trocar modo a cada 15 segundos
            
            mode_idx = (mode_idx + 1) % len(modes)
            new_mode = modes[mode_idx]
            
            print(f"\n🔄 Trocando visualização para: {new_mode.value}")
            detector.set_visualization_mode(new_mode)
            
    except KeyboardInterrupt:
        print("\n\nParando sistema visual...")
        detector.shutdown()
        print("✅ Sistema visual parado com sucesso!")
        print("🎨 Obrigado por testar as animações do Astra!")
