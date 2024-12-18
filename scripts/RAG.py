import getpass
import os

from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain import hub
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from langgraph.graph import START, StateGraph

# Find OpenAI API key and set (1) which LLM and (2) encoding model are wanted
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

llm = ChatOpenAI(model="gpt-4o-mini")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Define the vector database to use
vector_store = InMemoryVectorStore(embeddings)

# Load the documents
docs_path = Path(r"C:\Users\danie\PycharmProjects\TDarkRAG\data")
file_count = len([f for f in docs_path.iterdir() if f.is_file()])

text_loader_kwargs = {"autodetect_encoding": True}
loader = DirectoryLoader(
    str(docs_path),
    glob="**/*.txt",  # which kind of file are desired
    loader_cls=TextLoader,  # loader class
    loader_kwargs=text_loader_kwargs  # asks TextLoader to auto-detect the doc encoding before failing
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

# Run the application
for step in graph.stream(
        {"question": "What is the function and the clinical relevance of protein tanc2?"},
        stream_mode="updates"
):
    print(f"{step}\n\n----------------\n")
