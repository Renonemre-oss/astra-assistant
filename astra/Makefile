# Jarvis AI Assistant - Makefile
.DEFAULT_GOAL := help
.PHONY: help install clean test lint format build deploy

# Variables
PYTHON := python
PIP := pip
PROJECT_NAME := jarvis
VENV_NAME := .venv
DOCKER_IMAGE := jarvis-ai
DOCKER_TAG := latest

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)Jarvis AI Assistant - Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Install dependencies and setup environment
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

install-dev: ## Install development dependencies
	@echo "$(YELLOW)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements-dev.txt
	pre-commit install
	@echo "$(GREEN)Development environment setup complete!$(NC)"

clean: ## Clean up generated files and caches
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "$(GREEN)Cleanup complete!$(NC)"

test: ## Run all tests
	@echo "$(YELLOW)Running tests...$(NC)"
	$(PYTHON) -m pytest tests/ -v --cov=$(PROJECT_NAME) --cov-report=html --cov-report=term
	@echo "$(GREEN)Tests completed!$(NC)"

test-unit: ## Run unit tests only
	@echo "$(YELLOW)Running unit tests...$(NC)"
	$(PYTHON) -m pytest tests/unit/ -v
	@echo "$(GREEN)Unit tests completed!$(NC)"

test-integration: ## Run integration tests only
	@echo "$(YELLOW)Running integration tests...$(NC)"
	$(PYTHON) -m pytest tests/integration/ -v
	@echo "$(GREEN)Integration tests completed!$(NC)"

lint: ## Run linters and code analysis
	@echo "$(YELLOW)Running linters...$(NC)"
	flake8 $(PROJECT_NAME)/ tests/
	pylint $(PROJECT_NAME)/
	mypy $(PROJECT_NAME)/
	bandit -r $(PROJECT_NAME)/
	@echo "$(GREEN)Linting completed!$(NC)"

format: ## Format code with black and isort
	@echo "$(YELLOW)Formatting code...$(NC)"
	black $(PROJECT_NAME)/ tests/
	isort $(PROJECT_NAME)/ tests/
	@echo "$(GREEN)Code formatting completed!$(NC)"

security-check: ## Run security analysis
	@echo "$(YELLOW)Running security checks...$(NC)"
	safety check
	bandit -r $(PROJECT_NAME)/
	@echo "$(GREEN)Security check completed!$(NC)"

docs: ## Generate documentation
	@echo "$(YELLOW)Generating documentation...$(NC)"
	$(PYTHON) tools/generators/doc_generator.py
	@echo "$(GREEN)Documentation generated!$(NC)"

build: ## Build the application
	@echo "$(YELLOW)Building application...$(NC)"
	$(PYTHON) setup.py build
	@echo "$(GREEN)Build completed!$(NC)"

docker-build: ## Build Docker image
	@echo "$(YELLOW)Building Docker image...$(NC)"
	docker build -f deployment/docker/Dockerfile -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)Docker image built successfully!$(NC)"

docker-run: ## Run Docker container
	@echo "$(YELLOW)Starting Docker container...$(NC)"
	docker-compose -f deployment/docker/docker-compose.yml up -d
	@echo "$(GREEN)Docker container started!$(NC)"

docker-stop: ## Stop Docker container
	@echo "$(YELLOW)Stopping Docker container...$(NC)"
	docker-compose -f deployment/docker/docker-compose.yml down
	@echo "$(GREEN)Docker container stopped!$(NC)"

deploy-dev: ## Deploy to development environment
	@echo "$(YELLOW)Deploying to development...$(NC)"
	./deployment/scripts/deploy.sh development
	@echo "$(GREEN)Deployed to development!$(NC)"

deploy-prod: ## Deploy to production environment
	@echo "$(YELLOW)Deploying to production...$(NC)"
	./deployment/scripts/deploy.sh production
	@echo "$(GREEN)Deployed to production!$(NC)"

backup: ## Create backup of data and configurations
	@echo "$(YELLOW)Creating backup...$(NC)"
	$(PYTHON) tools/backup_manager.py --create
	@echo "$(GREEN)Backup created successfully!$(NC)"

restore: ## Restore from backup
	@echo "$(YELLOW)Restoring from backup...$(NC)"
	$(PYTHON) tools/backup_manager.py --restore
	@echo "$(GREEN)Restore completed!$(NC)"

benchmark: ## Run performance benchmarks
	@echo "$(YELLOW)Running benchmarks...$(NC)"
	$(PYTHON) tools/benchmarks/performance_test.py
	@echo "$(GREEN)Benchmarks completed!$(NC)"

setup-pre-commit: ## Setup pre-commit hooks
	@echo "$(YELLOW)Setting up pre-commit hooks...$(NC)"
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "$(GREEN)Pre-commit hooks installed!$(NC)"

validate: ## Run all validation checks
	@echo "$(YELLOW)Running validation suite...$(NC)"
	make lint
	make test
	make security-check
	@echo "$(GREEN)All validations passed!$(NC)"

start: ## Start Jarvis in development mode
	@echo "$(YELLOW)Starting Jarvis AI Assistant...$(NC)"
	$(PYTHON) main.py --env=development
	@echo "$(GREEN)Jarvis started!$(NC)"

start-prod: ## Start Jarvis in production mode
	@echo "$(YELLOW)Starting Jarvis in production mode...$(NC)"
	$(PYTHON) main.py --env=production
	@echo "$(GREEN)Jarvis started in production mode!$(NC)"

logs: ## Show application logs
	@echo "$(YELLOW)Showing logs...$(NC)"
	tail -f logs/app/jarvis.log

monitor: ## Open monitoring dashboard
	@echo "$(YELLOW)Opening monitoring dashboard...$(NC)"
	open http://localhost:3000  # Grafana dashboard

health-check: ## Check application health
	@echo "$(YELLOW)Checking application health...$(NC)"
	$(PYTHON) scripts/health_check.py
	@echo "$(GREEN)Health check completed!$(NC)"