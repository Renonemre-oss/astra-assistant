#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 ALEX - Gerenciador de Vozes Clonadas
Interface para criar, gerenciar e testar vozes clonadas.

Funcionalidades:
- Lista todas as vozes disponíveis
- Visualiza informações detalhadas
- Testa qualidade das vozes
- Remove vozes desnecessárias
- Integração com sistema híbrido
"""

import os
import time
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import List, Dict, Optional

# Componentes do sistema
try:
    from modules.speech.xtts_voice_cloning import SimpleVoiceCloner, XTTSVoiceCloning
    from modules.speech.hybrid_speech_engine import HybridSpeechEngine, TTSEngine
    from modules.speech.audio_recorder import AudioRecorderGUI
except ImportError as e:
    print(f"⚠️ Aviso: {e}")
    SimpleVoiceCloner = None


class VoiceManagerGUI:
    """
    Interface de gerenciamento de vozes clonadas.
    """
    
    def __init__(self):
        """Inicializa o gerenciador."""
        self.cloner = None
        self.hybrid_engine = None
        self.current_voices = []
        
        # Verificar disponibilidade
        self.check_system_availability()
        
        # Interface
        self.setup_gui()
        
        # Carregar dados iniciais
        self.refresh_voices()
        
        # Inicializar sistema híbrido
        self.init_hybrid_engine()
    
    def check_system_availability(self):
        """Verifica se os sistemas estão disponíveis."""
        try:
            if SimpleVoiceCloner:
                self.cloner = SimpleVoiceCloner()
                self.system_available = True
            else:
                self.system_available = False
        except Exception as e:
            print(f"Erro ao inicializar sistema: {e}")
            self.system_available = False
    
    def setup_gui(self):
        """Configura a interface gráfica."""
        self.root = tk.Tk()
        self.root.title("🎭 ALEX - Gerenciador de Vozes")
        self.root.geometry("900x700")
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="🎭 Gerenciador de Vozes ALEX", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Status do sistema
        status_frame = ttk.LabelFrame(main_frame, text="Status do Sistema", padding="5")
        status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        if self.system_available:
            status_text = "✅ Sistema XTTS disponível e funcional"
            status_color = "green"
        else:
            status_text = "❌ Sistema XTTS não disponível"
            status_color = "red"
        
        self.status_label = ttk.Label(status_frame, text=status_text, foreground=status_color)
        self.status_label.grid(row=0, column=0, sticky=(tk.W))
        
        # Ferramentas
        tools_frame = ttk.LabelFrame(main_frame, text="Ferramentas", padding="5")
        tools_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(tools_frame, text="🎙️ Gravar Nova Voz", 
                  command=self.open_recorder, width=20).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(tools_frame, text="📁 Importar Áudio", 
                  command=self.import_audio, width=20).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(tools_frame, text="🔄 Atualizar Lista", 
                  command=self.refresh_voices, width=20).grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(tools_frame, text="🎯 Testar Sistema", 
                  command=self.test_hybrid_system, width=20).grid(row=0, column=3)
        
        # Lista de vozes
        voices_frame = ttk.LabelFrame(main_frame, text="Vozes Disponíveis", padding="5")
        voices_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Treeview para listar vozes
        columns = ("Nome", "Criado", "Qualidade", "Duração")
        self.voices_tree = ttk.Treeview(voices_frame, columns=columns, show="headings", height=15)
        
        # Cabeçalhos
        self.voices_tree.heading("Nome", text="Nome da Voz")
        self.voices_tree.heading("Criado", text="Data de Criação") 
        self.voices_tree.heading("Qualidade", text="Qualidade")
        self.voices_tree.heading("Duração", text="Duração")
        
        # Larguras das colunas
        self.voices_tree.column("Nome", width=200)
        self.voices_tree.column("Criado", width=150)
        self.voices_tree.column("Qualidade", width=100)
        self.voices_tree.column("Duração", width=100)
        
        self.voices_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para a lista
        tree_scroll = ttk.Scrollbar(voices_frame, orient="vertical", command=self.voices_tree.yview)
        self.voices_tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Event handler para seleção
        self.voices_tree.bind("<<TreeviewSelect>>", self.on_voice_select)
        
        # Painel de detalhes
        details_frame = ttk.LabelFrame(main_frame, text="Detalhes da Voz", padding="5")
        details_frame.grid(row=3, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10), padx=(10, 0))
        
        self.details_text = tk.Text(details_frame, width=30, height=15, wrap=tk.WORD)
        details_scroll = ttk.Scrollbar(details_frame, orient="vertical", command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)
        
        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        details_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Controles da voz selecionada
        voice_controls_frame = ttk.LabelFrame(main_frame, text="Controles da Voz", padding="5")
        voice_controls_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.test_btn = ttk.Button(voice_controls_frame, text="🔊 Testar Voz", 
                                  command=self.test_selected_voice, state="disabled")
        self.test_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.quality_btn = ttk.Button(voice_controls_frame, text="📊 Análise de Qualidade", 
                                     command=self.analyze_voice_quality, state="disabled")
        self.quality_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.rename_btn = ttk.Button(voice_controls_frame, text="✏️ Renomear", 
                                    command=self.rename_voice, state="disabled")
        self.rename_btn.grid(row=0, column=2, padx=(0, 10))
        
        self.delete_btn = ttk.Button(voice_controls_frame, text="🗑️ Remover", 
                                    command=self.delete_voice, state="disabled")
        self.delete_btn.grid(row=0, column=3, padx=(0, 10))
        
        # Entry para texto de teste
        test_frame = ttk.LabelFrame(voice_controls_frame, text="Texto de Teste", padding="5")
        test_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.test_text_var = tk.StringVar()
        self.test_text_var.set("Olá, este é um teste da voz clonada do ALEX. Como você avalia a qualidade?")
        
        test_entry = ttk.Entry(test_frame, textvariable=self.test_text_var, width=80)
        test_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(test_frame, text="▶️ Falar", 
                  command=self.speak_test_text).grid(row=0, column=1)
        
        # Configurar weights para redimensionamento
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        voices_frame.columnconfigure(0, weight=1)
        voices_frame.rowconfigure(0, weight=1)
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
        test_frame.columnconfigure(0, weight=1)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def init_hybrid_engine(self):
        """Inicializa sistema híbrido."""
        try:
            def status_callback(message):
                self.status_label.config(text=f"🔄 {message}")
                self.root.update()
            
            self.hybrid_engine = HybridSpeechEngine(status_callback=status_callback)
            self.status_label.config(text="✅ Sistema híbrido inicializado")
            
        except Exception as e:
            self.status_label.config(text=f"❌ Erro no sistema híbrido: {str(e)}")
    
    def refresh_voices(self):
        """Atualiza lista de vozes."""
        if not self.system_available or not self.cloner:
            return
        
        try:
            # Limpar lista atual
            for item in self.voices_tree.get_children():
                self.voices_tree.delete(item)
            
            # Obter vozes disponíveis
            voices = self.cloner.list_voices()
            self.current_voices = voices
            
            # Adicionar à lista
            for voice_name in voices:
                info = self.cloner.xtts.get_voice_info(voice_name)
                if info:
                    # Formatar data
                    created_date = time.strftime("%d/%m/%Y", time.localtime(info.get('created_at', 0)))
                    
                    # Qualidade estimada (placeholder)
                    quality = "Boa"  # Futuramente baseada em análise real
                    
                    # Duração estimada (placeholder)
                    duration = "~15s"  # Futuramente baseada em análise do áudio
                    
                    self.voices_tree.insert("", "end", values=(voice_name, created_date, quality, duration))
            
            self.status_label.config(text=f"✅ {len(voices)} vozes carregadas")
            
        except Exception as e:
            self.status_label.config(text=f"❌ Erro ao carregar vozes: {str(e)}")
    
    def on_voice_select(self, event):
        """Handler para seleção de voz."""
        selection = self.voices_tree.selection()
        
        if selection:
            # Habilitar botões
            self.test_btn.config(state="normal")
            self.quality_btn.config(state="normal")
            self.rename_btn.config(state="normal")
            self.delete_btn.config(state="normal")
            
            # Mostrar detalhes
            item = self.voices_tree.item(selection[0])
            voice_name = item['values'][0]
            self.show_voice_details(voice_name)
        else:
            # Desabilitar botões
            self.test_btn.config(state="disabled")
            self.quality_btn.config(state="disabled") 
            self.rename_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            
            # Limpar detalhes
            self.details_text.delete(1.0, tk.END)
    
    def show_voice_details(self, voice_name: str):
        """Mostra detalhes de uma voz."""
        try:
            info = self.cloner.xtts.get_voice_info(voice_name)
            if info:
                created_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(info.get('created_at', 0)))
                
                details = f"""
