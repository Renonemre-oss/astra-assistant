#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Interface de Gestão de Perfil
Interface gráfica para configuração completa de perfil do utilizador

Este módulo fornece:
- Interface visual para configuração de preferências
- Gestão de informações pessoais
- Configuração de personalidade do assistente
- Import/Export de perfis
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime

try:
    from PyQt6 import QtWidgets, QtCore, QtGui
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QTabWidget, QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox,
        QPushButton, QCheckBox, QGroupBox, QScrollArea, QMessageBox,
        QFileDialog, QProgressBar, QSlider, QDateEdit, QColorDialog
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QFont, QPixmap, QColor, QPalette
except ImportError:
    print("PyQt6 não encontrado. Interface de perfil não disponível.")
    sys.exit(1)

from config import CONFIG, UI_STYLES, PERSONALITIES
from modules.personal_profile import PersonalProfile
from modules.people_manager import PeopleManager

logger = logging.getLogger(__name__)

class ProfileManagerUI(QMainWindow):
    """Interface principal para gestão de perfil."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.personal_profile = PersonalProfile()
        self.people_manager = PeopleManager()
        self.unsaved_changes = False
        
        self.init_ui()
        self.load_current_profile()
        
    def init_ui(self):
        """Inicializa a interface de utilizador."""
        self.setWindowTitle("ASTRA - Gestão de Perfil")
        self.setGeometry(200, 200, 900, 700)
        self.setStyleSheet(UI_STYLES["main_style"])
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # Tabs principais
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: rgba(45, 24, 16, 0.8);
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: rgba(60, 30, 20, 0.8);
                color: #f5f0e6;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 3px;
            }
            QTabBar::tab:selected {
                background-color: rgba(220, 160, 100, 0.4);
                border: 1px solid rgba(220, 160, 100, 0.6);
            }
        """)
        
        # Criar tabs
        self.create_personal_info_tab()
        self.create_preferences_tab()
        self.create_personality_tab()
        self.create_people_tab()
        self.create_advanced_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Footer com botões
        footer_layout = self.create_footer()
        main_layout.addLayout(footer_layout)
        
    def create_header(self) -> QHBoxLayout:
        """Cria o cabeçalho da interface."""
        header_layout = QHBoxLayout()
        
        # Título
        title_label = QLabel("🤖 Gestão de Perfil ASTRA")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Status
        self.status_label = QLabel("Perfil carregado")
        self.status_label.setStyleSheet("color: #27ae60; font-size: 12px;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        
        return header_layout
    
    def create_personal_info_tab(self):
        """Cria tab de informações pessoais."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Scroll area para acomodar muitos campos
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Informações básicas
        basic_group = QGroupBox("Informações Básicas")
        basic_layout = QGridLayout(basic_group)
        
        self.name_edit = QLineEdit()
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 150)
        self.location_edit = QLineEdit()
        self.occupation_edit = QLineEdit()
        self.email_edit = QLineEdit()
        
        basic_layout.addWidget(QLabel("Nome:"), 0, 0)
        basic_layout.addWidget(self.name_edit, 0, 1)
        basic_layout.addWidget(QLabel("Idade:"), 0, 2)
        basic_layout.addWidget(self.age_spin, 0, 3)
        
        basic_layout.addWidget(QLabel("Localização:"), 1, 0)
        basic_layout.addWidget(self.location_edit, 1, 1)
        basic_layout.addWidget(QLabel("Profissão:"), 1, 2)
        basic_layout.addWidget(self.occupation_edit, 1, 3)
        
        basic_layout.addWidget(QLabel("Email:"), 2, 0)
        basic_layout.addWidget(self.email_edit, 2, 1, 1, 3)
        
        scroll_layout.addWidget(basic_group)
        
        # Informações pessoais detalhadas
        details_group = QGroupBox("Detalhes Pessoais")
        details_layout = QVBoxLayout(details_group)
        
        self.bio_edit = QTextEdit()
        self.bio_edit.setMaximumHeight(100)
        self.bio_edit.setPlaceholderText("Conte um pouco sobre você...")
        
        details_layout.addWidget(QLabel("Biografia:"))
        details_layout.addWidget(self.bio_edit)
        
        scroll_layout.addWidget(details_group)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "👤 Perfil Pessoal")
    
    def create_preferences_tab(self):
        """Cria tab de preferências."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Preferências de comida
        food_group = QGroupBox("🍽️ Preferências Alimentares")
        food_layout = QGridLayout(food_group)
        
        self.favorite_food_edit = QLineEdit()
        self.favorite_drink_edit = QLineEdit()
        self.dietary_restrictions_edit = QLineEdit()
        
        food_layout.addWidget(QLabel("Comida favorita:"), 0, 0)
        food_layout.addWidget(self.favorite_food_edit, 0, 1)
        food_layout.addWidget(QLabel("Bebida favorita:"), 1, 0)
        food_layout.addWidget(self.favorite_drink_edit, 1, 1)
        food_layout.addWidget(QLabel("Restrições alimentares:"), 2, 0)
        food_layout.addWidget(self.dietary_restrictions_edit, 2, 1)
        
        scroll_layout.addWidget(food_group)
        
        # Preferências de entretenimento
        entertainment_group = QGroupBox("🎬 Entretenimento")
        entertainment_layout = QGridLayout(entertainment_group)
        
        self.favorite_music_edit = QLineEdit()
        self.favorite_artist_edit = QLineEdit()
        self.favorite_movie_edit = QLineEdit()
        self.favorite_book_edit = QLineEdit()
        self.favorite_sport_edit = QLineEdit()
        
        entertainment_layout.addWidget(QLabel("Género musical:"), 0, 0)
        entertainment_layout.addWidget(self.favorite_music_edit, 0, 1)
        entertainment_layout.addWidget(QLabel("Artista favorito:"), 0, 2)
        entertainment_layout.addWidget(self.favorite_artist_edit, 0, 3)
        
        entertainment_layout.addWidget(QLabel("Filme favorito:"), 1, 0)
        entertainment_layout.addWidget(self.favorite_movie_edit, 1, 1)
        entertainment_layout.addWidget(QLabel("Livro favorito:"), 1, 2)
        entertainment_layout.addWidget(self.favorite_book_edit, 1, 3)
        
        entertainment_layout.addWidget(QLabel("Desporto favorito:"), 2, 0)
        entertainment_layout.addWidget(self.favorite_sport_edit, 2, 1)
        
        scroll_layout.addWidget(entertainment_group)
        
        # Preferências gerais
        general_group = QGroupBox("🎨 Preferências Gerais")
        general_layout = QGridLayout(general_group)
        
        self.favorite_color_edit = QLineEdit()
        self.favorite_season_combo = QComboBox()
        self.favorite_season_combo.addItems(["", "Primavera", "Verão", "Outono", "Inverno"])
        
        self.color_button = QPushButton("Escolher Cor")
        self.color_button.clicked.connect(self.choose_color)
        
        general_layout.addWidget(QLabel("Cor favorita:"), 0, 0)
        general_layout.addWidget(self.favorite_color_edit, 0, 1)
        general_layout.addWidget(self.color_button, 0, 2)
        
        general_layout.addWidget(QLabel("Estação favorita:"), 1, 0)
        general_layout.addWidget(self.favorite_season_combo, 1, 1)
        
        scroll_layout.addWidget(general_group)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "❤️ Preferências")
    
    def create_personality_tab(self):
        """Cria tab de configuração de personalidade."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Personalidade do ASTRA
        personality_group = QGroupBox("🎭 Personalidade do ASTRA")
        personality_layout = QVBoxLayout(personality_group)
        
        self.personality_combo = QComboBox()
        for key, value in PERSONALITIES.items():
            self.personality_combo.addItem(f"{key.title()} - {value['greeting']}", key)
        
        personality_layout.addWidget(QLabel("Escolha a personalidade do assistente:"))
        personality_layout.addWidget(self.personality_combo)
        
        # Preview da personalidade
        self.personality_preview = QTextEdit()
        self.personality_preview.setReadOnly(True)
        self.personality_preview.setMaximumHeight(80)
        
        personality_layout.addWidget(QLabel("Descrição:"))
        personality_layout.addWidget(self.personality_preview)
        
        layout.addWidget(personality_group)
        
        # Configurações de resposta
        response_group = QGroupBox("💬 Configurações de Resposta")
        response_layout = QGridLayout(response_group)
        
        self.formal_responses = QCheckBox("Respostas formais")
        self.detailed_responses = QCheckBox("Respostas detalhadas")
        self.emoji_responses = QCheckBox("Usar emojis nas respostas")
        self.proactive_suggestions = QCheckBox("Sugestões proativas")
        
        response_layout.addWidget(self.formal_responses, 0, 0)
        response_layout.addWidget(self.detailed_responses, 0, 1)
        response_layout.addWidget(self.emoji_responses, 1, 0)
        response_layout.addWidget(self.proactive_suggestions, 1, 1)
        
        layout.addWidget(response_group)
        
        # Configurações de voz
        voice_group = QGroupBox("🔊 Configurações de Voz")
        voice_layout = QGridLayout(voice_group)
        
        self.tts_enabled = QCheckBox("Text-to-Speech ativo")
        self.voice_recognition = QCheckBox("Reconhecimento de voz ativo")
        
        self.tts_speed_label = QLabel("Velocidade da voz: 1.0x")
        self.tts_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.tts_speed_slider.setRange(50, 200)
        self.tts_speed_slider.setValue(100)
        self.tts_speed_slider.valueChanged.connect(
            lambda v: self.tts_speed_label.setText(f"Velocidade da voz: {v/100:.1f}x")
        )
        
        voice_layout.addWidget(self.tts_enabled, 0, 0)
        voice_layout.addWidget(self.voice_recognition, 0, 1)
        voice_layout.addWidget(self.tts_speed_label, 1, 0)
        voice_layout.addWidget(self.tts_speed_slider, 1, 1)
        
        layout.addWidget(voice_group)
        
        # Connect personality change
        self.personality_combo.currentIndexChanged.connect(self.update_personality_preview)
        self.update_personality_preview()
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🎭 Personalidade")
    
    def create_people_tab(self):
        """Cria tab de gestão de pessoas."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lista de pessoas
        people_group = QGroupBox("👥 Pessoas Conhecidas")
        people_layout = QVBoxLayout(people_group)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        add_person_btn = QPushButton("➕ Adicionar Pessoa")
        edit_person_btn = QPushButton("✏️ Editar")
        remove_person_btn = QPushButton("🗑️ Remover")
        
        add_person_btn.clicked.connect(self.add_person)
        edit_person_btn.clicked.connect(self.edit_person)
        remove_person_btn.clicked.connect(self.remove_person)
        
        toolbar_layout.addWidget(add_person_btn)
        toolbar_layout.addWidget(edit_person_btn)
        toolbar_layout.addWidget(remove_person_btn)
        toolbar_layout.addStretch()
        
        people_layout.addLayout(toolbar_layout)
        
        # Lista
        self.people_list = QtWidgets.QListWidget()
        self.people_list.setMaximumHeight(200)
        people_layout.addWidget(self.people_list)
        
        layout.addWidget(people_group)
        
        # Estatísticas
        stats_group = QGroupBox("📊 Estatísticas")
        stats_layout = QGridLayout(stats_group)
        
        self.total_people_label = QLabel("0")
        self.family_count_label = QLabel("0")
        self.friends_count_label = QLabel("0")
        
        stats_layout.addWidget(QLabel("Total de pessoas:"), 0, 0)
        stats_layout.addWidget(self.total_people_label, 0, 1)
        stats_layout.addWidget(QLabel("Família:"), 1, 0)
        stats_layout.addWidget(self.family_count_label, 1, 1)
        stats_layout.addWidget(QLabel("Amigos:"), 2, 0)
        stats_layout.addWidget(self.friends_count_label, 2, 1)
        
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "👥 Pessoas")
    
    def create_advanced_tab(self):
        """Cria tab de configurações avançadas."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Privacidade
        privacy_group = QGroupBox("🔒 Privacidade")
        privacy_layout = QVBoxLayout(privacy_group)
        
        self.data_collection = QCheckBox("Permitir coleta de dados para melhorar o assistente")
        self.voice_analysis = QCheckBox("Permitir análise de padrões de voz")
        self.conversation_logging = QCheckBox("Registar conversas para histórico")
        
        privacy_layout.addWidget(self.data_collection)
        privacy_layout.addWidget(self.voice_analysis)
        privacy_layout.addWidget(self.conversation_logging)
        
        layout.addWidget(privacy_group)
        
        # Backup e restauro
        backup_group = QGroupBox("💾 Backup e Restauro")
        backup_layout = QHBoxLayout(backup_group)
        
        export_btn = QPushButton("📤 Exportar Perfil")
        import_btn = QPushButton("📥 Importar Perfil")
        backup_btn = QPushButton("💾 Fazer Backup")
        
        export_btn.clicked.connect(self.export_profile)
        import_btn.clicked.connect(self.import_profile)
        backup_btn.clicked.connect(self.backup_profile)
        
        backup_layout.addWidget(export_btn)
        backup_layout.addWidget(import_btn)
        backup_layout.addWidget(backup_btn)
        
        layout.addWidget(backup_group)
        
        # Reset
        reset_group = QGroupBox("⚠️ Reset")
        reset_layout = QVBoxLayout(reset_group)
        
        reset_preferences_btn = QPushButton("🔄 Reset Preferências")
        reset_all_btn = QPushButton("⚠️ Reset Completo")
        
        reset_preferences_btn.clicked.connect(self.reset_preferences)
        reset_all_btn.clicked.connect(self.reset_all)
        
        reset_layout.addWidget(reset_preferences_btn)
        reset_layout.addWidget(reset_all_btn)
        
        layout.addWidget(reset_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "⚙️ Avançado")
    
    def create_footer(self) -> QHBoxLayout:
        """Cria o rodapé com botões de ação."""
        footer_layout = QHBoxLayout()
        
        # Progress bar (oculta por padrão)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Botões
        save_btn = QPushButton("💾 Guardar")
        cancel_btn = QPushButton("❌ Cancelar")
        apply_btn = QPushButton("✅ Aplicar")
        
        save_btn.clicked.connect(self.save_profile)
        cancel_btn.clicked.connect(self.cancel_changes)
        apply_btn.clicked.connect(self.apply_changes)
        
        footer_layout.addWidget(self.progress_bar)
        footer_layout.addStretch()
        footer_layout.addWidget(save_btn)
        footer_layout.addWidget(apply_btn)
        footer_layout.addWidget(cancel_btn)
        
        return footer_layout
    
    def load_current_profile(self):
        """Carrega o perfil atual na interface."""
        try:
            # Carregar dados do perfil pessoal
            facts = self.personal_profile.facts_cache
            
            # Informações básicas
            self.name_edit.setText(facts.get('nome', ''))
            if 'idade' in facts:
                try:
                    self.age_spin.setValue(int(facts['idade']))
                except ValueError:
                    pass
            
            self.location_edit.setText(facts.get('localizacao', ''))
            self.occupation_edit.setText(facts.get('profissao', ''))
            self.email_edit.setText(facts.get('email', ''))
            self.bio_edit.setPlainText(facts.get('biografia', ''))
            
            # Preferências
            self.favorite_food_edit.setText(facts.get('comida_favorita', ''))
            self.favorite_drink_edit.setText(facts.get('bebida_favorita', ''))
            self.favorite_music_edit.setText(facts.get('musica_favorita', ''))
            self.favorite_artist_edit.setText(facts.get('artista_favorito', ''))
            self.favorite_movie_edit.setText(facts.get('filme_favorito', ''))
            self.favorite_book_edit.setText(facts.get('livro_favorito', ''))
            self.favorite_sport_edit.setText(facts.get('desporto_favorito', ''))
            self.favorite_color_edit.setText(facts.get('cor_favorita', ''))
            
            season = facts.get('estacao_favorita', '')
            index = self.favorite_season_combo.findText(season)
            if index >= 0:
                self.favorite_season_combo.setCurrentIndex(index)
            
            # Configurações avançadas
            self.data_collection.setChecked(facts.get('data_collection_consent', True))
            self.voice_analysis.setChecked(facts.get('voice_analysis_consent', True))
            self.conversation_logging.setChecked(facts.get('conversation_logging', True))
            
            # Carregar lista de pessoas
            self.load_people_list()
            
            self.status_label.setText("✅ Perfil carregado com sucesso")
            self.status_label.setStyleSheet("color: #27ae60;")
            
        except Exception as e:
            logger.error(f"Erro ao carregar perfil: {e}")
            self.status_label.setText("❌ Erro ao carregar perfil")
            self.status_label.setStyleSheet("color: #e74c3c;")
    
    def load_people_list(self):
        """Carrega a lista de pessoas conhecidas."""
        try:
            # Aqui você carregaria as pessoas do people_manager
            # Por enquanto, exemplo básico
            self.people_list.clear()
            
            # Mock data para demonstração
            people_data = [
                "João Silva - Amigo",
                "Maria Santos - Família (Irmã)",
                "Pedro Costa - Colega de trabalho"
            ]
            
            for person in people_data:
                self.people_list.addItem(person)
            
            # Atualizar estatísticas
            self.total_people_label.setText(str(len(people_data)))
            self.family_count_label.setText("1")
            self.friends_count_label.setText("1")
            
        except Exception as e:
            logger.error(f"Erro ao carregar lista de pessoas: {e}")
    
    def update_personality_preview(self):
        """Atualiza a prévia da personalidade selecionada."""
        try:
            current_data = self.personality_combo.currentData()
            if current_data and current_data in PERSONALITIES:
                personality = PERSONALITIES[current_data]
                preview_text = f"Cumprimento: \"{personality['greeting']}\"\n"
                preview_text += f"Estilo: {personality['style']}"
                self.personality_preview.setText(preview_text)
        except Exception as e:
            logger.error(f"Erro ao atualizar prévia da personalidade: {e}")
    
    def choose_color(self):
        """Abre diálogo para escolher cor."""
        color = QColorDialog.getColor(Qt.GlobalColor.white, self)
        if color.isValid():
            self.favorite_color_edit.setText(color.name())
    
    def add_person(self):
        """Adiciona nova pessoa."""
        QMessageBox.information(self, "Em desenvolvimento", 
                               "Funcionalidade de adicionar pessoa será implementada em breve.")
    
    def edit_person(self):
        """Edita pessoa selecionada."""
        current_item = self.people_list.currentItem()
        if current_item:
            QMessageBox.information(self, "Em desenvolvimento", 
                                   "Funcionalidade de editar pessoa será implementada em breve.")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma pessoa para editar.")
    
    def remove_person(self):
        """Remove pessoa selecionada."""
        current_item = self.people_list.currentItem()
        if current_item:
            reply = QMessageBox.question(self, "Confirmar", 
                                       "Tem certeza que deseja remover esta pessoa?")
            if reply == QMessageBox.StandardButton.Yes:
                row = self.people_list.row(current_item)
                self.people_list.takeItem(row)
                self.unsaved_changes = True
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma pessoa para remover.")
    
    def save_profile(self):
        """Guarda o perfil."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        try:
            # Recolher dados do formulário
            profile_data = self.collect_form_data()
            
            self.progress_bar.setValue(50)
            
            # Guardar usando personal_profile
            success = self.personal_profile.save_multiple_facts(profile_data)
            
            self.progress_bar.setValue(100)
            
            if success:
                self.unsaved_changes = False
                self.status_label.setText("✅ Perfil guardado com sucesso")
                self.status_label.setStyleSheet("color: #27ae60;")
                QMessageBox.information(self, "Sucesso", "Perfil guardado com sucesso!")
            else:
                raise Exception("Falha ao guardar perfil")
                
        except Exception as e:
            logger.error(f"Erro ao guardar perfil: {e}")
            self.status_label.setText("❌ Erro ao guardar perfil")
            self.status_label.setStyleSheet("color: #e74c3c;")
            QMessageBox.critical(self, "Erro", f"Erro ao guardar perfil: {str(e)}")
        
        finally:
            self.progress_bar.setVisible(False)
    
    def collect_form_data(self) -> Dict[str, Any]:
        """Recolhe dados do formulário."""
        return {
            'nome': self.name_edit.text(),
            'idade': self.age_spin.value() if self.age_spin.value() > 0 else None,
            'localizacao': self.location_edit.text(),
            'profissao': self.occupation_edit.text(),
            'email': self.email_edit.text(),
            'biografia': self.bio_edit.toPlainText(),
            'comida_favorita': self.favorite_food_edit.text(),
            'bebida_favorita': self.favorite_drink_edit.text(),
            'restricoes_alimentares': self.dietary_restrictions_edit.text(),
            'musica_favorita': self.favorite_music_edit.text(),
            'artista_favorito': self.favorite_artist_edit.text(),
            'filme_favorito': self.favorite_movie_edit.text(),
            'livro_favorito': self.favorite_book_edit.text(),
            'desporto_favorito': self.favorite_sport_edit.text(),
            'cor_favorita': self.favorite_color_edit.text(),
            'estacao_favorita': self.favorite_season_combo.currentText(),
            'personalidade_ASTRA': self.personality_combo.currentData(),
            'data_collection_consent': self.data_collection.isChecked(),
            'voice_analysis_consent': self.voice_analysis.isChecked(),
            'conversation_logging': self.conversation_logging.isChecked()
        }
    
    def apply_changes(self):
        """Aplica mudanças sem fechar."""
        self.save_profile()
    
    def cancel_changes(self):
        """Cancela mudanças."""
        if self.unsaved_changes:
            reply = QMessageBox.question(self, "Confirmar", 
                                       "Tem certeza que deseja cancelar as alterações?")
            if reply == QMessageBox.StandardButton.Yes:
                self.load_current_profile()
                self.unsaved_changes = False
        
        self.close()
    
    def export_profile(self):
        """Exporta perfil para ficheiro."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Perfil", "ASTRA_profile.json", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                profile_data = self.collect_form_data()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(profile_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Sucesso", 
                                      f"Perfil exportado para {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar perfil: {str(e)}")
    
    def import_profile(self):
        """Importa perfil de ficheiro."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar Perfil", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                
                # Aplicar dados importados à interface
                if 'nome' in profile_data:
                    self.name_edit.setText(profile_data['nome'] or '')
                if 'idade' in profile_data and profile_data['idade']:
                    self.age_spin.setValue(profile_data['idade'])
                
                # ... (aplicar outros campos)
                
                self.unsaved_changes = True
                QMessageBox.information(self, "Sucesso", "Perfil importado com sucesso!")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao importar perfil: {str(e)}")
    
    def backup_profile(self):
        """Cria backup do perfil atual."""
        try:
            backup_dir = Path(__file__).parent.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"ASTRA_profile_backup_{timestamp}.json"
            
            profile_data = self.collect_form_data()
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Sucesso", 
                                  f"Backup criado: {backup_file}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao criar backup: {str(e)}")
    
    def reset_preferences(self):
        """Reset apenas das preferências."""
        reply = QMessageBox.question(self, "Confirmar Reset", 
                                   "Isto irá apagar todas as preferências. Continuar?")
        if reply == QMessageBox.StandardButton.Yes:
            # Limpar campos de preferências
            self.favorite_food_edit.clear()
            self.favorite_drink_edit.clear()
            self.favorite_music_edit.clear()
            self.favorite_artist_edit.clear()
            self.favorite_movie_edit.clear()
            self.favorite_book_edit.clear()
            self.favorite_sport_edit.clear()
            self.favorite_color_edit.clear()
            self.favorite_season_combo.setCurrentIndex(0)
            
            self.unsaved_changes = True
    
    def reset_all(self):
        """Reset completo do perfil."""
        reply = QMessageBox.question(self, "⚠️ Reset Completo", 
                                   "Isto irá apagar TODOS os dados do perfil!\n"
                                   "Esta ação não pode ser desfeita.\n"
                                   "Tem certeza que deseja continuar?")
        if reply == QMessageBox.StandardButton.Yes:
            # Limpar todos os campos
            self.name_edit.clear()
            self.age_spin.setValue(0)
            self.location_edit.clear()
            self.occupation_edit.clear()
            self.email_edit.clear()
            self.bio_edit.clear()
            
            self.reset_preferences()
            
            # Reset configurações para padrão
            self.data_collection.setChecked(True)
            self.voice_analysis.setChecked(True)
            self.conversation_logging.setChecked(True)
            
            self.unsaved_changes = True
            
            QMessageBox.information(self, "Reset Completo", "Perfil resetado com sucesso!")


def main():
    """Função principal para testar a interface."""
    app = QtWidgets.QApplication(sys.argv)
    
    # Aplicar estilo dark
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(45, 24, 16))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(245, 240, 230))
    app.setPalette(palette)
    
    window = ProfileManagerUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
