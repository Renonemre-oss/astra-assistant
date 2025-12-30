#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal
Módulo de Processamento de Texto

Funções para OCR, processamento de imagens e análise de texto.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict
from ..config import TESSERACT_AVAILABLE, DEPENDENCIES

logger = logging.getLogger(__name__)

# ==========================
# PROCESSAMENTO DE IMAGENS (OCR)
# ==========================
def processar_imagem(image_path: str) -> str:
    """
    Extrai texto de uma imagem usando OCR (Tesseract).
    
    Args:
        image_path: Caminho para o arquivo de imagem
        
    Returns:
        str: Texto extraído da imagem ou mensagem de erro
    """
    if not TESSERACT_AVAILABLE:
        return "OCR não disponível. Tesseract não foi encontrado."
    
    if not DEPENDENCIES.get('pytesseract', False):
        return "OCR não disponível. Pytesseract não instalado."
    
    if not DEPENDENCIES.get('PIL', False):
        return "OCR não disponível. PIL (Pillow) não instalado."
    
    try:
        import pytesseract
        from PIL import Image
        
        # Verificar se arquivo existe
        if not Path(image_path).exists():
            logger.error(f"Arquivo de imagem não encontrado: {image_path}")
            return "Erro: Arquivo de imagem não encontrado."
        
        # Carregar e verificar imagem
        logger.info(f"Processando imagem: {image_path}")
        img = Image.open(image_path)
        
        # Verificar se imagem não está vazia/corrompida
        if img.size[0] == 0 or img.size[1] == 0:
            return "Erro: Imagem vazia ou corrompida."
            
        # Tentar OCR com diferentes idiomas
        try:
            text = pytesseract.image_to_string(img, lang='por+eng')  # Português e Inglês
        except pytesseract.TesseractError:
            # Fallback para inglês apenas
            logger.warning("Fallback para OCR apenas em inglês")
            text = pytesseract.image_to_string(img, lang='eng')
            
        text = text.strip()
        if text:
            logger.info(f"Texto extraído: {len(text)} caracteres")
            return text
        else:
            logger.warning("Nenhum texto encontrado na imagem")
            return "Nenhum texto foi encontrado na imagem."
            
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {image_path}")
        return "Erro: Arquivo de imagem não encontrado."
    except PermissionError:
        logger.error(f"Permissão negada para acessar: {image_path}")
        return "Erro: Permissão negada para acessar o arquivo."
    except Exception as e:
        logger.error(f"Erro ao processar imagem '{image_path}': {str(e)}")
        return f"Erro ao processar a imagem: {str(e)[:100]}..."

def validar_imagem(image_path: str) -> bool:
    """
    Valida se um arquivo é uma imagem válida.
    
    Args:
        image_path: Caminho para o arquivo
        
    Returns:
        bool: True se for uma imagem válida
    """
    try:
        if not DEPENDENCIES.get('PIL', False):
            return False
            
        from PIL import Image
        
        # Verificar extensão
        valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        if Path(image_path).suffix.lower() not in valid_extensions:
            return False
        
        # Tentar abrir a imagem
        with Image.open(image_path) as img:
            img.verify()  # Verificar se é uma imagem válida
            return True
            
    except Exception as e:
        logger.warning(f"Imagem inválida '{image_path}': {e}")
        return False