🎤 Nome: {voice_name}
📅 Criado: {created_time}
🔧 Modelo: {info.get('model_used', 'N/A')}
📊 Sample Rate: {info.get('sample_rate', 'N/A')} Hz
📁 Arquivo: {info.get('reference_file', 'N/A')}

📋 Informações:
• Baseado em XTTS v2
• Qualidade premium
• Suporte multilíngue
• Síntese em tempo real

🎯 Status: Pronta para uso
"""
                
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(1.0, details)
            
        except Exception as e:
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, f"❌ Erro ao carregar detalhes: {str(e)}")
    
    def test_selected_voice(self):
        """Testa a voz selecionada."""
        selection = self.voices_tree.selection()
        if not selection:
            return
        
        item = self.voices_tree.item(selection[0])
        voice_name = item['values'][0]
        test_text = self.test_text_var.get()
        
        self.speak_with_voice(voice_name, test_text)
    
    def speak_test_text(self):
        """Fala o texto de teste com sistema híbrido."""
        if self.hybrid_engine:
            text = self.test_text_var.get()
            self.status_label.config(text="🔊 Falando...")
            
            def speak_thread():
                success = self.hybrid_engine.speak(text, blocking=True)
                self.root.after(0, lambda: self.status_label.config(
                    text="✅ Concluído" if success else "❌ Erro na síntese"
                ))
            
            threading.Thread(target=speak_thread, daemon=True).start()
    
    def speak_with_voice(self, voice_name: str, text: str):
        """Fala usando uma voz específica."""
        if not self.cloner:
            messagebox.showerror("Erro", "Sistema não disponível")
            return
        
        self.status_label.config(text=f"🎤 Sintetizando com '{voice_name}'...")
        
        def speak_thread():
            try:
                audio_file = self.cloner.speak(text, voice_name, language="pt-br")
                if audio_file:
                    os.startfile(audio_file)
                    self.root.after(0, lambda: self.status_label.config(text="✅ Áudio reproduzido"))
                else:
                    self.root.after(0, lambda: self.status_label.config(text="❌ Erro na síntese"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"❌ Erro: {str(e)}"))
        
        threading.Thread(target=speak_thread, daemon=True).start()
    
    def analyze_voice_quality(self):
        """Analisa qualidade da voz selecionada."""
        selection = self.voices_tree.selection()
        if not selection:
            return
        
        item = self.voices_tree.item(selection[0])
        voice_name = item['values'][0]
        
        self.status_label.config(text="🔍 Analisando qualidade...")
        
        def analyze_thread():
            try:
                metrics = self.cloner.xtts.test_voice_quality(voice_name)
                
                if "error" in metrics:
                    result_text = f"❌ Erro na análise: {metrics['error']}"
                else:
                    result_text = f"""
