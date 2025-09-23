.PHONY: help lint format typecheck test security cicd clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make lint       - Run Ruff linting"
	@echo "  make format     - Apply Ruff formatting"
	@echo "  make typecheck  - Run mypy type checking"
	@echo "  make test       - Run pytest with coverage"
	@echo "  make security   - Run Bandit security scan"
	@echo "  make cicd       - Run full CI/CD pipeline"
	@echo "  make clean      - Clean cache directories"

# Linting
lint:
	uv run ruff check src/ tests/

# Formatting
format:
	uv run ruff format src/ tests/

# Type checking
typecheck:
	uv run mypy src/
	uv run mypy tests/

# Testing
test:
	uv run pytest tests/ --cov=celeste --cov-report=term-missing --cov-fail-under=90

# Security scanning
security:
	uv run bandit -r src/ -f screen

# Full CI/CD pipeline - what GitHub Actions will run
cicd:
	@echo "🔍 Running Full CI/CD Pipeline..."
	@echo "================================="
	@echo "1️⃣  Ruff Linting..."
	@uv run ruff check src/ tests/ || (echo "❌ Linting failed" && exit 1)
	@echo "✅ Linting passed"
	@echo ""
	@echo "2️⃣  Ruff Format Check..."
	@uv run ruff format --check src/ tests/ || (echo "❌ Format check failed. Run 'make format' to fix." && exit 1)
	@echo "✅ Format check passed"
	@echo ""
	@echo "3️⃣  MyPy Type Checking..."
	@uv run mypy src/ || (echo "❌ Type checking failed (src)" && exit 1)
	@uv run mypy tests/ || (echo "❌ Type checking failed (tests)" && exit 1)
	@echo "✅ Type checking passed"
	@echo ""
	@echo "4️⃣  Bandit Security Scan..."
	@uv run bandit -r src/ -q || (echo "❌ Security scan failed" && exit 1)
	@echo "✅ Security scan passed"
	@echo ""
	@echo "5️⃣  Running Tests with Coverage..."
	@uv run pytest tests/ --cov=celeste --cov-report=term --cov-fail-under=90 -q || (echo "❌ Tests failed" && exit 1)
	@echo ""
	@echo "================================="
	@echo "🎉 All CI/CD checks passed! Ready to commit."

# Clean cache directories
clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
