#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎙️ ASTRA - Interface de Gravação de Áudio
Sistema para gravar áudio de qualidade para clonagem de voz.

Funcionalidades:
- Gravação com interface gráfica
- Monitoramento de nível de áudio
- Pré-visualização e edição
- Validação de qualidade
- Export para clonagem
"""

import os
import time
import wave
import threading
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyaudio
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import librosa
import soundfile as sf
from pathlib import Path


class AudioRecorder:
    """
    Sistema de gravação de áudio para voice cloning.
    """
    
    def __init__(self):
        """Inicializa o gravador de áudio."""
        # Configurações de áudio
        self.sample_rate = 22050
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        
        # Estado da gravação
        self.is_recording = False
        self.is_playing = False
        self.audio_data = []
        self.recorded_frames = []
        
        # PyAudio
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # Arquivos
        self.current_file = None
        self.output_dir = Path("speech/recorded_audio")
        self.output_dir.mkdir(exist_ok=True)
    
    def get_audio_devices(self):
        """Lista dispositivos de áudio disponíveis."""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'sample_rate': int(info['defaultSampleRate'])
                })
        return devices
    
    def start_recording(self, device_index=None):
        """Inicia a gravação."""
        try:
            self.recorded_frames = []
            self.is_recording = True
            
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.stream.start_stream()
            return True
            
        except Exception as e:
            print(f"Erro ao iniciar gravação: {e}")
            return False
    
    def stop_recording(self):
        """Para a gravação."""
        if self.is_recording:
            self.is_recording = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            return True
        return False
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback para processar áudio."""
        if self.is_recording:
            self.recorded_frames.append(in_data)
        return (in_data, pyaudio.paContinue)
    
    def save_recording(self, filename):
        """Salva a gravação atual."""
        if not self.recorded_frames:
            return False
        
        try:
            filepath = self.output_dir / filename
            with wave.open(str(filepath), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.recorded_frames))
            
            self.current_file = filepath
            return True
            
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            return False
    
    def get_audio_data(self):
        """Retorna dados de áudio como numpy array."""
        if not self.recorded_frames:
            return None
        
        audio_data = np.frombuffer(b''.join(self.recorded_frames), dtype=np.int16)
        return audio_data / 32768.0  # Normalizar para [-1, 1]
    
    def get_audio_info(self):
        """Retorna informações do áudio gravado."""
        if not self.recorded_frames:
            return None
        
        audio_data = self.get_audio_data()
        duration = len(audio_data) / self.sample_rate
        
        # Calcular RMS com segurança
        try:
            audio_squared = audio_data**2
            mean_squared = np.mean(audio_squared)
            rms = np.sqrt(mean_squared) if mean_squared >= 0 else 0.0
        except (ValueError, RuntimeWarning):
            rms = 0.0
        
        return {
            'duration': round(duration, 2),
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'rms_level': round(rms, 4),
            'max_amplitude': round(np.max(np.abs(audio_data)), 4)
        }
    
    def cleanup(self):
        """Limpa recursos."""
        if self.stream:
            self.stream.close()
        self.audio.terminate()


