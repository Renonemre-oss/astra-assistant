# 🎨 JARVIS - Sistema de Visualização de Áudio

## 📋 Resumo

O sistema de visualização de áudio do Jarvis usa **Manim** para criar animações em tempo real que reagem às vibrações sonoras durante o modo de escuta. Quando o Jarvis está ouvindo por wake words, em vez de apenas mostrar texto, ele exibe animações visuais dinâmicas que respondem ao áudio captado pelo microfone.

## ✨ Funcionalidades Principais

### 🎵 **Visualização em Tempo Real**
- Captura áudio do microfone em tempo real
- Análise de amplitude e frequência (FFT)
- Animações a 60 FPS que reagem ao som
- Múltiplos modos de visualização

### 🎨 **Modos de Visualização**
1. **PULSE** - Pulsação central que varia com amplitude
2. **WAVEFORM** - Forma de onda em tempo real  
3. **SPECTRUM** - Espectro de frequência com picos
4. **CIRCLE_WAVE** - Onda circular rotatória
5. **BARS** - Barras de frequência (equalizer)
6. **PARTICLES** - Sistema de partículas reativo

### 🔗 **Integração com Hotword Detection**
- Ativa automaticamente durante escuta
- Feedback visual especial quando wake word é detectado
- Não interfere com performance do reconhecimento de voz
- Modos visuais configuráveis

## 🚀 Como Usar

### **Instalação Rápida**

O sistema já está configurado no projeto Jarvis. Apenas certifique-se de que o Manim está instalado:

```bash
pip install manim
```

### **Uso Básico - AudioVisualizer**

```python
from modules.audio_visualizer import create_audio_visualizer, VisualizationMode

def on_status(message):
    print(f"Status: {message}")

# Criar visualizador
visualizer = create_audio_visualizer(on_status, VisualizationMode.PULSE)

# Iniciar visualização
visualizer.start()

# Falar no microfone - verá as animações!

# Parar quando terminar
visualizer.stop()
```

### **Uso Integrado - VisualHotwordDetector**

```python
from modules.visual_hotword_detector import create_visual_hotword_detector, VisualMode

def on_status(message):
    print(f"Status: {message}")
    
def on_detection(word):
    print(f"Wake word detectado: {word}")

# Criar detector visual integrado
detector = create_visual_hotword_detector(
    status_callback=on_status,
    visual_mode=VisualMode.LISTENING_ONLY,  # Anima só durante escuta
    visualization_mode=VisualizationMode.PULSE
)

# Configurar callback de detecção
detector.set_detection_callback(on_detection)

# Iniciar escuta com visualização
detector.start_listening()

# Dizer "Jarvis" ou "Alex" - verá animação + detecção!
```

## ⚙️ Configurações Avançadas

### **Modos Visuais (VisualMode)**

```python
# Sem visualização
detector.set_visual_mode(VisualMode.OFF)

# Apenas durante escuta (padrão)
detector.set_visual_mode(VisualMode.LISTENING_ONLY)

# Sempre ativo
detector.set_visual_mode(VisualMode.ALWAYS)

# Reativo ao áudio
detector.set_visual_mode(VisualMode.REACTIVE)
```

### **Personalizar Visualização**

```python
# Alterar modo de visualização
detector.set_visualization_mode(VisualizationMode.PARTICLES)

# Ajustar sensibilidade (0.1 a 5.0)
detector.set_sensitivity(2.0)

# Cores personalizadas (tema Matrix/Jarvis)
colors = ["#00ff41", "#41ff00", "#00ffff", "#0080ff", "#ffffff"]
detector.set_colors(colors)
```

### **Configurar Wake Words**

```python
# Adicionar nova wake word
detector.add_wake_word("hey jarvis")
detector.add_wake_word("computer")

# Remover wake word
detector.remove_wake_word("alex")
```

## 📊 Modos de Visualização Detalhados

### **1. PULSE (Pulsação)**
- **Descrição**: Círculo central que pulsa conforme amplitude
- **Reativo a**: Volume do áudio
- **Efeito**: Tamanho varia com intensidade sonora
- **Melhor para**: Feedback geral de áudio

### **2. WAVEFORM (Forma de Onda)**
- **Descrição**: Ondas que mostram forma do áudio
- **Reativo a**: Amplitude temporal
- **Efeito**: Linha ondulante em movimento
- **Melhor para**: Visualizar padrões de fala

### **3. SPECTRUM (Espectro)**
- **Descrição**: Análise de frequências em tempo real
- **Reativo a**: Diferentes frequências
- **Efeito**: Picos coloridos por frequência
- **Melhor para**: Analisar tons e timbres

### **4. CIRCLE_WAVE (Onda Circular)**
- **Descrição**: Onda que gira em círculo
- **Reativo a**: Amplitude + frequências
- **Efeito**: Rotação varia com áudio
- **Melhor para**: Visual dinâmico e hipnótico

### **5. BARS (Barras)**
- **Descrição**: Equalizer com barras verticais
- **Reativo a**: Bandas de frequência
- **Efeito**: 20 barras dancantes
- **Melhor para**: Visualização clássica

### **6. PARTICLES (Partículas)**
- **Descrição**: Sistema de partículas explosivas
- **Reativo a**: Volume gera novas partículas
- **Efeito**: Explosões coloridas
- **Melhor para**: Efeito visual dramático

## 🎯 Integração no Projeto Jarvis

### **Modificar Launcher Existente**

Para integrar no launcher principal do Jarvis, edite o arquivo de launcher:

