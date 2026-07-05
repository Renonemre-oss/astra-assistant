#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal
Launcher principal: `python -m astra [comando]`
"""

import sys
from pathlib import Path

# Garantir que a raiz do projeto está no sys.path (execução direta do ficheiro)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from astra.config.settings.main_config import configure_logging

configure_logging()


def main():
    """Arranca o assistente (interface gráfica)."""
    try:
        from astra.core.assistant import main as assistant_main

        print("ASTRA - Assistente Pessoal")
        print("-" * 50)
        assistant_main()

    except ImportError as e:
        print(f"Erro de importação: {e}")
        print("Verifica se as dependências estão instaladas: pip install -r requirements.txt")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Ficheiro não encontrado: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def run_tests():
    """Executa os testes do sistema."""
    import subprocess

    print("A executar testes do ASTRA...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "astra/tests", "tests", "-v"],
        cwd=project_root,
    )
    return result.returncode == 0


def run_diagnostics():
    """Executa diagnóstico completo do sistema."""
    try:
        from astra.utils.system_diagnostics import SystemDiagnostics

        print("A executar diagnóstico do sistema...")
        diagnostics = SystemDiagnostics()
        diagnostics.run_full_diagnostic()
        print(diagnostics.generate_report("text"))

        actions = diagnostics.auto_fix_issues()
        if actions:
            print("\nCorreções automáticas aplicadas:")
            for action in actions:
                print(f"  - {action}")

    except ImportError:
        print("Sistema de diagnóstico não disponível.")


def run_profile_manager():
    """Abre a interface de gestão de perfil."""
    try:
        from astra.modules.ui.profile_manager_ui import main as profile_main

        profile_main()
    except ImportError as e:
        print(f"Interface de perfil não disponível: {e}")
        print("Verifica se o PyQt6 está instalado: pip install PyQt6")


def run_performance_report():
    """Mostra o relatório de performance."""
    try:
        from astra.utils.profiling.performance_monitor import performance_monitor as pm

        print("Relatório de Performance ASTRA")
        print("=" * 40)
        stats = pm.get_statistics()
        if stats:
            print(f"CPU: {stats.get('cpu', {}).get('current', 0):.1f}%")
            print(f"Memória: {stats.get('memory', {}).get('current', 0):.1f}%")
            print(f"Métricas coletadas: {stats.get('total_measurements', 0)}")
            print(f"Tempo de monitorização: {stats.get('uptime_seconds', 0):.1f}s")
        else:
            print("Nenhuma estatística disponível ainda.")

    except ImportError:
        print("Sistema de performance não disponível.")


def show_help():
    print("ASTRA - comandos disponíveis:")
    print("  python -m astra           Executar o assistente")
    print("  python -m astra test      Executar testes")
    print("  python -m astra diag      Executar diagnóstico do sistema")
    print("  python -m astra profile   Abrir gestão de perfil")
    print("  python -m astra perf      Mostrar relatório de performance")
    print("  python -m astra help      Mostrar esta ajuda")


def cli():
    """Interpreta os argumentos da linha de comandos."""
    if len(sys.argv) <= 1:
        main()
        return

    command = sys.argv[1].lower()
    if command in ("test", "tests"):
        sys.exit(0 if run_tests() else 1)
    elif command in ("diag", "diagnostic"):
        run_diagnostics()
    elif command in ("profile", "config"):
        run_profile_manager()
    elif command in ("perf", "performance"):
        run_performance_report()
    elif command == "help":
        show_help()
    else:
        print(f"Comando desconhecido: {command}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    cli()
