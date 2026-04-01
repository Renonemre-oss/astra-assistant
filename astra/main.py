#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal Inteligente
Launcher Principal

Este script facilita a execução do ASTRA com a nova estrutura organizada.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao Python path
project_root = Path(__file__).parent.parent  # Diretório jarvis_organized
sys.path.insert(0, str(project_root))

# Importar e executar __init__ para configurar paths
import astra

# Configurar logging
from astra.config.settings.main_config import configure_logging
configure_logging()

def main():
    """Função principal para executar o ASTRA."""
    try:
        # Importar o assistente principal
        from astra.core.assistant import main as assistente_main
        
        print("🤖 ASTRA - Assistente Pessoal Inteligente")
        print("📁 Nova estrutura organizada carregada!")
        print("-" * 50)
        
        # Executar o assistente
        assistente_main()
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("\n💡 Certifique-se de que todos os módulos estão nas pastas corretas:")
        print("   - astra/core/assistant.py")
        print("   - astra/modules/")
        print("   - astra/config/settings/main_config.py")
        print("   - etc...")
        
    except FileNotFoundError as e:
        print(f"❌ Arquivo não encontrado: {e}")
        print("\n💡 Verifique se a estrutura do projeto está completa.")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

def run_tests():
    """Executa os testes do sistema."""
    try:
        from astra.tests.test_framework import run_tests as framework_run_tests
        print("🧪 Executando framework de testes do ASTRA...")
        result = framework_run_tests(verbosity=2)
        return result.wasSuccessful()
    except ImportError:
        # Fallback para método antigo
        import subprocess
        print("🧪 Executando testes básicos do ASTRA...")
        
        test_files = [
            "tests/test_multi_user_system.py",
            "tests/test_contextual_integration.py", 
            "tests/demo_contextual_system.py",
            "tests/test_framework.py"
        ]
        
        success = True
        for test_file in test_files:
            if Path(test_file).exists():
                print(f"\n▶️  Executando {test_file}...")
                try:
                    subprocess.run([sys.executable, test_file], check=True)
                    print(f"✅ {test_file} passou!")
                except subprocess.CalledProcessError:
                    print(f"❌ {test_file} falhou!")
                    success = False
            else:
                print(f"⚠️  {test_file} não encontrado!")
        
        return success

def show_structure():
    """Mostra a estrutura do projeto."""
    print("📁 Estrutura do Projeto ASTRA:")
    print("-" * 40)
    
    folders = [
        "core/", "modules/", "utils/", "database/", 
        "voice/", "audio/", "config/", "data/",
        "neural_models/", "scripts/", "tests/", 
        "docs/", "logs/"
    ]
    
    for folder in folders:
        if Path(folder).exists():
            files = list(Path(folder).glob("*.py"))
            print(f"📂 {folder} ({len(files)} arquivos Python)")
        else:
            print(f"📂 {folder} (não encontrada)")

def run_cleanup():
    """Executa o script de limpeza do projeto."""
    import subprocess
    
    print("🧹 Executando limpeza do projeto ASTRA...")
    
    cleanup_script = "scripts/cleanup.py"
    if Path(cleanup_script).exists():
        try:
            subprocess.run([sys.executable, cleanup_script], check=True)
            print("✅ Limpeza executada com sucesso!")
        except subprocess.CalledProcessError:
            print("❌ Erro durante a limpeza!")
    else:
        print("⚠️  Script de limpeza não encontrado!")

def run_diagnostics():
    """Executa diagnóstico completo do sistema."""
    try:
        from astra.utils.system_diagnostics import SystemDiagnostics
        print("🔍 Executando diagnóstico do sistema ASTRA...")
        
        diagnostics = SystemDiagnostics()
        diagnostics.run_full_diagnostic()
        
        # Gerar relatório
        report = diagnostics.generate_report('text')
        print(report)
        
        # Auto-fix se disponível
        actions = diagnostics.auto_fix_issues()
        if actions:
            print("\n🔧 Correções automáticas aplicadas:")
            for action in actions:
                print(f"  ✅ {action}")
                
    except ImportError:
        print("⚠️  Sistema de diagnóstico não disponível")

def run_profile_manager():
    """Executa interface de gestão de perfil."""
    try:
        from astra.modules.ui.profile_manager_ui import main as profile_main
        print("📄 Abrindo interface de gestão de perfil...")
        profile_main()
    except ImportError as e:
        print("⚠️  Interface de perfil não disponível")
        print(f"  Erro: {e}")
        print("  Verifique se PyQt6 está instalado: pip install PyQt6")

def run_performance_report():
    """Mostra relatório de performance."""
    try:
        from astra.utils.profiling.performance_monitor import performance_monitor as pm
        
        print("📈 Relatório de Performance ASTRA")
        print("=" * 40)
        
        stats = pm.get_statistics()
        
        # Mostrar estatísticas
        if stats:
            print(f"CPU: {stats.get('cpu', {}).get('current', 0):.1f}%")
            print(f"Memória: {stats.get('memory', {}).get('current', 0):.1f}%")
            print(f"\nMétricas coletadas: {stats.get('total_measurements', 0)}")
            print(f"Tempo de monitoramento: {stats.get('uptime_seconds', 0):.1f}s")
        else:
            print("⚠️  Nenhuma estatística disponível ainda")
        
    except ImportError:
        print("⚠️  Sistema de performance não disponível")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test" or command == "tests":
            success = run_tests()
            sys.exit(0 if success else 1)
        elif command == "structure" or command == "struct":
            show_structure()
        elif command == "clean" or command == "cleanup":
            run_cleanup()
        elif command == "diag" or command == "diagnostic":
            run_diagnostics()
        elif command == "profile" or command == "config":
            run_profile_manager()
        elif command == "perf" or command == "performance":
            run_performance_report()
        elif command == "help":
            print("🤖 ASTRA Launcher - Comandos disponíveis:")
            print("  python run_ASTRA.py              - Executar o assistente")
            print("  python run_ASTRA.py test         - Executar testes")
            print("  python run_ASTRA.py struct       - Mostrar estrutura")
            print("  python run_ASTRA.py clean        - Limpar arquivos desnecessários")
            print("  python run_ASTRA.py diag         - Executar diagnóstico")
            print("  python run_ASTRA.py profile      - Abrir gestão de perfil")
            print("  python run_ASTRA.py perf         - Mostrar performance")
            print("  python run_ASTRA.py help         - Mostrar ajuda")
        else:
            print(f"❌ Comando desconhecido: {command}")
            print("Use 'python run_ASTRA.py help' para ver comandos disponíveis.")
    else:
        main()

