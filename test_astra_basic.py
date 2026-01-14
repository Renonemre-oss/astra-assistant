#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Script - ASTRA Basic Functionality
Tests core components without launching full GUI
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all critical modules can be imported."""
    print("=" * 60)
    print("TEST 1: Importação de Módulos Críticos")
    print("=" * 60)
    
    tests = {
        "Config": lambda: __import__('astra.config', fromlist=['CONFIG']),
        "AudioManager": lambda: __import__('astra.modules.audio.audio_manager', fromlist=['AudioManager']),
        "HotwordDetector": lambda: __import__('astra.modules.speech.hotword_detector', fromlist=['HotwordDetector']),
        "PersonalProfile": lambda: __import__('astra.modules.personal_profile', fromlist=['PersonalProfile']),
        "Utils": lambda: __import__('astra.utils.utils', fromlist=['perguntar_ollama']),
    }
    
    results = {}
    for name, import_func in tests.items():
        try:
            import_func()
            results[name] = "✅ OK"
        except Exception as e:
            results[name] = f"❌ FALHOU: {str(e)[:50]}"
    
    for name, result in results.items():
        print(f"  {name:20s} {result}")
    
    return all("✅" in r for r in results.values())

def test_config():
    """Test configuration loading."""
    print("\n" + "=" * 60)
    print("TEST 2: Configuração")
    print("=" * 60)
    
    try:
        from astra.config import CONFIG, DEPENDENCIES
        
        print(f"  Ollama URL: {CONFIG.get('ollama_url', 'N/A')}")
        print(f"  Model: {CONFIG.get('ollama_model', 'N/A')}")
        print(f"  Data Dir: {CONFIG.get('history_file', 'N/A').parent if CONFIG.get('history_file') else 'N/A'}")
        
        # Check YAML configs
        yaml_configs = [
            project_root / "config" / "ai_config.yaml",
            project_root / "config" / "skills_config.yaml"
        ]
        
        print(f"\n  Arquivos YAML:")
        for config_file in yaml_configs:
            exists = "✅" if config_file.exists() else "❌"
            print(f"    {exists} {config_file.name}")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro ao carregar config: {e}")
        return False

def test_audio_manager():
    """Test AudioManager initialization."""
    print("\n" + "=" * 60)
    print("TEST 3: Audio Manager")
    print("=" * 60)
    
    try:
        from astra.modules.audio.audio_manager import AudioManager
        
        print("  Inicializando AudioManager...")
        audio_mgr = AudioManager()
        
        print(f"  Status: {audio_mgr.get_status()}")
        print("  ✅ AudioManager inicializado")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ollama_connection():
    """Test connection to Ollama."""
    print("\n" + "=" * 60)
    print("TEST 4: Conexão Ollama")
    print("=" * 60)
    
    try:
        import requests
        from astra.config import CONFIG
        
        url = CONFIG.get('ollama_url', 'http://localhost:11434')
        
        print(f"  Testando conexão: {url}")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("  ✅ Ollama está online e acessível")
            
            # Try a simple generation test
            from astra.utils.utils import perguntar_ollama
            print("\n  Testando geração de resposta...")
            resposta = perguntar_ollama("Diz apenas 'OK'", [])
            
            if resposta and len(resposta) > 0:
                print(f"  ✅ Resposta recebida: '{resposta[:50]}...'")
                return True
            else:
                print("  ⚠️ Ollama online mas não respondeu")
                return False
        else:
            print(f"  ❌ Ollama retornou status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("  ❌ Ollama não está rodando (Connection refused)")
        print("     Execute: ollama serve")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_skills_basic():
    """Test basic skills functionality."""
    print("\n" + "=" * 60)
    print("TEST 5: Skills Básicas")
    print("=" * 60)
    
    try:
        import yaml
        
        skills_config = project_root / "config" / "skills_config.yaml"
        
        if not skills_config.exists():
            print("  ❌ skills_config.yaml não encontrado")
            return False
        
        with open(skills_config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        builtin_skills = config.get('builtin_skills', {})
        enabled_skills = [name for name, cfg in builtin_skills.items() if cfg.get('enabled', False)]
        
        print(f"  Skills configuradas: {len(builtin_skills)}")
        print(f"  Skills ativadas: {len(enabled_skills)}")
        print(f"  Ativadas: {', '.join(enabled_skills)}")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def main():
    """Run all tests."""
    print("\n🤖 ASTRA - Teste de Funcionalidade Básica")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Config": test_config(),
        "AudioManager": test_audio_manager(),
        "Ollama": test_ollama_connection(),
        "Skills": test_skills_basic()
    }
    
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"  {test_name:20s} {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! ASTRA está funcional.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
