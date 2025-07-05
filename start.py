#!/usr/bin/env python3
"""
Receipt OCR App - Startup Script
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_environment():
    """Check if environment is set up correctly"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found. Please copy .env.example to .env and configure it.")
        return False
    
    # Check if Google Cloud credentials are set
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS not set in .env file")
        return False
    
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Receipt OCR App...")
    try:
        os.chdir('src')
        subprocess.run([sys.executable, 'main.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")

def main():
    """Main startup function"""
    print("🧾 Receipt OCR App - Starting up...")
    
    # Check Python version
    check_python_version()
    
    # Check environment
    if not check_environment():
        print("\n📋 Setup steps:")
        print("1. Copy .env.example to .env")
        print("2. Set up Google Cloud Vision API credentials")
        print("3. Update GOOGLE_APPLICATION_CREDENTIALS in .env")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()