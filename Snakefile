rule all:
    input:
        "data/results.json"  # File finale della pipeline

rule fetch_papers:
    output:
        "data/raw_papers.json"
    script:
        "scripts/01_fetch_papers.py"

rule evaluate_papers:
    input:
        "data/raw_papers.json"
    output:
        "data/evaluated.json"
    script:
        "scripts/02_evaluate_papers.py"

rule apply_model:
    input:
        "data/evaluated.json"
    output:
        "data/results.json"
    script:
        "scripts/03_apply_model.py"
