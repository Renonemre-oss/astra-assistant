
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
            keywords = ['alexa', 'computer', 'hey google', 'hey siri']
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
