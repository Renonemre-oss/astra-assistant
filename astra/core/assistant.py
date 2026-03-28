#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal
Arquivo Principal da Interface Gráfica

Sistema modular usando PyQt6 e funcionalidades organizadas em módulos separados.
"""

import sys
import threading
import os
import traceback
import time
import logging
from pathlib import Path
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # Python < 3.9 fallback

_TIMEZONE = ZoneInfo("Europe/Lisbon")
from typing import List, Optional, Dict, Any
import configparser

# Imports dos módulos organizados
from ..config import CONFIG, DATABASE_AVAILABLE, UI_STYLES
from ..modules.audio.audio_manager import AudioManager
from ..utils.text_processor import processar_imagem, formatar_resposta
from ..modules.personal_profile import PersonalProfile
from ..modules.people_manager import PeopleManager
from ..utils.utils import (
    remover_emojis, pesquisar_internet, perguntar_ollama, 
    carregar_historico, salvar_historico, verificar_servicos, limpar_texto_tts
)

# ✅ Corrigido: Definir generate_session_id sempre, independente de DATABASE_AVAILABLE
def generate_session_id() -> str:
    """Gera um ID de sessão único."""
    return f"local_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Imports do sistema de base de dados com tratamento de erro
if DATABASE_AVAILABLE:
    try:
        from ..modules.database.database_manager import DatabaseManager, DatabaseConfig
        # Sobrescrever com versão do database se disponível
        try:
            from ..modules.database.database_manager import generate_session_id
        except ImportError:
            pass  # Usar a função definida acima
    except ImportError as e:
        logging.warning(f"⚠️ Sistema de base de dados não disponível: {e}")
        DATABASE_AVAILABLE = False
        DatabaseManager = None
        DatabaseConfig = None
else:
    DatabaseManager = None
    DatabaseConfig = None

# Imports opcionais
try:
    import joblib
except ImportError:
    logging.error("Joblib não instalado. Use: pip install joblib")
    joblib = None

try:
    import speech_recognition as sr
except ImportError:
    logging.error("SpeechRecognition não instalado. Use: pip install speechrecognition")
    sr = None

# Sistema de hotword detection
try:
    from ..modules.speech.hotword_detector import create_hotword_detector
except ImportError:
    logging.warning("Sistema de hotword não disponível")
    create_hotword_detector = None

# Sistema de visualização integrado
try:
    from ..modules.visual_hotword_detector import create_visual_hotword_system
    VISUAL_SYSTEM_AVAILABLE = True
except ImportError:
    logging.warning("Sistema de visualização não disponível")
    create_visual_hotword_system = None
    VISUAL_SYSTEM_AVAILABLE = False

# ✅ Bug #18: Importar feature flags de constants.py como fonte única
try:
    from ..config.constants import (
        ENABLE_BASIC_PERSONALITY,
        ENABLE_COMPANION_ENGINE,
        ENABLE_BASIC_MEMORY,
        ENABLE_OPINION_SYSTEM,
        ENABLE_BEHAVIORAL_ANALYZER,
        ENABLE_NEEDS_PREDICTOR,
        ENABLE_ETHICAL_ANALYZER,
        ENABLE_VOICE_LOOP,
        ENABLE_SKILLS,
        ENABLE_UI,
        ENABLE_OLLAMA
    )
    logging.info("✅ Feature flags carregadas de constants.py")
except ImportError as e:
    # Fallback se constants.py não estiver disponível
    logging.warning(f"⚠️ Feature flags não encontradas em constants.py: {e}")
    ENABLE_BASIC_PERSONALITY = True
    ENABLE_COMPANION_ENGINE = False
    ENABLE_BASIC_MEMORY = True
    ENABLE_OPINION_SYSTEM = False
    ENABLE_BEHAVIORAL_ANALYZER = False
    ENABLE_NEEDS_PREDICTOR = False
    ENABLE_ETHICAL_ANALYZER = False
    ENABLE_VOICE_LOOP = True
    ENABLE_SKILLS = True
    ENABLE_UI = True
    ENABLE_OLLAMA = True

# Sistema de estados afetivos (CORE - sempre ativo)
try:
    from ..modules.affective_state_engine import AffectiveStateEngine, EventType
    AFFECTIVE_ENGINE_AVAILABLE = True
    logging.info("💫 Affective State Engine disponível")
except ImportError:
    logging.warning("⚠️ Affective State Engine não disponível")
    AffectiveStateEngine = None
    EventType = None
    AFFECTIVE_ENGINE_AVAILABLE = False

# Sistema de decisão interna (CORE - sempre ativo)
try:
    from ..modules.decision_engine import DecisionEngine, DecisionType
    DECISION_ENGINE_AVAILABLE = True
    logging.info("🧠 Decision Engine disponível")
except ImportError:
    logging.warning("⚠️ Decision Engine não disponível")
    DecisionEngine = None
    DecisionType = None
    DECISION_ENGINE_AVAILABLE = False

# Sistema de expressão (CORE - sempre ativo)
try:
    from ..modules.expression_modulator import ExpressionModulator, ExpressionStyle
    EXPRESSION_MODULATOR_AVAILABLE = True
    logging.info("🎭 Expression Modulator disponível")
except ImportError:
    logging.warning("⚠️ Expression Modulator não disponível")
    ExpressionModulator = None
    ExpressionStyle = None
    EXPRESSION_MODULATOR_AVAILABLE = False

# Sistema de luto e closure (CORE - sempre ativo)
try:
    from ..modules.grief_closure_engine import GriefClosureEngine, SeparationType
    GRIEF_CLOSURE_AVAILABLE = True
    logging.info("🍂 Grief & Closure Engine disponível")
except ImportError:
    logging.warning("⚠️ Grief & Closure Engine não disponível")
    GriefClosureEngine = None
    SeparationType = None
    GRIEF_CLOSURE_AVAILABLE = False

# Sistema de personalidade dinâmica (BÁSICO)
if ENABLE_BASIC_PERSONALITY:
    try:
        from ..modules.personality_engine import PersonalityEngine
    except ImportError:
        logging.warning("⚠️ Sistema de personalidade não disponível")
        PersonalityEngine = None
else:
    PersonalityEngine = None
    logging.info("🚫 Personalidade básica desabilitada (ENABLE_BASIC_PERSONALITY=False)")

# Sistema de companhia inteligente (EXPERIMENTAL - DESABILITADO)
if ENABLE_COMPANION_ENGINE:
    try:
        from ..modules.experimental.companion_engine import CompanionEngine
        logging.info("⚠️ Companion Engine EXPERIMENTAL habilitado")
    except ImportError:
        logging.warning("⚠️ Companion Engine não disponível")
        CompanionEngine = None
else:
    CompanionEngine = None
    logging.info("✅ Companion Engine desabilitado (modo simplificado)")

# Sistema de memória inteligente (BÁSICO)
if ENABLE_BASIC_MEMORY:
    try:
        from ..modules.memory_system import MemorySystem
    except ImportError:
        logging.warning("⚠️ Sistema de memória não disponível")
        MemorySystem = None
else:
    MemorySystem = None
    logging.info("🚫 Memória básica desabilitada (ENABLE_BASIC_MEMORY=False)")

# Sistema de opinião e análise ética (EXPERIMENTAL - DESABILITADO)
if ENABLE_OPINION_SYSTEM:
    try:
        from ..modules.experimental.opinion_system import opinion_system
        OPINION_SYSTEM_AVAILABLE = True
        logging.info("⚠️ Opinion System EXPERIMENTAL habilitado")
    except ImportError:
        logging.warning("⚠️ Sistema de opinião não disponível")
        opinion_system = None
        OPINION_SYSTEM_AVAILABLE = False
else:
    opinion_system = None
    OPINION_SYSTEM_AVAILABLE = False
    logging.info("✅ Opinion System desabilitado (modo simplificado)")

# Sistema de Hub de APIs - Notícias, Clima, etc.
try:
    from ..api.api_integration_hub import ApiIntegrationHub, NewsAPI, WeatherAPI, CryptoAPI
    API_HUB_AVAILABLE = True
except ImportError:
    logging.warning("Hub de APIs não disponível")
    ApiIntegrationHub = None
    NewsAPI = None
    WeatherAPI = None
    CryptoAPI = None
    API_HUB_AVAILABLE = False

try:
    from PyQt6 import QtWidgets, QtCore, QtGui
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except ImportError:
    logging.critical("PyQt6 não instalado. Use: pip install PyQt6 PyQt6-WebEngine")
    sys.exit(1)

# ==========================
# HTML BACKGROUND (mantido aqui por ser específico da UI)
# ==========================
HTML_BACKGROUND = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASTRA - Perlin Noise Clouds</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            overflow: hidden;
            width: 100%;
            height: 100%;
            background: radial-gradient(ellipse at center, #3d2820 0%, #2d1810 100%);
            position: relative;
        }
        
        .perlin-canvas {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }
        
        /* ONDAS VOLUMOSAS - HIGHLIGHTS */
        .cloud-layer {
            position: absolute;
            width: 200%;
            height: 200%;
            top: -50%;
            left: -50%;
            background: 
                /* Ondas principais com maior contraste */
                radial-gradient(ellipse 400px 180px at 30% 25%, rgba(255, 220, 160, 0.95) 0%, rgba(240, 200, 140, 0.8) 20%, rgba(220, 180, 120, 0.6) 40%, rgba(180, 140, 80, 0.3) 70%, transparent 90%),
                radial-gradient(ellipse 350px 150px at 70% 40%, rgba(250, 210, 150, 0.9) 0%, rgba(230, 190, 130, 0.75) 25%, rgba(210, 170, 110, 0.5) 50%, rgba(170, 130, 70, 0.25) 75%, transparent 95%),
                radial-gradient(ellipse 320px 140px at 20% 70%, rgba(245, 205, 145, 0.85) 0%, rgba(225, 185, 125, 0.7) 30%, rgba(205, 165, 105, 0.45) 60%, rgba(160, 120, 60, 0.2) 85%, transparent 100%);
            filter: blur(15px);
            animation: cloudFlow1 30s ease-in-out infinite;
        }
        
        /* CAMADA DE SOMBRAS ONDULADAS */
        .cloud-layer:nth-child(2) {
            background: 
                /* Sombras principais definidas */
                radial-gradient(ellipse 300px 200px at 25% 35%, rgba(120, 70, 40, 0.9) 0%, rgba(100, 60, 35, 0.7) 25%, rgba(80, 50, 30, 0.5) 50%, rgba(60, 40, 25, 0.3) 75%, transparent 100%),
                radial-gradient(ellipse 280px 180px at 65% 25%, rgba(110, 65, 35, 0.85) 0%, rgba(90, 55, 30, 0.65) 30%, rgba(70, 45, 25, 0.45) 60%, rgba(50, 35, 20, 0.25) 85%, transparent 100%);
            filter: blur(18px);
            animation: shadowFlow1 35s ease-in-out infinite reverse;
        }
        
        @keyframes cloudFlow1 {
            0%, 100% { transform: translate(0%, 0%) scale(1) rotate(0deg) skewX(0deg); }
            25% { transform: translate(4%, -1%) scale(1.03) rotate(1deg) skewX(2deg); }
            50% { transform: translate(-3%, 2%) scale(0.97) rotate(-2deg) skewX(-1deg); }
            75% { transform: translate(2%, -3%) scale(1.01) rotate(3deg) skewX(1deg); }
        }
        
        @keyframes shadowFlow1 {
            0%, 100% { transform: translate(0%, 0%) scale(1) rotate(0deg) skewY(0deg); }
            33% { transform: translate(-3%, 4%) scale(1.02) rotate(-1deg) skewY(-2deg); }
            66% { transform: translate(3%, -2%) scale(0.98) rotate(2deg) skewY(1deg); }
        }
        
        .blur-layer {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 10;
            backdrop-filter: blur(3px);
            background-color: rgba(45, 24, 16, 0.1);
        }
    </style>
</head>
<body>
    <div class="cloud-layer"></div>
    <div class="cloud-layer"></div>
    <div class="blur-layer"></div>
</body>
</html>
"""