class AudioRecorderGUI:
    """
    Interface gráfica para gravação de áudio.
    """
    
    def __init__(self):
        """Inicializa a interface."""
        self.recorder = AudioRecorder()
        self.recording_thread = None
        self.is_monitoring = False
        
        # Interface
        self.setup_gui()
        
        # Configuração inicial
        self.update_devices()
        self.start_level_monitoring()
    
    def setup_gui(self):
        """Configura a interface gráfica."""
        self.root = tk.Tk()
        self.root.title("🎙️ ASTRA - Gravador de Voz")
        self.root.geometry("800x600")
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="🎙️ Gravador de Voz ASTRA", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Seleção de dispositivo
        device_frame = ttk.LabelFrame(main_frame, text="Dispositivo de Áudio", padding="5")
        device_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(device_frame, textvariable=self.device_var, 
                                        state="readonly", width=60)
        self.device_combo.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(device_frame, text="Atualizar", 
                  command=self.update_devices).grid(row=0, column=1)
        
        # Controles de gravação
        control_frame = ttk.LabelFrame(main_frame, text="Controles", padding="5")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.record_btn = ttk.Button(control_frame, text="🔴 Gravar", 
                                    command=self.toggle_recording, width=15)
        self.record_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.play_btn = ttk.Button(control_frame, text="▶️ Reproduzir", 
                                  command=self.play_audio, state="disabled", width=15)
        self.play_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.save_btn = ttk.Button(control_frame, text="💾 Salvar", 
                                  command=self.save_audio, state="disabled", width=15)
        self.save_btn.grid(row=0, column=2, padx=(0, 10))
        
        self.clone_btn = ttk.Button(control_frame, text="🎯 Clonar Voz", 
                                   command=self.clone_voice, state="disabled", width=15)
        self.clone_btn.grid(row=0, column=3)
        
        # Monitor de nível
        level_frame = ttk.LabelFrame(main_frame, text="Nível de Áudio", padding="5")
        level_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.level_var = tk.DoubleVar()
        self.level_bar = ttk.Progressbar(level_frame, variable=self.level_var, 
                                        maximum=100, length=400)
        self.level_bar.grid(row=0, column=0, padx=(0, 10))
        
        self.level_label = ttk.Label(level_frame, text="0%")
        self.level_label.grid(row=0, column=1)
        
        # Informações do áudio
        info_frame = ttk.LabelFrame(main_frame, text="Informações", padding="5")
        info_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=6, width=80)
        info_scroll = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scroll.set)
        
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        info_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Gráfico de onda (simplificado)
        graph_frame = ttk.LabelFrame(main_frame, text="Visualização", padding="5")
        graph_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        
        # Configurar grid weights
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
    
    def update_devices(self):
        """Atualiza lista de dispositivos."""
        devices = self.recorder.get_audio_devices()
        device_names = [f"{d['name']} ({d['sample_rate']} Hz)" for d in devices]
        
        self.device_combo['values'] = device_names
        if device_names:
            self.device_combo.set(device_names[0])
        
        self.log_info(f"Encontrados {len(devices)} dispositivos de áudio")
    
    def toggle_recording(self):
        """Alterna entre gravar e parar."""
        if not self.recorder.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Inicia gravação."""
        device_index = self.device_combo.current() if self.device_combo.current() != -1 else None
        
        if self.recorder.start_recording(device_index):
            self.record_btn.config(text="⏹️ Parar")
            self.play_btn.config(state="disabled")
            self.save_btn.config(state="disabled")
            self.clone_btn.config(state="disabled")
            
            self.log_info("🔴 Gravação iniciada...")
            self.start_recording_timer()
        else:
            messagebox.showerror("Erro", "Não foi possível iniciar a gravação")
    
    def stop_recording(self):
        """Para gravação."""
        if self.recorder.stop_recording():
            self.record_btn.config(text="🔴 Gravar")
            self.play_btn.config(state="normal")
            self.save_btn.config(state="normal")
            self.clone_btn.config(state="normal")
            
            # Atualizar informações
            self.update_audio_info()
            self.update_waveform()
            
            self.log_info("⏹️ Gravação finalizada")
    
    def start_recording_timer(self):
        """Inicia timer da gravação."""
        self.recording_start_time = time.time()
        self.update_recording_timer()
    
    def update_recording_timer(self):
        """Atualiza timer da gravação."""
        if self.recorder.is_recording:
            elapsed = time.time() - self.recording_start_time
            self.level_label.config(text=f"⏱️ {elapsed:.1f}s")
            self.root.after(100, self.update_recording_timer)
    
    def play_audio(self):
        """Reproduz áudio gravado (simulado)."""
        info = self.recorder.get_audio_info()
        if info:
            self.log_info(f"▶️ Reproduzindo áudio ({info['duration']}s)")
            # Aqui você poderia implementar reprodução real
        else:
            messagebox.showwarning("Aviso", "Nenhum áudio para reproduzir")
    
    def save_audio(self):
        """Salva áudio."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            title="Salvar Áudio"
        )
        
        if filename:
            base_name = os.path.basename(filename)
            if self.recorder.save_recording(base_name):
                self.log_info(f"💾 Áudio salvo: {filename}")
                messagebox.showinfo("Sucesso", f"Áudio salvo como {filename}")
            else:
                messagebox.showerror("Erro", "Não foi possível salvar o áudio")
    
    def clone_voice(self):
        """Inicia processo de clonagem de voz."""
        if not self.recorder.current_file and not self.recorder.recorded_frames:
            messagebox.showwarning("Aviso", "Grave um áudio primeiro")
            return
        
        # Salvar temporariamente se necessário
        if not self.recorder.current_file:
            temp_file = f"temp_recording_{int(time.time())}.wav"
            if not self.recorder.save_recording(temp_file):
                messagebox.showerror("Erro", "Não foi possível preparar áudio para clonagem")
                return
        
        # Dialog para nome da voz
        voice_name = tk.simpledialog.askstring(
            "Nome da Voz", 
            "Digite um nome para sua voz clonada:",
            initialvalue="minha_voz"
        )
        
        if voice_name:
            self.log_info(f"🎯 Iniciando clonagem da voz '{voice_name}'...")
            # Aqui integramos com o sistema XTTS
            self.start_voice_cloning(voice_name)
    
    def start_voice_cloning(self, voice_name):
        """Inicia clonagem em thread separada."""
        def clone_thread():
            try:
                from speech.xtts_voice_cloning import SimpleVoiceCloner
                
                cloner = SimpleVoiceCloner()
                audio_file = str(self.recorder.current_file)
                
                self.log_info("🔄 Processando áudio para clonagem...")
                
                if cloner.clone_from_file(audio_file, voice_name):
                    self.log_info(f"✅ Voz '{voice_name}' clonada com sucesso!")
                    messagebox.showinfo("Sucesso", f"Voz '{voice_name}' criada com sucesso!")
                else:
                    self.log_info("❌ Falha na clonagem da voz")
                    messagebox.showerror("Erro", "Não foi possível clonar a voz")
                    
            except Exception as e:
                error_msg = f"Erro na clonagem: {str(e)}"
                self.log_info(f"❌ {error_msg}")
                messagebox.showerror("Erro", error_msg)
        
        threading.Thread(target=clone_thread, daemon=True).start()
    
    def start_level_monitoring(self):
        """Inicia monitoramento de nível de áudio."""
        self.is_monitoring = True
        self.update_level()
    
    def update_level(self):
        """Atualiza nível de áudio."""
        if self.is_monitoring:
            if self.recorder.is_recording and self.recorder.recorded_frames:
                # Simular nível baseado nos frames mais recentes
                try:
                    recent_frames = self.recorder.recorded_frames[-5:]
                    if recent_frames:
                        audio_data = np.frombuffer(b''.join(recent_frames), dtype=np.int16)
                        try:
                            audio_squared = audio_data.astype(np.float64)**2
                            mean_squared = np.mean(audio_squared)
                            rms = np.sqrt(mean_squared) if mean_squared >= 0 else 0.0
                        except (ValueError, RuntimeWarning):
                            rms = 0.0
                        level = min(100, (rms / 10000) * 100)
                        
                        self.level_var.set(level)
                        if not self.recorder.is_recording:  # Se não está gravando, mostrar %
                            self.level_label.config(text=f"{level:.0f}%")
                except:
                    pass
            else:
                self.level_var.set(0)
                if not self.recorder.is_recording:
                    self.level_label.config(text="0%")
            
            self.root.after(100, self.update_level)
    
    def update_audio_info(self):
        """Atualiza informações do áudio."""
        info = self.recorder.get_audio_info()
        if info:
            info_text = f"""
📊 Informações do Áudio:
├─ Duração: {info['duration']} segundos
├─ Taxa de amostragem: {info['sample_rate']} Hz
├─ Canais: {info['channels']}
├─ Nível RMS: {info['rms_level']}
└─ Amplitude máxima: {info['max_amplitude']}

✅ Status: {"Adequado para clonagem" if info['duration'] >= 5 else "Muito curto (mín. 5s)"}
"""
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
    
    def update_waveform(self):
        """Atualiza visualização da forma de onda."""
        audio_data = self.recorder.get_audio_data()
        if audio_data is not None:
            self.ax.clear()
            
            # Mostrar apenas uma amostra para performance
            sample_data = audio_data[::100]  # Cada 100ª amostra
            time_axis = np.linspace(0, len(audio_data) / self.recorder.sample_rate, len(sample_data))
            
            self.ax.plot(time_axis, sample_data)
            self.ax.set_xlabel('Tempo (s)')
            self.ax.set_ylabel('Amplitude')
            self.ax.set_title('Forma de Onda do Áudio')
            self.ax.grid(True, alpha=0.3)
            
            self.canvas.draw()
    
    def log_info(self, message):
        """Adiciona mensagem ao log."""
        timestamp = time.strftime("%H:%M:%S")
        current_text = self.info_text.get(1.0, tk.END)
        new_text = f"[{timestamp}] {message}\n{current_text}"
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, new_text)
    
    def run(self):
        """Executa a interface."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Limpeza ao fechar."""
        self.is_monitoring = False
        self.recorder.stop_recording()
        self.recorder.cleanup()
        self.root.destroy()


if __name__ == "__main__":
    # Importar tkinter.simpledialog se necessário
    try:
        import tkinter.simpledialog
    except ImportError:
        pass
    
    print("🎙️ Iniciando Gravador de Voz ASTRA...")
    app = AudioRecorderGUI()
    app.run()
