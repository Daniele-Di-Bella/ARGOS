from pathlib import Path
from scripts.API_keys import TDarkRAG_Zotero_API_key, Zotero_library_ID

def sanitize_filename(question):
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in question) + ".md"


rule all:
    input:
        "outputs/*/*.md"  # final pipeline file

rule zotero_retrieval:
    input:
        "scripts/zotero_retriever.py"
    params:
        tdarkrag_zotero_api_key=TDarkRAG_Zotero_API_key,
        zotero_library_id=Zotero_library_ID,
        keywords="{keywords}",
        zotero_storage_dir=Path(r"C:\Users\danie\Zotero\storage"),
        file_extensions={".pdf", ".html"}
    output:
        "data/{keywords}/"
    run:
        command = (
            f"python scripts/zotero_retriever.py "
            f"--tdarkrag_zotero_api_key {{params.tdarkrag_zotero_api_key}} "
            f"--zotero_library_id {{params.zotero_library_id}} "
            f"--keywords {{params.keywords}} "
            f"--zotero_storage_dir {{params.zotero_storage_dir}} "
            f"--file_extensions {{params.file_extensions}} "
        )
        shell(command)


rule RAG:
    input:
        input_dir="data/{keywords}/",  # Path to the folder containing the documents
        output_dir="outputs/"  # Path to output folder
    params:
        question="What is UGGT?",  # The question to be answered
        llm_model="gpt-4o-mini",
        embeddings_model="text-embedding-3-large",
        vector_store_type="InMemory"
    output:
        temp("outputs/{sanitized_question}")  # Placeholder for the sanitized question
    run:
        # Sanitize the question to create a valid filename
        sanitized_question = sanitize_filename(params.question)
        output_path = f"outputs/{sanitized_question}"

        # Run the Python command without passing output_path as an argument
        command = (
            f"python scripts/RAG.py "
            f"--input_dir {{input.input_dir}} "
            f"--output_dir {{input.output_dir}} "
            f"--question {{params.question}} "
            f"--llm_model {{params.llm_model}} "
            f"--embeddings_model {{params.embeddings_model}} "
            f"--vector_store_type {{params.vector_store_type}}"
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
