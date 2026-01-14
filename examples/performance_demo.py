#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/JARVIS - Performance & Cache Demo
Demonstração do sistema de cache e benchmarks.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent / 'jarvis'
sys.path.insert(0, str(root_dir))


def demo_smart_cache():
    """Demo do sistema de cache inteligente."""
    print("=" * 70)
    print("💾 SMART CACHE SYSTEM DEMO")
    print("=" * 70)
    
    from utils.cache.smart_cache import get_smart_cache, cached
    
    cache = get_smart_cache()
    
    # Teste básico
    print("\n1️⃣ Cache básico:")
    cache.set("user:name", "João", ttl=300)
    print(f"   Set: user:name = João")
    
    value = cache.get("user:name")
    print(f"   Get: user:name = {value}")
    
    # Decorador @cached
    print("\n2️⃣ Decorador @cached:")
    
    @cached(ttl=60, key_prefix="calc")
    def expensive_calculation(n):
        import time
        time.sleep(0.1)  # Simular operação cara
        return n ** 2
    
    import time
    start = time.time()
    result1 = expensive_calculation(10)
    time1 = time.time() - start
    print(f"   1ª chamada: {result1} ({time1*1000:.0f}ms)")
    
    start = time.time()
    result2 = expensive_calculation(10)
    time2 = time.time() - start
    print(f"   2ª chamada: {result2} ({time2*1000:.0f}ms) - CACHED!")
    
    # Stats
    print("\n3️⃣ Estatísticas:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Demo de cache completo!")


def demo_optimized_rag():
    """Demo do RAG otimizado."""
    print("\n" + "=" * 70)
    print("🚀 OPTIMIZED RAG DEMO")
    print("=" * 70)
    
    try:
        from ai.optimized_rag import get_optimized_rag
        
        rag = get_optimized_rag()
        
        # Add some test data
        print("\n1️⃣ Adicionando dados de teste...")
        texts = [
            "Python é versátil e fácil de aprender",
            "FastAPI é rápido e moderno",
            "RAG melhora respostas de IA"
        ]
        
        rag.batch_add_texts(texts)
        
        # Search com cache
        print("\n2️⃣ Busca com cache:")
        import time
        
        query = "Python programação"
        
        start = time.time()
        results1 = rag.search_cached(query)
        time1 = time.time() - start
        print(f"   1ª busca: {len(results1)} resultados ({time1*1000:.0f}ms)")
        
        start = time.time()
        results2 = rag.search_cached(query)
        time2 = time.time() - start
        print(f"   2ª busca: {len(results2)} resultados ({time2*1000:.0f}ms) - CACHED!")
        
        # Stats
        print("\n3️⃣ Performance Stats:")
        stats = rag.get_performance_stats()
        print(f"   RAG carregado: {stats['rag_loaded']}")
        print(f"   Cache ativo: {stats['cache_enabled']}")
        
        print("\n✅ RAG otimizado funcionando!")
        
    except Exception as e:
        print(f"⚠️ RAG não disponível: {e}")


def demo_benchmarks():
    """Demo do sistema de benchmarks."""
    print("\n" + "=" * 70)
    print("🔬 BENCHMARK SYSTEM DEMO")
    print("=" * 70)
    
    from utils.profiling.benchmark_system import get_benchmark_system
    
    benchmark = get_benchmark_system()
    
    # Benchmarks simples
    print("\n1️⃣ Benchmarks básicos:")
    
    def test_list_comprehension():
        return [x**2 for x in range(1000)]
    
    def test_map():
        return list(map(lambda x: x**2, range(1000)))
    
    benchmarks = {
        "list_comprehension": test_list_comprehension,
        "map_function": test_map
    }
    
    results = benchmark.benchmark_multiple(benchmarks, iterations=100)
    
    # Comparação
    print("\n2️⃣ Comparação:")
    comparison = benchmark.compare_benchmarks(["list_comprehension", "map_function"])
    
    if comparison:
        print(f"   Mais rápido: {comparison['fastest']}")
        for comp in comparison['comparisons']:
            print(f"   - {comp['name']}: {comp['avg_time_ms']:.2f}ms ({comp['vs_fastest']})")
    
    # Relatório
    print("\n3️⃣ Relatório:")
    report = benchmark.generate_report()
    print(report)
    
    print("✅ Benchmarks completos!")


if __name__ == "__main__":
    # Executar demos
    demo_smart_cache()
    demo_optimized_rag()
    demo_benchmarks()
    
    print("\n" + "=" * 70)
    print("🎉 TODOS OS DEMOS COMPLETOS!")
    print("=" * 70)
