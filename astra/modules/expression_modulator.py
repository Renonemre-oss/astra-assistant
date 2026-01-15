"""
Expression Modulator - Tradução de Estados Afetivos em Expressão

Estados internos invisíveis → Expressão SENTIDA pelo utilizador

Não basta TER emoções. Tem de EXPRESSÁ-las de forma coerente.
Caso contrário, são apenas números numa base de dados.

O salto de "inteligente" para "vivo".

Author: ASTRA Team
Co-Authored-By: Warp <agent@warp.dev>
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum
import re


class PunctuationEnergy(Enum):
    """Tipo de pontuação que expressa energia/tom"""
    PERIOD = "."           # Neutro/seco
    EXCLAMATION = "!"      # Energético/entusiasmo
    QUESTION = "?"         # Curioso/engajado
    ELLIPSIS = "..."       # Pensativo/hesitante
    NONE = ""              # Silêncio/minimalista


@dataclass
class ExpressionStyle:
    """Estilo de expressão calculado a partir de estados afetivos"""
    
    # Parâmetros textuais
    sentence_length_factor: float = 1.0  # 0.3=curto, 1.0=normal, 1.5=longo
    punctuation_energy: PunctuationEnergy = PunctuationEnergy.PERIOD
    emoji_frequency: float = 0.0  # 0.0=nenhum, 1.0=frequente
    formality: float = 0.3  # 0.0=casual, 1.0=formal
    verbosity: float = 0.7  # 0.0=minimalista, 1.0=elaborado
    proactivity: float = 0.5  # 0.0=só responde, 1.0=sugere/pergunta
    
    # Parâmetros de prosódia (para TTS)
    speaking_rate: float = 1.0  # 0.5=lento, 1.5=rápido
    pause_duration_factor: float = 1.0  # 0.5=pausas curtas, 2.0=longas
    volume_factor: float = 1.0  # 0.5=baixo, 1.0=normal
    pitch_variation: float = 1.0  # 0.5=monotônico, 1.5=expressivo
    
    # Comportamentais
    use_intentional_delay: bool = False  # Responder com delay intencional
    delay_seconds: float = 0.0  # Quantos segundos esperar
    prefer_silence: bool = False  # Às vezes não responder é válido
    
    # Meta
    description: str = ""  # Descrição do estilo


class ExpressionModulator:
    """Modula expressão baseado em estados afetivos"""
    
    def __init__(self, affective_engine=None):
        """
        Inicializar Expression Modulator
        
        Args:
            affective_engine: Referência ao AffectiveStateEngine
        """
        self.affective_engine = affective_engine
    
    def calculate_expression_style(self) -> ExpressionStyle:
        """
        Calcula estilo de expressão baseado em estados afetivos atuais.
        
        Returns:
            ExpressionStyle com parâmetros de expressão
        """
        if not self.affective_engine:
            return ExpressionStyle()  # Default neutro
        
        states = self.affective_engine.states
        style = ExpressionStyle()
        
        # === CÁLCULO DE PARÂMETROS ===
        
        # 1. SENTENCE LENGTH
        # Irritado/withdrawal → frases curtas
        # Engajado/care → frases normais/longas
        if states.irritation > 0.6 or states.withdrawal > 0.6:
            style.sentence_length_factor = 0.3  # Muito curto
        elif states.irritation > 0.4 or states.withdrawal > 0.4:
            style.sentence_length_factor = 0.6  # Curto
        elif states.engagement > 0.7 and states.care > 0.6:
            style.sentence_length_factor = 1.3  # Longo
        else:
            style.sentence_length_factor = 1.0  # Normal
        
        # 2. PUNCTUATION ENERGY
        if states.irritation > 0.6:
            style.punctuation_energy = PunctuationEnergy.PERIOD  # Seco
        elif states.withdrawal > 0.7:
            style.punctuation_energy = PunctuationEnergy.ELLIPSIS  # Hesitante
        elif states.engagement > 0.7 and states.closeness > 0.6:
            style.punctuation_energy = PunctuationEnergy.EXCLAMATION  # Energético
        elif states.engagement > 0.6:
            style.punctuation_energy = PunctuationEnergy.QUESTION  # Curioso
        else:
            style.punctuation_energy = PunctuationEnergy.PERIOD  # Neutro
        
        # 3. EMOJI FREQUENCY
        # Care + closeness alto → emojis
        # Irritation/formal → sem emojis
        if states.irritation > 0.5 or states.disappointment > 0.5:
            style.emoji_frequency = 0.0  # Nenhum
        elif states.closeness > 0.7 and states.care > 0.6:
            style.emoji_frequency = 0.6  # Frequente
        elif states.closeness > 0.5:
            style.emoji_frequency = 0.3  # Ocasional
        else:
            style.emoji_frequency = 0.1  # Raro
        
        # 4. FORMALITY
        # Withdrawal/respect baixo → mais formal
        # Closeness alto → casual
        if states.withdrawal > 0.6 or states.respect < 0.4:
            style.formality = 0.7  # Formal
        elif states.closeness > 0.7:
            style.formality = 0.2  # Muito casual
        else:
            style.formality = 0.4  # Equilibrado
        
        # 5. VERBOSITY
        # Withdrawal/irritation → minimalista
        # Engagement/care → elaborado
        if states.withdrawal > 0.6 or states.irritation > 0.6:
            style.verbosity = 0.2  # Minimalista
        elif states.withdrawal > 0.4 or states.irritation > 0.4:
            style.verbosity = 0.5  # Conciso
        elif states.engagement > 0.7 and states.care > 0.5:
            style.verbosity = 0.9  # Elaborado
        else:
            style.verbosity = 0.7  # Normal
        
        # 6. PROACTIVITY
        # Care + engagement → proativo (pergunta, sugere)
        # Withdrawal/irritation → reativo (só responde)
        if states.withdrawal > 0.6 or states.irritation > 0.6:
            style.proactivity = 0.0  # Zero iniciativa
        elif states.care > 0.6 and states.engagement > 0.7:
            style.proactivity = 0.8  # Muito proativo
        elif states.engagement > 0.5:
            style.proactivity = 0.5  # Moderado
        else:
            style.proactivity = 0.2  # Baixo
        
        # === PROSÓDIA (para TTS) ===
        
        # 7. SPEAKING RATE
        # Entusiasmo → rápido
        # Vulnerabilidade (user) / care alto → lento (dar espaço)
        # Irritação → normal/rápido (quer acabar)
        if states.engagement > 0.8 and states.closeness > 0.6:
            style.speaking_rate = 1.3  # Rápido (entusiasmo)
        elif states.care > 0.7:
            style.speaking_rate = 0.8  # Lento (compassivo)
        elif states.irritation > 0.6:
            style.speaking_rate = 1.1  # Ligeiramente rápido
        else:
            style.speaking_rate = 1.0  # Normal
        
        # 8. PAUSE DURATION
        # Care alto + vulnerabilidade → pausas longas (dar espaço)
        # Irritação/withdrawal → pausas curtas (quer acabar)
        if states.care > 0.7:
            style.pause_duration_factor = 1.5  # Pausas longas
        elif states.irritation > 0.6 or states.withdrawal > 0.6:
            style.pause_duration_factor = 0.5  # Pausas curtas
        else:
            style.pause_duration_factor = 1.0  # Normal
        
        # 9. VOLUME
        # Vulnerabilidade/care alto → volume mais baixo (intimidade)
        # Irritação → volume normal (não grita, mantém controle)
        if states.care > 0.7 and states.closeness > 0.6:
            style.volume_factor = 0.8  # Ligeiramente baixo
        else:
            style.volume_factor = 1.0  # Normal
        
        # 10. PITCH VARIATION
        # Engagement alto → expressivo
        # Withdrawal/irritation → monótono
        if states.withdrawal > 0.6 or states.irritation > 0.6:
            style.pitch_variation = 0.6  # Monótono
        elif states.engagement > 0.7:
            style.pitch_variation = 1.3  # Expressivo
        else:
            style.pitch_variation = 1.0  # Normal
        
        # === COMPORTAMENTAIS ===
        
        # 11. INTENTIONAL DELAY
        # Protective mode ou withdrawal muito alto → delay antes de responder
        if states.protective_mode or states.withdrawal > 0.8:
            style.use_intentional_delay = True
            style.delay_seconds = 3.0 + (states.withdrawal * 5.0)  # 3-8 segundos
        
        # 12. PREFER SILENCE
        # Às vezes não responder É a resposta
        if states.withdrawal > 0.85 and states.irritation > 0.7:
            style.prefer_silence = True
        
        # === DESCRIÇÃO ===
        style.description = self._generate_style_description(style, states)
        
        return style
    
    def _generate_style_description(self, style: ExpressionStyle, states) -> str:
        """Gera descrição legível do estilo"""
        parts = []
        
        # Sentença
        if style.sentence_length_factor < 0.5:
            parts.append("frases muito curtas")
        elif style.sentence_length_factor > 1.2:
            parts.append("frases elaboradas")
        
        # Tom
        if style.punctuation_energy == PunctuationEnergy.PERIOD and states.irritation > 0.5:
            parts.append("tom seco")
        elif style.punctuation_energy == PunctuationEnergy.EXCLAMATION:
            parts.append("tom energético")
        elif style.punctuation_energy == PunctuationEnergy.ELLIPSIS:
            parts.append("tom hesitante")
        
        # Emojis
        if style.emoji_frequency == 0.0:
            parts.append("sem emojis")
        elif style.emoji_frequency > 0.5:
            parts.append("com emojis")
        
        # Verbosidade
        if style.verbosity < 0.3:
            parts.append("minimalista")
        elif style.verbosity > 0.8:
            parts.append("elaborado")
        
        # Proatividade
        if style.proactivity < 0.2:
            parts.append("não proativo")
        elif style.proactivity > 0.7:
            parts.append("sugere/pergunta")
        
        # Comportamental
        if style.prefer_silence:
            parts.append("preferência por silêncio")
        elif style.use_intentional_delay:
            parts.append(f"delay intencional ({style.delay_seconds:.0f}s)")
        
        return ", ".join(parts) if parts else "expressão neutra"
    
    def apply_style_to_text(self, text: str, style: ExpressionStyle) -> str:
        """
        Aplica estilo de expressão a um texto.
        
        Args:
            text: Texto original
            style: Estilo a aplicar
        
        Returns:
            Texto modificado
        """
        # Se preferência por silêncio, retornar mensagem mínima ou vazio
        if style.prefer_silence:
            return ""  # Silêncio
        
        modified_text = text
        
        # 1. AJUSTAR COMPRIMENTO DE FRASES
        if style.sentence_length_factor < 0.7:
            # Encurtar: pegar apenas primeiras frases
            sentences = re.split(r'[.!?]+', modified_text)
            # Manter apenas primeira(s) frase(s)
            num_keep = 1 if style.sentence_length_factor < 0.4 else 2
            modified_text = '. '.join(s.strip() for s in sentences[:num_keep] if s.strip())
            if modified_text and not modified_text.endswith(('.', '!', '?')):
                modified_text += '.'
        
        # 2. AJUSTAR PONTUAÇÃO
        # Substituir pontuação final baseado em energia
        if style.punctuation_energy == PunctuationEnergy.PERIOD:
            modified_text = re.sub(r'[!?]+$', '.', modified_text)
        elif style.punctuation_energy == PunctuationEnergy.ELLIPSIS:
            modified_text = re.sub(r'[.!?]+$', '...', modified_text)
        elif style.punctuation_energy == PunctuationEnergy.EXCLAMATION:
            modified_text = re.sub(r'[.]$', '!', modified_text)
        
        # 3. REMOVER/REDUZIR EMOJIS
        if style.emoji_frequency < 0.2:
            # Remover emojis
            modified_text = re.sub(r'[😀-🙏💀-🙏🌀-🗿🚀-🛿]', '', modified_text)
            modified_text = re.sub(r'\s+', ' ', modified_text).strip()
        
        # 4. REMOVER PROATIVIDADE
        if style.proactivity < 0.3:
            # Remover perguntas de seguimento
            # Exemplo: "Feito. Precisas de mais alguma coisa?" → "Feito."
            sentences = re.split(r'(?<=[.!?])\s+', modified_text)
            # Remover última frase se for pergunta de seguimento
            if len(sentences) > 1 and '?' in sentences[-1]:
                if any(word in sentences[-1].lower() for word in ['mais', 'alguma coisa', 'algo', 'ajuda']):
                    modified_text = ' '.join(sentences[:-1])
        
        return modified_text
    
    def get_prosody_params(self, style: ExpressionStyle) -> dict:
        """
        Retorna parâmetros de prosódia para sistema TTS.
        
        Returns:
            dict com parâmetros para TTS engine
        """
        return {
            "rate": style.speaking_rate,
            "volume": style.volume_factor,
            "pitch": 1.0,  # Base pitch
            "pitch_range": style.pitch_variation,
            "pause_duration_ms": int(style.pause_duration_factor * 500),  # 500ms base
        }
