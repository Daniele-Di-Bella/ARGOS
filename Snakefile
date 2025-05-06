"""
Snakemake workflow for running a Retrieval-Augmented Generation (RAG) pipeline using
Zotero-sourced documents.

This pipeline retrieves documents from a local Zotero library using specified
keywords, generates answers to a user-defined question using a RAG model, and
evaluates the generated answers by comparing them to reference answers.

Steps:
1. Zotero Retrieval:
   Retrieves documents (PDF and HTML) from a local Zotero library based on
   specified keywords. Zotero API credentials from `scripts/API_keys.py` are required.

2. RAG Generation:
   Uses a specified language model (LLM) to generate an answer to the user-defined
   question based on the retrieved documents. The process involves embedding models
   and a vector store for chunk-based retrieval.

3. Evaluation:
   Compares the generated answer to a reference answer using evaluation scripts,
   outputting a markdown file with the results, and optionally a CSV file with
   evaluation metrics.

Configuration:
    The workflow relies on the `config` dictionary, which should define the following keys:
    - `keywords` (str): The search term for document retrieval and folder naming.
    - `question` (str): The natural language question to answer.
    - `model` (str): The LLM used for answer generation.
    - `vector_store_type` (str): The type of vector store used for chunk indexing.
    - `k_chunks` (int): The number of top chunks to retrieve.

Inputs:
    - Zotero library, fetched from a local storage path.
    - API credentials from `scripts/API_keys.py`.
    - Supporting Python scripts: `zotero_retriever.py`, `RAG.py`, `evaluation.py`.

Outputs:
    - Retrieved documents saved in `data/{keywords}/`.
    - Answer markdown file saved in `outputs/{keywords}/`.
    - Evaluation results saved as a markdown and optionally as a CSV file in `outputs/{keywords}/`.

Requirements:
    - Python 3.8+
    - Snakemake
    - Zotero with local storage
    - Access to OpenAI or compatible LLM APIs

Note:
    This workflow is designed for use in a Windows environment (e.g., `C:\\Users\\...` paths).
    For cross-platform compatibility, paths and shell invocations may need adjustment.

Author: Daniele Di Bella (daniele.dibella99@gmail.com)
"""

import os
from pathlib import Path
from scripts.API_keys import TDarkRAG_Zotero_API_key, Zotero_library_ID

def sanitize_filename(question):
    sanitized_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in question).strip()
    return sanitized_name + ".md"

configfile: "config.yaml"

keywords = config["keywords"]
language = config["language"]
target_audience= config["target_audience"]
question = config["question"]
model = config["model"]
vector_store_type = config["vector_store_type"]
k_chunks = config["k_chunks"]


rule all:
    input:
        f"outputs/{keywords}/{sanitize_filename(question[:50]).removesuffix('.md')}.md"  # final pipeline file


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
    params:
        keywords=keywords,
        language=language,
        target_audience=target_audience,
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
            f'--output_dir outputs/"{params.keywords}" '  
            f'--keywords "{params.keywords}" '
            f'--language "{params.language}" '
            f'--target_audience "{params.target_audience}" '
            f'--question "{params.question}" '
            f'--llm_model "{params.llm_model}" '
            f'--embeddings_model "{params.embeddings_model}" '
            f'--vector_store_type "{params.vector_store_type}" '
            f'--k_chunks {{params.k_chunks}}'
        )
        shell(command)

        assert os.path.exists(f"outputs/{params.keywords}"), f"Output file outputs/{params.keywords} was not created!"


rule evaluation:
    input:
        to_be_evaluated=rules.RAG.output,
        reference_text=f"outputs/{keywords}/{keywords}_RT.md"
    params:
        question = question,
        keyword=keywords,
        model=model,
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
         f'--model "{params.model}" '
         f'--k_chunks "{params.k_chunks}" '
         f'--csv_YN "{params.csv_YN}" '
        )
        shell(command)
