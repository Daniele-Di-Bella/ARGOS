import argparse
import os
from pathlib import Path
from langchain import hub
from langchain_community.document_loaders import PyPDFLoader, UnstructuredHTMLLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict
from API_keys import TDarkRAG_API_key, LANGCHAIN_TRACING_V2, LANGCHAIN_ENDPOINT, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT

# Set API keys as environment variables
os.environ["OPENAI_API_KEY"] = TDarkRAG_API_key
os.environ["LANGCHAIN_TRACING_V2"] = LANGCHAIN_TRACING_V2
os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT


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


def deduplicate_chunks(chunks):
    seen = set()
    unique_chunks = []
    for chunk in chunks:
        if chunk.page_content not in seen:
            seen.add(chunk.page_content)
            unique_chunks.append(chunk)
    return unique_chunks


def sanitize_filename(question):
    sanitized_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in question).strip()
    return sanitized_name + ".md"


def save_response_to_file(output_dir, question, answer, retrieved_docs: list):
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    sanitized_filename = sanitize_filename(question)
    file_path = output_dir / sanitized_filename

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"# Wikipedia page\n{answer}")

        # Add References section
        file.write("\n\n## References\n")
        file.write(f"Chunks retrieved: {len(retrieved_docs)}\n\n")

        for i, doc in enumerate(retrieved_docs):
            file.write(f"Source of chunk {i + 1}: {doc.metadata['source']}<br>"
                       f"Content: {doc.page_content[:300]} [...] \n\n")  # Get only the first 300 characters to avoid overly long content.

    return str(file_path)


def main(input_dir,
         output_dir,
         question,
         llm_model,
         embeddings_model,
         k_chunks: int,
         vector_store_type="InMemory"
         ):
    # LLM and embedding models to be used
    llm = ChatOpenAI(model=llm_model)
    embeddings = OpenAIEmbeddings(model=embeddings_model)

    # Splitting and loading the docs
    docs_path = Path(input_dir)
    all_documents = load_documents_from_folder(docs_path)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50, add_start_index=True)
    all_splits = text_splitter.split_documents(all_documents)

    # Define the type of the vector store
    if vector_store_type == "InMemory":
        vector_store = InMemoryVectorStore(embeddings)
    elif vector_store_type == "FAISS":
        vector_store = FAISS.from_documents(all_splits, embeddings)
    else:
        raise ValueError(f"Unknown vector store type: {vector_store_type}")

    vector_store.add_documents(documents=all_splits)

    prompt = hub.pull("tdarkrag-wikipedia-page-generation")

    class State(TypedDict):
        question: str
        context: list[Document]
        answer: str

    def retrieve(state: State):
        if vector_store_type == "InMemory":
            retriever = vector_store.as_retriever(searh_type="similarity", search_kwargs={"k": k_chunks})
            retrieved_docs = retriever.invoke(state["question"])

        if vector_store_type == "FAISS":
            retriever = vector_store.as_retriever(search_type="similarity_score_threshold",
                                                  search_kwargs={"score_threshold": 0.0,
                                                                 "k": k_chunks})
            retrieved_docs = retriever.invoke(state["question"])

        retrieved_docs = deduplicate_chunks(retrieved_docs)
        return {"context": retrieved_docs}

    def generate(state: State):
        docs_content = "\n\n".join(
            f"source: {doc.metadata['source']}\nchunk: {doc.page_content}" for doc in state["context"])
        message_for_llm = prompt.invoke(
            {"target_audience": "Biologists and people with a degree in medicine.", "context": docs_content})
        response = llm.invoke(message_for_llm)
        file_path = save_response_to_file(output_dir, state["question"], response.content, state["context"])
        return {"answer": response.content, "output_path": file_path}

    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()

    state = {"question": question}
    output_path = None
    for step in graph.stream(state, stream_mode="updates"):
        print(f"{step}\n\n----------------\n")
        if "output_path" in step:
            output_path = step["output_path"]
            break

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates a Wikipedia page from documents in a folder")
    parser.add_argument("--input_dir", required=True, help="Path to the folder containing documents")
    parser.add_argument("--output_dir", required=True, help="Path to the output folder")
    parser.add_argument("--question", required=True, help="Question that the RAG system has to answer")
    parser.add_argument("--llm_model", default="gpt-4o-mini", help="LLM model to use")
    parser.add_argument("--embeddings_model", default="text-embedding-3-large", help="Embeddings model to use")
    parser.add_argument("--vector_store_type", default="InMemory", help="Type of vector store to use")
    parser.add_argument("--k_chunks", help="How many chunks shall be kept to answer the user's query")

    args = parser.parse_args()

    main(args.input_dir,
         args.output_dir,
         args.question,
         args.llm_model,
         args.embeddings_model,
         int(args.k_chunks),  # if this is not passed as an integer an error will rise: better be sure
         args.vector_store_type
         )
