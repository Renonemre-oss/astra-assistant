#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Splash Screen Component
Interface de inicialização com logo do ASTRA

Este módulo fornece uma tela de apresentação moderna com o logo do ASTRA,
animações suaves e indicadores de progresso de carregamento.
"""

import sys
import time
from pathlib import Path
from typing import Optional, Callable, List

try:
    from PyQt6 import QtWidgets, QtCore, QtGui
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
    )
    from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
    from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor, QBrush, QLinearGradient
except ImportError:
    print("PyQt6 não encontrado. Splash screen não disponível.")
    sys.exit(1)

from utils.asset_manager import get_asset_manager

class SplashScreen(QWidget):
    """Tela de splash moderna com logo do ASTRA."""
    
    # Sinais para comunicação
    finished = pyqtSignal()
    progress_update = pyqtSignal(int, str)
    
    def __init__(self, parent=None, loading_steps: Optional[List[str]] = None):
        super().__init__(parent)
        
        self.loading_steps = loading_steps or [
            "Inicializando sistema ASTRA...",
            "Carregando módulos principais...",
            "Configurando interface...",
            "Carregando modelos de IA...",
            "Conectando serviços...",
            "Finalizando inicialização..."
        ]
        
        self.current_step = 0
        self.asset_manager = get_asset_manager()
        
        # Configurar janela
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(500, 350)
        
        # Centralizar na tela
        self.center_on_screen()
        
        # Inicializar UI
        self.init_ui()
        
        # Configurar animações
        self.setup_animations()
        
    def center_on_screen(self):
        """Centraliza a janela na tela."""
        screen = QtWidgets.QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        
        self.move(x, y)
    
    def init_ui(self):
        """Inicializa a interface de usuário."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Container principal com fundo
        self.main_container = QWidget()
        self.main_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(45, 24, 16, 0.95),
                    stop: 1 rgba(60, 30, 20, 0.95)
                );
                border-radius: 15px;
                border: 2px solid rgba(220, 160, 100, 0.3);
            }
        """)
        
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(25)
        
        # Logo do ASTRA
        self.logo_label = self.create_logo_widget()
        container_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Título
        self.title_label = QLabel("ASTRA")
        self.title_label.setStyleSheet("""
            QLabel {
                font-family: Arial, sans-serif;
                font-size: 32px;
                font-weight: bold;
                color: #f5f0e6;
                background: transparent;
                text-align: center;
            }
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.title_label)
        
        # Subtítulo
        self.subtitle_label = QLabel("Assistente Pessoal Inteligente")
        self.subtitle_label.setStyleSheet("""
            QLabel {
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: rgba(245, 240, 230, 0.8);
                background: transparent;
                text-align: center;
            }
        """)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.subtitle_label)
        
        # Espaçador
        container_layout.addStretch()
        
        # Status de carregamento
        self.status_label = QLabel("Inicializando...")
        self.status_label.setStyleSheet("""
            QLabel {
                font-family: Arial, sans-serif;
                font-size: 12px;
                color: rgba(245, 240, 230, 0.7);
                background: transparent;
                text-align: center;
                padding: 5px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.status_label)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(len(self.loading_steps))
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid rgba(220, 160, 100, 0.3);
                border-radius: 8px;
                text-align: center;
                background-color: rgba(60, 30, 20, 0.8);
                color: #f5f0e6;
                font-size: 11px;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(220, 160, 100, 0.8),
                    stop: 1 rgba(255, 193, 7, 0.8)
                );
                border-radius: 6px;
            }
        """)
        container_layout.addWidget(self.progress_bar)
        
        # Versão
        version_label = QLabel("v2.0 - Nova Arquitetura")
        version_label.setStyleSheet("""
            QLabel {
                font-family: Arial, sans-serif;
                font-size: 10px;
                color: rgba(245, 240, 230, 0.5);
                background: transparent;
                text-align: center;
                padding: 5px;
            }
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(version_label)
        
        layout.addWidget(self.main_container)
        self.setLayout(layout)
    
    def create_logo_widget(self) -> QLabel:
        """Cria o widget do logo."""
        logo_label = QLabel()
        logo_label.setFixedSize(128, 128)
        logo_label.setStyleSheet("background: transparent;")
        
        # Tentar carregar logo do asset manager
        try:
            logo_asset = self.asset_manager.get_asset("ASTRA_logo_main")
            if logo_asset and logo_asset.path.exists():
                pixmap = QPixmap(str(logo_asset.path))
                if not pixmap.isNull():
                    # Redimensionar mantendo proporção
                    scaled_pixmap = pixmap.scaled(
                        128, 128, 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    logo_label.setPixmap(scaled_pixmap)
                    logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    return logo_label
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
        
        # Fallback: criar logo textual
        logo_label.setText("🤖\nASTRA")
        logo_label.setStyleSheet("""
            QLabel {
                font-family: Arial, sans-serif;
                font-size: 24px;
                font-weight: bold;
                color: #f5f0e6;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(0, 123, 255, 0.3),
                    stop: 1 rgba(108, 117, 125, 0.3)
                );
                border-radius: 64px;
                border: 2px solid rgba(255, 193, 7, 0.4);
                text-align: center;
            }
        """)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return logo_label
    
    def setup_animations(self):
        """Configura as animações da tela de splash."""
        # Animação de fade in
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(800)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Timer para simular carregamento
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_progress)
    
    def show_animated(self):
        """Mostra a tela de splash com animação."""
        self.show()
        self.opacity_animation.start()
    
    def start_loading(self, duration_ms: int = 4000):
        """
        Inicia o processo de carregamento simulado.
        
        Args:
            duration_ms: Duração total do carregamento em milissegundos
        """
        if not self.loading_steps:
            return
            
        # Calcular intervalo entre steps
        step_duration = duration_ms // len(self.loading_steps)
        
        self.current_step = 0
        self.loading_timer.start(step_duration)
    
    def update_progress(self):
        """Atualiza o progresso do carregamento."""
        if self.current_step < len(self.loading_steps):
            step_text = self.loading_steps[self.current_step]
            self.status_label.setText(step_text)
            self.progress_bar.setValue(self.current_step + 1)
            
            # Emitir sinal de progresso
            self.progress_update.emit(self.current_step + 1, step_text)
            
            self.current_step += 1
        else:
            # Carregamento concluído
            self.loading_timer.stop()
            self.status_label.setText("Carregamento concluído!")
            
            # Fade out e fechar
            QTimer.singleShot(500, self.finish_splash)
    
    def finish_splash(self):
        """Finaliza a tela de splash com animação de saída."""
        fade_out = QPropertyAnimation(self, b"windowOpacity")
        fade_out.setDuration(500)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        
        def on_fade_complete():
            self.finished.emit()
            self.close()
        
        fade_out.finished.connect(on_fade_complete)
        fade_out.start()
    
    def set_step(self, step: int, message: str = ""):
        """
        Define manualmente o passo atual.
        
        Args:
            step: Número do passo (0-based)
            message: Mensagem opcional para exibir
        """
        if 0 <= step <= len(self.loading_steps):
            self.current_step = step
            self.progress_bar.setValue(step)
            
            if message:
                self.status_label.setText(message)
            elif step < len(self.loading_steps):
                self.status_label.setText(self.loading_steps[step])
    
    def paintEvent(self, event):
        """Desenha sombra suave ao redor da janela."""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Sombra
        shadow_rect = self.rect().adjusted(5, 5, -5, -5)
        shadow_gradient = QLinearGradient(0, 0, 0, shadow_rect.height())
        shadow_gradient.setColorAt(0, QColor(0, 0, 0, 100))
        shadow_gradient.setColorAt(1, QColor(0, 0, 0, 150))
        
        painter.setBrush(QBrush(shadow_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(shadow_rect, 15, 15)


class LoadingWorker(QThread):
    """Worker thread para simular tarefas de carregamento."""
    
    progress_update = pyqtSignal(int, str)
    finished = pyqtSignal()
    
    def __init__(self, tasks: List[Callable] = None):
        super().__init__()
        self.tasks = tasks or []
    
    def run(self):
        """Executa as tarefas de carregamento."""
        total_tasks = len(self.tasks)
        
        for i, task in enumerate(self.tasks):
            try:
                if callable(task):
                    result = task()
                    if isinstance(result, str):
                        self.progress_update.emit(i + 1, result)
                    else:
                        self.progress_update.emit(i + 1, f"Tarefa {i + 1} concluída")
                else:
                    self.progress_update.emit(i + 1, f"Executando: {task}")
                
                # Simular tempo de processamento
                self.msleep(200)
                
            except Exception as e:
                self.progress_update.emit(i + 1, f"Erro na tarefa {i + 1}: {str(e)}")
        
        self.finished.emit()


def show_splash_screen(parent=None, loading_tasks: List[Callable] = None, 
                      auto_duration_ms: int = 4000) -> SplashScreen:
    """
    Mostra a tela de splash do ASTRA.
    
    Args:
        parent: Widget pai (opcional)
        loading_tasks: Lista de tarefas para executar durante o carregamento
        auto_duration_ms: Duração automática se não houver tarefas específicas
        
    Returns:
        SplashScreen: Instância da tela de splash
    """
    splash = SplashScreen(parent)
    splash.show_animated()
    
    if loading_tasks:
        # Usar worker thread para tarefas reais
        worker = LoadingWorker(loading_tasks)
        worker.progress_update.connect(
            lambda step, msg: splash.set_step(step - 1, msg)
        )
        worker.finished.connect(splash.finish_splash)
        worker.start()
    else:
        # Usar simulação automática
        splash.start_loading(auto_duration_ms)
    
    return splash


# Exemplo de uso
def main():
    """Função principal para testar a tela de splash."""
    app = QtWidgets.QApplication(sys.argv)
    
    # Tarefas de exemplo
    def task1():
        time.sleep(0.5)
        return "Módulos carregados"
    
    def task2():
        time.sleep(0.3)
        return "Configuração aplicada"
    
    def task3():
        time.sleep(0.4)
        return "Sistema pronto"
    
    tasks = [task1, task2, task3]
    
    splash = show_splash_screen(loading_tasks=tasks)
    
    # Conectar sinal de término
    def on_splash_finished():
        print("Splash screen finalizada!")
        app.quit()
    
    splash.finished.connect(on_splash_finished)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
