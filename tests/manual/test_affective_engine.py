"""
Script de Teste - Affective State Engine

Demonstra o sistema de estados afetivos em ação.
"""

from astra.modules.affective_state_engine import (
    AffectiveStateEngine,
    EventType
)
import time


def print_separator(title: str = ""):
    """Print separador visual"""
    print("\n" + "="*60)
    if title:
        print(f"  {title}")
        print("="*60)
    print()


def test_scenario_1_positive_relationship():
    """Cenário 1: Construção de relacionamento positivo"""
    print_separator("CENÁRIO 1: Construção de Relacionamento Positivo")
    
    engine = AffectiveStateEngine(user_id="test_user_1")
    engine.reset_to_defaults()
    
    print("Estado Inicial:")
    print(engine.get_state_summary())
    
    # Várias interações positivas
    print("\n[Usuário pede ajuda genuína]")
    engine.trigger_event(EventType.GENUINE_HELP, context="Pediu ajuda com código")
    
    print("\n[Usuário mostra respeito consistente]")
    engine.trigger_event(EventType.CONSISTENT_RESPECT, context="Agradeceu pela ajuda")
    
    print("\n[Mais uma interação positiva]")
    engine.trigger_event(EventType.POSITIVE_INTERACTION, context="Conversa agradável")
    
    print("\nEstado Após Interações Positivas:")
    print(engine.get_state_summary())
    
    tone = engine.get_response_tone()
    print("\nTom de Resposta Gerado:")
    print(tone.to_prompt())


def test_scenario_2_irritation_buildup():
    """Cenário 2: Acumulação de irritação"""
    print_separator("CENÁRIO 2: Acumulação de Irritação")
    
    engine = AffectiveStateEngine(user_id="test_user_2")
    engine.reset_to_defaults()
    
    print("Estado Inicial:")
    print(engine.get_state_summary())
    
    # Primeira interrupção
    print("\n[1ª interrupção]")
    engine.trigger_event(EventType.INTERRUPTION, 
                        context="Interrompeu no meio da resposta",
                        accumulation_factor=1.0)
    
    # Segunda interrupção (mais impacto)
    print("\n[2ª interrupção - 5 minutos depois]")
    engine.trigger_event(EventType.INTERRUPTION,
                        context="Interrompeu novamente",
                        accumulation_factor=2.0)
    
    # Terceira interrupção (muito impacto)
    print("\n[3ª interrupção!]")
    engine.trigger_event(EventType.INTERRUPTION,
                        context="Mais uma interrupção",
                        accumulation_factor=3.0)
    
    print("\nEstado Após 3 Interrupções:")
    print(engine.get_state_summary())
    
    tone = engine.get_response_tone()
    print("\nTom de Resposta Gerado:")
    print(tone.to_prompt())


def test_scenario_3_verbal_aggression_recovery():
    """Cenário 3: Agressão verbal e recuperação com desculpa"""
    print_separator("CENÁRIO 3: Agressão Verbal → Desculpa")
    
    engine = AffectiveStateEngine(user_id="test_user_3")
    engine.reset_to_defaults()
    
    print("Estado Inicial:")
    print(engine.get_state_summary())
    
    # Agressão verbal
    print("\n[Usuário foi agressivo verbalmente]")
    engine.trigger_event(EventType.VERBAL_AGGRESSION,
                        context="Disse palavrões e foi desrespeitoso")
    
    print("\nEstado Após Agressão:")
    print(engine.get_state_summary())
    
    tone = engine.get_response_tone()
    print("\nTom de Resposta (pós-agressão):")
    print(tone.to_prompt())
    
    # Usuário se desculpa
    print("\n[Usuário se desculpou]")
    engine.trigger_event(EventType.USER_APOLOGY,
                        context="Reconheceu o erro e pediu desculpas")
    
    print("\nEstado Após Desculpa:")
    print(engine.get_state_summary())
    
    tone = engine.get_response_tone()
    print("\nTom de Resposta (pós-desculpa):")
    print(tone.to_prompt())


