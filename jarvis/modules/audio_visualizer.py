#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Astra - Audio Visualizer with Manim
Sistema de visualização de áudio em tempo real que reage às vibrações sonoras
durante o modo de escuta do assistente usando animações Manim.

Funcionalidades:
- Captura de áudio em tempo real
- Análise de amplitude e frequência 
- Visualizações animadas com Manim
- Integração com sistema de hotword detection
- Múltiplos modos de visualização
"""

import logging
import threading
import time
import numpy as np
import pyaudio
from typing import Optional, Callable, List
from enum import Enum
import queue
import math

try:
    from manim import *
    from manim.opengl import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False
    logging.warning("Manim não está disponível. Visualização desabilitada.")

# Configure logger
logger = logging.getLogger(__name__)

class VisualizationMode(Enum):
    """Modos de visualização disponíveis."""
    WAVEFORM = "waveform"          # Forma de onda
    SPECTRUM = "spectrum"          # Espectro de frequência  
    CIRCLE_WAVE = "circle_wave"    # Onda circular
    PULSE = "pulse"                # Pulsação central
    BARS = "bars"                  # Barras de frequência
    PARTICLES = "particles"        # Sistema de partículas

class AudioVisualizer:
    """
    Sistema de visualização de áudio em tempo real com Manim.
    Cria animações que reagem às vibrações sonoras captadas pelo microfone.
    """
    
    def __init__(self, status_callback: Optional[Callable[[str], None]] = None):
        """
        Inicializa o visualizador de áudio.
        
        Args:
            status_callback: Função para receber atualizações de status
        """
        self.status_callback = status_callback
        self.is_active = False
        self.is_listening = False
        
        # Configurações de áudio
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        
        # PyAudio
        self.audio = None
        self.stream = None
        
        # Threads de controle
        self.audio_thread = None
        self.visualizer_thread = None
        self._shutdown = False
        
        # Dados de áudio
        self.audio_queue = queue.Queue(maxsize=100)
        self.current_amplitude = 0.0
        self.current_frequencies = np.zeros(512)
        
        # Configurações de visualização
        self.mode = VisualizationMode.PULSE
        self.sensitivity = 1.0
        self.colors = ["#00ff41", "#41ff00", "#ff4100", "#4100ff"]  # Matrix green, etc
        
        # Verificar se Manim está disponível
        if not MANIM_AVAILABLE:
            self.set_status("⚠️ Manim não disponível - visualização desabilitada")
            return
            
        self.set_status("🎨 Audio Visualizer inicializado")
    
    def set_status(self, message: str):
        """Envia atualização de status."""
        if self.status_callback:
            self.status_callback(f"[VISUALIZER] {message}")
        logger.info(f"AudioVisualizer: {message}")
    
    def start(self, mode: VisualizationMode = None) -> bool:
        """
        Inicia a captura de áudio e visualização.
        
        Args:
            mode: Modo de visualização a usar
            
        Returns:
            bool: True se iniciado com sucesso
        """
        if not MANIM_AVAILABLE:
            self.set_status("❌ Manim não disponível")
            return False
            
        if self.is_active:
            return True
            
        if mode:
            self.mode = mode
            
        try:
            # Inicializar PyAudio
            self.audio = pyaudio.PyAudio()
            
            # Verificar dispositivos de áudio disponíveis
            input_device_count = self.audio.get_device_count()
            if input_device_count == 0:
                raise Exception("Nenhum dispositivo de áudio encontrado")
            
            # Configurar stream de áudio
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.is_active = True
            self.is_listening = True
            self._shutdown = False
            
            # Iniciar threads
            self.audio_thread = threading.Thread(target=self._audio_loop, daemon=True)
            self.visualizer_thread = threading.Thread(target=self._visualizer_loop, daemon=True)
            
            self.audio_thread.start()
            self.visualizer_thread.start()
            
            self.stream.start_stream()
            
            self.set_status(f"🎨 Visualização ativa - Modo: {self.mode.value}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar visualizador: {e}")
            self.set_status(f"❌ Erro ao iniciar: {e}")
            return False
    
    def stop(self):
        """Para a visualização e libera recursos."""
        if not self.is_active:
            return
            
        self.is_active = False
        self.is_listening = False
        self._shutdown = True
        
        try:
            if self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except:
                    pass  # Ignorar erros ao fechar stream
                    
            if self.audio:
                try:
                    self.audio.terminate()
                except:
                    pass  # Ignorar erros ao terminar audio
                
            # Aguardar threads terminarem
            if self.audio_thread and self.audio_thread.is_alive():
                self.audio_thread.join(timeout=2)
                
            if self.visualizer_thread and self.visualizer_thread.is_alive():
                self.visualizer_thread.join(timeout=2)
                
        except Exception as e:
            logger.error(f"Erro ao parar visualizador: {e}")
            
        self.set_status("🛑 Visualização parada")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback do PyAudio para dados de áudio."""
        if not self._shutdown and self.is_listening:
            try:
                # Converter dados para numpy array
                audio_data = np.frombuffer(in_data, dtype=np.int16)
                
                # Adicionar à fila se não estiver cheia
                if not self.audio_queue.full():
                    self.audio_queue.put_nowait(audio_data)
                    
            except Exception as e:
                logger.error(f"Erro no callback de áudio: {e}")
                
        return (None, pyaudio.paContinue)
    
    def _audio_loop(self):
        """Loop principal de processamento de áudio."""
        while not self._shutdown and self.is_active:
            try:
                # Obter dados da fila (timeout para evitar bloqueio)
                audio_data = self.audio_queue.get(timeout=0.1)
                
                # Processar dados de áudio
                self._process_audio_data(audio_data)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Erro no loop de áudio: {e}")
                time.sleep(0.01)
    
    def _process_audio_data(self, audio_data):
        """
        Processa os dados de áudio para extrair informações visuais.
        
        Args:
            audio_data: Dados de áudio como numpy array
        """
        try:
            # Verificar se dados são válidos
            if audio_data is None or len(audio_data) == 0:
                return
                
            # Normalizar dados (-1.0 a 1.0)
            normalized = audio_data.astype(np.float32) / 32768.0
            
            # Calcular amplitude (RMS)
            self.current_amplitude = np.sqrt(np.mean(normalized ** 2))
            
            # Aplicar janela para FFT
            windowed = normalized * np.hanning(len(normalized))
            
            # Calcular FFT para análise de frequência
            fft = np.fft.fft(windowed)
            
            # Obter magnitude e frequências
            magnitude = np.abs(fft[:len(fft)//2])
            
            # Redimensionar para 512 bins
            if len(magnitude) > 512:
                # Downsample
                step = len(magnitude) // 512
                self.current_frequencies = magnitude[::step][:512]
            else:
                # Upsample com zeros
                self.current_frequencies = np.pad(magnitude, (0, 512 - len(magnitude)))
                
            # Aplicar sensibilidade
            self.current_amplitude *= self.sensitivity
            self.current_frequencies *= self.sensitivity
            
        except Exception as e:
            logger.error(f"Erro ao processar áudio: {e}")
    
    def _visualizer_loop(self):
        """Loop principal de visualização."""
        self.set_status(f"🎨 Iniciando visualização - Modo: {self.mode.value}")
        
        try:
            if self.mode == VisualizationMode.PULSE:
                self._run_pulse_visualization()
            elif self.mode == VisualizationMode.WAVEFORM:
                self._run_waveform_visualization()
            elif self.mode == VisualizationMode.SPECTRUM:
                self._run_spectrum_visualization()
            elif self.mode == VisualizationMode.CIRCLE_WAVE:
                self._run_circle_wave_visualization()
            elif self.mode == VisualizationMode.BARS:
                self._run_bars_visualization()
            elif self.mode == VisualizationMode.PARTICLES:
                self._run_particles_visualization()
                
        except Exception as e:
            logger.error(f"Erro na visualização: {e}")
            self.set_status(f"❌ Erro na visualização: {e}")
    
    def _run_pulse_visualization(self):
        """Executa visualização de pulsação central."""
        self.set_status("🎵 Executando visualização de pulso")
        
        # Simulação da visualização (em implementação real usaria Manim scene)
        while not self._shutdown and self.is_active:
            try:
                # Calcular tamanho do pulso baseado na amplitude
                pulse_size = max(0.1, self.current_amplitude * 5.0)
                
                # Calcular cor baseada na frequência dominante
                dominant_freq_idx = np.argmax(self.current_frequencies[:100])
                color_idx = dominant_freq_idx % len(self.colors)
                
                # Log da visualização (em implementação real seria renderização)
                if self.current_amplitude > 0.01:  # Só mostrar se há áudio significativo
                    logger.debug(f"Pulso: tamanho={pulse_size:.3f}, cor={self.colors[color_idx]}")
                
                time.sleep(1/60)  # 60 FPS
                
            except Exception as e:
                logger.error(f"Erro na visualização de pulso: {e}")
                break
    
    def _run_waveform_visualization(self):
        """Executa visualização de forma de onda."""
        self.set_status("🌊 Executando visualização de onda")
        
        waveform_history = []
        
        while not self._shutdown and self.is_active:
            try:
                # Manter histórico de 100 pontos
                waveform_history.append(self.current_amplitude)
                if len(waveform_history) > 100:
                    waveform_history.pop(0)
                
                # Log da forma de onda
                if len(waveform_history) > 10:
                    avg_amp = np.mean(waveform_history[-10:])
                    if avg_amp > 0.01:
                        logger.debug(f"Onda: amplitude_média={avg_amp:.3f}")
                
                time.sleep(1/60)
                
            except Exception as e:
                logger.error(f"Erro na visualização de onda: {e}")
                break
    
    def _run_spectrum_visualization(self):
        """Executa visualização de espectro de frequência."""
        self.set_status("📊 Executando visualização de espectro")
        
        while not self._shutdown and self.is_active:
            try:
                # Encontrar picos de frequência
                freq_peaks = []
                for i in range(1, len(self.current_frequencies)-1):
                    if (self.current_frequencies[i] > self.current_frequencies[i-1] and 
                        self.current_frequencies[i] > self.current_frequencies[i+1] and
                        self.current_frequencies[i] > 0.1):
                        freq_peaks.append((i, self.current_frequencies[i]))
                
                # Log dos picos principais
                if freq_peaks:
                    main_peaks = sorted(freq_peaks, key=lambda x: x[1], reverse=True)[:5]
                    logger.debug(f"Espectro: {len(main_peaks)} picos principais")
                
                time.sleep(1/60)
                
            except Exception as e:
                logger.error(f"Erro na visualização de espectro: {e}")
                break
    
    def _run_circle_wave_visualization(self):
        """Executa visualização de onda circular."""
        self.set_status("⭕ Executando visualização circular")
        
        angle_offset = 0
        
        while not self._shutdown and self.is_active:
            try:
                # Criar onda circular baseada na amplitude
                radius_base = 1.0
                radius_variation = self.current_amplitude * 2.0
                
                # Rotacionar baseado na frequência
                rotation_speed = np.mean(self.current_frequencies[:50]) * 0.1
                angle_offset += rotation_speed
                
                if self.current_amplitude > 0.01:
                    logger.debug(f"Circular: raio={radius_base + radius_variation:.3f}, rotação={angle_offset:.2f}")
                
                time.sleep(1/60)
                
            except Exception as e:
                logger.error(f"Erro na visualização circular: {e}")
                break
    
    def _run_bars_visualization(self):
        """Executa visualização de barras de frequência.""" 
        self.set_status("📊 Executando visualização de barras")
        
        while not self._shutdown and self.is_active:
            try:
                # Dividir espectro em 20 barras
                num_bars = 20
                bar_size = len(self.current_frequencies) // num_bars
                bars = []
                
                for i in range(num_bars):
                    start_idx = i * bar_size
                    end_idx = min((i + 1) * bar_size, len(self.current_frequencies))
                    bar_height = np.mean(self.current_frequencies[start_idx:end_idx])
                    bars.append(bar_height)
                
                # Log das barras mais altas
                max_bars = [(i, h) for i, h in enumerate(bars) if h > 0.1]
                if max_bars:
                    logger.debug(f"Barras: {len(max_bars)} barras ativas")
                
                time.sleep(1/60)
                
            except Exception as e:
                logger.error(f"Erro na visualização de barras: {e}")
                break
    
    def _run_particles_visualization(self):
        """Executa visualização de sistema de partículas."""
        self.set_status("✨ Executando visualização de partículas")
        
        particles = []
        
        while not self._shutdown and self.is_active:
            try:
                # Criar novas partículas baseadas na amplitude
                if self.current_amplitude > 0.05:
                    num_new_particles = int(self.current_amplitude * 20)
                    for _ in range(min(num_new_particles, 10)):
                        particle = {
                            'x': 0,
                            'y': 0, 
                            'vx': np.random.uniform(-1, 1),
                            'vy': np.random.uniform(-1, 1),
                            'life': 1.0,
                            'size': self.current_amplitude
                        }
                        particles.append(particle)
                
                # Atualizar partículas existentes
                particles = [p for p in particles if p['life'] > 0]
                for particle in particles:
                    particle['x'] += particle['vx'] * 0.1
                    particle['y'] += particle['vy'] * 0.1
                    particle['life'] -= 0.02
                
                if particles:
                    logger.debug(f"Partículas: {len(particles)} ativas")
                
                time.sleep(1/60)
                
            except Exception as e:
                logger.error(f"Erro na visualização de partículas: {e}")
                break
    
    def set_mode(self, mode: VisualizationMode):
        """
        Altera o modo de visualização.
        
        Args:
            mode: Novo modo de visualização
        """
        old_mode = self.mode
        self.mode = mode
        
        self.set_status(f"🔄 Modo alterado: {old_mode.value} → {mode.value}")
    
    def set_sensitivity(self, sensitivity: float):
        """
        Ajusta a sensibilidade da visualização.
        
        Args:
            sensitivity: Valor de sensibilidade (0.1 a 5.0)
        """
        self.sensitivity = max(0.1, min(5.0, sensitivity))
        self.set_status(f"🎚️ Sensibilidade: {self.sensitivity:.1f}")
    
    def set_colors(self, colors: List[str]):
        """
        Define cores personalizadas para a visualização.
        
        Args:
            colors: Lista de cores em formato hex
        """
        if colors and len(colors) > 0:
            self.colors = colors
            self.set_status(f"🎨 Cores atualizadas: {len(colors)} cores")
    
    def get_status_info(self) -> dict:
        """Retorna informações de status do visualizador."""
        return {
            'is_active': self.is_active,
            'is_listening': self.is_listening,
            'mode': self.mode.value,
            'current_amplitude': float(self.current_amplitude),
            'sensitivity': self.sensitivity,
            'manim_available': MANIM_AVAILABLE,
            'sample_rate': self.sample_rate
        }


# Classe para integração com Manim Scene (implementação futura)
if MANIM_AVAILABLE:
    class AudioVisualizationScene(Scene):
        """
        Cena Manim para renderização de visualizações de áudio.
        Esta é uma base para implementação futura de renderização real.
        """
        
        def __init__(self, visualizer: AudioVisualizer, **kwargs):
            super().__init__(**kwargs)
            self.visualizer = visualizer
        
        def construct(self):
            """Constrói a cena de visualização."""
            # Implementação futura para renderização real com Manim
            pass
else:
    # Classe dummy se Manim não estiver disponível
    class AudioVisualizationScene:
        def __init__(self, *args, **kwargs):
            pass


# Função utilitária para criar visualizador
def create_audio_visualizer(status_callback: Optional[Callable[[str], None]] = None,
                           mode: VisualizationMode = VisualizationMode.PULSE) -> AudioVisualizer:
    """
    Cria um visualizador de áudio com configuração padrão.
    
    Args:
        status_callback: Função para receber updates de status
        mode: Modo de visualização inicial
        
    Returns:
        AudioVisualizer: Instância configurada
    """
    visualizer = AudioVisualizer(status_callback)
    visualizer.set_mode(mode)
    
    # Cores tema Astra/Matrix
    Astra_colors = ["#00ff41", "#41ff00", "#00ffff", "#0080ff", "#4000ff"]
    visualizer.set_colors(Astra_colors)
    
    return visualizer


if __name__ == "__main__":
    # Teste do sistema
    def on_status(message):
        print(f"Status: {message}")
    
    print("=== Astra Audio Visualizer Test ===")
    print("Testando sistema de visualização de áudio...")
    
    visualizer = create_audio_visualizer(on_status, VisualizationMode.PULSE)
    
    if not MANIM_AVAILABLE:
        print("⚠️ Manim não está disponível. Instale com: pip install manim")
        exit(1)
    
    print("Iniciando visualização...")
    print("Fale algo no microfone para ver a reação!")
    print("Pressione Ctrl+C para sair.")
    
    visualizer.start()
    
    try:
        # Testar diferentes modos
        modes = list(VisualizationMode)
        mode_idx = 0
        
        while True:
            time.sleep(10)  # Trocar modo a cada 10 segundos
            
            mode_idx = (mode_idx + 1) % len(modes)
            new_mode = modes[mode_idx]
            
            print(f"\n🔄 Trocando para modo: {new_mode.value}")
            visualizer.set_mode(new_mode)
            
    except KeyboardInterrupt:
        print("\nParando visualizador...")
        visualizer.stop()
        print("✅ Visualizador parado com sucesso!")
