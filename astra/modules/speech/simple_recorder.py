#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎙️ ASTRA - Gravador Simples de Áudio
Interface simplificada para gravação de áudio para clonagem de voz.
"""

import os
import time
import wave
import threading
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyaudio
from pathlib import Path


class SimpleAudioRecorder:
    """Sistema simplificado de gravação."""
    
    def __init__(self):
        self.sample_rate = 22050
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        
        self.is_recording = False
        self.recorded_frames = []
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        self.output_dir = Path("speech/recorded_audio")
        self.output_dir.mkdir(exist_ok=True)
    
    def get_audio_devices(self):
        """Lista dispositivos de áudio."""
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
        """Inicia gravação."""
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
        """Para gravação."""
        if self.is_recording:
            self.is_recording = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            return True
        return False
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback de áudio."""
        if self.is_recording:
            self.recorded_frames.append(in_data)
        return (in_data, pyaudio.paContinue)
    
    def save_recording(self, filepath):
        """Salva gravação."""
        if not self.recorded_frames:
            return False
        
        try:
            with wave.open(str(filepath), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.recorded_frames))
            return True
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            return False
    
    def get_audio_info(self):
        """Retorna info do áudio."""
        if not self.recorded_frames:
            return None
        
        audio_data = np.frombuffer(b''.join(self.recorded_frames), dtype=np.int16)
        duration = len(audio_data) / self.sample_rate
        rms = np.sqrt(np.mean(audio_data.astype(np.float64)**2))
        
        return {
            'duration': round(duration, 2),
            'sample_rate': self.sample_rate,
            'rms_level': round(rms, 4)
        }
    
    def cleanup(self):
        """Limpa recursos."""
        if self.stream:
            self.stream.close()
        self.audio.terminate()


class SimpleRecorderGUI:
    """Interface simplificada."""
    
    def __init__(self):
        self.recorder = SimpleAudioRecorder()
        self.recording_start_time = 0
        self.setup_gui()
    
    def setup_gui(self):
        """Configura interface."""
        self.root = tk.Tk()
        self.root.title("🎙️ ASTRA - Gravador Simples")
        self.root.geometry("600x500")
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="🎙️ Gravador de Voz ASTRA", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Dispositivos
        device_frame = ttk.LabelFrame(main_frame, text="Dispositivo", padding="10")
        device_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(device_frame, textvariable=self.device_var, 
                                        state="readonly", width=50)
        self.device_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(device_frame, text="Atualizar", 
                  command=self.update_devices).pack(side=tk.LEFT)
        
        # Controles
        control_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.record_btn = ttk.Button(control_frame, text="🔴 Gravar", 
                                    command=self.toggle_recording, width=15)
        self.record_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_btn = ttk.Button(control_frame, text="💾 Salvar Como...", 
                                  command=self.save_audio, state="disabled", width=15)
        self.save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Timer
        self.timer_label = ttk.Label(control_frame, text="⏱️ 0.0s", font=("Arial", 12, "bold"))
        self.timer_label.pack(side=tk.RIGHT)
        
        # Informações
        info_frame = ttk.LabelFrame(main_frame, text="Informações", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=15, width=70)
        info_scroll = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scroll.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Instruções iniciais
        instructions = """
🎙️ INSTRUÇÕES PARA GRAVAÇÃO:

1. Selecione seu microfone na lista de dispositivos
2. Clique em "🔴 Gravar" para iniciar
3. Fale de forma clara por 10-30 segundos:
   
   Exemplos de texto:
   • "Olá, meu nome é [SEU NOME]. Eu sou o assistente virtual ASTRA."
   • "Como posso ajudá-lo hoje? Estou aqui para tornar sua vida mais fácil."
   • "Posso responder perguntas e executar diversas tarefas."

4. Clique em "⏹️ Parar" quando terminar
5. Use "💾 Salvar Como..." para salvar o arquivo
6. Use o arquivo salvo para criar sua voz clonada!

💡 DICAS:
• Ambiente silencioso
• Fale naturalmente 
• 10-30 segundos são suficientes
• Evite ruídos de fundo
"""
        
        self.info_text.insert(1.0, instructions)
        
        # Inicializar
        self.update_devices()
    
    def update_devices(self):
        """Atualiza dispositivos."""
        devices = self.recorder.get_audio_devices()
        device_names = [f"{d['name']} ({d['sample_rate']} Hz)" for d in devices]
        
        self.device_combo['values'] = device_names
        if device_names:
            self.device_combo.set(device_names[0])
        
        self.log_info(f"Encontrados {len(devices)} dispositivos de áudio")
    
    def toggle_recording(self):
        """Alterna gravação."""
        if not self.recorder.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Inicia gravação."""
        device_index = self.device_combo.current() if self.device_combo.current() != -1 else None
        
        if self.recorder.start_recording(device_index):
            self.record_btn.config(text="⏹️ Parar")
            self.save_btn.config(state="disabled")
            self.recording_start_time = time.time()
            self.update_timer()
            self.log_info("🔴 Gravação iniciada! Fale agora...")
        else:
            messagebox.showerror("Erro", "Não foi possível iniciar a gravação")
    
    def stop_recording(self):
        """Para gravação."""
        if self.recorder.stop_recording():
            self.record_btn.config(text="🔴 Gravar")
            self.save_btn.config(state="normal")
            
            info = self.recorder.get_audio_info()
            if info:
                self.log_info(f"⏹️ Gravação finalizada!")
                self.log_info(f"   Duração: {info['duration']} segundos")
                self.log_info(f"   Qualidade: {'Boa' if info['duration'] >= 5 else 'Muito curta'}")
                
                if info['duration'] < 5:
                    messagebox.showwarning("Atenção", "Gravação muito curta! Recomenda-se pelo menos 5 segundos.")
                elif info['duration'] > 30:
                    messagebox.showinfo("Info", "Gravação longa. Para clonagem, os primeiros 30s serão usados.")
    
    def update_timer(self):
        """Atualiza timer."""
        if self.recorder.is_recording:
            elapsed = time.time() - self.recording_start_time
            self.timer_label.config(text=f"⏱️ {elapsed:.1f}s")
            self.root.after(100, self.update_timer)
        else:
            info = self.recorder.get_audio_info()
            if info:
                self.timer_label.config(text=f"✅ {info['duration']}s")
    
    def save_audio(self):
        """Salva áudio."""
        if not self.recorder.recorded_frames:
            messagebox.showwarning("Aviso", "Nenhuma gravação para salvar")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            title="Salvar Gravação"
        )
        
        if filename:
            if self.recorder.save_recording(filename):
                self.log_info(f"💾 Áudio salvo: {filename}")
                messagebox.showinfo("Sucesso", 
                    f"Áudio salvo com sucesso!\n\n"
                    f"Arquivo: {filename}\n\n"
                    f"Para clonar a voz:\n"
                    f"1. Use o Gerenciador de Vozes\n"
                    f"2. Clique em 'Importar Áudio'\n"
                    f"3. Selecione este arquivo")
            else:
                messagebox.showerror("Erro", "Não foi possível salvar o arquivo")
    
    def log_info(self, message):
        """Log de informações."""
        timestamp = time.strftime("%H:%M:%S")
        self.info_text.insert(tk.END, f"\n[{timestamp}] {message}")
        self.info_text.see(tk.END)
    
    def run(self):
        """Executa interface."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Limpeza."""
        self.recorder.cleanup()
        self.root.destroy()


if __name__ == "__main__":
    print("🎙️ Iniciando Gravador Simples ASTRA...")
    app = SimpleRecorderGUI()
    app.run()
