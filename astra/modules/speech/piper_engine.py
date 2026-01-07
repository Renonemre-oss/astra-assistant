#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Piper TTS Engine
Wrapper para Piper TTS - Sistema de voz neural de alta qualidade offline.
"""

import logging
import io
import wave
from pathlib import Path
from typing import Optional
import tempfile

logger = logging.getLogger(__name__)


class PiperTTSEngine:
    """
    Engine Piper TTS para o Astra.
    
    Piper é um sistema de TTS neural de alta qualidade que roda offline.
    Produz vozes muito mais naturais que pyttsx3.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializa o Piper TTS Engine.
        
        Args:
            model_path: Caminho para o modelo Piper (.onnx)
        """
        self.piper_voice = None
        self.model_path = model_path
        self.is_initialized = False
        self.temp_audio_file = None
        
        # Diretório de modelos
        self.models_dir = Path(__file__).parent / "piper_models"
        self.models_dir.mkdir(exist_ok=True)
        
        logger.info("Piper TTS Engine criado")
    
    def initialize(self, model_name: str = "pt_PT-tugao-medium") -> bool:
        """
        Inicializa o Piper com um modelo específico.
        
        Args:
            model_name: Nome do modelo a carregar
            
        Returns:
            bool: True se inicializado com sucesso
        """
        try:
            from piper import PiperVoice
            
            # Se model_path foi fornecido, usar ele
            if self.model_path and Path(self.model_path).exists():
                model_file = Path(self.model_path)
            else:
                # Procurar modelo no diretório de modelos
                model_file = self.models_dir / f"{model_name}.onnx"
                
                if not model_file.exists():
                    logger.warning(f"Modelo Piper não encontrado: {model_file}")
                    logger.info("Use download_model() para baixar modelos")
                    return False
            
            # Carregar modelo
            logger.info(f"Carregando modelo Piper: {model_file}")
            self.piper_voice = PiperVoice.load(str(model_file))
            
            self.is_initialized = True
            logger.info(f"✅ Piper TTS inicializado com modelo: {model_name}")
            return True
            
        except ImportError:
            logger.error("Piper TTS não está instalado. Execute: pip install piper-tts")
            return False
        except Exception as e:
            logger.error(f"Erro ao inicializar Piper: {e}")
            return False
    
    def synthesize(self, text: str) -> Optional[bytes]:
        """
        Sintetiza texto em áudio.
        
        Args:
            text: Texto para sintetizar
            
        Returns:
            bytes: Dados de áudio WAV ou None se falhar
        """
        if not self.is_initialized or not self.piper_voice:
            logger.error("Piper não inicializado")
            return None
        
        if not text or not text.strip():
            return None
        
        try:
            # Buffer para armazenar áudio
            audio_buffer = io.BytesIO()
            
            # Sintetizar texto - retorna um iterador de AudioChunk
            audio_chunks = list(self.piper_voice.synthesize(text))
            
            if not audio_chunks:
                logger.error("Nenhum áudio gerado")
                return None
            
            # Pegar parâmetros do primeiro chunk
            first_chunk = audio_chunks[0]
            sample_rate = first_chunk.sample_rate
            sample_width = first_chunk.sample_width
            num_channels = first_chunk.sample_channels
            
            # Criar arquivo WAV em memória
            with wave.open(audio_buffer, 'wb') as wav_file:
                wav_file.setnchannels(num_channels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(sample_rate)
                
                # Escrever todos os chunks de áudio
                for chunk in audio_chunks:
                    wav_file.writeframes(chunk.audio_int16_bytes)
            
            # Retornar dados de áudio
            audio_buffer.seek(0)
            return audio_buffer.read()
            
        except Exception as e:
            logger.error(f"Erro ao sintetizar com Piper: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        Fala o texto usando Piper TTS.
        
        Args:
            text: Texto a ser falado
            blocking: Se deve aguardar conclusão
            
        Returns:
            bool: True se sucesso
        """
        if not text or not text.strip():
            return False
        
        try:
            # Sintetizar áudio
            audio_data = self.synthesize(text)
            if not audio_data:
                return False
            
            # Salvar em arquivo temporário
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                self.temp_audio_file = temp_file.name
            
            # Reproduzir áudio
            return self._play_audio(self.temp_audio_file, blocking)
            
        except Exception as e:
            logger.error(f"Erro ao falar com Piper: {e}")
            return False
    
    def _play_audio(self, audio_file: str, blocking: bool = True) -> bool:
        """
        Reproduz arquivo de áudio.
        
        Args:
            audio_file: Caminho para arquivo de áudio
            blocking: Se deve aguardar conclusão
            
        Returns:
            bool: True se sucesso
        """
        import platform
        import subprocess
        
        try:
            # Tentar usar pygame primeiro (melhor compatibilidade multiplataforma)
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                
                if blocking:
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                
                return True
            except ImportError:
                pass
            
            # Fallback para playsound
            try:
                from playsound import playsound
                playsound(audio_file, block=blocking)
                return True
            except ImportError:
                pass
            
            # Fallback específico para Linux
            if platform.system() == 'Linux':
                # Tentar aplay (ALSA - mais comum)
                try:
                    if blocking:
                        subprocess.run(['aplay', '-q', audio_file], check=True)
                    else:
                        subprocess.Popen(['aplay', '-q', audio_file])
                    return True
                except (FileNotFoundError, subprocess.CalledProcessError):
                    pass
                
                # Tentar paplay (PulseAudio)
                try:
                    if blocking:
                        subprocess.run(['paplay', audio_file], check=True)
                    else:
                        subprocess.Popen(['paplay', audio_file])
                    return True
                except (FileNotFoundError, subprocess.CalledProcessError):
                    pass
                
                # Tentar ffplay (ffmpeg)
                try:
                    cmd = ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', audio_file]
                    if blocking:
                        subprocess.run(cmd, check=True)
                    else:
                        subprocess.Popen(cmd)
                    return True
                except (FileNotFoundError, subprocess.CalledProcessError):
                    pass
            
            # Fallback para winsound (Windows only)
            elif platform.system() == 'Windows':
                try:
                    import winsound
                    if blocking:
                        winsound.PlaySound(audio_file, winsound.SND_FILENAME)
                    else:
                        winsound.PlaySound(audio_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    return True
                except ImportError:
                    pass
            
            logger.error("Nenhum sistema de reprodução de áudio disponível")
            logger.info("Linux: Instale aplay (alsa-utils), paplay (pulseaudio-utils) ou ffplay (ffmpeg)")
            logger.info("Ou instale pygame: pip install pygame")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao reproduzir áudio: {e}")
            return False
    
    def stop(self):
        """Para a reprodução atual."""
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except:
            pass
        
        # Limpar arquivo temporário
        if self.temp_audio_file:
            try:
                Path(self.temp_audio_file).unlink(missing_ok=True)
            except:
                pass
    
    def get_available_models(self) -> list:
        """
        Lista modelos Piper disponíveis localmente.
        
        Returns:
            list: Lista de modelos encontrados
        """
        models = []
        for model_file in self.models_dir.glob("*.onnx"):
            models.append(model_file.stem)
        return models
    
    def download_model(self, model_name: str = "pt_BR-faber-medium") -> bool:
        """
        Baixa um modelo Piper do Hugging Face.
        
        Args:
            model_name: Nome do modelo a baixar
            
        Returns:
            bool: True se baixado com sucesso
        """
        try:
            # URL base dos modelos Piper no Hugging Face
            base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
            
            # Modelos disponíveis em português
            pt_models = {
                # Português Brasileiro
                "pt_BR-faber-medium": {
                    "path": "pt/pt_BR/faber/medium",
                    "file": "pt_BR-faber-medium.onnx"
                },
                "pt_BR-cadu-medium": {
                    "path": "pt/pt_BR/cadu/medium",
                    "file": "pt_BR-cadu-medium.onnx"
                },
                # Português de Portugal
                "pt_PT-tugao-medium": {
                    "path": "pt/pt_PT/tug%C3%A3o/medium",
                    "file": "pt_PT-tug%C3%A3o-medium.onnx"  # Nome real do arquivo com til encodado
                },
            }
            
            if model_name not in pt_models:
                logger.error(f"Modelo {model_name} não disponível")
                logger.info(f"Modelos disponíveis: {list(pt_models.keys())}")
                return False
            
            model_info = pt_models[model_name]
            model_filename = model_info["file"]
            model_path_url = model_info["path"]
            
            # URLs completas
            model_url = f"{base_url}/{model_path_url}/{model_filename}"
            json_url = f"{base_url}/{model_path_url}/{model_filename}.json"
            
            model_path = self.models_dir / model_filename
            json_path = self.models_dir / f"{model_filename}.json"
            
            logger.info(f"📥 Baixando modelo Piper: {model_name}...")
            logger.info(f"URL: {model_url}")
            
            # Tentar usar requests primeiro (melhor suporte a Unicode)
            try:
                import requests
                
                # Baixar modelo .onnx
                logger.info("Baixando arquivo .onnx (pode levar alguns minutos)...")
                response = requests.get(model_url, stream=True)
                response.raise_for_status()
                
                with open(model_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Baixar arquivo de configuração JSON
                logger.info("Baixando arquivo de configuração .json...")
                try:
                    json_response = requests.get(json_url)
                    json_response.raise_for_status()
                    with open(json_path, 'wb') as f:
                        f.write(json_response.content)
                except Exception as e:
                    logger.warning(f"Arquivo de configuração JSON não encontrado: {e}")
                    
            except ImportError:
                # Fallback para urllib
                import urllib.request
                logger.info("Usando urllib (requests não disponível)")
                
                # Baixar modelo .onnx
                logger.info("Baixando arquivo .onnx (pode levar alguns minutos)...")
                urllib.request.urlretrieve(model_url, model_path)
                
                # Baixar arquivo de configuração JSON
                logger.info("Baixando arquivo de configuração .json...")
                try:
                    urllib.request.urlretrieve(json_url, json_path)
                except Exception as e:
                    logger.warning(f"Arquivo de configuração JSON não encontrado: {e}")
            
            logger.info(f"✅ Modelo baixado com sucesso: {model_path}")
            
            # Renomear arquivo se tiver caracteres encodados no nome
            if "%" in model_filename:
                # Criar nome sem encoding
                clean_filename = model_filename.replace("%C3%A3", "a")  # ã -> a
                clean_path = self.models_dir / clean_filename
                clean_json_path = self.models_dir / f"{clean_filename}.json"
                
                try:
                    import shutil
                    shutil.move(str(model_path), str(clean_path))
                    if json_path.exists():
                        shutil.move(str(json_path), str(clean_json_path))
                    logger.info(f"Arquivo renomeado para: {clean_path}")
                except Exception as e:
                    logger.warning(f"Não foi possível renomear arquivo: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao baixar modelo: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Criar engine
    engine = PiperTTSEngine()
    
    # Listar modelos disponíveis
    models = engine.get_available_models()
    print(f"Modelos disponíveis: {models}")
    
    # Se não houver modelos, baixar um
    if not models:
        print("Baixando modelo pt_BR-faber-medium...")
        engine.download_model("pt_BR-faber-medium")
    
    # Inicializar
    if engine.initialize():
        # Testar
        print("Testando Piper TTS...")
        engine.speak("Olá! Eu sou o Astra, seu assistente pessoal inteligente.")
    else:
        print("Falha ao inicializar Piper TTS")