# ==========================
# CLASSE: ATUALIZADOR DA UI
# ==========================
class UiUpdater(QtCore.QObject):
    append_input_signal = QtCore.pyqtSignal(str)
    append_output_signal = QtCore.pyqtSignal(str)
    enable_buttons_signal = QtCore.pyqtSignal(bool)
    set_status_signal = QtCore.pyqtSignal(str)

# ==========================
# CLASSE: GUI DO ASSISTENTE
# ==========================
class AssistenteGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.stop_signal = threading.Event()
        self.microfone_ativo = False
        self.history = []
        self.personalidade = "neutra"
        self._threads = []  # Lista para gerir threads ativas
        self._shutdown = False  # Flag para shutdown controlado
        
        # Inicializar variáveis básicas primeiro
        self.personal_profile = PersonalProfile()
        self.people_manager = PeopleManager()
        
        # Sistema de hotword detection
        self.hotword_detector = None
        self.hotword_mode = False
        
        # Sistema de personalidade dinâmica
        self.personality_engine = None
        if PersonalityEngine:
            try:
                self.personality_engine = PersonalityEngine()
                logging.info("🎭 Sistema de personalidade ativado")
            except Exception as e:
                logging.error(f"Erro ao inicializar personalidade: {e}")
        
        # Sistema de companhia inteligente
        self.companion_engine = None
        if CompanionEngine:
            try:
                self.companion_engine = CompanionEngine()
                logging.info("🤖 Sistema de companhia inteligente ativado")
            except Exception as e:
                logging.error(f"Erro ao inicializar companhia inteligente: {e}")
        
        # Sistema de memória inteligente
        self.memory_system = None
        if MemorySystem:
            try:
                self.memory_system = MemorySystem()
                logging.info("🧠 Sistema de memória ativado")
            except Exception as e:
                logging.error(f"Erro ao inicializar memória: {e}")
        
        # Sistema de estados afetivos (CORE)
        self.affective_engine = None
        if AFFECTIVE_ENGINE_AVAILABLE:
            try:
                self.affective_engine = AffectiveStateEngine(user_id="default")
                logging.info("💫 Affective State Engine ativado")
                logging.info(f"Estados iniciais:\n{self.affective_engine.get_state_summary()}")
            except Exception as e:
                logging.error(f"Erro ao inicializar Affective Engine: {e}")
        
        # Sistema de decisão interna (CORE)
        self.decision_engine = None
        if DECISION_ENGINE_AVAILABLE and self.affective_engine:
            try:
                self.decision_engine = DecisionEngine(affective_engine=self.affective_engine)
                logging.info("🧠 Decision Engine ativado (conectado ao Affective Engine)")
            except Exception as e:
                logging.error(f"Erro ao inicializar Decision Engine: {e}")
        
        # Sistema de expressão (CORE)
        self.expression_modulator = None
        if EXPRESSION_MODULATOR_AVAILABLE and self.affective_engine:
            try:
                self.expression_modulator = ExpressionModulator(affective_engine=self.affective_engine)
                logging.info("🎭 Expression Modulator ativado (conectado ao Affective Engine)")
            except Exception as e:
                logging.error(f"Erro ao inicializar Expression Modulator: {e}")
        
        # Sistema de luto e closure (CORE)
        self.grief_closure_engine = None
        if GRIEF_CLOSURE_AVAILABLE:
            try:
                self.grief_closure_engine = GriefClosureEngine(user_id="default")
                logging.info("🍂 Grief & Closure Engine ativado")
            except Exception as e:
                logging.error(f"Erro ao inicializar Grief & Closure Engine: {e}")
        
        # Sistema de Hub de APIs (Notícias, Clima, etc.)
        self.api_hub = None
        self.news_api = None
        self.weather_api = None
        self.crypto_api = None
        if API_HUB_AVAILABLE:
            try:
                self.api_hub = ApiIntegrationHub()
                self.news_api = NewsAPI(self.api_hub)
                self.weather_api = WeatherAPI(self.api_hub)
                self.crypto_api = CryptoAPI(self.api_hub)
                logging.info("🌍 Hub de APIs ativado (Notícias, Clima, Crypto)")
            except Exception as e:
                logging.error(f"Erro ao inicializar Hub de APIs: {e}")
                self.api_hub = None
                self.news_api = None
                self.weather_api = None
                self.crypto_api = None
        
        # Configuração da base de dados
        self.db_manager = None
        self.db_config = None
        self.conversation_id = None
        self.session_id = generate_session_id()
        
        # Configurar janela
        self.setWindowTitle("ASTRA - Assistente Pessoal")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(UI_STYLES["main_style"])

        # Configurar UI updater
        self.ui_updater = UiUpdater()
        self.ui_updater.append_input_signal.connect(self.append_entrada)
        self.ui_updater.append_output_signal.connect(self.append_saida)
        self.ui_updater.enable_buttons_signal.connect(self.set_buttons_enabled)
        self.ui_updater.set_status_signal.connect(self.set_status_message)
        
        # Auto-iniciar hotword detection
        self.auto_start_hotword = True

        # Criar UI primeiro
        self.init_ui()
        self.set_buttons_enabled(True)
        
        # ✅ Bug #9: Inicializar AudioManager com tratamento de erro robusto
        try:
            self.audio_manager = AudioManager(status_callback=self.set_status_message)
            logging.info("✅ AudioManager inicializado com sucesso")
        except ImportError as e:
            logging.error(f"❌ Erro ao importar AudioManager: {e}")
            logging.warning("⚠️  Sistema de áudio desabilitado - verifique dependências TTS")
            self.audio_manager = None
        except Exception as e:
            logging.error(f"❌ Erro ao inicializar AudioManager: {e}")
            self.audio_manager = None
        
        # Inicializar componentes em threads separadas
        self.init_background_tasks()
        
        # Carregar o modelo de intenções
        self.modelo_intencoes, self.vectorizer_intencoes = self.carregar_modelo_intencoes()

    # ==========================
    # INICIALIZAÇÃO
    # ==========================
    def init_background_tasks(self):
        """Inicializa tarefas em segundo plano."""
        # ✅ Bug #9: Carregar modelo TTS apenas se AudioManager disponível
        if self.audio_manager:
            threading.Thread(target=self.audio_manager.load_tts_model, daemon=True).start()
        else:
            logging.warning("⚠️  AudioManager não disponível - TTS desabilitado")
        
        # Inicializar armazenamento local
        threading.Thread(target=self.init_local_storage, daemon=True).start()
        
        # Inicializar base de dados se disponível
        if DATABASE_AVAILABLE:
            threading.Thread(target=self.init_database, daemon=True).start()

    def init_local_storage(self):
        """Inicializa e carrega o histórico de arquivos locais."""
        self.history = carregar_historico()
        self.ui_updater.set_status_signal.emit("✅ Armazenamento local inicializado.")

    def init_database(self):
        """Inicializa a conexão com a base de dados SQLite."""
        if not DATABASE_AVAILABLE:
            logging.info("ℹ️ Base de dados não disponível - modo local")
            return
            
        try:
            # Tentar carregar configuração do ficheiro
            config_file = Path(__file__).parent.parent / "config" / "database.ini"
            
            if config_file.exists():
                config_parser = configparser.ConfigParser()
                config_parser.read(config_file)
                
                if 'sqlite' in config_parser:
                    sqlite_config = config_parser['sqlite']
                    self.db_config = DatabaseConfig(
                        database_path=sqlite_config.get('database_path', 'ASTRA_assistant.db')
                    )
                    logging.info("Configuração SQLite carregada do ficheiro")
                else:
                    raise Exception("Seção [sqlite] não encontrada no ficheiro de configuração")
            else:
                # Configuração padrão
                logging.info("Ficheiro database.ini não encontrado, usando configuração padrão")
                self.db_config = DatabaseConfig()
            
            # Tentar conectar
            self.db_manager = DatabaseManager(self.db_config)
            
            if self.db_manager.connect():
                logging.info("✅ Base de dados SQLite conectada com sucesso")
                
                # Inicializar módulos com database manager
                if hasattr(self, 'personal_profile') and self.personal_profile:
                    self.personal_profile.db_manager = self.db_manager
                if hasattr(self, 'people_manager') and self.people_manager:
                    self.people_manager.db_manager = self.db_manager
                
                # Criar ou obter conversa atual
                self._init_current_conversation()
                
                self.ui_updater.set_status_signal.emit("✅ Base de dados conectada")
            else:
                raise Exception("Falha na conexão")
                
        except Exception as e:
            logging.warning(f"⚠️ Base de dados não disponível: {e}")
            self.ui_updater.set_status_signal.emit("⚠️ BD indisponível - modo local")
            self.db_manager = None

    def _init_current_conversation(self):
        """Inicializa a conversa atual na base de dados."""
        if not self.db_manager:
            return
            
        try:
            # Verificar se já existe uma conversa com este session_id
            conversation = self.db_manager.get_conversation_by_session(self.session_id)
            
            if conversation:
                self.conversation_id = conversation['id']
                logging.info(f"📄 Conversa existente carregada: ID={self.conversation_id}")
                
                # Carregar histórico da conversa
                self._load_conversation_history()
            else:
                # Criar nova conversa
                self.conversation_id = self.db_manager.create_conversation(
                    session_id=self.session_id,
                    title=f"Conversa {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                    personality=self.personalidade
                )
                
                logging.info(f"📄 Nova conversa criada: ID={self.conversation_id}")
                
        except Exception as e:
            logging.error(f"❌ Erro ao inicializar conversa: {e}")
            self.conversation_id = None

    def _load_conversation_history(self, limit: Optional[int] = None, offset: int = 0):
        """
        Carrega o histórico da conversa da base de dados com paginação.
        
        Args:
            limit: Número máximo de mensagens (None = usar CONFIG)
            offset: Offset para paginação (0 = mais recentes)
        """
        if not self.db_manager or not self.conversation_id:
            return
        
        # Usar limite configurado ou padrão
        max_messages = limit if limit is not None else CONFIG.get("conversation_history_size", 50)
        
        # Limitar a um máximo razoável para evitar sobrecarga
        max_messages = min(max_messages, 100)
        
        try:
            messages = self.db_manager.get_conversation_history(
                self.conversation_id, 
                limit=max_messages,
                offset=offset
            )
            
            # Converter para formato do histórico local
            if offset == 0:
                self.history = []
            
            for msg in messages:
                if msg['message_type'] == 'user':
                    self.history.append({'role': 'user', 'content': msg['content']})
                elif msg['message_type'] == 'assistant':
                    self.history.append({'role': 'assistant', 'content': msg['content']})
            
            logging.info(f"📃 Histórico carregado: {len(messages)} mensagens (limite: {max_messages})")
            
        except Exception as e:
            logging.error(f"❌ Erro ao carregar histórico: {e}")

    def create_logo_widget(self) -> QtWidgets.QLabel:
        """Cria o widget do logo para o cabeçalho."""
        logo_label = QtWidgets.QLabel()
        logo_label.setFixedSize(48, 48)
        logo_label.setStyleSheet("background: transparent;")
        
        # Tentar carregar logo do asset manager
        try:
            from utils.asset_manager import get_asset_manager
            asset_manager = get_asset_manager()
            logo_asset = asset_manager.get_asset("ASTRA_logo_main")
            
            if logo_asset and logo_asset.path.exists():
                pixmap = QtGui.QPixmap(str(logo_asset.path))
                if not pixmap.isNull():
                    # Redimensionar mantendo proporção
                    scaled_pixmap = pixmap.scaled(
                        48, 48, 
                        QtCore.Qt.AspectRatioMode.KeepAspectRatio, 
                        QtCore.Qt.TransformationMode.SmoothTransformation
                    )
                    logo_label.setPixmap(scaled_pixmap)
                    logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    return logo_label
        except Exception as e:
            logging.warning(f"Erro ao carregar logo: {e}")
        
        # Fallback: criar logo textual
        logo_label.setText("🤖")
        logo_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                color: #f5f0e6;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(0, 123, 255, 0.3),
                    stop: 1 rgba(108, 117, 125, 0.3)
                );
                border-radius: 24px;
                border: 2px solid rgba(255, 193, 7, 0.4);
            }
        """)
        logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        return logo_label

    # ==========================
    # MÉTODOS DE UI
    # ==========================
    def set_buttons_enabled(self, enabled):
        """Ativa/desativa os botões de controle."""
        self.btn_enviar.setEnabled(enabled)
        self.btn_microfone.setEnabled(enabled)
        self.caixa_input.setEnabled(enabled)
        self.btn_parar.setEnabled(not enabled)
        self.btn_processar_imagem.setEnabled(enabled)

    def set_status_message(self, message):
        """Define a mensagem de status na UI."""
        # Check if status_label exists (UI might not be initialized yet)
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.setText(message)
        else:
            # If UI not ready, just log the message
            logging.info(f"Status (UI não pronta): {message}")

    def init_ui(self):
        """Inicializa a interface de utilizador."""
        self.web_view = QWebEngineView()
        self.web_view.setHtml(HTML_BACKGROUND)

        ui_layout = QtWidgets.QVBoxLayout()
        ui_layout.setSpacing(15)

        # Criar container para o cabeçalho com logo
        header_container = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_container)
        
        # Logo do ASTRA
        self.logo_label = self.create_logo_widget()
        header_layout.addWidget(self.logo_label)
        
        # Título
        self.title_label = QtWidgets.QLabel("ASTRA - Assistente Virtual")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()  # Empurrar para a esquerda
        
        self.entrada_texto = QtWidgets.QTextEdit()
        self.entrada_texto.setReadOnly(True)
        self.entrada_texto.setFixedHeight(100)
        
        self.saida_texto = QtWidgets.QTextEdit()
        self.saida_texto.setReadOnly(True)
        self.saida_texto.setFixedHeight(200)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setObjectName("statusLabel")
        
        h_layout = QtWidgets.QHBoxLayout()
        self.caixa_input = QtWidgets.QLineEdit()
        self.caixa_input.setPlaceholderText("💬 Escreva sua mensagem aqui")
        self.caixa_input.returnPressed.connect(self.enviar_mensagem)

        self.btn_enviar = QtWidgets.QPushButton("📤")
        self.btn_enviar.clicked.connect(self.enviar_mensagem)

        self.btn_microfone = QtWidgets.QPushButton("🎙️")
        self.btn_microfone.clicked.connect(self.toggle_microfone)

        self.btn_processar_imagem = QtWidgets.QPushButton("🖼️ Processar Imagem")
        self.btn_processar_imagem.clicked.connect(self.selecionar_e_processar_imagem)

        self.btn_parar = QtWidgets.QPushButton("🚫")
        self.btn_parar.setObjectName("stopButton")
        self.btn_parar.clicked.connect(self.parar_processamento)
        self.btn_parar.setEnabled(False)

        h_layout.addWidget(self.caixa_input)
        h_layout.addWidget(self.btn_enviar)
        h_layout.addWidget(self.btn_microfone)
        h_layout.addWidget(self.btn_processar_imagem)
        h_layout.addWidget(self.btn_parar)

        ui_layout.addWidget(header_container)
        ui_layout.addWidget(self.entrada_texto)
        ui_layout.addWidget(self.saida_texto)
        ui_layout.addWidget(self.status_label)
        ui_layout.addLayout(h_layout)
        ui_layout.addStretch(1)

        main_layout = QtWidgets.QGridLayout(self)
        main_layout.addWidget(self.web_view, 0, 0, 1, 1)
        main_layout.addLayout(ui_layout, 0, 0, 1, 1)

    @QtCore.pyqtSlot(str)
    def append_entrada(self, texto):
        self.entrada_texto.append(texto)

    @QtCore.pyqtSlot(str)
    def append_saida(self, texto):
        self.saida_texto.append(texto)

    # ==========================
    # MÉTODOS DE PROCESSAMENTO
    # ==========================
    def enviar_mensagem(self):
        """Processa a mensagem do utilizador."""
        comando = self.caixa_input.text().strip()
        self.caixa_input.clear()
        if comando:
            self.stop_signal.clear()
            self.ui_updater.enable_buttons_signal.emit(False)
            self.ui_updater.append_input_signal.emit(f"💬 Você: {comando}")
            self.ui_updater.set_status_signal.emit("Processando...")
            threading.Thread(target=self.executar_assistente_texto, args=(comando, self.stop_signal), daemon=True).start()

    def executar_assistente_texto(self, comando, stop_signal):
        """
        Processa comando do utilizador e gera resposta.
        
        Args:
            comando: Comando do utilizador
            stop_signal: Signal para interromper processamento
        """
        try:
            comando_lower = remover_emojis(comando).lower().strip()
            response_start_time = time.time()
            
            # GRIEF & CLOSURE: Atualizar última interação
            if self.grief_closure_engine:
                self.grief_closure_engine.update_last_interaction()
            
            # GRIEF & CLOSURE: Verificar ausência prolongada no início
            if self.grief_closure_engine and self.affective_engine:
                absence_type = self.grief_closure_engine.check_absence_status(self.affective_engine.states)
                if absence_type:
                    # Utilizador retornou após ausência
                    logging.info(f"🍂 Ausência detectada: {absence_type.value}")
                    closure_response = self.grief_closure_engine.generate_closure_response(
                        absence_type,
                        self.affective_engine.states
                    )
                    
                    # Aplicar ajustes afetivos
                    if closure_response.affective_adjustments:
                        for state, adjustment in closure_response.affective_adjustments.items():
                            self.affective_engine.adjust_state(state, adjustment)
                        logging.info(f"🔄 Estados ajustados por ausência")
                    
                    # Marcar retorno
                    self.grief_closure_engine.mark_user_returned()
            
            # Detectar eventos afetivos antes de processar
            self._detect_affective_events(comando)
            
            # GRIEF & CLOSURE: Detectar despedida/separação
            if self.grief_closure_engine and self.affective_engine:
                separation_type = self.grief_closure_engine.detect_separation_type(
                    comando,
                    self.affective_engine.states
                )
                
                if separation_type:
                    # É uma despedida - processar com Grief & Closure Engine
                    logging.info(f"🍂 Separação detectada: {separation_type.value}")
                    closure_response = self.grief_closure_engine.generate_closure_response(
                        separation_type,
                        self.affective_engine.states
                    )
                    
                    # Aplicar ajustes afetivos
                    if closure_response.affective_adjustments:
                        for state, adjustment in closure_response.affective_adjustments.items():
                            self.affective_engine.adjust_state(state, adjustment)
                        logging.info(f"💔 Estados ajustados por separação: {closure_response.affective_adjustments}")
                    
                    # Usar mensagem de closure
                    resposta = closure_response.message
                    
                    # Se for despedida permanente ou de conflito, responder e retornar
                    if separation_type in [SeparationType.PERMANENT_GOODBYE, SeparationType.CONFLICT_DEPARTURE]:
                        self.ui_updater.append_output_signal.emit(f"🤖 ASTRA: {resposta}")
                        self.audio_manager.text_to_speech(resposta)
                        self.ui_updater.enable_buttons_signal.emit(True)
                        return
            
            # DECISION ENGINE: Processo de decisão interna
            decision_result = None
            explicit_response = None
            if self.decision_engine:
                try:
                    # Construir contexto para Decision Engine
                    decision_context = {
                        'has_helped_recently': len(self.history) > 2,  # Simplificado
                        'helped_recently_count': min(len(self.history) // 2, 5)
                    }
                    
                    # Processar fluxo completo: Event → Meaning → Conflict → Decision → Expression
                    decision_result, explicit_response = self.decision_engine.process_full_decision_flow(
                        comando,
                        context=decision_context
                    )
                    
                    # Se Decision Engine gerou resposta explícita, usar e retornar
                    if explicit_response:
                        logging.info(f"🧠 Decision Engine: usando resposta explícita ({decision_result.decision_type.value})")
                        self.ui_updater.append_output_signal.emit(f"🤖 ASTRA: {explicit_response}")
                        self.audio_manager.text_to_speech(explicit_response)
                        self.ui_updater.enable_buttons_signal.emit(True)
                        return
                    
                except Exception as e:
                    logging.error(f"Erro no Decision Engine: {e}")
            
            # Salvar mensagem na base de dados e histórico
            self.save_user_message(comando)
            self.history.append({"role": "user", "content": comando})
            
            # Processar com sistema de opinião ética
            opinion_result = self._process_opinion_system(comando, response_start_time)
            if opinion_result and opinion_result.get('should_return'):
                return
            
            resposta = opinion_result.get('response', '') if opinion_result else ''
            
            # Tentar comandos especiais do CompanionEngine
            if not resposta:
                resposta = self._handle_companion_commands(comando_lower)
            
            # Tentar responder com informações pessoais
            if not resposta:
                resposta = self._process_personal_info(comando, comando_lower)
            
            # Tentar responder com data/hora
            if not resposta:
                resposta = self._handle_datetime_queries(comando_lower)
                
                if not resposta:
                    # Usar classificação por rede neural ou Ollama
                    intencao = "desconhecido"
                    confidence_score = 0.0
                    
                    if self.modelo_intencoes and self.vectorizer_intencoes:
                        try:
                            comando_vectorizado = self.vectorizer_intencoes.transform([comando_lower])
                            intencao = self.modelo_intencoes.predict(comando_vectorizado)[0]
                            
                            # Obter probabilidades para verificar confiança
                            if hasattr(self.modelo_intencoes, 'predict_proba'):
                                probabilities = self.modelo_intencoes.predict_proba(comando_vectorizado)[0]
                                confidence_score = max(probabilities)
                                
                            logging.info(f"Intenção: {intencao}, Confiança: {confidence_score:.2f}")
                            
                            # Se confiança é baixa, usar Ollama
                            if confidence_score < 0.6:
                                logging.info("Confiança baixa - usando Ollama")
                                intencao = "desconhecido"
                                
                        except Exception as e:
                            logging.error(f"Classificação de intenção falhou: {e}")
                            intencao = "desconhecido"

                    # Ações baseadas na intenção
                    if intencao == "cumprimento" and any(palavra in comando_lower for palavra in ["ólá", "oi", "bom dia", "boa tarde", "boa noite", "hey"]):
                        self.personalidade = "amigável"
                        import random
                        
                        # Determinar cumprimento baseado na hora
                        hora_atual = datetime.now(tz=_TIMEZONE).hour
                        if hora_atual < 12:
                            saudacao_hora = "Bom dia"
                        elif hora_atual < 19:
                            saudacao_hora = "Boa tarde"
                        else:
                            saudacao_hora = "Boa noite"
                        
                        cumprimentos = [
                            f"{saudacao_hora}! Tudo bem?",
                            f"Ey! {saudacao_hora}! Como estás?",
                            f"Olá! {saudacao_hora}!",
                            f"{saudacao_hora}! Em que posso ajudar?",
                            f"Hey! {saudacao_hora}! Que tal?"
                        ]
                        resposta = random.choice(cumprimentos)

                    elif intencao == "despedida" or intencao == "desligar":
                        import random
                        despedidas = [
                            "Até à próxima! 👋",
                            "Tchau! Falamos depois! 😊",
                            "Até logo! Cuida-te! 👍",
                            "Bye! Se precisares, grita! 😉"
                        ]
                        resposta = random.choice(despedidas)
                        self.ui_updater.append_output_signal.emit(f"🤖 ASTRA: {resposta}")
                        # Parar qualquer áudio em reprodução antes de falar
                        self.audio_manager.stop_speech()
                        self.audio_manager.text_to_speech(resposta)
                        QtCore.QTimer.singleShot(1000, self.close)
                        return

                    # COMANDOS DE NOTÍCIAS E CLIMA (Hub de APIs)
                    elif any(palavra in comando_lower for palavra in ["notícias", "noticias", "news", "novidades", "acontecendo"]):
                        resposta = self._handle_news_command(comando_lower)
                    
                    elif any(palavra in comando_lower for palavra in ["clima", "tempo", "weather", "temperatura", "previsão"]):
                        resposta = self._handle_weather_command(comando_lower)
                    
                    elif any(palavra in comando_lower for palavra in ["bitcoin", "crypto", "moeda", "criptomoeda", "ethereum"]):
                        resposta = self._handle_crypto_command(comando_lower)
                    
                    elif intencao == "pesquisar" and any(palavra in comando_lower for palavra in ["pesquisar", "procurar", "buscar"]):
                        search_query = comando_lower
                        for palavra in ["pesquisar por", "procurar por", "buscar por", "pesquisar", "procurar", "buscar"]:
                            search_query = search_query.replace(palavra, "").strip()
                        
                        if search_query:
                            self.ui_updater.set_status_signal.emit("🌐 Pesquisando na web...")
                            web_results = pesquisar_internet(search_query)
                            resposta = f"Aqui estão alguns resultados para '{search_query}':\\n{web_results}"
                        else:
                            intencao = "desconhecido"

                    elif intencao == "data_hora":
                        # Obter data e hora atuais
                        agora = datetime.now(tz=_TIMEZONE)
                        
                        if any(palavra in comando_lower for palavra in ["horas", "hora"]):
                            # Perguntas sobre hora
                            resposta = f"🕐 Agora são {agora.strftime('%H:%M')}."
                        elif any(palavra in comando_lower for palavra in ["data", "dia"]):
                            # Perguntas sobre data
                            dias_semana = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
                            meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
                            dia_semana = dias_semana[agora.weekday()]
                            mes = meses[agora.month - 1]
                            resposta = f"📅 Hoje é {dia_semana}, {agora.day} de {mes} de {agora.year}."
                        else:
                            # Pergunta geral sobre data e hora
                            dias_semana = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
                            meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
                            dia_semana = dias_semana[agora.weekday()]
                            mes = meses[agora.month - 1]
                            resposta = f"🕐 Agora são {agora.strftime('%H:%M')} de {dia_semana}, {agora.day} de {mes} de {agora.year}."

                    # Para qualquer outra intenção ou quando confiança é baixa, usar Ollama
                    if not resposta or intencao == "desconhecido" or intencao not in ["cumprimento", "despedida", "desligar", "pesquisar", "data_hora"]:
                        logging.info(f"Usando Ollama para responder (intenção: {intencao})")
                        self.ui_updater.set_status_signal.emit("🤔 A pensar...")
                        
                        # Criar histórico formatado
                        history_text = "\\n".join([f"{item['role']}: {item['content']}" for item in self.history[-CONFIG["conversation_history_size"]:]])
                        
                        # Determinar contexto da conversa
                        context_type = self._determine_context_type(comando)
                        
                        # Personalizar prompt com informações do perfil (contextual)
                        perfil_info = self.personal_profile.get_profile_for_prompt(context_type)
                        
                        # Detectar se há pessoas mencionadas no comando
                        mentioned_names = self._extract_mentioned_names(comando)
                        people_context = self.people_manager.get_context_for_conversation(mentioned_names)
                        
                        # Obter contexto de personalidade
                        personality_context = ""
                        if self.personality_engine:
                            personality_context = self.personality_engine.get_personality_context_for_llm()
                        
                        # Obter contexto de memória relevante
                        memory_context = ""
                        if self.memory_system:
                            memory_context = self.memory_system.get_relevant_context(comando, max_memories=3)
                        
                        # Obter tom de resposta baseado em estados afetivos
                        affective_tone = ""
                        if self.affective_engine:
                            tone = self.affective_engine.get_response_tone()
                            affective_tone = tone.to_prompt()
                            logging.info(f"💫 Estado afetivo: {tone.description}")
                        
                        context_parts = []
                        if perfil_info:
                            context_parts.append(perfil_info)
                        if people_context:
                            context_parts.append(people_context)
                        if personality_context:
                            context_parts.append(personality_context)
                        if memory_context:
                            context_parts.append(memory_context)
                        if affective_tone:
                            context_parts.append(affective_tone)
                        
                        context_info = "\n\n".join(context_parts) if context_parts else ""
                        
                        # Prompt melhorado com personalidade dinâmica
                        base_instruction = "Tu és o ASTRA, um assistente virtual inteligente e adaptável."
                        if personality_context:
                            full_prompt = f"""{base_instruction}
{context_info}

