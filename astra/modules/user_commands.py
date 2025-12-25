#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Assistente Pessoal
Sistema de Comandos de Utilizador

Comandos especiais para gestão manual de utilizadores múltiplos.
"""

import re
from typing import Dict, Optional, List, Any
from .multi_user_manager import MultiUserManager

class UserCommands:
    """
    Sistema de comandos para gestão de utilizadores.
    Permite mudança manual, listagem, e gestão de utilizadores.
    """
    
    def __init__(self, multi_user_manager: MultiUserManager):
        self.multi_user = multi_user_manager
        
        # Comandos disponíveis
        self.commands = {
            'switch_user': {
                'patterns': [
                    r'mudar para (?:o|a) ([A-Za-záàâãéèêíïóôõöúçñ\s]+)',
                    r'trocar para (?:o|a) ([A-Za-záàâãéèêíïóôõöúçñ\s]+)',
                    r'agora é (?:o|a) ([A-Za-záàâãéèêíïóôõöúçñ\s]+)',
                    r'switch to ([A-Za-záàâãéèêíïóôõöúçñ\s]+)',
                ],
                'description': 'Muda para outro utilizador'
            },
            'list_users': {
                'patterns': [
                    r'listar utilizadores',
                    r'quem são os utilizadores',
                    r'mostrar utilizadores',
                    r'list users',
                    r'show users'
                ],
                'description': 'Lista todos os utilizadores conhecidos'
            },
            'who_am_i': {
                'patterns': [
                    r'quem sou eu',
                    r'qual é o meu nome',
                    r'who am i',
                    r'utilizador atual',
                    r'current user'
                ],
                'description': 'Mostra informações do utilizador atual'
            },
            'create_user': {
                'patterns': [
                    r'criar utilizador ([A-Za-záàâãéèêíïóôõöúçñ\s]+)',
                    r'novo utilizador ([A-Za-záàâãéèêíïóôõöúçñ\s]+)',
                    r'adicionar utilizador ([A-Za-záàâãéèêíïóôõöúçñ\s]+)',
                    r'create user ([A-Za-záàâãéèêíïóôõöúçñ\s]+)'
                ],
                'description': 'Cria um novo utilizador'
            },
            'delete_user': {
                'patterns': [
                    r'apagar utilizador ([A-Za-záàâãéèêíïóôõöúçñ\s]+)',
                    r'remover utilizador ([A-Za-záàâãéèêíïóôõöúçñ\s]+)',
                    r'delete user ([A-Za-záàâãéèêíïóôõöúçñ\s]+)'
                ],
                'description': 'Remove um utilizador'
            },
            'forget_me': {
                'patterns': [
                    r'esquecer-me',
                    r'apagar meus dados',
                    r'forget me',
                    r'delete my data'
                ],
                'description': 'Remove dados do utilizador atual'
            }
        }
    
    def process_command(self, input_text: str) -> Dict[str, Any]:
        """
        Processa comandos de utilizador.
        
        Args:
            input_text: Texto de entrada
            
        Returns:
            Dict com resultado do comando
        """
        result = {
            'is_command': False,
            'command_type': None,
            'success': False,
            'message': '',
            'data': None
        }
        
        # Verificar cada comando
        for command_type, command_info in self.commands.items():
            for pattern in command_info['patterns']:
                match = re.search(pattern, input_text.strip(), re.IGNORECASE)
                if match:
                    result['is_command'] = True
                    result['command_type'] = command_type
                    
                    # Executar comando específico
                    if command_type == 'switch_user':
                        result = self._switch_user_command(match.group(1), result)
                    elif command_type == 'list_users':
                        result = self._list_users_command(result)
                    elif command_type == 'who_am_i':
                        result = self._who_am_i_command(result)
                    elif command_type == 'create_user':
                        result = self._create_user_command(match.group(1), result)
                    elif command_type == 'delete_user':
                        result = self._delete_user_command(match.group(1), result)
                    elif command_type == 'forget_me':
                        result = self._forget_me_command(result)
                    
                    return result
        
        return result
    
    def _switch_user_command(self, user_name: str, result: Dict) -> Dict:
        """Executa comando de mudança de utilizador."""
        user_name = user_name.strip()
        
        if self.multi_user.switch_user(user_name):
            current_user = self.multi_user.get_current_user()
            result['success'] = True
            result['message'] = f"Mudei para o utilizador: {current_user['name']}"
            result['data'] = current_user
        else:
            # Tentar criar utilizador se não existe
            available_users = self.multi_user.get_all_users()
            user_names = [u['name'].lower() for u in available_users]
            
            if user_name.lower() not in user_names:
                # Criar novo utilizador
                new_user_id = self.multi_user._create_new_user({'name': user_name.title()})
                self.multi_user.current_user_id = new_user_id
                
                result['success'] = True
                result['message'] = f"Criei e mudei para novo utilizador: {user_name.title()}"
                result['data'] = self.multi_user.get_current_user()
            else:
                result['success'] = False
                result['message'] = f"Erro ao mudar para utilizador: {user_name}"
        
        return result
    
    def _list_users_command(self, result: Dict) -> Dict:
        """Executa comando de listagem de utilizadores."""
        users = self.multi_user.get_all_users()
        
        if users:
            user_list = []
            for i, user in enumerate(users, 1):
                status = " (ATUAL)" if user['is_current'] else ""
                conv_count = user.get('conversation_count', 0)
                last_seen = user.get('last_seen', 'Nunca')[:10] if user.get('last_seen') else 'Nunca'
                
                user_info = f"{i}. {user['name']}{status}"
                user_info += f" - {conv_count} conversas"
                user_info += f" - Última vez: {last_seen}"
                
                if user.get('profession'):
                    user_info += f" - {user['profession']}"
                
                user_list.append(user_info)
            
            result['success'] = True
            result['message'] = f"Utilizadores conhecidos ({len(users)}):\n" + "\n".join(user_list)
            result['data'] = users
        else:
            result['success'] = True
            result['message'] = "Nenhum utilizador registado ainda."
            result['data'] = []
        
        return result
    
    def _who_am_i_command(self, result: Dict) -> Dict:
        """Executa comando de identificação do utilizador atual."""
        current_user = self.multi_user.get_current_user()
        
        if current_user:
            info_parts = [f"Utilizador atual: {current_user['name']}"]
            
            if current_user.get('profession'):
                info_parts.append(f"Profissão: {current_user['profession']}")
            
            if current_user.get('location'):
                info_parts.append(f"Localização: {current_user['location']}")
            
            conv_count = current_user.get('conversation_count', 0)
            info_parts.append(f"Conversas realizadas: {conv_count}")
            
            created_at = current_user.get('created_at', '')
            if created_at:
                info_parts.append(f"Registado em: {created_at[:10]}")
            
            relationships = current_user.get('known_relationships', [])
            if relationships:
                info_parts.append(f"Relacionamentos mencionados: {', '.join(relationships[:5])}")
            
            result['success'] = True
            result['message'] = "\n".join(info_parts)
            result['data'] = current_user
        else:
            result['success'] = False
            result['message'] = "Nenhum utilizador está atualmente identificado."
        
        return result
    
    def _create_user_command(self, user_name: str, result: Dict) -> Dict:
        """Executa comando de criação de utilizador."""
        user_name = user_name.strip().title()
        
        # Verificar se já existe
        existing_users = self.multi_user.get_all_users()
        for user in existing_users:
            if user['name'].lower() == user_name.lower():
                result['success'] = False
                result['message'] = f"Utilizador '{user_name}' já existe."
                return result
        
        # Criar novo utilizador
        try:
            new_user_id = self.multi_user._create_new_user({'name': user_name})
            new_user = self.multi_user.users_data[new_user_id]
            
            result['success'] = True
            result['message'] = f"Utilizador '{user_name}' criado com sucesso!"
            result['data'] = new_user
        except Exception as e:
            result['success'] = False
            result['message'] = f"Erro ao criar utilizador: {e}"
        
        return result
    
    def _delete_user_command(self, user_name: str, result: Dict) -> Dict:
        """Executa comando de remoção de utilizador."""
        user_name = user_name.strip()
        
        # Procurar utilizador
        target_user = None
        for user_id, user_data in self.multi_user.users_data.items():
            if user_data['name'].lower() == user_name.lower():
                target_user = (user_id, user_data)
                break
        
        if target_user:
            user_id, user_data = target_user
            
            # Não permitir apagar utilizador atual
            if user_id == self.multi_user.current_user_id:
                result['success'] = False
                result['message'] = f"Não posso apagar o utilizador atual. Muda para outro utilizador primeiro."
                return result
            
            if self.multi_user.delete_user(user_id):
                result['success'] = True
                result['message'] = f"Utilizador '{user_data['name']}' removido com sucesso."
            else:
                result['success'] = False
                result['message'] = f"Erro ao remover utilizador '{user_name}'."
        else:
            result['success'] = False
            result['message'] = f"Utilizador '{user_name}' não encontrado."
        
        return result
    
    def _forget_me_command(self, result: Dict) -> Dict:
        """Executa comando de esquecimento do utilizador atual."""
        current_user = self.multi_user.get_current_user()
        
        if not current_user:
            result['success'] = False
            result['message'] = "Nenhum utilizador está identificado atualmente."
            return result
        
        user_name = current_user['name']
        user_id = current_user['user_id']
        
        # Verificar se há outros utilizadores
        all_users = self.multi_user.get_all_users()
        if len(all_users) <= 1:
            result['success'] = False
            result['message'] = "Não posso esquecer o único utilizador. Cria outro utilizador primeiro."
            return result
        
        # Remover utilizador atual
        if self.multi_user.delete_user(user_id):
            result['success'] = True
            result['message'] = f"Esqueci todas as informações sobre '{user_name}'. Agora precisas de te identificar novamente."
            
            # Reset para nenhum utilizador atual
            self.multi_user.current_user_id = None
        else:
            result['success'] = False
            result['message'] = f"Erro ao esquecer dados do utilizador."
        
        return result
    
    def get_help_text(self) -> str:
        """Retorna texto de ajuda sobre comandos disponíveis."""
        help_lines = ["COMANDOS DE UTILIZADOR DISPONÍVEIS:"]
        
        for command_type, command_info in self.commands.items():
            help_lines.append(f"\n• {command_info['description']}:")
            for pattern in command_info['patterns'][:2]:  # Mostrar apenas 2 padrões
                # Remover regex e mostrar exemplo mais legível
                example = pattern.replace('([A-Za-záàâãéèêíïóôõöúçñ\\s]+)', '[NOME]')
                example = example.replace('(?:o|a) ', '')
                example = example.replace('(?:', '').replace(')', '')
                help_lines.append(f"  - {example}")
        
        help_lines.append("\nExemplos:")
        help_lines.append("• 'Mudar para Maria' - Muda para utilizador Maria")
        help_lines.append("• 'Listar utilizadores' - Mostra todos os utilizadores")
        help_lines.append("• 'Quem sou eu' - Mostra informações do utilizador atual")
        
        return "\n".join(help_lines)