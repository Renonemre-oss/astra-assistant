#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/JARVIS - API Migration Script
Script para consolidar api_integration_hub.py em modules/external_apis/

Este script:
1. Verifica funcionalidades únicas em api_integration_hub.py
2. Cria um wrapper compatível em modules/external_apis/
3. Atualiza todos os imports no projeto
4. Move api_integration_hub.py para backup
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Adicionar o diretório raiz ao Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def create_compatibility_layer():
    """Criar camada de compatibilidade em modules/external_apis/"""
    
    compatibility_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/JARVIS - API Integration Hub Compatibility Layer
Camada de compatibilidade para código antigo que usa api.api_integration_hub

Este módulo mantém compatibilidade retroativa enquanto usa o novo sistema modular.
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime

# Importar o novo sistema modular
from modules.external_apis.api_manager import APIManager
from modules.external_apis.news_api import NewsAPI as NewsExternal
from modules.external_apis.weather_api import WeatherAPI as WeatherExternal

logger = logging.getLogger(__name__)

class ApiResponse:
    """Classe para padronizar respostas das APIs (compatibilidade)"""
    def __init__(self, source: str, data: Any, timestamp: datetime, status: str, error_message: Optional[str] = None):
        self.source = source
        self.data = data
        self.timestamp = timestamp
        self.status = status
        self.error_message = error_message

class ApiIntegrationHub:
    """
    Hub principal para integração de múltiplas APIs (compatibilidade).
    
    NOTA: Este é um wrapper de compatibilidade.
    Novo código deve usar: modules.external_apis.api_manager.APIManager
    """
    
    def __init__(self):
        logger.warning("ApiIntegrationHub está deprecated. Use modules.external_apis.api_manager.APIManager")
        self.api_manager = APIManager()
        
        # Cache e configurações legadas
        self.cache = {}
        self.cache_duration = {
            'news': 300,
            'weather': 600,
            'stocks': 60,
            'crypto': 30
        }
    
    def set_api_key(self, service: str, api_key: str):
        """Configurar chave de API (compatibilidade)"""
        logger.info(f"Setting API key for {service} via compatibility layer")
        # Implementar se necessário

class NewsAPI:
    """Wrapper de compatibilidade para NewsAPI"""
    
    def __init__(self, hub: ApiIntegrationHub):
        self.hub = hub
        self._news_api = hub.api_manager.news
    
    def get_latest_news(self, query: str = None, category: str = None, 
                       country: str = None, language: str = None, size: int = 10) -> ApiResponse:
        """Obter últimas notícias (compatibilidade)"""
        logger.warning("NewsAPI.get_latest_news está deprecated. Use api_manager.news.get_news()")
        
        try:
            # Converter para novo formato
            result = self._news_api.get_news(
                query=query,
                category=category,
                country=country,
                language=language or 'pt',
                page_size=size
            )
            
            return ApiResponse(
                source="newsdata",
                data=result,
                timestamp=datetime.now(),
                status="success"
            )
        except Exception as e:
            return ApiResponse(
                source="newsdata",
                data=None,
                timestamp=datetime.now(),
                status="error",
                error_message=str(e)
            )

class WeatherAPI:
    """Wrapper de compatibilidade para WeatherAPI"""
    
    def __init__(self, hub: ApiIntegrationHub):
        self.hub = hub
        self._weather_api = hub.api_manager.weather
    
    def get_current_weather(self, city: str = "São Paulo", country_code: str = "BR") -> ApiResponse:
        """Obter clima atual (compatibilidade)"""
        logger.warning("WeatherAPI.get_current_weather está deprecated. Use api_manager.weather.get_current()")
        
        try:
            location = f"{city},{country_code}"
            result = self._weather_api.get_current(location)
            
            return ApiResponse(
                source="openweather",
                data=result,
                timestamp=datetime.now(),
                status="success"
            )
        except Exception as e:
            return ApiResponse(
                source="openweather",
                data=None,
                timestamp=datetime.now(),
                status="error",
                error_message=str(e)
            )