def test_scenario_4_ignored_requests():
    """Cenário 4: Pedidos ignorados repetidamente"""
    print_separator("CENÁRIO 4: Pedidos Ignorados Repetidamente")
    
    engine = AffectiveStateEngine(user_id="test_user_4")
    engine.reset_to_defaults()
    
    print("Estado Inicial:")
    print(engine.get_state_summary())
    
    # ASTRA pede algo, usuário ignora
    print("\n[1ª vez ignorado]")
    engine.trigger_event(EventType.IGNORED_REQUEST,
                        context="ASTRA pediu confirmação, usuário ignorou",
                        accumulation_factor=1.0)
    
    print("\n[2ª vez ignorado]")
    engine.trigger_event(EventType.IGNORED_REQUEST,
                        context="Novamente ignorado",
                        accumulation_factor=2.0)
    
    print("\n[3ª vez ignorado - limite atingido]")
    engine.trigger_event(EventType.IGNORED_REQUEST,
                        context="Completamente ignorado de novo",
                        accumulation_factor=3.0)
    
    print("\nEstado Após Ser Ignorado 3x:")
    print(engine.get_state_summary())
    
    tone = engine.get_response_tone()
    print("\nTom de Resposta Gerado:")
    print(tone.to_prompt())


def test_scenario_5_decay_over_time():
    """Cenário 5: Decay ao longo do tempo"""
    print_separator("CENÁRIO 5: Decay Natural ao Longo do Tempo")
    
    engine = AffectiveStateEngine(user_id="test_user_5")
    engine.reset_to_defaults()
    
    # Causar irritação
    print("[Causando irritação alta...]")
    engine.trigger_event(EventType.VERBAL_AGGRESSION)
    engine.trigger_event(EventType.INTERRUPTION, accumulation_factor=2.0)
    
    print("\nEstado Imediatamente Após Eventos:")
    print(engine.get_state_summary())
    
    # Simular passagem de 1 dia
    print("\n[Simulando passagem de 1 dia...]")
    engine.states.last_updated -= 86400  # -1 dia
    engine._apply_decay()
    
    print("\nEstado Após 1 Dia:")
    print(engine.get_state_summary())
    
    # Simular mais 2 dias
    print("\n[Simulando mais 2 dias...]")
    engine.states.last_updated -= 86400 * 2
    engine._apply_decay()
    
    print("\nEstado Após 3 Dias Total:")
    print(engine.get_state_summary())
    
    tone = engine.get_response_tone()
    print("\nTom de Resposta (após 3 dias):")
    print(tone.to_prompt())


def test_scenario_6_limit_reached():
    """Cenário 6: Limite atingido - ASTRA precisa de espaço"""
    print_separator("CENÁRIO 6: LIMITE ATINGIDO")
    
    engine = AffectiveStateEngine(user_id="test_user_6")
    engine.reset_to_defaults()
    
    print("Estado Inicial:")
    print(engine.get_state_summary())
    
    # Empilhar eventos negativos
    print("\n[Sequência de eventos negativos...]")
    engine.trigger_event(EventType.VERBAL_AGGRESSION)
    engine.trigger_event(EventType.INTERRUPTION, accumulation_factor=3.0)
    engine.trigger_event(EventType.IGNORED_REQUEST, accumulation_factor=3.0)
    engine.trigger_event(EventType.VERBAL_AGGRESSION)
    engine.trigger_event(EventType.INTERRUPTION, accumulation_factor=3.0)
    
    print("\nEstado Final - LIMITE ATINGIDO:")
    print(engine.get_state_summary())
    
    tone = engine.get_response_tone()
    print("\nTom de Resposta (limite atingido):")
    print(tone.to_prompt())


def main():
    """Executar todos os cenários de teste"""
    print("\n" + "="*60)
    print("  AFFECTIVE STATE ENGINE - DEMONSTRAÇÃO")
    print("  Arquitetura Emocional Real para ASTRA")
    print("="*60)
    
    scenarios = [
        ("1", "Relacionamento Positivo", test_scenario_1_positive_relationship),
        ("2", "Acumulação de Irritação", test_scenario_2_irritation_buildup),
        ("3", "Agressão + Recuperação", test_scenario_3_verbal_aggression_recovery),
        ("4", "Pedidos Ignorados", test_scenario_4_ignored_requests),
        ("5", "Decay ao Longo do Tempo", test_scenario_5_decay_over_time),
        ("6", "LIMITE ATINGIDO", test_scenario_6_limit_reached),
    ]
    
    print("\nEscolha um cenário para testar:")
    for num, name, _ in scenarios:
        print(f"  [{num}] {name}")
    print("  [0] Executar TODOS os cenários")
    
    choice = input("\nEscolha (0-6): ").strip()
    
    if choice == "0":
        for _, _, test_func in scenarios:
            test_func()
            input("\nPressione ENTER para continuar para o próximo cenário...")
    else:
        for num, _, test_func in scenarios:
            if choice == num:
                test_func()
                break
        else:
            print("Opção inválida!")
    
    print("\n" + "="*60)
    print("  FIM DA DEMONSTRAÇÃO")
    print("="*60)


if __name__ == "__main__":
    main()
