#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Script para mostrar showcase de logos
Abre o navegador com a página de demonstração dos logos
"""

import os
import sys
import webbrowser
from pathlib import Path

def show_logo_showcase():
    """Abre o showcase de logos no navegador."""
    project_root = Path(__file__).parent.parent
    showcase_path = project_root / "docs" / "logo_showcase.html"
    
    if not showcase_path.exists():
        print("❌ Arquivo de showcase não encontrado!")
        print(f"   Esperado em: {showcase_path}")
        return False
    
    try:
        # Converter para URL file://
        file_url = showcase_path.as_uri()
        
        print("🎨 Abrindo showcase de logos do ALEX...")
        print(f"📂 Arquivo: {showcase_path}")
        
        # Abrir no navegador padrão
        webbrowser.open(file_url)
        
        print("✅ Showcase aberto no navegador!")
        print("\n🔍 O que você pode ver:")
        print("  • Logo Principal (512x512)")
        print("  • Logo Horizontal (800x300)")  
        print("  • Favicon (64x64)")
        print("  • Ícone da Aplicação (256x256)")
        print("  • Exemplos de uso")
        print("  • Estatísticas dos assets")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao abrir showcase: {e}")
        print("\n💡 Alternativas:")
        print(f"  • Abra manualmente: {showcase_path}")
        print(f"  • URL direta: {file_url}")
        return False

def check_assets():
    """Verifica se os assets existem."""
    project_root = Path(__file__).parent.parent
    assets_dir = project_root / "assets"
    
    if not assets_dir.exists():
        print("⚠️  Diretório de assets não encontrado!")
        print("💡 Execute: python scripts/generate_logos.py")
        return False
    
    # Verificar arquivos principais
    expected_files = [
        "logos/alex_logo_main.png",
        "logos/alex_logo_horizontal.png", 
        "favicons/alex_favicon.png",
        "icons/alex_app_icon.png"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in expected_files:
        full_path = assets_dir / file_path
        if full_path.exists():
            existing_files.append(file_path)
        else:
            missing_files.append(file_path)
    
    print(f"📊 Status dos Assets:")
    print(f"  ✅ Encontrados: {len(existing_files)}")
    print(f"  ❌ Ausentes: {len(missing_files)}")
    
    if existing_files:
        print("\n✅ Assets disponíveis:")
        for file_path in existing_files:
            print(f"  • {file_path}")
    
    if missing_files:
        print("\n❌ Assets ausentes:")
        for file_path in missing_files:
            print(f"  • {file_path}")
        print("\n💡 Para gerar assets: python scripts/generate_logos.py")
        return False
    
    return True

def main():
    """Função principal."""
    print("🎨 ALEX - Logo Showcase")
    print("=" * 40)
    
    # Verificar assets primeiro
    if not check_assets():
        print("\n❌ Assets não encontrados - execute o gerador primeiro")
        return 1
    
    # Mostrar showcase
    if show_logo_showcase():
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())