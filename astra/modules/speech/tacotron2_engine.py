#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Tacotron 2 Engine
Implementação do modelo Tacotron 2 da NVIDIA para síntese de voz de alta qualidade
"""

import os
import sys
import logging
import threading
import time
from pathlib import Path
from typing import Optional, List, Dict, Callable, Any
import json
import tempfile
import warnings

# Configurar logger
logger = logging.getLogger(__name__)

class Tacotron2Engine:
    """Engine de TTS usando Tacotron 2 da NVIDIA."""
    
    def __init__(self, status_callback: Optional[Callable[[str], None]] = None):
        """
        Inicializa o engine Tacotron 2.
        
        Args:
            status_callback: Função para receber atualizações de status
        """
        self.status_callback = status_callback
        self.model = None
        self.vocoder = None
        self.model_loaded = False
        self.sample_rate = 22050
        
        # Diretório temporário para áudios gerados
        self.temp_dir = Path(tempfile.gettempdir()) / "ASTRA_tacotron2"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Cache do último áudio gerado
        self.last_audio_path = None
        
    def set_status(self, message: str):
        """Atualiza status."""
        if self.status_callback:
            self.status_callback(message)
        logger.info(f"Tacotron2: {message}")
    
    def load_model(self) -> bool:
        """Carrega os modelos Tacotron 2 e WaveGlow do PyTorch Hub."""
        if self.model_loaded:
            return True
        
        try:
            self.set_status("🤖 Carregando Tacotron 2 da NVIDIA...")
            
            import torch
            import numpy as np
            
            # Suprimir warnings do modelo
            warnings.filterwarnings('ignore')
            
            # Definir device (forçar CPU)
            device = torch.device('cpu')
            
            # Carregar Tacotron 2
            self.set_status("📦 Baixando modelo Tacotron 2...")
            self.model = torch.hub.load(
                'NVIDIA/DeepLearningExamples:torchhub', 
                'nvidia_tacotron2',
                pretrained=True,
                map_location=device
            )
            self.model.to(device)
            self.model.eval()
            
            # Carregar WaveGlow (vocoder)
            self.set_status("📦 Baixando modelo WaveGlow...")
            self.vocoder = torch.hub.load(
                'NVIDIA/DeepLearningExamples:torchhub', 
                'nvidia_waveglow',
                pretrained=True,
                map_location=device
            )
            self.vocoder.to(device)
            self.vocoder.eval()
            
            # Otimizar para inferência
            if hasattr(self.vocoder, 'infer'):
                # Remover weightnorm para performance
                try:
                    self.vocoder = torch.jit.script(self.vocoder)
                except Exception as e:
                    logger.warning(f"Não foi possível otimizar vocoder: {e}")
            
            self.model_loaded = True
            self.set_status("✅ Tacotron 2 + WaveGlow carregados com sucesso!")
            
            return True
            
        except Exception as e:
            self.set_status(f"❌ Erro ao carregar Tacotron 2: {str(e)[:100]}...")
            logger.error(f"Erro ao carregar Tacotron 2: {e}")
            return False
    
    def text_to_speech(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Converte texto para fala usando Tacotron 2.
        
        Args:
            text: Texto a ser sintetizado
            output_path: Caminho de saída (opcional)
            
        Returns:
            str: Caminho do arquivo de áudio gerado ou None se erro
        """
        if not self.model_loaded:
            if not self.load_model():
                return None
        
        if not text or not text.strip():
            return None
        
        try:
            self.set_status(f"🎙️ Sintetizando: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            import torch
            import torchaudio
            import numpy as np
            
            # Limpar texto
            clean_text = self._clean_text(text)
            
            # Preparar sequência de entrada
            sequence = self._text_to_sequence(clean_text)
            
            # Gerar mel spectrogram usando Tacotron 2
            with torch.no_grad():
                mel_outputs, mel_outputs_postnet, _, alignments = self.model.inference(sequence)
            
            # Gerar áudio usando WaveGlow
            with torch.no_grad():
                audio = self.vocoder.infer(mel_outputs_postnet)
                audio = audio[0].data.cpu().numpy()
            
            # Normalizar áudio
            audio = audio / np.max(np.abs(audio))
            
            # Definir caminho de saída
            if not output_path:
                timestamp = int(time.time())
                output_path = self.temp_dir / f"tacotron2_output_{timestamp}.wav"
            else:
                output_path = Path(output_path)
            
            # Salvar áudio
            audio_tensor = torch.from_numpy(audio).float().unsqueeze(0)
            torchaudio.save(str(output_path), audio_tensor, self.sample_rate)
            
            self.last_audio_path = str(output_path)
            self.set_status(f"✅ Áudio gerado: {output_path.name}")
            
            return str(output_path)
            
        except Exception as e:
            self.set_status(f"❌ Erro na síntese: {str(e)[:100]}...")
            logger.error(f"Erro na síntese Tacotron 2: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Limpa e prepara texto para o Tacotron 2."""
        import re
        
        # Remover caracteres especiais problemáticos
        text = re.sub(r'[^\w\s\.,!?;:\-]', '', text)
        
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text)
        
        # Limitar tamanho (Tacotron 2 tem limite de sequência)
        if len(text) > 200:
            text = text[:200] + "."
        
        return text.strip()
    
    def _text_to_sequence(self, text: str):
        """Converte texto para sequência numérica."""
        import torch
        
        try:
            # Usar o utils do Tacotron 2 se disponível
            from tacotron2_common.text import text_to_sequence
            sequence = text_to_sequence(text, ['english_cleaners'])
            return torch.IntTensor(sequence)[None, :].long()
            
        except ImportError:
            # Implementação simples se não tiver os utils
            # Mapear caracteres para números (alfabeto básico)
            char_to_idx = {char: idx for idx, char in enumerate(' abcdefghijklmnopqrstuvwxyz.,!?;:-')}
            
            sequence = []
            for char in text.lower():
                if char in char_to_idx:
                    sequence.append(char_to_idx[char])
                else:
                    sequence.append(0)  # Espaço para caracteres desconhecidos
            
            return torch.IntTensor(sequence)[None, :].long()
    
    def play_audio(self, audio_path: str) -> bool:
        """
        Reproduz arquivo de áudio usando o sistema.
        
        Args:
            audio_path: Caminho do arquivo de áudio
            
        Returns:
            bool: True se reproduzido com sucesso
        """
        try:
            import os
            import subprocess
            import platform
            
            if not Path(audio_path).exists():
                return False
            
            system = platform.system().lower()
            
            if system == "windows":
                # Windows: usar comando start
                os.startfile(audio_path)
            elif system == "darwin":  # macOS
                subprocess.run(["open", audio_path])
            else:  # Linux
                subprocess.run(["xdg-open", audio_path])
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao reproduzir áudio: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtém informações do modelo."""
        return {
            'model_name': 'NVIDIA Tacotron 2',
            'vocoder': 'NVIDIA WaveGlow',
            'sample_rate': self.sample_rate,
            'model_loaded': self.model_loaded,
            'quality': 'high',
            'language': 'en-US',
            'last_audio': self.last_audio_path
        }
    
    def cleanup_temp_files(self):
        """Limpa arquivos temporários antigos."""
        try:
            import time
            current_time = time.time()
            
            for file_path in self.temp_dir.glob("tacotron2_output_*.wav"):
                # Remover arquivos mais antigos que 1 hora
                if current_time - file_path.stat().st_mtime > 3600:
                    file_path.unlink()
                    
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos temporários: {e}")

def test_tacotron2():
    """Função de teste do Tacotron 2."""
    print("🤖 Testando NVIDIA Tacotron 2")
    print("=" * 40)
    
    def status_print(msg):
        print(f"  {msg}")
    
    # Criar engine
    engine = Tacotron2Engine(status_callback=status_print)
    
    # Obter informações
    info = engine.get_model_info()
    print(f"\n📊 Informações do Modelo:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Teste de síntese
    print(f"\n🎙️ Teste de Síntese:")
    test_text = "Hello, this is a high quality text to speech synthesis using NVIDIA Tacotron 2."
    
    try:
        audio_path = engine.text_to_speech(test_text)
        
        if audio_path:
            print(f"✅ Áudio gerado com sucesso: {audio_path}")
            
            # Tentar reproduzir
            print("🔊 Tentando reproduzir áudio...")
            if engine.play_audio(audio_path):
                print("✅ Áudio reproduzido")
            else:
                print("⚠️  Não foi possível reproduzir automaticamente")
                print(f"   Arquivo salvo em: {audio_path}")
        else:
            print("❌ Falha na geração de áudio")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
    
    return engine

if __name__ == "__main__":
    test_tacotron2()
