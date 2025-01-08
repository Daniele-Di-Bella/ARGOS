import os
from pathlib import Path

from langchain import hub
from langchain_community.document_loaders import PyPDFLoader, UnstructuredHTMLLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict

from API_keys import TDarkRAG_API_key, LANGCHAIN_TRACING_V2, LANGCHAIN_ENDPOINT, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT

# Find OpenAI API key and set (1) which LLM and (2) which encoding model are wanted
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


def load_documents_from_folder(folder_path: str):
    documents = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        elif filename.endswith('.html'):
            loader = UnstructuredHTMLLoader(file_path)
            documents.extend(loader.load())
        else:
            print(f"Unsupported format: {filename}")
    return documents


all_documents = load_documents_from_folder(docs_path)

# Divide the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # chunk size (characters)
    chunk_overlap=200,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)
all_splits = text_splitter.split_documents(all_documents)

print(f"All the documents were successfully split into {len(all_splits)} sub-documents.")

# Embed the chunks and store them in the vector database that was chosen above
document_ids = vector_store.add_documents(documents=all_splits)

# Choose from the hub the prompt to submit to the LLM
prompt = hub.pull("hardkothari/blog-generator")


# Define state for application
class State(TypedDict):
    question: str  # aka, which question(s) will answer our Wikipedia page?
    context: list[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    retriever = vector_store.as_retriever(searh_type="similarity", k=10)
    retrieved_docs = retriever.get_relevant_documents(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(f"source: {doc.metadata['source']}\nchunk: {doc.page_content}" for doc in state["context"])
    message_for_llm = prompt.invoke(
        {
            "text": docs_content,
            "target_audience": "Biologists and people with a degree in medicine."
        }
    )
    response = llm.invoke(message_for_llm)
    # Save the answer to a file
    save_response_to_file(state["question"], response.content)
    return {"answer": response.content}


def save_response_to_file(question: str, answer: str):
    # Create the output folder if it doesn't exist
    output_dir = Path(r"C:\Users\danie\PycharmProjects\TDarkRAG\outputs")
    output_dir.mkdir(exist_ok=True)

    # Replace any invalid characters in the filename
    sanitized_filename = "".join(
        c if c.isalnum() or c in " _-" else "_" for c in question
    ) + ".md"

    # Save the answer as a Markdown file
    file_path = output_dir / sanitized_filename
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"# Question(s) to answer\n{question}\n\n# Wikipedia page\n{answer}")
    print(f"Response saved to {file_path}")


# Compile application and test with LangGraph
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

if __name__ == "__main__":
    # Run the application
    for step in graph.stream(
            {"question": "What is UGGT?"},
            stream_mode="updates"
    ):
        print(f"{step}\n\n----------------\n")
