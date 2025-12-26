# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Astra AI Assistant is a modular, extensible AI assistant platform with support for multiple AI providers and a plug-and-play skills system. The project combines local AI processing (via Ollama) with optional cloud providers (OpenAI), featuring voice interaction, RAG (Retrieval Augmented Generation), and a comprehensive plugin/skills architecture.

**Primary Language:** Python 3.10+
**Key Technologies:** PyQt6, FastAPI, Ollama, ChromaDB, SQLAlchemy

## Development Setup

### Initial Setup
```pwsh
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install Ollama for local AI
# Download from: https://ollama.ai
ollama pull llama3.2
```

### Running the Application

**Main ASTRA application (PyQt6 GUI):**
```pwsh
python astra\main.py
```

**Available launcher commands:**
```pwsh
python astra\main.py test          # Run test suite
python astra\main.py structure     # Show project structure
python astra\main.py clean         # Clean up generated files
python astra\main.py diag          # Run system diagnostics
python astra\main.py profile       # Open profile manager UI
python astra\main.py perf          # Show performance report
```

## Testing

### Running Tests
```pwsh
# All tests
pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# Specific test categories
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests only

# From launcher
python astra\main.py test

# Using Makefile (in astra/ directory)
cd astra
make test                                # All tests with coverage
make test-unit                           # Unit tests only
make test-integration                    # Integration tests only
```

### Test Configuration
- Test fixtures and configuration: `astra/tests/conftest.py`
- Tests use pytest with pytest-cov, pytest-mock, and pytest-asyncio
- Coverage reports generated in HTML format

## Code Quality

### Linting and Formatting
```pwsh
# Linting
ruff check jarvis/
mypy jarvis/

# Formatting
black jarvis/ tests/
```

**Standards:**
- Follow PEP 8
- Maximum line length: 100 characters
- Use type hints for all functions
- Google-style docstrings

## Architecture

### High-Level Structure
```
jarvis_organized/
├── astra/               # Legacy ASTRA GUI application (PyQt6)
│   ├── core/           # Core assistant logic
│   ├── modules/        # Feature modules (audio, speech, personality, memory)
│   ├── skills/         # Skill system for ASTRA
│   ├── ui/             # PyQt6 interface components
│   ├── config/         # Configuration management
│   └── main.py         # ASTRA launcher
├── ai/                 # AI Engine (for newer architecture)
├── api_server/         # FastAPI REST API server
├── plugins/            # Plugin system with interface
│   ├── builtin/       # Built-in plugins
│   └── plugin_interface.py
├── skills/             # Modular skills system (newer architecture)
│   ├── base_skill.py  # Base class for all skills
│   ├── builtin/       # Built-in skills (weather, etc.)
│   └── custom/        # Custom user skills
├── modules/            # Core functional modules
├── config/             # Configuration files (YAML-based)
├── tests/              # Test suite
└── examples/           # Usage examples
```

### Dual Architecture

This codebase has **two parallel architectures**:

1. **ASTRA Application** (`astra/`): Legacy PyQt6-based GUI assistant with integrated modules
2. **Modular Architecture** (root level): Newer plugin/skills-based architecture with AI engine abstraction

When working on features, clarify which architecture to target. The modular architecture (root level) is the future direction.

### AI Engine Layer

**Location:** Root-level `ai/` (planned/newer architecture)
**Purpose:** Unified interface for multiple AI providers (Ollama, OpenAI)

**Key Concepts:**
- Provider abstraction with automatic fallback
- Response caching (configurable TTL)
- Streaming support
- Configuration via `config/ai_config.yaml`

**Configuration Example:**
```yaml
default_provider: ollama
providers:
  ollama:
    enabled: true
    model: llama3.2
    url: http://localhost:11434
  openai:
    enabled: false
    model: gpt-3.5-turbo
fallback_chain:
  - ollama
cache_enabled: true
cache_ttl: 3600
```

### Skills System

**Location:** `skills/` (root level), `astra/skills/` (ASTRA-specific)

Skills are modular capabilities with:
- **Base class:** `BaseSkill` with abstract methods
- **Metadata:** Name, version, dependencies, priority
- **Lifecycle:** `initialize()`, `can_handle()`, `execute()`
- **Auto-discovery:** Skills loaded automatically from config
- **Priority system:** `SkillPriority` enum (CRITICAL → MINIMAL)

**Creating a Custom Skill:**
```python
from skills.base_skill import BaseSkill, SkillMetadata, SkillResponse, SkillPriority

class MySkill(BaseSkill):
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="my_skill",
            version="1.0.0",
            description="Does something cool",
            keywords=["keyword1", "keyword2"],
            priority=SkillPriority.NORMAL
        )
    
    def initialize(self) -> bool:
        # Setup code
        return True
    
    def can_handle(self, query: str, context: dict) -> bool:
        return "keyword1" in query.lower()
    
    def execute(self, query: str, context: dict) -> SkillResponse:
        return SkillResponse.success_response("Response content")
```

Add to `config/skills_config.yaml`:
```yaml
custom_skills:
  my_skill:
    enabled: true
    module: "skills.custom.my_skill"
    class: "MySkill"
```

### Plugin System

**Location:** `plugins/`

Similar to skills but with broader capabilities:
- **Base:** `PluginInterface` with metadata and lifecycle hooks
- **Capabilities:** Command handling, event listening, hooks
- **Priority:** Similar to skills

### Key Modules (ASTRA)

