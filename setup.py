#!/usr/bin/env python3
"""
Setup script for Tax Lien Search Application
"""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

def create_virtual_environment():
    """Create Python virtual environment"""
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("✓ Virtual environment created")

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    
    # Determine the correct pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = "venv/Scripts/pip"
    else:  # Unix/Linux/Mac
        pip_path = "venv/bin/pip"
    
    subprocess.run([pip_path, "install", "-r", "backend/requirements.txt"], check=True)
    print("✓ Dependencies installed")

def create_database():
    """Initialize SQLite database"""
    print("Creating database...")
    
    # Create database directory if it doesn't exist
    db_dir = Path("backend")
    db_dir.mkdir(exist_ok=True)
    
    # Read schema file
    schema_file = Path("database/schema.sql")
    if schema_file.exists():
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Create database and execute schema
        db_path = "backend/tax_liens.db"
        conn = sqlite3.connect(db_path)
        conn.executescript(schema_sql)
        conn.close()
        
        print("✓ Database created and initialized")
    else:
        print("⚠ Schema file not found, skipping database creation")

def create_env_file():
    """Create .env file from template"""
    print("Setting up environment configuration...")
    
    env_template = Path(".env.template")
    env_file = Path(".env")
    
    if env_template.exists() and not env_file.exists():
        # Copy template to .env
        with open(env_template, 'r') as template:
            content = template.read()
        
        with open(env_file, 'w') as env:
            env.write(content)
        
        print("✓ .env file created from template")
        print("📝 Please edit .env file with your actual configuration values")
    elif env_file.exists():
        print("✓ .env file already exists")
    else:
        print("⚠ .env.template not found")

def create_upload_directory():
    """Create uploads directory for file storage"""
    print("Creating upload directory...")
    
    upload_dir = Path("backend/uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (upload_dir / "documents").mkdir(exist_ok=True)
    (upload_dir / "images").mkdir(exist_ok=True)
    
    print("✓ Upload directories created")

def setup_gitignore():
    """Create or update .gitignore"""
    print("Setting up .gitignore...")
    
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Uploads
backend/uploads/*
!backend/uploads/.gitkeep

# Frontend
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.eslintcache

# Production builds
/build
/dist

# Temporary files
*.tmp
*.temp
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content.strip())
    
    print("✓ .gitignore created")

def main():
    """Main setup function"""
    print("🚀 Setting up Tax Lien Search Application")
    print("=" * 50)
    
    try:
        # Check if we're in the right directory
        if not Path("CLAUDE.md").exists():
            print("❌ Please run this script from the project root directory")
            sys.exit(1)
        
        # Setup steps
        create_virtual_environment()
        install_dependencies()
        create_database()
        create_env_file()
        create_upload_directory()
        setup_gitignore()
        
        print("\n" + "=" * 50)
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your configuration")
        print("2. Start the backend server:")
        
        if os.name == 'nt':  # Windows
            print("   venv\\Scripts\\activate")
        else:  # Unix/Linux/Mac
            print("   source venv/bin/activate")
        
        print("   cd backend")
        print("   python main.py")
        print("\n3. The API will be available at http://localhost:8000")
        print("4. API documentation at http://localhost:8000/docs")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()