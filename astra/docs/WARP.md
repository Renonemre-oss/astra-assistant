# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

ASTRA is an intelligent Portuguese-language voice assistant with advanced multi-user recognition, contextual analysis, and modular architecture. Built with PyQt6, the system features sophisticated user identification, machine learning intent classification, and comprehensive database integration with MySQL fallback.

### Key Features
- **Multi-User System** with voice pattern recognition and contextual analysis
- **Advanced Contextual Analysis** including emotion detection, topic analysis, and behavioral patterns
- **Hybrid Database Architecture** with MySQL primary + JSON fallback
- **Modular Design** with separate concerns for audio, database, neural models, and UI
- **Voice Recognition & TTS** with Portuguese language support
- **Machine Learning Intent Classification** with Ollama LLM integration
- **People Management System** with relationship tracking
- **Personal Profile System** with preference learning

## Architecture

### High-Level Architecture

The system follows a **modular, service-oriented architecture** with clean separation of concerns:

```
┌─────────────────────┐
│   User Interface    │  PyQt6 GUI with animated background
│   (core/assistente) │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│   Core Services     │
├─────────────────────┤
│ • Audio Manager     │  TTS, Speech Recognition, Audio Processing
│ • Multi-User Mgr    │  User identification, context switching
│ • Context Analyzer  │  Behavioral analysis, emotion detection
│ • People Manager    │  Relationship tracking, personal data
│ • Personal Profile  │  User preferences, learning
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│   Data Layer        │
├─────────────────────┤
│ • Database Manager  │  MySQL with JSON fallback
│ • Neural Models     │  ML intent classification
│ • Configuration     │  Centralized config management
└─────────────────────┘
```

### Core Components

1. **Multi-User System** (`modules/multi_user_manager.py`)
   - Voice pattern recognition with librosa + Gaussian Mixture Models
   - Text pattern analysis (vocabulary, phrases, punctuation style)
   - Contextual clues analysis (personal references, behavioral patterns)
   - Auto-identification parsing ("eu sou...", "chamo-me...")
   - User switching and profile management

2. **Contextual Analyzer** (`modules/contextual_analyzer.py`)
   - Topic detection (trabalho, família, entretenimento, desporto, saúde, tecnologia)
   - Emotion analysis (alegria, tristeza, raiva, stress, surpresa)
   - Formality level detection (formal, informal, muito_informal)
   - Temporal pattern analysis (time/day preferences)
   - Behavioral indicator tracking

3. **Database Architecture** (`database/database_manager.py`)
   - **Primary**: MySQL with full relational schema
   - **Fallback**: JSON file storage for offline operation
   - **Tables**: conversations, messages, voice_interactions, user_preferences, people
   - **Features**: UTF-8 support, automatic schema creation, session management

4. **Audio Management** (`audio/audio_manager.py`)
   - TTS with Coqui-TTS Portuguese models (`tts_models/pt/cv/vits`)
   - Speech recognition with Google Speech API
   - Audio processing with threading for UI responsiveness
   - Voice sample recording and analysis

### Data Flow Architecture

```
User Input (Voice/Text)
        ↓
Multi-User Identification:
├── Voice Pattern Analysis (80% weight)
├── Text Pattern Analysis (40% weight) 
├── Contextual Analysis (60% weight)
├── Auto-identification (80% weight)
└── Conversation Continuity (20% weight)
        ↓
Contextual Analysis:
├── Topic Detection
├── Emotion Analysis 
├── Formality Assessment
├── Temporal Patterns
└── Behavioral Indicators
        ↓
Intent Classification (Neural Models)
        ↓
Action Routing:
├── Direct Response (known intents)
├── Ollama LLM (unknown intents)
├── Database Operations
├── People Management
└── Web Search (DuckDuckGo)
        ↓
Response Generation & TTS
        ↓
Database Persistence & Learning Updates
```

## Development Commands

### Environment Setup
```powershell
# Create and activate virtual environment
python -m venv .venv_assistente
.venv_assistente\Scripts\Activate.ps1

# Install all dependencies
pip install -r requirements.txt

# Optional: Setup MySQL database (see Configuration section)
python scripts\setup_database.py
```

### Primary Launcher Commands
```powershell
# Run the main application
python run_ASTRA.py

# Run comprehensive test suite
python run_ASTRA.py test

# Show project structure
python run_ASTRA.py struct

# Clean project files (cache, temp files, logs)
python run_ASTRA.py clean

# Show help and available commands
python run_ASTRA.py help
```

### Individual Component Testing
```powershell
# Test multi-user system
python tests\test_multi_user_system.py

# Test contextual integration
python tests\test_contextual_integration.py

# Demo contextual system capabilities
python tests\demo_contextual_system.py

# Test people management system
python tests\test_people_system.py

# Test preferences system
python tests\test_preferences.py
```

