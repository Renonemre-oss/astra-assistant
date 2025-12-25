#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Assistente Pessoal
Demonstração do Sistema Multi-Utilizador com Análise Contextual

Demonstra o sistema integrado de gestão multi-utilizador com análise contextual avançada,
mostrando como o sistema identifica e personaliza respostas para diferentes utilizadores.
"""

import sys
import json
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def demonstrate_contextual_system():
    """Demonstração completa do sistema contextual."""
    
    try:
        import sys
        from pathlib import Path
        # Adicionar diretório pai ao path para permitir importação
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from modules.multi_user_manager import MultiUserManager
        
        logger.info("=== DEMONSTRAÇÃO DO SISTEMA MULTI-UTILIZADOR CONTEXTUAL ===")
        
        # Inicializar sistema
        manager = MultiUserManager()
        
        # Verificar recursos disponíveis
        logger.info(f"✓ Sistema de voz: {'Disponível' if manager.voice_id else 'Indisponível'}")
        logger.info(f"✓ Análise contextual: {'Disponível' if manager.contextual_analyzer else 'Indisponível'}")
        
        print("\n" + "="*60)
        print("           SISTEMA ALEX MULTI-UTILIZADOR")
        print("       Com Análise Contextual Inteligente")
        print("="*60)
        
        # === CENÁRIO 1: Identificação automática ===
        print("\n🎯 CENÁRIO 1: Identificação Automática de Utilizadores")
        print("-" * 50)
        
        # Simular diferentes utilizadores
        conversations = [
            {
                'user': 'Professor João',
                'messages': [
                    "Bom dia! Sou o Professor João da Universidade do Porto",
                    "Preciso de preparar as aulas para amanhã",
                    "Os alunos têm exame na próxima semana",
                    "Vou corrigir os trabalhos de programação"
                ]
            },
            {
                'user': 'Maria (Médica)',
                'messages': [
                    "Olá, eu sou a Maria e trabalho como médica no hospital",
                    "Tenho consultas marcadas para esta tarde",
                    "O paciente do quarto 204 precisa de acompanhamento",
                    "Vou verificar os exames laboratoriais"
                ]
            },
            {
                'user': 'Tiago (Jovem)',
                'messages': [
                    "Hey! Sou o Tiago, tou aqui na faculdade",
                    "Cara, tenho teste amanhã e não estudei nada!",
                    "Bora jogar futebol depois das aulas?",
                    "Que seca, esqueci-me do livro em casa..."
                ]
            }
        ]
        
        user_ids = {}
        
        # Processar conversas
        for conversation in conversations:
            print(f"\n👤 {conversation['user']}:")
            for message in conversation['messages']:
                result = manager.process_input(message)
                
                user_name = manager.users_data[result['user_id']]['name']
                confidence = result['confidence']
                
                # Armazenar ID do utilizador
                if conversation['user'] not in user_ids:
                    user_ids[conversation['user']] = result['user_id']
                
                print(f"  💬 \"{message[:50]}{'...' if len(message) > 50 else ''}\"")
                print(f"     → Identificado: {user_name} (Confiança: {confidence:.2f})")
        
        # === CENÁRIO 2: Análise de padrões comportamentais ===
        print(f"\n🧠 CENÁRIO 2: Análise de Padrões Comportamentais")
        print("-" * 50)
        
        if manager.contextual_analyzer:
            for conv_name, user_id in user_ids.items():
                if user_id in manager.users_data:
                    patterns = manager.analyze_user_patterns(user_id)
                    user_data = manager.users_data[user_id]
                    
                    print(f"\n📊 Análise para {user_data['name']}:")
                    
                    # Tópicos principais
                    if 'topics' in patterns and patterns['topics']:
                        top_topics = sorted(patterns['topics'].items(), key=lambda x: x[1], reverse=True)[:3]
                        print(f"  🏷️  Tópicos: {', '.join([topic for topic, _ in top_topics])}")
                    
                    # Nível de formalidade
                    if 'formality' in patterns and patterns['formality']:
                        formality_levels = patterns['formality']
                        if formality_levels:
                            max_formality = max(formality_levels.items(), key=lambda x: x[1])
                            print(f"  🎩 Formalidade: {max_formality[0]} ({max_formality[1]:.2f})")
                    
                    # Emoções detectadas
                    if 'emotions' in patterns and patterns['emotions']:
                        emotions = patterns['emotions']
                        if emotions:
                            max_emotion = max(emotions.items(), key=lambda x: x[1])
                            print(f"  😊 Emoção principal: {max_emotion[0]} ({max_emotion[1]:.2f})")
                    
                    # Informações profissionais
                    if user_data.get('profession'):
                        print(f"  💼 Profissão: {user_data['profession']}")
        
        # === CENÁRIO 3: Identificação por contexto ===
        print(f"\n🔍 CENÁRIO 3: Identificação por Contexto")
        print("-" * 50)
        
        # Mensagens ambíguas que devem ser identificadas por contexto
        ambiguous_messages = [
            ("Tenho de dar aulas amanhã de manhã", "Professor João"),
            ("O paciente está melhor hoje", "Maria (Médica)"),
            ("Mano, que seca de teste!", "Tiago (Jovem)"),
            ("Preciso de preparar material didático", "Professor João"),
            ("Vou verificar a medicação", "Maria (Médica)"),
            ("Bora ao McDonald's?", "Tiago (Jovem)")
        ]
        
        correct_identifications = 0
        total_tests = len(ambiguous_messages)
        
        for message, expected_user in ambiguous_messages:
            result = manager.process_input(message)
            identified_name = manager.users_data[result['user_id']]['name']
            confidence = result['confidence']
            
            # Verificar se identificou corretamente
            is_correct = expected_user.lower() in identified_name.lower() or identified_name.lower() in expected_user.lower()
            status = "✅" if is_correct else "❌"
            
            if is_correct:
                correct_identifications += 1
            
            print(f"{status} \"{message}\"")
            print(f"   → Esperado: {expected_user} | Identificado: {identified_name} ({confidence:.2f})")
        
        accuracy = (correct_identifications / total_tests) * 100
        print(f"\n📈 Precisão da identificação contextual: {accuracy:.1f}% ({correct_identifications}/{total_tests})")
        
        # === CENÁRIO 4: Estatísticas do sistema ===
        print(f"\n📊 CENÁRIO 4: Estatísticas do Sistema")
        print("-" * 50)
        
        all_stats = manager.get_all_stats()
        
        print(f"👥 Total de utilizadores: {all_stats['total_users']}")
        print(f"🎯 Utilizador atual: {all_stats.get('current_user', {}).get('name', 'Nenhum')}")
        
        # Estatísticas contextuais
        if 'contextual' in all_stats and all_stats['contextual']['contextual_available']:
            contextual_stats = all_stats['contextual']
            print(f"🧠 Comportamentos analisados: {contextual_stats.get('total_behaviors_analyzed', 0)}")
            
            # Métodos de análise disponíveis
            methods = contextual_stats.get('analysis_methods', {})
            active_methods = [method for method, active in methods.items() if active]
            print(f"🔧 Métodos de análise ativos: {len(active_methods)}")
        
        # === CENÁRIO 5: Simulação de conversa em tempo real ===
        print(f"\n💬 CENÁRIO 5: Simulação de Conversa Dinâmica")
        print("-" * 50)
        
        # Simular alternância rápida entre utilizadores
        dynamic_conversation = [
            ("João", "Vou enviar as notas dos alunos por email"),
            ("Maria", "O paciente do 204 teve alta médica"),
            ("Tiago", "Fixe! Passei no exame de matemática!"),
            ("João", "A próxima aula será sobre algoritmos"),
            ("Maria", "Preciso atualizar o histórico clínico"),
            ("Tiago", "Vou celebrar com os amigos no bar")
        ]
        
        print("Conversa dinâmica com alternância de utilizadores:")
        for expected_user, message in dynamic_conversation:
            result = manager.process_input(message)
            identified_name = manager.users_data[result['user_id']]['name']
            confidence = result['confidence']
            
            # Simplificar comparação de nomes
            is_correct = expected_user.lower() in identified_name.lower()
            status = "✅" if is_correct else "❌"
            
            print(f"{status} {expected_user}: \"{message}\"")
            print(f"    → {identified_name} ({confidence:.2f})")
        
        # === RESUMO FINAL ===
        print(f"\n🎉 RESUMO FINAL")
        print("="*50)
        
        final_users = manager.get_all_users()
        print(f"✓ Sistema processou {len(final_users)} utilizadores únicos")
        print(f"✓ Análise contextual: {'Ativa' if manager.contextual_analyzer else 'Inativa'}")
        print(f"✓ Reconhecimento por voz: {'Disponível' if manager.voice_id else 'Indisponível'}")
        
        # Mostrar perfis criados
        print(f"\n👥 Perfis de Utilizadores Criados:")
        for user in final_users[:5]:  # Mostrar apenas os primeiros 5
            print(f"  • {user['name']}")
            print(f"    - Conversas: {user.get('conversation_count', 0)}")
            if user.get('profession'):
                print(f"    - Profissão: {user['profession']}")
            print()
        
        print("✅ Demonstração do sistema contextual concluída com sucesso!")
        return True
        
    except ImportError as e:
        logger.error(f"Erro de importação: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()
        return False

def interactive_mode():
    """Modo interativo para testar o sistema."""
    print("\n🔧 MODO INTERATIVO")
    print("-" * 30)
    print("Digite mensagens para testar o sistema (digite 'sair' para terminar)")
    
    try:
        import sys
        from pathlib import Path
        # Adicionar diretório pai ao path para permitir importação
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from modules.multi_user_manager import MultiUserManager
        manager = MultiUserManager()
        
        while True:
            message = input("\n💬 Sua mensagem: ")
            
            if message.lower() in ['sair', 'exit', 'quit']:
                break
            
            if message.strip():
                result = manager.process_input(message)
                user_name = manager.users_data[result['user_id']]['name']
                confidence = result['confidence']
                
                print(f"👤 Identificado como: {user_name}")
                print(f"🎯 Confiança: {confidence:.2f}")
                
                # Mostrar contexto personalizado
                context = result.get('context', '')
                if context:
                    print(f"📋 Contexto:")
                    print(f"    {context.replace(chr(10), chr(10) + '    ')}")
    
    except KeyboardInterrupt:
        print("\n\n👋 Modo interativo encerrado.")
    except Exception as e:
        logger.error(f"Erro no modo interativo: {e}")

if __name__ == "__main__":
    logger.info("Iniciando demonstração do sistema contextual...")
    
    success = demonstrate_contextual_system()
    
    if success:
        logger.info("\n🎉 Demonstração concluída com sucesso!")
        
        # Perguntar se quer modo interativo
        while True:
            try:
                choice = input("\n❓ Deseja testar o modo interativo? (s/n): ").strip().lower()
                if choice in ['s', 'sim', 'y', 'yes']:
                    interactive_mode()
                    break
                elif choice in ['n', 'não', 'nao', 'no']:
                    break
                else:
                    print("Por favor, digite 's' para sim ou 'n' para não.")
            except KeyboardInterrupt:
                break
    else:
        logger.error("\n❌ Demonstração falhou!")
        sys.exit(1)
    
    logger.info("\n✅ Sistema contextual demonstrado com sucesso!")