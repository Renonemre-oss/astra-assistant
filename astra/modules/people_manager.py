#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal
Módulo de Gestão de Pessoas

Sistema automático para reconhecer e guardar informações sobre pessoas
que o utilizador menciona nas conversas.
"""

import json
import logging
import re
from datetime import datetime, date
from typing import Dict, Optional, List, Any
from pathlib import Path
from ..config import CONFIG, DATABASE_AVAILABLE
from ..utils.user_profile import UserProfile

logger = logging.getLogger(__name__)

class PeopleManager:
    """
    Gerenciador de pessoas conhecido pelo utilizador.
    Reconhece automaticamente informações sobre pessoas e armazena-as.
    """
    
    def __init__(self, database_manager=None):
        self.db_manager = database_manager
        self.people_cache = {}
        
        # Inicializar perfil do utilizador
        self.user_profile = UserProfile(database_manager)
        
        # Padrões para reconhecimento automático de informações sobre pessoas
        self.recognition_patterns = {
            # Apresentação de pessoas
            'introduction': [
                r'(?:esta é|este é|apresento[- ](?:te|vos)?|conhece(?:s|m)?) (?:a|o) ([A-Z][a-záàâãéèêíïóôõöúçñ]+)',
                r'(?:a|o) ([A-Z][a-záàâãéèêíïóôõöúçñ]+) é (?:a|o) (?:minha|meu) (.+)',
                r'([A-Z][a-záàâãéèêíïóôõöúçñ]+) é (?:uma|um) (?:amiga|amigo|pessoa|colega)'
            ],
            
            # Relacionamentos familiares
            'family': {
                'mãe': ['minha mãe', 'a mãe', 'minha mae', 'a mae'],
                'pai': ['meu pai', 'o pai'],
                'irmã': ['minha irmã', 'minha irma', 'a irmã', 'a irma'],
                'irmão': ['meu irmão', 'meu irmao', 'o irmão', 'o irmao'],
                'filha': ['minha filha', 'a filha'],
                'filho': ['meu filho', 'o filho'],
                'esposa': ['minha esposa', 'a esposa', 'minha mulher'],
                'marido': ['meu marido', 'o marido'],
                'namorada': ['minha namorada', 'a namorada'],
                'namorado': ['meu namorado', 'o namorado'],
                'avó': ['minha avó', 'minha avo', 'a avó', 'a avo'],
                'avô': ['meu avô', 'meu avo', 'o avô', 'o avo'],
                'tia': ['minha tia', 'a tia'],
                'tio': ['meu tio', 'o tio'],
                'prima': ['minha prima', 'a prima'],
                'primo': ['meu primo', 'o primo'],
                'sogra': ['minha sogra', 'a sogra'],
                'sogro': ['meu sogro', 'o sogro']
            },
            
            # Relacionamentos sociais
            'social': {
                'amiga': ['minha amiga', 'uma amiga', 'a amiga'],
                'amigo': ['meu amigo', 'um amigo', 'o amigo'],
                'colega': ['minha colega', 'meu colega', 'uma colega', 'um colega'],
                'chefe': ['meu chefe', 'minha chefe', 'o chefe', 'a chefe'],
                'vizinha': ['minha vizinha', 'a vizinha'],
                'vizinho': ['meu vizinho', 'o vizinho']
                # Remover professor/professora daqui pois são profissões, não relacionamentos
            },
            
            # Características pessoais
            'personality': [
                r'(?:é|está|anda) (?:muito )?(?:alegre|triste|engraçada|engraçado|simpática|simpático|inteligente|esperta|esperto|carinhosa|carinhoso|teimosa|teimoso)',
                r'(?:gosta de|adora|detesta|odeia) (.+)',
                r'(?:é (?:muito )?(?:tímida|tímido|extrovertida|extrovertido|calma|calmo|nervosa|nervoso))'
            ],
            
            # Gostos e interesses
            'interests': [
                r'(?:gosta de|adora|ama|curte) (?:ouvir|ver|fazer|comer|beber|jogar) (.+)',
                r'(?:o|a) (?:filme|música|comida|bebida|jogo|livro|série) (?:favorita|favorito) (?:dela|dele) é (.+)',
                r'(?:ela|ele) (?:pratica|faz|joga) (.+)'
            ],
            
            # Profissão
            'profession': [
                r'(?:trabalha como|é|atua como) (?:uma |um )?(.+?)(?:\s|$)',
                r'(?:profissão|trabalho|emprego) (?:dela|dele) é (.+)',
                r'(?:ela|ele) é (?:uma |um )?(.+?) de profissão'
            ],
            
            # Idade
            'age': [
                r'(?:tem|possui) (\d+) anos?',
                r'(?:idade|anos?) (?:dela|dele) (?:é|são) (\d+)',
                r'(\d+) anos? de idade'
            ]
        }
    
    def process_user_input(self, text: str, context: str = '', conversation_count: int = 0) -> Dict[str, Any]:
        """
        Processa entrada do utilizador para extrair informações sobre pessoas.
        
        Args:
            text: Texto a processar
            context: Contexto adicional da conversa
            conversation_count: Número de mensagens na conversa
            
        Returns:
            Dict com informações extraídas e ações realizadas
        """
        text_lower = text.lower()
        results = {
            'people_mentioned': [],
            'information_extracted': [],
            'actions_performed': [],
            'response_suggestions': [],
            'user_profile_updated': False,
            'ask_for_profile': False
        }
        
        logger.info(f"Processando texto para pessoas: '{text_lower}'")
        
        # 1. PRIMEIRO: Verificar se há informações sobre o próprio utilizador
        user_info = self.user_profile.detect_user_from_input(text)
        if user_info:
            # Atualizar perfil do utilizador
            if self.user_profile.create_or_update_profile(user_info):
                results['user_profile_updated'] = True
                results['actions_performed'].append(f"Perfil do utilizador atualizado")
                if user_info.get('name'):
                    results['response_suggestions'].append(f"Obrigado por me dizeres o teu nome, {user_info['name']}! Vou lembrar-me disso.")
                else:
                    results['response_suggestions'].append("Obrigado por partilhares essa informação comigo!")
        
        # 2. Verificar se deve perguntar sobre o perfil do utilizador
        if self.user_profile.should_ask_for_profile(conversation_count):
            results['ask_for_profile'] = True
            questions = self.user_profile.get_profile_questions()
            if questions:
                results['response_suggestions'].append(questions[0])  # Começar com a primeira pergunta
        
        # 1. Detectar menções de pessoas
        people_mentioned = self._detect_people_mentions(text_lower)
        results['people_mentioned'] = people_mentioned
        
        # 2. Para cada pessoa mencionada, extrair informações
        for person_info in people_mentioned:
            extracted_info = self._extract_person_information(text_lower, person_info)
            if extracted_info:
                results['information_extracted'].append(extracted_info)
                
                # 3. Guardar ou atualizar informações
                success = self._save_or_update_person(extracted_info)
                if success:
                    results['actions_performed'].append(f"Informações sobre {extracted_info.get('name', 'pessoa')} guardadas")
                    results['response_suggestions'].append(f"Guardei as informações sobre {extracted_info.get('name', 'essa pessoa')}!")
        
        # 4. Verificar se está a perguntar sobre alguém
        question_response = self._handle_people_questions(text_lower)
        if question_response:
            results['response_suggestions'].append(question_response)
        
        return results
    
    def _detect_people_mentions(self, text: str) -> List[Dict[str, str]]:
        """Detecta menções de pessoas no texto com validação rigorosa."""
        people_found = []
        
        # Lista expandida de palavras que NÃO são nomes
        not_names = {
            'Para', 'Mas', 'Que', 'Como', 'Quando', 'Onde', 'Esta', 'Este', 'Essa', 'Esse',
            'Minha', 'Meu', 'Sua', 'Seu', 'Nossa', 'Nosso', 'Dela', 'Dele', 'Eles', 'Elas',
            'Gosta', 'Adora', 'Comer', 'Beber', 'Fazer', 'Ver', 'Ouvir', 'Jogar', 'Ler',
            'Pizza', 'Rock', 'Música', 'Filme', 'Livro', 'Jogo', 'Comida', 'Bebida',
            'Hoje', 'Ontem', 'Amanhã', 'Sempre', 'Nunca', 'Muito', 'Pouco', 'Bem', 'Mal',
            'Sim', 'Não', 'Talvez', 'Claro', 'Obviamente', 'Realmente', 'Certamente',
            # Adicionar palavras problemáticas identificadas
            'Tem', 'Anos', 'Trabalha', 'Professora', 'Professor', 'Ela', 'Ele', 'Livros',
            'Clássica', 'Clássico', 'Música', 'Engraçado', 'Engraçada', 'Futebol', 'Favorita',
            'Favorito', 'Lasanha', 'Super', 'Inteligente', 'Está', 'Café', 'Engenheira',
            'Engenheiro', 'Software', 'Irmã', 'Irmão', 'Amigo', 'Amiga', 'Colega'
        }
        
        # Padrões específicos para capturar nomes em contextos apropriados
        name_context_patterns = [
            r'(?:meu|minha|o|a)\s+(?:pai|mãe|irmão|irmã|filho|filha|marido|esposa|namorado|namorada|amigo|amiga|colega|primo|prima|tio|tia|avô|avó|cunhado|cunhada)\s+([A-Z][a-záàâãéèêíïóôõöúçñ]{2,})\b',
            r'(?:chama-se|nome é|nome dele é|nome dela é)\s+([A-Z][a-záàâãéèêíïóôõöúçñ]{2,})\b',
            r'([A-Z][a-záàâãéèêíïóôõöúçñ]{2,})\s+(?:é\s+(?:muito|super|bastante)\s+(?:inteligente|engraçado|engraçada|simpático|simpática)|tem\s+\d+\s+anos|trabalha\s+como)',
            r'([A-Z][a-záàâãéèêíïóôõöúçñ]{2,})\s+(?:gosta\s+de|adora|detesta)',
        ]
        
        # Procurar por nomes em contextos específicos
        found_names = set()  # Para evitar duplicatas
        for pattern in name_context_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1).title()
                if (name not in not_names and 
                    name not in found_names and
                    len(name) >= 3 and 
                    name.isalpha() and 
                    not name.isupper()):
                    people_found.append({'name': name, 'position': match.start()})
                    found_names.add(name)
        
        # Procurar por relações familiares/sociais mencionadas
        all_relations = {}
        all_relations.update(self.recognition_patterns['family'])
        all_relations.update(self.recognition_patterns['social'])
        
        for relation, patterns in all_relations.items():
            for pattern in patterns:
                if pattern in text:
                    people_found.append({'relationship': relation, 'mentioned_as': pattern})
        
        return people_found
    
    def _extract_person_information(self, text: str, person_info: Dict) -> Optional[Dict]:
        """Extrai informações detalhadas sobre uma pessoa."""
        extracted = {
            'name': person_info.get('name'),
            'relationship': person_info.get('relationship'),
            'mentioned_as': person_info.get('mentioned_as'),
            'source_text': text[:200] + '...' if len(text) > 200 else text  # Limitar tamanho do texto
        }
        
        # Apenas extrair informações se temos um nome válido ou relacionamento
        if not extracted.get('name') and not extracted.get('relationship'):
            return None
        
        # Extrair características de personalidade de forma mais seletiva
        personality_traits = []
        for pattern in self.recognition_patterns['personality']:
            matches = re.finditer(pattern, text)
            for match in matches:
                trait = match.group(0).strip()
                if len(trait) > 3 and trait not in personality_traits:
                    personality_traits.append(trait)
        if personality_traits:
            extracted['personality_traits'] = '; '.join(personality_traits[:3])  # Limitar a 3 traços
        
        # Extrair gostos e interesses de forma mais seletiva
        interests = []
        for pattern in self.recognition_patterns['interests']:
            matches = re.finditer(pattern, text)
            for match in matches:
                if match.groups() and match.group(1):
                    interest = match.group(1).strip()
                    if len(interest) > 2 and interest not in interests:
                        interests.append(interest)
        if interests:
            extracted['interests'] = '; '.join(interests[:3])  # Limitar a 3 interesses
        
        # Extrair profissão
        for pattern in self.recognition_patterns['profession']:
            match = re.search(pattern, text)
            if match and match.group(1):
                profession = match.group(1).strip()
                if len(profession) > 2:
                    extracted['profession'] = profession
                    break
        
        # Extrair idade
        for pattern in self.recognition_patterns['age']:
            match = re.search(pattern, text)
            if match:
                try:
                    age = int(match.group(1))
                    if 1 <= age <= 120:  # Validar idade razoável
                        extracted['age'] = age
                        break
                except (ValueError, IndexError):
                    continue
        
        # Extrair informações específicas baseadas no contexto
        contextual_info = self._extract_contextual_info(text)
        extracted.update(contextual_info)
        
        # Só retornar se temos pelo menos nome/relacionamento e mais alguma info
        has_identity = extracted.get('name') or extracted.get('relationship')
        has_additional_info = any(extracted.get(key) for key in 
                                ['personality_traits', 'interests', 'profession', 'age', 'favorite_foods', 'favorite_music'])
        
        if has_identity and has_additional_info:
            return extracted
        
        return None
    
    def _extract_contextual_info(self, text: str) -> Dict[str, Any]:
        """Extrai informações contextuais baseadas em padrões específicos."""
        info = {}
        
        # Detectar género baseado em artigos e adjetivos
        if re.search(r'\b(?:ela|a|uma|minha|linda|bonita|inteligente)\b', text):
            info['gender'] = 'feminino'
        elif re.search(r'\b(?:ele|o|um|meu|bonito|inteligente)\b', text):
            info['gender'] = 'masculino'
        
        # Detectar comidas favoritas
        food_patterns = [
            r'(?:gosta de comer|adora|comida favorita (?:dela|dele) é) (.+?)(?:\s|$|\.|\,)',
            r'(?:come sempre|prefere comer|só come) (.+?)(?:\s|$|\.|\,)'
        ]
        for pattern in food_patterns:
            match = re.search(pattern, text)
            if match:
                info['favorite_foods'] = match.group(1).strip()
                break
        
        # Detectar música favorita
        music_patterns = [
            r'(?:gosta de ouvir|música favorita (?:dela|dele) é|ouve sempre) (.+?)(?:\s|$|\.|\,)',
            r'(?:só ouve|prefere ouvir) (.+?)(?:\s|$|\.|\,)'
        ]
        for pattern in music_patterns:
            match = re.search(pattern, text)
            if match:
                info['favorite_music'] = match.group(1).strip()
                break
        
        # Detectar atividades favoritas
        activity_patterns = [
            r'(?:gosta de fazer|adora fazer|faz sempre) (.+?)(?:\s|$|\.|\,)',
            r'(?:hobby (?:dela|dele) é|pratica|joga) (.+?)(?:\s|$|\.|\,)'
        ]
        for pattern in activity_patterns:
            match = re.search(pattern, text)
            if match:
                info['favorite_activities'] = match.group(1).strip()
                break
        
        return info
    
    def _save_or_update_person(self, person_info: Dict) -> bool:
        """Guarda ou atualiza informações sobre uma pessoa."""
        try:
            # Primeiro, tentar encontrar se a pessoa já existe
            existing_person = None
            if person_info.get('name'):
                existing_person = self.get_person_by_name(person_info['name'])
            elif person_info.get('relationship'):
                existing_person = self.get_person_by_relationship(person_info['relationship'])
            
            if existing_person:
                # Atualizar pessoa existente
                return self._update_person(existing_person['id'], person_info)
            else:
                # Criar nova pessoa
                return self._create_person(person_info)
                
        except Exception as e:
            logger.error(f"Erro ao guardar pessoa: {e}")
            return False
    
    def _create_person(self, person_info: Dict) -> bool:
        """Cria uma nova entrada de pessoa na base de dados."""
        # Validar se temos pelo menos um nome ou relacionamento
        if not person_info.get('name') and not person_info.get('relationship'):
            logger.warning("Tentativa de criar pessoa sem nome nem relacionamento")
            return False
            
        if not DATABASE_AVAILABLE or not self.db_manager:
            # Fallback para armazenamento local
            return self._save_person_local(person_info)
        
        try:
            # Garantir que pelo menos o nome ou relacionamento não é None
            name = person_info.get('name') or 'Desconhecido'
            relationship = person_info.get('relationship')
            
            # Se não temos nome mas temos relacionamento, usar relacionamento como nome
            if name == 'Desconhecido' and relationship:
                name = relationship.title()
            
            query = """
                INSERT INTO people (
                    name, relationship, age, gender, personality_traits, 
                    interests, favorite_foods, favorite_music, favorite_activities,
                    profession, notes, importance_level
                ) VALUES (
                    %(name)s, %(relationship)s, %(age)s, %(gender)s, %(personality_traits)s,
                    %(interests)s, %(favorite_foods)s, %(favorite_music)s, %(favorite_activities)s,
                    %(profession)s, %(notes)s, %(importance_level)s
                )
            """
            
            data = {
                'name': name,
                'relationship': relationship,
                'age': person_info.get('age'),
                'gender': person_info.get('gender'),
                'personality_traits': person_info.get('personality_traits'),
                'interests': person_info.get('interests'),
                'favorite_foods': person_info.get('favorite_foods'),
                'favorite_music': person_info.get('favorite_music'),
                'favorite_activities': person_info.get('favorite_activities'),
                'profession': person_info.get('profession'),
                'notes': person_info.get('source_text'),
                'importance_level': 'média'
            }
            
            self.db_manager.cursor.execute(query, data)
            person_id = self.db_manager.cursor.lastrowid
            
            logger.info(f"✅ Nova pessoa criada: {name} (ID: {person_id})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar pessoa na BD: {e}")
            return self._save_person_local(person_info)
    
    def _update_person(self, person_id: int, new_info: Dict) -> bool:
        """Atualiza informações de uma pessoa existente."""
        if not DATABASE_AVAILABLE or not self.db_manager:
            return self._save_person_local(new_info)
        
        try:
            # Construir query dinamicamente baseada nas informações disponíveis
            update_fields = []
            data = {'id': person_id}
            
            for field in ['name', 'relationship', 'age', 'gender', 'personality_traits', 
                         'interests', 'favorite_foods', 'favorite_music', 'favorite_activities', 'profession']:
                if new_info.get(field):
                    update_fields.append(f"{field} = %({field})s")
                    data[field] = new_info[field]
            
            if update_fields:
                query = f"UPDATE people SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = %(id)s"
                self.db_manager.cursor.execute(query, data)
                
                logger.info(f"✅ Pessoa atualizada: ID {person_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao atualizar pessoa na BD: {e}")
            return False
    
    def _save_person_local(self, person_info: Dict) -> bool:
        """Fallback para guardar pessoas localmente."""
        try:
            people_file = CONFIG["facts_file"].parent / "people.json"
            
            # Carregar pessoas existentes
            people = {}
            if people_file.exists():
                with open(people_file, 'r', encoding='utf-8') as f:
                    people = json.load(f)
            
            # Adicionar nova pessoa
            key = person_info.get('name') or person_info.get('relationship') or f"person_{len(people)+1}"
            people[key] = {
                **person_info,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Guardar
            with open(people_file, 'w', encoding='utf-8') as f:
                json.dump(people, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Pessoa guardada localmente: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao guardar pessoa localmente: {e}")
            return False
    
    def get_person_by_name(self, name: str) -> Optional[Dict]:
        """Obtém pessoa pelo nome."""
        if not DATABASE_AVAILABLE or not self.db_manager:
            return self._get_person_local(name=name)
        
        try:
            query = "SELECT * FROM people WHERE name = %s AND is_active = TRUE"
            self.db_manager.cursor.execute(query, (name,))
            return self.db_manager.cursor.fetchone()
        except Exception as e:
            logger.error(f"Erro ao buscar pessoa por nome: {e}")
            return None
    
    def get_person_by_relationship(self, relationship: str) -> Optional[Dict]:
        """Obtém pessoa pelo relacionamento."""
        if not DATABASE_AVAILABLE or not self.db_manager:
            return self._get_person_local(relationship=relationship)
        
        try:
            query = "SELECT * FROM people WHERE relationship = %s AND is_active = TRUE"
            self.db_manager.cursor.execute(query, (relationship,))
            return self.db_manager.cursor.fetchone()
        except Exception as e:
            logger.error(f"Erro ao buscar pessoa por relacionamento: {e}")
            return None
    
    def _get_person_local(self, name: str = None, relationship: str = None) -> Optional[Dict]:
        """Obtém pessoa do armazenamento local."""
        try:
            people_file = CONFIG["facts_file"].parent / "people.json"
            if not people_file.exists():
                return None
            
            with open(people_file, 'r', encoding='utf-8') as f:
                people = json.load(f)
            
            for key, person in people.items():
                if name and person.get('name') and person.get('name').lower() == name.lower():
                    return person
                if relationship and person.get('relationship') and person.get('relationship').lower() == relationship.lower():
                    return person
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar pessoa localmente: {e}")
            return None
    
    def _handle_people_questions(self, text: str) -> Optional[str]:
        """Lida com perguntas sobre pessoas."""
        question_patterns = [
            (r'(?:como é|como está|quem é) (?:a|o) ([A-Za-z]+)', 'person_info'),
            (r'(?:o que|que) (?:gosta|adora) (?:a|o) ([A-Za-z]+)', 'person_likes'),
            (r'qual é (?:a profissão|o trabalho) (?:da|do) ([A-Za-z]+)', 'person_profession'),
        ]
        
        for pattern, question_type in question_patterns:
            match = re.search(pattern, text)
            if match:
                person_name = match.group(1)
                person = self.get_person_by_name(person_name)
                
                if person:
                    return self._generate_person_response(person, question_type)
                else:
                    return f"Ainda não conheço informações sobre {person_name}. Podes contar-me algo sobre essa pessoa?"
        
        return None
    
    def _generate_person_response(self, person: Dict, question_type: str) -> str:
        """Gera resposta sobre uma pessoa baseada no tipo de pergunta."""
        name = person.get('name', 'essa pessoa')
        
        if question_type == 'person_info':
            parts = []
            if person.get('relationship'):
                parts.append(f"{name} é {person['relationship']}")
            if person.get('age'):
                parts.append(f"tem {person['age']} anos")
            if person.get('profession'):
                parts.append(f"trabalha como {person['profession']}")
            if person.get('personality_traits'):
                parts.append(f"é {person['personality_traits']}")
            
            if parts:
                return f"Sobre {name}: " + ", ".join(parts) + "."
            else:
                return f"Conheço {name}, mas ainda não tenho muitas informações sobre essa pessoa."
        
        elif question_type == 'person_likes':
            likes = []
            if person.get('interests'):
                likes.append(person['interests'])
            if person.get('favorite_foods'):
                likes.append(f"comer {person['favorite_foods']}")
            if person.get('favorite_music'):
                likes.append(f"ouvir {person['favorite_music']}")
            if person.get('favorite_activities'):
                likes.append(person['favorite_activities'])
            
            if likes:
                return f"{name} gosta de: " + ", ".join(likes) + "."
            else:
                return f"Ainda não sei do que {name} gosta. Podes contar-me?"
        
        elif question_type == 'person_profession':
            if person.get('profession'):
                return f"{name} trabalha como {person['profession']}."
            else:
                return f"Não sei qual é a profissão de {name}."
        
        return f"Tenho algumas informações sobre {name}, mas preciso de mais detalhes para responder a essa pergunta."
    
    def get_all_people(self) -> List[Dict]:
        """Obtém todas as pessoas conhecidas."""
        if not DATABASE_AVAILABLE or not self.db_manager:
            return self._get_all_people_local()
        
        try:
            query = "SELECT * FROM people WHERE is_active = TRUE ORDER BY importance_level DESC, name ASC"
            self.db_manager.cursor.execute(query)
            return self.db_manager.cursor.fetchall()
        except Exception as e:
            logger.error(f"Erro ao buscar todas as pessoas: {e}")
            return []
    
    def _get_all_people_local(self) -> List[Dict]:
        """Obtém todas as pessoas do armazenamento local."""
        try:
            people_file = CONFIG["facts_file"].parent / "people.json"
            if not people_file.exists():
                return []
            
            with open(people_file, 'r', encoding='utf-8') as f:
                people_dict = json.load(f)
            
            return list(people_dict.values())
            
        except Exception as e:
            logger.error(f"Erro ao carregar pessoas localmente: {e}")
            return []
    
    def get_context_for_conversation(self, mentioned_names: List[str] = None) -> str:
        """Gera contexto completo sobre pessoas e utilizador para incluir na conversa."""
        try:
            context_parts = []
            
            # 1. CONTEXTO DO UTILIZADOR PRINCIPAL
            user_context = self.user_profile.get_greeting_context()
            if user_context:
                context_parts.append(user_context)
            
            # 2. CONTEXTO DE PESSOAS CONHECIDAS
            people_context_parts = []
            
            if mentioned_names:
                # Informações sobre pessoas específicas mencionadas
                for name in mentioned_names:
                    person = self.get_person_by_name(name)
                    if person:
                        people_context_parts.append(self._format_person_context(person))
            else:
                # Contexto geral sobre pessoas importantes
                important_people = []
                if DATABASE_AVAILABLE and self.db_manager:
                    try:
                        query = "SELECT * FROM people WHERE importance_level IN ('alta', 'muito_alta') AND is_active = TRUE LIMIT 5"
                        self.db_manager.cursor.execute(query)
                        important_people = self.db_manager.cursor.fetchall()
                    except:
                        important_people = []
                
                for person in important_people:
                    people_context_parts.append(self._format_person_context(person))
            
            if people_context_parts:
                context_parts.append("PESSOAS CONHECIDAS:\n" + "\n".join(people_context_parts) + "\n\nUSE estas informações para personalizar respostas quando estas pessoas forem mencionadas.")
            
            return "\n\n".join(context_parts) if context_parts else ""
            
        except Exception as e:
            logger.error(f"Erro ao gerar contexto de pessoas: {e}")
            return ""
    
    def _format_person_context(self, person: Dict) -> str:
        """Formata informações de uma pessoa para contexto."""
        parts = []
        name = person.get('name', 'Pessoa')
        
        if person.get('relationship'):
            parts.append(f"Relação: {person['relationship']}")
        if person.get('age'):
            parts.append(f"Idade: {person['age']} anos")
        if person.get('profession'):
            parts.append(f"Profissão: {person['profession']}")
        if person.get('personality_traits'):
            parts.append(f"Personalidade: {person['personality_traits']}")
        if person.get('interests'):
            parts.append(f"Gostos: {person['interests']}")
        
        context = f"- {name}"
        if parts:
            context += f": {'; '.join(parts)}"
        
        return context


# ==========================
# FUNÇÕES DE TESTE
# ==========================
def test_people_manager():
    """Testa o sistema de gestão de pessoas."""
    print("👥 TESTE DO SISTEMA DE PESSOAS")
    print("=" * 40)
    
    people_manager = PeopleManager()
    
    # Teste 1: Reconhecimento automático
    print("\n📝 Teste 1: Reconhecimento automático")
    text1 = "A minha irmã Maria gosta de comer pizza e ouvir rock"
    result1 = people_manager.process_user_input(text1)
    print(f"Texto: '{text1}'")
    print(f"Resultado: {result1}")
    
    # Teste 2: Pergunta sobre pessoa
    print("\n📝 Teste 2: Pergunta sobre pessoa")
    text2 = "Como é a Maria?"
    result2 = people_manager.process_user_input(text2)
    print(f"Texto: '{text2}'")
    print(f"Resultado: {result2}")
    
    # Teste 3: Listar todas as pessoas
    print("\n📝 Teste 3: Pessoas conhecidas")
    people = people_manager.get_all_people()
    print(f"Total de pessoas: {len(people)}")
    for person in people[:3]:  # Mostrar apenas as primeiras 3
        print(f"- {person}")


if __name__ == "__main__":
    test_people_manager()
