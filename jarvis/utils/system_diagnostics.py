#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Sistema de Diagnóstico
Módulo para verificar o estado do sistema e sugerir correções

Este módulo fornece funcionalidades para:
- Verificar dependências instaladas
- Diagnosticar problemas de configuração
- Sugerir correções automáticas
- Gerar relatórios de sistema
"""

import sys
import platform
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
from config import CONFIG, DEPENDENCIES, DATABASE_AVAILABLE, TESSERACT_AVAILABLE

logger = logging.getLogger(__name__)

class SystemDiagnostics:
    """Sistema de diagnóstico completo para o ALEX."""
    
    def __init__(self):
        self.results = {}
        self.suggestions = []
        self.errors = []
        self.warnings = []
    
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """
        Executa diagnóstico completo do sistema.
        
        Returns:
            Dict com resultado completo do diagnóstico
        """
        logger.info("🔍 Iniciando diagnóstico completo do sistema...")
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_basic_system_info(),
            'python_info': self._get_python_info(),
            'dependencies': self._check_dependencies(),
            'configuration': self._check_configuration(),
            'database': self._check_database_status(),
            'file_structure': self._check_file_structure(),
            'permissions': self._check_permissions(),
            'disk_space': self._check_disk_space(),
            'suggestions': self.suggestions,
            'errors': self.errors,
            'warnings': self.warnings
        }
        
        self._generate_suggestions()
        
        logger.info(f"✅ Diagnóstico concluído. {len(self.errors)} erros, {len(self.warnings)} avisos")
        return self.results
    
    def _get_basic_system_info(self) -> Dict[str, str]:
        """Obtém informações básicas do sistema."""
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node()
        }
    
    def _get_python_info(self) -> Dict[str, str]:
        """Obtém informações do Python."""
        return {
            'version': sys.version,
            'executable': sys.executable,
            'prefix': sys.prefix,
            'path': sys.path[:3]  # Primeiros 3 paths apenas
        }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Verifica estado das dependências."""
        deps = DEPENDENCIES
        
        # Definir dependências críticas e opcionais
        critical_deps = ['PyQt6', 'requests', 'numpy']
        optional_deps = ['TTS', 'speech_recognition', 'mysql_connector', 'PIL', 'scikit_learn']
        
        critical_missing = [dep for dep in critical_deps if not deps.get(dep, False)]
        optional_missing = [dep for dep in optional_deps if not deps.get(dep, False)]
        
        total_available = sum(1 for v in deps.values() if v)
        total_dependencies = len(deps)
        
        result = {
            'total_available': total_available,
            'total_dependencies': total_dependencies,
            'critical_missing': critical_missing,
            'optional_missing': optional_missing,
            'details': deps,
            'percentage': (total_available / total_dependencies) * 100 if total_dependencies > 0 else 0
        }
        
        # Adicionar erros para dependências críticas em falta
        for dep in critical_missing:
            self.errors.append(f"Dependência crítica em falta: {dep}")
        
        # Adicionar avisos para dependências opcionais em falta
        for dep in optional_missing:
            self.warnings.append(f"Dependência opcional em falta: {dep}")
        
        return result
    
    def _check_configuration(self) -> Dict[str, Any]:
        """Verifica configurações do sistema."""
        config_status = {
            'config_file_exists': True,  # config.py sempre existe
            'data_directory': CONFIG['facts_file'].parent.exists(),
            'logs_directory': CONFIG['log_file'].parent.exists(),
            'neural_directory': CONFIG['model_file'].parent.exists(),
            'audio_directory': CONFIG['temp_audio_file'].parent.exists(),
            'tesseract_configured': TESSERACT_AVAILABLE,
            'database_configured': DATABASE_AVAILABLE
        }
        
        # Verificar se diretorias existem e criar se necessário
        directories = [
            ('data', CONFIG['facts_file'].parent),
            ('logs', CONFIG['log_file'].parent),
            ('neural_models', CONFIG['model_file'].parent),
            ('audio', CONFIG['temp_audio_file'].parent)
        ]
        
        for name, path in directories:
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"📁 Diretório {name} criado: {path}")
                    config_status[f'{name}_directory'] = True
                except Exception as e:
                    self.errors.append(f"Falha ao criar diretório {name}: {e}")
                    config_status[f'{name}_directory'] = False
        
        return config_status
    
    def _check_database_status(self) -> Dict[str, Any]:
        """Verifica estado da base de dados."""
        status = {
            'available': DATABASE_AVAILABLE,
            'mysql_config_exists': False,
            'sqlite_fallback': True
        }
        
        # Verificar se ficheiro de configuração MySQL existe
        mysql_config = Path(__file__).parent.parent / "mysql_config.ini"
        status['mysql_config_exists'] = mysql_config.exists()
        
        if DATABASE_AVAILABLE and not status['mysql_config_exists']:
            self.warnings.append("MySQL disponível mas ficheiro de configuração não encontrado")
        
        return status
    
    def _check_file_structure(self) -> Dict[str, bool]:
        """Verifica estrutura de arquivos essenciais."""
        base_path = Path(__file__).parent.parent
        
        essential_files = {
            'run_alex.py': base_path / 'run_alex.py',
            'requirements.txt': base_path / 'requirements.txt',
            'build/pyproject.toml': base_path / 'build' / 'pyproject.toml',
            'config/config.py': base_path / 'config' / 'config.py',
            'core/assistente.py': base_path / 'core' / 'assistente.py',
            'database/models.py': base_path / 'database' / 'models.py',
            'audio/audio_manager.py': base_path / 'audio' / 'audio_manager.py'
        }
        
        structure_status = {}
        
        for file_name, file_path in essential_files.items():
            exists = file_path.exists()
            structure_status[file_name] = exists
            
            if not exists:
                self.errors.append(f"Arquivo essencial em falta: {file_name}")
        
        return structure_status
    
    def _check_permissions(self) -> Dict[str, bool]:
        """Verifica permissões de escrita nos diretórios importantes."""
        directories_to_check = [
            CONFIG['facts_file'].parent,
            CONFIG['log_file'].parent,
            Path(__file__).parent.parent / 'data'
        ]
        
        permissions = {}
        
        for directory in directories_to_check:
            try:
                # Tentar criar um arquivo temporário para testar escrita
                test_file = directory / '.test_write_permission'
                test_file.write_text('test')
                test_file.unlink()  # Remover arquivo de teste
                permissions[str(directory)] = True
            except Exception as e:
                permissions[str(directory)] = False
                self.warnings.append(f"Sem permissão de escrita em: {directory}")
        
        return permissions
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Verifica espaço em disco disponível."""
        try:
            import shutil
            
            project_path = Path(__file__).parent.parent
            total, used, free = shutil.disk_usage(project_path)
            
            free_gb = free // (1024**3)
            total_gb = total // (1024**3)
            used_percentage = (used / total) * 100
            
            disk_info = {
                'free_gb': free_gb,
                'total_gb': total_gb,
                'used_percentage': used_percentage,
                'sufficient_space': free_gb >= 1  # Pelo menos 1GB livre
            }
            
            if free_gb < 1:
                self.warnings.append(f"Pouco espaço em disco: {free_gb}GB livre")
            
            return disk_info
            
        except Exception as e:
            self.warnings.append(f"Não foi possível verificar espaço em disco: {e}")
            return {'error': str(e)}
    
    def _generate_suggestions(self):
        """Gera sugestões baseadas nos resultados do diagnóstico."""
        deps = self.results['dependencies']
        
        # Sugestões para dependências em falta
        if deps['critical_missing']:
            missing_deps = ', '.join(deps['critical_missing'])
            self.suggestions.append(f"Instalar dependências críticas: pip install {missing_deps}")
        
        if deps['optional_missing']:
            important_optional = ['TTS', 'speech_recognition', 'PIL', 'pytesseract']
            missing_important = [dep for dep in deps['optional_missing'] if dep in important_optional]
            
            if missing_important:
                missing_deps = ', '.join(missing_important)
                self.suggestions.append(f"Instalar dependências importantes: pip install {missing_deps}")
        
        # Sugestões para Tesseract
        if not TESSERACT_AVAILABLE and DEPENDENCIES.get('pytesseract', False):
            self.suggestions.append("Instalar Tesseract OCR: https://github.com/tesseract-ocr/tesseract/wiki")
        
        # Sugestões para base de dados
        if not DATABASE_AVAILABLE:
            self.suggestions.append("Para usar MySQL: pip install mysql-connector-python sqlalchemy")
        
        # Sugestão para configuração MySQL
        if DATABASE_AVAILABLE and not self.results['database']['mysql_config_exists']:
            self.suggestions.append("Criar arquivo mysql_config.ini para configurar base de dados")
    
    def generate_report(self, format_type: str = 'text') -> str:
        """
        Gera relatório de diagnóstico.
        
        Args:
            format_type: Formato do relatório ('text', 'json', 'html')
        
        Returns:
            Relatório formatado
        """
        if not self.results:
            self.run_full_diagnostic()
        
        if format_type == 'json':
            import json
            return json.dumps(self.results, indent=2, ensure_ascii=False)
        
        elif format_type == 'html':
            return self._generate_html_report()
        
        else:  # text
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Gera relatório em formato texto."""
        report = []
        report.append("=" * 60)
        report.append("🤖 ALEX - RELATÓRIO DE DIAGNÓSTICO DO SISTEMA")
        report.append("=" * 60)
        report.append(f"⏰ Data: {self.results['timestamp']}")
        report.append(f"💻 Sistema: {self.results['system_info']['platform']} {self.results['system_info']['platform_release']}")
        report.append(f"🐍 Python: {self.results['python_info']['version'].split()[0]}")
        report.append("")
        
        # Resumo geral
        report.append("📊 RESUMO GERAL")
        report.append("-" * 30)
        deps = self.results['dependencies']
        report.append(f"✅ Dependências instaladas: {deps['total_available']}/{deps['total_dependencies']} ({deps['percentage']:.1f}%)")
        report.append(f"❌ Erros encontrados: {len(self.errors)}")
        report.append(f"⚠️  Avisos: {len(self.warnings)}")
        report.append("")
        
        # Dependências
        report.append("📦 DEPENDÊNCIAS")
        report.append("-" * 30)
        for dep, status in deps['details'].items():
            status_icon = "✅" if status else "❌"
            report.append(f"{status_icon} {dep}")
        report.append("")
        
        # Erros
        if self.errors:
            report.append("❌ ERROS")
            report.append("-" * 30)
            for error in self.errors:
                report.append(f"• {error}")
            report.append("")
        
        # Avisos
        if self.warnings:
            report.append("⚠️  AVISOS")
            report.append("-" * 30)
            for warning in self.warnings:
                report.append(f"• {warning}")
            report.append("")
        
        # Sugestões
        if self.suggestions:
            report.append("💡 SUGESTÕES")
            report.append("-" * 30)
            for suggestion in self.suggestions:
                report.append(f"• {suggestion}")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def _generate_html_report(self) -> str:
        """Gera relatório em formato HTML."""
        deps = self.results['dependencies']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ALEX - Relatório de Diagnóstico</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .success {{ color: #27ae60; }}
                .error {{ color: #e74c3c; }}
                .warning {{ color: #f39c12; }}
                .dependency {{ display: inline-block; margin: 5px; padding: 5px 10px; border-radius: 3px; }}
                .dep-ok {{ background: #d5f4e6; color: #27ae60; }}
                .dep-missing {{ background: #fadbd8; color: #e74c3c; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 ALEX - Relatório de Diagnóstico</h1>
                <p>Data: {self.results['timestamp']}</p>
                <p>Sistema: {self.results['system_info']['platform']} {self.results['system_info']['platform_release']}</p>
            </div>
            
            <div class="section">
                <h2>📊 Resumo Geral</h2>
                <p><strong>Dependências:</strong> {deps['total_available']}/{deps['total_dependencies']} ({deps['percentage']:.1f}%)</p>
                <p><strong>Erros:</strong> <span class="error">{len(self.errors)}</span></p>
                <p><strong>Avisos:</strong> <span class="warning">{len(self.warnings)}</span></p>
            </div>
            
            <div class="section">
                <h2>📦 Dependências</h2>
        """
        
        for dep, status in deps['details'].items():
            css_class = "dep-ok" if status else "dep-missing"
            icon = "✅" if status else "❌"
            html += f'<span class="dependency {css_class}">{icon} {dep}</span>\n'
        
        html += """
            </div>
        """
        
        if self.errors:
            html += """
            <div class="section">
                <h2 class="error">❌ Erros</h2>
                <ul>
            """
            for error in self.errors:
                html += f"<li class='error'>{error}</li>"
            html += "</ul></div>"
        
        if self.warnings:
            html += """
            <div class="section">
                <h2 class="warning">⚠️ Avisos</h2>
                <ul>
            """
            for warning in self.warnings:
                html += f"<li class='warning'>{warning}</li>"
            html += "</ul></div>"
        
        if self.suggestions:
            html += """
            <div class="section">
                <h2>💡 Sugestões</h2>
                <ul>
            """
            for suggestion in self.suggestions:
                html += f"<li>{suggestion}</li>"
            html += "</ul></div>"
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def auto_fix_issues(self) -> List[str]:
        """
        Tenta corrigir automaticamente problemas encontrados.
        
        Returns:
            Lista de ações realizadas
        """
        actions_taken = []
        
        # Criar diretórios em falta
        directories = [
            ('data', CONFIG['facts_file'].parent),
            ('logs', CONFIG['log_file'].parent),
            ('neural_models', CONFIG['model_file'].parent),
            ('audio', CONFIG['temp_audio_file'].parent)
        ]
        
        for name, path in directories:
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    actions_taken.append(f"Criado diretório: {path}")
                    logger.info(f"📁 Diretório {name} criado automaticamente")
                except Exception as e:
                    logger.error(f"Falha ao criar diretório {name}: {e}")
        
        # Criar arquivo de configuração MySQL exemplo
        mysql_config_path = Path(__file__).parent.parent / "mysql_config.ini.example"
        if DATABASE_AVAILABLE and not mysql_config_path.exists():
            try:
                example_config = """[mysql]
host = localhost
port = 3306
user = root
password = sua_senha_aqui
database = alex_assistant
charset = utf8mb4
collation = utf8mb4_unicode_ci

# Instruções:
# 1. Renomeie este arquivo para 'mysql_config.ini'
# 2. Configure suas credenciais MySQL
# 3. Reinicie o ALEX
"""
                mysql_config_path.write_text(example_config, encoding='utf-8')
                actions_taken.append(f"Criado arquivo exemplo: mysql_config.ini.example")
            except Exception as e:
                logger.error(f"Falha ao criar arquivo de configuração exemplo: {e}")
        
        return actions_taken


def main():
    """Função principal para executar diagnóstico via linha de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(description='ALEX System Diagnostics')
    parser.add_argument('--format', choices=['text', 'json', 'html'], default='text',
                       help='Formato do relatório')
    parser.add_argument('--output', type=str, help='Arquivo para salvar o relatório')
    parser.add_argument('--autofix', action='store_true', help='Tentar corrigir problemas automaticamente')
    
    args = parser.parse_args()
    
    diagnostics = SystemDiagnostics()
    
    if args.autofix:
        print("🔧 Tentando corrigir problemas automaticamente...")
        actions = diagnostics.auto_fix_issues()
        for action in actions:
            print(f"✅ {action}")
    
    print("🔍 Executando diagnóstico do sistema...")
    diagnostics.run_full_diagnostic()
    
    report = diagnostics.generate_report(args.format)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Relatório salvo em: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()