#!/usr/bin/env python3
"""
Comprehensive setup script for the RAG Jenkins Agent.
This script helps users configure all necessary environment variables and dependencies.
"""

import os
import sys
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a formatted step."""
    print(f"\n{step}. {description}")
    print("-" * 40)

def check_python_version():
    """Check if Python version is compatible."""
    print_step("1", "Checking Python version")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"Python {version.major}.{version.minor} detected")
        print("   This application requires Python 3.8 or higher")
        return False
    
    print(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required Python packages."""
    print_step("2", "Installing Python dependencies")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def setup_openai_api_key():
    """Setup OpenAI API key."""
    print_step("3", "Setting up OpenAI API key")
    
    load_dotenv()
    current_key = os.getenv("OPENAI_API_KEY")
    
    if current_key and current_key != "your_openai_api_key_here":
        print("OpenAI API key already configured")
        return True
    
    print("\nOpenAI API Key Setup")
    print("You need an OpenAI API key to use this application.")
    print("Get your API key from: https://platform.openai.com/account/api-keys")
    print()
    
    api_key = input("Enter your OpenAI API key (starts with 'sk-'): ").strip()
    
    if not api_key:
        print("No API key provided. Setup cancelled.")
        return False
    
    if not api_key.startswith('sk-'):
        print("Invalid API key format. API keys should start with 'sk-'")
        return False
    
    env_path = Path(".env")
    env_content = f"""# OpenAI API Configuration
OPENAI_API_KEY={api_key}

# Jenkins Configuration (optional)
JENKINS_URL=http://localhost:8080
JENKINS_USERNAME=your_jenkins_username
JENKINS_API_TOKEN=your_jenkins_api_token
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"API key saved to {env_path}")
        print("Remember: Never commit this file to version control!")
        return True
    except Exception as e:
        print(f"Error creating .env file: {e}")
        return False

def setup_jenkins_optional():
    """Optional Jenkins setup."""
    print_step("4", "Optional: Jenkins Setup")
    
    print("\nJenkins Integration (Optional)")
    print("Jenkins integration allows the agent to:")
    print("- Create and manage Jenkins jobs")
    print("- Trigger builds and deployments")
    print("- Analyze build logs for errors")
    print("- Monitor deployment status")
    print()
    
    setup_jenkins = input("Do you want to set up Jenkins integration? (y/N): ").lower().strip()
    
    if setup_jenkins != 'y':
        print("Skipping Jenkins setup. You can configure it later.")
        return True
    
    print("\nJenkins Setup Options:")
    print("1. Use Docker (recommended for testing)")
    print("2. Use existing Jenkins instance")
    print("3. Skip for now")
    
    choice = input("\nChoose an option (1-3): ").strip()
    
    if choice == "1":
        return setup_jenkins_docker()
    elif choice == "2":
        return setup_existing_jenkins()
    else:
        print("Skipping Jenkins setup. You can configure it later.")
        return True

def setup_jenkins_docker():
    """Setup Jenkins using Docker."""
    print("\nSetting up Jenkins with Docker...")
    
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("Docker is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Docker is not available")
        print("   Please install Docker first: https://docs.docker.com/get-docker/")
        return False
    
    try:
        print("Starting Jenkins with Docker Compose...")
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        print("Jenkins started successfully")
        print("Please wait 30-60 seconds for Jenkins to fully start")
        print("Then open http://localhost:8080 in your browser")
        print("\nNext steps:")
        print("1. Complete the Jenkins setup wizard")
        print("2. Create an admin user")
        print("3. Install suggested plugins")
        print("4. Create an API token")
        print("5. Update the .env file with your credentials")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to start Jenkins: {e}")
        return False

def setup_existing_jenkins():
    """Setup connection to existing Jenkins instance."""
    print("\nConnecting to existing Jenkins instance...")
    
    jenkins_url = input("Enter Jenkins URL (e.g., http://localhost:8080): ").strip()
    if not jenkins_url:
        print("No URL provided")
        return False
    
    try:
        response = requests.get(f"{jenkins_url}/api/json", timeout=5)
        if response.status_code == 200:
            print("Successfully connected to Jenkins")
        else:
            print(f"Jenkins responded with status code: {response.status_code}")
    except Exception as e:
        print(f"Could not connect to Jenkins: {e}")
        return False
    
    username = input("Enter Jenkins username: ").strip()
    api_token = input("Enter Jenkins API token: ").strip()
    
    if not username or not api_token:
        print("Username and API token are required")
        return False
    
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        updated_lines = []
        jenkins_updated = False
        
        for line in lines:
            if line.startswith('JENKINS_URL='):
                updated_lines.append(f'JENKINS_URL={jenkins_url}')
                jenkins_updated = True
            elif line.startswith('JENKINS_USERNAME='):
                updated_lines.append(f'JENKINS_USERNAME={username}')
                jenkins_updated = True
            elif line.startswith('JENKINS_API_TOKEN='):
                updated_lines.append(f'JENKINS_API_TOKEN={api_token}')
                jenkins_updated = True
            else:
                updated_lines.append(line)
        
        if not jenkins_updated:
            updated_lines.extend([
                f'JENKINS_URL={jenkins_url}',
                f'JENKINS_USERNAME={username}',
                f'JENKINS_API_TOKEN={api_token}'
            ])
        
        with open(env_path, 'w') as f:
            f.write('\n'.join(updated_lines))
    else:
        with open(env_path, 'w') as f:
            f.write(f"""# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Jenkins Configuration
JENKINS_URL={jenkins_url}
JENKINS_USERNAME={username}
JENKINS_API_TOKEN={api_token}
""")
    
    print("Jenkins configuration saved")
    return True

def test_setup():
    """Test the setup by running basic functionality."""
    print_step("5", "Testing setup")
    
    try:
        import streamlit
        import langchain
        import chromadb
        print("All required packages imported successfully")
        
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            print("OpenAI API key configured")
        else:
            print("OpenAI API key not configured")
        
        jenkins_url = os.getenv("JENKINS_URL")
        jenkins_user = os.getenv("JENKINS_USERNAME")
        jenkins_token = os.getenv("JENKINS_API_TOKEN")
        
        if all([jenkins_url, jenkins_user, jenkins_token]):
            print("Jenkins configuration complete")
        else:
            print("Jenkins configuration optional")
        
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False

def main():
    """Main setup function."""
    print_header("RAG Jenkins Agent Setup")
    
    print("This script will help you set up the RAG Jenkins Agent.")
    print("It will configure all necessary dependencies and environment variables.")
    
    if not check_python_version():
        sys.exit(1)
    
    if not install_dependencies():
        sys.exit(1)
    
    if not setup_openai_api_key():
        sys.exit(1)
    
    setup_jenkins_optional()
    
    if test_setup():
        print_header("Setup Complete!")
        print("Your RAG Jenkins Agent is ready to use!")
        print("\nTo start the application, run:")
        print("   streamlit run app.py")
        print("\nFor more information, see the README.md file")
    else:
        print_header("Setup Issues")
        print("Some issues were encountered during setup.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main() 