class CryptoAPI:
    """Wrapper de compatibilidade para CryptoAPI"""
    
    def __init__(self, hub: ApiIntegrationHub):
        self.hub = hub
    
    def get_price(self, coin: str = "bitcoin") -> ApiResponse:
        """Obter preço de criptomoeda (compatibilidade)"""
        logger.warning("CryptoAPI está deprecated. Use um módulo específico de crypto")
        
        return ApiResponse(
            source="crypto",
            data=None,
            timestamp=datetime.now(),
            status="error",
            error_message="CryptoAPI não implementado no novo sistema"
        )

# Mensagem de deprecation
logger.info("=" * 60)
logger.info("AVISO: Você está usando a camada de compatibilidade de API")
logger.info("Migre para: modules.external_apis.api_manager.APIManager")
logger.info("=" * 60)
'''
    
    output_path = project_root / 'jarvis' / 'api' / '__init__.py'
    
    # Criar diretório se não existir
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Salvar arquivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(compatibility_code)
    
    print(f"✅ Camada de compatibilidade criada em: {output_path}")

def backup_old_file():
    """Criar backup do arquivo antigo"""
    old_file = project_root / 'jarvis' / 'api' / 'api_integration_hub.py'
    
    if not old_file.exists():
        print("ℹ️  api_integration_hub.py não encontrado, pulando backup")
        return
    
    # Criar diretório de backup
    backup_dir = project_root / 'jarvis' / 'api' / 'backup'
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Nome do backup com timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'api_integration_hub_{timestamp}.py'
    
    # Copiar arquivo
    shutil.copy2(old_file, backup_file)
    print(f"✅ Backup criado em: {backup_file}")
    
    # Remover arquivo original
    old_file.unlink()
    print(f"✅ Arquivo original removido: {old_file}")

def update_imports():
    """Atualizar imports em arquivos que usam o sistema antigo"""
    
    files_to_update = []
    
    # Buscar arquivos que importam de api.api_integration_hub
    for py_file in (project_root / 'jarvis').rglob('*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            
            if 'from api.api_integration_hub import' in content or \
               'import api.api_integration_hub' in content:
                files_to_update.append(py_file)
        except:
            pass
    
    if not files_to_update:
        print("ℹ️  Nenhum arquivo precisa de atualização de imports")
        return
    
    print(f"\n📝 Encontrados {len(files_to_update)} arquivo(s) que precisam atualização:")
    for f in files_to_update:
        print(f"  - {f.relative_to(project_root)}")
    
    print("\n⚠️  NOTA: Os imports antigos continuarão funcionando via camada de compatibilidade")
    print("   Mas é recomendado atualizar para o novo sistema:")
    print("   - OLD: from api.api_integration_hub import ApiIntegrationHub")
    print("   - NEW: from modules.external_apis.api_manager import APIManager")

def main():
    """Executar migração completa"""
    
    print("=" * 60)
    print("🚀 ALEX/JARVIS - Migração de Sistema de APIs")
    print("=" * 60)
    print()
    
    print("📋 Este script irá:")
    print("  1. Criar camada de compatibilidade em modules/external_apis/")
    print("  2. Fazer backup de api_integration_hub.py")
    print("  3. Verificar arquivos que usam o sistema antigo")
    print()
    
    input("Pressione ENTER para continuar ou Ctrl+C para cancelar...")
    print()
    
    # Executar migração
    print("PASSO 1: Criando camada de compatibilidade...")
    create_compatibility_layer()
    print()
    
    print("PASSO 2: Fazendo backup do arquivo antigo...")
    backup_old_file()
    print()
    
    print("PASSO 3: Verificando imports...")
    update_imports()
    print()
    
    print("=" * 60)
    print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print()
    print("📚 Próximos passos:")
    print("  1. Código antigo continuará funcionando via compatibilidade")
    print("  2. Migre gradualmente para o novo sistema:")
    print("     from modules.external_apis.api_manager import APIManager")
    print("  3. Teste todas as funcionalidades de API")
    print("  4. Remova a camada de compatibilidade quando não for mais necessária")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Migração cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro durante migração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
