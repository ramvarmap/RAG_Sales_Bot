#!/usr/bin/env python3
"""
Smart Chart RAG System - Setup Script
Automated setup script for new installations
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🤖 Smart Chart RAG System - Setup Script")
    print("=" * 60)
    print()


def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True


def check_requirements():
    """Check if requirements.txt exists"""
    print("\n📋 Checking requirements file...")
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    print("✅ requirements.txt found")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_env_template():
    """Create .env template file"""
    print("\n⚙️ Creating .env template...")

    env_template = """# Google Cloud Configuration
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_APPLICATION_CREDENTIALS=secrets/llama-sa-key.json
ENDPOINT=us-central1-aiplatform.googleapis.com
REGION=us-central1
PROJECT_ID=your-project-id
VERTEX_PROJECT_ID=your-project-id
VERTEX_LOCATION=us-central1
VERTEX_EMBEDDING_MODEL=text-embedding-005

# Oracle Database Configuration
ORACLE_USERNAME=VECTOR_USER
ORACLE_PASSWORD=your-password
ORACLE_HOST=your-host
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=your-service-name

# Application Configuration
BACKEND_URL=http://fastapi-backend:8000

# Chunking Configuration
TARGET_CHUNK_SIZE=1500
MAX_CHUNK_SIZE=2000
OVERLAP_SIZE=200
MIN_CHUNK_SIZE=500
DOCUMENT_SIZE_LIMIT=256000
"""

    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_template)
        print("✅ Created .env template file")
        print("⚠️  Please update .env with your actual credentials")
    else:
        print("✅ .env file already exists")


def check_service_account():
    """Check if service account key exists"""
    print("\n🔑 Checking service account key...")
    key_path = "secrets/llama-sa-key.json"

    if os.path.exists(key_path):
        print("✅ Service account key found")
        return True
    else:
        print("⚠️  Service account key not found")
        print("   Please place your Google service account JSON key at:")
        print(f"   {key_path}")
        return False


def setup_database():
    """Set up database tables"""
    print("\n🗄️ Setting up database tables...")

    try:
        # Import database operations
        from database.operations import create_tables

        # Create tables
        success = create_tables()

        if success:
            print("✅ Database tables created successfully")
            return True
        else:
            print("❌ Failed to create database tables")
            return False

    except ImportError as e:
        print(f"❌ Failed to import database module: {e}")
        print("   Make sure .env file is configured with database credentials")
        return False
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


def run_tests():
    """Run basic tests"""
    print("\n🧪 Running basic tests...")

    # Test if we can import the modules
    try:
        from config.settings import DB_CONFIG

        print("✅ Configuration module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import configuration: {e}")
        return False

    try:
        from database.connection import get_connection

        print("✅ Database module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import database module: {e}")
        return False

    try:
        from services.auth import generate_access_token

        print("✅ Services module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import services module: {e}")
        return False

    return True


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Setup completed! Next steps:")
    print("=" * 60)
    print()
    print("1. 📝 Update .env file with your credentials:")
    print("   - Google Cloud project details")
    print("   - Oracle database connection details")
    print()
    print("2. 🔑 Place your service account key:")
    print("   secrets/llama-sa-key.json")
    print()
    print("3. 🗄️ Ensure Oracle 23c AI database is running")
    print()
    print("4. 🧪 Test the setup:")
    print("   python testing/test_models.py")
    print()
    print("5. 🚀 Run the application:")
    print("   # Web interface:")
    print("   streamlit run streamlit_app_modular.py")
    print()
    print("   # Command line:")
    print("   python cli_app_modular.py")
    print()
    print("📖 For detailed instructions, see README.md")
    print("=" * 60)


def main():
    """Main setup function"""
    print_header()

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check requirements
    if not check_requirements():
        print("❌ Setup failed: requirements.txt not found")
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed: Could not install dependencies")
        sys.exit(1)

    # Create .env template
    create_env_template()

    # Check service account
    check_service_account()

    # Run basic tests
    if not run_tests():
        print("❌ Setup failed: Module import tests failed")
        sys.exit(1)

    # Setup database (optional - user can skip if .env not configured)
    print("\n" + "=" * 60)
    print("🗄️ Database Setup")
    print("=" * 60)
    print("Do you want to set up the database tables now?")
    print("(Make sure your .env file is configured with database credentials)")

    try:
        response = input("Setup database tables? (y/n): ").lower().strip()
        if response in ["y", "yes"]:
            if setup_database():
                print("✅ Database setup completed successfully!")
            else:
                print("⚠️  Database setup failed. You can run it manually later.")
        else:
            print("⏭️  Skipping database setup. You can run it manually later.")
    except KeyboardInterrupt:
        print("\n⏭️  Skipping database setup.")

    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
