import os
import streamlit as st
from code_indexer import unzip_and_index
import tempfile
import shutil
from dotenv import load_dotenv

load_dotenv()


st.set_page_config(
    page_title="RAG Jenkins Agent",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


st.markdown('<h1 class="main-header">RAG Jenkins Agent</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Configuration")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY not set")
        st.info("Please set your OpenAI API key in the environment or .env file")
    else:
        st.success("OpenAI API key configured")
    
    jenkins_url = os.getenv("JENKINS_URL", "http://localhost:8080")
    jenkins_user = os.getenv("JENKINS_USERNAME")
    jenkins_token = os.getenv("JENKINS_API_TOKEN")
    
    st.subheader("Jenkins Settings")
    st.text(f"URL: {jenkins_url}")
    if jenkins_user and jenkins_token:
        st.success("Jenkins credentials configured")
    else:
        st.warning("Jenkins credentials not set")
        st.info("Set JENKINS_USERNAME and JENKINS_API_TOKEN for Jenkins integration")

if 'index_created' not in st.session_state:
    st.session_state['index_created'] = False

col1, col2 = st.columns([2, 1])

with col1:
    st.header("Upload Codebase")
    
    uploaded_file = st.file_uploader(
        "Choose a ZIP file containing your codebase",
        type=["zip"],
        help="Upload a ZIP file containing your project files"
    )
    
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
        st.info(f"File size: {uploaded_file.size / 1024:.1f} KB")

with col2:
    st.header("Settings")
    
    language = st.selectbox(
        "Programming Language",
        ["All", "Python", "JavaScript", "Java", "Markdown", "Text"],
        help="Select the primary language of your codebase"
    )
    
    job_name = st.text_input(
        "Jenkins Job Name",
        value="rag-agent-job",
        help="Name of the Jenkins job (will be created if it doesn't exist)"
    )

st.header("Agent Instructions")
prompt = st.text_area(
    "What should the agent do?",
    placeholder="Examples:\n• Run the tests in the uploaded codebase\n• Analyze the code for potential bugs\n• Create a Jenkins pipeline for this project\n• Deploy the application and check for errors",
    height=100,
    help="Describe what you want the agent to accomplish"
)

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    index_only = st.button("Index Only", help="Only index the codebase without running the agent")

with col2:
    run_agent_btn = st.button("Run Full Agent", help="Index the codebase and run the agent", disabled=not st.session_state['index_created'])

with col3:
    if st.button("Clear Index", help="Clear the current codebase index"):
        if os.path.exists("chroma_store"):
            shutil.rmtree("chroma_store")
            st.success("Index cleared successfully")
            st.session_state['index_created'] = False
        else:
            st.info("No index to clear")

if uploaded_file and index_only:
    if not api_key:
        st.error("OpenAI API key is required. Please set the OPENAI_API_KEY environment variable.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_zip_path = tmp_file.name
        try:
            with st.spinner("Indexing codebase..."):
                status = unzip_and_index(temp_zip_path, language)
            if status.startswith("Indexed"):
                st.success(status)
                st.session_state['index_created'] = True
                if "chroma_store" in os.listdir("."):
                    st.info("Index created successfully")
            else:
                st.error(status)
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
        finally:
            if os.path.exists(temp_zip_path):
                os.unlink(temp_zip_path)

if uploaded_file and run_agent_btn:
    if not api_key:
        st.error("OpenAI API key is required. Please set the OPENAI_API_KEY environment variable.")
    elif not st.session_state['index_created']:
        st.warning("Please index the codebase first by pressing 'Index Only'.")
    elif not prompt:
        st.warning("Please enter a prompt for the agent")
    else:
        with st.spinner("Running agent..."):
            try:
                from agent_runner import run_agent
                response = run_agent(prompt, job_name)
                st.subheader("Agent Response:")
                st.markdown(response)
                st.download_button(
                    label="Download Response",
                    data=response,
                    file_name="agent_response.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"Error running agent: {str(e)}")
                st.info("Try checking your OpenAI API key and network connection")

elif (index_only or run_agent_btn) and not uploaded_file:
    st.warning("Please upload a ZIP file first")

elif run_agent_btn and not prompt:
    st.warning("Please enter a prompt for the agent")

st.markdown("---")
st.markdown("""
### How to Use

1. **Upload Codebase**: Upload a ZIP file containing your project files
2. **Configure Settings**: Select the programming language and Jenkins job name
3. **Write Instructions**: Describe what you want the agent to do
4. **Run Agent**: Click "Run Full Agent" to index and process your codebase

### Features

- **Multi-language Support**: Python, JavaScript, Java, Markdown, and more
- **Smart Indexing**: Automatically extracts and indexes relevant code files
- **Jenkins Integration**: Create, trigger, and monitor Jenkins jobs
- **Error Analysis**: Automatically detect and analyze build errors
- **RAG-powered**: Uses your codebase context for intelligent responses

### Quick Start

1. Set your OpenAI API key: `export OPENAI_API_KEY="your_key_here"`
2. (Optional) Set Jenkins credentials for deployment features
3. Upload your codebase ZIP file
4. Ask the agent to analyze, test, or deploy your code
""")
