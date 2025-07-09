import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_community.vectorstores import Chroma
from langchain.tools.retriever import create_retriever_tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from jenkins_tool import get_jenkins_tool
from langchain.tools import Tool

load_dotenv()

CHROMA_DIR = "chroma_store"

api_key = os.getenv("OPENAI_API_KEY")
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment!")

llm = ChatOpenAI(
    model_name="deepseek/deepseek-r1:free",
    openai_api_key=api_key,
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.1
)

def run_agent(prompt, job_name):
    try:
        embedding_fn = HuggingFaceEmbeddings(
            model_name ="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )

        if not os.path.exists(CHROMA_DIR):
            return "No indexed codebase found. Please upload and index a codebase first."

        retriever = Chroma(
            embedding_function=embedding_fn,
            persist_directory=CHROMA_DIR
        ).as_retriever(search_kwargs={"k": 5})

        retriever_tool = create_retriever_tool(
            retriever,
            name="codebase_search",
            description="Search the user's uploaded codebase for relevant code, functions, classes, and documentation."
        )

        def universal_input_adapter(input_data):
            if isinstance(input_data, dict):
                for key in ['query', 'input', 'page_content']:
                    if key in input_data and input_data[key]:
                        return {"query": input_data[key]}
                if input_data:
                    return {"query": next(iter(input_data.values()))}
            return {"query": str(input_data)}

        universal_retriever_tool = Tool.from_function(
            func=lambda x: retriever_tool(universal_input_adapter(x)),
            name="codebase_search",
            description="Search the user's uploaded codebase for relevant code, functions, classes, and documentation."
        )

        jenkins_tool = get_jenkins_tool(job_name)

        agent = initialize_agent(
            tools=[universal_retriever_tool, jenkins_tool],
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )

        return agent.run(prompt)

    except Exception as e:
        return f"Error running agent: {str(e)}"