**Audio/Voice:** `astra/audio/`, `astra/modules/speech/`
- TTS via Piper (preferred) or Windows SAPI (fallback)
- Speech recognition with hotword detection
- Audio playback management

**Memory System:** `astra/modules/memory_system.py`
- Intelligent memory with context tracking
- Personal profile management
- Conversation history

**Personality Engine:** `astra/modules/personality_engine.py`
- Dynamic personality traits
- Contextual response adaptation

**Database:** `astra/database/`
- SQLite by default (also supports MySQL)
- SQLAlchemy ORM
- Migration: `astra/scripts/setup/setup_database.py`

**RAG System:** Root-level RAG components
- ChromaDB for vector storage
- Sentence transformers for embeddings
- PDF processing with PyPDF2

## Configuration Management

**Location:** `config/` (root), `astra/config/` (ASTRA-specific)

- YAML-based configuration files
- Environment variable support: `${VAR_NAME}`
- Settings categories: AI providers, skills, database, API keys

**Important files:**
- `config/ai_config.yaml` - AI provider settings
- `config/skills_config.yaml` - Skills configuration
- `astra/config/settings/main_config.py` - ASTRA configuration

## Database Setup

```pwsh
# SQLite (default)
python astra\scripts\setup\setup_database.py

# Configuration in astra/config/database.ini:
# [sqlite]
# database_path = ASTRA_assistant.db
```

## API Integration

**FastAPI Server:** `api_server/`
```pwsh
# Start API server
uvicorn api_server.main:app --reload
```

**External APIs:**
- Weather API (OpenWeather)
- News APIs (various sources)
- Crypto APIs

Configure API keys in `config/` files or environment variables.

## Important Patterns

### Logging
- Centralized logging system: `astra/core/logging_system.py`
- UTF-8 encoding with emoji support
- Location: `logs/ASTRA_assistant.log`
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Error Handling
- Graceful degradation for missing dependencies
- Try-import pattern for optional features
- Error tracking with error_handler utility

### TTS Preference
**User Preference:** Piper TTS over Windows SAPI
- Piper offers better voice quality
- Fallback to Windows SAPI if Piper unavailable

### Async/Await
- FastAPI endpoints use async
- Speech recognition uses threading
- Audio playback uses threading

## Git Workflow

**Important:** After any significant changes, push to GitHub:
```pwsh
git add .
git commit -m "feat: description"

# Include co-author attribution
git commit -m "feat: description

Co-Authored-By: Warp <agent@warp.dev>"

git push origin main
```

**Repository:** https://github.com/Renonemre-oss/astra-assistant

## Dependencies Management

**Main dependencies file:** `requirements.txt` (root level)
**ASTRA-specific:** `astra/requirements.txt`

Key dependencies:
- **AI/ML:** requests, numpy, scikit-learn, joblib, sentence-transformers
- **RAG:** chromadb, PyPDF2
- **Web:** fastapi, uvicorn, pydantic, httpx
- **UI:** PyQt6, PyQt6-WebEngine
- **Speech:** pyttsx3, SpeechRecognition, pyaudio, TTS (Coqui)
- **Database:** sqlalchemy, redis, diskcache
- **Testing:** pytest, pytest-cov, pytest-mock, pytest-asyncio, faker
- **Code Quality:** mypy, ruff, black

## Common Tasks

### Adding a New Skill
1. Create skill class in `skills/custom/` or `astra/skills/builtin/`
2. Inherit from `BaseSkill`
3. Implement required methods
4. Add to configuration YAML
5. Test with `pytest tests/`

### Adding a New API Integration
1. Create API client in `api/`
2. Add configuration to appropriate config file
3. Document API key requirements
4. Add error handling and fallbacks

### Updating Dependencies
Reference `MIGRATION_V3.md` for version migration guidance.

```pwsh
pip install -r requirements.txt --upgrade
```

### Creating a Plugin
1. Create plugin file in `plugins/builtin/` or `plugins/custom/`
2. Inherit from `PluginInterface`
3. Implement `get_metadata()`, `on_load()`, `on_unload()`
4. Add capability methods (e.g., `handle_command()`)
5. Test the plugin

## Documentation

**Location:** `docs/`

Structure:
- `docs/guides/` - Getting started, tutorials
- `docs/api/` - API documentation
- `docs/architecture/` - System design
- `astra/docs/` - ASTRA-specific documentation

**Key Documents:**
- `README.md` - Main project overview
- `CONTRIBUTING.md` - Contribution guidelines
- `REORGANIZATION_SUMMARY.md` - Project structure history
- `MIGRATION_V3.md` - Dependency migration guide

## Platform Notes

**Windows-Specific:**
- Use `pwsh` (PowerShell) for commands
- Path separators: backslashes (`\`)
- Virtual environment activation: `.venv\Scripts\activate`
- Some Unix-specific Makefile commands may not work directly

**Cross-Platform Considerations:**
- Use `pathlib.Path` for file paths
- Test on target platforms
- Check audio/TTS compatibility (platform-dependent)

## Troubleshooting

### Ollama Not Responding
```pwsh
# Check if running
ollama list

# Start Ollama service if needed
```

### TTS Issues
- Verify Piper TTS is installed and accessible
- Fallback to Windows SAPI is automatic
- Check audio device configuration

### Database Connection Issues
- Verify `database.ini` configuration
- Check SQLite file permissions
- Validate MySQL service if using MySQL

### Import Errors
- Check virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.10+)