### Neural Model Commands
```powershell
# Train intent classification model
python neural_models\modelo.py

# Test intent predictions
python neural_models\prever.py

# Test specific text prediction
python neural_models\prever.py "Como está o tempo?"
```

### Database Operations
```powershell
# Setup database schema
python scripts\setup_database.py

# Run database queries (if mysql_config.ini exists)
python scripts\consultas_perfil.sql

# Clean database and reset
python scripts\cleanup.py --database
```

## Configuration System

### Essential External Dependencies

1. **Tesseract OCR**: Must be installed separately
   - Multiple path detection:
   ```python
   # Auto-detected paths from config.py
   TESSERACT_PATHS = [
       r'C:\Tesseract-OCR\tesseract.exe',
       r'C:\Program Files\Tesseract-OCR\tesseract.exe',
       r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
   ]
   ```

2. **Ollama Server**: Must be running locally on `http://localhost:11434`
   - Default model: `gemma3n:e4b`
   - Configure in `config.py`:
   ```python
   CONFIG = {
       "ollama_model": "gemma3n:e4b",
       "ollama_url": "http://localhost:11434/api/generate",
       # Other settings...
   }
   ```

3. **MySQL Database** (Optional):
   - System works in fallback mode without MySQL
   - Configuration via `mysql_config.ini` file:
   ```ini
   [mysql]
   host = localhost
   port = 3306
   user = root
   password = your_password
   database = ASTRA_assistant
   charset = utf8mb4
   collation = utf8mb4_unicode_ci
   ```

### Configuration Files

- **Core Config**: `config/config.py` - Central configuration system
- **Neural Data**: `neural_models/dados/intents.json` - Intent training data
- **Persistence Files**:
  - `data/conversation_history.json` - Conversation history
  - `data/personal_facts.json` - Personal information
  - `data/users.json` - User profiles with patterns
  - `data/people.json` - People relationships
  - `logs/ASTRA_assistant.log` - Activity logging

## File Structure & Architecture

```
ASTRA/
├── audio/                 # Audio management subsystem
│   └── audio_manager.py   # TTS and speech recognition
├── config/                # Centralized configuration
│   ├── config.py          # Main configuration system
│   └── __init__.py        # Package initialization
├── core/                  # Core application
│   └── assistente.py      # Main PyQt6 GUI and application logic
├── database/              # Database management
│   └── database_manager.py # MySQL interface with JSON fallback
├── data/                  # Persistent data storage
│   ├── conversation_history.json # Conversation records
│   ├── personal_facts.json      # User facts
│   ├── people.json              # People relationships
│   └── users.json               # User profiles
├── docs/                  # Documentation
│   ├── logging_system.md         # Logging documentation
│   ├── README_ESTRUTURA.md       # Structure overview
│   ├── README_MySQL.md           # MySQL setup guide
│   ├── SISTEMA_MULTIUSER_CONTEXTUAL_README.md # Multi-user system docs
│   └── WARP.md                    # WARP documentation
├── logs/                  # System logs
│   └── ASTRA_assistant.log # Main log file
├── modules/               # Core functionality modules
│   ├── contextual_analyzer.py    # Context analysis
│   ├── multi_user_manager.py     # User identification
│   ├── people_manager.py         # People relationships
│   ├── personal_profile.py       # Personal preferences
│   └── user_commands.py          # Command interpretation
├── neural_models/         # ML intent classification
│   ├── modelo.pkl         # Trained model binary
│   ├── modelo.py          # Model training script
│   └── prever.py          # Prediction module
├── scripts/               # Utility scripts
│   ├── cleanup.py         # Maintenance script
│   ├── setup_database.py  # Database initialization
│   └── consultas_perfil.sql # Profile query examples
├── tests/                 # Testing subsystem
│   ├── demo_contextual_system.py     # Contextual system demo
│   ├── test_contextual_integration.py # Integration tests
│   ├── test_multi_user_system.py     # Multi-user tests
│   ├── test_people_fixed.py          # People system tests
│   ├── test_people_system.py         # People API tests
│   └── test_preferences.py           # Preferences tests
├── .venv_assistente/      # Virtual environment
├── README.md              # Project overview
├── requirements.txt       # Dependencies
└── run_ASTRA.py            # Main application launcher
```

## Key Technical Details

### Multi-User Identification System
- **Voice Pattern Recognition**: Librosa + Gaussian Mixture Models for speaker identification
- **Text Analysis**: Vocabulary overlap, typical phrases, punctuation style analysis
- **Contextual Clues**: Personal references, relationship mentions, behavioral patterns
- **Auto-identification**: Natural language parsing ("eu sou...", "chamo-me...") with 80% confidence weight
- **Confidence Scoring**: Weighted combination of multiple identification methods

