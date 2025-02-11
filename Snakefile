import os
from pathlib import Path
from scripts.API_keys import TDarkRAG_Zotero_API_key, Zotero_library_ID

def sanitize_filename(question):
    sanitized_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in question).strip()
    return sanitized_name + ".md"


keywords = config["keywords"]
question = config["question"]
model = config["model"]
vector_store_type = config["vector_store_type"]
k_chunks = config["k_chunks"]


rule all:
    input:
        f"outputs/{keywords}/{sanitize_filename(question[:50]).removesuffix('.md')}[Eval].md"  # final pipeline file


rule zotero_retrieval:
    input:
        "scripts/zotero_retriever.py"
    params:
        tdarkrag_zotero_api_key=TDarkRAG_Zotero_API_key,
        zotero_library_id=Zotero_library_ID,
        keywords=keywords,
        zotero_storage_dir=Path(r"C:\Users\danie\Zotero\storage"),
        file_extensions=",".join({".pdf", ".html"})
    output:
        directory(f"data/{keywords}/")
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
        input_dir=f"data/{keywords}/",  # Path to the folder containing the documents
        output_dir=f"outputs/{keywords}"  # Path to output folder
    params:
        question=question,  # The question to be answered
        llm_model=model,
        embeddings_model="text-embedding-3-large",
        vector_store_type=vector_store_type,
        k_chunks=k_chunks
    output:
        f"outputs/{keywords}/{sanitize_filename(question[:50])}"
    run:
        command = (
            f'python scripts/RAG.py '
            f'--input_dir {{input.input_dir}} '
            f'--output_dir {{input.output_dir}} '
            f'--question "{params.question}" '
            f'--llm_model "{params.llm_model}" '
            f'--embeddings_model {{params.embeddings_model}} '
            f'--vector_store_type "{params.vector_store_type}" '
            f'--k_chunks {{params.k_chunks}}'
        )
        shell(command)

        assert os.path.exists(output[0]), f"Output file {output[0]} was not created!"


rule evaluation:
    input:
        to_be_evaluated=rules.RAG.output,
        reference_text=f"outputs/{keywords}/{keywords}_RT.md"
    params:
        question = question,
        keyword=keywords,
        k_chunks=k_chunks,
        csv_YN=True
    output:
        f"outputs/{keywords}/{sanitize_filename(question[:50]).removesuffix('.md')}[Eval].md"
    run:
        command = (
         f'python scripts/evaluation.py '
         f'--question "{params.question}" '
         f'--to_be_evaluated "{input.to_be_evaluated}" '
         f'--reference_text "{input.reference_text}" '
         f'--keyword "{params.keyword}" '
         f'--k_chunks "{params.k_chunks}" '
         f'--csv_YN "{params.csv_YN}" '
        )
        shell(command)
