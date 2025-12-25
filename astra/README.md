## 🤖 ALEX - Assistente Pessoal Inteligente

![ALEX Logo](assets/logos/alex_logo_main.png)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)
![TTS](https://img.shields.io/badge/TTS-Coqui-orange.svg)
![MySQL](https://img.shields.io/badge/Database-MySQL-blue.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

## 📋 Sobre

O ALEX é um assistente virtual inteligente desenvolvido em Python com interface gráfica, que combina processamento de linguagem natural, síntese de voz, reconhecimento de fala e integração com base de dados. Projetado para ser um assistente pessoal completo com funcionalidades avançadas de personalização e memória.

## ✨ Funcionalidades

### 🎯 **Core Features**
- 🗣️ **Text-to-Speech (TTS)** - Síntese de voz em português
- 🎤 **Reconhecimento de Voz** - Entrada por comando de voz
- 🧠 **IA Conversacional** - Integração com Ollama para respostas inteligentes
- 💾 **Sistema de Memória** - Armazena informações pessoais e preferências
- 👥 **Gestão de Pessoas** - Sistema de reconhecimento e armazenamento de informações sobre pessoas

### 🎨 **Interface**
- 🖥️ **Interface Gráfica Moderna** - Desenvolvida em PyQt6
- 🌊 **Fundo Animado** - Animações fluidas com CSS/HTML5
- 📱 **Interface Responsiva** - Adaptável a diferentes tamanhos de tela

### 🔧 **Tecnologias**
- 🐍 **Python 3.8+** - Linguagem principal
- 🎭 **PyQt6** - Interface gráfica
- 🔊 **Coqui TTS** - Síntese de voz
- 🎙️ **SpeechRecognition** - Reconhecimento de fala
- 🗄️ **MySQL** - Base de dados
- 🧠 **Ollama** - Modelo de linguagem local
- 📊 **Scikit-learn** - Machine learning para classificação de intenções
- 🎨 **PIL/Pillow** - Processamento de imagens para logos

### 🎨 **Sistema de Assets**
- 🖼️ **Logo Principal** - Versão quadrada alta resolução (512x512)
- 📱 **Logo Horizontal** - Para interfaces largas (800x300)
- 🌐 **Favicon** - Ícone pequeno para web (64x64)
- 💻 **Ícone da Aplicação** - Para sistema operacional (256x256)
- 📋 **Formatos Suportados** - PNG, ICO, SVG
- 🔧 **Asset Manager** - Sistema automatizado de gestão de recursos

## 🏗️ Estrutura do Projeto

```
ALEX/
├── 📁 assets/               # Sistema de recursos visuais
│   ├── 📁 logos/           # Logos principais
│   ├── 📁 icons/           # Ícones da aplicação
│   ├── 📁 favicons/        # Favicons para web
│   └── assets_registry.json # Registro de assets
├── 📁 audio/                # Gestão de áudio (TTS, reprodução)
│   └── audio_manager.py
├── 📁 config/              # Configurações centralizadas
│   ├── config.py
│   └── __init__.py
├── 📁 core/                # Núcleo da aplicação
│   └── assistente.py
├── 📁 database/            # Sistema de base de dados
│   └── database_manager.py
├── 📁 docs/                # Documentação
│   ├── logo_showcase.html  # Showcse dos logos
│   └── logging_system.md
├── 📁 logs/                # Arquivos de log
├── 📁 modules/             # Módulos funcionais
│   ├── contextual_analyzer.py
│   ├── multi_user_manager.py
│   ├── people_manager.py
│   ├── personal_profile.py
│   └── user_commands.py
├── 📁 neural_models/       # Modelos de IA
│   └── modelo.py
├── 📁 scripts/             # Scripts utilitários
│   ├── cleanup.py
│   ├── generate_logos.py   # Gerador de logos
│   └── setup_database.py
├── 📁 tests/               # Testes do sistema
├── 📁 ui/                  # Componentes de interface
│   ├── profile_manager_ui.py
│   └── splash_screen.py
├── 📁 utils/               # Utilitários diversos
│   ├── asset_manager.py    # Gestor de assets
│   ├── text_processor.py
│   └── utils.py
├── 📄 run_alex.py          # Launcher principal
└── 📄 requirements.txt     # Dependências
```

## 🚀 Instalação

### 📋 Pré-requisitos

- Python 3.8 ou superior
- SQLite (incluído com Python)
- Ollama (para funcionalidades de IA)

### 🔧 Passos de Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/Renonemre-oss/ALEX.git
cd ALEX
```

2. **Crie um ambiente virtual:**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure a base de dados (opcional):**
```bash
python scripts/setup_database.py
```

5. **Execute o ALEX:**
```bash
python run_alex.py
```

## ⚙️ Configuração

### 🗄️ Base de Dados SQLite

O ALEX usa SQLite por padrão. Para personalizar, crie um arquivo `database.ini` na pasta `config/`:

```ini
[sqlite]
database_path = alex_assistant.db

# Configurações adicionais
check_same_thread = false
timeout = 30.0
foreign_keys = true
```

### 🤖 Ollama

1. Instale o Ollama: https://ollama.ai
2. Baixe um modelo (recomendado: llama3.2 ou mistral)
```bash
ollama pull llama3.2
```

## 🎮 Como Usar

### 🚀 **Launcher Principal**
```bash
python run_alex.py           # Executar o assistente
python run_alex.py test      # Executar testes
python run_alex.py struct    # Mostrar estrutura
python run_alex.py clean     # Limpar arquivos desnecessários
python run_alex.py help      # Mostrar ajuda
```

### 💬 **Comandos de Voz/Texto**
- "Olá" - Cumprimentar o assistente
- "Como te chamas?" - Perguntar o nome
- "Meu nome é..." - Definir seu nome
- "Qual é minha comida favorita?" - Consultar preferências
- "Minha cor favorita é azul" - Definir preferências
- "Quem é Maria?" - Consultar informações sobre pessoas

### 🎛️ **Interface Gráfica**
- **Caixa de texto** - Digite suas mensagens
- **Botão microfone (🎙️)** - Ativar reconhecimento de voz
- **Botão imagem (🖼️)** - Processar imagens (OCR)
- **Botão enviar (📤)** - Enviar mensagem
- **Botão parar (🚫)** - Interromper processamento

### 🎨 **Visualizar Logos**
```bash
# Gerar novos logos
python scripts/generate_logos.py

# Ver showcase dos logos no navegador
start docs/logo_showcase.html
# ou
open docs/logo_showcase.html  # Linux/Mac
```

## 📊 Sistema de Logging

O ALEX possui um sistema de logging centralizado que registra todas as atividades:

- **Localização:** `logs/alex_assistant.log`
- **Formato:** UTF-8 com suporte a emojis
- **Níveis:** DEBUG, INFO, WARNING, ERROR, CRITICAL

Consulte `docs/logging_system.md` para mais detalhes.

## 🧪 Testes

Execute os testes do sistema:

```bash
python run_alex.py test
```

Testes individuais:
```bash
python tests/test_multi_user_system.py
python tests/test_contextual_integration.py
```

## 🛠️ Desenvolvimento

### 📁 **Adicionando Novos Módulos**

1. Crie o arquivo na pasta apropriada (`modules/`, `utils/`, etc.)
2. Adicione as importações necessárias
3. Documente as funções seguindo o padrão existente
4. Adicione testes em `tests/`

### 🔄 **Sistema de Intenções**

O ALEX usa machine learning para classificar intenções do usuário:
- Treinado com scikit-learn
- Armazenado em `neural_models/modelo.pkl`
- Fallback para Ollama em baixa confiança

## 🐛 Troubleshooting

### ❌ **Problemas Comuns**

**TTS não funciona:**
- Verifique se o `coqui-tts` está instalado
- Teste a conexão de internet (download do modelo)

**Base de dados não conecta:**
- Verifique as configurações em `mysql_config.ini`
- Confirme se o MySQL está rodando

**Reconhecimento de voz não funciona:**
- Verifique o microfone
- Instale `pyaudio`: `pip install pyaudio`

**Ollama não responde:**
- Verifique se o Ollama está executando
- Teste: `ollama list`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**António Pereira** - [Renonemre-oss](https://github.com/Renonemre-oss)

## 🙏 Agradecimentos

- Comunidade Open Source
- Desenvolvedores do Coqui TTS
- Equipe do Ollama
- Contribuidores do PyQt6

---

⭐ **Se este projeto foi útil para você, considere dar uma estrela!**

📧 **Dúvidas?** Abra uma [issue](https://github.com/Renonemre-oss/ALEX/issues) ou entre em contato!

🚀 **Happy coding!**