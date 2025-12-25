#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Gerenciador de Assets
Sistema para gestão de recursos visuais e assets do projeto
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging
from dataclasses import dataclass
from enum import Enum

# Importar configurações do projeto
try:
    from config import CONFIG, PROJECT_ROOT
except ImportError:
    PROJECT_ROOT = Path(__file__).parent.parent
    CONFIG = {}

class AssetType(Enum):
    """Tipos de assets disponíveis."""
    LOGO = "logo"
    ICON = "icon"
    IMAGE = "image"
    UI_ELEMENT = "ui_element"
    FAVICON = "favicon"
    SPLASH = "splash"

class AssetFormat(Enum):
    """Formatos de arquivo suportados."""
    PNG = "png"
    ICO = "ico"
    SVG = "svg"
    JPEG = "jpeg"
    JPG = "jpg"
    GIF = "gif"
    WEBP = "webp"

@dataclass
class AssetInfo:
    """Informações sobre um asset."""
    name: str
    type: AssetType
    format: AssetFormat
    path: Path
    size: Optional[tuple] = None  # (width, height)
    description: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class AssetManager:
    """Gerenciador de assets do ASTRA."""
    
    def __init__(self, assets_dir: Optional[Path] = None):
        """
        Inicializa o gerenciador de assets.
        
        Args:
            assets_dir: Diretório base dos assets (padrão: PROJECT_ROOT/assets)
        """
        self.project_root = PROJECT_ROOT
        self.assets_dir = assets_dir or (self.project_root / "assets")
        self.logger = logging.getLogger(f"{__name__}.AssetManager")
        
        # Criar estrutura de diretórios se não existir
        self._ensure_directory_structure()
        
        # Cache de assets carregados
        self._assets_cache: Dict[str, AssetInfo] = {}
        
        # Carregar registry de assets
        self._load_assets_registry()
    
    def _ensure_directory_structure(self):
        """Garante que a estrutura de diretórios existe."""
        directories = [
            self.assets_dir / "logos",
            self.assets_dir / "icons", 
            self.assets_dir / "images",
            self.assets_dir / "ui",
            self.assets_dir / "favicons",
            self.assets_dir / "splash"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_assets_registry(self):
        """Carrega registry de assets do arquivo JSON."""
        registry_file = self.assets_dir / "assets_registry.json"
        
        if registry_file.exists():
            try:
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry_data = json.load(f)
                
                for asset_data in registry_data.get('assets', []):
                    asset = AssetInfo(
                        name=asset_data['name'],
                        type=AssetType(asset_data['type']),
                        format=AssetFormat(asset_data['format']),
                        path=Path(asset_data['path']),
                        size=tuple(asset_data['size']) if asset_data.get('size') else None,
                        description=asset_data.get('description', ''),
                        tags=asset_data.get('tags', [])
                    )
                    self._assets_cache[asset.name] = asset
                    
                self.logger.info(f"Registry carregado: {len(self._assets_cache)} assets")
                
            except Exception as e:
                self.logger.error(f"Erro ao carregar registry: {e}")
        else:
            # Criar registry inicial
            self._create_initial_registry()
    
    def _create_initial_registry(self):
        """Cria registry inicial com estrutura básica."""
        initial_assets = [
            {
                "name": "ASTRA_logo_main",
                "type": "logo",
                "format": "png",
                "path": "assets/logos/ASTRA_logo_main.png",
                "size": [512, 512],
                "description": "Logo principal do ASTRA - versão quadrada alta resolução",
                "tags": ["main", "primary", "high-res"]
            },
            {
                "name": "ASTRA_logo_horizontal",
                "type": "logo", 
                "format": "png",
                "path": "assets/logos/ASTRA_logo_horizontal.png",
                "size": [800, 300],
                "description": "Logo horizontal do ASTRA para interfaces largas",
                "tags": ["horizontal", "interface", "wide"]
            },
            {
                "name": "ASTRA_favicon",
                "type": "favicon",
                "format": "ico",
                "path": "assets/favicons/ASTRA_favicon.ico",
                "size": [32, 32],
                "description": "Favicon do ASTRA para navegadores e aplicações",
                "tags": ["favicon", "browser", "small"]
            },
            {
                "name": "ASTRA_app_icon",
                "type": "icon",
                "format": "ico",
                "path": "assets/icons/ASTRA_app_icon.ico",
                "size": [256, 256],
                "description": "Ícone da aplicação ASTRA para Windows",
                "tags": ["application", "windows", "desktop"]
            }
        ]
        
        registry = {
            "metadata": {
                "version": "1.0.0",
                "created": "2025-09-20",
                "description": "Registry de assets do ASTRA"
            },
            "assets": initial_assets
        }
        
        self._save_registry(registry)
    
    def _save_registry(self, registry_data: Dict[str, Any]):
        """Salva registry no arquivo JSON."""
        registry_file = self.assets_dir / "assets_registry.json"
        
        try:
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Registry salvo em {registry_file}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar registry: {e}")
    
    def add_asset(self, asset_info: AssetInfo) -> bool:
        """
        Adiciona um novo asset ao sistema.
        
        Args:
            asset_info: Informações do asset
            
        Returns:
            True se adicionado com sucesso
        """
        try:
            # Verificar se arquivo existe
            if not asset_info.path.exists():
                self.logger.warning(f"Arquivo não encontrado: {asset_info.path}")
                # Não falha, apenas avisa (pode ser adicionado antes do arquivo)
            
            # Adicionar ao cache
            self._assets_cache[asset_info.name] = asset_info
            
            # Atualizar registry
            self._update_registry()
            
            self.logger.info(f"Asset adicionado: {asset_info.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar asset: {e}")
            return False
    
    def get_asset(self, name: str) -> Optional[AssetInfo]:
        """
        Obtém informações de um asset pelo nome.
        
        Args:
            name: Nome do asset
            
        Returns:
            AssetInfo ou None se não encontrado
        """
        return self._assets_cache.get(name)
    
    def get_asset_path(self, name: str) -> Optional[Path]:
        """
        Obtém caminho de um asset pelo nome.
        
        Args:
            name: Nome do asset
            
        Returns:
            Path do asset ou None se não encontrado
        """
        asset = self.get_asset(name)
        return asset.path if asset else None
    
    def get_assets_by_type(self, asset_type: AssetType) -> List[AssetInfo]:
        """
        Obtém todos os assets de um tipo específico.
        
        Args:
            asset_type: Tipo de asset
            
        Returns:
            Lista de AssetInfo
        """
        return [asset for asset in self._assets_cache.values() 
                if asset.type == asset_type]
    
    def get_assets_by_tag(self, tag: str) -> List[AssetInfo]:
        """
        Obtém todos os assets com uma tag específica.
        
        Args:
            tag: Tag a procurar
            
        Returns:
            Lista de AssetInfo
        """
        return [asset for asset in self._assets_cache.values() 
                if tag in asset.tags]
    
    def list_all_assets(self) -> Dict[str, AssetInfo]:
        """
        Lista todos os assets carregados.
        
        Returns:
            Dicionário com todos os assets
        """
        return self._assets_cache.copy()
    
    def _update_registry(self):
        """Atualiza o arquivo de registry com os assets em cache."""
        assets_data = []
        
        for asset in self._assets_cache.values():
            asset_data = {
                "name": asset.name,
                "type": asset.type.value,
                "format": asset.format.value,
                "path": str(asset.path),
                "size": list(asset.size) if asset.size else None,
                "description": asset.description,
                "tags": asset.tags
            }
            assets_data.append(asset_data)
        
        registry = {
            "metadata": {
                "version": "1.0.0",
                "updated": "2025-09-20", 
                "description": "Registry de assets do ASTRA",
                "total_assets": len(assets_data)
            },
            "assets": assets_data
        }
        
        self._save_registry(registry)
    
    def get_logo_variants(self) -> Dict[str, AssetInfo]:
        """
        Obtém todas as variantes do logo do ASTRA.
        
        Returns:
            Dicionário com variantes do logo
        """
        logos = self.get_assets_by_type(AssetType.LOGO)
        return {logo.name: logo for logo in logos}
    
    def get_main_logo(self) -> Optional[AssetInfo]:
        """
        Obtém o logo principal do ASTRA.
        
        Returns:
            AssetInfo do logo principal
        """
        return self.get_asset("ASTRA_logo_main")
    
    def get_favicon(self) -> Optional[AssetInfo]:
        """
        Obtém o favicon do ASTRA.
        
        Returns:
            AssetInfo do favicon
        """
        return self.get_asset("ASTRA_favicon")
    
    def get_app_icon(self) -> Optional[AssetInfo]:
        """
        Obtém o ícone da aplicação.
        
        Returns:
            AssetInfo do ícone da aplicação
        """
        return self.get_asset("ASTRA_app_icon")
    
    def validate_assets(self) -> Dict[str, Any]:
        """
        Valida todos os assets registrados.
        
        Returns:
            Relatório de validação
        """
        report = {
            "total_assets": len(self._assets_cache),
            "valid_assets": 0,
            "missing_files": [],
            "invalid_assets": [],
            "warnings": []
        }
        
        for name, asset in self._assets_cache.items():
            if asset.path.exists():
                report["valid_assets"] += 1
            else:
                report["missing_files"].append({
                    "name": name,
                    "path": str(asset.path),
                    "type": asset.type.value
                })
        
        # Verificar se temos pelo menos um logo principal
        if not self.get_main_logo():
            report["warnings"].append("Logo principal não encontrado")
        
        return report
    
    def get_asset_url(self, name: str, relative: bool = True) -> Optional[str]:
        """
        Obtém URL/path do asset para uso em interfaces web/GUI.
        
        Args:
            name: Nome do asset
            relative: Se deve retornar path relativo
            
        Returns:
            String com URL/path do asset
        """
        asset = self.get_asset(name)
        if not asset:
            return None
        
        if relative:
            try:
                return str(asset.path.relative_to(self.project_root))
            except ValueError:
                return str(asset.path)
        else:
            return str(asset.path.absolute())
    
    def create_asset_html_tag(self, name: str, alt_text: str = "", 
                            css_class: str = "", width: int = None, 
                            height: int = None) -> str:
        """
        Cria tag HTML <img> para o asset.
        
        Args:
            name: Nome do asset
            alt_text: Texto alternativo
            css_class: Classe CSS
            width: Largura em pixels
            height: Altura em pixels
            
        Returns:
            String com tag HTML
        """
        asset = self.get_asset(name)
        if not asset:
            return f'<!-- Asset "{name}" não encontrado -->'
        
        url = self.get_asset_url(name, relative=True)
        if not url:
            return f'<!-- Erro ao obter URL do asset "{name}" -->'
        
        # Construir atributos
        attrs = [f'src="{url}"']
        
        if alt_text:
            attrs.append(f'alt="{alt_text}"')
        elif asset.description:
            attrs.append(f'alt="{asset.description}"')
        
        if css_class:
            attrs.append(f'class="{css_class}"')
        
        if width:
            attrs.append(f'width="{width}"')
        elif asset.size and not height:
            attrs.append(f'width="{asset.size[0]}"')
        
        if height:
            attrs.append(f'height="{height}"')
        elif asset.size and not width:
            attrs.append(f'height="{asset.size[1]}"')
        
        return f'<img {" ".join(attrs)} />'


# Instância global do gerenciador de assets
_asset_manager = None

def get_asset_manager() -> AssetManager:
    """
    Obtém instância global do gerenciador de assets.
    
    Returns:
        AssetManager: Instância do gerenciador
    """
    global _asset_manager
    if _asset_manager is None:
        _asset_manager = AssetManager()
    return _asset_manager

# Funções de conveniência
def get_logo_path() -> Optional[Path]:
    """Obtém caminho do logo principal."""
    return get_asset_manager().get_asset_path("ASTRA_logo_main")

def get_favicon_path() -> Optional[Path]:
    """Obtém caminho do favicon."""
    return get_asset_manager().get_asset_path("ASTRA_favicon")

def get_app_icon_path() -> Optional[Path]:
    """Obtém caminho do ícone da aplicação."""
    return get_asset_manager().get_asset_path("ASTRA_app_icon")

def create_logo_html(css_class: str = "ASTRA-logo", width: int = None) -> str:
    """Cria tag HTML para o logo principal."""
    return get_asset_manager().create_asset_html_tag(
        "ASTRA_logo_main", 
        alt_text="ASTRA - Assistente Pessoal",
        css_class=css_class,
        width=width
    )
