#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 ALEX Voice System Launcher
Launcher para todas as interfaces do sistema de voz.

Interfaces disponíveis:
1. 🎙️ Audio Recorder - Gravar e processar áudio para clonagem
2. 🎭 Voice Manager - Gerenciar vozes clonadas
3. 🎤 Hybrid Speech Test - Testar sistema híbrido
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from pathlib import Path


class VoiceLauncher:
    """
    Launcher principal para o sistema de voz ALEX.
    """
    
    def __init__(self):
        """Inicializa o launcher."""
        self.setup_gui()
    
    def setup_gui(self):
        """Configura a interface gráfica."""
        self.root = tk.Tk()
        self.root.title("🎭 ALEX Voice System Launcher")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="🎭 ALEX Voice System", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Sistema Avançado de Clonagem de Voz", 
                                  font=("Arial", 10))
        subtitle_label.pack(pady=(0, 30))
        
        # Botões das interfaces
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        # Audio Recorder
        recorder_frame = ttk.LabelFrame(buttons_frame, text="🎙️ Gravação de Áudio", padding="10")
        recorder_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(recorder_frame, text="Grave sua voz para criar uma clonagem personalizada").pack(anchor=tk.W)
        ttk.Button(recorder_frame, text="🎙️ Abrir Gravador", 
                  command=self.open_recorder, width=25).pack(pady=(10, 0))
        
        # Voice Manager
        manager_frame = ttk.LabelFrame(buttons_frame, text="🎭 Gerenciador de Vozes", padding="10")
        manager_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(manager_frame, text="Gerencie, teste e organize suas vozes clonadas").pack(anchor=tk.W)
        ttk.Button(manager_frame, text="🎭 Abrir Gerenciador", 
                  command=self.open_manager, width=25).pack(pady=(10, 0))
        
        # Hybrid Speech Test
        hybrid_frame = ttk.LabelFrame(buttons_frame, text="🎤 Sistema Híbrido", padding="10")
        hybrid_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(hybrid_frame, text="Teste o sistema híbrido de síntese de voz").pack(anchor=tk.W)
        ttk.Button(hybrid_frame, text="🎤 Testar Sistema", 
                  command=self.test_hybrid, width=25).pack(pady=(10, 0))
        
        # Status e informações
        info_frame = ttk.LabelFrame(buttons_frame, text="ℹ️ Informações", padding="10")
        info_frame.pack(fill=tk.X, pady=(15, 0))
        
        info_text = """Sistema baseado em Coqui XTTS v2
• Clonagem com apenas 10-30 segundos de áudio
• Suporte a múltiplos idiomas
• Qualidade premium de síntese
• Interface amigável e intuitiva"""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Botão de saída
        ttk.Button(main_frame, text="❌ Sair", 
                  command=self.root.quit, width=15).pack(pady=(20, 0))
    
    def open_recorder(self):
        """Abre o gravador de áudio."""
        try:
            project_root = Path(__file__).parent.parent
            subprocess.Popen([sys.executable, "speech/audio_recorder.py"], 
                           cwd=str(project_root))
            messagebox.showinfo("Sucesso", "🎙️ Gravador de áudio aberto!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o gravador:\n{str(e)}")
    
    def open_manager(self):
        """Abre o gerenciador de vozes."""
        try:
            project_root = Path(__file__).parent.parent
            subprocess.Popen([sys.executable, "speech/voice_manager.py"], 
                           cwd=str(project_root))
            messagebox.showinfo("Sucesso", "🎭 Gerenciador de vozes aberto!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o gerenciador:\n{str(e)}")
    
    def test_hybrid(self):
        """Testa o sistema híbrido."""
        try:
            project_root = Path(__file__).parent.parent
            subprocess.Popen([sys.executable, "speech/hybrid_speech_engine.py"], 
                           cwd=str(project_root), 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            messagebox.showinfo("Sucesso", "🎤 Teste do sistema híbrido iniciado!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível testar o sistema:\n{str(e)}")
    
    def run(self):
        """Executa o launcher."""
        self.root.mainloop()


if __name__ == "__main__":
    print("🎭 Iniciando ALEX Voice System Launcher...")
    
    # Verificar se estamos no diretório correto
    project_root = Path(__file__).parent.parent
    if not (project_root / "speech").exists():
        print("❌ Erro: Diretório 'speech' não encontrado")
        print("   Execute este script do diretório principal do ALEX")
        input("Pressione Enter para sair...")
        sys.exit(1)
    
    # Iniciar launcher
    launcher = VoiceLauncher()
    launcher.run()