#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Configuração do Sistema de Visualização
Configurações para feedback visual durante escuta e interações.
"""

from dataclasses import dataclass
from typing import List, Optional
from modules.audio_visualizer import VisualizationMode
from modules.visual_hotword_detector import VisualMode


@dataclass
class VisualConfig:
    """Configurações do sistema de visualização"""
    
    # Habilitar/desabilitar visualização
    enabled: bool = True
    
    # Modo visual padrão
    visual_mode: VisualMode = VisualMode.LISTENING_ONLY
    
    # Modo de visualização padrão
    visualization_mode: VisualizationMode = VisualizationMode.PULSE
    
    # Sensibilidade da visualização (0.1 - 3.0)
    sensitivity: float = 1.5
    
    # Cores da visualização (hex codes)
    colors: List[str] = None
    
    # Mostrar visualização em janela separada
    show_window: bool = False
    
    # Salvar visualizações como vídeo
    save_video: bool = False
    
    # Resolução da visualização (largura, altura)
    resolution: tuple = (800, 600)
    
    # FPS da visualização
    fps: int = 30
    
    def __post_init__(self):
        if self.colors is None:
            self.colors = [
                "#00ff41",  # Matrix green
                "#41ff00",  # Lime green  
                "#ff4100",  # Orange red
                "#4100ff",  # Blue purple
                "#ff0041"   # Pink red
            ]


class VisualConfigManager:
    """Gerenciador de configurações de visualização"""
    
    def __init__(self):
        self.config = VisualConfig()
        self._load_user_preferences()
    
    def _load_user_preferences(self):
        """Carrega preferências do usuário do arquivo de configuração"""
        try:
            import json
            from pathlib import Path
            
            config_file = Path("config/visual_preferences.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                
                # Atualizar configurações com preferências do usuário
                for key, value in prefs.items():
                    if hasattr(self.config, key):
                        # Converter strings de enum de volta para enum
                        if key == 'visual_mode':
                            value = VisualMode(value)
                        elif key == 'visualization_mode':
                            value = VisualizationMode(value)
                        
                        setattr(self.config, key, value)
                        
        except Exception as e:
            print(f"⚠️ Erro ao carregar preferências visuais: {e}")
    
    def save_preferences(self):
        """Salva as configurações atuais"""
        try:
            import json
            from pathlib import Path
            
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            
            # Converter enums para strings para serialização
            prefs = {}
            for key, value in self.config.__dict__.items():
                if hasattr(value, 'value'):  # É um enum
                    prefs[key] = value.value
                else:
                    prefs[key] = value
            
            config_file = config_dir / "visual_preferences.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar preferências visuais: {e}")
            return False
    
    def get_config(self) -> VisualConfig:
        """Retorna a configuração atual"""
        return self.config
    
    def update_config(self, **kwargs):
        """Atualiza configurações específicas"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Salvar automaticamente
        self.save_preferences()
    
    def reset_to_defaults(self):
        """Restaura configurações padrão"""
        self.config = VisualConfig()
        self.save_preferences()


def get_visual_config() -> VisualConfig:
    """Função helper para obter configurações visuais"""
    manager = VisualConfigManager()
    return manager.get_config()


def update_visual_config(**kwargs) -> bool:
    """Função helper para atualizar configurações visuais"""
    manager = VisualConfigManager()
    manager.update_config(**kwargs)
    return True


# Configurações de exemplo para diferentes cenários
VISUAL_PRESETS = {
    "minimalista": VisualConfig(
        visual_mode=VisualMode.LISTENING_ONLY,
        visualization_mode=VisualizationMode.PULSE,
        sensitivity=1.0,
        colors=["#00ff41", "#41ff00"]
    ),
    
    "completo": VisualConfig(
        visual_mode=VisualMode.ALWAYS,
        visualization_mode=VisualizationMode.BARS,
        sensitivity=2.0,
        colors=["#00ff41", "#41ff00", "#ff4100", "#4100ff", "#ff0041"]
    ),
    
    "discreto": VisualConfig(
        visual_mode=VisualMode.REACTIVE,
        visualization_mode=VisualizationMode.PULSE,
        sensitivity=0.8,
        colors=["#004400", "#002200"]
    ),
    
    "festa": VisualConfig(
        visual_mode=VisualMode.ALWAYS,
        visualization_mode=VisualizationMode.PARTICLES,
        sensitivity=2.5,
        colors=["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"]
    )
}


def apply_preset(preset_name: str) -> bool:
    """Aplica um preset de configuração visual"""
    if preset_name in VISUAL_PRESETS:
        manager = VisualConfigManager()
        manager.config = VISUAL_PRESETS[preset_name]
        manager.save_preferences()
        print(f"✅ Preset '{preset_name}' aplicado com sucesso!")
        return True
    else:
        print(f"❌ Preset '{preset_name}' não encontrado")
        print(f"Presets disponíveis: {list(VISUAL_PRESETS.keys())}")
        return False
