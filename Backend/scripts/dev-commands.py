"""
Development commands and utilities.

This module provides comprehensive development tools and commands
for maintaining a production-ready codebase with enterprise standards.
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Optional
import click


class DevCommands:
    """Development command utilities."""
    
    @staticmethod
    def run_command(cmd: List[str], cwd: Optional[str] = None) -> bool:
        """Run command and return success status."""
        try:
            result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(cmd)}")
            print(f"Error: {e.stderr}")
            return False
    
    @staticmethod
    def check_dependencies() -> bool:
        """Check if all required tools are installed."""
        required_tools = [
            ("poetry", "Poetry package manager"),
            ("docker", "Docker containerization"),
            ("pre-commit", "Pre-commit hooks"),
        ]
        
        all_present = True
        for tool, description in required_tools:
            try:
                subprocess.run([tool, "--version"], check=True, capture_output=True)
                print(f"✅ {description} is installed")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"❌ {description} is missing")
                all_present = False
        
        return all_present


@click.group()
def cli():
    """Development commands for Real Estate API."""
    pass


@cli.command()
def setup():
    """Complete development environment setup."""
    click.echo("🚀 Setting up development environment...")
    
    # Check dependencies
    if not DevCommands.check_dependencies():
        click.echo("❌ Please install missing dependencies first")
        sys.exit(1)
    
    # Install Python dependencies
    click.echo("📦 Installing Python dependencies...")
    if not DevCommands.run_command(["poetry", "install"]):
        sys.exit(1)
    
    # Setup pre-commit hooks
    click.echo("🔧 Setting up pre-commit hooks...")
    if not DevCommands.run_command(["poetry", "run", "pre-commit", "install"]):
        sys.exit(1)
    
    # Initialize database
    click.echo("🗃️ Setting up database...")
    if not DevCommands.run_command(["poetry", "run", "alembic", "upgrade", "head"]):
        sys.exit(1)
    
    click.echo("✅ Development environment setup complete!")


@cli.command()
def test():
    """Run comprehensive test suite."""
    click.echo("🧪 Running comprehensive test suite...")
    
    # Unit tests
    click.echo("🔬 Running unit tests...")
    if not DevCommands.run_command([
        "poetry", "run", "pytest", 
        "tests/unit/", 
        "-v", 
        "--cov=app", 
        "--cov-report=html",
        "--cov-report=term-missing"
    ]):
        sys.exit(1)
    
    # Integration tests
    click.echo("🔗 Running integration tests...")
    if not DevCommands.run_command([
        "poetry", "run", "pytest", 
        "tests/integration/", 
        "-v"
    ]):
        sys.exit(1)
    
    click.echo("✅ All tests passed!")


@cli.command()
def quality():
    """Run code quality checks."""
    click.echo("🔍 Running code quality checks...")
    
    # Black formatting
    click.echo("🎨 Checking code formatting...")
    if not DevCommands.run_command(["poetry", "run", "black", "--check", "app/", "tests/"]):
        click.echo("❌ Code formatting issues found. Run 'poetry run black app/ tests/' to fix.")
        sys.exit(1)
    
    # Import sorting
    click.echo("📋 Checking import sorting...")
    if not DevCommands.run_command(["poetry", "run", "isort", "--check-only", "app/", "tests/"]):
        click.echo("❌ Import sorting issues found. Run 'poetry run isort app/ tests/' to fix.")
        sys.exit(1)
    
    # Linting
    click.echo("🔎 Running linter...")
    if not DevCommands.run_command(["poetry", "run", "flake8", "app/", "tests/"]):
        sys.exit(1)
    
    # Type checking
    click.echo("🎯 Running type checker...")
    if not DevCommands.run_command(["poetry", "run", "mypy", "app/"]):
        sys.exit(1)
    
    click.echo("✅ All quality checks passed!")


@cli.command()
def format():
    """Format code according to standards."""
    click.echo("🎨 Formatting code...")
    
    # Black formatting
    DevCommands.run_command(["poetry", "run", "black", "app/", "tests/"])
    
    # Import sorting
    DevCommands.run_command(["poetry", "run", "isort", "app/", "tests/"])
    
    click.echo("✅ Code formatted successfully!")


@cli.command()
def security():
    """Run security checks."""
    click.echo("🔒 Running security checks...")
    
    # Bandit security scanner
    click.echo("🛡️ Running security scanner...")
    if not DevCommands.run_command(["poetry", "run", "bandit", "-r", "app/"]):
        click.echo("⚠️ Security issues found. Please review and fix.")
        sys.exit(1)
    
    # Safety dependency checker
    click.echo("🔍 Checking dependencies for vulnerabilities...")
    if not DevCommands.run_command(["poetry", "run", "safety", "check"]):
        click.echo("⚠️ Vulnerable dependencies found. Please update.")
        sys.exit(1)
    
    click.echo("✅ No security issues found!")


@cli.command()
def migrate():
    """Run database migrations."""
    click.echo("🗃️ Running database migrations...")
    
    if not DevCommands.run_command(["poetry", "run", "alembic", "upgrade", "head"]):
        sys.exit(1)
    
    click.echo("✅ Database migrations completed!")


@cli.command()
def seed():
    """Seed database with sample data."""
    click.echo("🌱 Seeding database with sample data...")
    
    if not DevCommands.run_command(["poetry", "run", "python", "-m", "app.scripts.seed_developers"]):
        sys.exit(1)
    
    click.echo("✅ Database seeded successfully!")


@cli.command()
def dev():
    """Start development server with hot reload."""
    click.echo("🚀 Starting development server...")
    
    DevCommands.run_command([
        "poetry", "run", "uvicorn", 
        "app.main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ])


@cli.command()
def prod():
    """Start production server."""
    click.echo("🏭 Starting production server...")
    
    DevCommands.run_command([
        "poetry", "run", "gunicorn", 
        "app.main:app", 
        "-w", "4", 
        "-k", "uvicorn.workers.UvicornWorker",
        "--bind", "0.0.0.0:8000"
    ])


@cli.command()
def docker_build():
    """Build Docker image."""
    click.echo("🐳 Building Docker image...")
    
    if not DevCommands.run_command(["docker", "build", "-t", "realestate-api", "."]):
        sys.exit(1)
    
    click.echo("✅ Docker image built successfully!")


@cli.command()
def docker_run():
    """Run application in Docker."""
    click.echo("🐳 Running application in Docker...")
    
    if not DevCommands.run_command([
        "docker", "run", 
        "-p", "8000:8000",
        "--env-file", ".env",
        "realestate-api"
    ]):
        sys.exit(1)


@cli.command()
def infrastructure():
    """Start full infrastructure (databases, monitoring)."""
    click.echo("🏗️ Starting full infrastructure...")
    
    if not DevCommands.run_command([
        "docker-compose", 
        "-f", "docker-compose.full.yml", 
        "up", "-d"
    ]):
        sys.exit(1)
    
    click.echo("✅ Infrastructure started successfully!")
    click.echo("🌐 Access points:")
    click.echo("  - API: http://localhost:8000")
    click.echo("  - Grafana: http://localhost:3000")
    click.echo("  - Prometheus: http://localhost:9090")
    click.echo("  - Kafka UI: http://localhost:8080")


@cli.command()
def check_all():
    """Run all quality checks (format, lint, type, test, security)."""
    click.echo("🔍 Running all quality checks...")
    
    # Format check
    if not DevCommands.run_command(["poetry", "run", "black", "--check", "app/", "tests/"]):
        click.echo("❌ Formatting issues found")
        sys.exit(1)
    
    # Import sorting
    if not DevCommands.run_command(["poetry", "run", "isort", "--check-only", "app/", "tests/"]):
        click.echo("❌ Import sorting issues found")
        sys.exit(1)
    
    # Linting
    if not DevCommands.run_command(["poetry", "run", "flake8", "app/", "tests/"]):
        sys.exit(1)
    
    # Type checking
    if not DevCommands.run_command(["poetry", "run", "mypy", "app/"]):
        sys.exit(1)
    
    # Tests
    if not DevCommands.run_command([
        "poetry", "run", "pytest", 
        "--cov=app", 
        "--cov-fail-under=80"
    ]):
        sys.exit(1)
    
    # Security
    if not DevCommands.run_command(["poetry", "run", "bandit", "-r", "app/"]):
        sys.exit(1)
    
    click.echo("✅ All quality checks passed! Code is production-ready! 🚀")


@cli.command()
def performance():
    """Run performance tests."""
    click.echo("⚡ Running performance tests...")
    
    # Load testing with locust
    if not DevCommands.run_command([
        "poetry", "run", "locust", 
        "-f", "tests/performance/locustfile.py",
        "--headless",
        "--users", "10",
        "--spawn-rate", "2",
        "--run-time", "30s",
        "--host", "http://localhost:8000"
    ]):
        sys.exit(1)
    
    click.echo("✅ Performance tests completed!")


@cli.command()
def docs():
    """Generate and serve documentation."""
    click.echo("📚 Generating documentation...")
    
    # Generate API docs
    if not DevCommands.run_command(["poetry", "run", "python", "-m", "app.scripts.generate_docs"]):
        sys.exit(1)
    
    click.echo("✅ Documentation generated!")
    click.echo("📖 View API docs at: http://localhost:8000/docs")


@cli.command()
def clean():
    """Clean up generated files and caches."""
    click.echo("🧹 Cleaning up...")
    
    # Remove Python cache
    import shutil
    paths_to_clean = [
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "htmlcov",
        "*.pyc",
        "*.pyo",
        "*.egg-info"
    ]
    
    for pattern in paths_to_clean:
        for path in Path(".").rglob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    
    click.echo("✅ Cleanup completed!")


if __name__ == "__main__":
    cli()
