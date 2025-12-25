#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/Astra - Benchmark System
Sistema de benchmarks para medir performance.
"""

import logging
import time
import statistics
from typing import Dict, Any, List, Callable, Optional
from functools import wraps
from dataclasses import dataclass, field
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Resultado de um benchmark."""
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    operations_per_second: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'name': self.name,
            'iterations': self.iterations,
            'total_time': round(self.total_time, 4),
            'avg_time_ms': round(self.avg_time * 1000, 2),
            'min_time_ms': round(self.min_time * 1000, 2),
            'max_time_ms': round(self.max_time * 1000, 2),
            'std_dev_ms': round(self.std_dev * 1000, 2),
            'ops_per_second': round(self.operations_per_second, 2),
            'metadata': self.metadata
        }


class BenchmarkSystem:
    """Sistema de benchmarking e profiling."""
    
    def __init__(self):
        """Inicializa sistema de benchmark."""
        self.results: List[BenchmarkResult] = []
        self.current_benchmarks: Dict[str, List[float]] = {}
    
    def benchmark(
        self,
        func: Callable,
        iterations: int = 100,
        name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> BenchmarkResult:
        """
        Executa benchmark de uma função.
        
        Args:
            func: Função para testar
            iterations: Número de iterações
            name: Nome do benchmark
            metadata: Metadados adicionais
            
        Returns:
            Resultado do benchmark
        """
        if name is None:
            name = func.__name__
        
        logger.info(f"🔬 Benchmarking {name} ({iterations} iterações)...")
        
        times = []
        
        # Executar iterações
        for i in range(iterations):
            start = time.perf_counter()
            try:
                func()
            except Exception as e:
                logger.error(f"❌ Erro na iteração {i}: {e}")
                continue
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        
        # Calcular estatísticas
        if not times:
            logger.error(f"❌ Nenhuma medida bem-sucedida para {name}")
            return None
        
        total_time = sum(times)
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        ops_per_sec = 1.0 / avg_time if avg_time > 0 else 0.0
        
        result = BenchmarkResult(
            name=name,
            iterations=len(times),
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_dev=std_dev,
            operations_per_second=ops_per_sec,
            metadata=metadata or {}
        )
        
        self.results.append(result)
        
        logger.info(f"✅ {name}: {avg_time*1000:.2f}ms avg, {ops_per_sec:.2f} ops/s")
        
        return result
    
    def benchmark_multiple(
        self,
        benchmarks: Dict[str, Callable],
        iterations: int = 100
    ) -> List[BenchmarkResult]:
        """
        Executa múltiplos benchmarks.
        
        Args:
            benchmarks: Dicionário {nome: função}
            iterations: Iterações por benchmark
            
        Returns:
            Lista de resultados
        """
        results = []
        
        for name, func in benchmarks.items():
            result = self.benchmark(func, iterations, name)
            if result:
                results.append(result)
        
        return results
    
    def compare_benchmarks(self, names: List[str]) -> Dict[str, Any]:
        """
        Compara benchmarks por nome.
        
        Args:
            names: Lista de nomes de benchmarks
            
        Returns:
            Comparação detalhada
        """
        # Filtrar resultados
        filtered = [r for r in self.results if r.name in names]
        
        if not filtered:
            logger.warning("Nenhum benchmark encontrado")
            return {}
        
        # Ordenar por tempo médio
        sorted_results = sorted(filtered, key=lambda x: x.avg_time)
        
        # Calcular comparações
        fastest = sorted_results[0]
        comparisons = []
        
        for result in sorted_results:
            speedup = result.avg_time / fastest.avg_time
            comparisons.append({
                'name': result.name,
                'avg_time_ms': round(result.avg_time * 1000, 2),
                'vs_fastest': f"{speedup:.2f}x" if result != fastest else "fastest",
                'ops_per_second': round(result.operations_per_second, 2)
            })
        
        return {
            'fastest': fastest.name,
            'comparisons': comparisons
        }
    
    def generate_report(self, output_file: Optional[Path] = None) -> str:
        """
        Gera relatório de benchmarks.
        
        Args:
            output_file: Arquivo de saída (opcional)
            
        Returns:
            Relatório em texto
        """
        if not self.results:
            return "Nenhum benchmark executado."
        
        report_lines = [
            "=" * 70,
            "📊 RELATÓRIO DE BENCHMARKS",
            "=" * 70,
            ""
        ]
        
        for result in self.results:
            report_lines.extend([
                f"🔬 {result.name}",
                f"   Iterações: {result.iterations}",
                f"   Tempo médio: {result.avg_time*1000:.2f}ms",
                f"   Min/Max: {result.min_time*1000:.2f}ms / {result.max_time*1000:.2f}ms",
                f"   Desvio padrão: {result.std_dev*1000:.2f}ms",
                f"   Operações/seg: {result.operations_per_second:.2f}",
                ""
            ])
        
        report_lines.append("=" * 70)
        report = "\n".join(report_lines)
        
        # Salvar em arquivo se especificado
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(report, encoding='utf-8')
            logger.info(f"📄 Relatório salvo em {output_file}")
        
        return report
    
    def export_json(self, output_file: Path) -> None:
        """Exporta resultados para JSON."""
        data = {
            'benchmarks': [r.to_dict() for r in self.results],
            'summary': {
                'total_benchmarks': len(self.results),
                'avg_time_ms': statistics.mean([r.avg_time * 1000 for r in self.results])
            }
        }
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"💾 Resultados exportados para {output_file}")
    
    def clear_results(self) -> None:
        """Limpa resultados de benchmarks."""
        self.results.clear()
        logger.info("🧹 Resultados de benchmark limpos")


