#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Setup do Sistema de Voz
Script para configurar e baixar dependências do sistema de voz e hotword detection.

Funcionalidades:
- Download automático de modelos Vosk
- Instalação de dependências de hotword
- Configuração inicial do sistema de voz
- Teste de funcionalidades
"""

import os
import sys
import urllib.request
import zipfile
import logging
from pathlib import Path
import subprocess
import json

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoiceSystemSetup:
    """Configurador do sistema de voz ALEX."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.models_dir = self.project_root / "models"
        self.voice_dir = self.project_root / "voice"
        self.config_file = self.voice_dir / "voice_config.json"
        
        # URLs dos modelos
        self.vosk_models = {
            "portuguese_small": {
                "url": "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip",
                "filename": "vosk-model-small-pt-0.3.zip",
                "extracted_name": "vosk-model-small-pt-0.3",
                "size": "40MB"
            },
            "portuguese_large": {
                "url": "https://alphacephei.com/vosk/models/vosk-model-pt-0.3.zip",
                "filename": "vosk-model-pt-0.3.zip", 
                "extracted_name": "vosk-model-pt-0.3",
                "size": "1.8GB"
            }
        }
    
    def ensure_directories(self):
        """Cria diretórios necessários."""
        self.models_dir.mkdir(exist_ok=True)
        self.voice_dir.mkdir(exist_ok=True)
        logger.info(f"📁 Diretórios criados: {self.models_dir}, {self.voice_dir}")
    
    def install_hotword_dependencies(self):
        """Instala dependências de hotword detection."""
        logger.info("📦 Instalando dependências de hotword...")
        
        dependencies = [
            "pvporcupine",
            "vosk", 
            "pyaudio"
        ]
        
        for dep in dependencies:
            try:
                logger.info(f"Instalando {dep}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, text=True, check=True)
                logger.info(f"✅ {dep} instalado com sucesso")
            except subprocess.CalledProcessError as e:
                logger.warning(f"⚠️ Erro ao instalar {dep}: {e}")
                if dep == "pyaudio":
                    logger.info("💡 Para PyAudio no Windows, tente: pip install pipwin && pipwin install pyaudio")
    
    def download_vosk_model(self, model_name="portuguese_small"):
        """Baixa modelo Vosk."""
        if model_name not in self.vosk_models:
            logger.error(f"❌ Modelo {model_name} não encontrado")
            return False
        
        model_info = self.vosk_models[model_name]
        model_path = self.models_dir / model_info["extracted_name"]
        
        # Verificar se já existe
        if model_path.exists():
            logger.info(f"✅ Modelo {model_name} já existe em {model_path}")
            return True
        
        logger.info(f"📥 Baixando modelo {model_name} ({model_info['size']})...")
        
        try:
            zip_path = self.models_dir / model_info["filename"]
            
            # Download com barra de progresso
            def progress_hook(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, (block_num * block_size * 100) // total_size)
                    print(f"\r📊 Download: {percent}%", end="", flush=True)
            
            urllib.request.urlretrieve(
                model_info["url"], 
                zip_path, 
                reporthook=progress_hook
            )
            print()  # Nova linha após progresso
            
            # Extrair
            logger.info("📂 Extraindo modelo...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.models_dir)
            
            # Remover arquivo zip
            zip_path.unlink()
            
            logger.info(f"✅ Modelo {model_name} instalado em {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao baixar modelo {model_name}: {e}")
            return False
    
    def create_config_file(self):
        """Cria arquivo de configuração."""
        config = {
            "hotword": {
                "enabled": True,
                "wake_words": ["jarvis", "alex", "assistente", "hey alex"],
                "sensitivity": 0.7,
                "engine": "auto"  # auto, porcupine, vosk, simple_stt
            },
            "vosk": {
                "model_path": str(self.models_dir / "vosk-model-small-pt-0.3"),
                "sample_rate": 16000
            },
            "porcupine": {
                "keywords": ["computer", "alexa"],
                "sensitivity": 0.7
            },
            "tts": {
                "engine": "auto",  # auto, sapi, xtts
                "voice_rate": 180,
                "voice_volume": 0.9
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"⚙️ Configuração criada em {self.config_file}")
    
    def test_system(self):
        """Testa componentes do sistema."""
        logger.info("🧪 Testando sistema de voz...")
        
        # Teste 1: Import do hotword detector
        try:
            from voice.hotword_detector import create_hotword_detector
            logger.info("✅ Hotword detector importado com sucesso")
        except ImportError as e:
            logger.error(f"❌ Erro ao importar hotword detector: {e}")
        
        # Teste 2: PyAudio
        try:
            import pyaudio
            audio = pyaudio.PyAudio()
            device_count = audio.get_device_count()
            audio.terminate()
            logger.info(f"✅ PyAudio funcionando - {device_count} dispositivos de áudio")
        except Exception as e:
            logger.error(f"❌ Erro no PyAudio: {e}")
        
        # Teste 3: SpeechRecognition
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            logger.info("✅ SpeechRecognition disponível")
        except ImportError:
            logger.error("❌ SpeechRecognition não instalado")
        
        # Teste 4: Modelos Vosk
        vosk_model_path = self.models_dir / "vosk-model-small-pt-0.3"
        if vosk_model_path.exists():
            logger.info(f"✅ Modelo Vosk encontrado em {vosk_model_path}")
        else:
            logger.warning("⚠️ Modelo Vosk não encontrado")
        
        # Teste 5: Porcupine
        try:
            import pvporcupine
            logger.info("✅ Porcupine disponível")
        except ImportError:
            logger.warning("⚠️ Porcupine não instalado")
        
        # Teste 6: VOSK
        try:
            import vosk
            logger.info("✅ Vosk disponível")
        except ImportError:
            logger.warning("⚠️ Vosk não instalado")
    
    def run_full_setup(self):
        """Executa setup completo."""
        logger.info("🚀 Iniciando configuração do sistema de voz ALEX...")
        
        # 1. Criar diretórios
        self.ensure_directories()
        
        # 2. Instalar dependências
        self.install_hotword_dependencies()
        
        # 3. Baixar modelo Vosk pequeno
        self.download_vosk_model("portuguese_small")
        
        # 4. Criar configuração
        self.create_config_file()
        
        # 5. Testar sistema
        self.test_system()
        
        logger.info("🎉 Setup do sistema de voz concluído!")
        logger.info("💡 Agora você pode usar: 'Jarvis' ou 'Alex' para ativar o assistente")
    
    def interactive_setup(self):
        """Setup interativo."""
        print("🤖 ALEX - Configuração do Sistema de Voz")
        print("=" * 40)
        
        # Perguntar sobre modelo Vosk
        print("\n📥 Modelos Vosk disponíveis:")
        print("1. Português Pequeno (40MB) - Recomendado")
        print("2. Português Grande (1.8GB) - Melhor precisão")
        print("3. Pular download de modelos")
        
        while True:
            choice = input("\nEscolha (1-3): ").strip()
            if choice == "1":
                model = "portuguese_small"
                break
            elif choice == "2":
                model = "portuguese_large"
                break
            elif choice == "3":
                model = None
                break
            else:
                print("❌ Escolha inválida")
        
        # Executar setup
        self.ensure_directories()
        self.install_hotword_dependencies()
        
        if model:
            self.download_vosk_model(model)
        
        self.create_config_file()
        
        # Perguntar sobre teste
        test = input("\n🧪 Executar testes? (s/N): ").strip().lower()
        if test in ['s', 'sim', 'y', 'yes']:
            self.test_system()
        
        print("\n🎉 Configuração concluída!")
        print("💡 Execute 'python run_alex.py' para testar o assistente")


def main():
    """Função principal."""
    setup = VoiceSystemSetup()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "auto":
            setup.run_full_setup()
        elif command == "models":
            setup.download_vosk_model("portuguese_small")
        elif command == "deps":
            setup.install_hotword_dependencies()
        elif command == "test":
            setup.test_system()
        elif command == "config":
            setup.create_config_file()
        else:
            print("❌ Comando inválido")
            print("Comandos disponíveis: auto, models, deps, test, config")
    else:
        setup.interactive_setup()


if __name__ == "__main__":
    main()