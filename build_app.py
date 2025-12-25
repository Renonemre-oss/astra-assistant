#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏗️ JARVIS APP BUILDER
Script para construir a aplicação Jarvis como executável standalone
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import zipfile
from datetime import datetime

# Cores para terminal
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_step(message):
    """Imprime etapa"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}[→] {message}{Colors.END}")

def print_success(message):
    """Imprime sucesso"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Imprime erro"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    """Imprime aviso"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def clean_build_dirs():
    """Limpa diretórios de build anteriores"""
    print_step("Limpando builds anteriores...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print_success(f"Removido: {dir_name}/")
    
    # Limpar .pyc recursivamente
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
    
    print_success("Limpeza concluída")

def check_dependencies():
    """Verifica dependências necessárias"""
    print_step("Verificando dependências...")
    
    required = ['pyinstaller', 'PyQt6', 'pyttsx3', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_').lower())
            print_success(f"{package} instalado")
        except ImportError:
            missing.append(package)
            print_error(f"{package} não encontrado")
    
    if missing:
        print_error(f"Instale as dependências faltantes:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True

def create_icon():
    """Cria/verifica ícone da aplicação"""
    print_step("Verificando ícone...")
    
    icon_dir = Path('jarvis/assets')
    icon_dir.mkdir(parents=True, exist_ok=True)
    
    icon_path = icon_dir / 'icon.ico'
    
    if not icon_path.exists():
        print_warning("Ícone não encontrado, usando padrão")
        # Você pode adicionar lógica para criar um ícone básico aqui
    else:
        print_success(f"Ícone encontrado: {icon_path}")
    
    return icon_path.exists()

def build_executable():
    """Constrói o executável usando PyInstaller"""
    print_step("Construindo executável com PyInstaller...")
    
    try:
        # Executar PyInstaller
        cmd = ['pyinstaller', 'jarvis.spec', '--clean', '--noconfirm']
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Build concluído com sucesso!")
            return True
        else:
            print_error("Falha no build")
            print(result.stderr)
            return False
            
    except Exception as e:
        print_error(f"Erro durante build: {e}")
        return False

def create_installer():
    """Cria pacote instalador"""
    print_step("Criando pacote instalador...")
    
    dist_dir = Path('dist/Jarvis')
    
    if not dist_dir.exists():
        print_error("Diretório dist/Jarvis não encontrado")
        return False
    
    # Criar arquivo README para distribuição
    readme_content = """# JARVIS - Assistente Pessoal Inteligente

## 🚀 Como usar

1. Execute `Jarvis.exe`
2. A interface gráfica será aberta
3. Configure o assistente conforme suas preferências

## 📖 Documentação

Para documentação completa, visite:
- Arquivo: ATUALIZACAO.md
- Arquivo: TESTE_INTENSIVO_RELATORIO.md

## 🔄 Atualizações

O Jarvis verifica automaticamente por atualizações.
Para gerenciar manualmente, execute o Update Manager.

## 🆘 Suporte

Em caso de problemas:
1. Verifique os logs em: logs/
2. Consulte a documentação
3. Reporte issues no GitHub

