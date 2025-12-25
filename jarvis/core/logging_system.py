"""
Jarvis AI Assistant - Sistema de Logging Avançado

Sistema de logging centralizado com múltiplos handlers, formatadores customizados,
rotação automática e integração com sistemas de monitoramento.
"""

import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import structlog
from pythonjsonlogger import jsonlogger

class JarvisLogger:
    """Sistema de logging avançado para Jarvis AI Assistant."""
    
    def __init__(self, name: str = "jarvis", config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or self._default_config()
        self.logger = self._setup_logger()
        
    def _default_config(self) -> Dict[str, Any]:
        """Configuração padrão do sistema de logging."""
        return {
            "level": "INFO",
            "format": "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "handlers": {
                "console": {
                    "enabled": True,
                    "level": "INFO"
                },
                "file": {
                    "enabled": True,
                    "level": "DEBUG",
                    "filename": "logs/app/jarvis.log",
                    "max_bytes": 10 * 1024 * 1024,  # 10MB
                    "backup_count": 10
                },
                "error_file": {
                    "enabled": True,
                    "level": "ERROR",
                    "filename": "logs/errors/errors.log",
                    "max_bytes": 5 * 1024 * 1024,  # 5MB
                    "backup_count": 5
                },
                "json_file": {
                    "enabled": True,
                    "level": "INFO",
                    "filename": "logs/app/jarvis.json",
                    "max_bytes": 10 * 1024 * 1024,
                    "backup_count": 10
                }
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Configurar o logger principal."""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, self.config["level"]))
        
        # Limpar handlers existentes
        logger.handlers.clear()
        
        # Configurar handlers
        if self.config["handlers"]["console"]["enabled"]:
            logger.addHandler(self._setup_console_handler())
            
        if self.config["handlers"]["file"]["enabled"]:
            logger.addHandler(self._setup_file_handler())
            
        if self.config["handlers"]["error_file"]["enabled"]:
            logger.addHandler(self._setup_error_file_handler())
            
        if self.config["handlers"]["json_file"]["enabled"]:
            logger.addHandler(self._setup_json_file_handler())
        
        return logger
    
    def _setup_console_handler(self) -> logging.StreamHandler:
        """Configurar handler para console com cores."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, self.config["handlers"]["console"]["level"]))
        
        # Formatter com cores
        formatter = ColoredFormatter(
            fmt=self.config["format"],
            datefmt=self.config["date_format"]
        )
        handler.setFormatter(formatter)
        
        return handler
    
    def _setup_file_handler(self) -> logging.handlers.RotatingFileHandler:
        """Configurar handler para arquivo com rotação."""
        file_config = self.config["handlers"]["file"]
        
        # Criar diretório se não existir
        log_file = Path(file_config["filename"])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            filename=file_config["filename"],
            maxBytes=file_config["max_bytes"],
            backupCount=file_config["backup_count"],
            encoding='utf-8'
        )
        handler.setLevel(getattr(logging, file_config["level"]))
        
        formatter = logging.Formatter(
            fmt=self.config["format"],
            datefmt=self.config["date_format"]
        )
        handler.setFormatter(formatter)
        
        return handler
    
    def _setup_error_file_handler(self) -> logging.handlers.RotatingFileHandler:
        """Configurar handler específico para erros."""
        error_config = self.config["handlers"]["error_file"]
        
        # Criar diretório se não existir
        log_file = Path(error_config["filename"])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            filename=error_config["filename"],
            maxBytes=error_config["max_bytes"],
            backupCount=error_config["backup_count"],
            encoding='utf-8'
        )
        handler.setLevel(getattr(logging, error_config["level"]))
        
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
            datefmt=self.config["date_format"]
        )
        handler.setFormatter(formatter)
        
        return handler
    
    def _setup_json_file_handler(self) -> logging.handlers.RotatingFileHandler:
        """Configurar handler para logs em formato JSON."""
        json_config = self.config["handlers"]["json_file"]
        
        # Criar diretório se não existir
        log_file = Path(json_config["filename"])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            filename=json_config["filename"],
            maxBytes=json_config["max_bytes"],
            backupCount=json_config["backup_count"],
            encoding='utf-8'
        )
        handler.setLevel(getattr(logging, json_config["level"]))
        
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt=self.config["date_format"]
        )
        handler.setFormatter(formatter)
        
        return handler
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, extra=kwargs)
    
    def log_user_action(self, action: str, user_id: str, details: Dict[str, Any]):
        """Log ação do usuário."""
        self.info(f"User action: {action}", extra={
            "event_type": "user_action",
            "user_id": user_id,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_ai_interaction(self, interaction_type: str, input_data: str, output_data: str, duration: float):
        """Log interação com IA."""
        self.info(f"AI interaction: {interaction_type}", extra={
            "event_type": "ai_interaction",
            "interaction_type": interaction_type,
            "input_length": len(input_data),
            "output_length": len(output_data),
            "duration_ms": duration * 1000,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str):
        """Log métrica de performance."""
        self.info(f"Performance metric: {metric_name}", extra={
            "event_type": "performance_metric",
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log evento de segurança."""
        self.warning(f"Security event: {event_type}", extra={
            "event_type": "security_event",
            "security_event_type": event_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })


class ColoredFormatter(logging.Formatter):
    """Formatter com cores para terminal."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Aplicar cor apenas ao nível de log
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)


class StructuredLogger:
    """Logger estruturado usando structlog."""
    
    def __init__(self, name: str = "jarvis"):
        self.logger = structlog.get_logger(name)
    
    def bind(self, **kwargs):
        """Bind contexto ao logger."""
        return self.logger.bind(**kwargs)
    
    def debug(self, event: str, **kwargs):
        """Log debug estruturado."""
        self.logger.debug(event, **kwargs)
    
    def info(self, event: str, **kwargs):
        """Log info estruturado."""
        self.logger.info(event, **kwargs)
    
    def warning(self, event: str, **kwargs):
        """Log warning estruturado."""
        self.logger.warning(event, **kwargs)
    
    def error(self, event: str, **kwargs):
        """Log error estruturado."""
        self.logger.error(event, **kwargs)


# Instância global do logger
jarvis_logger = JarvisLogger()

# Funções de conveniência
def debug(message: str, **kwargs):
    jarvis_logger.debug(message, **kwargs)

def info(message: str, **kwargs):
    jarvis_logger.info(message, **kwargs)

def warning(message: str, **kwargs):
    jarvis_logger.warning(message, **kwargs)

def error(message: str, **kwargs):
    jarvis_logger.error(message, **kwargs)

def critical(message: str, **kwargs):
    jarvis_logger.critical(message, **kwargs)