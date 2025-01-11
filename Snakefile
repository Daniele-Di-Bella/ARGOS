from pathlib import Path
from scripts.API_keys import TDarkRAG_Zotero_API_key, Zotero_library_ID

def sanitize_filename(question):
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in question) + ".md"


rule all:
    input:
        "data/results.json"  # File finale della pipeline

rule zotero_retrieval:
    input:
        tdarkrag_zotero_api_key=TDarkRAG_Zotero_API_key,
        zotero_library_id=Zotero_library_ID,
        keywords="UGGT",
        zotero_storage_dir=Path(r"C:\Users\danie\Zotero\storage"),
        file_extensions={".pdf", ".html"}
    output:
        Path(r"C:\Users\danie\PycharmProjects\TDarkRAG\data")
    script:
        "scripts/zotero_retriever.py"

rule RAG:
    input:
        input_dir=rules.zotero_retrieval.output,  # Path to the folder containing the documents
        output_dir="outputs",  # Path to output folder
        question="What is UGGT?",  # The question to be answered
        llm_model="gpt-4o-mini",
        embeddings_model="text-embedding-3-large",
        vector_store_type="InMemory"
    output:
        temp("outputs/{sanitized_question}")  # Placeholder for the sanitized question
    run:
        # Sanitize the question to create a valid filename
        sanitized_question = sanitize_filename(input.question)
        output_path = f"outputs/{sanitized_question}"

        # Run the Python command without passing output_path as an argument
        command = (
            f"python scripts/RAG.py "
            f"--input_dir {input.input_dir} "
            f"--output_dir {input.output_dir} "
            f"--question {input.question} "
            f"--llm_model {input.llm_model} "
            f"--embeddings_model {input.embeddings_model} "
            f"--vector_store_type {input.vector_store_type}"
        )
        shell(command)

        # At the end of the rule, specify the output file
        touch(output_path)


rule evaluation:
    input:
        candidate=rules.RAG.output,
        reference="outputs/reference_text.md"
    output:
        candidate=r"C:\Users\danie\PycharmProjects\TDarkRAG\outputs\test\What is UGGT_ Which is its function_.md"
    script:
        "scripts/evaluation.py"
