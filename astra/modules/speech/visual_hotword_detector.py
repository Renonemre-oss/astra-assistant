#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Hotword Detector com Visualização Integrada
Sistema que combina detecção de wake words com feedback visual imersivo.
"""

import logging
from typing import Optional, Callable
from ..modules.speech.hotword_detector import HotwordDetector, HotwordStatus
from ..modules.visual_hotword_detector import create_visual_hotword_detector, VisualMode
from ..modules.audio_visualizer import VisualizationMode
from config.visual_config import get_visual_config

logger = logging.getLogger(__name__)


class VisualHotwordSystem:
    """Sistema integrado de detecção de hotword com visualização"""
    
    def __init__(self, status_callback: Optional[Callable[[str], None]] = None,
                 detection_callback: Optional[Callable[[str], None]] = None):
        """
        Inicializa o sistema visual de hotword.
        
        Args:
            status_callback: Callback para atualizações de status
            detection_callback: Callback para quando hotword é detectado
        """
        self.status_callback = status_callback
        self.detection_callback = detection_callback
        
        # Carregar configurações visuais
        self.visual_config = get_visual_config()
        
        # Inicializar componentes
        self.hotword_detector = None
        self.visual_detector = None
        self.is_visual_enabled = self.visual_config.enabled
        
        self._initialize_system()
    
    def _initialize_system(self):
        """Inicializa o sistema de detecção"""
        try:
            if self.is_visual_enabled:
                # Sistema visual completo
                self.set_status("🎨 Inicializando sistema visual de hotword...")
                
                def visual_status_callback(message):
                    if self.status_callback:
                        self.status_callback(f"[VISUAL] {message}")
                
                # Criar detector visual integrado
                self.visual_detector = create_visual_hotword_detector(
                    status_callback=visual_status_callback,
                    visual_mode=self.visual_config.visual_mode,
                    visualization_mode=self.visual_config.visualization_mode
                )
                
                # Configurar detector visual
                if self.visual_detector:
                    self.visual_detector.set_sensitivity(self.visual_config.sensitivity)
                    self.visual_detector.set_colors(self.visual_config.colors)
                    
                    # Configurar callback de detecção
                    self.visual_detector.set_detection_callback(self._on_hotword_detected)
                    
                    self.set_status("✅ Sistema visual de hotword inicializado")
                else:
                    self.set_status("⚠️ Detector visual falhou, usando sistema básico")
                    self.is_visual_enabled = False
            
            # Fallback para sistema básico se visual não funcionar
            if not self.is_visual_enabled or not self.visual_detector:
                self.set_status("🎤 Inicializando sistema básico de hotword...")
                
                self.hotword_detector = HotwordDetector(self._on_basic_status)
                if self.hotword_detector:
                    self.hotword_detector.set_detection_callback(self._on_hotword_detected)
                    self.set_status("✅ Sistema básico de hotword inicializado")
                else:
                    self.set_status("❌ Falha ao inicializar sistema de hotword")
                    
        except Exception as e:
            logger.error(f"Erro na inicialização do sistema: {e}")
            self.set_status(f"❌ Erro na inicialização: {e}")
    
    def set_status(self, message: str):
        """Envia atualização de status"""
        if self.status_callback:
            self.status_callback(message)
        logger.info(f"VisualHotwordSystem: {message}")
    
    def _on_basic_status(self, message: str):
        """Callback para status do detector básico"""
        if self.status_callback:
            self.status_callback(message)
    
    def _on_hotword_detected(self, detected_word: str):
        """Callback interno para detecção de hotword"""
        self.set_status(f"✅ Wake word detectado: {detected_word}")
        
        if self.detection_callback:
            try:
                self.detection_callback(detected_word)
            except Exception as e:
                logger.error(f"Erro no callback de detecção: {e}")
    
    def start_listening(self) -> bool:
        """
        Inicia a escuta de hotwords com visualização.
        
        Returns:
            bool: True se iniciado com sucesso
        """
        try:
            if self.visual_detector:
                success = self.visual_detector.start_listening()
                if success:
                    self.set_status("🎨 Sistema visual de escuta ativo")
                return success
            elif self.hotword_detector:
                success = self.hotword_detector.start_listening()
                if success:
                    self.set_status("🎤 Sistema básico de escuta ativo")
                return success
            else:
                self.set_status("❌ Nenhum sistema de detecção disponível")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao iniciar escuta: {e}")
            self.set_status(f"❌ Erro ao iniciar escuta: {e}")
            return False
    
    def stop_listening(self):
        """Para a escuta de hotwords"""
        try:
            if self.visual_detector:
                self.visual_detector.stop_listening()
                self.set_status("🛑 Sistema visual de escuta parado")
            elif self.hotword_detector:
                self.hotword_detector.stop_listening()
                self.set_status("🛑 Sistema básico de escuta parado")
                
        except Exception as e:
            logger.error(f"Erro ao parar escuta: {e}")
    
    def shutdown(self):
        """Encerra completamente o sistema"""
        try:
            self.stop_listening()
            
            if self.visual_detector and hasattr(self.visual_detector, 'shutdown'):
                self.visual_detector.shutdown()
            
            if self.hotword_detector and hasattr(self.hotword_detector, 'shutdown'):
                self.hotword_detector.shutdown()
                
            self.set_status("🔐 Sistema de hotword encerrado")
            
        except Exception as e:
            logger.error(f"Erro no shutdown: {e}")
    
    def set_detection_callback(self, callback: Callable[[str], None]):
        """Define o callback para detecção de hotword"""
        self.detection_callback = callback
    
    def add_wake_word(self, word: str):
        """Adiciona uma nova palavra de ativação"""
        if self.visual_detector and hasattr(self.visual_detector, 'add_wake_word'):
            self.visual_detector.add_wake_word(word)
        elif self.hotword_detector:
            self.hotword_detector.add_wake_word(word)
    
    def remove_wake_word(self, word: str):
        """Remove uma palavra de ativação"""
        if self.visual_detector and hasattr(self.visual_detector, 'remove_wake_word'):
            self.visual_detector.remove_wake_word(word)
        elif self.hotword_detector:
            self.hotword_detector.remove_wake_word(word)
    
    def is_listening(self) -> bool:
        """Verifica se está escutando"""
        if self.visual_detector:
            return getattr(self.visual_detector, 'is_active', False)
        elif self.hotword_detector:
            return getattr(self.hotword_detector, 'is_listening', False)
        return False
    
    def get_status_info(self) -> dict:
        """Retorna informações de status do sistema"""
        info = {
            'visual_enabled': self.is_visual_enabled,
            'is_listening': self.is_listening(),
            'system_type': 'visual' if self.visual_detector else 'basic'
        }
        
        if self.visual_detector and hasattr(self.visual_detector, 'get_status_info'):
            info.update(self.visual_detector.get_status_info())
        
        return info
    
    def toggle_visual_mode(self):
        """Alterna entre modo visual e modo básico"""
        if self.visual_detector:
            # Alternar configurações visuais
            current_mode = self.visual_detector.visual_mode
            if current_mode == VisualMode.OFF:
                new_mode = VisualMode.LISTENING_ONLY
            elif current_mode == VisualMode.LISTENING_ONLY:
                new_mode = VisualMode.ALWAYS
            elif current_mode == VisualMode.ALWAYS:
                new_mode = VisualMode.REACTIVE
            else:
                new_mode = VisualMode.OFF
            
            self.visual_detector.set_visual_mode(new_mode)
            self.set_status(f"🎨 Modo visual alterado: {new_mode.value}")
        else:
            self.set_status("⚠️ Sistema visual não disponível")
    
    def set_visualization_preset(self, preset_name: str):
        """Aplica um preset de visualização"""
        try:
            from config.visual_config import apply_preset, VISUAL_PRESETS
            
            if apply_preset(preset_name):
                # Recarregar configurações
                self.visual_config = get_visual_config()
                
                # Aplicar ao detector visual se disponível
                if self.visual_detector:
                    preset = VISUAL_PRESETS[preset_name]
                    self.visual_detector.set_visual_mode(preset.visual_mode)
                    self.visual_detector.set_visualization_mode(preset.visualization_mode)
                    self.visual_detector.set_sensitivity(preset.sensitivity)
                    self.visual_detector.set_colors(preset.colors)
                
                self.set_status(f"✅ Preset '{preset_name}' aplicado com sucesso")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Erro ao aplicar preset: {e}")
            self.set_status(f"❌ Erro ao aplicar preset: {e}")
            return False


def create_visual_hotword_system(status_callback: Optional[Callable[[str], None]] = None,
                                detection_callback: Optional[Callable[[str], None]] = None) -> VisualHotwordSystem:
    """
    Factory function para criar um sistema visual de hotword.
    
    Args:
        status_callback: Callback para atualizações de status
        detection_callback: Callback para quando hotword é detectado
    
    Returns:
        VisualHotwordSystem: Sistema configurado
    """
    return VisualHotwordSystem(status_callback, detection_callback)


# Função de compatibilidade com sistema antigo
def create_enhanced_hotword_detector(*args, **kwargs):
    """Alias para compatibilidade com sistema antigo"""
    return create_visual_hotword_system(*args, **kwargs)
