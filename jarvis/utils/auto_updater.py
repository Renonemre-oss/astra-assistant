#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 JARVIS AUTO-UPDATER
Sistema de atualização automática com verificação de versões e download seguro
"""

import os
import sys
import json
import logging
import requests
import hashlib
import zipfile
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime
import tempfile

logger = logging.getLogger(__name__)


class Version:
    """Gerenciador de versões semânticas"""
    
    def __init__(self, version_string: str):
        """
        Inicializa versão a partir de string (ex: "2.0.1")
        
        Args:
            version_string: String da versão (formato: major.minor.patch)
        """
        parts = version_string.split('.')
        self.major = int(parts[0]) if len(parts) > 0 else 0
        self.minor = int(parts[1]) if len(parts) > 1 else 0
        self.patch = int(parts[2]) if len(parts) > 2 else 0
    
    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def __eq__(self, other):
        return (self.major == other.major and 
                self.minor == other.minor and 
                self.patch == other.patch)
    
    def __lt__(self, other):
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        return self.patch < other.patch
    
    def __gt__(self, other):
        return not (self < other or self == other)
    
    def __le__(self, other):
        return self < other or self == other
    
    def __ge__(self, other):
        return self > other or self == other


class JarvisUpdater:
    """Sistema de atualização automática do Jarvis"""
    
    # URLs de atualização (configurar com seu repositório)
    UPDATE_SERVER = "https://api.github.com/repos/YOUR_USERNAME/jarvis"
    RELEASES_URL = f"{UPDATE_SERVER}/releases/latest"
    
    def __init__(self, current_version: str = "2.0.0"):
        """
        Inicializa o atualizador.
        
        Args:
            current_version: Versão atual do Jarvis
        """
        self.current_version = Version(current_version)
        self.project_root = Path(__file__).parent.parent
        self.update_dir = self.project_root / ".updates"
        self.backup_dir = self.project_root / ".backups"
        
        # Criar diretórios
        self.update_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Arquivo de configuração de atualizações
        self.config_file = self.project_root / "config" / "update_config.json"
        self.load_config()
    
    def load_config(self):
        """Carrega configurações de atualização"""
        default_config = {
            "auto_check": True,
            "auto_download": False,
            "auto_install": False,
            "check_interval_hours": 24,
            "update_channel": "stable",  # stable, beta, dev
            "last_check": None,
            "skip_version": None
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = {**default_config, **json.load(f)}
            except Exception as e:
                logger.error(f"Erro ao carregar config de atualização: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Salva configurações de atualização"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Erro ao salvar config de atualização: {e}")
    
    def check_for_updates(self, force: bool = False) -> Optional[Dict]:
        """
        Verifica se há atualizações disponíveis.
        
        Args:
            force: Forçar verificação mesmo se recente
            
        Returns:
            Dict com informações da atualização ou None
        """
        logger.info("🔍 Verificando atualizações...")
        
        # Verificar se deve checar
        if not force and not self._should_check():
            logger.info("⏭️ Verificação de atualizações pulada (muito recente)")
            return None
        
        try:
            # Fazer requisição para API de releases
            response = requests.get(
                self.RELEASES_URL,
                timeout=10,
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            
            if response.status_code != 200:
                logger.warning(f"⚠️ Erro ao verificar atualizações: {response.status_code}")
                return None
            
            release_data = response.json()
            
            # Extrair informações
            latest_version = Version(release_data['tag_name'].lstrip('v'))
            
            # Atualizar last_check
            self.config['last_check'] = datetime.now().isoformat()
            self.save_config()
            
            # Verificar se há atualização
            if latest_version > self.current_version:
                update_info = {
                    'version': str(latest_version),
                    'current_version': str(self.current_version),
                    'release_name': release_data.get('name', 'Nova versão'),
                    'release_notes': release_data.get('body', 'Sem notas de lançamento'),
                    'download_url': self._get_download_url(release_data),
                    'published_at': release_data.get('published_at'),
                    'is_prerelease': release_data.get('prerelease', False),
                    'size': self._get_download_size(release_data)
                }
                
                logger.info(f"✨ Nova versão disponível: {latest_version}")
                return update_info
            else:
                logger.info(f"✅ Jarvis está atualizado (v{self.current_version})")
                return None
                
        except requests.RequestException as e:
            logger.error(f"❌ Erro de rede ao verificar atualizações: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao verificar atualizações: {e}")
            return None
    
    def _should_check(self) -> bool:
        """Verifica se deve fazer check de atualização"""
        if not self.config['auto_check']:
            return False
        
        last_check = self.config.get('last_check')
        if not last_check:
            return True
        
        try:
            last_check_time = datetime.fromisoformat(last_check)
            hours_since = (datetime.now() - last_check_time).total_seconds() / 3600
            return hours_since >= self.config['check_interval_hours']
        except:
            return True
    
    def _get_download_url(self, release_data: Dict) -> Optional[str]:
        """Extrai URL de download dos assets da release"""
        assets = release_data.get('assets', [])
        
        # Procurar por arquivo .zip
        for asset in assets:
            if asset['name'].endswith('.zip'):
                return asset['browser_download_url']
        
        # Fallback: zipball_url
        return release_data.get('zipball_url')
    
    def _get_download_size(self, release_data: Dict) -> Optional[int]:
        """Extrai tamanho do download"""
        assets = release_data.get('assets', [])
        for asset in assets:
            if asset['name'].endswith('.zip'):
                return asset.get('size', 0)
        return None
    
    def download_update(self, update_info: Dict, 
                       progress_callback: Optional[callable] = None) -> Optional[Path]:
        """
        Baixa a atualização.
        
        Args:
            update_info: Informações da atualização
            progress_callback: Callback para progresso (recebe bytes baixados e total)
            
        Returns:
            Path do arquivo baixado ou None
        """
        download_url = update_info.get('download_url')
        if not download_url:
            logger.error("❌ URL de download não disponível")
            return None
        
        logger.info(f"📥 Baixando atualização v{update_info['version']}...")
        
        try:
            # Fazer download com stream
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Nome do arquivo
            filename = f"jarvis_v{update_info['version']}.zip"
            download_path = self.update_dir / filename
            
            # Tamanho total
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            # Baixar em chunks
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            logger.info(f"✅ Download concluído: {download_path}")
            
            # Verificar integridade (se houver checksum)
            if self._verify_download(download_path, update_info):
                return download_path
            else:
                logger.error("❌ Falha na verificação de integridade")
                download_path.unlink()
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao baixar atualização: {e}")
            return None
    
    def _verify_download(self, file_path: Path, update_info: Dict) -> bool:
        """Verifica integridade do download"""
        # Implementar verificação de checksum se disponível
        # Por enquanto, apenas verifica se o arquivo existe e não está vazio
        return file_path.exists() and file_path.stat().st_size > 0
    
    def create_backup(self) -> Optional[Path]:
        """
        Cria backup da versão atual.
        
        Returns:
            Path do backup ou None
        """
        logger.info("💾 Criando backup da versão atual...")
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"jarvis_backup_v{self.current_version}_{timestamp}.zip"
            backup_path = self.backup_dir / backup_name
            
            # Criar zip do projeto
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.project_root):
                    # Ignorar diretórios de backup, updates, cache, etc
                    dirs[:] = [d for d in dirs if d not in 
                              ['.backups', '.updates', '__pycache__', '.git', 
                               'logs', 'data', 'venv', 'env']]
                    
                    for file in files:
                        if file.endswith(('.py', '.json', '.yaml', '.yml', '.txt', '.md')):
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(self.project_root)
                            zipf.write(file_path, arcname)
            
            logger.info(f"✅ Backup criado: {backup_path}")
            
            # Limpar backups antigos (manter apenas últimos 5)
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
            return None
    
    def _cleanup_old_backups(self, keep: int = 5):
        """Remove backups antigos, mantendo apenas os mais recentes"""
        try:
            backups = sorted(
                self.backup_dir.glob("jarvis_backup_*.zip"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # Remover backups excedentes
            for backup in backups[keep:]:
                backup.unlink()
                logger.info(f"🗑️ Backup antigo removido: {backup.name}")
                
        except Exception as e:
            logger.error(f"Erro ao limpar backups: {e}")
    
    def install_update(self, update_file: Path) -> bool:
        """
        Instala a atualização.
        
        Args:
            update_file: Path do arquivo de atualização
            
        Returns:
            True se instalado com sucesso
        """
        logger.info(f"📦 Instalando atualização de {update_file}...")
        
        try:
            # Criar backup primeiro
            backup = self.create_backup()
            if not backup:
                logger.error("❌ Falha ao criar backup - atualização cancelada")
                return False
            
            # Extrair atualização para diretório temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                logger.info("📂 Extraindo atualização...")
                with zipfile.ZipFile(update_file, 'r') as zipf:
                    zipf.extractall(temp_path)
                
                # Encontrar diretório raiz da extração
                extracted_dirs = list(temp_path.iterdir())
                if len(extracted_dirs) == 1 and extracted_dirs[0].is_dir():
                    source_dir = extracted_dirs[0]
                else:
                    source_dir = temp_path
                
                # Copiar arquivos atualizados
                logger.info("📋 Copiando arquivos atualizados...")
                self._copy_update_files(source_dir, self.project_root)
            
            logger.info("✅ Atualização instalada com sucesso!")
            logger.info("🔄 Reinicie o Jarvis para aplicar as mudanças")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao instalar atualização: {e}")
            logger.info("💾 Restaurando backup...")
            # Tentar restaurar backup
            if backup:
                self.restore_backup(backup)
            return False
    
    def _copy_update_files(self, source: Path, dest: Path):
        """Copia arquivos da atualização"""
        for item in source.rglob('*'):
            if item.is_file():
                # Calcular caminho relativo
                rel_path = item.relative_to(source)
                dest_path = dest / rel_path
                
                # Criar diretórios se necessário
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copiar arquivo
                shutil.copy2(item, dest_path)
    
    def restore_backup(self, backup_file: Path) -> bool:
        """
        Restaura um backup.
        
        Args:
            backup_file: Path do arquivo de backup
            
        Returns:
            True se restaurado com sucesso
        """
        logger.info(f"♻️ Restaurando backup de {backup_file}...")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extrair backup
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    zipf.extractall(temp_path)
                
                # Copiar arquivos
                self._copy_update_files(temp_path, self.project_root)
            
            logger.info("✅ Backup restaurado com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao restaurar backup: {e}")
            return False
    
    def auto_update(self) -> bool:
        """
        Executa atualização automática completa.
        
        Returns:
            True se atualizado
        """
        # Verificar atualizações
        update_info = self.check_for_updates()
        
        if not update_info:
            return False
        
        # Verificar se versão deve ser pulada
        if update_info['version'] == self.config.get('skip_version'):
            logger.info(f"⏭️ Versão {update_info['version']} marcada para pular")
            return False
        
        logger.info(f"✨ Nova versão disponível: {update_info['version']}")
        logger.info(f"📝 {update_info['release_name']}")
        
        # Baixar se configurado
        if not self.config.get('auto_download'):
            logger.info("ℹ️ Download automático desativado")
            return False
        
        # Callback de progresso
        def progress(downloaded, total):
            if total > 0:
                percent = (downloaded / total) * 100
                print(f"\r📥 Baixando: {percent:.1f}%", end='', flush=True)
        
        update_file = self.download_update(update_info, progress)
        print()  # Nova linha após progresso
        
        if not update_file:
            return False
        
        # Instalar se configurado
        if not self.config.get('auto_install'):
            logger.info("ℹ️ Instalação automática desativada")
            logger.info(f"💾 Atualização baixada em: {update_file}")
            return False
        
        return self.install_update(update_file)


def get_updater() -> JarvisUpdater:
    """Retorna instância do updater"""
    # Ler versão atual do __init__.py
    try:
        from jarvis import __version__
        version = __version__
    except:
        version = "2.0.0"
    
    return JarvisUpdater(version)


if __name__ == "__main__":
    # CLI para testes
    logging.basicConfig(level=logging.INFO)
    
    updater = get_updater()
    
    print("🔄 JARVIS AUTO-UPDATER")
    print("=" * 50)
    print(f"Versão atual: {updater.current_version}")
    print()
    
    # Verificar atualizações
    update = updater.check_for_updates(force=True)
    
    if update:
        print(f"\n✨ Nova versão disponível: {update['version']}")
        print(f"📝 {update['release_name']}")
        print(f"📅 Publicado em: {update['published_at']}")
        print(f"\n📋 Notas da versão:")
        print(update['release_notes'][:500])
    else:
        print("\n✅ Jarvis está atualizado!")
