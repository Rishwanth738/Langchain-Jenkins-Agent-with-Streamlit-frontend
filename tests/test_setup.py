#!/usr/bin/env python3
"""
Test script to verify the RAG Jenkins Agent setup.
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import streamlit
        print("streamlit")
    except ImportError as e:
        print(f"streamlit: {e}")
        return False
    
    try:
        import langchain
        print("langchain")
    except ImportError as e:
        print(f"langchain: {e}")
        return False
    
    try:
        import chromadb
        print("chromadb")
    except ImportError as e:
        print(f"chromadb: {e}")
        return False
    
    try:
        import langchain_openai
        print("langchain_openai")
    except ImportError as e:
        print(f"langchain_openai: {e}")
        return False
    
    try:
        import langchain_community
        print("langchain_community")
    except ImportError as e:
        print(f"langchain_community: {e}")
        return False
    
    try:
        import sentence_transformers
        print("sentence_transformers")
    except ImportError as e:
        print(f"sentence_transformers: {e}")
        return False
    
    return True

def test_environment():
    """Test environment variables."""
    print("\nTesting environment variables...")
    
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_openai_api_key_here":
        print("OPENAI_API_KEY configured")
    else:
        print("OPENAI_API_KEY not configured")
        return False
    
    jenkins_url = os.getenv("JENKINS_URL")
    jenkins_user = os.getenv("JENKINS_USERNAME")
    jenkins_token = os.getenv("JENKINS_API_TOKEN")
    
    if all([jenkins_url, jenkins_user, jenkins_token]):
        print("Jenkins credentials configured")
    else:
        print("Jenkins credentials not configured (optional)")
    
    return True

def test_embeddings():
    """Test embedding functionality."""
    print("\nTesting embeddings...")
    
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        
        hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        embedding_fn = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            huggingfacehub_api_token=hf_token
        )
        
        test_texts = ["Hello world", "This is a test"]
        embeddings = embedding_fn.embed_documents(test_texts)
        
        print(f"Embeddings generated successfully")
        print(f"   Dimension: {len(embeddings[0])}")
        print(f"   Number of texts: {len(embeddings)}")
        
        return True
    except Exception as e:
        print(f"Embedding test failed: {e}")
        return False

def test_code_indexer():
    """Test code indexing functionality."""
    print("\nTesting code indexer...")
    
    try:
        from code_indexer import EXTENSIONS, force_delete
        
        print(f"Code indexer imported successfully")
        print(f"   Supported languages: {list(EXTENSIONS.keys())}")
        
        return True
    except Exception as e:
        print(f"Code indexer test failed: {e}")
        return False

def test_agent_runner():
    """Test agent runner functionality."""
    print("\nTesting agent runner...")
    
    try:
        from agent_runner import run_agent
        
        print("Agent runner imported successfully")
        
        print("Agent runner ready (API test skipped)")
        
        return True
    except Exception as e:
        print(f"Agent runner test failed: {e}")
        return False

def test_jenkins_tool():
    """Test Jenkins tool functionality."""
    print("\nTesting Jenkins tool...")
    
    try:
        from jenkins_tool import get_jenkins_tool, check_jenkins_connection
        
        print("Jenkins tool imported successfully")
        
        connection_status = check_jenkins_connection()
        if connection_status:
            print("Jenkins connection test passed")
        else:
            print("Jenkins not accessible (optional)")
        
        return True
    except Exception as e:
        print(f"Jenkins tool test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("RAG Jenkins Agent - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("Embeddings", test_embeddings),
        ("Code Indexer", test_code_indexer),
        ("Agent Runner", test_agent_runner),
        ("Jenkins Tool", test_jenkins_tool),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"{test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! Your setup is ready.")
        print("Run 'streamlit run app.py' to start the application.")
    else:
        print("\nSome tests failed. Please check the errors above.")
        print("Run 'python setup.py' to configure missing components.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 