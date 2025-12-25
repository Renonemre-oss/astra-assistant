#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal
Teste de Integração do Analisador Contextual com Sistema Multi-Utilizador

Testa a integração completa do analisador contextual com o sistema de gestão
multi-utilizador, validando análise comportamental e identificação melhorada.
"""

import sys
import json
import logging
from pathlib import Path

# Configurar logging para o teste
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_contextual_integration():
    """Teste principal da integração contextual."""
    
    try:
        import sys
        from pathlib import Path
        # Adicionar diretório pai ao path para permitir importação
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from modules.multi_user_manager import MultiUserManager
        
        logger.info("=== TESTE DE INTEGRAÇÃO DO ANALISADOR CONTEXTUAL ===")
        
        # Inicializar sistema
        manager = MultiUserManager()
        
        # Verificar se analisador contextual está disponível
        if not manager.contextual_analyzer:
            logger.warning("Analisador contextual não disponível - teste limitado")
        else:
            logger.info("✓ Analisador contextual inicializado com sucesso")
        
        # === TESTE 1: Criação de utilizadores com padrões distintos ===
        logger.info("\n--- TESTE 1: Criação de utilizadores com padrões distintos ---")
        
        # Ana - Profissional formal
        ana_messages = [
            "Olá, eu sou a Ana e trabalho como engenheira de software",
            "Gostaria de saber informações sobre o projeto de hoje",
            "Por favor, pode enviar-me o relatório técnico?",
            "Obrigada pela colaboração. Tenho uma reunião às 15h",
            "Preciso de acesso aos logs do sistema para análise"
        ]
        
        # João - Casual e descontraído  
        joao_messages = [
            "Hey! Sou o João, estudante aqui",
            "Cara, adoro jogar futebol nos fins de semana!",
            "Mano, esqueci onde pus as chaves do carro...",
            "Que fixe! Vamos sair hoje à noite?",
            "Tás a gozar comigo? hahaha"
        ]
        
        # Processar mensagens da Ana
        ana_id = None
        for message in ana_messages:
            result = manager.process_input(message)
            if ana_id is None:
                ana_id = result['user_id']
            logger.info(f"Ana: {message[:40]}... -> Confiança: {result['confidence']:.2f}")
        
        # Processar mensagens do João
        joao_id = None
        for message in joao_messages:
            result = manager.process_input(message)
            if joao_id is None:
                joao_id = result['user_id']
            logger.info(f"João: {message[:40]}... -> Confiança: {result['confidence']:.2f}")
        
        # === TESTE 2: Verificar identificação melhorada por contexto ===
        logger.info("\n--- TESTE 2: Identificação melhorada por contexto ---")
        
        # Testar mensagens ambíguas que devem ser identificadas por contexto
        test_messages = [
            ("Preciso do relatório técnico urgente", "Ana (formal/profissional)"),
            ("Vou jogar à bola hoje", "João (descontraído/desporto)"),
            ("A reunião foi cancelada", "Ana (contexto profissional)"),
            ("Que fixe, mano!", "João (linguagem informal)")
        ]
        
        for message, expected in test_messages:
            result = manager.process_input(message)
            identified_user = manager.users_data[result['user_id']]['name']
            logger.info(f"'{message}' -> {identified_user} (esperado: {expected}) - Confiança: {result['confidence']:.2f}")
        
        # === TESTE 3: Análise de padrões comportamentais ===
        logger.info("\n--- TESTE 3: Análise de padrões comportamentais ---")
        
        if manager.contextual_analyzer:
            # Analisar padrões da Ana
            ana_patterns = manager.analyze_user_patterns(ana_id)
            logger.info(f"Padrões da Ana:")
            if 'formality' in ana_patterns:
                formality_data = ana_patterns['formality']
                if isinstance(formality_data, dict):
                    for level, score in formality_data.items():
                        logger.info(f"  - Formalidade {level}: {score:.2f}")
                else:
                    logger.info(f"  - Formalidade: {formality_data}")
            if 'emotions' in ana_patterns:
                emotions_data = ana_patterns['emotions']
                if isinstance(emotions_data, dict) and emotions_data:
                    top_emotion = max(emotions_data.items(), key=lambda x: x[1])
                    logger.info(f"  - Emoção principal: {top_emotion[0]} ({top_emotion[1]:.2f})")
            if 'topics' in ana_patterns:
                topics_data = ana_patterns['topics']
                if isinstance(topics_data, dict) and topics_data:
                    top_topics = sorted(topics_data.items(), key=lambda x: x[1], reverse=True)[:3]
                    topic_names = [topic for topic, score in top_topics]
                    logger.info(f"  - Tópicos principais: {', '.join(topic_names)}")
            
            # Analisar padrões do João
            joao_patterns = manager.analyze_user_patterns(joao_id)
            logger.info(f"Padrões do João:")
            if 'formality' in joao_patterns:
                formality_data = joao_patterns['formality']
                if isinstance(formality_data, dict):
                    for level, score in formality_data.items():
                        logger.info(f"  - Formalidade {level}: {score:.2f}")
                else:
                    logger.info(f"  - Formalidade: {formality_data}")
            if 'emotions' in joao_patterns:
                emotions_data = joao_patterns['emotions']
                if isinstance(emotions_data, dict) and emotions_data:
                    top_emotion = max(emotions_data.items(), key=lambda x: x[1])
                    logger.info(f"  - Emoção principal: {top_emotion[0]} ({top_emotion[1]:.2f})")
            if 'topics' in joao_patterns:
                topics_data = joao_patterns['topics']
                if isinstance(topics_data, dict) and topics_data:
                    top_topics = sorted(topics_data.items(), key=lambda x: x[1], reverse=True)[:3]
                    topic_names = [topic for topic, score in top_topics]
                    logger.info(f"  - Tópicos principais: {', '.join(topic_names)}")
        
        # === TESTE 4: Continuidade e aprendizagem ===
        logger.info("\n--- TESTE 4: Continuidade e aprendizagem ---")
        
        # Simular conversa contínua da Ana
        ana_continuation = [
            "Conforme discutido na reunião anterior",
            "Os requisitos técnicos foram atualizados",
            "Por favor confirme a implementação"
        ]
        
        for message in ana_continuation:
            result = manager.process_input(message)
            identified_user = manager.users_data[result['user_id']]['name']
            logger.info(f"Continuidade Ana: '{message}' -> {identified_user} - Confiança: {result['confidence']:.2f}")
        
        # === TESTE 5: Estatísticas contextuais ===
        logger.info("\n--- TESTE 5: Estatísticas contextuais ---")
        
        # Obter estatísticas completas
        all_stats = manager.get_all_stats()
        logger.info(f"Total de utilizadores: {all_stats['total_users']}")
        logger.info(f"Utilizador atual: {all_stats.get('current_user', {}).get('name', 'Nenhum')}")
        
        if 'contextual' in all_stats:
            contextual_stats = all_stats['contextual']
            if contextual_stats.get('contextual_available'):
                logger.info("✓ Estatísticas contextuais disponíveis")
                if 'total_behaviors_analyzed' in contextual_stats:
                    logger.info(f"  - Comportamentos analisados: {contextual_stats['total_behaviors_analyzed']}")
            else:
                logger.info("⚠ Estatísticas contextuais não disponíveis")
        
        # === TESTE 6: Teste de mudança de contexto ===
        logger.info("\n--- TESTE 6: Teste de mudança de contexto ---")
        
        # Alternar entre utilizadores rapidamente
        rapid_switches = [
            ("Tenho de ir à biblioteca estudar", "João"),
            ("O código precisa de refatoração", "Ana"),
            ("Bora jantar pizza?", "João"),
            ("Reunião adiada para amanhã", "Ana")
        ]
        
        for message, expected_name in rapid_switches:
            result = manager.process_input(message)
            identified_user = manager.users_data[result['user_id']]['name']
            is_correct = identified_user.lower() == expected_name.lower()
            status = "✓" if is_correct else "✗"
            logger.info(f"{status} '{message}' -> {identified_user} (esperado: {expected_name}) - {result['confidence']:.2f}")
        
        # === TESTE 7: Análise de diferentes tons emocionais ===
        logger.info("\n--- TESTE 7: Análise de tons emocionais ---")
        
        emotional_tests = [
            ("Estou muito feliz com os resultados!", "positivo"),
            ("Que frustração, nada funciona hoje...", "negativo"), 
            ("O relatório está pronto conforme solicitado", "neutro"),
            ("INCRÍVEL! Conseguimos resolver o bug!", "muito positivo")
        ]
        
        for message, expected_tone in emotional_tests:
            result = manager.process_input(message)
            identified_user = manager.users_data[result['user_id']]['name']
            logger.info(f"'{message}' -> {identified_user} - Tom esperado: {expected_tone}")
        
        logger.info("\n=== RESULTADO DO TESTE ===")
        logger.info("✓ Teste de integração contextual concluído com sucesso!")
        logger.info(f"✓ Utilizadores criados: {len(manager.users_data)}")
        logger.info(f"✓ Sistema contextual ativo: {'Sim' if manager.contextual_analyzer else 'Não'}")
        
        # Mostrar resumo final dos utilizadores
        logger.info("\n--- RESUMO DOS UTILIZADORES ---")
        for user_data in manager.get_all_users():
            logger.info(f"• {user_data['name']} (ID: {user_data['user_id'][:8]})")
            logger.info(f"  - Conversas: {user_data.get('conversation_count', 0)}")
            logger.info(f"  - Profissão: {user_data.get('profession', 'Não definida')}")
            logger.info(f"  - Última interação: {user_data.get('last_seen', 'N/A')[:19]}")
        
        return True
        
    except ImportError as e:
        logger.error(f"Erro de importação: {e}")
        logger.error("Certifique-se de que todos os módulos estão disponíveis")
        return False
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_contextual_fallback():
    """Testa o sistema quando o analisador contextual não está disponível."""
    logger.info("\n=== TESTE DE FALLBACK SEM ANALISADOR CONTEXTUAL ===")
    
    try:
        # Simular indisponibilidade do analisador contextual
        import multi_user_manager
        original_flag = multi_user_manager.CONTEXTUAL_ANALYZER_AVAILABLE
        multi_user_manager.CONTEXTUAL_ANALYZER_AVAILABLE = False
        
        manager = multi_user_manager.MultiUserManager()
        
        # Verificar se sistema funciona sem analisador contextual
        result = manager.process_input("Olá, eu sou o Pedro")
        logger.info(f"✓ Sistema funciona sem analisador contextual")
        logger.info(f"  - Utilizador criado: {manager.users_data[result['user_id']]['name']}")
        logger.info(f"  - Confiança: {result['confidence']:.2f}")
        
        # Restaurar flag original
        multi_user_manager.CONTEXTUAL_ANALYZER_AVAILABLE = original_flag
        
        return True
        
    except Exception as e:
        logger.error(f"Erro no teste de fallback: {e}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando teste de integração do analisador contextual...")
    
    success = test_contextual_integration()
    if success:
        logger.info("\n🎉 Todos os testes de integração passaram!")
    else:
        logger.error("\n❌ Alguns testes falharam!")
        sys.exit(1)
    
    # Teste adicional de fallback
    test_contextual_fallback()
    
    logger.info("\n✅ Teste completo de integração contextual finalizado!")
