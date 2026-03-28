#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASTRA - Script de Reestruturação do Projeto
============================================

Este script OPCIONAL move o projeto da estrutura nested:
  jarvis_organized/jarvis_organized/astra/
Para uma estrutura mais limpa:
  jarvis_organized/astra/

⚠️ AVISO: Este script move arquivos! Faça backup antes de executar.

Uso:
    python scripts/restructure_project.py --dry-run  # Ver o que será feito
    python scripts/restructure_project.py            # Executar reestruturação
"""

import sys
import shutil
from pathlib import Path
import argparse

def print_banner():
    print("=" * 60)
    print("🔄 ASTRA - Reestruturação do Projeto")
    print("=" * 60)
    print()

def find_project_root() -> tuple[Path, Path]:
    """
    Encontra o diretório atual do projeto e o destino.
    
    Returns:
        tuple: (source_path, destination_path)
    """
    # Este script está em astra/scripts/
    script_path = Path(__file__).resolve()
    
    # Caminho atual: .../jarvis_organized/jarvis_organized/astra/scripts/
    current_astra = script_path.parent.parent
    current_middle = current_astra.parent
    current_top = current_middle.parent
    
    # Caminho destino: .../jarvis_organized/astra/
    destination_top = current_top
    destination_astra = destination_top / "astra"
    
    return current_astra, destination_astra

def check_structure(source: Path) -> bool:
    """Verifica se a estrutura atual é nested."""
    # Verificar se estamos em jarvis_organized/jarvis_organized/astra/
    if source.name != "astra":
        print("❌ Erro: Este script deve ser executado do diretório astra/")
        return False
    
    parent = source.parent
    if parent.name != "jarvis_organized":
        print("❌ Erro: Estrutura inesperada - parent não é 'jarvis_organized'")
        return False
    
    grandparent = parent.parent
    if grandparent.name != "jarvis_organized":
        print("⚠️ Aviso: Estrutura já pode estar correta ou diferente do esperado")
        print(f"   Caminho atual: {source}")
        response = input("Continuar mesmo assim? (y/N): ")
        return response.lower() == 'y'
    
    return True

def list_changes(source: Path, destination: Path):
    """Lista as mudanças que serão feitas."""
    print("\n📋 Mudanças que serão feitas:")
    print("-" * 60)
    print(f"DE:   {source}")
    print(f"PARA: {destination}")
    print()
    
    if destination.exists():
        print("⚠️  AVISO: Destino já existe!")
        print(f"   {destination}")
        print("   Conteúdo existente será SOBRESCRITO!")
        print()
    
    # Contar arquivos
    total_files = sum(1 for _ in source.rglob('*') if _.is_file())
    total_dirs = sum(1 for _ in source.rglob('*') if _.is_dir())
    
    print(f"📁 Total de diretórios: {total_dirs}")
    print(f"📄 Total de arquivos: {total_files}")
    print()

def perform_restructure(source: Path, destination: Path, dry_run: bool = False):
    """
    Executa a reestruturação.
    
    Args:
        source: Diretório fonte (atual astra/)
        destination: Diretório destino (novo astra/)
        dry_run: Se True, apenas mostra o que seria feito
    """
    if dry_run:
        print("\n🔍 MODO DRY-RUN (nenhuma alteração será feita)")
        print("-" * 60)
        list_changes(source, destination)
        print("\n✅ Dry-run completo. Execute sem --dry-run para aplicar mudanças.")
        return True
    
    # Confirmação final
    print("\n⚠️  CONFIRMAÇÃO FINAL")
    print("-" * 60)
    print("Esta operação irá:")
    print(f"1. Mover todo o conteúdo de:")
    print(f"   {source}")
    print(f"2. Para:")
    print(f"   {destination}")
    print()
    
    if destination.exists():
        print("⚠️  O destino JÁ EXISTE e será SOBRESCRITO!")
        print()
    
    response = input("Tem certeza que deseja continuar? Digite 'SIM' para confirmar: ")
    
    if response != "SIM":
        print("\n❌ Operação cancelada pelo utilizador.")
        return False
    
    print("\n🚀 Iniciando reestruturação...")
    print("-" * 60)
    
    try:
        # Se destino existe, remover
        if destination.exists():
            print(f"🗑️  Removendo destino existente...")
            shutil.rmtree(destination)
        
        # Criar diretório pai se não existir
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Mover diretório inteiro
        print(f"📦 Movendo {source.name}/ para {destination.parent.name}/...")
        shutil.move(str(source), str(destination))
        
        print("\n✅ Reestruturação completa!")
        print()
        print("📍 Novo caminho do projeto:")
        print(f"   {destination}")
        print()
        print("🔧 Próximos passos:")
        print("1. Atualizar seus bookmarks/atalhos para o novo caminho")
        print("2. Atualizar configurações de IDE se necessário")
        print("3. Verificar se o projeto funciona:")
        print(f"   cd {destination}")
        print(f"   python main.py")
        print()
        
        # Verificar se diretório intermediário ficou vazio
        intermediate = source.parent
        if intermediate.exists():
            contents = list(intermediate.iterdir())
            if not contents:
                print(f"🗑️  Removendo diretório intermediário vazio:")
                print(f"   {intermediate}")
                intermediate.rmdir()
                print("   ✅ Removido")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO durante reestruturação: {e}")
        print("\n⚠️  O projeto pode estar em estado inconsistente!")
        print("   Verifique manualmente os diretórios:")
        print(f"   Fonte: {source}")
        print(f"   Destino: {destination}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Reestrutura o projeto ASTRA de estrutura nested para estrutura limpa",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python scripts/restructure_project.py --dry-run   # Ver o que será feito
  python scripts/restructure_project.py             # Executar reestruturação
  
⚠️  IMPORTANTE: Faça backup antes de executar!
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Mostrar o que seria feito sem fazer alterações'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Pular confirmações (use com cuidado!)'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Encontrar caminhos
    try:
        source, destination = find_project_root()
    except Exception as e:
        print(f"❌ Erro ao encontrar diretórios: {e}")
        return 1
    
    # Verificar estrutura
    if not check_structure(source):
        return 1
    
    # Listar mudanças se dry-run
    if args.dry_run:
        list_changes(source, destination)
        print("\n✅ Dry-run completo. Execute sem --dry-run para aplicar mudanças.")
        return 0
    
    # Executar reestruturação
    success = perform_restructure(source, destination, dry_run=args.dry_run)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
