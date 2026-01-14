# 🎵 Configuração Segura do ElevenLabs TTS

## ⚠️ **SEGURANÇA PRIMEIRO!**

**NUNCA partilhes a tua chave API publicamente!** A chave que partilhaste deve ser **REVOGADA IMEDIATAMENTE**.

## 🔒 **Passos de Segurança Urgentes:**

### 1. **Revogar Chave Atual**
- Vai para: https://elevenlabs.io/app/speech-synthesis
- Acede às configurações da conta
- Revoga a chave atual: `sk_6a518d15fe7f9b79fc58e94b08ec58701c5bcc3c3cb5a82a`
- Gera uma nova chave API

### 2. **Configuração Segura**

#### Opção A: Usando arquivo `.env` (Recomendado)
```bash
# Edita o arquivo: audio/.env
ELEVENLABS_API_KEY=SUA_NOVA_CHAVE_AQUI
```

#### Opção B: Usando variável de ambiente
```bash
# Windows (PowerShell)
$env:ELEVENLABS_API_KEY = "SUA_NOVA_CHAVE_AQUI"

# Windows (CMD)
set ELEVENLABS_API_KEY=SUA_NOVA_CHAVE_AQUI
```

## 🚀 **Teste da Configuração**

### 1. **Teste Básico**
```bash
python audio/elevenlabs_tts.py
```

### 2. **Teste Integrado**
```bash
python audio/enhanced_tts.py
```

### 3. **Configurador Completo**
```bash
python audio/tts_configurator.py
```

## ✅ **Verificação de Funcionamento**

O sistema deve mostrar:
- ✅ API key configurada
- ✅ ElevenLabs disponível
- ✅ X vozes encontradas
- ✅ Teste de TTS bem-sucedido

## 🎤 **Vozes ElevenLabs Disponíveis**

O sistema detectará automaticamente todas as vozes da tua conta ElevenLabs, incluindo:
- Vozes pré-definidas (Rachel, Adam, etc.)
- Vozes personalizadas
- Vozes clonadas
- Todas com naturalidade 10/10 ou superior

## 🎛️ **Configurações Avançadas**

No configurador (`python audio/tts_configurator.py`), podes ajustar:
- **Velocidade**: 0.5x - 2.0x
- **Volume**: 0% - 100%
- **Qualidade**: Modelo multilíngue v2
- **Configurações de voz**: Estabilidade, similaridade, etc.

## 💡 **Dicas de Uso**

1. **Economia de Créditos**: ElevenLabs cobra por caractere. Use com moderação.
2. **Qualidade**: Use modelo `eleven_multilingual_v2` para melhor qualidade.
3. **Cache**: O sistema salva configurações automaticamente.
4. **Fallback**: Se ElevenLabs falhar, o sistema usa Windows SAPI automaticamente.

## 🔧 **Resolução de Problemas**

### Erro "API key não configurada"
```bash
# Verifica se o arquivo .env existe
ls audio/.env

# Verifica o conteúdo (sem mostrar a chave)
head -n 1 audio/.env
```

### Erro "ElevenLabs não disponível"
- Verifica conexão com internet
- Confirma que a chave API está válida
- Verifica se tens créditos na conta

### Erro "Nenhuma voz encontrada"
- Verifica se tens vozes ativas na tua conta ElevenLabs
- Confirma permissões da API key

## 📞 **Suporte**

Se encontrares problemas:
1. Verifica os logs no terminal
2. Testa primeiro com `python audio/elevenlabs_tts.py`
3. Confirma que a nova chave API está funcionando no site da ElevenLabs

---

**Lembra-te**: Mantém sempre as tuas chaves API seguras e nunca as partilhes publicamente! 🔒