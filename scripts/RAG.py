import os
from pathlib import Path

from langchain import hub
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

from API_keys import TDarkRAG_API_key, LANGCHAIN_TRACING_V2, LANGCHAIN_ENDPOINT, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT

# Find OpenAI API key and set (1) which LLM and (2) encoding model are wanted
os.environ["OPENAI_API_KEY"] = TDarkRAG_API_key
os.environ["LANGCHAIN_TRACING_V2"] = LANGCHAIN_TRACING_V2
os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT

llm = ChatOpenAI(model="gpt-4o-mini")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Define the vector database to use
vector_store = InMemoryVectorStore(embeddings)

# Load the documents
docs_path = Path(r"C:\Users\danie\PycharmProjects\TDarkRAG\data")
file_count = len([f for f in docs_path.iterdir() if f.is_file()])

loader = DirectoryLoader(
    str(docs_path),
    glob="**/*.pdf",  # which kind of file are desired
    loader_cls=PyPDFLoader,  # loader class
)
try:
    docs = loader.load()  # return a list of the desired documents
except UnicodeDecodeError as u:
    print(f"{file_count - len(docs)} have not been loaded, probably because of: {u}")

# Divide the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # chunk size (characters)
    chunk_overlap=200,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)
all_splits = text_splitter.split_documents(docs)

print(f"All the documents were successfully split into {len(all_splits)} sub-documents.")

# Embed the chunks and store them in the vector database that was chosen above
document_ids = vector_store.add_documents(documents=all_splits)

# Define the prompt to submit to the LLM
prompt = hub.pull("hardkothari/blog-generator")


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    message_for_llm = prompt.invoke(
        {
            "text": docs_content,
            "target_audience": "people that have a degree in medicine or biology"
        }
    )
    response = llm.invoke(message_for_llm)
    return {"answer": response.content}


# Compile application and test with LangGraph
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

if __name__ == "__main__":
    # Run the application
    for step in graph.stream(
            {"question": "Do diatoms benefit from glacier melting?"},
            stream_mode="updates"
    ):
        print(f"{step}\n\n----------------\n")