📊 Análise de Qualidade - {voice_name}

⏱️ Tempo de síntese: {metrics.get('synthesis_time', 'N/A')} segundos
🎵 Duração do áudio: {metrics.get('audio_duration', 'N/A')} segundos  
📈 Energia RMS: {metrics.get('rms_energy', 'N/A')}
🎯 Pontuação: {metrics.get('quality_score', 'N/A')}

💡 A voz está {'adequada' if metrics.get('quality_score') == 'good' else 'com qualidade baixa'}
"""
                
                self.root.after(0, lambda: [
                    messagebox.showinfo("Análise de Qualidade", result_text),
                    self.status_label.config(text="✅ Análise concluída")
                ])
                
            except Exception as e:
                self.root.after(0, lambda: [
                    messagebox.showerror("Erro", f"Erro na análise: {str(e)}"),
                    self.status_label.config(text="❌ Erro na análise")
                ])
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def rename_voice(self):
        """Renomeia uma voz."""
        messagebox.showinfo("Em desenvolvimento", "Funcionalidade de renomear será implementada em breve")
    
    def delete_voice(self):
        """Remove uma voz."""
        selection = self.voices_tree.selection()
        if not selection:
            return
        
        item = self.voices_tree.item(selection[0])
        voice_name = item['values'][0]
        
        # Confirmação
        if messagebox.askyesno("Confirmar", f"Remover a voz '{voice_name}'?\n\nEsta ação não pode ser desfeita."):
            try:
                if self.cloner.xtts.delete_voice(voice_name):
                    messagebox.showinfo("Sucesso", f"Voz '{voice_name}' removida com sucesso")
                    self.refresh_voices()
                else:
                    messagebox.showerror("Erro", "Não foi possível remover a voz")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover voz: {str(e)}")
    
    def open_recorder(self):
        """Abre a interface de gravação."""
        try:
            recorder = AudioRecorderGUI()
            recorder.run()
            # Atualizar lista após fechar gravador
            self.root.after(1000, self.refresh_voices)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o gravador: {str(e)}")
    
    def import_audio(self):
        """Importa arquivo de áudio para clonagem."""
        if not self.cloner:
            messagebox.showerror("Erro", "Sistema não disponível")
            return
        
        file_path = filedialog.askopenfilename(
            title="Selecionar Arquivo de Áudio",
            filetypes=[
                ("Arquivos de Áudio", "*.wav *.mp3 *.flac *.m4a"),
                ("WAV", "*.wav"),
                ("MP3", "*.mp3"),
                ("Todos", "*.*")
            ]
        )
        
        if file_path:
            # Pedir nome para a voz
            voice_name = tk.simpledialog.askstring(
                "Nome da Voz",
                "Digite um nome para esta voz:",
                initialvalue=os.path.splitext(os.path.basename(file_path))[0]
            )
            
            if voice_name:
                self.status_label.config(text=f"🔄 Processando '{voice_name}'...")
                
                def import_thread():
                    try:
                        success = self.cloner.clone_from_file(file_path, voice_name)
                        if success:
                            self.root.after(0, lambda: [
                                messagebox.showinfo("Sucesso", f"Voz '{voice_name}' criada com sucesso!"),
                                self.refresh_voices(),
                                self.status_label.config(text="✅ Importação concluída")
                            ])
                        else:
                            self.root.after(0, lambda: [
                                messagebox.showerror("Erro", "Não foi possível clonar a voz"),
                                self.status_label.config(text="❌ Falha na importação")
                            ])
                            
                    except Exception as e:
                        self.root.after(0, lambda: [
                            messagebox.showerror("Erro", f"Erro na clonagem: {str(e)}"),
                            self.status_label.config(text="❌ Erro na importação")
                        ])
                
                threading.Thread(target=import_thread, daemon=True).start()
    
    def test_hybrid_system(self):
        """Testa o sistema híbrido completo."""
        if not self.hybrid_engine:
            messagebox.showwarning("Aviso", "Sistema híbrido não disponível")
            return
        
        # Mostrar informações do sistema
        info = self.hybrid_engine.get_system_info()
        
        info_text = f"""
