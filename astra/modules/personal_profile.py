#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal
Módulo de Perfil Pessoal

Sistema completo de gestão de preferências e personalização do utilizador.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path
from ..config import CONFIG, DATABASE_AVAILABLE
from ..utils.utils import salvar_historico, carregar_historico

logger = logging.getLogger(__name__)

class PersonalProfile:
    """
    Gerenciador do perfil pessoal e preferências do utilizador.
    Suporta armazenamento local e MySQL.
    """
    
    def __init__(self, database_manager=None):
        self.db_manager = database_manager
        self.facts_cache = {}
        self.load_local_facts()
        
        # Definir categorias de preferências
        self.preference_categories = {
            # Alimentação
            'comida_favorita': {
                'patterns': [
                    "minha comida favorita e", "a minha comida favorita e",
                    "minha comida favorita é", "a minha comida favorita é",
                    "gosto de comer", "prefiro comer"
                ],
                'queries': [
                    "qual a minha comida favorita", "lembras te da minha comida favorita",
                    "que comida gosto", "o que gosto de comer"
                ],
                'display_name': 'Comida favorita'
            },
            'bebida_favorita': {
                'patterns': [
                    "minha bebida favorita e", "a minha bebida favorita e",
                    "minha bebida favorita é", "a minha bebida favorita é",
                    "gosto de beber"
                ],
                'queries': [
                    "qual a minha bebida favorita", "lembras te da minha bebida favorita",
                    "que bebida gosto"
                ],
                'display_name': 'Bebida favorita'
            },
            
            # Música/Filmes
            'musica_favorita': {
                'patterns': [
                    "minha musica favorita e", "a minha musica favorita e",
                    "minha musica favorita é", "a minha musica favorita é"
                ],
                'queries': [
                    "qual a minha musica favorita", "lembras te da minha musica favorita"
                ],
                'display_name': 'Música favorita'
            },
            'artista_favorito': {
                'patterns': [
                    "meu artista favorito e", "o meu artista favorito e",
                    "meu artista favorito é", "o meu artista favorito é",
                    "minha banda favorita e", "a minha banda favorita e"
                ],
                'queries': [
                    "qual o meu artista favorito", "lembras te do meu artista favorito",
                    "qual a minha banda favorita"
                ],
                'display_name': 'Artista favorito'
            },
            'genero_musical': {
                'patterns': [
                    "meu genero musical favorito e", "o meu genero musical favorito e",
                    "meu genero musical favorito é", "o meu genero musical favorito é",
                    "gosto de ouvir"
                ],
                'queries': [
                    "qual o meu genero musical favorito", "que musica gosto de ouvir"
                ],
                'display_name': 'Género musical favorito'
            },
            'filme_favorito': {
                'patterns': [
                    "meu filme favorito e", "o meu filme favorito e",
                    "meu filme favorito é", "o meu filme favorito é",
                    "minha serie favorita e", "a minha serie favorita e"
                ],
                'queries': [
                    "qual o meu filme favorito", "qual a minha serie favorita"
                ],
                'display_name': 'Filme/série favorita'
            },
            
            # Estilo de vida
            'cor_favorita': {
                'patterns': [
                    "minha cor favorita e", "a minha cor favorita e",
                    "minha cor favorita é", "a minha cor favorita é"
                ],
                'queries': [
                    "qual a minha cor favorita", "lembras te da minha cor favorita"
                ],
                'display_name': 'Cor favorita'
            },
            'desporto_favorito': {
                'patterns': [
                    "meu desporto favorito e", "o meu desporto favorito e",
                    "meu desporto favorito é", "o meu desporto favorito é",
                    "meu esporte favorito e"
                ],
                'queries': [
                    "qual o meu desporto favorito", "qual o meu esporte favorito"
                ],
                'display_name': 'Desporto favorito'
            },
            'hobby_favorito': {
                'patterns': [
                    "meu hobby favorito e", "o meu hobby favorito e",
                    "meu hobby favorito é", "o meu hobby favorito é",
                    "o que eu gosto de fazer e"
                ],
                'queries': [
                    "qual o meu hobby favorito", "o que gosto de fazer"
                ],
                'display_name': 'Hobby favorito'
            },
            'animal_favorito': {
                'patterns': [
                    "meu animal favorito e", "o meu animal favorito e",
                    "meu animal favorito é", "o meu animal favorito é"
                ],
                'queries': [
                    "qual o meu animal favorito"
                ],
                'display_name': 'Animal favorito'
            },
            'estacao_favorita': {
                'patterns': [
                    "minha estacao favorita e", "a minha estacao favorita e",
                    "minha estacao favorita é", "a minha estacao favorita é"
                ],
                'queries': [
                    "qual a minha estacao favorita"
                ],
                'display_name': 'Estação favorita'
            },
            'cidade_favorita': {
                'patterns': [
                    "minha cidade favorita e", "a minha cidade favorita e",
                    "minha cidade favorita é", "a minha cidade favorita é",
                    "minha cidade preferida e", "a minha cidade preferida e"
                ],
                'queries': [
                    "qual a minha cidade favorita", "qual a minha cidade preferida"
                ],
                'display_name': 'Cidade favorita'
            },
        }
    
    def load_local_facts(self):
        """Carrega fatos pessoais do arquivo JSON local."""
        try:
            facts_file = CONFIG["facts_file"]
            if facts_file.exists():
                with open(facts_file, "r", encoding="utf-8") as f:
                    self.facts_cache = json.load(f)
                logger.info(f"Fatos pessoais carregados: {len(self.facts_cache)} itens")
            else:
                self.facts_cache = {}
        except Exception as e:
            logger.error(f"Erro ao carregar fatos pessoais: {e}")
            self.facts_cache = {}
    
    def save_local_facts(self) -> bool:
        """Salva fatos pessoais no arquivo JSON local."""
        try:
            facts_file = CONFIG["facts_file"]
            facts_file.parent.mkdir(exist_ok=True)
            
            with open(facts_file, "w", encoding="utf-8") as f:
                json.dump(self.facts_cache, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Fatos pessoais salvos: {len(self.facts_cache)} itens")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar fatos pessoais: {e}")
            return False
    
    def save_preference(self, key: str, value: str) -> bool:
        """
        Salva uma preferência tanto localmente quanto na base de dados.
        
        Args:
            key: Chave da preferência
            value: Valor da preferência
            
        Returns:
            bool: True se salvou com sucesso
        """
        if not key or not value or not value.strip():
            return False
        
        # Salvar localmente
        self.facts_cache[key] = value.strip()
        local_success = self.save_local_facts()
        
        # Salvar na base de dados se disponível
        db_success = True
        if DATABASE_AVAILABLE and self.db_manager:
            try:
                self.db_manager.cursor.execute("""
                    INSERT INTO user_preferences (preference_key, preference_value, data_type)
                    VALUES (%s, %s, 'string')
                    ON DUPLICATE KEY UPDATE 
                        preference_value = VALUES(preference_value), 
                        updated_at = CURRENT_TIMESTAMP
                """, (key, value.strip()))
                
                logger.info(f"Preferência salva na BD: {key} = {value}")
                
            except Exception as e:
                logger.warning(f"Erro ao salvar na BD: {e}")
                db_success = False
        
        return local_success and db_success
    
    def get_preference(self, key: str) -> Optional[str]:
        """
        Obtém uma preferência, priorizando a base de dados.
        
        Args:
            key: Chave da preferência
            
        Returns:
            str: Valor da preferência ou None se não encontrada
        """
        # Tentar obter da base de dados primeiro
        if DATABASE_AVAILABLE and self.db_manager:
            try:
                self.db_manager.cursor.execute(
                    "SELECT preference_value FROM user_preferences WHERE preference_key = %s",
                    (key,)
                )
                row = self.db_manager.cursor.fetchone()
                if row:
                    value = row.get('preference_value')
                    # Atualizar cache local
                    self.facts_cache[key] = value
                    return value
                    
            except Exception as e:
                logger.debug(f"Erro ao consultar BD: {e}")
        
        # Fallback para cache local
        return self.facts_cache.get(key)
    
    def process_user_input(self, comando_lower: str) -> str:
        """
        Processa entrada do utilizador para detetar e salvar/consultar preferências.
        
        Args:
            comando_lower: Comando do utilizador em minúsculas
            
        Returns:
            str: Resposta gerada ou string vazia se não processou nada
        """
        logger.info(f"Processando comando para perfil: '{comando_lower}'")
        
        # 1) Verificar se está a declarar uma preferência
        for key, config in self.preference_categories.items():
            for pattern in config['patterns']:
                if pattern in comando_lower:
                    # Extrair valor
                    parts = comando_lower.split(pattern, 1)
                    if len(parts) > 1:
                        valor = parts[1].strip(" .!?:;\n\t")
                        if valor:
                            logger.info(f"Pattern '{pattern}' encontrado, valor: '{valor}'")
                            
                            # Salvar preferência
                            if self.save_preference(key, valor):
                                logger.info(f"Preferência salva: {key} = {valor}")
                                return f"Perfeito! Guardei que a sua {config['display_name'].lower()} é '{valor}'."
                            else:
                                return f"Erro ao guardar a preferência. Tente novamente."
        
        # 2) Verificar se está a consultar uma preferência
        for key, config in self.preference_categories.items():
            for pattern in config['queries']:
                if pattern in comando_lower:
                    valor = self.get_preference(key)
                    if valor:
                        return f"Sim, lembro-me. A sua {config['display_name'].lower()} é {valor}."
                    else:
                        return f"Ainda não me disse a sua {config['display_name'].lower()}. Pode dizer, por exemplo: 'A minha {config['display_name'].lower()} é ...'"
        
        return ""
    
    def get_profile_for_prompt(self, context_relevance: str = "general") -> str:
        """
        Gera informação do perfil para incluir no prompt do AI de forma contextual.
        
        Args:
            context_relevance: Tipo de contexto ('general', 'food_related', 'personal_info', 'minimal')
        
        Returns:
            str: Informação formatada do perfil
        """
        try:
            # Obter todas as preferências
            all_preferences = {}
            
            # Da base de dados se disponível
            if DATABASE_AVAILABLE and self.db_manager:
                try:
                    self.db_manager.cursor.execute(
                        "SELECT preference_key, preference_value FROM user_preferences"
                    )
                    db_prefs = self.db_manager.cursor.fetchall()
                    for pref in db_prefs:
                        all_preferences[pref['preference_key']] = pref['preference_value']
                except Exception as e:
                    logger.debug(f"Erro ao carregar preferências da BD: {e}")
            
            # Adicionar do cache local
            for key, value in self.facts_cache.items():
                if key not in all_preferences:
                    all_preferences[key] = value
            
            if not all_preferences:
                return "PERFIL: O utilizador ainda não partilhou preferências pessoais."
            
            # Filtrar preferências baseado no contexto
            relevant_preferences = self._filter_preferences_by_context(all_preferences, context_relevance)
            
            if not relevant_preferences:
                return ""
            
            # Construir informação do perfil
            if context_relevance == "minimal":
                # Para contexto mínimo, apenas informação básica
                basic_info = []
                if 'nome_completo' in relevant_preferences:
                    basic_info.append(f"Nome: {relevant_preferences['nome_completo']}")
                if basic_info:
                    return "PERFIL: " + ", ".join(basic_info) + ". (Use apenas se relevante para a conversa)"
                return ""
            
            profile_lines = ["INFORMAÇÃO CONTEXTUAL:"]
            
            for key, value in relevant_preferences.items():
                if key in self.preference_categories:
                    display_name = self.preference_categories[key]['display_name']
                    profile_lines.append(f"- {display_name}: {value}")
                else:
                    # Para preferências não categorizadas
                    display_name = key.replace('_', ' ').title()
                    profile_lines.append(f"- {display_name}: {value}")
            
            # Instrução contextual mais inteligente
            if context_relevance == "food_related":
                profile_lines.append("\nUse esta informação apenas se a conversa for sobre comida/alimentação.")
            elif context_relevance == "personal_info":
                profile_lines.append("\nUse esta informação para responder perguntas pessoais diretas.")
            else:
                profile_lines.append("\nUse esta informação apenas quando naturalmente relevante para a conversa.")
            
            return "\n".join(profile_lines)
            
        except Exception as e:
            logger.error(f"Erro ao gerar perfil para prompt: {e}")
            return ""
    
    def _filter_preferences_by_context(self, preferences: Dict[str, str], context: str) -> Dict[str, str]:
        """
        Filtra preferências baseado no contexto da conversa.
        
        Args:
            preferences: Dicionário com todas as preferências
            context: Tipo de contexto
            
        Returns:
            Dict: Preferências filtradas
        """
        if context == "minimal":
            # Apenas informação essencial (nome)
            return {k: v for k, v in preferences.items() if k in ['nome_completo', 'nome']}
        
        elif context == "food_related":
            # Apenas informação sobre comida
            food_keys = ['comida_favorita', 'bebida_favorita', 'restaurante_favorito']
            return {k: v for k, v in preferences.items() if k in food_keys}
        
        elif context == "personal_info":
            # Informação pessoal básica (sem comida a menos que perguntado)
            personal_keys = ['nome_completo', 'idade', 'profissao', 'cidade', 'hobbies']
            return {k: v for k, v in preferences.items() if k in personal_keys}
        
        else:  # "general" ou outros
            # Contexto geral - apenas informação muito relevante
            general_keys = ['nome_completo', 'nome']
            return {k: v for k, v in preferences.items() if k in general_keys}
    
    def get_all_preferences(self) -> Dict[str, str]:
        """
        Obtém todas as preferências do utilizador.
        
        Returns:
            Dict: Todas as preferências
        """
        all_preferences = {}
        
        # Da base de dados
        if DATABASE_AVAILABLE and self.db_manager:
            try:
                self.db_manager.cursor.execute(
                    "SELECT preference_key, preference_value FROM user_preferences"
                )
                db_prefs = self.db_manager.cursor.fetchall()
                for pref in db_prefs:
                    all_preferences[pref['preference_key']] = pref['preference_value']
            except Exception as e:
                logger.debug(f"Erro ao carregar da BD: {e}")
        
        # Do cache local (sobrescreve conflitos)
        all_preferences.update(self.facts_cache)
        
        return all_preferences
    
    def get_preference_statistics(self) -> Dict[str, any]:
        """
        Obtém estatísticas das preferências.
        
        Returns:
            Dict: Estatísticas do perfil
        """
        prefs = self.get_all_preferences()
        
        # Categorizar preferências
        categorized = {}
        for key, value in prefs.items():
            if key in self.preference_categories:
                category = self.preference_categories[key]['display_name']
                category_group = category.split()[0]  # Primeira palavra
                
                if category_group not in categorized:
                    categorized[category_group] = []
                
                categorized[category_group].append({
                    'key': key,
                    'name': category,
                    'value': value
                })
        
        return {
            'total_preferences': len(prefs),
            'categories': categorized,
            'completion_rate': len(prefs) / len(self.preference_categories) * 100
        }
    
    def suggest_missing_preferences(self) -> List[str]:
        """
        Sugere preferências que ainda não foram definidas.
        
        Returns:
            List[str]: Lista de sugestões
        """
        current_prefs = set(self.get_all_preferences().keys())
        all_possible = set(self.preference_categories.keys())
        missing = all_possible - current_prefs
        
        suggestions = []
        for key in missing:
            display_name = self.preference_categories[key]['display_name']
            example_pattern = self.preference_categories[key]['patterns'][0]
            
            suggestions.append(f"Pode dizer '{example_pattern.replace('e', 'é')} ...' para definir {display_name.lower()}")
        
        return suggestions[:5]  # Máximo 5 sugestões
    
    def export_profile(self) -> Dict[str, any]:
        """
        Exporta o perfil completo para backup.
        
        Returns:
            Dict: Perfil completo
        """
        return {
            'preferences': self.get_all_preferences(),
            'statistics': self.get_preference_statistics(),
            'categories': list(self.preference_categories.keys()),
            'export_timestamp': str(datetime.now())
        }
    
    def import_profile(self, profile_data: Dict[str, any]) -> bool:
        """
        Importa perfil de backup.
        
        Args:
            profile_data: Dados do perfil
            
        Returns:
            bool: True se importou com sucesso
        """
        try:
            preferences = profile_data.get('preferences', {})
            
            success_count = 0
            for key, value in preferences.items():
                if self.save_preference(key, value):
                    success_count += 1
            
            logger.info(f"Perfil importado: {success_count}/{len(preferences)} preferências")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Erro ao importar perfil: {e}")
            return False

