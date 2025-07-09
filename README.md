# RAG Jenkins Agent

A powerful AI agent that processes codebases, indexes them in ChromaDB, and integrates with Jenkins for automated deployment and error detection.

## Features

- Codebase Processing: Upload ZIP files and automatically extract and index code
- Smart Indexing: Multi-language support with intelligent document chunking
- RAG-Powered Search: Context-aware code search using your indexed codebase
- Jenkins Integration: Create, trigger, and monitor Jenkins jobs
- Error Analysis: Automatically detect and analyze build errors
- AI Agent: Natural language interface for code analysis and deployment
- Modern UI: Streamlit interface with real-time feedback

## Quick Start

### 1. Automated Setup (Recommended)

```bash
# Clone or download the project
cd rag-jenkins-agent/venv

# Run the automated setup
python setup.py
```

The setup script will:
- Check Python version compatibility
- Install all required dependencies
- Configure OpenAI API key
- Optionally set up Jenkins integration
- Test the complete setup

### 2. Manual Setup

#### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- (Optional) Jenkins server

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment

Create a `.env` file in the project root:

```env
# Required: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Jenkins Configuration
JENKINS_URL=http://localhost:8080
JENKINS_USERNAME=your_jenkins_username
JENKINS_API_TOKEN=your_jenkins_api_token
```

#### Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Sign in or create an account
3. Create a new API key
4. Copy the generated key to your `.env` file

### 3. Test Your Setup

```bash
python -m tests.test_setup
```

This will verify that all components are working correctly.

### 4. Run the Application

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

## Jenkins Setup (Optional)

### Option A: Docker (Recommended for Testing)

```bash
# Start Jenkins with Docker Compose
docker-compose up -d

# Wait 30-60 seconds, then open http://localhost:8080
# Complete the setup wizard and create an API token
```

### Option B: Existing Jenkins

1. Ensure your Jenkins instance is accessible
2. Create an API token in Jenkins:
   - Go to Manage Jenkins > Manage Users
   - Click on your username > Configure
   - Add new API token
3. Update your `.env` file with the credentials

## Usage

### 1. Upload Your Codebase

- Prepare a ZIP file containing your project
- Upload it through the Streamlit interface
- Select the primary programming language

### 2. Configure Settings

- Choose the programming language for optimal indexing
- Set a Jenkins job name (will be created if needed)

### 3. Write Instructions

Tell the agent what to do, for example:

- Run the tests in the uploaded codebase
- Analyze the code for potential bugs
- Create a Jenkins pipeline for this project
- Deploy the application and check for errors
- Find all functions that handle user authentication

### 4. Run the Agent

- Click "Index Only" to just process your codebase
- Click "Run Full Agent" to index and execute your instructions
- Use "Clear Index" to remove the current codebase

## Supported Languages

- Python: `.py` files
- JavaScript: `.js`, `.jsx`, `.ts`, `.tsx` files
- Java: `.java` files
- Markdown: `.md` files
- Text: `.txt` files
- All: Comprehensive support for multiple file types

## Architecture

### Core Components

- `app.py`: Streamlit web interface
- `code_indexer.py`: ZIP extraction and ChromaDB indexing
- `agent_runner.py`: LangChain agent
- `jenkins_tool.py`: Jenkins integration
- `setup.py`: Automated setup
- `requirements.txt`: Python dependencies
- `docker-compose.yml`: Jenkins Docker setup
- `README.md`: This file
- `tests/`: All test scripts and utilities

## Testing

All test scripts are located in the `tests/` directory. To run the main setup test:

```bash
python -m tests.test_setup
```

You can also run other test scripts in the `tests/` directory as needed.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python -m tests.test_setup`
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Run the test suite: `python -m tests.test_setup`
3. Review the console output for error messages
4. Ensure all prerequisites are met

---

Happy coding! 