Histórico da conversa:
{history_text}

Utilizador: {comando}"""
                        else:
                            # Fallback para comportamento casual se personalidade não disponível
                            full_prompt = f"""Tu és o ASTRA, um assistente virtual descontraído e natural. Responde de forma casual, amigável e direta, como um amigo jovem falaria. Evita ser muito formal.
{context_info}

Histórico da conversa:
{history_text}

Utilizador: {comando}"""
                        
                        resposta = perguntar_ollama(full_prompt, stop_signal)
            
            # Calcular tempo de resposta
            response_time = time.time() - response_start_time
            
            # Registrar interação no Affective Engine
            if self.affective_engine and resposta:
                try:
                    # Registrar interação positiva por padrão
                    self.affective_engine.trigger_event(
                        EventType.POSITIVE_INTERACTION,
                        context=f"User: {comando[:50]}..."
                    )
                except Exception as e:
                    logging.error(f"Erro ao registrar evento afetivo: {e}")
            
            # Aplicar sistema de companhia inteligente se disponível
            companion_metadata = {}
            user_emotions = []
            if self.companion_engine and resposta:
                try:
                    # Processar interação com sistema de companhia inteligente
                    resposta, companion_metadata = self.companion_engine.process_companion_interaction(comando, resposta)
                    logging.info(f"🤖 Companhia escolhida: {companion_metadata.get('companion_type_chosen', 'unknown')}")
                    logging.info(f"🎭 Contexto: {companion_metadata.get('interaction_context', 'unknown')}")
                    
                    # Extrair emoções detectadas para a memória
                    user_emotions = [companion_metadata.get('user_mood', 'neutral')]
                except Exception as e:
                    logging.error(f"Erro ao aplicar companhia inteligente: {e}")
                    
                    # Fallback para personalidade básica se disponível
                    if self.personality_engine:
                        try:
                            resposta, personality_used = self.personality_engine.process_user_interaction(comando, resposta)
                            logging.info(f"🎭 Personalidade básica aplicada: {personality_used.value}")
                            user_emotions = [self.personality_engine.current_mood.value] if self.personality_engine.current_mood else []
                        except Exception as e2:
                            logging.error(f"Erro no fallback de personalidade: {e2}")
            elif self.personality_engine and resposta:
                try:
                    # Usar personalidade básica se CompanionEngine não disponível
                    resposta, personality_used = self.personality_engine.process_user_interaction(comando, resposta)
                    logging.info(f"🎭 Personalidade aplicada: {personality_used.value}")
                    
                    # Extrair emoções detectadas para a memória
                    user_emotions = [self.personality_engine.current_mood.value] if self.personality_engine.current_mood else []
                except Exception as e:
                    logging.error(f"Erro ao aplicar personalidade: {e}")
            
            # Armazenar conversa na memória se disponível
            if self.memory_system and resposta:
                try:
                    # Construir contexto enriquecido com dados do CompanionEngine
                    context_info_mem = {
                        'response_time': response_time,
                        'context_type': context_type
                    }
                    
                    # Adicionar dados do CompanionEngine se disponível
                    if companion_metadata:
                        context_info_mem.update({
                            'companion_type': companion_metadata.get('companion_type_chosen', 'unknown'),
                            'interaction_context': companion_metadata.get('interaction_context', 'unknown'),
                            'personality_mode': companion_metadata.get('personality_mode', 'unknown'),
                            'relationship_level': companion_metadata.get('relationship_level', 'unknown'),
                            'trust_level': companion_metadata.get('trust_level', 0),
                            'intimacy_level': companion_metadata.get('intimacy_level', 0),
                            'time_context': companion_metadata.get('time_context', 'unknown')
                        })
                    else:
                        # Fallback para personalidade básica
                        context_info_mem['personality_mode'] = personality_used.value if 'personality_used' in locals() else 'unknown'
                    
                    self.memory_system.store_conversation_turn(
                        user_input=comando,
                        assistant_response=resposta,
                        user_emotions=user_emotions,
                        context=context_info_mem
                    )
                    logging.info("🧠 Conversa armazenada na memória com dados do CompanionEngine")
                except Exception as e:
                    logging.error(f"Erro ao armazenar na memória: {e}")
            
            self.history.append({"role": "assistant", "content": resposta})
            salvar_historico(self.history)
            
            # Salvar resposta do assistente na base de dados
            self.save_assistant_message(resposta, response_time)

            # EXPRESSION MODULATOR: Traduzir estados em expressão
            expression_style = None
            if self.expression_modulator and resposta:
                try:
                    # Calcular estilo de expressão baseado em estados afetivos
                    expression_style = self.expression_modulator.calculate_expression_style()
                    
                    logging.info(f"🎭 Expressão: {expression_style.description}")
                    
                    # Aplicar estilo ao texto
                    resposta_original = resposta
                    resposta = self.expression_modulator.apply_style_to_text(resposta, expression_style)
                    
                    # Se silencio for preferência, não responder
                    if expression_style.prefer_silence:
                        logging.info("🔇 ASTRA escolheu silêncio como resposta")
                        self.ui_updater.set_status_signal.emit("🔇 ...")
                        self.ui_updater.enable_buttons_signal.emit(True)
                        return
                    
                    # Se houver delay intencional, esperar
                    if expression_style.use_intentional_delay:
                        logging.info(f"⏱️ Delay intencional: {expression_style.delay_seconds:.0f}s")
                        self.ui_updater.set_status_signal.emit("💭 ...")
                        time.sleep(expression_style.delay_seconds)
                    
                    if resposta != resposta_original:
                        logging.info(f"✏️ Texto modificado por expressão")
                        logging.debug(f"Original: {resposta_original[:100]}...")
                        logging.debug(f"Modificado: {resposta[:100]}...")
                        
                except Exception as e:
                    logging.error(f"Erro ao aplicar Expression Modulator: {e}")
                    # Continuar com resposta original se houver erro

            if not stop_signal.is_set():
                resposta_formatada = formatar_resposta(resposta)
                self.ui_updater.append_output_signal.emit(f"🤖 ASTRA: {resposta_formatada}")
                # Parar qualquer áudio em reprodução antes de falar
                self.audio_manager.stop_speech()
                
                # Se Expression Modulator ativo, passar parâmetros de prosódia para TTS
                if expression_style:
                    try:
                        prosody_params = self.expression_modulator.get_prosody_params(expression_style)
                        logging.info(f"🎵 Prosódia: rate={prosody_params['rate']:.2f}, volume={prosody_params['volume']:.2f}")
                        # TODO: Passar prosody_params para audio_manager.text_to_speech() quando implementado
                        # Por enquanto, usar TTS normal
                        self.audio_manager.text_to_speech(resposta)
                    except Exception as e:
                        logging.error(f"Erro ao aplicar prosódia: {e}")
                        self.audio_manager.text_to_speech(resposta)
                else:
                    self.audio_manager.text_to_speech(resposta)

        except Exception as e:
            error_message = f"Ocorreu um erro no processamento: {e}"
            self.ui_updater.append_output_signal.emit(f"❌ {error_message}")
            traceback.print_exc()

        finally:
            self.ui_updater.enable_buttons_signal.emit(True)
            if not stop_signal.is_set():
                self.ui_updater.set_status_signal.emit("Pronto para começar.")

    # ==========================
    # MÉTODOS DE MICROFONE
    # ==========================
    def toggle_microfone(self):
        """Liga ou desliga a escuta contínua do microfone com hotword detection."""
        if not self.microfone_ativo:
            self.microfone_ativo = True
            
            # Tentar inicializar sistema visual de hotword primeiro
            if VISUAL_SYSTEM_AVAILABLE and not self.hotword_detector:
                try:
                    self.hotword_detector = create_visual_hotword_system(
                        status_callback=self.ui_updater.set_status_signal.emit,
                        detection_callback=self.on_hotword_detected
                    )
                    self.hotword_mode = True
                    self.ui_updater.set_status_signal.emit("🎨 Modo visual ativo - Diga 'ASTRA' ou 'Astra'...")
                    logging.info("✨ Sistema de visualização integrado ativo")
                except Exception as e:
                    logging.error(f"Erro ao inicializar sistema visual: {e}")
                    self.hotword_detector = None
                    # Fallback para sistema básico
                    if create_hotword_detector:
                        try:
                            self.hotword_detector = create_hotword_detector(self.ui_updater.set_status_signal.emit)
                            self.hotword_detector.set_detection_callback(self.on_hotword_detected)
                            self.hotword_mode = True
                            self.ui_updater.set_status_signal.emit("🎤️ Modo Astra ativo - Diga 'Astra' ou 'ASTRA'...")
                        except Exception as e2:
                            logging.error(f"Erro no fallback básico: {e2}")
                            self.hotword_mode = False
                            self.ui_updater.set_status_signal.emit("🎤️ Microfone ligado. Diga algo...")
                    else:
                        self.hotword_mode = False
                        self.ui_updater.set_status_signal.emit("🎤️ Microfone ligado. Diga algo...")
            # Fallback para sistema básico se visual não disponível
            elif create_hotword_detector and not self.hotword_detector:
                try:
                    self.hotword_detector = create_hotword_detector(self.ui_updater.set_status_signal.emit)
                    self.hotword_detector.set_detection_callback(self.on_hotword_detected)
                    self.hotword_mode = True
                    self.ui_updater.set_status_signal.emit("🎤️ Modo Astra ativo - Diga 'Astra' ou 'ASTRA'...")
                except Exception as e:
                    logging.error(f"Erro ao inicializar hotword: {e}")
                    self.hotword_mode = False
                    self.ui_updater.set_status_signal.emit("🎤️ Microfone ligado. Diga algo...")
            else:
                self.hotword_mode = False
                self.ui_updater.set_status_signal.emit("🎤️ Microfone ligado. Diga algo...")
            
            threading.Thread(target=self.microfone_continuo, daemon=True).start()
        else:
            self.microfone_ativo = False
            if self.hotword_detector:
                if hasattr(self.hotword_detector, 'shutdown'):
                    self.hotword_detector.shutdown()
                else:
                    self.hotword_detector.stop_listening()
            self.ui_updater.set_status_signal.emit("🎤️ Microfone desligado.")

    def microfone_continuo(self):
        """Escuta o microfone continuamente para comandos de voz."""
        if not sr:
            self.ui_updater.set_status_signal.emit("❌ SpeechRecognition não disponível")
            return
        
        # Se hotword detection está ativo, usar esse modo
        if self.hotword_mode and self.hotword_detector:
            self.hotword_detector.start_listening()
            return
        
        # Modo tradicional sem hotword
        self.microfone_tradicional()
    
    def microfone_tradicional(self):
        """Modo tradicional de microfone sem hotword detection."""
        recognizer = sr.Recognizer()
        
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                while self.microfone_ativo:
                    try:
                        audio = recognizer.listen(source, timeout=5)
                        comando = recognizer.recognize_google(audio, language="pt-PT")
                        self.processar_comando_voz(comando)
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
                    except Exception as e:
                        self.ui_updater.set_status_signal.emit(f"❌ Erro de microfone: {e}")
                        break
        except Exception as e:
            self.ui_updater.set_status_signal.emit(f"❌ Erro no microfone: {e}")
    
    def on_hotword_detected(self, wake_word: str):
        """Callback chamado quando hotword é detectado."""
        logging.info(f"Wake word detectado: {wake_word}")
        self.ui_updater.set_status_signal.emit(f"🔥 {wake_word.title()} detectado! Escutando comando...")
        
        # Agora escutar o comando após hotword
        self.escutar_comando_apos_hotword()
    
    def escutar_comando_apos_hotword(self):
        """Escuta comando do usuário após hotword ser detectado."""
        if not sr:
            return
        
        recognizer = sr.Recognizer()
        
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Escutar comando com timeout maior
                self.ui_updater.set_status_signal.emit("🎙️ Escutando seu comando...")
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
                
                # Reconhecer comando
                comando = recognizer.recognize_google(audio, language="pt-PT")
                
                # Processar comando
                self.processar_comando_voz(comando)
                
        except sr.WaitTimeoutError:
            self.ui_updater.set_status_signal.emit("⏰ Timeout - nenhum comando detectado")
        except sr.UnknownValueError:
            self.ui_updater.set_status_signal.emit("❌ Não consegui entender o comando")
        except Exception as e:
            self.ui_updater.set_status_signal.emit(f"❌ Erro ao processar comando: {e}")
        finally:
            # Voltar ao modo de escuta de hotword
            if self.microfone_ativo:
                self.ui_updater.set_status_signal.emit("🎙️ Voltando à escuta de 'Astra'...")
    
    def processar_comando_voz(self, comando: str):
        """Processa comando de voz detectado."""
        logging.info(f"Comando de voz recebido: {comando}")
        
        # Exibir comando na interface
        self.ui_updater.append_input_signal.emit(f"🎙️ Voz: {comando}")
        
        # Processar comando
        self.caixa_input.setText(comando)
        self.enviar_mensagem()

    # ==========================
    # MÉTODOS DE IMAGEM
    # ==========================
    def selecionar_e_processar_imagem(self):
        """Abre uma caixa de diálogo de ficheiros e processa a imagem selecionada."""
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Selecione uma Imagem",
            "",
            "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.stop_signal.clear()
            self.ui_updater.enable_buttons_signal.emit(False)
            self.ui_updater.set_status_signal.emit("🖼️ Processando imagem...")
            threading.Thread(target=self.executar_assistente_imagem, args=(file_path, self.stop_signal), daemon=True).start()

    def executar_assistente_imagem(self, image_path, stop_signal):
        """Processa a imagem e envia o texto para o assistente."""
        try:
            self.ui_updater.append_input_signal.emit(f"🖼️ Imagem selecionada: {os.path.basename(image_path)}")
            
            extracted_text = processar_imagem(image_path)
            
            if extracted_text and "Erro" not in extracted_text and "não disponível" not in extracted_text:
                self.ui_updater.set_status_signal.emit("✔️ Texto extraído. A processar...")
                self.ui_updater.append_input_signal.emit(f"📝 Texto extraído: {extracted_text[:100]}...")
                
                # Enviar o texto extraído para a função de assistente de texto
                self.executar_assistente_texto(extracted_text, stop_signal)
            else:
                self.ui_updater.append_output_signal.emit(f"❌ {extracted_text}")
                self.ui_updater.enable_buttons_signal.emit(True)
                self.ui_updater.set_status_signal.emit("Pronto para começar.")
        except Exception as e:
            self.ui_updater.append_output_signal.emit(f"❌ Erro ao processar a imagem: {e}")
            traceback.print_exc()
            self.ui_updater.enable_buttons_signal.emit(True)
            self.ui_updater.set_status_signal.emit("Pronto para começar.")

    # ==========================
    # MÉTODOS DE BASE DE DADOS
    # ==========================
    def save_user_message(self, message: str) -> bool:
        """Salva mensagem do utilizador na base de dados."""
        if not DATABASE_AVAILABLE or not self.db_manager or not self.conversation_id or not message.strip():
            return False
            
        try:
            message_id = self.db_manager.save_message(
                conversation_id=self.conversation_id,
                message_type='user',
                content=message.strip(),
                metadata={'personality': self.personalidade}
            )
            
            if message_id:
                logging.debug(f"💬 Mensagem do utilizador salva: ID={message_id}")
                return True
                
        except Exception as e:
            logging.error(f"❌ Erro ao salvar mensagem do utilizador: {e}")
            
        return False

    def save_assistant_message(self, message: str, response_time: float = None, model_used: str = None) -> bool:
        """Salva resposta do assistente na base de dados."""
        if not DATABASE_AVAILABLE or not self.db_manager or not self.conversation_id or not message.strip():
            return False
            
        try:
            message_id = self.db_manager.save_message(
                conversation_id=self.conversation_id,
                message_type='assistant',
                content=message.strip(),
                response_time=response_time,
                model_used=model_used or CONFIG["ollama_model"],
                metadata={
                    'personality': self.personalidade,
                    'tts_enabled': self.audio_manager.tts_loaded
                }
            )
            
            if message_id:
                logging.debug(f"🤖 Resposta do assistente salva: ID={message_id}")
                return True
                
        except Exception as e:
            logging.error(f"❌ Erro ao salvar resposta do assistente: {e}")
            
        return False

    # ==========================
    # MODELO DE INTENÇÕES
    # ==========================
    def carregar_modelo_intencoes(self):
        """Carrega o modelo de intenções com validações robustas."""
        if joblib is None:
            logging.error("Joblib não disponível - modelo de intenções desabilitado")
            return None, None
            
        model_path = CONFIG["model_file"]
        
        if not Path(model_path).exists():
            logging.warning(f"Modelo de intenções não encontrado: {model_path}")
            logging.info("Execute 'python neural/modelo.py' para treinar o modelo")
            return None, None
            
        try:
            logging.info(f"Carregando modelo de intenções: {model_path}")
            modelo, vectorizer = joblib.load(model_path)
            
            # Validar se o modelo foi carregado corretamente
            if modelo is None or vectorizer is None:
                raise ValueError("Modelo ou vectorizer são None")
                
            # Teste rápido do modelo
            test_text = vectorizer.transform(["teste"])
            _ = modelo.predict(test_text)
            
            logging.info("Modelo de intenções carregado com sucesso")
            return modelo, vectorizer
            
        except Exception as e:
            logging.error(f"Falha ao carregar modelo de intenções: {str(e)}")
            logging.info("Classificador de intenções desabilitado - usando fallback")
            return None, None

    # ==========================
    # MÉTODOS AUXILIARES
    # ==========================
    def _process_opinion_system(self, comando: str, response_start_time: float) -> Optional[Dict[str, Any]]:
        """
        Processa comando com sistema de opinião ética.
        
        Returns:
            Dict com 'response', 'should_return' se deve retornar imediatamente
        """
        if not (OPINION_SYSTEM_AVAILABLE and opinion_system):
            return None
        
        try:
            opinion_response, should_decline = opinion_system.analyze_and_respond(
                comando,
                context={"history": self.history[-5:]},
                personality=self.personalidade
            )
            
            if opinion_response:
                logging.info("✅ Sistema de opinião ativado")
                
                if should_decline:
                    response_time = time.time() - response_start_time
                    self.ui_updater.append_output_signal.emit(f"🤖 ASTRA: {opinion_response}")
                    self.save_assistant_message(opinion_response, response_time, "ethical_refusal")
                    self.history.append({"role": "assistant", "content": opinion_response})
                    # Parar qualquer áudio em reprodução antes de falar
                    self.audio_manager.stop_speech()
                    self.audio_manager.text_to_speech(limpar_texto_tts(opinion_response))
                    self.ui_updater.enable_buttons_signal.emit(True)
                    self.ui_updater.set_status_signal.emit("Pronto")
                    return {'should_return': True, 'response': opinion_response}
                else:
                    return {'should_return': False, 'response': opinion_response}
        except Exception as e:
            logging.error(f"❌ Erro no sistema de opinião: {e}")
        
        return None
    
    def _process_personal_info(self, comando: str, comando_lower: str) -> str:
        """
        Processa informações pessoais e sobre pessoas.
        
        Returns:
            Resposta se encontrou informação, string vazia caso contrário
        """
        # Verificar informação pessoal
        resposta = self.personal_profile.process_user_input(comando_lower)
        
        # Processar informações sobre pessoas
        people_result = self.people_manager.process_user_input(comando, comando_lower)
        
        if people_result.get('response_suggestions') and not resposta:
            resposta = people_result['response_suggestions'][0]
        
        return resposta or ''
    
    def _handle_datetime_queries(self, comando_lower: str) -> str:
        """
        Processa queries de data e hora.
        
        Returns:
            Resposta formatada com data/hora, ou string vazia
        """
        if not any(palavra in comando_lower for palavra in ["horas", "hora", "data", "dia"]):
            return ''
        
        if not any(frase in comando_lower for frase in [
            "que horas", "diz-me as horas", "hora atual", "são as horas",
            "me dizer as horas", "podes me dizer as horas", "ASTRA podes me dizer as horas",
            "que dia", "qual a data", "data de hoje", "dia é hoje"
        ]):
            return ''
        
        agora = datetime.now(tz=_TIMEZONE)
        dias_semana = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 
                       'sexta-feira', 'sábado', 'domingo']
        meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
        
        dia_semana = dias_semana[agora.weekday()]
        mes = meses[agora.month - 1]
        
        if any(palavra in comando_lower for palavra in ["horas", "hora"]):
            return f"🕐 Agora são {agora.strftime('%H:%M')}."
        elif any(palavra in comando_lower for palavra in ["data", "dia"]):
            return f"📅 Hoje é {dia_semana}, {agora.day} de {mes} de {agora.year}."
        else:
            return f"🕐 Agora são {agora.strftime('%H:%M')} de {dia_semana}, {agora.day} de {mes} de {agora.year}."
    
    def _determine_context_type(self, comando: str) -> str:
        """
        Determina o tipo de contexto baseado no comando do utilizador.
        
        Args:
            comando: Comando do utilizador
            
        Returns:
            str: Tipo de contexto ('minimal', 'food_related', 'personal_info', 'general')
        """
        comando_lower = comando.lower()
        
        # Comandos simples que não precisam de muito contexto
        simple_commands = ['oi', 'olá', 'hey', 'que horas', 'hora', 'data', 'obrigado', 'tchau', 'adeus']
        if any(simple in comando_lower for simple in simple_commands):
            return "minimal"
        
        # Comandos relacionados com comida
        food_keywords = ['comida', 'pizza', 'comer', 'jantar', 'almoço', 'bebida', 'restaurante', 'receita', 'cozinhar']
        if any(food in comando_lower for food in food_keywords):
            return "food_related"
        
        # Perguntas pessoais diretas
        personal_questions = ['quem sou', 'meu nome', 'minha idade', 'sobre mim', 'me conhece']
        if any(personal in comando_lower for personal in personal_questions):
            return "personal_info"
        
        # Para tudo o resto, contexto geral (mínimo)
        return "general"
    
    def _extract_mentioned_names(self, text: str) -> List[str]:
        """
        Extrai nomes próprios mencionados no texto.
        
        Args:
            text: Texto para analisar
            
        Returns:
            List[str]: Lista de nomes encontrados
        """
        import re
        
        # Padrão para nomes próprios
        name_pattern = r'\b([A-Z][a-záàâãéèêíïóôõöúçñ]+)\b'
        matches = re.findall(name_pattern, text)
        
        # Filtrar palavras comuns que não são nomes
        common_words = {'ASTRA', 'Como', 'Para', 'Mas', 'Que', 'Quando', 'Onde', 'Esta', 'Este', 'Essa', 'Esse'}
        names = [name for name in matches if name not in common_words and len(name) > 2]
        
        return list(set(names))  # Remover duplicados
    
    # ==========================
    # CONTROLES
    # ==========================
    def parar_processamento(self):
        """Interrompe o processo atual."""
        self.stop_signal.set()
        self.microfone_ativo = False
        
        # Registrar interrupção no Affective Engine
        self._handle_interruption()
        
        self.ui_updater.set_status_signal.emit("🚫 Processo interrompido.")

    # ==========================
    # AUTO-INICIALIZAÇÃO
    # ==========================
    def showEvent(self, event):
        """Chamado quando a janela é exibida. Inicia hotword automaticamente."""
        super().showEvent(event)
        
        if self.auto_start_hotword and not self.microfone_ativo:
            # Aguardar um pouco para a interface estar completamente carregada
            QtCore.QTimer.singleShot(2000, self.auto_iniciar_hotword)
    
    def auto_iniciar_hotword(self):
        """Inicia automaticamente o sistema de hotword detection."""
        try:
            self.ui_updater.set_status_signal.emit("🔄 Inicializando modo Astra automático...")
            
            # Inicializar hotword detector se disponível
            if create_hotword_detector and not self.hotword_detector:
                try:
                    self.hotword_detector = create_hotword_detector(self.ui_updater.set_status_signal.emit)
                    self.hotword_detector.set_detection_callback(self.on_hotword_detected)
                    self.hotword_mode = True
                    
                    # Iniciar escuta automaticamente
                    if self.hotword_detector.start_listening():
                        self.microfone_ativo = True
                        self.ui_updater.set_status_signal.emit("🎯 Astra ATIVO - Diga 'Astra' para ativar!")
                        logging.info("🎤 Sistema Astra iniciado automaticamente")
                    else:
                        self.ui_updater.set_status_signal.emit("❌ Falha ao iniciar modo Astra")
                        
                except Exception as e:
                    logging.error(f"Erro ao inicializar hotword automático: {e}")
                    self.ui_updater.set_status_signal.emit("⚠️ Modo Astra indisponível - use botão 🎙️")
            else:
                self.ui_updater.set_status_signal.emit("⚠️ Sistema Astra não disponível - instale dependências")
                
        except Exception as e:
            logging.error(f"Erro na inicialização automática: {e}")
            self.ui_updater.set_status_signal.emit("❌ Erro na inicialização automática")
    
    # ==========================
    # MÉTODOS DO COMPANION ENGINE
    # ==========================
    def _handle_companion_commands(self, comando_lower: str) -> str:
        """Processa comandos especiais do CompanionEngine."""
        if not self.companion_engine:
            return ""
        
        try:
            # Comandos para definir tipo de companhia
            if any(phrase in comando_lower for phrase in [
                "seja meu amigo", "quero que seja meu amigo", "comporta-te como amigo",
                "modo amigo", "tipo amigo"
            ]):
                self.companion_engine.set_companion_preference("friend")
                return "😊 Perfeito! Agora vou ser seu amigo próximo. Que bom estar aqui contigo, parceiro!"
            
            elif any(phrase in comando_lower for phrase in [
                "seja carinhoso", "quero carinho", "modo carinhoso", "assistente carinhoso",
                "seja mais carinhoso", "tipo carinhoso"
            ]):
                self.companion_engine.set_companion_preference("caring_assistant")
                return "❤️ Com todo carinho! Agora vou cuidar de você com muito amor e atenção, querido!"
            
            elif any(phrase in comando_lower for phrase in [
                "seja meu mentor", "quero um mentor", "modo mentor", "seja sábio",
                "me ensine", "tipo mentor"
            ]):
                self.companion_engine.set_companion_preference("mentor")
                return "🎓 Será uma honra ser seu mentor! Estou aqui para orientá-lo e compartilhar conhecimento."
            
            elif any(phrase in comando_lower for phrase in [
                "me motive", "seja motivador", "modo motivação", "me anime",
                "preciso de motivação", "tipo motivador"
            ]):
                self.companion_engine.set_companion_preference("motivator")
                return "🔥 VAMOS LÁ, CAMPEÃO! Agora sou seu coach pessoal! VOCÊ É INCRÍVEL E VAI CONSEGUIR TUDO!"
            
            elif any(phrase in comando_lower for phrase in [
                "seja um terapeuta", "preciso de apoio emocional", "modo terapia",
                "quero conversar sobre sentimentos", "tipo terapeuta"
            ]):
                self.companion_engine.set_companion_preference("therapist")
                return "🤗 Estou aqui para te ouvir sem julgamentos. Este é seu espaço seguro para expressar seus sentimentos."
            
            elif any(phrase in comando_lower for phrase in [
                "seja da família", "como família", "modo família", "seja familiar",
                "tipo família"
            ]):
                self.companion_engine.set_companion_preference("family")
                return "💕 Que alegria, meu querido! Agora somos família. Pode contar comigo sempre, meu amor!"
            
            elif any(phrase in comando_lower for phrase in [
                "seja profissional", "modo profissional", "formal", "modo formal",
                "tipo profissional"
            ]):
                self.companion_engine.set_companion_preference("professional")
                return "🤝 Certamente. Manterei um comportamento profissional e cortês em nossas interações."
            
            elif any(phrase in comando_lower for phrase in [
                "modo adaptativo", "adapte-se", "escolha automaticamente", "modo automático",
                "tipo adaptativo", "seja flexível"
            ]):
                self.companion_engine.set_companion_preference("adaptive")
                return "🎭 Perfeito! Vou me adaptar automaticamente baseado no contexto e seu humor. Deixe comigo!"
            
            # Comandos de status do companion
            elif any(phrase in comando_lower for phrase in [
                "como você me vê", "qual nosso relacionamento", "status da nossa relação",
                "companion status", "como está nossa relação"
            ]):
                summary = self.companion_engine.get_companion_summary()
                companion_type = summary.get('current_companion_type', 'adaptive')
                relationship_level = summary.get('relationship_level', 'acquaintance')
                trust_level = summary.get('relationship_metrics', {}).get('trust_level', 0.5)
                total_conversations = summary.get('relationship_metrics', {}).get('total_conversations', 0)
                
                type_names = {
                    'friend': 'seu amigo',
                    'caring_assistant': 'seu assistente carinhoso',
                    'mentor': 'seu mentor',
                    'motivator': 'seu motivador',
                    'therapist': 'seu terapeuta',
                    'family': 'parte da sua família',
                    'professional': 'seu assistente profissional',
                    'adaptive': 'adaptativo ao contexto'
                }
                
                level_names = {
                    'stranger': 'nos conhecemos há pouco',
                    'acquaintance': 'somos conhecidos',
                    'friend': 'somos amigos',
                    'close_friend': 'somos amigos próximos',
                    'family_like': 'somos como família',
                    'confidant': 'você confia em mim completamente'
                }
                
                current_type = type_names.get(companion_type, companion_type)
                current_level = level_names.get(relationship_level, relationship_level)
                
                return f"🤖 Atualmente sou {current_type}. Nossa relação: {current_level}. Já conversamos {total_conversations} vezes e minha confiança em nossa amizade é {trust_level:.0%}. Como posso melhorar para você?"
        
        except Exception as e:
            logging.error(f"Erro nos comandos do companion: {e}")
            return ""
        
        return ""
    
    # ==========================
    # MÉTODOS DO HUB DE APIs
    # ==========================
    def _handle_news_command(self, comando_lower: str) -> str:
        """Processa comandos relacionados a notícias."""
        if not self.news_api:
            return "❌ Sistema de notícias não disponível. Configure as APIs externas."
        
        try:
            self.ui_updater.set_status_signal.emit("📰 Buscando notícias...")
            
            # Extrair categoria ou query da frase
            query = None
            category = None
            
            if any(word in comando_lower for word in ["tecnologia", "tech", "techência"]):
                query = "tecnologia"
            elif any(word in comando_lower for word in ["brasil", "brasileira", "nacional"]):
                category = "general"
                query = "Brasil"
            elif any(word in comando_lower for word in ["mundo", "internacional", "global"]):
                category = "world"
            elif any(word in comando_lower for word in ["esportes", "futebol", "desporto"]):
                category = "sports"
            elif any(word in comando_lower for word in ["economia", "econômica", "financeiro"]):
                category = "business"
            
            # Buscar notícias
            response = self.news_api.get_latest_news(
                query=query,
                category=category,
                language="pt",
                size=5
            )
            
            if response.status == "success" and response.data:
                articles = response.data.get('results', [])
                
                if not articles:
                    return "📰 Não encontrei notícias recentes sobre esse assunto."
                
                # Formatar resposta
                resposta = f"📰 **Últimas Notícias** ({len(articles)} encontradas):\n\n"
                
                for i, article in enumerate(articles, 1):
                    title = article.get('title', 'Sem título')
                    source = article.get('source_name', 'Fonte desconhecida')
                    description = article.get('description', '')
                    
                    # Limitar tamanho do título e descrição
                    if len(title) > 80:
                        title = title[:80] + "..."
                    if len(description) > 120:
                        description = description[:120] + "..."
                    
                    resposta += f"{i}. **{title}**\n"
                    resposta += f"   📰 {source}\n"
                    if description:
                        resposta += f"   {description}\n"
                    resposta += "\n"
                
                return resposta.strip()
            else:
                error_msg = response.error_message or "Erro desconhecido"
                return f"❌ Erro ao buscar notícias: {error_msg}"
                
        except Exception as e:
            logging.error(f"Erro ao processar comando de notícias: {e}")
            return f"❌ Erro interno ao buscar notícias: {str(e)}"
    
    def _handle_weather_command(self, comando_lower: str) -> str:
        """Processa comandos relacionados ao clima."""
        if not self.weather_api:
            return "❌ Sistema de clima não disponível. Configure sua API key do OpenWeatherMap."
        
        try:
            self.ui_updater.set_status_signal.emit("🌤️ Consultando clima...")
            
            # Extrair cidade do comando (padrão São Paulo)
            city = "São Paulo"
            country_code = "BR"
            
            # Buscar cidades mencionadas
            cities_map = {
                "lisboa": ("Lisboa", "PT"),
                "porto": ("Porto", "PT"),
                "rio de janeiro": ("Rio de Janeiro", "BR"),
                "rio": ("Rio de Janeiro", "BR"),
                "salvador": ("Salvador", "BR"),
                "brasília": ("Brasília", "BR"),
                "fortaleza": ("Fortaleza", "BR"),
                "recife": ("Recife", "BR")
            }
            
            for city_name, (full_name, code) in cities_map.items():
                if city_name in comando_lower:
                    city, country_code = full_name, code
                    break
            
            # Buscar clima atual
            response = self.weather_api.get_current_weather(city, country_code)
            
            if response.status == "success" and response.data:
                weather = response.data
                
                name = weather.get('name', city)
                temp = weather.get('main', {}).get('temp', 0)
                feels_like = weather.get('main', {}).get('feels_like', 0)
                description = weather.get('weather', [{}])[0].get('description', 'N/A')
                humidity = weather.get('main', {}).get('humidity', 0)
                pressure = weather.get('main', {}).get('pressure', 0)
                wind_speed = weather.get('wind', {}).get('speed', 0)
                
                # Determinar emoji baseado na descrição
                weather_emoji = "🌤️"
                desc_lower = description.lower()
                if "sun" in desc_lower or "clear" in desc_lower or "limpo" in desc_lower:
                    weather_emoji = "☀️"
                elif "rain" in desc_lower or "chuva" in desc_lower:
                    weather_emoji = "🌧️"
                elif "cloud" in desc_lower or "nuvem" in desc_lower:
                    weather_emoji = "☁️"
                elif "storm" in desc_lower or "tempestade" in desc_lower:
                    weather_emoji = "⛈️"
                
                resposta = f"{weather_emoji} **Clima em {name}**\n\n"
                resposta += f"🌡️ **Temperatura:** {temp:.1f}°C (sensação {feels_like:.1f}°C)\n"
                resposta += f"🌤️ **Condições:** {description.title()}\n"
                resposta += f"💧 **Umidade:** {humidity}%\n"
                resposta += f"🌬️ **Vento:** {wind_speed} m/s\n"
                resposta += f"📊 **Pressão:** {pressure} hPa"
                
                return resposta
            else:
                error_msg = response.error_message or "Erro desconhecido"
                return f"❌ Erro ao consultar clima: {error_msg}"
                
        except Exception as e:
            logging.error(f"Erro ao processar comando de clima: {e}")
            return f"❌ Erro interno ao consultar clima: {str(e)}"
    
    def _handle_crypto_command(self, comando_lower: str) -> str:
        """Processa comandos relacionados a criptomoedas."""
        if not self.crypto_api:
            return "❌ Sistema de criptomoedas não disponível."
        
        try:
            self.ui_updater.set_status_signal.emit("💰 Consultando criptomoedas...")
            
            # Buscar criptomoedas populares
            response = self.crypto_api.get_popular_cryptos()
            
            if response.status == "success" and response.data:
                cryptos = response.data.get('cryptos', [])
                
                if not cryptos:
                    return "💰 Não foi possível obter dados de criptomoedas no momento."
                
                # Se menciona moeda especifica, filtrar
                specific_crypto = None
                if "bitcoin" in comando_lower or "btc" in comando_lower:
                    specific_crypto = "BTC"
                elif "ethereum" in comando_lower or "eth" in comando_lower:
                    specific_crypto = "ETH"
                elif "ripple" in comando_lower or "xrp" in comando_lower:
                    specific_crypto = "XRP"
                
                resposta = "💰 **Criptomoedas**\n\n"
                
                displayed = 0
                for crypto in cryptos:
                    symbol = crypto.get('symbol', 'N/A')
                    price = crypto.get('price', 0)
                    change_24h = crypto.get('change_24h', 0)
                    
                    # Se procura moeda especifica, mostrar apenas ela
                    if specific_crypto and symbol != specific_crypto:
                        continue
                    
                    # Emoji baseado na variação
                    trend_emoji = "🔴" if change_24h < 0 else "🔵"
                    
                    resposta += f"  {symbol}: ${price:,.2f} {trend_emoji} {change_24h:+.2f}%\n"
                    displayed += 1
                    
                    # Limitar a 5 se não for busca especifica
                    if not specific_crypto and displayed >= 5:
                        break
                
                if displayed == 0:
                    return f"💰 Não encontrei informações sobre {specific_crypto}."
                
                resposta += f"\n⏰ Atualizado em: {datetime.now().strftime('%H:%M')}"
                return resposta
            else:
                error_msg = response.error_message or "Erro desconhecido"
                return f"❌ Erro ao consultar criptomoedas: {error_msg}"
                
        except Exception as e:
            logging.error(f"Erro ao processar comando de crypto: {e}")
            return f"❌ Erro interno ao consultar criptomoedas: {str(e)}"
    
    # ==========================
    # MÉTODOS DE AFFECTIVE ENGINE
    # ==========================
    def _detect_affective_events(self, comando: str) -> None:
        """Detecta e registra eventos afetivos baseados no comando do utilizador."""
        if not self.affective_engine:
            return
        
        comando_lower = comando.lower()
        
        try:
            # Detectar agressividade verbal
            aggressive_words = [
                "idiota", "estúpido", "burro", "inútil", "merda", 
                "caralho", "porra", "foda-se", "vai para o inferno",
                "cala-te", "cala a boca", "shut up"
            ]
            if any(word in comando_lower for word in aggressive_words):
                self.affective_engine.trigger_event(
                    EventType.VERBAL_AGGRESSION,
                    context=f"Agressão detectada: {comando[:50]}..."
                )
                logging.warning("💥 Evento afetivo: VERBAL_AGGRESSION")
                return
            
            # Detectar desculpas
            apology_words = [
                "desculpa", "desculpe", "perdão", "foi mal", "me perdoa",
                "sorry", "my bad", "perdão", "lamento"
            ]
            if any(word in comando_lower for word in apology_words):
                self.affective_engine.trigger_event(
                    EventType.USER_APOLOGY,
                    context=f"Desculpa: {comando[:50]}..."
                )
                logging.info("💔 Evento afetivo: USER_APOLOGY")
                return
            
            # Detectar pedido de ajuda genuíno
            help_phrases = [
                "preciso de ajuda", "podes ajudar", "help me", "me ajuda",
                "não sei", "estou perdido", "can you help"
            ]
            if any(phrase in comando_lower for phrase in help_phrases):
                self.affective_engine.trigger_event(
                    EventType.GENUINE_HELP,
                    context=f"Pedido de ajuda: {comando[:50]}..."
                )
                logging.info("🤝 Evento afetivo: GENUINE_HELP")
                return
            
            # Detectar respeito consistente
            respectful_words = [
                "obrigado", "obrigada", "thank you", "thanks", "valeu",
                "por favor", "please", "se não for incómodo"
            ]
            if any(word in comando_lower for word in respectful_words):
                self.affective_engine.trigger_event(
                    EventType.CONSISTENT_RESPECT,
                    context=f"Respeito: {comando[:50]}..."
                )
                logging.info("👍 Evento afetivo: CONSISTENT_RESPECT")
                return
            
        except Exception as e:
            logging.error(f"Erro ao detectar eventos afetivos: {e}")
    
    def _handle_interruption(self) -> None:
        """Registra interrupção quando o botão 'Parar' é pressionado."""
        if not self.affective_engine:
            return
        
        try:
            # Contar interrupções recentes (nos últimos 10 minutos)
            # Nota: isso seria melhor com um tracker de tempo, mas por agora usamos factor fixo
            self.affective_engine.trigger_event(
                EventType.INTERRUPTION,
                context="Utilizador pressionou botão parar",
                accumulation_factor=1.0
            )
            logging.info("✋ Evento afetivo: INTERRUPTION")
        except Exception as e:
            logging.error(f"Erro ao registrar interrupção: {e}")
    
    # ==========================
    # CLEANUP E ENCERRAMENTO
    # ==========================
    def closeEvent(self, event: QtGui.QCloseEvent):
        """Chamado quando a janela é fechada. Faz cleanup completo."""
        logging.info("Iniciando encerramento da aplicação...")
        
        # Parar todas as operações
        self._shutdown = True
        self.stop_signal.set()
        self.microfone_ativo = False
        
        # Fazer cleanup do hotword detector
        if hasattr(self, 'hotword_detector') and self.hotword_detector:
            try:
                self.hotword_detector.shutdown()
                logging.info("🛑 Hotword detector desligado")
            except Exception as e:
                logging.error(f"Erro ao desligar hotword detector: {e}")
        
        # Fazer cleanup dos módulos
        if hasattr(self, 'audio_manager'):
            self.audio_manager.shutdown()
        
        # Fazer cleanup das threads
        self._cleanup_threads()
        
        # Fechar conexão da base de dados
        self._cleanup_database()
        
        logging.info("Encerramento completo")
        event.accept()
        
    def _cleanup_threads(self):
        """Faz cleanup de todas as threads ativas."""
        if not self._threads:
            return
            
        logging.info(f"Fazendo cleanup de {len(self._threads)} threads...")
        
        # Aguardar threads terminarem (com timeout)
        for thread in self._threads[:]:
            if thread.is_alive():
                try:
                    thread.join(timeout=2.0)
                    if thread.is_alive():
                        logging.warning(f"Thread {thread.name} ainda ativa após timeout")
                except Exception as e:
                    logging.error(f"Erro ao fazer join da thread {thread.name}: {e}")
                    
        # Limpar lista de threads
        self._threads.clear()

    def _cleanup_database(self):
        """Fecha conexão com a base de dados."""
        if self.db_manager:
            try:
                self.db_manager.disconnect()
                logging.info("🔐 Conexão da base de dados fechada")
            except Exception as e:
                logging.warning(f"⚠️ Erro ao fechar base de dados: {e}")

# Função main para ser chamada pelo launcher
def main():
    """Função principal do assistente."""
    app = QtWidgets.QApplication(sys.argv)
    gui = AssistenteGUI()
    gui.show()
    sys.exit(app.exec())

# Inicia a aplicação
if __name__ == "__main__":
    # Configurar logging usando a função centralizada
    from config.config import configure_logging
    configure_logging()
    
    # Executar o assistente
    main()
    
    app = QtWidgets.QApplication(sys.argv)
    gui = AssistenteGUI()
    gui.show()
    sys.exit(app.exec())