### Database Architecture
- **Hybrid System**: MySQL primary with JSON fallback for offline operation
- **Schema**: Full relational design with conversations, messages, voice_interactions, user_preferences, people tables
- **UTF-8 Support**: Full Unicode with emoji support for Portuguese content
- **Session Management**: Automatic session generation and conversation tracking
- **Migration Strategy**: Automatic schema creation with version control

### Audio & TTS System
- **Speech Recognition**: Google Speech API with Portuguese language detection
- **TTS Engine**: Coqui-TTS with Portuguese VITS model (`tts_models/pt/cv/vits`)
- **Audio Processing**: Threaded operations with status callbacks
- **Voice Sample Analysis**: Real-time voice pattern extraction for user identification
- **Audio Management**: Automatic temp file cleanup and resource management

### Contextual Analysis Engine
- **Topic Detection**: 6 categories (trabalho, família, entretenimento, desporto, saúde, tecnologia)
- **Emotion Analysis**: 5 primary emotions with pattern matching and emoji detection
- **Formality Assessment**: Three levels (formal, informal, muito_informal)
- **Temporal Patterns**: Time-based user behavior analysis
- **Behavioral Tracking**: Language features, personal references, location mentions

### Neural Network & ML
- **Intent Classification**: TF-IDF vectorization with MultinomialNB classifier
- **Training Data**: Portuguese patterns in `neural_models/dados/intents.json`
- **Fallback System**: Ollama LLM integration for unrecognized intents
- **Model Persistence**: Joblib serialization for trained models
- **Continuous Learning**: User pattern updates and model retraining

### UI Architecture
- **Framework**: PyQt6 with QWebEngineView for rich animations
- **Background**: Perlin noise clouds with CSS3 animations
- **Threading**: Signal-slot pattern for thread-safe UI updates
- **Responsive Design**: Automatic scaling and status feedback
- **Error Handling**: Graceful degradation with user feedback

## Development Patterns & Best Practices

### Adding New Features
1. **Module Structure**: Create new functionality in appropriate `modules/` subdirectory
2. **Configuration**: Add settings to `config/config.py` CONFIG dictionary
3. **Database Schema**: Update `database_manager.py` for new tables/fields
4. **Testing**: Create corresponding test in `tests/` directory
5. **Documentation**: Update relevant README files and docstrings

### Multi-User System Integration
```python
# Initialize multi-user manager
self.multi_user_manager = MultiUserManager(database_manager=self.db_manager)

# Process user input with identification
result = self.multi_user_manager.process_input(
    input_text=user_input,
    audio_data=audio_samples,  # Optional
    context=current_context
)

# Extract user information
user_id = result['user_id']
confidence = result['confidence']
user_profile = result['user_profile']
```

### Contextual Analysis Integration
```python
# Analyze user context
context_analysis = self.contextual_analyzer.analyze_context(
    text=user_input,
    user_id=current_user_id,
    timestamp=datetime.now()
)

# Extract insights
topics = context_analysis['topics']
emotions = context_analysis['emotions']
formality = context_analysis['formality']
behavioral_indicators = context_analysis['behavioral_indicators']
```

### Thread-Safe UI Updates
```python
# Always use signals for UI updates from worker threads
self.ui_updater.append_output_signal.emit(response_text)
self.ui_updater.set_status_signal.emit("Processing...")
self.ui_updater.enable_buttons_signal.emit(False)

# For heavy operations, use separate threads
worker_thread = threading.Thread(target=self._heavy_operation)
worker_thread.daemon = True
worker_thread.start()
```

### Database Operations
```python
# Always check database availability
if DATABASE_AVAILABLE and self.db_manager:
    # Use MySQL operations
    result = self.db_manager.save_conversation(conversation_data)
else:
    # Fallback to JSON storage
    self._save_to_json(conversation_data)
```

### Error Handling
```python
# Log all errors with context
try:
    # Operation
    pass
except Exception as e:
    logger.error(f"Error in {operation_name}: {e}")
    self.ui_updater.set_status_signal.emit(f"Erro: {str(e)}")
    # Graceful degradation
```

## System Dependencies & Requirements

### Critical Dependencies
- **PyQt6 + WebEngine**: GUI framework with web view support
- **Coqui-TTS**: Portuguese voice synthesis
- **SpeechRecognition**: Multi-engine voice recognition
- **MySQL-Connector-Python**: Database connectivity (optional)
- **Scikit-learn + Joblib**: Machine learning pipeline
- **Ollama**: Local LLM integration

### Optional Dependencies  
- **Librosa**: Voice pattern analysis (advanced user identification)
- **Pytesseract**: OCR functionality
- **OpenCV**: Image processing
- **NLTK**: Natural language processing enhancements

### External Services
- **Ollama Server**: Must be running locally with Portuguese-capable model
- **MySQL Server**: Optional but recommended for production use
- **Tesseract OCR**: System-level installation for image text recognition

