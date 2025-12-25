#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Sistema de Validação e Geração
Valida configurações usando schemas e gera novos módulos usando templates
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging
import re

# Opcional: usar jsonschema se disponível
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    logging.warning("jsonschema não disponível - validação limitada")

try:
    from .test_config import get_config_manager
except ImportError:
    from test_config import get_config_manager


class ConfigValidator:
    """Validador de configurações usando schemas JSON."""
    
    def __init__(self, schema_file: Optional[Path] = None):
        """
        Inicializa o validador.
        
        Args:
            schema_file: Caminho para arquivo de schema
        """
        self.project_root = Path(__file__).parent.parent
        self.schema_file = schema_file or (
            self.project_root / "config" / "test_settings_schema.json"
        )
        self._logger = logging.getLogger(f"{__name__}.ConfigValidator")
        self._schema: Optional[Dict[str, Any]] = None
    
    def load_schema(self) -> Dict[str, Any]:
        """
        Carrega schema de validação.
        
        Returns:
            Dicionário com o schema
        """
        if self._schema is not None:
            return self._schema
        
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                self._schema = json.load(f)
            self._logger.info(f"Schema carregado de {self.schema_file}")
            return self._schema
            
        except FileNotFoundError:
            self._logger.error(f"Arquivo de schema não encontrado: {self.schema_file}")
            return {}
        except json.JSONDecodeError as e:
            self._logger.error(f"Erro ao decodificar schema JSON: {e}")
            return {}
    
    def validate_config(self, config_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Valida configuração contra o schema.
        
        Args:
            config_data: Dados de configuração a validar
            
        Returns:
            Tuple (válido, lista_de_erros)
        """
        schema = self.load_schema()
        if not schema:
            return False, ["Schema não pôde ser carregado"]
        
        errors = []
        
        if HAS_JSONSCHEMA:
            # Usar jsonschema para validação completa
            try:
                jsonschema.validate(config_data, schema)
                self._logger.info("Configuração validada com sucesso usando jsonschema")
                return True, []
                
            except jsonschema.ValidationError as e:
                error_msg = f"Erro de validação: {e.message}"
                if e.path:
                    error_msg += f" em {'.'.join(str(p) for p in e.path)}"
                errors.append(error_msg)
                
            except jsonschema.SchemaError as e:
                errors.append(f"Schema inválido: {e.message}")
                
        else:
            # Validação básica sem jsonschema
            errors.extend(self._basic_validation(config_data, schema))
        
        return len(errors) == 0, errors
    
    def _basic_validation(self, config: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """
        Validação básica sem biblioteca jsonschema.
        
        Args:
            config: Configuração a validar
            schema: Schema de validação
            
        Returns:
            Lista de erros encontrados
        """
        errors = []
        
        # Verificar campos obrigatórios
        required = schema.get("required", [])
        for field in required:
            if field not in config:
                errors.append(f"Campo obrigatório ausente: {field}")
        
        # Verificar propriedades
        properties = schema.get("properties", {})
        
        for field_name, field_config in config.items():
            if field_name not in properties:
                if not schema.get("additionalProperties", True):
                    errors.append(f"Campo não permitido: {field_name}")
                continue
            
            field_schema = properties[field_name]
            field_errors = self._validate_field(field_config, field_schema, field_name)
            errors.extend(field_errors)
        
        return errors
    
    def _validate_field(self, value: Any, field_schema: Dict[str, Any], field_name: str) -> List[str]:
        """Valida um campo específico."""
        errors = []
        expected_type = field_schema.get("type")
        
        # Mapeamento de tipos JSON para Python
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        if expected_type and expected_type in type_mapping:
            python_type = type_mapping[expected_type]
            
            if not isinstance(value, python_type):
                errors.append(f"Campo {field_name}: tipo inválido. Esperado {expected_type}")
        
        # Validação de enum
        if "enum" in field_schema and value not in field_schema["enum"]:
            errors.append(f"Campo {field_name}: valor não permitido. Valores válidos: {field_schema['enum']}")
        
        # Validação de range para números
        if expected_type in ["integer", "number"]:
            if "minimum" in field_schema and value < field_schema["minimum"]:
                errors.append(f"Campo {field_name}: valor muito baixo (mínimo: {field_schema['minimum']})")
            
            if "maximum" in field_schema and value > field_schema["maximum"]:
                errors.append(f"Campo {field_name}: valor muito alto (máximo: {field_schema['maximum']})")
        
        # Validação de comprimento para strings
        if expected_type == "string":
            if "minLength" in field_schema and len(value) < field_schema["minLength"]:
                errors.append(f"Campo {field_name}: muito curto (mínimo: {field_schema['minLength']})")
            
            if "maxLength" in field_schema and len(value) > field_schema["maxLength"]:
                errors.append(f"Campo {field_name}: muito longo (máximo: {field_schema['maxLength']})")
        
        return errors
    
    def validate_current_config(self) -> tuple[bool, List[str]]:
        """
        Valida configuração atual do sistema.
        
        Returns:
            Tuple (válido, lista_de_erros)
        """
        config_manager = get_config_manager()
        current_config = config_manager.load_config()
        
        return self.validate_config(current_config)


class TestModuleGenerator:
    """Gerador de módulos de teste usando templates."""
    
    def __init__(self, template_dir: Optional[Path] = None):
        """
        Inicializa o gerador.
        
        Args:
            template_dir: Diretório com templates
        """
        self.project_root = Path(__file__).parent.parent
        self.template_dir = template_dir or (Path(__file__).parent / "templates")
        self.tests_dir = Path(__file__).parent
        self._logger = logging.getLogger(f"{__name__}.TestModuleGenerator")
    
    def list_available_templates(self) -> List[str]:
        """
        Lista templates disponíveis.
        
        Returns:
            Lista de nomes de templates
        """
        if not self.template_dir.exists():
            return []
        
        templates = []
        for template_file in self.template_dir.glob("*.py"):
            if not template_file.name.startswith("_"):
                templates.append(template_file.stem)
        
        return templates
    
    def generate_test_module(self, module_name: str, module_path: str,
                           template_name: str = "test_module_template",
                           output_file: Optional[Path] = None) -> bool:
        """
        Gera módulo de teste a partir de template.
        
        Args:
            module_name: Nome da classe/módulo a testar
            module_path: Caminho de importação do módulo
            template_name: Nome do template a usar
            output_file: Arquivo de saída (padrão: tests/test_[module_name_lower].py)
            
        Returns:
            True se geração foi bem-sucedida
        """
        template_file = self.template_dir / f"{template_name}.py"
        
        if not template_file.exists():
            self._logger.error(f"Template não encontrado: {template_file}")
            return False
        
        # Definir arquivo de saída
        if output_file is None:
            module_name_lower = re.sub(r'([A-Z])', r'_\1', module_name).lower().lstrip('_')
            output_file = self.tests_dir / f"test_{module_name_lower}.py"
        
        try:
            # Ler template
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Fazer substituições
            replacements = {
                '[ModuleName]': module_name,
                '[module_path]': module_path,
                '[module_name]': module_name_lower
            }
            
            generated_content = template_content
            for placeholder, replacement in replacements.items():
                generated_content = generated_content.replace(placeholder, replacement)
            
            # Escrever arquivo de saída
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(generated_content)
            
            self._logger.info(f"Módulo de teste gerado: {output_file}")
            
            # Atualizar configurações se necessário
            self._update_test_settings(module_name)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Erro ao gerar módulo de teste: {e}")
            return False
    
    def _update_test_settings(self, module_name: str) -> None:
        """
        Atualiza configurações de teste para incluir novo módulo.
        
        Args:
            module_name: Nome do módulo adicionado
        """
        try:
            config_manager = get_config_manager()
            config = config_manager.load_config()
            
            # Adicionar a suites apropriadas
            test_suites = config.get("test_suites", {})
            
            # Adicionar aos testes unitários
            unit_tests = test_suites.get("unit_tests", [])
            test_class_name = f"Test{module_name}"
            
            if test_class_name not in unit_tests:
                unit_tests.append(test_class_name)
                test_suites["unit_tests"] = unit_tests
            
            # Adicionar testes de integração e performance
            integration_class = f"Test{module_name}Integration"
            integration_tests = test_suites.get("integration_tests", [])
            if integration_class not in integration_tests:
                integration_tests.append(integration_class)
                test_suites["integration_tests"] = integration_tests
            
            performance_class = f"Performance{module_name}"
            performance_tests = test_suites.get("performance_tests", [])
            if performance_class not in performance_tests:
                performance_tests.append(performance_class)
                test_suites["performance_tests"] = performance_tests
            
            # Salvar configurações atualizadas
            config["test_suites"] = test_suites
            config_manager.save_config(config)
            
            self._logger.info(f"Configurações atualizadas para incluir {module_name}")
            
        except Exception as e:
            self._logger.warning(f"Não foi possível atualizar configurações: {e}")


class ValidationSystem:
    """Sistema integrado de validação e geração."""
    
    def __init__(self):
        """Inicializa o sistema de validação."""
        self.validator = ConfigValidator()
        self.generator = TestModuleGenerator()
        self._logger = logging.getLogger(f"{__name__}.ValidationSystem")
    
    def run_full_validation(self) -> Dict[str, Any]:
        """
        Executa validação completa do sistema.
        
        Returns:
            Relatório de validação
        """
        report = {
            "config_validation": {"valid": False, "errors": []},
            "templates_available": [],
            "recommendations": []
        }
        
        # Validar configurações
        is_valid, errors = self.validator.validate_current_config()
        report["config_validation"]["valid"] = is_valid
        report["config_validation"]["errors"] = errors
        
        if is_valid:
            self._logger.info("✅ Configurações válidas")
        else:
            self._logger.warning("❌ Configurações inválidas:")
            for error in errors:
                self._logger.warning(f"  - {error}")
        
        # Listar templates disponíveis
        templates = self.generator.list_available_templates()
        report["templates_available"] = templates
        self._logger.info(f"📋 Templates disponíveis: {len(templates)}")
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(is_valid, errors)
        report["recommendations"] = recommendations
        
        return report
    
    def _generate_recommendations(self, config_valid: bool, config_errors: List[str]) -> List[str]:
        """Gera recomendações baseadas na validação."""
        recommendations = []
        
        if not config_valid:
            recommendations.append("Corrigir erros de configuração antes de executar testes")
            
            # Recomendações específicas baseadas nos erros
            for error in config_errors:
                if "obrigatório ausente" in error:
                    recommendations.append(f"Adicionar campo obrigatório mencionado: {error}")
                elif "tipo inválido" in error:
                    recommendations.append("Verificar tipos de dados nas configurações")
                elif "valor não permitido" in error:
                    recommendations.append("Usar valores permitidos conforme documentação")
        
        # Recomendações gerais
        config_manager = get_config_manager()
        config = config_manager.load_config()
        
        if config.get("test_framework", {}).get("logging_level") == "DEBUG":
            recommendations.append("Considerar usar nível de logging INFO para testes de produção")
        
        performance_thresholds = config.get("test_framework", {}).get("performance_thresholds", {})
        if not performance_thresholds:
            recommendations.append("Configurar limites de performance para testes mais robustos")
        
        return recommendations
    
    def create_new_test_module(self, module_name: str, module_path: str) -> bool:
        """
        Cria novo módulo de teste com validação.
        
        Args:
            module_name: Nome do módulo
            module_path: Caminho de importação
            
        Returns:
            True se criação foi bem-sucedida
        """
        # Validar entrada
        if not module_name or not module_path:
            self._logger.error("Nome do módulo e caminho são obrigatórios")
            return False
        
        # Verificar se módulo já existe
        module_name_lower = re.sub(r'([A-Z])', r'_\1', module_name).lower().lstrip('_')
        output_file = Path(__file__).parent / f"test_{module_name_lower}.py"
        
        if output_file.exists():
            self._logger.warning(f"Arquivo já existe: {output_file}")
            response = input("Sobrescrever? (s/N): ")
            if response.lower() != 's':
                return False
        
        # Gerar módulo
        success = self.generator.generate_test_module(module_name, module_path)
        
        if success:
            # Validar configurações após geração
            is_valid, errors = self.validator.validate_current_config()
            if not is_valid:
                self._logger.warning("Configurações inválidas após geração:")
                for error in errors:
                    self._logger.warning(f"  - {error}")
        
        return success


# Função de conveniência para usar o sistema
def validate_test_system() -> Dict[str, Any]:
    """
    Função de conveniência para validar todo o sistema.
    
    Returns:
        Relatório de validação
    """
    system = ValidationSystem()
    return system.run_full_validation()


def create_test_module(module_name: str, module_path: str) -> bool:
    """
    Função de conveniência para criar módulo de teste.
    
    Args:
        module_name: Nome do módulo
        module_path: Caminho de importação
        
    Returns:
        True se criação foi bem-sucedida
    """
    system = ValidationSystem()
    return system.create_new_test_module(module_name, module_path)