# ==========================
# FUNÇÕES DE TESTE
# ==========================
def test_personal_profile():
    """Testa o sistema de perfil pessoal."""
    print("👤 TESTE DO PERFIL PESSOAL")
    print("=" * 40)
    
    profile = PersonalProfile()
    
    # Teste 1: Salvar preferência
    print("\n📝 Teste 1: Salvar preferência")
    result = profile.process_user_input("a minha comida favorita é pizza")
    print(f"Resultado: {result}")
    
    # Teste 2: Consultar preferência
    print("\n📝 Teste 2: Consultar preferência")
    result = profile.process_user_input("qual a minha comida favorita")
    print(f"Resultado: {result}")
    
    # Teste 3: Gerar perfil para prompt
    print("\n📝 Teste 3: Perfil para prompt")
    prompt_info = profile.get_profile_for_prompt()
    print(f"Perfil: {prompt_info}")
    
    # Teste 4: Estatísticas
    print("\n📝 Teste 4: Estatísticas")
    stats = profile.get_preference_statistics()
    print(f"Estatísticas: {stats}")
    
    # Teste 5: Sugestões
    print("\n📝 Teste 5: Sugestões")
    suggestions = profile.suggest_missing_preferences()
    for suggestion in suggestions[:3]:
        print(f"- {suggestion}")

if __name__ == "__main__":
    test_personal_profile()
