#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal
Script de Limpeza do Projeto

Este script remove arquivos desnecessários do projeto ASTRA,
mantendo apenas os arquivos essenciais para funcionamento.
"""

import os
import shutil
import glob
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def cleanup_project():
    """Remove arquivos desnecessários do projeto."""
    
    logger.info("🧹 Iniciando limpeza do projeto ASTRA...")
    
    # Definir o diretório raiz do projeto
    project_root = Path(__file__).parent.parent
    
    # Lista de padrões de arquivos para remover
    files_to_remove = [
        "*.pyc",
        "*.pyo", 
        "*.tmp",
        "*.temp",
        "*.log",  # Exceto logs importantes
        "*_temp.*",
        "*.bak",
        "*.old",
        "allfiles.txt",
        "*.spec"  # Arquivos de PyInstaller
    ]
    
    # Lista de diretórios para remover
    dirs_to_remove = [
        "__pycache__",
        ".pytest_cache",
        "build",
        "dist", 
        "*.egg-info",
        "tmp_*",
        "temp_*"
    ]
    
    # Diretórios que devem ser preservados
    preserve_dirs = [
        ".venv_assistente",  # Ambiente virtual
        ".venv",
        ".git",
        "node_modules"
    ]
    
    files_removed = 0
    dirs_removed = 0
    
    # Remover arquivos desnecessários
    for pattern in files_to_remove:
        for file_path in project_root.rglob(pattern):
            # Verificar se não está em diretório preservado
            if not any(preserve in str(file_path) for preserve in preserve_dirs):
                try:
                    # Exceção especial para logs importantes
                    if pattern == "*.log" and file_path.name in ["ASTRA_assistant.log"]:
                        continue
                    
                    file_path.unlink()
                    logger.info(f"   🗑️  Removido: {file_path.relative_to(project_root)}")
                    files_removed += 1
                except Exception as e:
                    logger.warning(f"   ⚠️  Erro ao remover {file_path}: {e}")
    
    # Remover diretórios desnecessários
    for pattern in dirs_to_remove:
        for dir_path in project_root.rglob(pattern):
            if dir_path.is_dir():
                # Verificar se não está em diretório preservado
                if not any(preserve in str(dir_path) for preserve in preserve_dirs):
                    try:
                        shutil.rmtree(dir_path)
                        logger.info(f"   📁 Diretório removido: {dir_path.relative_to(project_root)}")
                        dirs_removed += 1
                    except Exception as e:
                        logger.warning(f"   ⚠️  Erro ao remover diretório {dir_path}: {e}")
    
    # Verificar e remover arquivos específicos conhecidos
    specific_files = [
        "firebase_credentials.json",  # Credenciais (se existir, deve estar em config/)
        "resposta_temp.wav",
        "test_audio.wav"
    ]
    
    for filename in specific_files:
        file_path = project_root / filename
        if file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"   🗑️  Arquivo específico removido: {filename}")
                files_removed += 1
            except Exception as e:
                logger.warning(f"   ⚠️  Erro ao remover {filename}: {e}")
    
    logger.info(f"✅ Limpeza concluída:")
    logger.info(f"   📄 Arquivos removidos: {files_removed}")
    logger.info(f"   📁 Diretórios removidos: {dirs_removed}")
    
    return files_removed, dirs_removed

def get_project_size():
    """Calcula o tamanho do projeto."""
    project_root = Path(__file__).parent.parent
    total_size = 0
    file_count = 0
    
    # Contar apenas arquivos do projeto (excluir .venv_assistente)
    for file_path in project_root.rglob("*"):
        if file_path.is_file() and ".venv_assistente" not in str(file_path):
            try:
                total_size += file_path.stat().st_size
                file_count += 1
            except:
                pass
    
    # Converter para MB
    size_mb = total_size / (1024 * 1024)
    return size_mb, file_count

def main():
    """Função principal."""
    try:
        # Tamanho antes da limpeza
        size_before, files_before = get_project_size()
        logger.info(f"📊 Tamanho do projeto antes: {size_before:.2f} MB ({files_before} arquivos)")
        
        # Executar limpeza
        files_removed, dirs_removed = cleanup_project()
        
        # Tamanho depois da limpeza
        size_after, files_after = get_project_size()
        logger.info(f"📊 Tamanho do projeto depois: {size_after:.2f} MB ({files_after} arquivos)")
        
        # Calcular economia
        size_saved = size_before - size_after
        logger.info(f"💾 Espaço economizado: {size_saved:.2f} MB")
        
        if files_removed > 0 or dirs_removed > 0:
            logger.info("🎉 Projeto limpo com sucesso!")
        else:
            logger.info("✨ Projeto já estava limpo!")
            
    except Exception as e:
        logger.error(f"❌ Erro durante a limpeza: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
