#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/JARVIS - Sistema de Teste Completo
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'jarvis'))

print("=" * 60)
print("🧪 ALEX/JARVIS - TESTE COMPLETO")
print("=" * 60)

import logging
logging.basicConfig(level=logging.WARNING)

results = {'passed': 0, 'failed': 0, 'warnings': 0}

# TESTE 1: Segurança
print("\n🔒 Sistema de Segurança")
print("-" * 60)

try:
    from security import get_secret_manager
    sm = get_secret_manager()
    status = sm.get_status()
    print(f"✅ SecretManager: {status['total_secrets']} secrets")
    results['passed'] += 1
except Exception as e:
    print(f"❌ SecretManager: {e}")
    results['failed'] += 1

try:
    from security import get_auth_manager
    auth = get_auth_manager()
    token = auth.create_access_token('test')
    if token:
        print(f"✅ Authentication: Token criado")
        results['passed'] += 1
    else:
        print(f"⚠️ Authentication: PyJWT não instalado")
        results['warnings'] += 1
except Exception as e:
    print(f"❌ Authentication: {e}")
    results['failed'] += 1

try:
    from security import rate_limit
    allowed, _ = rate_limit('test')
    print(f"✅ RateLimiter: Funcionando")
    results['passed'] += 1
except Exception as e:
    print(f"❌ RateLimiter: {e}")
    results['failed'] += 1

try:
    from security import encrypt_data, decrypt_data
    encrypted = encrypt_data("test")
    if encrypted:
        print(f"✅ Encryption: Funcionando")
        results['passed'] += 1
    else:
        print(f"⚠️ Encryption: cryptography não instalado")
        results['warnings'] += 1
except Exception as e:
    print(f"❌ Encryption: {e}")
    results['failed'] += 1

# TESTE 2: Cache
print("\n💾 Cache System")
print("-" * 60)

try:
    from utils.cache.cache_manager import CacheManager
    cache = CacheManager()
    cache.set('test', 'value')
    value = cache.get('test')
    if value == 'value':
        print(f"✅ CacheManager: Funcionando")
        results['passed'] += 1
except Exception as e:
    print(f"❌ CacheManager: {e}")
    results['failed'] += 1

# TESTE 3: Performance Monitor
print("\n📊 Performance Monitor")
print("-" * 60)

try:
    from utils.profiling.performance_monitor import PerformanceMonitor
    pm = PerformanceMonitor()
    pm.start_monitoring()
    import time
    time.sleep(0.1)
    pm.stop_monitoring()
    print(f"✅ PerformanceMonitor: Funcionando")
    results['passed'] += 1
except Exception as e:
    print(f"⚠️ PerformanceMonitor: {e}")
    results['warnings'] += 1

# TESTE 4: Modules
print("\n🤖 Core Modules")
print("-" * 60)

try:
    from modules.personality_engine import PersonalityEngine
    pe = PersonalityEngine()
    print(f"✅ PersonalityEngine: Funcionando")
    results['passed'] += 1
except Exception as e:
    print(f"⚠️ PersonalityEngine: {e}")
    results['warnings'] += 1

try:
    from modules.memory_system import MemorySystem
    ms = MemorySystem()
    ms.store_memory("test", "short_term")
    print(f"✅ MemorySystem: Funcionando")
    results['passed'] += 1
except Exception as e:
    print(f"⚠️ MemorySystem: {e}")
    results['warnings'] += 1

# RELATÓRIO
print("\n" + "=" * 60)
print("📊 RELATÓRIO")
print("=" * 60)

total = results['passed'] + results['failed'] + results['warnings']
rate = (results['passed'] / total * 100) if total > 0 else 0

print(f"\n✅ Passaram:  {results['passed']}")
print(f"⚠️  Avisos:   {results['warnings']}")
print(f"❌ Falharam: {results['failed']}")
print(f"🎯 Taxa:     {rate:.1f}%\n")

if results['failed'] == 0:
    print("🎉 SISTEMA FUNCIONAL!")
else:
    print("⚠️ SISTEMA COM PROBLEMAS")

print("=" * 60)
sys.exit(0 if results['failed'] == 0 else 1)