def profile_function(name: Optional[str] = None):
    """
    Decorador para profile de função.
    
    Example:
        @profile_function("minha_funcao")
        def minha_funcao():
            pass
    """
    def decorator(func: Callable) -> Callable:
        func_name = name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.perf_counter() - start
                logger.debug(f"⏱️ {func_name}: {elapsed*1000:.2f}ms")
        
        return wrapper
    return decorator


class RAGBenchmarks:
    """Benchmarks específicos para sistema RAG."""
    
    def __init__(self):
        """Inicializa benchmarks RAG."""
        self.benchmark_system = BenchmarkSystem()
    
    def run_embedding_benchmark(self, texts: List[str], iterations: int = 10):
        """Benchmark de geração de embeddings."""
        try:
            from ai.embeddings_manager import get_embeddings_manager
            
            em = get_embeddings_manager()
            
            def test_embedding():
                for text in texts:
                    em.encode_single(text)
            
            return self.benchmark_system.benchmark(
                test_embedding,
                iterations=iterations,
                name="embedding_generation",
                metadata={'num_texts': len(texts)}
            )
        except Exception as e:
            logger.error(f"❌ Erro no benchmark de embedding: {e}")
            return None
    
    def run_search_benchmark(self, queries: List[str], iterations: int = 10):
        """Benchmark de busca no RAG."""
        try:
            from ai.optimized_rag import get_optimized_rag
            
            rag = get_optimized_rag()
            
            def test_search():
                for query in queries:
                    rag.search_cached(query, n_results=5)
            
            return self.benchmark_system.benchmark(
                test_search,
                iterations=iterations,
                name="rag_search",
                metadata={'num_queries': len(queries)}
            )
        except Exception as e:
            logger.error(f"❌ Erro no benchmark de busca: {e}")
            return None
    
    def run_context_generation_benchmark(self, queries: List[str], iterations: int = 10):
        """Benchmark de geração de contexto."""
        try:
            from ai.optimized_rag import get_optimized_rag
            
            rag = get_optimized_rag()
            
            def test_context():
                for query in queries:
                    rag.generate_context_cached(query, n_results=3)
            
            return self.benchmark_system.benchmark(
                test_context,
                iterations=iterations,
                name="context_generation",
                metadata={'num_queries': len(queries)}
            )
        except Exception as e:
            logger.error(f"❌ Erro no benchmark de contexto: {e}")
            return None
    
    def run_full_benchmark_suite(self):
        """Executa suite completa de benchmarks."""
        logger.info("🚀 Executando suite completa de benchmarks RAG...")
        
        # Dados de teste
        test_texts = [
            "Python é uma linguagem de programação",
            "FastAPI é um framework moderno",
            "ChromaDB é um banco de dados vetorial"
        ]
        
        test_queries = [
            "O que é Python?",
            "Como criar APIs?",
            "Banco de dados vetorial"
        ]
        
        # Executar benchmarks
        self.run_embedding_benchmark(test_texts, iterations=10)
        self.run_search_benchmark(test_queries, iterations=10)
        self.run_context_generation_benchmark(test_queries, iterations=10)
        
        # Gerar relatório
        report = self.benchmark_system.generate_report()
        print(report)
        
        return self.benchmark_system.results


# Instância global
_benchmark_system: Optional[BenchmarkSystem] = None


def get_benchmark_system() -> BenchmarkSystem:
    """Obtém instância global do sistema de benchmark."""
    global _benchmark_system
    if _benchmark_system is None:
        _benchmark_system = BenchmarkSystem()
    return _benchmark_system

