"""
Testes unitários para Expression Modulator

Valida tradução de estados afetivos em expressão verbal.
"""

import pytest
from unittest.mock import Mock, MagicMock
from astra.modules.expression_modulator import (
    ExpressionModulator,
    ExpressionStyle,
    PunctuationEnergy
)


@pytest.fixture
def mock_affective_engine():
    """Criar mock do AffectiveStateEngine"""
    engine = Mock()
    
    # Estados padrão (neutros)
    engine.states = Mock(
        trust=0.5,
        closeness=0.5,
        respect=0.5,
        care=0.5,
        irritation=0.3,
        withdrawal=0.3,
        disappointment=0.3,
        engagement=0.5,
        patience=0.5,
        protective_mode=False
    )
    
    return engine


@pytest.fixture
def modulator(mock_affective_engine):
    """Criar modulator com affective engine"""
    return ExpressionModulator(affective_engine=mock_affective_engine)


class TestExpressionStyle:
    """Testes para ExpressionStyle dataclass"""
    
    def test_default_values(self):
        """Testar valores padrão"""
        style = ExpressionStyle()
        
        assert style.sentence_length_factor == 1.0
        assert style.punctuation_energy == PunctuationEnergy.PERIOD
        assert style.emoji_frequency == 0.0
        assert style.formality == 0.3
        assert style.verbosity == 0.7
        assert style.proactivity == 0.5
        assert style.speaking_rate == 1.0
        assert style.pause_duration_factor == 1.0
        assert style.volume_factor == 1.0
        assert style.pitch_variation == 1.0
        assert style.use_intentional_delay is False
        assert style.delay_seconds == 0.0
        assert style.prefer_silence is False
        assert style.description == ""


class TestExpressionCalculation:
    """Testes para cálculo de expressão"""
    
    def test_irritation_high(self, modulator, mock_affective_engine):
        """Irritação alta → frases curtas, seco, sem emojis"""
        mock_affective_engine.states.irritation = 0.7
        mock_affective_engine.states.withdrawal = 0.5
        
        style = modulator.calculate_expression_style()
        
        assert style.sentence_length_factor == 0.3  # Muito curto
        assert style.punctuation_energy == PunctuationEnergy.PERIOD  # Seco
        assert style.emoji_frequency == 0.0  # Nenhum
        assert style.verbosity == 0.2  # Minimalista
        assert style.proactivity == 0.0  # Zero iniciativa
    
    def test_withdrawal_high(self, modulator, mock_affective_engine):
        """Withdrawal alto → frases curtas, hesitante"""
        mock_affective_engine.states.withdrawal = 0.75
        mock_affective_engine.states.irritation = 0.3
        
        style = modulator.calculate_expression_style()
        
        assert style.sentence_length_factor == 0.3  # Muito curto
        assert style.punctuation_energy == PunctuationEnergy.ELLIPSIS  # Hesitante
        assert style.verbosity == 0.2  # Minimalista
        assert style.proactivity == 0.0  # Zero iniciativa
    
    def test_engagement_high_care_high(self, modulator, mock_affective_engine):
        """Engagement + care alto → frases longas, energético, proativo"""
        mock_affective_engine.states.engagement = 0.8
        mock_affective_engine.states.care = 0.7
        mock_affective_engine.states.closeness = 0.7
        mock_affective_engine.states.irritation = 0.2
        
        style = modulator.calculate_expression_style()
        
        assert style.sentence_length_factor == 1.3  # Longo
        assert style.punctuation_energy == PunctuationEnergy.EXCLAMATION  # Energético
        assert style.emoji_frequency == 0.6  # Frequente
        assert style.verbosity == 0.9  # Elaborado
        assert style.proactivity == 0.8  # Muito proativo
    
    def test_protective_mode(self, modulator, mock_affective_engine):
        """Protective mode → delay intencional"""
        mock_affective_engine.states.protective_mode = True
        mock_affective_engine.states.withdrawal = 0.6
        
        style = modulator.calculate_expression_style()
        
        assert style.use_intentional_delay is True
        assert style.delay_seconds > 3.0
    
    def test_extreme_withdrawal_and_irritation(self, modulator, mock_affective_engine):
        """Withdrawal + irritation extremos → preferência por silêncio"""
        mock_affective_engine.states.withdrawal = 0.9
        mock_affective_engine.states.irritation = 0.75
        
        style = modulator.calculate_expression_style()
        
        assert style.prefer_silence is True


