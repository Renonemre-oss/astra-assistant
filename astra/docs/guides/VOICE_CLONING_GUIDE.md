# 🎤 Guia de Voice Cloning para ASTRA

Este guia mostra como implementar voice cloning no seu assistente ASTRA usando múltiplas tecnologias.

## 🎯 Opções de Voice Cloning Disponíveis

### 1. **ElevenLabs (Já Integrado) - RECOMENDADO** ⭐
Sua instalação ASTRA já tem suporte ao ElevenLabs, que oferece voice cloning premium.

#### Configuração do ElevenLabs:
```powershell
# 1. Configurar chave API
$env:ELEVENLABS_API_KEY = "sua_chave_aqui"

# Ou criar arquivo .env no diretório audio/
echo "ELEVENLABS_API_KEY=sua_chave_aqui" > audio\.env
```

#### Como usar:
```python
# Testar ElevenLabs no ASTRA
python -c "
from audio.elevenlabs_tts import ElevenLabsTTS
tts = ElevenLabsTTS()
if tts.is_available():
    print('✅ ElevenLabs disponível!')
    voices = tts.get_voices()
    for voice in voices:
        print(f'🎵 {voice.name} ({voice.language}, {voice.gender})')
else:
    print('❌ Configure sua API key do ElevenLabs')
"
```

### 2. **Real-Time Voice Cloning (Instalado)**
Sistema open-source para clonagem de voz em tempo real.

#### Instalação das dependências:
```powershell
# Ir para o diretório do Real-Time Voice Cloning
cd ..\Real-Time-Voice-Cloning

# Instalar dependências (em ambiente virtual separado)
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Baixar modelos pré-treinados
# ATENÇÃO: Este download pode ser grande (varios GB)
python demo_cli.py
```

#### Como usar:
```powershell
# Executar interface de linha de comando
python demo_cli.py

# Ou interface gráfica
python demo_toolbox.py
```

### 3. **Coqui TTS com Voice Cloning**
Sua instalação ASTRA usa Coqui TTS que suporta voice cloning.

#### Atualizar para voice cloning:
```powershell
# Voltar ao diretório ASTRA
cd ..\ASTRA

# Ativar ambiente virtual do ASTRA
.venv_assistente\Scripts\Activate.ps1

# Instalar versão atualizada do Coqui TTS com voice cloning
pip install TTS[all] --upgrade
```

## 🔧 Integração com ASTRA

### Opção 1: ElevenLabs Voice Cloning (Mais Fácil)

1. **Obter chave API do ElevenLabs**:
   - Acesse https://elevenlabs.io
   - Crie uma conta
   - Vá para Profile > API Key

2. **Configurar no ASTRA**:
```powershell
# Criar arquivo de configuração
$configContent = @"
ELEVENLABS_API_KEY=sua_chave_api_aqui
"@
$configContent | Out-File -FilePath "audio\.env" -Encoding UTF8
```

3. **Testar integração**:
```powershell
python -c "
from audio.enhanced_tts import EnhancedTTS
tts = EnhancedTTS()
tts.auto_select_best_voice()
print('Voz atual:', tts.current_voice.description if tts.current_voice else 'Nenhuma')
"
```

### Opção 2: Integrar Real-Time Voice Cloning

Vou criar um módulo integrado para o ASTRA:

```python
# Arquivo: audio/voice_cloning.py
import sys
import os
from pathlib import Path
import logging

# Adicionar path do Real-Time Voice Cloning
rtvc_path = Path(__file__).parent.parent.parent / "Real-Time-Voice-Cloning"
sys.path.append(str(rtvc_path))

try:
    from encoder import inference as encoder
    from vocoder import inference as vocoder
    from synthesizer.inference import Synthesizer
    import librosa
    import numpy as np
    import soundfile as sf
    
    class RealTimeVoiceCloning:
        def __init__(self):
            self.encoder_model = None
            self.vocoder_model = None  
            self.synthesizer = None
            self.load_models()
        
        def load_models(self):
            # Carregar modelos pré-treinados
            encoder.load_model(rtvc_path / "encoder" / "saved_models" / "pretrained.pt")
            self.vocoder_model = vocoder.load_model(rtvc_path / "vocoder" / "saved_models" / "pretrained.pt")
            self.synthesizer = Synthesizer(rtvc_path / "synthesizer" / "saved_models" / "pretrained.pt")
        
        def clone_voice(self, audio_file: str, text: str, output_file: str = None):
            # Preprocessar áudio
            wav, sample_rate = librosa.load(audio_file, sr=None)
            
            # Gerar embedding da voz
            embed = encoder.embed_utterance(wav)
            
            # Sintetizar com a voz clonada
            specs = self.synthesizer.synthesize_spectrograms([text], [embed])
            spec = specs[0]
            
            # Gerar áudio final
            generated_wav = vocoder.infer_waveform(spec, target=self.vocoder_model)
            
            # Salvar se especificado
            if output_file:
                sf.write(output_file, generated_wav, 22050)
            
            return generated_wav

    VOICE_CLONING_AVAILABLE = True
    
except ImportError as e:
    logging.warning(f"Real-Time Voice Cloning não disponível: {e}")
    VOICE_CLONING_AVAILABLE = False
    RealTimeVoiceCloning = None
```

