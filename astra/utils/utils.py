#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal  
Módulo de Utilidades

Funções auxiliares e utilities para o sistema.
"""

import re
import requests
import json
import time
import logging
from typing import Optional, List, Dict, Any
from ..config import CONFIG, DEPENDENCIES

# ✅ Corrigido: Usar logger sem reconfigurar (centralizado em main_config)
logger = logging.getLogger(__name__)

# ==========================
# FUNÇÕES DE TEXTO
# ==========================
def remover_emojis(texto: str) -> str:
    """
    Remove emojis de uma string.
    ✅ Corrigido: Regex atualizado para cobrir todos os ranges Unicode modernos
    """
    emoji_pattern = re.compile(
        r"["
        r"\U0001F600-\U0001F64F"  # emoticons
        r"\U0001F300-\U0001F5FF"  # símbolos & pictogramas
        r"\U0001F680-\U0001F6FF"  # transporte & símbolos de mapas
        r"\U0001F1E0-\U0001F1FF"  # bandeiras (iOS)
        r"\U0001F900-\U0001F9FF"  # suplementos de símbolos e pictogramas
        r"\U0001FA00-\U0001FA6F"  # Chess Symbols
        r"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        r"\U00002702-\U000027B0"  # Dingbats
        r"\U000024C2-\U0001F251"  # Enclosed characters
        r"\U0001F910-\U0001F93E"  # Rostos suplementares
        r"\U0001F940-\U0001F970"  # Símbolos adicionais
        r"\U0001F980-\U0001F9E0"  # Animais e natureza
        r"\u200d"                   # Zero Width Joiner
        r"\ufe0f"                   # Variation Selector
        r"]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', texto)

def limpar_texto_tts(texto: str) -> str:
    """
    Limpa texto para TTS removendo caracteres problemáticos.
    """
    if not texto:
        return ""
    
    # Remover emojis primeiro
    texto = remover_emojis(texto)
    
    # Substituições para melhorar a pronúncia
    substituicoes = {
        # URLs e emails
        r'http[s]?://\S+': '[link]',
        r'\S+@\S+\.\S+': '[email]',
        
        # Caracteres especiais
        r'[^\w\s\.\!\?\,\;\:\-\(\)]': ' ',
        
        # Múltiplos espaços
        r'\s+': ' ',
        
        # Pontuação múltipla
        r'\.{2,}': '.',
        r'\!{2,}': '!',
        r'\?{2,}': '?',
    }
    
    for pattern, replacement in substituicoes.items():
        texto = re.sub(pattern, replacement, texto)
    
    return texto.strip()

def validar_entrada(texto: str, min_length: int = 1, max_length: int = 1000) -> bool:
    """
    Valida entrada do utilizador.
    """
    if not texto or not isinstance(texto, str):
        return False
    
    texto = texto.strip()
    return min_length <= len(texto) <= max_length

# ==========================
# PESQUISA NA INTERNET
# ==========================
def pesquisar_internet(query: str, num_results: int = 3) -> str:
    """
    Realiza uma pesquisa na internet usando DuckDuckGo com tratamento robusto de erros.
    """
    logger.info(f"Pesquisando: '{query}'")
    
    if not DEPENDENCIES.get('duckduckgo_search', False):
        logger.error("DuckDuckGo Search não está disponível")
        return "Pesquisa na internet indisponível. DuckDuckGo Search não instalado."
    
    if not query or not query.strip():
        return "Query de pesquisa vazia."
        
    try:
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query.strip(), max_results=num_results):
                if "href" in r and r["href"]:
                    results.append(r["href"])
                    
        if results:
            logger.info(f"Encontrados {len(results)} resultados para '{query}'")
            return "\n".join(results)
        else:
            logger.warning(f"Nenhum resultado encontrado para '{query}'")
            return "Não foram encontrados resultados relevantes."
            
    # ✅ Corrigido: Exception handling específico
    except ImportError as e:
        logger.error(f"Módulo duckduckgo_search não encontrado: {e}")
        return "Erro: Módulo de pesquisa não instalado."
    except (ConnectionError, TimeoutError) as e:
        logger.error(f"Erro de conexão na pesquisa '{query}': {str(e)}")
        return "Erro: Não foi possível conectar ao serviço de pesquisa."
    except Exception as e:
        logger.error(f"Erro inesperado na pesquisa '{query}': {str(e)}")
        return f"Erro ao pesquisar na internet: Serviço temporariamente indisponível."

# ==========================
# COMUNICAÇÃO COM OLLAMA
# ==========================
def perguntar_ollama(prompt: str, stop_signal, modelo: str = None, system_prompt: str = None) -> str:
    """
    Envia um prompt para o modelo Ollama com tratamento robusto de erros.
    """
    if not prompt or not prompt.strip():
        return "Prompt vazio."
        
    resposta_completa = ""
    max_retries = CONFIG["max_retries"]
    modelo_usado = modelo or CONFIG["ollama_model"]
    
    for tentativa in range(max_retries):
        try:
            if tentativa > 0:
                logger.info(f"Tentativa {tentativa + 1} de {max_retries} para Ollama")
                time.sleep(1)  # Pequeno delay entre tentativas
                
            logger.info(f"Enviando prompt para Ollama: '{prompt[:50]}...'")  # Log truncado
            
            request_json = {
                "model": modelo_usado, 
                "prompt": prompt.strip(), 
                "stream": True
            }
            if system_prompt:
                request_json["system"] = system_prompt
            
            response = requests.post(
                CONFIG["ollama_url"],
                json=request_json,
                stream=True,
                timeout=CONFIG["request_timeout"]
            )
            
            if response.status_code == 404:
                return f"Modelo '{modelo_usado}' não encontrado. Certifique-se de que o modelo está instalado no Ollama."
            elif response.status_code != 200:
                raise requests.RequestException(f"HTTP {response.status_code}: {response.text[:200]}")
                
            for linha in response.iter_lines():
                if stop_signal.is_set():
                    response.close()
                    logger.info("Requisição Ollama cancelada pelo utilizador")
                    return "Processo interrompido."
                    
                if linha:
                    try:
                        json_data = json.loads(linha.decode('utf-8'))
                        if 'response' in json_data:
                            resposta_completa += json_data['response']
                        if json_data.get('done', False):
                            break
                    except json.JSONDecodeError as json_err:
                        logger.warning(f"JSON inválido recebido: {json_err}")
                        continue
                        
            response.close()
            
            if resposta_completa.strip():
                logger.info(f"Resposta Ollama recebida: {len(resposta_completa)} caracteres")
                return resposta_completa.strip()
            else:
                raise ValueError("Resposta vazia do Ollama")
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout na tentativa {tentativa + 1} para Ollama")
            if tentativa == max_retries - 1:
                return "Timeout: O modelo está a demorar muito a responder. Tente novamente."
                
        except requests.exceptions.ConnectionError:
            logger.error(f"Erro de conexão na tentativa {tentativa + 1}")
            if tentativa == max_retries - 1:
                return "Erro: Não foi possível conectar ao Ollama. Verifique se o serviço está a funcionar."
                
        # ✅ Corrigido: Capturar requests.RequestException e outros erros específicos
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição Ollama tentativa {tentativa + 1}: {str(e)}")
            if tentativa == max_retries - 1:
                return f"Erro de comunicação com Ollama: {str(e)[:100]}..."
        except (ValueError, KeyError) as e:
            logger.error(f"Erro de dados Ollama tentativa {tentativa + 1}: {str(e)}")
            if tentativa == max_retries - 1:
                return f"Erro de processamento: {str(e)[:100]}..."
        except Exception as e:
            logger.error(f"Erro inesperado Ollama tentativa {tentativa + 1}: {str(e)}")
            if tentativa == max_retries - 1:
                return f"Erro interno: {str(e)[:100]}..."
                
    return "Falha após múltiplas tentativas. Tente novamente mais tarde."

# ==========================
# ARMAZENAMENTO LOCAL
# ==========================
def carregar_historico() -> List[Dict]:
    """
    Carrega o histórico de conversas do arquivo local.
    """
    try:
        history_file = CONFIG["history_file"]
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
    # ✅ Corrigido: Exception handling específico
    except (FileNotFoundError, PermissionError) as e:
        logger.warning(f"Histórico não acessível: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Histórico corrompido: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao carregar histórico: {e}")
    
    return []

def salvar_historico(history: List[Dict]) -> bool:
    """
    Salva o histórico de conversas no arquivo local.
    """
    try:
        history_file = CONFIG["history_file"]
        history_file.parent.mkdir(exist_ok=True)
        
        # Manter apenas os últimos registos para evitar ficheiros muito grandes
        max_entries = CONFIG["conversation_history_size"] * 10
        if len(history) > max_entries:
            history = history[-max_entries:]
        
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
            
        return True
        
    # ✅ Corrigido: Exception handling específico
    except (PermissionError, OSError) as e:
        logger.error(f"Erro de permissão/sistema ao salvar histórico: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado ao salvar histórico: {e}")
        return False

def carregar_lembretes() -> List[str]:
    """
    Carrega lembretes do arquivo local.
    """
    try:
        lembretes_file = CONFIG["lembretes_file"]
        if lembretes_file.exists():
            with open(lembretes_file, "r", encoding="utf-8") as f:
                return [linha.strip() for linha in f if linha.strip()]
    except Exception as e:
        logger.error(f"Erro ao carregar lembretes: {e}")
    
    return []

def salvar_lembrete(lembrete: str) -> bool:
    """
    Adiciona um lembrete ao arquivo local.
    """
    try:
        lembretes_file = CONFIG["lembretes_file"]
        lembretes_file.parent.mkdir(exist_ok=True)
        
        with open(lembretes_file, "a", encoding="utf-8") as f:
            f.write(f"{lembrete}\n")
            
        return True
        
    except Exception as e:
        logger.error(f"Erro ao salvar lembrete: {e}")
        return False

# ==========================
# VALIDAÇÕES E VERIFICAÇÕES
# ==========================
def verificar_servicos() -> Dict[str, bool]:
    """
    Verifica o status de todos os serviços externos.
    """
    status = {}
    
    # Verificar Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        status['ollama'] = response.status_code == 200
    except:
        status['ollama'] = False
    
    # Verificar MySQL (se disponível)
    if DEPENDENCIES.get('mysql.connector', False):
        try:
            from database_manager import DatabaseManager, DatabaseConfig
            db = DatabaseManager(DatabaseConfig())
            status['mysql'] = db.connect()
            if status['mysql']:
                db.disconnect()
        except:
            status['mysql'] = False
    else:
        status['mysql'] = False
    
    return status

def formatar_tempo_resposta(segundos: float) -> str:
    """
    Formata tempo de resposta de forma legível.
    """
    if segundos < 1:
        return f"{segundos*1000:.0f}ms"
    elif segundos < 60:
        return f"{segundos:.1f}s"
    else:
        minutos = int(segundos // 60)
        segundos_rest = segundos % 60
        return f"{minutos}m {segundos_rest:.1f}s"

# ==========================
# FUNÇÕES DE DEBUG
# ==========================
def debug_info() -> Dict[str, Any]:
    """
    Retorna informações de debug do sistema.
    """
    return {
        'dependencies': DEPENDENCIES,
        'services': verificar_servicos(),
        'config': {
            'model': CONFIG['ollama_model'],
            'history_size': CONFIG['conversation_history_size'],
            'data_dir': str(CONFIG['history_file'].parent)
        }
    }

if __name__ == "__main__":
    print("🔧 UTILITÁRIOS DO ASTRA")
    print("=" * 40)
    
    # Testar funções principais
    print("📝 Teste de limpeza de texto:")
    texto_teste = "Olá! 🤖 Como está? https://example.com 😊😊😊"
    print(f"Original: {texto_teste}")
    print(f"Limpo: {limpar_texto_tts(texto_teste)}")
    
    print("\n🔍 Status dos serviços:")
    servicos = verificar_servicos()
    for servico, status in servicos.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {servico.upper()}")
    
    print(f"\n📊 Debug info: {debug_info()}")