🎯 Sistema Híbrido ALEX

🔧 Engine Principal: {info.get('current_engine', 'N/A')}
🛡️ Engine Fallback: {info.get('fallback_engine', 'N/A')}
📊 Engines Disponíveis: {info.get('available_engines', 0)}/{info.get('total_engines', 0)}

⚙️ Configurações:
• Qualidade: {info.get('preferred_quality', 'N/A')}
• Gênero: {info.get('preferred_gender', 'N/A')}
• Idioma: {info.get('preferred_locale', 'N/A')}
• Auto-fallback: {info.get('auto_fallback', 'N/A')}

🚀 Engines:
"""
        
        engines = info.get('engines', {})
        for engine_name, engine_info in engines.items():
            status = "✅" if engine_info.get('available') else "❌"
            quality = engine_info.get('quality', 'N/A')
            info_text += f"  {status} {engine_name}: {quality}\n"
        
        messagebox.showinfo("Teste do Sistema", info_text)
    
    def run(self):
        """Executa a interface."""
        self.root.mainloop()


# Importar módulo necessário para dialogs
try:
    import tkinter.simpledialog
except ImportError:
    pass


if __name__ == "__main__":
    print("🎭 Iniciando Gerenciador de Vozes ALEX...")
    
    app = VoiceManagerGUI()
    app.run()