def otimizar_imagem_para_ocr(image_path: str, output_path: str = None) -> str:
    """
    Otimiza uma imagem para melhorar a precisão do OCR.
    
    Args:
        image_path: Caminho da imagem original
        output_path: Caminho para salvar a imagem otimizada (opcional)
        
    Returns:
        str: Caminho da imagem otimizada ou mensagem de erro
    """
    if not DEPENDENCIES.get('PIL', False):
        return image_path  # Retorna original se não pode otimizar
    
    try:
        from PIL import Image, ImageFilter, ImageEnhance
        
        # Carregar imagem
        img = Image.open(image_path)
        
        # Converter para escala de cinza
        if img.mode != 'L':
            img = img.convert('L')
        
        # Aumentar contraste
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # Aumentar nitidez
        img = img.filter(ImageFilter.SHARPEN)
        
        # Redimensionar se muito pequena (mínimo 300px width)
        width, height = img.size
        if width < 300:
            scale_factor = 300 / width
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Salvar imagem otimizada
        if not output_path:
            output_path = str(Path(image_path).with_suffix('.optimized.png'))
        
        img.save(output_path, 'PNG', optimize=True)
        logger.info(f"Imagem otimizada salva: {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.warning(f"Erro ao otimizar imagem: {e}")
        return image_path  # Retorna original se otimização falhar

# ==========================
# ANÁLISE DE TEXTO
# ==========================
def analisar_sentimento_basico(texto: str) -> Dict[str, any]:
    """
    Análise básica de sentimento do texto.
    
    Args:
        texto: Texto para analisar
        
    Returns:
        Dict: Resultado da análise
    """
    if not texto or not texto.strip():
        return {"sentimento": "neutro", "confiança": 0.0, "palavras_chave": []}
    
    # Palavras positivas e negativas em português
    palavras_positivas = {
        'bom', 'ótimo', 'excelente', 'fantástico', 'maravilhoso', 'perfeito',
        'feliz', 'alegre', 'contente', 'satisfeito', 'gosto', 'adoro', 'amo',
        'incrível', 'espetacular', 'genial', 'fixe', 'bacano', 'legal'
    }
    
    palavras_negativas = {
        'mau', 'péssimo', 'terrível', 'horrível', 'odioso', 'detesto', 'odeio',
        'triste', 'deprimido', 'chateado', 'irritado', 'zangado', 'furioso',
        'problemático', 'difícil', 'complicado', 'chato', 'aborrecido'
    }
    
    palavras = texto.lower().split()
    score_positivo = sum(1 for palavra in palavras if palavra in palavras_positivas)
    score_negativo = sum(1 for palavra in palavras if palavra in palavras_negativas)
    
    # Determinar sentimento
    if score_positivo > score_negativo:
        sentimento = "positivo"
        confiança = min(0.9, 0.5 + (score_positivo - score_negativo) * 0.1)
    elif score_negativo > score_positivo:
        sentimento = "negativo" 
        confiança = min(0.9, 0.5 + (score_negativo - score_positivo) * 0.1)
    else:
        sentimento = "neutro"
        confiança = 0.5
    
    # Palavras-chave encontradas
    palavras_chave = [p for p in palavras if p in palavras_positivas or p in palavras_negativas]
    
    return {
        "sentimento": sentimento,
        "confiança": confiança,
        "palavras_chave": palavras_chave,
        "score_positivo": score_positivo,
        "score_negativo": score_negativo
    }

def extrair_palavras_chave(texto: str, num_palavras: int = 5) -> List[str]:
    """
    Extrai palavras-chave mais importantes do texto.
    
    Args:
        texto: Texto para analisar
        num_palavras: Número de palavras-chave a retornar
        
    Returns:
        List[str]: Lista de palavras-chave
    """
    if not texto or not texto.strip():
        return []
    
    # Palavras a ignorar (stop words em português)
    stop_words = {
        'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das',
        'em', 'no', 'na', 'nos', 'nas', 'para', 'por', 'com', 'sem', 'sob', 'sobre',
        'e', 'ou', 'mas', 'que', 'se', 'quando', 'onde', 'como', 'porque', 'então',
        'é', 'são', 'foi', 'foram', 'ser', 'estar', 'tem', 'ter', 'havia', 'há',
        'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas', 'me', 'te', 'se',
        'meu', 'minha', 'meus', 'minhas', 'teu', 'tua', 'seu', 'sua', 'nosso', 'nossa',
        'este', 'esta', 'esse', 'essa', 'aquele', 'aquela', 'isto', 'isso', 'aquilo',
        'muito', 'mais', 'menos', 'bem', 'mal', 'só', 'também', 'já', 'ainda', 'não'
    }
    
    # Limpar e dividir texto
    import re
    texto_limpo = re.sub(r'[^\w\s]', ' ', texto.lower())
    palavras = texto_limpo.split()
    
    # Filtrar stop words e palavras muito curtas
    palavras_filtradas = [
        palavra for palavra in palavras 
        if len(palavra) > 2 and palavra not in stop_words
    ]
    
    # Contar frequência
    from collections import Counter
    contador = Counter(palavras_filtradas)
    
    # Retornar as mais frequentes
    return [palavra for palavra, freq in contador.most_common(num_palavras)]

def detectar_idioma_basico(texto: str) -> str:
    """
    Detecção básica do idioma do texto.
    
    Args:
        texto: Texto para analisar
        
    Returns:
        str: Código do idioma detectado ('pt', 'en', 'es', etc.)
    """
    if not texto or len(texto.strip()) < 10:
        return 'pt'  # Padrão português
    
    # Palavras características de cada idioma
    indicadores = {
        'pt': ['que', 'com', 'para', 'são', 'mais', 'uma', 'está', 'como', 'muito', 'também'],
        'en': ['the', 'and', 'for', 'are', 'with', 'you', 'that', 'this', 'have', 'from'],
        'es': ['que', 'con', 'para', 'son', 'más', 'una', 'está', 'como', 'muy', 'también'],
        'fr': ['que', 'avec', 'pour', 'sont', 'plus', 'une', 'est', 'comme', 'très', 'aussi']
    }
    
    texto_lower = texto.lower()
    scores = {}
    
    for idioma, palavras in indicadores.items():
        score = sum(1 for palavra in palavras if palavra in texto_lower)
        scores[idioma] = score
    
    # Retornar idioma com maior score
    return max(scores.keys(), key=lambda k: scores[k]) if scores else 'pt'

# ==========================
# FORMATAÇÃO DE TEXTO
# ==========================
def formatar_resposta(texto: str, max_linhas: int = 50) -> str:
    """
    Formata texto de resposta para exibição na interface.
    
    Args:
        texto: Texto a formatar
        max_linhas: Máximo de linhas
        
    Returns:
        str: Texto formatado
    """
    if not texto:
        return ""
    
    # Primeiro substituir placeholders
    texto = substituir_placeholders(texto)
    
    linhas = texto.split('\n')
    
    # Limitar número de linhas
    if len(linhas) > max_linhas:
        linhas = linhas[:max_linhas]
        linhas.append(f"... (texto truncado)")
    
    # Limitar largura das linhas
    max_chars_por_linha = 100
    linhas_formatadas = []
    
    for linha in linhas:
        if len(linha) <= max_chars_por_linha:
            linhas_formatadas.append(linha)
        else:
            # Quebrar linha longa
            palavras = linha.split(' ')
            linha_atual = ""
            
            for palavra in palavras:
                if len(linha_atual + palavra) <= max_chars_por_linha:
                    linha_atual += palavra + " "
                else:
                    if linha_atual:
                        linhas_formatadas.append(linha_atual.strip())
                    linha_atual = palavra + " "
            
            if linha_atual:
                linhas_formatadas.append(linha_atual.strip())
    
    return '\n'.join(linhas_formatadas)

def substituir_placeholders(texto: str) -> str:
    """
    Substitui placeholders no texto por valores reais.
    
    Args:
        texto (str): Texto com placeholders
        
    Returns:
        str: Texto com placeholders substituídos
    """
    if not texto:
        return texto
    
    try:
        from datetime import datetime
        agora = datetime.now()
        
        # Detectar se há placeholders no texto
        placeholders_encontrados = False
        
        # Mapeamento de placeholders para valores reais
        substituicoes = {
            '[hora atual]': agora.strftime('%H:%M'),
            '[data atual]': agora.strftime('%d/%m/%Y'),
            '[data e hora atual]': agora.strftime('%H:%M de %d/%m/%Y')
        }
        
        # Placeholders especiais que precisam de formatação específica
        if '[data completa]' in texto:
            dias_semana = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
            meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
            dia_semana = dias_semana[agora.weekday()]
            mes = meses[agora.month - 1]
            data_completa = f"{agora.strftime('%H:%M')} de {dia_semana}, {agora.day} de {mes} de {agora.year}"
            substituicoes['[data completa]'] = data_completa
        
        # Realizar substituições
        for placeholder, valor in substituicoes.items():
            if placeholder in texto:
                texto = texto.replace(placeholder, valor)
                placeholders_encontrados = True
        
        # Log da substituição se placeholders foram encontrados
        if placeholders_encontrados:
            logger.info("✅ Placeholders de data/hora substituídos na resposta")
        
        return texto
        
    except Exception as e:
        logger.error(f"❌ Erro ao substituir placeholders: {e}")
        return texto

def extrair_urls(texto: str) -> List[str]:
    """
    Extrai URLs do texto.
    
    Args:
        texto: Texto para analisar
        
    Returns:
        List[str]: Lista de URLs encontradas
    """
    import re
    
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(pattern, texto)
    
    return urls

# ==========================
# FUNÇÕES DE TESTE
# ==========================
def testar_ocr():
    """Testa a funcionalidade de OCR."""
    print("🔍 TESTE DE OCR")
    print("-" * 30)
    
    if not TESSERACT_AVAILABLE:
        print("❌ Tesseract não disponível")
        return
    
    print("✅ OCR disponível")
    print("Para testar, use uma imagem com texto.")

def testar_analise_texto():
    """Testa análise de texto."""
    print("\n📝 TESTE DE ANÁLISE DE TEXTO")
    print("-" * 30)
    
    textos_teste = [
        "Estou muito feliz hoje! O dia está fantástico!",
        "Que dia terrível... Estou muito chateado.",
        "O assistente ASTRA funciona bem com Python e MySQL."
    ]
    
    for texto in textos_teste:
        print(f"\nTexto: '{texto}'")
        
        # Sentimento
        sentimento = analisar_sentimento_basico(texto)
        print(f"Sentimento: {sentimento['sentimento']} (confiança: {sentimento['confiança']:.2f})")
        
        # Palavras-chave
        palavras_chave = extrair_palavras_chave(texto)
        print(f"Palavras-chave: {palavras_chave}")
        
        # Idioma
        idioma = detectar_idioma_basico(texto)
        print(f"Idioma: {idioma}")

if __name__ == "__main__":
    print("📄 PROCESSADOR DE TEXTO DO ASTRA")
    print("=" * 40)
    
    testar_ocr()
    testar_analise_texto()