class TestTextModification:
    """Testes para modificação de texto"""
    
    def test_silence_preference(self, modulator):
        """Preferência por silêncio → texto vazio"""
        style = ExpressionStyle(prefer_silence=True)
        text = "Esta é uma resposta normal."
        
        result = modulator.apply_style_to_text(text, style)
        
        assert result == ""
    
    def test_shorten_sentences(self, modulator):
        """Frases curtas → manter apenas primeira"""
        style = ExpressionStyle(sentence_length_factor=0.3)
        text = "Primeira frase. Segunda frase. Terceira frase."
        
        result = modulator.apply_style_to_text(text, style)
        
        assert "Primeira frase" in result
        assert "Segunda frase" not in result
        assert "Terceira frase" not in result
    
    def test_punctuation_period(self, modulator):
        """Substituir pontuação por ponto"""
        style = ExpressionStyle(punctuation_energy=PunctuationEnergy.PERIOD)
        text = "Texto com exclamação!"
        
        result = modulator.apply_style_to_text(text, style)
        
        assert result.endswith(".")
        assert "!" not in result
    
    def test_punctuation_ellipsis(self, modulator):
        """Substituir pontuação por reticências"""
        style = ExpressionStyle(punctuation_energy=PunctuationEnergy.ELLIPSIS)
        text = "Texto com ponto final."
        
        result = modulator.apply_style_to_text(text, style)
        
        assert result.endswith("...")
    
    def test_remove_emojis(self, modulator):
        """Remover emojis quando frequency < 0.2"""
        style = ExpressionStyle(emoji_frequency=0.0)
        text = "Texto com emoji 😊 no meio."
        
        result = modulator.apply_style_to_text(text, style)
        
        assert "😊" not in result
        assert "Texto com emoji" in result
    
    def test_remove_proactive_questions(self, modulator):
        """Remover perguntas de seguimento quando proactivity < 0.3"""
        style = ExpressionStyle(proactivity=0.1)
        text = "Feito. Precisas de mais alguma coisa?"
        
        result = modulator.apply_style_to_text(text, style)
        
        assert "Feito" in result
        assert "Precisas de mais alguma coisa?" not in result


class TestProsodyParams:
    """Testes para parâmetros de prosódia"""
    
    def test_default_prosody(self, modulator):
        """Parâmetros padrão de prosódia"""
        style = ExpressionStyle()
        
        params = modulator.get_prosody_params(style)
        
        assert params["rate"] == 1.0
        assert params["volume"] == 1.0
        assert params["pitch"] == 1.0
        assert params["pitch_range"] == 1.0
        assert params["pause_duration_ms"] == 500
    
    def test_fast_speaking_rate(self, modulator):
        """Taxa de fala rápida"""
        style = ExpressionStyle(speaking_rate=1.3)
        
        params = modulator.get_prosody_params(style)
        
        assert params["rate"] == 1.3
    
    def test_long_pauses(self, modulator):
        """Pausas longas"""
        style = ExpressionStyle(pause_duration_factor=1.5)
        
        params = modulator.get_prosody_params(style)
        
        assert params["pause_duration_ms"] == 750  # 1.5 * 500
    
    def test_low_volume(self, modulator):
        """Volume baixo"""
        style = ExpressionStyle(volume_factor=0.8)
        
        params = modulator.get_prosody_params(style)
        
        assert params["volume"] == 0.8
    
    def test_expressive_pitch(self, modulator):
        """Pitch expressivo"""
        style = ExpressionStyle(pitch_variation=1.3)
        
        params = modulator.get_prosody_params(style)
        
        assert params["pitch_range"] == 1.3


class TestStyleDescription:
    """Testes para geração de descrição de estilo"""
    
    def test_irritated_description(self, modulator, mock_affective_engine):
        """Descrição quando irritado"""
        mock_affective_engine.states.irritation = 0.7
        
        style = modulator.calculate_expression_style()
        
        assert "frases muito curtas" in style.description
        assert "tom seco" in style.description
        assert "sem emojis" in style.description
        assert "minimalista" in style.description
    
    def test_engaged_description(self, modulator, mock_affective_engine):
        """Descrição quando engajado"""
        mock_affective_engine.states.engagement = 0.8
        mock_affective_engine.states.closeness = 0.7
        mock_affective_engine.states.care = 0.7
        
        style = modulator.calculate_expression_style()
        
        assert "tom energético" in style.description
        assert "com emojis" in style.description
        assert "elaborado" in style.description
        assert "sugere/pergunta" in style.description


class TestNoAffectiveEngine:
    """Testes sem affective engine"""
    
    def test_no_engine_returns_default(self):
        """Sem affective engine → retorna estilo neutro"""
        modulator = ExpressionModulator(affective_engine=None)
        
        style = modulator.calculate_expression_style()
        
        # Verificar valores padrão
        assert style.sentence_length_factor == 1.0
        assert style.punctuation_energy == PunctuationEnergy.PERIOD
        assert style.verbosity == 0.7


class TestIntegration:
    """Testes de integração"""
    
    def test_full_flow_irritated(self, modulator, mock_affective_engine):
        """Fluxo completo: irritado → texto modificado"""
        mock_affective_engine.states.irritation = 0.7
        mock_affective_engine.states.withdrawal = 0.5
        
        text = "Claro! Posso ajudar-te com isso! Tens mais alguma pergunta? 😊"
        
        # Calcular estilo
        style = modulator.calculate_expression_style()
        
        # Aplicar ao texto
        result = modulator.apply_style_to_text(text, style)
        
        # Verificações
        assert len(result) < len(text)  # Texto mais curto
        assert "😊" not in result  # Emoji removido
        assert result.endswith(".")  # Pontuação seca
        assert "Tens mais alguma pergunta" not in result  # Pergunta removida
    
    def test_full_flow_caring(self, modulator, mock_affective_engine):
        """Fluxo completo: cuidadoso → texto preservado/elaborado"""
        mock_affective_engine.states.care = 0.8
        mock_affective_engine.states.engagement = 0.7
        mock_affective_engine.states.closeness = 0.7
        
        text = "Entendo. Isso deve ser difícil."
        
        # Calcular estilo
        style = modulator.calculate_expression_style()
        
        # Aplicar ao texto
        result = modulator.apply_style_to_text(text, style)
        
        # Verificações
        assert len(result) >= len(text)  # Texto preservado
        # Pontuação pode ter mudado para exclamação
        assert style.punctuation_energy in [PunctuationEnergy.EXCLAMATION, PunctuationEnergy.QUESTION]
