import os
import zipfile
import shutil
import time
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

CHROMA_DIR = "chroma_store"

EXTENSIONS = {
    "Python": [".py"],
    "JavaScript": [".js", ".jsx", ".ts", ".tsx"],
    "Java": [".java"],
    "Markdown": [".md"],
    "Text": [".txt"],
    "All": [".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".md", ".txt", ".json", ".yaml", ".yml", ".xml", ".html", ".css"]
}


def force_delete(path, retries=3, delay=2):
    """Safely delete locked folders like Chroma's SQLite files on Windows."""
    for attempt in range(retries):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
            return
        except PermissionError as e:
            print(f"Attempt {attempt+1}: Chroma is still using the DB. Retrying in {delay}s...")
            time.sleep(delay)
    raise RuntimeError(f"Failed to delete {path} after {retries} retries.")


def unzip_and_index(zip_path, language):
    """Extract zip file and index the codebase in ChromaDB."""
    try:
        if os.path.exists(CHROMA_DIR):
            force_delete(CHROMA_DIR)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("unzipped")

        valid_exts = EXTENSIONS.get(language, EXTENSIONS["All"])
        docs = []
        file_paths = []

        for root, _, files in os.walk("unzipped"):
            for file in files:
                if any(file.endswith(ext) for ext in valid_exts):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            if content.strip():
                                docs.append(content)
                                file_paths.append(file_path)
                    except Exception as e:
                        print(f"Could not read {file_path}: {e}")

        if not docs:
            shutil.rmtree("unzipped")
            return "No supported code files found for indexing."

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )
        
        documents = []
        for i, (content, file_path) in enumerate(zip(docs, file_paths)):
            chunks = splitter.split_text(content)
            for j, chunk in enumerate(chunks):
                documents.append(Document(
                    page_content=chunk,
                    metadata={
                        "source": file_path,
                        "chunk_id": j,
                        "language": language
                    }
                ))

        embedding_fn = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

        vectorstore = Chroma.from_documents(
            documents,
            embedding_fn,
            persist_directory=CHROMA_DIR
        )
        vectorstore.persist()

        shutil.rmtree("unzipped")
        return f"Indexed {len(docs)} files and stored {len(documents)} document chunks."

    except Exception as e:
        if os.path.exists("unzipped"):
            shutil.rmtree("unzipped")
        return f"Error during indexing: {str(e)}"
