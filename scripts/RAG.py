import getpass
import os

from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from pathlib import Path

# Find OpenAI API key and set (1) which LLM and (2) encoding model are wanted
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

llm = ChatOpenAI(model="gpt-4o-mini")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Define the vector database to use
vector_store = InMemoryVectorStore(embeddings)

# Load the documents
docs_path = Path(r"C:\Users\danie\PycharmProjects\TDarkRAG\data")
text_loader_kwargs = {"autodetect_encoding": True}
loader = DirectoryLoader(
    str(docs_path),
    glob="**/*.txt",  # which kind of file are desired
    loader_cls=TextLoader,  # loader class
    loader_kwargs=text_loader_kwargs  # asks TextLoader to auto-detect the doc encoding before failing
)
docs = loader.load()  # return a list of the desired documents

file_count = len([f for f in docs_path.iterdir() if f.is_file()])
try:
    len(docs) == file_count
except UnicodeDecodeError as u:
    print(f"{u}: {file_count - len(docs)} have not been loaded, probably because of encoding errors")

