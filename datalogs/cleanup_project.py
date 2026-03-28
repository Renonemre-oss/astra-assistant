#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Limpeza e Reorganização do Projeto ASTRA
Executa análise completa e limpeza automatizada
"""

import os
import sys
import json
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import re

class ProjectCleaner:
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'problematic_folders': [],
            'empty_folders': [],
            'large_files': [],
            'duplicate_configs': [],
            'unused_imports': [],
            'hardcoded_values': [],
            'files_removed': [],
            'folders_renamed': [],
            'total_space_freed': 0
        }
    
    def analyze_structure(self):
        """Analisa a estrutura completa do projeto"""
        print("🔍 Analisando estrutura do projeto...")
        
        # Encontrar pastas vazias
        for dirpath, dirnames, filenames in os.walk(self.root):
            if '.venv' in dirpath or '__pycache__' in dirpath:
                continue
            
            if not dirnames and not filenames:
                rel_path = Path(dirpath).relative_to(self.root)
                self.report['empty_folders'].append(str(rel_path))
        
        print(f"   ✅ {len(self.report['empty_folders'])} pastas vazias encontradas")
    
    def find_problematic_folders(self):
        """Encontra pastas com nomes problemáticos"""
        print("📁 Procurando pastas com nomes problemáticos...")
        
        problematic_patterns = [
            r'.*\{.*',  # Contém {
            r'.*\}.*',  # Contém }
            r'.* .*',   # Contém espaços
            r'.*temp.*',  # Pasta temporária
            r'.*backup.*',  # Pasta de backup desorganizada
        ]
        
        for dirpath, dirnames, _ in os.walk(self.root):
            if '.venv' in dirpath:
                continue
            
            for dirname in dirnames:
                for pattern in problematic_patterns:
                    if re.match(pattern, dirname, re.IGNORECASE):
                        full_path = Path(dirpath) / dirname
                        rel_path = full_path.relative_to(self.root)
                        self.report['problematic_folders'].append(str(rel_path))
                        break
        
        print(f"   ✅ {len(self.report['problematic_folders'])} pastas problemáticas")
    
    def find_large_files(self, threshold_mb=10):
        """Encontra arquivos grandes que podem ser removidos"""
        print(f"📦 Procurando arquivos > {threshold_mb}MB...")
        
        for filepath in self.root.rglob('*'):
            if filepath.is_file() and '.venv' not in str(filepath):
                size_mb = filepath.stat().st_size / (1024 * 1024)
                if size_mb > threshold_mb:
                    self.report['large_files'].append({
                        'path': str(filepath.relative_to(self.root)),
                        'size_mb': round(size_mb, 2)
                    })
        
        print(f"   ✅ {len(self.report['large_files'])} arquivos grandes")
    
    def find_duplicate_configs(self):
        """Encontra arquivos de configuração duplicados"""
        print("⚙️  Procurando configurações duplicadas...")
        
        config_files = defaultdict(list)
        
        for filepath in self.root.rglob('*'):
            if filepath.is_file() and '.venv' not in str(filepath):
                if filepath.suffix in ['.ini', '.yaml', '.yml', '.json', '.conf']:
                    if 'config' in filepath.name.lower() or 'settings' in filepath.name.lower():
                        config_files[filepath.name].append(str(filepath.relative_to(self.root)))
        
        for name, paths in config_files.items():
            if len(paths) > 1:
                self.report['duplicate_configs'].append({
                    'filename': name,
                    'locations': paths
                })
        
        print(f"   ✅ {len(self.report['duplicate_configs'])} configs duplicados")
    
    def scan_hardcoded_values(self):
        """Escaneia arquivos Python para valores hardcoded"""
        print("🔒 Escaneando valores hardcoded...")
        
        patterns = {
            'paths': r'["\']/(home|usr|var|tmp|opt)/[^"\']+["\']',
            'ips': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'ports': r':\s*\d{4,5}(?!\d)',  # Portas hardcoded
        }
        
        python_files = list(self.root.rglob('*.py'))
        sample_size = min(50, len(python_files))  # Analisar amostra
        
        for filepath in python_files[:sample_size]:
            if '.venv' in str(filepath):
                continue
            
            try:
                content = filepath.read_text(encoding='utf-8')
                for pattern_type, pattern in patterns.items():
                    matches = re.findall(pattern, content)
                    if matches:
                        self.report['hardcoded_values'].append({
                            'file': str(filepath.relative_to(self.root)),
                            'type': pattern_type,
                            'count': len(matches)
                        })
            except:
                pass
        
        print(f"   ✅ {len(self.report['hardcoded_values'])} arquivos com valores hardcoded")
    
    def remove_empty_folders(self):
        """Remove pastas vazias"""
        print("🗑️  Removendo pastas vazias...")
        removed = 0
        
        for folder in self.report['empty_folders']:
            folder_path = self.root / folder
            if folder_path.exists() and not any(folder_path.iterdir()):
                try:
                    folder_path.rmdir()
                    self.report['files_removed'].append(str(folder))
                    removed += 1
                except Exception as e:
                    print(f"   ⚠️  Erro ao remover {folder}: {e}")
        
        print(f"   ✅ {removed} pastas vazias removidas")
    
    def clean_cache_files(self):
        """Remove arquivos de cache"""
        print("🧹 Limpando arquivos de cache...")
        
        cache_patterns = ['*.pyc', '*.pyo', '.DS_Store', 'Thumbs.db', '*.log']
        removed = 0
        
        for pattern in cache_patterns:
            for filepath in self.root.rglob(pattern):
                if '.venv' not in str(filepath):
                    try:
                        filepath.unlink()
                        removed += 1
                    except:
                        pass
        
        print(f"   ✅ {removed} arquivos de cache removidos")
    
    def generate_report(self):
        """Gera relatório final em JSON"""
        report_path = self.root / 'CLEANUP_REPORT.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Relatório gerado: {report_path}")
        return report_path
    
    def print_summary(self):
        """Imprime resumo das operações"""
        print("\n" + "="*60)
        print("📋 RESUMO DA LIMPEZA")
        print("="*60)
        print(f"✅ Pastas vazias removidas: {len([f for f in self.report['files_removed'] if 'folder' in str(f)])}")
        print(f"✅ Arquivos problemáticos: {len(self.report['problematic_folders'])}")
        print(f"✅ Configs duplicados: {len(self.report['duplicate_configs'])}")
        print(f"✅ Arquivos grandes: {len(self.report['large_files'])}")
        print(f"✅ Hardcoded values: {len(self.report['hardcoded_values'])}")
        print("="*60)

def main():
    project_root = Path(__file__).parent.resolve()
    print(f"🚀 Iniciando limpeza do projeto: {project_root}\n")
    
    cleaner = ProjectCleaner(project_root)
    
    # Fase 1: Análise
    cleaner.analyze_structure()
    cleaner.find_problematic_folders()
    cleaner.find_large_files()
    cleaner.find_duplicate_configs()
    cleaner.scan_hardcoded_values()
    
    print("\n" + "="*60)
    print("🧹 Iniciando limpeza...")
    print("="*60 + "\n")
    
    # Fase 2: Limpeza
    cleaner.remove_empty_folders()
    cleaner.clean_cache_files()
    
    # Fase 3: Relatório
    cleaner.print_summary()
    report_path = cleaner.generate_report()
    
    print(f"\n✨ Limpeza concluída! Verifique {report_path} para detalhes.")

if __name__ == "__main__":
    main()