```python
# No início do arquivo
from modules.visual_hotword_detector import create_visual_hotword_detector, VisualMode

# Substituir hotword detector normal
# detector = HotwordDetector(status_callback)
detector = create_visual_hotword_detector(
    status_callback=status_callback,
    visual_mode=VisualMode.LISTENING_ONLY
)
```

### **Configurar na Interface GUI**

```python
# Adicionar controles visuais na interface
def setup_visual_controls():
    # Botões para trocar modo visual
    pulse_btn = Button("Pulso", command=lambda: set_visual_mode("pulse"))
    bars_btn = Button("Barras", command=lambda: set_visual_mode("bars"))
    
    # Slider de sensibilidade
    sensitivity_scale = Scale(from_=0.1, to=5.0, command=set_sensitivity)
    
def set_visual_mode(mode):
    if mode == "pulse":
        detector.set_visualization_mode(VisualizationMode.PULSE)
    elif mode == "bars":
        detector.set_visualization_mode(VisualizationMode.BARS)
```

## 🔧 Resolução de Problemas

### **Manim Não Instalado**

```
⚠️ Manim não está disponível. Visualização desabilitada.
```

**Solução:**
```bash
pip install manim
```

### **Problemas de Áudio**

```
❌ Erro ao iniciar: [Errno -9998] Invalid number of channels
```

**Solução:**
- Verificar se microfone está conectado
- Tentar reiniciar o programa
- Verificar configurações de áudio do sistema

### **Performance Lenta**

```
Visualização travando ou com lag
```

**Solução:**
```python
# Reduzir sensibilidade
detector.set_sensitivity(0.5)

# Usar modo mais simples
detector.set_visualization_mode(VisualizationMode.PULSE)
```

### **Importação de Módulos**

```
❌ Módulos não disponíveis. Verifique as importações.
```

**Solução:**
- Verificar se todos os arquivos estão no lugar correto
- Verificar paths no PYTHONPATH
- Executar do diretório raiz do projeto

## 📈 Performance e Otimizações

### **Configurações de Performance**

```python
# AudioVisualizer configurações otimizadas
visualizer.sample_rate = 22050  # Reduzir de 44100
visualizer.chunk_size = 512     # Reduzir de 1024
visualizer.sensitivity = 1.0    # Valor balanceado
```

### **Monitoramento de Recursos**

```python
# Verificar status do sistema
status = detector.get_status_info()
print(f"CPU: {status['visualizer']['is_active']}")
print(f"Amplitude: {status['visualizer']['current_amplitude']}")
```

## 🎨 Personalização Avançada

### **Criar Tema Personalizado**

```python
# Tema Sci-Fi
sci_fi_colors = ["#00ffff", "#0080ff", "#8000ff", "#ff0080", "#ff8000"]

# Tema Matrix
matrix_colors = ["#00ff41", "#41ff00", "#008f11", "#004411"]

# Tema Fogo
fire_colors = ["#ff4500", "#ff6347", "#ffff00", "#ffa500"]

detector.set_colors(matrix_colors)
```

### **Configuração Completa Personalizada**

```python
def setup_custom_jarvis_visual():
    detector = create_visual_hotword_detector()
    
    # Configurações visuais
    detector.set_visual_mode(VisualMode.LISTENING_ONLY)
    detector.set_visualization_mode(VisualizationMode.CIRCLE_WAVE)
    detector.set_sensitivity(1.8)
    
    # Cores tema Jarvis
    jarvis_colors = ["#00ff41", "#41ff00", "#00ffff", "#ffffff"]
    detector.set_colors(jarvis_colors)
    
    # Wake words personalizadas
    detector.add_wake_word("jarvis")
    detector.add_wake_word("alex")
    detector.add_wake_word("computer")
    detector.add_wake_word("assistant")
    
    return detector
```

## 📝 Exemplos de Uso

### **Exemplo 1: Teste Rápido**

```python
python modules/audio_visualizer.py
```

### **Exemplo 2: Sistema Integrado**

```python
python modules/visual_hotword_detector.py
```

### **Exemplo 3: Personalizado**

```python
from modules.visual_hotword_detector import *

detector = create_visual_hotword_detector()
detector.set_visualization_mode(VisualizationMode.PARTICLES)
detector.set_sensitivity(2.5)

detector.start_listening()
# Falar "Jarvis" e ver explosão de partículas!
```

## 🔮 Implementações Futuras

### **Renderização Real com Manim**
- Atualmente o sistema simula as visualizações
- Implementação futura: renderização real com Manim Scene
- OpenGL para performance em tempo real

### **Modos Visuais Avançados**
- **3D VISUALIZATION**: Visualização tridimensional
- **INTERACTIVE**: Responde a comandos específicos
- **AMBIENT**: Modo ambiente suave
- **REACTIVE_SPEECH**: Reage diferente para fala vs outros sons

### **Integração com IA**
- Visualizações que mudam baseadas no contexto
- Cores que refletem humor do assistente
- Animações específicas para diferentes tipos de resposta

---

## 📞 Suporte

Para dúvidas ou problemas:

1. **Teste básico**: Execute `python modules/audio_visualizer.py`
2. **Verifique logs**: Observe mensagens de erro no console
3. **Configurações**: Ajuste sensibilidade e modo conforme necessário
4. **Performance**: Use modos mais simples se houver lag

---

**🎯 Status**: ✅ Funcional e integrado  
**🔄 Última atualização**: 02/10/2025  
**👨‍💻 Desenvolvido para**: Projeto Jarvis

**🎨 Experimente diferentes modos e descubra qual visualização mais combina com seu estilo de uso do Jarvis!** ✨