#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Sistema de Debug e Diagnóstico Detalhado
===============================================

Sistema abrangente de diagnóstico que analisa:
- Estrutura e organização do projeto
- Dependências e ambiente
- Funcionalidades principais
- Performance e otimizações
- Logs e tratamento de erros
- Saúde geral do sistema
"""

import os
import sys
import json
import time
import logging
import traceback
import importlib
import subprocess
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import platform

class ASTRADebugger:
    """Sistema completo de debug e diagnóstico do projeto ASTRA"""
    
    def __init__(self):
        self.start_time = time.time()
        self.project_root = Path(__file__).parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'execution_time': 0,
            'summary': {},
            'structure': {},
            'dependencies': {},
            'functionality': {},
            'performance': {},
            'logs': {},
            'recommendations': [],
            'issues': [],
            'warnings': []
        }
        
        # Configurar logging temporário para debug
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Configura logger para o debug system"""
        logger = logging.getLogger('ASTRADebugger')
        logger.setLevel(logging.DEBUG)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def run_full_debug(self) -> Dict[str, Any]:
        """Executa debug completo do projeto"""
        print("🔍 ASTRA PROJECT DEBUG SYSTEM")
        print("=" * 50)
        
        try:
            self.logger.info("Iniciando diagnóstico completo...")
            
            # 1. Análise da estrutura
            print("\n📁 Analisando estrutura do projeto...")
            self.results['structure'] = self._analyze_project_structure()
            
            # 2. Verificação de dependências
            print("\n📦 Verificando dependências...")
            self.results['dependencies'] = self._check_dependencies()
            
            # 3. Teste de funcionalidades
            print("\n⚙️ Testando funcionalidades...")
            self.results['functionality'] = self._test_functionality()
            
            # 4. Análise de performance
            print("\n🚀 Analisando performance...")
            self.results['performance'] = self._analyze_performance()
            
            # 5. Verificação de logs
            print("\n📝 Verificando logs e erros...")
            self.results['logs'] = self._analyze_logs()
            
            # 6. Gerar resumo e recomendações
            print("\n📊 Gerando resumo...")
            self._generate_summary()
            
            self.results['execution_time'] = time.time() - self.start_time
            
            return self.results
            
        except Exception as e:
            self.logger.error(f"Erro durante debug: {e}")
            self.results['issues'].append({
                'type': 'CRITICAL',
                'component': 'DEBUG_SYSTEM',
                'message': f'Falha no sistema de debug: {str(e)}',
                'traceback': traceback.format_exc()
            })
            return self.results
    
    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analisa estrutura e organização do projeto"""
        structure = {
            'directories': {},
            'files': {},
            'imports': {},
            'issues': []
        }
        
        try:
            # Mapear diretórios principais
            expected_dirs = ['core', 'modules', 'utils', 'audio', 'database', 'ui', 'data', 'neural_models', 'tests', 'docs']
            
            for dir_name in expected_dirs:
                dir_path = self.project_root / dir_name
                structure['directories'][dir_name] = {
                    'exists': dir_path.exists(),
                    'files_count': len(list(dir_path.glob('*.py'))) if dir_path.exists() else 0,
                    'size_mb': self._get_dir_size(dir_path) if dir_path.exists() else 0
                }
            
            # Analisar arquivos principais
            main_files = ['main.py', 'config.py', 'requirements.txt', 'README.md']
            for file_name in main_files:
                file_path = self.project_root / file_name
                structure['files'][file_name] = {
                    'exists': file_path.exists(),
                    'size_kb': file_path.stat().st_size / 1024 if file_path.exists() else 0,
                    'last_modified': file_path.stat().st_mtime if file_path.exists() else None
                }
            
            # Analisar imports e dependências internas
            structure['imports'] = self._analyze_imports()
            
            return structure
            
        except Exception as e:
            structure['issues'].append(f"Erro na análise estrutural: {str(e)}")
            return structure
    
    def _get_dir_size(self, path: Path) -> float:
        """Calcula tamanho de um diretório em MB"""
        try:
            total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0
    
    def _analyze_imports(self) -> Dict[str, Any]:
        """Analisa imports e dependências internas"""
        imports = {
            'internal_modules': [],
            'external_packages': set(),
            'circular_imports': [],
            'missing_imports': []
        }
        
        try:
            # Buscar todos os arquivos Python
            python_files = list(self.project_root.rglob('*.py'))
            
            for py_file in python_files[:20]:  # Limitar para performance
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Extrair imports
                        import_lines = [line.strip() for line in content.split('\n') 
                                      if line.strip().startswith(('import ', 'from '))]
                        
                        for line in import_lines:
                            if 'from ' in line and ' import ' in line:
                                module = line.split('from ')[1].split(' import')[0].strip()
                            elif 'import ' in line:
                                module = line.split('import ')[1].split()[0].strip()
                            else:
                                continue
                            
                            # Categorizar import
                            if module.startswith('.') or module in ['config', 'utils', 'modules', 'core']:
                                imports['internal_modules'].append(module)
                            else:
                                imports['external_packages'].add(module.split('.')[0])
                
                except Exception as e:
                    imports['missing_imports'].append(f"{py_file.name}: {str(e)}")
            
            imports['external_packages'] = list(imports['external_packages'])
            return imports
            
        except Exception as e:
            imports['missing_imports'].append(f"Erro geral na análise: {str(e)}")
            return imports
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Verifica dependências e ambiente"""
        deps = {
            'python_version': platform.python_version(),
            'platform': platform.system(),
            'installed_packages': {},
            'missing_packages': [],
            'outdated_packages': [],
            'services': {},
            'environment': {}
        }
        
        try:
            # Verificar pacotes essenciais
            required_packages = [
                'PyQt6', 'requests', 'speechrecognition', 'pyttsx3',
                'opencv-python', 'pillow', 'numpy', 'joblib', 'mysql-connector-python',
                'duckduckgo-search', 'psutil'
            ]
            
            for package in required_packages:
                try:
                    module = importlib.import_module(package.replace('-', '_').lower())
                    version = getattr(module, '__version__', 'unknown')
                    deps['installed_packages'][package] = {
                        'version': version,
                        'status': 'OK'
                    }
                except ImportError:
                    deps['missing_packages'].append(package)
                    deps['installed_packages'][package] = {
                        'version': None,
                        'status': 'MISSING'
                    }
            
            # Verificar serviços externos
            deps['services'] = self._check_external_services()
            
            # Verificar ambiente
            deps['environment'] = {
                'working_directory': str(self.project_root),
                'python_path': sys.executable,
                'memory_available': f"{psutil.virtual_memory().available / (1024**3):.1f} GB",
                'cpu_count': psutil.cpu_count(),
                'disk_free': f"{psutil.disk_usage('.').free / (1024**3):.1f} GB"
            }
            
            return deps
            
        except Exception as e:
            deps['environment']['error'] = str(e)
            return deps
    
    def _check_external_services(self) -> Dict[str, Any]:
        """Verifica status dos serviços externos"""
        services = {}
        
        # Verificar Ollama
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            services['ollama'] = {
                'status': 'ONLINE' if response.status_code == 200 else 'ERROR',
                'response_time': response.elapsed.total_seconds(),
                'models': response.json().get('models', []) if response.status_code == 200 else []
            }
        except Exception as e:
            services['ollama'] = {
                'status': 'OFFLINE',
                'error': str(e)
            }
        
        # Verificar MySQL
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                connect_timeout=5
            )
            services['mysql'] = {
                'status': 'ONLINE',
                'version': conn.get_server_info()
            }
            conn.close()
        except Exception as e:
            services['mysql'] = {
                'status': 'OFFLINE',
                'error': str(e)
            }
        
        return services
    
    def _test_functionality(self) -> Dict[str, Any]:
        """Testa funcionalidades principais"""
        func = {
            'core_modules': {},
            'neural_models': {},
            'database': {},
            'audio': {},
            'ui_components': {},
            'utilities': {}
        }
        
        try:
            # Testar módulos core
            func['core_modules'] = self._test_core_modules()
            
            # Testar modelos neurais
            func['neural_models'] = self._test_neural_models()
            
            # Testar base de dados
            func['database'] = self._test_database_functionality()
            
            # Testar áudio
            func['audio'] = self._test_audio_functionality()
            
            # Testar utilitários
            func['utilities'] = self._test_utilities()
            
            return func
            
        except Exception as e:
            func['error'] = str(e)
            return func
    
    def _test_core_modules(self) -> Dict[str, Any]:
        """Testa módulos core"""
        core_tests = {}
        
        try:
            # Testar config
            try:
                sys.path.append(str(self.project_root))
                from config import CONFIG, DATABASE_AVAILABLE, UI_STYLES
                core_tests['config'] = {
                    'status': 'OK',
                    'database_available': DATABASE_AVAILABLE,
                    'config_keys': len(CONFIG) if isinstance(CONFIG, dict) else 'unknown',
                    'ui_styles': len(UI_STYLES) if isinstance(UI_STYLES, dict) else 'unknown'
                }
            except Exception as e:
                core_tests['config'] = {'status': 'ERROR', 'error': str(e)}
            
            # Testar assistente principal
            try:
                from core.assistente import AssistenteGUI
                core_tests['assistente'] = {'status': 'OK', 'class_loaded': True}
            except Exception as e:
                core_tests['assistente'] = {'status': 'ERROR', 'error': str(e)}
            
            return core_tests
            
        except Exception as e:
            return {'error': str(e)}
    
    def _test_neural_models(self) -> Dict[str, Any]:
        """Testa modelos neurais e classificação"""
        neural_tests = {}
        
        try:
            # Verificar arquivos de modelo
            model_path = self.project_root / 'neural_models' / 'modelo.pkl'
            intents_path = self.project_root / 'neural_models' / 'dados' / 'intents.json'
            
            neural_tests['model_file'] = {
                'exists': model_path.exists(),
                'size_mb': model_path.stat().st_size / (1024*1024) if model_path.exists() else 0
            }
            
            neural_tests['intents_file'] = {
                'exists': intents_path.exists(),
                'size_kb': intents_path.stat().st_size / 1024 if intents_path.exists() else 0
            }
            
            # Testar carregamento do modelo
            if model_path.exists():
                try:
                    import joblib
                    start_time = time.time()
                    model, vectorizer = joblib.load(model_path)
                    load_time = time.time() - start_time
                    
                    neural_tests['model_loading'] = {
                        'status': 'OK',
                        'load_time': round(load_time, 3),
                        'model_type': str(type(model).__name__),
                        'vectorizer_type': str(type(vectorizer).__name__)
                    }
                    
                    # Teste de predição
                    test_phrases = ["que horas são", "olá", "tchau"]
                    predictions = []
                    for phrase in test_phrases:
                        vectorized = vectorizer.transform([phrase])
                        prediction = model.predict(vectorized)[0]
                        predictions.append(prediction)
                    
                    neural_tests['predictions_test'] = {
                        'status': 'OK',
                        'test_results': dict(zip(test_phrases, predictions))
                    }
                    
                except Exception as e:
                    neural_tests['model_loading'] = {'status': 'ERROR', 'error': str(e)}
            
            return neural_tests
            
        except Exception as e:
            return {'error': str(e)}
    
    def _test_database_functionality(self) -> Dict[str, Any]:
        """Testa funcionalidades de base de dados"""
        db_tests = {}
        
        try:
            # Verificar arquivos de dados locais
            data_dir = self.project_root / 'data'
            if data_dir.exists():
                data_files = list(data_dir.glob('*.json'))
                db_tests['local_files'] = {
                    'count': len(data_files),
                    'files': [f.name for f in data_files[:10]],  # Primeiros 10
                    'total_size_mb': sum(f.stat().st_size for f in data_files) / (1024*1024)
                }
            
            # Testar conexão MySQL se disponível
            try:
                from database.database_manager import DatabaseManager, DatabaseConfig
                db_config = DatabaseConfig()
                db_manager = DatabaseManager(db_config)
                
                if db_manager.connect():
                    db_tests['mysql'] = {
                        'connection': 'OK',
                        'database': db_config.database
                    }
                    db_manager.disconnect()
                else:
                    db_tests['mysql'] = {'connection': 'FAILED'}
                    
            except Exception as e:
                db_tests['mysql'] = {'connection': 'ERROR', 'error': str(e)}
            
            return db_tests
            
        except Exception as e:
            return {'error': str(e)}
    
    def _test_audio_functionality(self) -> Dict[str, Any]:
        """Testa funcionalidades de áudio"""
        audio_tests = {}
        
        try:
            # Testar TTS
            try:
                import pyttsx3
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                audio_tests['tts'] = {
                    'status': 'OK',
                    'voices_available': len(voices) if voices else 0,
                    'engine': 'pyttsx3'
                }
                engine.stop()
            except Exception as e:
                audio_tests['tts'] = {'status': 'ERROR', 'error': str(e)}
            
            # Testar Speech Recognition
            try:
                import speech_recognition as sr
                r = sr.Recognizer()
                mics = sr.Microphone.list_microphone_names()
                audio_tests['stt'] = {
                    'status': 'OK',
                    'microphones': len(mics),
                    'engine': 'speech_recognition'
                }
            except Exception as e:
                audio_tests['stt'] = {'status': 'ERROR', 'error': str(e)}
            
            return audio_tests
            
        except Exception as e:
            return {'error': str(e)}
    
    def _test_utilities(self) -> Dict[str, Any]:
        """Testa módulos utilitários"""
        util_tests = {}
        
        try:
            # Testar processamento de texto
            try:
                from utils.text_processor import formatar_resposta
                test_text = "Teste de formatação"
                formatted = formatar_resposta(test_text)
                util_tests['text_processor'] = {
                    'status': 'OK',
                    'test_passed': len(formatted) > 0
                }
            except Exception as e:
                util_tests['text_processor'] = {'status': 'ERROR', 'error': str(e)}
            
            # Testar utilitários gerais
            try:
                from utils.utils import remover_emojis, verificar_servicos
                test_emoji = "Olá! 😊"
                clean_text = remover_emojis(test_emoji)
                services_status = verificar_servicos()
                
                util_tests['general_utils'] = {
                    'status': 'OK',
                    'emoji_removal': len(clean_text) < len(test_emoji),
                    'services_check': isinstance(services_status, dict)
                }
            except Exception as e:
                util_tests['general_utils'] = {'status': 'ERROR', 'error': str(e)}
            
            return util_tests
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analisa performance do sistema"""
        perf = {
            'system_resources': {},
            'file_sizes': {},
            'load_times': {},
            'memory_usage': {}
        }
        
        try:
            # Recursos do sistema
            perf['system_resources'] = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': psutil.disk_usage('.').percent,
                'processes_count': len(psutil.pids())
            }
            
            # Tamanhos de arquivos críticos
            critical_files = [
                'neural_models/modelo.pkl',
                'data/conversation_history.json',
                'core/assistente.py',
                'config.py'
            ]
            
            for file_path in critical_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    size_kb = full_path.stat().st_size / 1024
                    perf['file_sizes'][file_path] = round(size_kb, 2)
            
            # Testar tempos de carregamento
            perf['load_times'] = self._measure_load_times()
            
            return perf
            
        except Exception as e:
            perf['error'] = str(e)
            return perf
    
    def _measure_load_times(self) -> Dict[str, float]:
        """Mede tempos de carregamento de módulos críticos"""
        load_times = {}
        
        modules_to_test = [
            'config',
            'utils.utils',
            'datetime',
            'json'
        ]
        
        for module in modules_to_test:
            try:
                start_time = time.time()
                importlib.import_module(module)
                load_time = time.time() - start_time
                load_times[module] = round(load_time * 1000, 2)  # em ms
            except Exception:
                load_times[module] = -1  # Erro
        
        return load_times
    
    def _analyze_logs(self) -> Dict[str, Any]:
        """Analisa logs e tratamento de erros"""
        logs = {
            'log_files': {},
            'error_patterns': {},
            'logging_config': {}
        }
        
        try:
            # Procurar arquivos de log
            log_patterns = ['*.log', 'logs/*.log', 'data/*.log']
            log_files_found = []
            
            for pattern in log_patterns:
                log_files_found.extend(self.project_root.glob(pattern))
            
            for log_file in log_files_found[:5]:  # Primeiros 5
                logs['log_files'][log_file.name] = {
                    'size_kb': log_file.stat().st_size / 1024,
                    'last_modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                }
            
            # Verificar configuração de logging
            try:
                import logging
                root_logger = logging.getLogger()
                logs['logging_config'] = {
                    'level': root_logger.level,
                    'handlers_count': len(root_logger.handlers),
                    'effective_level': root_logger.getEffectiveLevel()
                }
            except Exception as e:
                logs['logging_config'] = {'error': str(e)}
            
            return logs
            
        except Exception as e:
            logs['error'] = str(e)
            return logs
    
    def _generate_summary(self):
        """Gera resumo e recomendações"""
        summary = {
            'overall_health': 'UNKNOWN',
            'critical_issues': 0,
            'warnings': 0,
            'recommendations_count': 0
        }
        
        issues_count = 0
        warnings_count = 0
        
        # Analisar resultados e gerar recomendações
        
        # Estrutura do projeto
        if not self.results['structure']['directories'].get('core', {}).get('exists', False):
            self.results['issues'].append({
                'type': 'CRITICAL',
                'component': 'STRUCTURE',
                'message': 'Diretório core não encontrado'
            })
            issues_count += 1
        
        # Dependências
        missing_deps = self.results['dependencies'].get('missing_packages', [])
        if missing_deps:
            self.results['warnings'].append({
                'type': 'WARNING',
                'component': 'DEPENDENCIES',
                'message': f'Pacotes faltando: {", ".join(missing_deps)}'
            })
            warnings_count += len(missing_deps)
        
        # Serviços
        services = self.results['dependencies'].get('services', {})
        if services.get('ollama', {}).get('status') != 'ONLINE':
            self.results['warnings'].append({
                'type': 'WARNING',
                'component': 'SERVICES',
                'message': 'Ollama não está disponível'
            })
            warnings_count += 1
        
        # Performance
        cpu_usage = self.results['performance'].get('system_resources', {}).get('cpu_percent', 0)
        memory_usage = self.results['performance'].get('system_resources', {}).get('memory_percent', 0)
        
        if cpu_usage > 80:
            self.results['warnings'].append({
                'type': 'WARNING',
                'component': 'PERFORMANCE',
                'message': f'Alto uso de CPU: {cpu_usage}%'
            })
            warnings_count += 1
        
        if memory_usage > 85:
            self.results['warnings'].append({
                'type': 'WARNING',
                'component': 'PERFORMANCE',
                'message': f'Alto uso de memória: {memory_usage}%'
            })
            warnings_count += 1
        
        # Gerar recomendações
        if missing_deps:
            self.results['recommendations'].append({
                'priority': 'HIGH',
                'component': 'DEPENDENCIES',
                'action': f'Instalar pacotes faltando: pip install {" ".join(missing_deps)}'
            })
        
        if services.get('ollama', {}).get('status') != 'ONLINE':
            self.results['recommendations'].append({
                'priority': 'MEDIUM',
                'component': 'SERVICES',
                'action': 'Iniciar o serviço Ollama: ollama serve'
            })
        
        # Determinar saúde geral
        if issues_count == 0 and warnings_count <= 2:
            summary['overall_health'] = 'EXCELLENT'
        elif issues_count == 0 and warnings_count <= 5:
            summary['overall_health'] = 'GOOD'
        elif issues_count <= 2:
            summary['overall_health'] = 'FAIR'
        else:
            summary['overall_health'] = 'POOR'
        
        summary['critical_issues'] = issues_count
        summary['warnings'] = warnings_count
        summary['recommendations_count'] = len(self.results['recommendations'])
        
        self.results['summary'] = summary
    
    def print_detailed_report(self):
        """Imprime relatório detalhado"""
        results = self.results
        
        print(f"\n🎯 ASTRA PROJECT DEBUG REPORT")
        print(f"{'='*60}")
        print(f"⏱️  Execution Time: {results['execution_time']:.2f}s")
        print(f"📅 Generated: {results['timestamp']}")
        print(f"🏥 Overall Health: {results['summary']['overall_health']}")
        
        # Resumo
        print(f"\n📊 SUMMARY")
        print(f"{'─'*30}")
        print(f"🔴 Critical Issues: {results['summary']['critical_issues']}")
        print(f"🟡 Warnings: {results['summary']['warnings']}")
        print(f"💡 Recommendations: {results['summary']['recommendations_count']}")
        
        # Estrutura
        print(f"\n📁 PROJECT STRUCTURE")
        print(f"{'─'*30}")
        for dir_name, info in results['structure']['directories'].items():
            status = "✅" if info['exists'] else "❌"
            files = f"({info['files_count']} files)" if info['exists'] else ""
            size = f"({info['size_mb']}MB)" if info['exists'] else ""
            print(f"{status} {dir_name:<15} {files:<12} {size}")
        
        # Dependências
        print(f"\n📦 DEPENDENCIES")
        print(f"{'─'*30}")
        print(f"🐍 Python: {results['dependencies']['python_version']}")
        print(f"💻 Platform: {results['dependencies']['platform']}")
        
        missing = results['dependencies']['missing_packages']
        if missing:
            print(f"❌ Missing: {', '.join(missing)}")
        
        installed_count = len([p for p in results['dependencies']['installed_packages'].values() 
                             if p['status'] == 'OK'])
        total_count = len(results['dependencies']['installed_packages'])
        print(f"✅ Installed: {installed_count}/{total_count} packages")
        
        # Serviços
        print(f"\n🌐 EXTERNAL SERVICES")
        print(f"{'─'*30}")
        for service, info in results['dependencies']['services'].items():
            status_icon = {"ONLINE": "🟢", "OFFLINE": "🔴", "ERROR": "🟡"}.get(info['status'], "❓")
            print(f"{status_icon} {service.upper():<10} {info['status']}")
        
        # Performance
        print(f"\n🚀 PERFORMANCE")
        print(f"{'─'*30}")
        perf = results['performance']['system_resources']
        print(f"🖥️  CPU Usage: {perf.get('cpu_percent', 'N/A')}%")
        print(f"🧠 Memory: {perf.get('memory_percent', 'N/A')}%")
        print(f"💽 Disk: {perf.get('disk_usage_percent', 'N/A')}%")
        
        # Issues críticos
        if results['issues']:
            print(f"\n🔴 CRITICAL ISSUES")
            print(f"{'─'*30}")
            for issue in results['issues']:
                print(f"❌ [{issue['component']}] {issue['message']}")
        
        # Warnings
        if results['warnings']:
            print(f"\n🟡 WARNINGS")
            print(f"{'─'*30}")
            for warning in results['warnings']:
                print(f"⚠️  [{warning['component']}] {warning['message']}")
        
        # Recomendações
        if results['recommendations']:
            print(f"\n💡 RECOMMENDATIONS")
            print(f"{'─'*30}")
            for rec in results['recommendations']:
                priority_icon = {"HIGH": "🔥", "MEDIUM": "⚡", "LOW": "💭"}.get(rec['priority'], "💡")
                print(f"{priority_icon} [{rec['component']}] {rec['action']}")
        
        print(f"\n{'='*60}")
        print(f"🎉 Debug completo! Saúde geral: {results['summary']['overall_health']}")

def main():
    """Função principal do debug"""
    debugger = ASTRADebugger()
    results = debugger.run_full_debug()
    
    # Imprimir relatório detalhado
    debugger.print_detailed_report()
    
    # Salvar resultados em arquivo
    debug_file = Path(__file__).parent.parent / 'reports' / 'debug_results.json'
    with open(debug_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Resultados salvos em: {debug_file}")
    
    return results

if __name__ == "__main__":
    main()
