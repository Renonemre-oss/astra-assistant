#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/Astra - Document Processor
Processamento de documentos para RAG.
"""

import logging
from typing import List, Dict, Any
from pathlib import Path

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processa documentos para extração de texto."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Inicializa processador.
        
        Args:
            chunk_size: Tamanho de cada chunk (caracteres)
            chunk_overlap: Sobreposição entre chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Processa arquivo e retorna chunks com metadata.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Lista de chunks com metadata
        """
        if not file_path.exists():
            logger.error(f"❌ Arquivo não encontrado: {file_path}")
            return []
        
        # Extrair texto baseado na extensão
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            text = self._extract_pdf(file_path)
        elif suffix in ['.txt', '.md']:
            text = self._extract_text(file_path)
        else:
            logger.warning(f"⚠️ Formato não suportado: {suffix}")
            return []
        
        if not text:
            logger.warning(f"⚠️ Nenhum texto extraído de {file_path}")
            return []
        
        # Dividir em chunks
        chunks = self._create_chunks(text)
        
        # Adicionar metadata
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                'text': chunk,
                'metadata': {
                    'source': str(file_path),
                    'chunk_id': i,
                    'total_chunks': len(chunks),
                    'file_type': suffix[1:]  # Remove o ponto
                }
            })
        
        logger.info(f"📄 Processado {file_path.name}: {len(chunks)} chunks")
        return documents
    
    def _extract_pdf(self, file_path: Path) -> str:
        """Extrai texto de PDF."""
        if not PDF_AVAILABLE:
            logger.error("❌ PyPDF2 não instalado! Use: pip install PyPDF2")
            return ""
        
        try:
            text = []
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text.append(page.extract_text())
            
            return "\n".join(text)
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair PDF: {e}")
            return ""
    
    def _extract_text(self, file_path: Path) -> str:
        """Extrai texto de arquivo texto."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Tentar com latin-1
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"❌ Erro ao ler arquivo: {e}")
                return ""
        except Exception as e:
            logger.error(f"❌ Erro ao ler arquivo: {e}")
            return ""
    
    def _create_chunks(self, text: str) -> List[str]:
        """
        Divide texto em chunks com sobreposição.
        
        Args:
            text: Texto completo
            
        Returns:
            Lista de chunks
        """
        # Limpar texto
        text = text.strip()
        
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Tentar quebrar em uma sentença
            if end < len(text):
                # Procurar por fim de sentença próximo
                for sep in ['. ', '.\n', '! ', '?\n', '? ']:
                    pos = text.rfind(sep, start, end)
                    if pos != -1:
                        end = pos + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Mover start com sobreposição
            start = end - self.chunk_overlap
            
            # Evitar loop infinito
            if start >= len(text):
                break
        
        return chunks
    
    def process_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """
        Processa todos os documentos em um diretório.
        
        Args:
            directory: Diretório a processar
            
        Returns:
            Lista de documentos processados
        """
        if not directory.exists() or not directory.is_dir():
            logger.error(f"❌ Diretório inválido: {directory}")
            return []
        
        all_documents = []
        
        # Processar arquivos suportados
        for pattern in ['*.pdf', '*.txt', '*.md']:
            for file_path in directory.glob(pattern):
                documents = self.process_file(file_path)
                all_documents.extend(documents)
        
        logger.info(f"📚 Processados {len(all_documents)} chunks de {directory}")
        return all_documents


# Instância global
_document_processor: DocumentProcessor = None


def get_document_processor() -> DocumentProcessor:
    """Obtém instância global do document processor."""
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor

