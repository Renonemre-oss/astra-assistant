#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Sistema de Tratamento de Erros e Validações
Sistema robusto para captura, tratamento e recuperação de erros

Este módulo fornece:
- Decoradores para tratamento automático de erros
- Validadores de entrada
- Sistema de recuperação de falhas
- Logging estruturado de erros
- Métricas de confiabilidade
"""

import logging
import traceback
import time
import json
from typing import Any, Callable, Dict, List, Optional, Union, Type, Tuple
from functools import wraps
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import re
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class ErrorLevel(Enum):
    """Níveis de severidade de erro."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Categorias de erro."""
    VALIDATION = "validation"
    NETWORK = "network"
    DATABASE = "database"
    FILE_SYSTEM = "filesystem"
    EXTERNAL_API = "external_api"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    CONFIGURATION = "configuration"

@dataclass
class ErrorInfo:
    """Informações detalhadas sobre um erro."""
    timestamp: datetime
    error_type: str
    message: str
    level: ErrorLevel
    category: ErrorCategory
    function_name: str
    file_path: str
    line_number: int
    traceback_info: str
    context: Dict[str, Any]
    recovery_attempted: bool = False
    recovery_successful: bool = False
    user_message: Optional[str] = None

class ValidationError(Exception):
    """Erro de validação customizado."""
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message)
        self.field = field
        self.value = value
        self.message = message

class RecoveryStrategy:
    """Estratégia de recuperação de erro."""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff_factor = backoff_factor
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função com estratégia de recuperação."""
        last_exception = None
        current_delay = self.delay
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    logger.warning(f"Tentativa {attempt + 1} falhou: {e}. "
                                 f"Tentando novamente em {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= self.backoff_factor
                else:
                    logger.error(f"Todas as {self.max_retries + 1} tentativas falharam")
        
        raise last_exception

class ErrorHandler:
    """Sistema principal de tratamento de erros."""
    
    def __init__(self, log_file: Optional[Path] = None):
        self.error_history: List[ErrorInfo] = []
        self.error_counts: Dict[str, int] = {}
        self.recovery_strategies: Dict[ErrorCategory, RecoveryStrategy] = {}
        self.log_file = log_file or Path("logs") / "errors.json"
        
        # Configurar estratégias padrão
        self._setup_default_strategies()
        
        # Criar diretório de logs se não existir
        self.log_file.parent.mkdir(exist_ok=True)
    
    def _setup_default_strategies(self):
        """Configura estratégias de recuperação padrão."""
        self.recovery_strategies = {
            ErrorCategory.NETWORK: RecoveryStrategy(max_retries=3, delay=2.0),
            ErrorCategory.DATABASE: RecoveryStrategy(max_retries=2, delay=1.0),
            ErrorCategory.EXTERNAL_API: RecoveryStrategy(max_retries=3, delay=5.0),
            ErrorCategory.FILE_SYSTEM: RecoveryStrategy(max_retries=2, delay=0.5)
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None,
                    level: ErrorLevel = ErrorLevel.MEDIUM,
                    category: ErrorCategory = ErrorCategory.SYSTEM,
                    user_message: Optional[str] = None) -> ErrorInfo:
        """Trata erro e cria registro detalhado."""
        
        # Obter informações do traceback
        tb = traceback.extract_tb(error.__traceback__)
        if tb:
            last_frame = tb[-1]
            file_path = last_frame.filename
            line_number = last_frame.lineno
            function_name = last_frame.name
        else:
            file_path = "unknown"
            line_number = 0
            function_name = "unknown"
        
        # Criar registro de erro
        error_info = ErrorInfo(
            timestamp=datetime.now(),
            error_type=type(error).__name__,
            message=str(error),
            level=level,
            category=category,
            function_name=function_name,
            file_path=file_path,
            line_number=line_number,
            traceback_info=traceback.format_exc(),
            context=context or {},
            user_message=user_message
        )
        
        # Adicionar ao histórico
        self.error_history.append(error_info)
        
        # Contar ocorrência
        error_key = f"{error_info.error_type}:{error_info.function_name}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log do erro
        self._log_error(error_info)
        
        # Salvar em arquivo
        self._save_error_to_file(error_info)
        
        return error_info
    
    def _log_error(self, error_info: ErrorInfo):
        """Faz log estruturado do erro."""
        log_message = (f"[{error_info.level.value.upper()}] {error_info.error_type}: "
                      f"{error_info.message} in {error_info.function_name}() "
                      f"at {error_info.file_path}:{error_info.line_number}")
        
        if error_info.level == ErrorLevel.CRITICAL:
            logger.critical(log_message)
        elif error_info.level == ErrorLevel.HIGH:
            logger.error(log_message)
        elif error_info.level == ErrorLevel.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Log detalhado em debug
        logger.debug(f"Error context: {error_info.context}")
        logger.debug(f"Traceback: {error_info.traceback_info}")
    
    def _save_error_to_file(self, error_info: ErrorInfo):
        """Salva erro em arquivo JSON."""
        try:
            # Converter para dict
            error_dict = asdict(error_info)
            error_dict['timestamp'] = error_info.timestamp.isoformat()
            error_dict['level'] = error_info.level.value
            error_dict['category'] = error_info.category.value
            
            # Ler erros existentes
            errors = []
            if self.log_file.exists():
                try:
                    with open(self.log_file, 'r', encoding='utf-8') as f:
                        errors = json.load(f)
                except:
                    errors = []  # Se não conseguir ler, criar lista vazia
            
            # Adicionar novo erro
            errors.append(error_dict)
            
            # Manter apenas últimos 1000 erros
            if len(errors) > 1000:
                errors = errors[-1000:]
            
            # Salvar
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(errors, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Falha ao salvar erro em arquivo: {e}")
    
    def attempt_recovery(self, func: Callable, category: ErrorCategory,
                        *args, **kwargs) -> Any:
        """Tenta recuperação usando estratégia apropriada."""
        strategy = self.recovery_strategies.get(category)
        if not strategy:
            # Se não há estratégia, executar diretamente
            return func(*args, **kwargs)
        
        return strategy.execute(func, *args, **kwargs)
    
    def get_error_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Retorna estatísticas de erro."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [e for e in self.error_history if e.timestamp >= cutoff_time]
        
        # Contar por categoria
        category_counts = {}
        level_counts = {}
        
        for error in recent_errors:
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            level_counts[error.level.value] = level_counts.get(error.level.value, 0) + 1
        
        return {
            'total_errors': len(recent_errors),
            'by_category': category_counts,
            'by_level': level_counts,
            'most_common': dict(sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'time_period_hours': hours
        }
    
    def clear_old_errors(self, days: int = 7):
        """Remove erros antigos do histórico."""
        cutoff_time = datetime.now() - timedelta(days=days)
        old_count = len(self.error_history)
        self.error_history = [e for e in self.error_history if e.timestamp >= cutoff_time]
        new_count = len(self.error_history)
        logger.info(f"Removidos {old_count - new_count} erros antigos do histórico")

# Instância global
error_handler = ErrorHandler()

class Validators:
    """Classe com validadores comuns."""
    
    @staticmethod
    def not_empty(value: Any, field_name: str = "valor") -> Any:
        """Valida que valor não está vazio."""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError(f"{field_name} não pode estar vazio", field_name, value)
        return value
    
    @staticmethod
    def string_length(value: str, min_len: int = 0, max_len: int = 1000, 
                     field_name: str = "texto") -> str:
        """Valida comprimento de string."""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} deve ser uma string", field_name, value)
        
        if len(value) < min_len:
            raise ValidationError(f"{field_name} deve ter pelo menos {min_len} caracteres", 
                                field_name, value)
        
        if len(value) > max_len:
            raise ValidationError(f"{field_name} deve ter no máximo {max_len} caracteres", 
                                field_name, value)
        
        return value
    
    @staticmethod
    def email(value: str, field_name: str = "email") -> str:
        """Valida formato de email."""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} deve ser uma string", field_name, value)
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise ValidationError(f"{field_name} tem formato inválido", field_name, value)
        
        return value
    
    @staticmethod
    def numeric_range(value: Union[int, float], min_val: float = None, 
                     max_val: float = None, field_name: str = "número") -> Union[int, float]:
        """Valida que número está dentro do intervalo."""
        if not isinstance(value, (int, float)):
            raise ValidationError(f"{field_name} deve ser um número", field_name, value)
        
        if min_val is not None and value < min_val:
            raise ValidationError(f"{field_name} deve ser maior ou igual a {min_val}", 
                                field_name, value)
        
        if max_val is not None and value > max_val:
            raise ValidationError(f"{field_name} deve ser menor ou igual a {max_val}", 
                                field_name, value)
        
        return value
    
    @staticmethod
    def file_exists(path: Union[str, Path], field_name: str = "arquivo") -> Path:
        """Valida que arquivo existe."""
        path_obj = Path(path)
        if not path_obj.exists():
            raise ValidationError(f"{field_name} não existe: {path}", field_name, str(path))
        if not path_obj.is_file():
            raise ValidationError(f"{field_name} não é um arquivo válido: {path}", 
                                field_name, str(path))
        return path_obj
    
    @staticmethod
    def directory_exists(path: Union[str, Path], field_name: str = "diretório") -> Path:
        """Valida que diretório existe."""
        path_obj = Path(path)
        if not path_obj.exists():
            raise ValidationError(f"{field_name} não existe: {path}", field_name, str(path))
        if not path_obj.is_dir():
            raise ValidationError(f"{field_name} não é um diretório válido: {path}", 
                                field_name, str(path))
        return path_obj
    
    @staticmethod
    def choice(value: Any, choices: List[Any], field_name: str = "valor") -> Any:
        """Valida que valor está entre as opções permitidas."""
        if value not in choices:
            raise ValidationError(f"{field_name} deve ser um dos seguintes: {choices}", 
                                field_name, value)
        return value
    
    @staticmethod
    def json_valid(value: str, field_name: str = "JSON") -> dict:
        """Valida que string é JSON válido."""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} deve ser uma string", field_name, value)
        
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            raise ValidationError(f"{field_name} não é JSON válido: {e}", field_name, value)

# Decoradores para tratamento de erro
def handle_errors(level: ErrorLevel = ErrorLevel.MEDIUM,
                 category: ErrorCategory = ErrorCategory.SYSTEM,
                 user_message: Optional[str] = None,
                 recovery_category: Optional[ErrorCategory] = None,
                 raise_on_error: bool = True):
    """
    Decorator para tratamento automático de erros.
    
    Args:
        level: Nível de severidade do erro
        category: Categoria do erro
        user_message: Mensagem amigável para o usuário
        recovery_category: Categoria para estratégia de recuperação
        raise_on_error: Se deve re-lançar o erro após tratamento
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if recovery_category:
                    return error_handler.attempt_recovery(func, recovery_category, *args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                # Criar contexto com informações dos argumentos
                context = {
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys()) if kwargs else []
                }
                
                # Tratar erro
                error_info = error_handler.handle_error(
                    e, context, level, category, user_message
                )
                
                if raise_on_error:
                    raise
                else:
                    logger.warning(f"Erro suprimido em {func.__name__}: {e}")
                    return None
        
        return wrapper
    return decorator

def validate_inputs(**validators_dict):
    """
    Decorator para validação automática de argumentos.
    
    Exemplo:
    @validate_inputs(name=Validators.not_empty, age=lambda x: Validators.numeric_range(x, 0, 150))
    def create_person(name: str, age: int):
        pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obter nomes dos argumentos da função
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validar cada argumento
            for param_name, validator in validators_dict.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    try:
                        # Executar validador
                        if callable(validator):
                            validated_value = validator(value)
                            bound_args.arguments[param_name] = validated_value
                    except ValidationError as e:
                        # Tratar erro de validação
                        context = {'parameter': param_name, 'function': func.__name__}
                        error_handler.handle_error(e, context, ErrorLevel.LOW, 
                                                 ErrorCategory.VALIDATION)
                        raise
            
            # Chamar função com argumentos validados
            return func(*bound_args.args, **bound_args.kwargs)
        
        return wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, 
                    backoff_factor: float = 2.0,
                    exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    """
    Decorator para retry automático em caso de falha.
    
    Args:
        max_retries: Número máximo de tentativas
        delay: Delay inicial entre tentativas
        backoff_factor: Fator de crescimento do delay
        exceptions: Tupla de exceções que devem causar retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            strategy = RecoveryStrategy(max_retries, delay, backoff_factor)
            
            def filtered_func(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    raise  # Re-lançar se for uma exceção que deve causar retry
                except Exception as e:
                    # Para outras exceções, não fazer retry
                    logger.error(f"Erro em {func.__name__} (sem retry): {e}")
                    raise
            
            return strategy.execute(filtered_func, *args, **kwargs)
        
        return wrapper
    return decorator

def log_performance(include_args: bool = False):
    """Decorator para logging de performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                log_msg = f"Função {func.__name__} executada em {duration:.3f}s"
                if include_args:
                    log_msg += f" com {len(args)} args e {len(kwargs)} kwargs"
                
                logger.info(log_msg)
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Função {func.__name__} falhou após {duration:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, default_value=None, **kwargs) -> Any:
    """
    Executa função de forma segura, retornando valor padrão em caso de erro.
    
    Args:
        func: Função a ser executada
        default_value: Valor padrão em caso de erro
        *args, **kwargs: Argumentos para a função
    
    Returns:
        Resultado da função ou valor padrão
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Execução segura falhou em {func.__name__}: {e}")
        return default_value

def main():
    """Função de teste dos sistemas de erro."""
    
    # Testar validadores
    print("Testando validadores...")
    try:
        Validators.not_empty("")
    except ValidationError as e:
        print(f"Validação capturada: {e}")
    
    # Testar decorator de erro
    @handle_errors(level=ErrorLevel.HIGH, category=ErrorCategory.SYSTEM)
    def function_with_error():
        raise ValueError("Erro de teste")
    
    print("\nTestando tratamento de erro...")
    try:
        function_with_error()
    except ValueError:
        print("Erro tratado e re-lançado")
    
    # Testar validação de inputs
    @validate_inputs(name=Validators.not_empty, 
                    age=lambda x: Validators.numeric_range(x, 0, 150))
    def create_person(name: str, age: int):
        return f"Pessoa criada: {name}, {age} anos"
    
    print("\nTestando validação de inputs...")
    try:
        result = create_person("João", 30)
        print(result)
        
        create_person("", 30)  # Deve falhar
    except ValidationError as e:
        print(f"Validação de input falhou: {e}")
    
    # Estatísticas
    print("\nEstatísticas de erro:")
    stats = error_handler.get_error_stats()
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()