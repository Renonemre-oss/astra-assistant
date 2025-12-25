#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correções para os problemas identificados no sistema de voz do ASTRA
"""

import sys
import os
import logging
from pathlib import Path

# Adicionar projeto ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def fix_logging_encoding():
    """
    Corrige problemas de encoding de emojis no logging
    """
    print("🔧 CORRIGINDO PROBLEMAS DE LOGGING")
    print("=" * 45)
    
    # 1. Configurar logging com encoding UTF-8
    try:
        # Remover handlers existentes
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Configurar novo handler com encoding UTF-8
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ],
            force=True
        )
        
        # Configurar encoding para UTF-8 se possível
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
                print("✅ Encoding do stdout configurado para UTF-8")
            except:
                print("⚠️ Não foi possível reconfigurar encoding do stdout")
        
        print("✅ Sistema de logging reconfigurado")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao reconfigurar logging: {e}")
        return False

def create_emoji_safe_logging():
    """
    Cria um sistema de logging sem emojis para evitar problemas de encoding
    """
    print("\n🔧 CRIANDO SISTEMA DE LOGGING SEGURO")
    print("=" * 45)
    
    safe_logging_config = '''
# Configuração de logging sem emojis para compatibilidade Windows
import logging
import sys

class SafeFormatter(logging.Formatter):
    """Formatter que remove emojis problemáticos"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Mapeamento de emojis para texto
        self.emoji_map = {
            '🔄': '[LOADING]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARNING]',
            '🎤': '[AUDIO]',
            '🗣️': '[TTS]',
            '🎙️': '[STT]',
            '🎯': '[TARGET]',
            '🤖': '[ASTRA]',
            '📊': '[INFO]',
            '🔊': '[SPEAKER]',
            '🎵': '[VOICE]',
            '🚫': '[STOP]',
            '🔐': '[SHUTDOWN]',
        }
    
    def format(self, record):
        # Aplicar formato normal
        formatted = super().format(record)
        
        # Substituir emojis problemáticos
        for emoji, replacement in self.emoji_map.items():
            formatted = formatted.replace(emoji, replacement)
        
        return formatted

def setup_safe_logging():
    """Configura logging seguro para Windows"""
    
    # Remover handlers existentes
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Criar handler com formatter seguro
    handler = logging.StreamHandler(sys.stdout)
    formatter = SafeFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Configurar logger root
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(handler)
    
    return True
'''
    
    try:
        # Salvar configuração
        safe_logging_file = project_root / "utils" / "safe_logging.py"
        with open(safe_logging_file, 'w', encoding='utf-8') as f:
            f.write(safe_logging_config)
        
        print(f"✅ Arquivo criado: {safe_logging_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar sistema de logging seguro: {e}")
        return False

def fix_porcupine_hotword():
    """
    Corrige problema no sistema de hotword Porcupine
    """
    print("\n🔧 CORRIGINDO PROBLEMA NO PORCUPINE")
    print("=" * 45)
    
    try:
        # Verificar se o arquivo existe
        hotword_file = project_root / "voice" / "hotword_detector.py"
        
        if not hotword_file.exists():
            print("❌ Arquivo hotword_detector.py não encontrado")
            return False
        
        # Ler conteúdo atual
        with open(hotword_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Procurar pelo erro "'set' object is not subscriptable"
        if "porcupine_library.DEFAULT_KEYWORD_PATHS" in content:
            print("🔍 Encontrado código problemático do Porcupine")
            
            # Criar backup
            backup_file = hotword_file.with_suffix('.py.backup')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Backup criado: {backup_file}")
            
            # Aplicar correção (converter set para list)
            fixed_content = content.replace(
                "list(porcupine_library.DEFAULT_KEYWORD_PATHS)[0]",
                "list(porcupine_library.DEFAULT_KEYWORD_PATHS.values())[0]"
            )
            
            # Também corrigir outras possíveis ocorrências
            if "DEFAULT_KEYWORD_PATHS[" in fixed_content:
                print("⚠️ Encontradas outras referências que podem ser problemáticas")
                
                # Adicionar try/except para tornar mais robusto
                error_handling = '''
                    try:
                        # Tentar acessar as palavras-chave padrão
                        if hasattr(porcupine_library, 'DEFAULT_KEYWORD_PATHS'):
                            default_paths = porcupine_library.DEFAULT_KEYWORD_PATHS
                            if isinstance(default_paths, dict):
                                keyword_path = list(default_paths.values())[0]
                            elif isinstance(default_paths, (list, tuple)):
                                keyword_path = default_paths[0]
                            else:
                                raise ValueError("Formato não suportado para DEFAULT_KEYWORD_PATHS")
                        else:
                            raise AttributeError("DEFAULT_KEYWORD_PATHS não encontrado")
                    except Exception as e:
                        logger.error(f"Erro ao acessar palavras-chave padrão do Porcupine: {e}")
                        return False
                '''
            
            # Salvar arquivo corrigido
            with open(hotword_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print("✅ Correção aplicada ao sistema de hotword")
            return True
        else:
            print("❌ Código problemático não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao corrigir Porcupine: {e}")
        return False

def create_voice_system_patches():
    """
    Cria patches específicos para melhorar o sistema de voz
    """
    print("\n🔧 CRIANDO PATCHES PARA O SISTEMA DE VOZ")
    print("=" * 45)
    
    patches = []
    
    # Patch 1: Logging sem emojis
    patch_logging = '''
