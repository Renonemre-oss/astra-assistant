#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/JARVIS - RAG Installation Script
Script para instalação rápida do sistema RAG.
"""

import subprocess
import sys
from pathlib import Path


def check_package(package_name: str) -> bool:
    """Verifica se um pacote está instalado."""
    try:
        __import__(package_name.replace('-', '_'))
        return True
    except ImportError:
        return False


def install_package(package: str) -> bool:
    """Instala um pacote via pip."""
    try:
        print(f"📦 Instalando {package}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package, "-q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        print(f"✅ {package} instalado com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Erro ao instalar {package}")
        return False


def main():
    """Instala dependências do sistema RAG."""
    
    print("=" * 60)
    print("🧠 ALEX/JARVIS - Instalação do Sistema RAG")
    print("=" * 60)
    
    # Dependências necessárias
    packages = {
        'chromadb': 'chromadb==0.5.23',
        'sentence_transformers': 'sentence-transformers==3.3.1',
        'PyPDF2': 'PyPDF2==3.0.1'
    }
    
    print("\n📋 Verificando dependências...\n")
    
    to_install = []
    for package_name, package_spec in packages.items():
        if check_package(package_name):
            print(f"✅ {package_name} já instalado")
        else:
            print(f"❌ {package_name} não encontrado")
            to_install.append(package_spec)
    
    if not to_install:
        print("\n✅ Todas as dependências já estão instaladas!")
        print("\n🎉 Sistema RAG pronto para uso!")
        return
    
    # Instalar pacotes faltantes
    print(f"\n📦 Instalando {len(to_install)} pacotes...\n")
    
    success_count = 0
    for package in to_install:
        if install_package(package):
            success_count += 1
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 Resultado da Instalação")
    print("=" * 60)
    print(f"Total: {len(to_install)} pacotes")
    print(f"Sucesso: {success_count} ✅")
    print(f"Falhas: {len(to_install) - success_count} ❌")
    
    if success_count == len(to_install):
        print("\n🎉 Instalação completa!")
        print("\n📝 Próximos passos:")
        print("   1. python examples/rag_example.py")
        print("   2. python examples/rag_memory_example.py")
        print("\n📖 Documentação: docs/RAG.md")
    else:
        print("\n⚠️ Algumas instalações falharam!")
        print("Tente instalar manualmente:")
        for package in to_install:
            print(f"   pip install {package}")


if __name__ == "__main__":
    main()