## 🎵 Como Usar Voice Cloning no ASTRA

### 1. Preparar Amostra de Voz
```powershell
# Gravar uma amostra de voz (10-30 segundos)
# Pode ser feito pelo próprio ASTRA ou externamente

# Exemplo de script para gravar
python -c "
import sounddevice as sd
import soundfile as sf
import numpy as np

print('Pressione Enter e fale por 15 segundos...')
input()
print('Gravando...')

duration = 15  # segundos
sample_rate = 22050
audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
sd.wait()

sf.write('minha_voz.wav', audio, sample_rate)
print('✅ Gravação salva como minha_voz.wav')
"
```

### 2. Clonar e Usar no ASTRA

#### Com ElevenLabs:
```python
# No código do ASTRA (audio/enhanced_tts.py)
# ElevenLabs permite upload de voice samples via API
# Implementar método de clonagem:

def clone_voice_elevenlabs(self, name: str, audio_files: list, description: str = ""):
    """Clona voz usando ElevenLabs."""
    # Upload voice samples para ElevenLabs
    # Retorna voice_id da voz clonada
    pass
```

#### Com Real-Time Voice Cloning:
```python
# Usar módulo integrado
from audio.voice_cloning import RealTimeVoiceCloning

cloner = RealTimeVoiceCloning()
cloned_audio = cloner.clone_voice(
    audio_file="minha_voz.wav",
    text="Olá, eu sou o ASTRA com sua voz!",
    output_file="resultado_clonado.wav"
)
```

## 🚀 Comandos de Instalação Rápida

### Configuração Completa:
```powershell
# 1. Ativar ambiente do ASTRA
.venv_assistente\Scripts\Activate.ps1

# 2. Atualizar TTS para suporte de clonagem
pip install TTS[all] --upgrade
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# 3. Instalar dependências de áudio
pip install sounddevice soundfile librosa

# 4. Testar sistema atual
python run_ASTRA.py

# 5. Configurar ElevenLabs (se tiver API key)
# Editar audio/.env ou definir variável de ambiente
```

### Teste Rápido:
```powershell
# Testar TTS atual do ASTRA
python -c "
from audio.audio_manager import AudioManager
audio = AudioManager()
if audio.load_tts_model():
    audio.text_to_speech('Olá! Este é um teste do sistema TTS do ASTRA.')
    print('✅ TTS funcionando')
else:
    print('❌ TTS com problema')
"
```

## 📊 Comparação das Opções

| Método | Qualidade | Facilidade | Custo | Offline |
|--------|-----------|------------|-------|---------|
| **ElevenLabs** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 💰 Pago | ❌ |
| **Real-Time Voice Cloning** | ⭐⭐⭐⭐ | ⭐⭐⭐ | 🆓 Grátis | ✅ |
| **Coqui TTS** | ⭐⭐⭐ | ⭐⭐⭐⭐ | 🆓 Grátis | ✅ |

## 🔍 Troubleshooting

### Problemas Comuns:

1. **"ModuleNotFoundError" no Real-Time Voice Cloning**:
```powershell
# Instalar dependências em separado
cd ..\Real-Time-Voice-Cloning
pip install torch torchvision torchaudio
pip install -r requirements.txt
```

2. **Erro de CUDA/GPU**:
```powershell
# Usar CPU apenas
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

3. **ElevenLabs API não funciona**:
```powershell
# Verificar chave API
python -c "
import os
print('API Key:', os.getenv('ELEVENLABS_API_KEY', 'NÃO CONFIGURADA'))
"
```

## 🎯 Próximos Passos

1. **Escolher método preferido** (ElevenLabs recomendado para iniciantes)
2. **Configurar chaves API** (se usando ElevenLabs)
3. **Testar com amostras de voz**
4. **Integrar com interface do ASTRA**
5. **Criar vozes personalizadas** para diferentes usuários

## 📞 Suporte

Para problemas específicos:
- Consulte logs em `logs/ASTRA_assistant.log`
- Execute `python run_ASTRA.py test` para diagnósticos
- Verifique documentação em `docs/`

---

**Desenvolvido para ASTRA - Assistente Pessoal Inteligente** 🤖