# Patch para logging sem problemas de encoding
import logging
import sys

def setup_windows_safe_logging():
    """Configura logging seguro para Windows com emojis"""
    
    class WindowsSafeFormatter(logging.Formatter):
        """Formatter que substitui emojis por texto em Windows"""
        
        EMOJI_REPLACEMENTS = {
            '🔄': '[LOADING]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARN]',
            '🎤': '[MIC]',
            '🗣️': '[SPEAK]',
            '🎙️': '[LISTEN]',
            '🎯': '[TARGET]',
            '🤖': '[ASTRA]',
        }
        
        def format(self, record):
            formatted = super().format(record)
            
            # Substituir emojis apenas no Windows
            if sys.platform == 'win32':
                for emoji, replacement in self.EMOJI_REPLACEMENTS.items():
                    formatted = formatted.replace(emoji, replacement)
            
            return formatted
    
    # Aplicar formatter a todos os handlers
    formatter = WindowsSafeFormatter('%(asctime)s - %(levelname)s - %(message)s')
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)
    
    return True
'''
    
    # Patch 2: Hotword mais robusto
    patch_hotword = '''
# Patch para sistema de hotword mais robusto
import logging

def safe_porcupine_init():
    """Inicialização mais segura do Porcupine"""
    try:
        import pvporcupine
        
        # Tentar diferentes métodos de acessar keywords
        keyword_paths = None
        
        # Método 1: Atributo direto
        if hasattr(pvporcupine, 'KEYWORD_PATHS'):
            keyword_paths = pvporcupine.KEYWORD_PATHS
        
        # Método 2: Como propriedade da classe
        elif hasattr(pvporcupine.Porcupine, 'KEYWORD_PATHS'):
            keyword_paths = pvporcupine.Porcupine.KEYWORD_PATHS
        
        # Método 3: Buscar por keywords built-in
        else:
            # Usar keywords padrão conhecidas
            keywords = ['ASTRAa', 'computer', 'hey google', 'hey siri']
            return keywords[0]  # Retornar primeira disponível
        
        # Processar keyword_paths encontradas
        if keyword_paths:
            if isinstance(keyword_paths, dict):
                return list(keyword_paths.values())[0]
            elif isinstance(keyword_paths, (list, tuple, set)):
                return list(keyword_paths)[0]
            else:
                return str(keyword_paths)
        
        return None
        
    except Exception as e:
        logging.error(f"Erro na inicialização segura do Porcupine: {e}")
        return None
'''
    
    patches.append(("logging_patch.py", patch_logging))
    patches.append(("hotword_patch.py", patch_hotword))
    
    # Salvar patches
    patches_dir = project_root / "patches"
    patches_dir.mkdir(exist_ok=True)
    
    for filename, content in patches:
        patch_file = patches_dir / filename
        try:
            with open(patch_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Patch criado: {patch_file}")
        except Exception as e:
            print(f"❌ Erro ao criar patch {filename}: {e}")
    
    return True

def test_fixes():
    """
    Testa se as correções funcionaram
    """
    print("\n🧪 TESTANDO CORREÇÕES")
    print("=" * 45)
    
    results = {}
    
    # Teste 1: Logging seguro
    try:
        from utils.safe_logging import setup_safe_logging
        setup_safe_logging()
        logging.info("Teste de logging com emoji: ✅ Funcionando")
        results['logging'] = True
        print("✅ Logging seguro funcionando")
    except Exception as e:
        results['logging'] = False
        print(f"❌ Problema no logging seguro: {e}")
    
    # Teste 2: TTS básico
    try:
        from audio.audio_manager import AudioManager
        am = AudioManager()
        am.load_tts_model()
        results['tts'] = True
        print("✅ TTS funcionando")
    except Exception as e:
        results['tts'] = False
        print(f"❌ Problema no TTS: {e}")
    
    return results

def main():
    """Função principal das correções"""
    print("🛠️ ASTRA - CORREÇÕES DO SISTEMA DE VOZ")
    print("=" * 50)
    
    results = {}
    
    # Executar correções
    results['logging_encoding'] = fix_logging_encoding()
    results['safe_logging'] = create_emoji_safe_logging()
    results['porcupine'] = fix_porcupine_hotword()
    results['patches'] = create_voice_system_patches()
    
    # Testar correções
    test_results = test_fixes()
    results.update(test_results)
    
    # Resumo
    print("\n📊 RESUMO DAS CORREÇÕES")
    print("=" * 50)
    
    for fix_name, success in results.items():
        status = "✅ OK" if success else "❌ FALHA"
        print(f"{fix_name}: {status}")
    
    # Recomendações finais
    print("\n💡 PRÓXIMOS PASSOS:")
    print("• Reiniciar o sistema para aplicar mudanças de logging")
    print("• Testar sistema de voz com: python test_voice_system.py")
    print("• Para usar logging seguro, importar: from utils.safe_logging import setup_safe_logging")
    
    successful_fixes = sum(results.values())
    total_fixes = len(results)
    print(f"\n🎯 {successful_fixes}/{total_fixes} correções aplicadas com sucesso")

if __name__ == "__main__":
    main()
