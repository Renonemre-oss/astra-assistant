#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎤 ASTRA - Módulo de Voice Cloning com Coqui XTTS v2
Sistema avançado de clonagem de voz usando o estado da arte em TTS.

Funcionalidades:
- Clonagem de voz com apenas 10-30 segundos de áudio
- Suporte multilíngue (Português, Inglês, Espanhol, etc.)
- Interface simples para gravação e processamento
- Cache inteligente de modelos
- Otimização automática CPU/GPU
"""

import os
import json
import time
import torch
import logging
import librosa
import soundfile as sf
import numpy as np
from typing import Optional, Dict, List, Tuple
from pathlib import Path

# Configurar PyTorch para permitir carregamento de modelos TTS
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Temporariamente definir weights_only=False para compatibilidade com TTS
original_torch_load = torch.load
def patched_torch_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_torch_load

from TTS.api import TTS
try:
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts
except ImportError:
    XttsConfig = None
    Xtts = None

# Processamento de áudio
import noisereduce as nr
from pydub import AudioSegment
from pydub.effects import normalize

class XTTSVoiceCloning:
    """
    Sistema de clonagem de voz usando Coqui XTTS v2.
    """
    
    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
        """
        Inicializa o sistema de voice cloning.
        
        Args:
            model_name: Nome do modelo XTTS a usar
        """
        self.model_name = model_name
        self.tts = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Diretórios
        self.voices_dir = Path("speech/cloned_voices")
        self.cache_dir = Path("speech/cache")
        self.temp_dir = Path("speech/temp")
        
        # Criar diretórios se não existirem
        for directory in [self.voices_dir, self.cache_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Configuração
        self.sample_rate = 22050
        self.max_audio_length = 30  # segundos
        self.min_audio_length = 5   # segundos
        
        # Logging
        self.logger = logging.getLogger("XTTS_VoiceCloning")
        self.logger.setLevel(logging.INFO)
        
        # Cache de vozes carregadas
        self.loaded_voices = {}
        
        self.logger.info(f"🎤 XTTS Voice Cloning iniciado - Dispositivo: {self.device}")
    
    def initialize_model(self) -> bool:
        """
        Inicializa o modelo XTTS.
        
        Returns:
            True se inicializado com sucesso
        """
        try:
            self.logger.info("🔄 Carregando modelo XTTS v2...")
            
            # Inicializar TTS
            self.tts = TTS(model_name=self.model_name)
            
            # Mover para dispositivo se necessário
            if hasattr(self.tts, 'synthesizer') and hasattr(self.tts.synthesizer, 'tts_model'):
                if hasattr(self.tts.synthesizer.tts_model, 'to'):
                    self.tts.synthesizer.tts_model.to(self.device)
            
            self.logger.info("✅ Modelo XTTS v2 carregado com sucesso!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar modelo XTTS: {str(e)}")
            return False
    
    def preprocess_audio(self, audio_file: str) -> Optional[str]:
        """
        Pré-processa áudio para clonagem de voz.
        
        Args:
            audio_file: Caminho para o arquivo de áudio
        
        Returns:
            Caminho para o áudio processado ou None se erro
        """
        try:
            self.logger.info(f"🎵 Pré-processando áudio: {audio_file}")
            
            # Carregar áudio
            audio, sr = librosa.load(audio_file, sr=None)
            
            # Converter para sample rate padrão
            if sr != self.sample_rate:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)
            
            # Normalizar volume
            audio = librosa.util.normalize(audio)
            
            # Redução de ruído
            audio = nr.reduce_noise(y=audio, sr=self.sample_rate)
            
            # Verificar duração
            duration = len(audio) / self.sample_rate
            if duration < self.min_audio_length:
                raise ValueError(f"Áudio muito curto: {duration:.1f}s (mín: {self.min_audio_length}s)")
            
            if duration > self.max_audio_length:
                self.logger.warning(f"Áudio longo ({duration:.1f}s), cortando para {self.max_audio_length}s")
                audio = audio[:self.sample_rate * self.max_audio_length]
            
            # Salvar áudio processado
            processed_file = self.temp_dir / f"processed_{int(time.time())}.wav"
            sf.write(processed_file, audio, self.sample_rate)
            
            self.logger.info(f"✅ Áudio processado: duração {duration:.1f}s")
            return str(processed_file)
            
        except Exception as e:
            self.logger.error(f"❌ Erro no pré-processamento: {str(e)}")
            return None
    
    def clone_voice(self, audio_file: str, voice_name: str) -> bool:
        """
        Clona uma voz a partir de um arquivo de áudio.
        
        Args:
            audio_file: Caminho para o arquivo de áudio fonte
            voice_name: Nome para salvar a voz clonada
        
        Returns:
            True se clonagem bem-sucedida
        """
        try:
            self.logger.info(f"🎯 Iniciando clonagem da voz '{voice_name}'...")
            
            # Inicializar modelo se necessário
            if not self.tts:
                if not self.initialize_model():
                    return False
            
            # Pré-processar áudio
            processed_audio = self.preprocess_audio(audio_file)
            if not processed_audio:
                return False
            
            # Criar diretório da voz
            voice_dir = self.voices_dir / voice_name
            voice_dir.mkdir(exist_ok=True)
            
            # Copiar áudio processado para diretório da voz
            voice_audio = voice_dir / "reference.wav"
            os.rename(processed_audio, voice_audio)
            
            # Salvar metadados
            metadata = {
                "name": voice_name,
                "created_at": time.time(),
                "model_used": self.model_name,
                "sample_rate": self.sample_rate,
                "reference_file": "reference.wav"
            }
            
            with open(voice_dir / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Adicionar ao cache
            self.loaded_voices[voice_name] = {
                "path": str(voice_audio),
                "metadata": metadata
            }
            
            self.logger.info(f"✅ Voz '{voice_name}' clonada com sucesso!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na clonagem da voz: {str(e)}")
            return False
    
    def synthesize_with_cloned_voice(self, text: str, voice_name: str, 
                                   language: str = "pt-br") -> Optional[str]:
        """
        Sintetiza texto usando uma voz clonada.
        
        Args:
            text: Texto para sintetizar
            voice_name: Nome da voz clonada
            language: Código do idioma
        
        Returns:
            Caminho para o arquivo de áudio gerado
        """
        try:
            self.logger.info(f"🗣️ Sintetizando com voz '{voice_name}': '{text[:50]}...'")
            
            # Inicializar modelo se necessário
            if not self.tts:
                if not self.initialize_model():
                    return None
            
            # Verificar se voz existe
            if voice_name not in self.loaded_voices:
                if not self.load_voice(voice_name):
                    return None
            
            voice_info = self.loaded_voices[voice_name]
            reference_audio = voice_info["path"]
            
            # Gerar áudio
            output_file = self.temp_dir / f"synthesis_{voice_name}_{int(time.time())}.wav"
            
            self.tts.tts_to_file(
                text=text,
                file_path=str(output_file),
                speaker_wav=reference_audio,
                language=language
            )
            
            self.logger.info(f"✅ Síntese completa: {output_file}")
            return str(output_file)
            
        except Exception as e:
            self.logger.error(f"❌ Erro na síntese: {str(e)}")
            return None
    
    def load_voice(self, voice_name: str) -> bool:
        """
        Carrega uma voz clonada existente.
        
        Args:
            voice_name: Nome da voz a carregar
        
        Returns:
            True se carregada com sucesso
        """
        try:
            voice_dir = self.voices_dir / voice_name
            metadata_file = voice_dir / "metadata.json"
            
            if not metadata_file.exists():
                self.logger.error(f"Voz '{voice_name}' não encontrada")
                return False
            
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            reference_file = voice_dir / metadata["reference_file"]
            if not reference_file.exists():
                self.logger.error(f"Arquivo de referência não encontrado: {reference_file}")
                return False
            
            self.loaded_voices[voice_name] = {
                "path": str(reference_file),
                "metadata": metadata
            }
            
            self.logger.info(f"✅ Voz '{voice_name}' carregada")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar voz '{voice_name}': {str(e)}")
            return False
    
    def list_available_voices(self) -> List[str]:
        """
        Lista todas as vozes clonadas disponíveis.
        
        Returns:
            Lista com nomes das vozes
        """
        voices = []
        for voice_dir in self.voices_dir.iterdir():
            if voice_dir.is_dir() and (voice_dir / "metadata.json").exists():
                voices.append(voice_dir.name)
        
        return sorted(voices)
    
    def get_voice_info(self, voice_name: str) -> Optional[Dict]:
        """
        Obtém informações sobre uma voz.
        
        Args:
            voice_name: Nome da voz
        
        Returns:
            Dicionário com informações da voz
        """
        if voice_name in self.loaded_voices:
            return self.loaded_voices[voice_name]["metadata"]
        
        if self.load_voice(voice_name):
            return self.loaded_voices[voice_name]["metadata"]
        
        return None
    
    def delete_voice(self, voice_name: str) -> bool:
        """
        Remove uma voz clonada.
        
        Args:
            voice_name: Nome da voz a remover
        
        Returns:
            True se removida com sucesso
        """
        try:
            voice_dir = self.voices_dir / voice_name
            
            if not voice_dir.exists():
                self.logger.warning(f"Voz '{voice_name}' não encontrada")
                return False
            
            # Remover do cache se carregada
            if voice_name in self.loaded_voices:
                del self.loaded_voices[voice_name]
            
            # Remover diretório
            import shutil
            shutil.rmtree(voice_dir)
            
            self.logger.info(f"✅ Voz '{voice_name}' removida")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao remover voz '{voice_name}': {str(e)}")
            return False
    
    def get_supported_languages(self) -> List[str]:
        """
        Retorna lista de idiomas suportados pelo XTTS.
        
        Returns:
            Lista de códigos de idioma
        """
        return [
            "pt-br",  # Português Brasil
            "en",     # Inglês
            "es",     # Espanhol
            "fr",     # Francês
            "de",     # Alemão
            "it",     # Italiano
            "pt",     # Português Portugal
            "pl",     # Polonês
            "tr",     # Turco
            "ru",     # Russo
            "nl",     # Holandês
            "cs",     # Tcheco
            "ar",     # Árabe
            "zh-cn",  # Chinês
            "hu",     # Húngaro
            "ko",     # Coreano
            "ja"      # Japonês
        ]
    
    def test_voice_quality(self, voice_name: str) -> Dict:
        """
        Testa a qualidade de uma voz clonada.
        
        Args:
            voice_name: Nome da voz a testar
        
        Returns:
            Dicionário com métricas de qualidade
        """
        test_text = "Este é um teste da qualidade da voz clonada do ASTRA."
        
        try:
            # Sintetizar texto de teste
            start_time = time.time()
            audio_file = self.synthesize_with_cloned_voice(test_text, voice_name)
            synthesis_time = time.time() - start_time
            
            if not audio_file:
                return {"error": "Falha na síntese"}
            
            # Carregar áudio gerado para análise
            audio, sr = librosa.load(audio_file)
            
            # Métricas básicas
            duration = len(audio) / sr
            rms_energy = np.sqrt(np.mean(audio**2))
            
            # Limpeza
            os.remove(audio_file)
            
            return {
                "synthesis_time": round(synthesis_time, 2),
                "audio_duration": round(duration, 2),
                "rms_energy": round(rms_energy, 4),
                "quality_score": "good" if rms_energy > 0.01 else "low"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_temp_files(self):
        """Remove arquivos temporários antigos."""
        try:
            current_time = time.time()
            for temp_file in self.temp_dir.glob("*"):
                if temp_file.is_file():
                    # Remover arquivos com mais de 1 hora
                    if current_time - temp_file.stat().st_mtime > 3600:
                        temp_file.unlink()
                        
        except Exception as e:
            self.logger.warning(f"Erro na limpeza de arquivos temporários: {e}")


# Classe de conveniência para uso simples
class SimpleVoiceCloner:
    """
    Interface simplificada para clonagem de voz.
    """
    
    def __init__(self):
        self.xtts = XTTSVoiceCloning()
    
    def clone_from_file(self, audio_file: str, voice_name: str) -> bool:
        """
        Clona voz de um arquivo de áudio.
        
        Args:
            audio_file: Caminho do arquivo de áudio
            voice_name: Nome da voz
        
        Returns:
            True se sucesso
        """
        return self.xtts.clone_voice(audio_file, voice_name)
    
    def speak(self, text: str, voice_name: str, language: str = "pt-br") -> Optional[str]:
        """
        Fala texto com voz clonada.
        
        Args:
            text: Texto para falar
            voice_name: Nome da voz
            language: Idioma
        
        Returns:
            Caminho do arquivo de áudio
        """
        return self.xtts.synthesize_with_cloned_voice(text, voice_name, language)
    
    def list_voices(self) -> List[str]:
        """Lista vozes disponíveis."""
        return self.xtts.list_available_voices()


if __name__ == "__main__":
    # Exemplo de uso
    print("🎤 ASTRA - Sistema de Voice Cloning XTTS v2")
    print("========================================")
    
    # Criar instância
    cloner = SimpleVoiceCloner()
    
    # Listar vozes disponíveis
    voices = cloner.list_voices()
    print(f"Vozes disponíveis: {voices}")
    
    # Exemplo de uso (descomente para testar)
    # cloner.clone_from_file("minha_voz.wav", "ASTRA_voice")
    # audio_file = cloner.speak("Olá, esta é minha voz clonada!", "ASTRA_voice")
    # print(f"Áudio gerado: {audio_file}")
