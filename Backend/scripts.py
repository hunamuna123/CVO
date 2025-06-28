"""
Poetry scripts for development tasks.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    print(f"🔧 Running: {command}")
    return subprocess.run(command, shell=True, check=check)


def dev():
    """Start development server with hot reload."""
    print("🚀 Starting development server...")
    run_command("uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")


def start():
    """Start production server."""
    print("🚀 Starting production server...")
    run_command("uvicorn app.main:app --host 0.0.0.0 --port 8000")


def test():
    """Run tests with coverage."""
    print("🧪 Running tests...")
    run_command("pytest")


def lint():
    """Run code linting."""
    print("🔍 Running linting...")
    print("📝 Running flake8...")
    run_command("flake8 app", check=False)
    
    print("🔍 Running mypy...")
    run_command("mypy app", check=False)


def format():
    """Format code with black and isort."""
    print("✨ Formatting code...")
    print("📝 Running isort...")
    run_command("isort app")
    
    print("🖤 Running black...")
    run_command("black app")


def migrate():
    """Run database migrations."""
    print("🗄️ Running database migrations...")
    run_command("alembic upgrade head")


def create_migration():
    """Create a new migration."""
    import sys
    
    if len(sys.argv) < 2:
        print("❌ Usage: poetry run create-migration 'migration message'")
        sys.exit(1)
    
    message = " ".join(sys.argv[1:])
    print(f"📝 Creating migration: {message}")
    run_command(f'alembic revision --autogenerate -m "{message}"')


def seed():
    """Seed database with sample data."""
    print("🌱 Seeding database...")
    run_command("python -m app.scripts.seed_developers")


def install_pre_commit():
    """Install pre-commit hooks."""
    print("🔧 Installing pre-commit hooks...")
    run_command("pre-commit install")


def check_all():
    """Run all checks (format, lint, test)."""
    print("🔍 Running all checks...")
    format()
    lint()
    test()
    print("✅ All checks completed!")


def build():
    """Build the application."""
    print("🏗️ Building application...")
    run_command("poetry build")


def clean():
    """Clean up build artifacts and cache."""
    print("🧹 Cleaning up...")
    
    # Remove Python cache
    run_command("find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true", check=False)
    run_command("find . -name '*.pyc' -delete", check=False)
    
    # Remove coverage files
    run_command("rm -rf .coverage htmlcov .pytest_cache", check=False)
    
    # Remove build artifacts
    run_command("rm -rf dist build *.egg-info", check=False)
    
    print("✅ Cleanup completed!")


def docker_build():
    """Build Docker image."""
    print("🐳 Building Docker image...")
    run_command("docker build -t realestate-api .")


def docker_run():
    """Run application in Docker."""
    print("🐳 Running Docker container...")
    run_command("docker run -p 8000:8000 --env-file .env realestate-api")


def docker_compose_up():
    """Start services with docker-compose."""
    print("🐳 Starting services with docker-compose...")
    run_command("docker-compose up -d")


def docker_compose_down():
    """Stop services with docker-compose."""
    print("🐳 Stopping services with docker-compose...")
    run_command("docker-compose down")


def docker_compose_logs():
    """View docker-compose logs."""
    print("🐳 Viewing docker-compose logs...")
    run_command("docker-compose logs -f")


def init_db():
    """Initialize database (create tables and run migrations)."""
    print("🗄️ Initializing database...")
    migrate()
    seed()
    print("✅ Database initialized!")


def reset_db():
    """Reset database (drop all tables and recreate)."""
    print("⚠️ Resetting database...")
    
    # This would require a reset script or manual database drop
    print("🗄️ Please manually reset your database and run 'poetry run migrate'")


def show_logs():
    """Show application logs."""
    print("📋 Showing application logs...")
    log_file = Path("api.log")
    if log_file.exists():
        run_command("tail -f api.log")
    else:
        print("❌ No log file found. Start the server first.")


def requirements():
    """Export requirements.txt from Poetry."""
    print("📋 Exporting requirements.txt...")
    run_command("poetry export -f requirements.txt --output requirements.txt --without-hashes")


def requirements_dev():
    """Export dev requirements.txt from Poetry."""
    print("📋 Exporting requirements-dev.txt...")
    run_command("poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes")


if __name__ == "__main__":
    # Allow running scripts directly
    if len(sys.argv) > 1:
        script_name = sys.argv[1]
        if script_name in globals():
            globals()[script_name]()
        else:
            print(f"❌ Unknown script: {script_name}")
            print("Available scripts:", [name for name in globals() if not name.startswith('_') and callable(globals()[name])])
    else:
        print("🔧 Available scripts:")
        scripts = [name for name in globals() if not name.startswith('_') and callable(globals()[name]) and name != 'run_command']
        for script in sorted(scripts):
            func = globals()[script]
            doc = func.__doc__ or "No description"
            print(f"  📝 {script}: {doc}")
