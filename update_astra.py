#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 JARVIS UPDATE MANAGER
Script de linha de comando para gerenciar atualizações do Jarvis
"""

import sys
import logging
from pathlib import Path

# Adicionar jarvis ao path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

from utils.auto_updater import JarvisUpdater, get_updater

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)


def print_banner():
    """Imprime banner do updater"""
    print("\n" + "=" * 60)
    print("🔄 JARVIS UPDATE MANAGER v2.0")
    print("=" * 60 + "\n")


def check_updates(updater: JarvisUpdater):
    """Verifica atualizações disponíveis"""
    print(f"📌 Versão atual: v{updater.current_version}\n")
    print("🔍 Verificando atualizações...")
    
    update_info = updater.check_for_updates(force=True)
    
    if update_info:
        print(f"\n✨ Nova versão disponível!")
        print(f"   Versão: v{update_info['version']}")
        print(f"   Nome: {update_info['release_name']}")
        print(f"   Data: {update_info['published_at']}")
        
        if update_info.get('size'):
            size_mb = update_info['size'] / (1024 * 1024)
            print(f"   Tamanho: {size_mb:.1f} MB")
        
        if update_info.get('is_prerelease'):
            print(f"   ⚠️ Versão beta/pré-lançamento")
        
        print(f"\n📋 Notas da versão:")
        print("-" * 60)
        notes = update_info['release_notes']
        if len(notes) > 400:
            print(notes[:400] + "...")
        else:
            print(notes)
        print("-" * 60)
        
        return update_info
    else:
        print("\n✅ Jarvis está atualizado!")
        return None


def download_update(updater: JarvisUpdater, update_info: dict):
    """Baixa atualização"""
    print(f"\n📥 Baixando v{update_info['version']}...")
    
    def progress_callback(downloaded, total):
        if total > 0:
            percent = (downloaded / total) * 100
            bar_len = 40
            filled = int(bar_len * downloaded / total)
            bar = '█' * filled + '░' * (bar_len - filled)
            print(f"\r[{bar}] {percent:.1f}%", end='', flush=True)
    
    update_file = updater.download_update(update_info, progress_callback)
    print()  # Nova linha
    
    if update_file:
        print(f"✅ Download completo: {update_file.name}")
        return update_file
    else:
        print("❌ Falha no download")
        return None


def install_update(updater: JarvisUpdater, update_file: Path):
    """Instala atualização"""
    print(f"\n📦 Instalando atualização...")
    
    response = input("⚠️ Deseja criar backup antes de instalar? (S/n): ")
    if response.lower() != 'n':
        print("💾 Criando backup...")
        backup = updater.create_backup()
        if backup:
            print(f"✅ Backup criado: {backup.name}")
        else:
            print("❌ Falha ao criar backup")
            response = input("Continuar sem backup? (s/N): ")
            if response.lower() != 's':
                print("❌ Instalação cancelada")
                return False
    
    if updater.install_update(update_file):
        print("\n" + "=" * 60)
        print("🎉 ATUALIZAÇÃO INSTALADA COM SUCESSO!")
        print("=" * 60)
        print("\n🔄 Por favor, reinicie o Jarvis para aplicar as mudanças")
        return True
    else:
        print("\n❌ Falha na instalação")
        return False


def configure_auto_update(updater: JarvisUpdater):
    """Configura atualização automática"""
    print("\n⚙️ CONFIGURAÇÃO DE ATUALIZAÇÃO AUTOMÁTICA")
    print("-" * 60)
    
    config = updater.config
    
    print(f"\n1. Verificação automática: {'✅ Ativada' if config['auto_check'] else '❌ Desativada'}")
    print(f"2. Download automático: {'✅ Ativado' if config['auto_download'] else '❌ Desativado'}")
    print(f"3. Instalação automática: {'✅ Ativada' if config['auto_install'] else '❌ Desativada'}")
    print(f"4. Intervalo de verificação: {config['check_interval_hours']}h")
    print(f"5. Canal de atualização: {config['update_channel']}")
    
    print("\n0. Voltar")
    
    choice = input("\nEscolha uma opção para modificar (0-5): ")
    
    if choice == '1':
        config['auto_check'] = not config['auto_check']
        print(f"✅ Verificação automática: {'Ativada' if config['auto_check'] else 'Desativada'}")
    elif choice == '2':
        config['auto_download'] = not config['auto_download']
        print(f"✅ Download automático: {'Ativado' if config['auto_download'] else 'Desativado'}")
    elif choice == '3':
        config['auto_install'] = not config['auto_install']
        print(f"✅ Instalação automática: {'Ativada' if config['auto_install'] else 'Desativada'}")
    elif choice == '4':
        try:
            hours = int(input("Digite o intervalo em horas (1-168): "))
            if 1 <= hours <= 168:
                config['check_interval_hours'] = hours
                print(f"✅ Intervalo atualizado: {hours}h")
            else:
                print("❌ Valor inválido")
        except ValueError:
            print("❌ Valor inválido")
    elif choice == '5':
        print("\nCanais disponíveis:")
        print("1. stable (estável)")
        print("2. beta (versões beta)")
        print("3. dev (desenvolvimento)")
        channel_choice = input("Escolha (1-3): ")
        channels = {'1': 'stable', '2': 'beta', '3': 'dev'}
        if channel_choice in channels:
            config['update_channel'] = channels[channel_choice]
            print(f"✅ Canal atualizado: {config['update_channel']}")
    
    updater.save_config()


def list_backups(updater: JarvisUpdater):
    """Lista backups disponíveis"""
    print("\n💾 BACKUPS DISPONÍVEIS")
    print("-" * 60)
    
    backups = sorted(
        updater.backup_dir.glob("jarvis_backup_*.zip"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not backups:
        print("Nenhum backup encontrado")
        return
    
    for i, backup in enumerate(backups, 1):
        size_mb = backup.stat().st_size / (1024 * 1024)
        mtime = backup.stat().st_mtime
        from datetime import datetime
        date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i}. {backup.name}")
        print(f"   Tamanho: {size_mb:.1f} MB | Data: {date_str}")
    
    print("\n0. Voltar")
    choice = input("\nRestaurar backup (0 ou número): ")
    
    try:
        idx = int(choice)
        if 1 <= idx <= len(backups):
            backup_file = backups[idx - 1]
            response = input(f"\n⚠️ Restaurar {backup_file.name}? (s/N): ")
            if response.lower() == 's':
                if updater.restore_backup(backup_file):
                    print("✅ Backup restaurado com sucesso!")
                    print("🔄 Reinicie o Jarvis")
                else:
                    print("❌ Falha ao restaurar backup")
    except ValueError:
        pass


def main_menu():
    """Menu principal"""
    print_banner()
    
    updater = get_updater()
    
    while True:
        print(f"\n📌 Versão atual: v{updater.current_version}")
        print("\n" + "=" * 60)
        print("MENU PRINCIPAL")
        print("=" * 60)
        print("\n1. Verificar atualizações")
        print("2. Atualizar agora")
        print("3. Configurar atualização automática")
        print("4. Gerenciar backups")
        print("5. Criar backup manual")
        print("0. Sair")
        
        choice = input("\nEscolha uma opção: ")
        
        if choice == '1':
            check_updates(updater)
            input("\nPressione Enter para continuar...")
            
        elif choice == '2':
            update_info = check_updates(updater)
            if update_info:
                response = input("\nBaixar e instalar esta atualização? (S/n): ")
                if response.lower() != 'n':
                    update_file = download_update(updater, update_info)
                    if update_file:
                        install_update(updater, update_file)
            input("\nPressione Enter para continuar...")
            
        elif choice == '3':
            configure_auto_update(updater)
            input("\nPressione Enter para continuar...")
            
        elif choice == '4':
            list_backups(updater)
            input("\nPressione Enter para continuar...")
            
        elif choice == '5':
            print("\n💾 Criando backup...")
            backup = updater.create_backup()
            if backup:
                print(f"✅ Backup criado: {backup.name}")
            else:
                print("❌ Falha ao criar backup")
            input("\nPressione Enter para continuar...")
            
        elif choice == '0':
            print("\n👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida")


def cli_mode():
    """Modo linha de comando"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Jarvis Update Manager')
    parser.add_argument('--check', action='store_true', help='Verificar atualizações')
    parser.add_argument('--update', action='store_true', help='Atualizar automaticamente')
    parser.add_argument('--backup', action='store_true', help='Criar backup')
    parser.add_argument('--config', action='store_true', help='Mostrar configuração')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        main_menu()
        return
    
    updater = get_updater()
    
    if args.check:
        print_banner()
        check_updates(updater)
    
    if args.update:
        print_banner()
        update_info = check_updates(updater)
        if update_info:
            update_file = download_update(updater, update_info)
            if update_file:
                install_update(updater, update_file)
    
    if args.backup:
        print_banner()
        print("💾 Criando backup...")
        backup = updater.create_backup()
        if backup:
            print(f"✅ Backup criado: {backup.name}")
    
    if args.config:
        print_banner()
        config = updater.config
        print("⚙️ CONFIGURAÇÃO ATUAL")
        print("-" * 60)
        print(f"Verificação automática: {config['auto_check']}")
        print(f"Download automático: {config['auto_download']}")
        print(f"Instalação automática: {config['auto_install']}")
        print(f"Intervalo: {config['check_interval_hours']}h")
        print(f"Canal: {config['update_channel']}")
        print(f"Última verificação: {config.get('last_check', 'Nunca')}")


if __name__ == "__main__":
    try:
        cli_mode()
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