---
Versão 2.0.0 - Feliz Natal! 🎄
"""
    
    readme_path = dist_dir / 'README.txt'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print_success("README criado")
    
    # Copiar documentação importante
    docs_to_copy = [
        'ATUALIZACAO.md',
        'TESTE_INTENSIVO_RELATORIO.md',
        'requirements.txt'
    ]
    
    for doc in docs_to_copy:
        if Path(doc).exists():
            shutil.copy(doc, dist_dir / doc)
            print_success(f"Copiado: {doc}")
    
    # Criar arquivo de versão
    version_info = {
        'version': '2.0.0',
        'build_date': datetime.now().isoformat(),
        'platform': 'Windows',
    }
    
    import json
    version_path = dist_dir / 'version.json'
    with open(version_path, 'w', encoding='utf-8') as f:
        json.dump(version_info, f, indent=4)
    
    print_success("Informações de versão criadas")
    
    # Criar arquivo ZIP para distribuição
    print_step("Criando arquivo ZIP...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f'Jarvis_v2.0.0_Windows_{timestamp}.zip'
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir.parent)
                zipf.write(file_path, arcname)
    
    print_success(f"Pacote criado: {zip_name}")
    
    # Mostrar tamanho
    size_mb = Path(zip_name).stat().st_size / (1024 * 1024)
    print_success(f"Tamanho: {size_mb:.1f} MB")
    
    return True

def create_portable_version():
    """Cria versão portable"""
    print_step("Criando versão portable...")
    
    portable_dir = Path('dist/Jarvis_Portable')
    dist_jarvis = Path('dist/Jarvis')
    
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    shutil.copytree(dist_jarvis, portable_dir)
    
    # Criar arquivo de configuração portable
    portable_config = portable_dir / 'portable.txt'
    with open(portable_config, 'w') as f:
        f.write('Este é o modo portable do Jarvis.\n')
        f.write('Todas as configurações serão salvas nesta pasta.\n')
    
    print_success("Versão portable criada")
    
    # Criar ZIP portable
    portable_zip = f'Jarvis_v2.0.0_Portable_{datetime.now().strftime("%Y%m%d")}.zip'
    
    with zipfile.ZipFile(portable_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(portable_dir.parent)
                zipf.write(file_path, arcname)
    
    print_success(f"Pacote portable: {portable_zip}")
    
    return True

def show_summary():
    """Mostra resumo do build"""
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}📊 RESUMO DO BUILD{Colors.END}")
    print("=" * 60)
    
    dist_dir = Path('dist/Jarvis')
    
    if dist_dir.exists():
        # Contar arquivos
        total_files = sum(1 for _ in dist_dir.rglob('*') if _.is_file())
        
        # Calcular tamanho total
        total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
        total_size_mb = total_size / (1024 * 1024)
        
        print(f"\n📁 Diretório: dist/Jarvis/")
        print(f"📄 Total de arquivos: {total_files}")
        print(f"💾 Tamanho total: {total_size_mb:.1f} MB")
        
        # Listar arquivos principais
        print(f"\n📌 Arquivos principais:")
        main_files = ['Jarvis.exe', 'README.txt', 'version.json']
        for file in main_files:
            file_path = dist_dir / file
            if file_path.exists():
                size = file_path.stat().st_size / (1024 * 1024)
                print(f"  ✅ {file} ({size:.1f} MB)")
    
    # Listar pacotes ZIP criados
    print(f"\n📦 Pacotes de distribuição:")
    for zip_file in Path('.').glob('Jarvis_*.zip'):
        size = zip_file.stat().st_size / (1024 * 1024)
        print(f"  ✅ {zip_file.name} ({size:.1f} MB)")
    
    print("\n" + "=" * 60)

def main():
    """Função principal"""
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}🏗️  JARVIS APP BUILDER v2.0{Colors.END}")
    print("=" * 60)
    
    # Etapa 1: Limpar
    clean_build_dirs()
    
    # Etapa 2: Verificar dependências
    if not check_dependencies():
        print_error("Corrija as dependências antes de continuar")
        return False
    
    # Etapa 3: Verificar ícone
    create_icon()
    
    # Etapa 4: Build
    if not build_executable():
        print_error("Build falhou")
        return False
    
    # Etapa 5: Criar instalador
    if not create_installer():
        print_error("Falha ao criar instalador")
        return False
    
    # Etapa 6: Versão portable
    if not create_portable_version():
        print_warning("Falha ao criar versão portable")
    
    # Mostrar resumo
    show_summary()
    
    # Sucesso!
    print("\n" + "=" * 60)
    print(f"{Colors.GREEN}{Colors.BOLD}🎉 BUILD CONCLUÍDO COM SUCESSO!{Colors.END}")
    print("=" * 60)
    print(f"\n📂 Executável: dist/Jarvis/Jarvis.exe")
    print(f"📦 Pacotes: Jarvis_*.zip")
    print(f"\n🚀 Para testar, execute: dist/Jarvis/Jarvis.exe")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Build cancelado pelo usuário{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
