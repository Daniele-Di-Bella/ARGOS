import argparse

from nltk import word_tokenize
from nltk.translate.bleu_score import sentence_bleu
from rouge import Rouge
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer


# ROUGE metric
def calculate_rouge(candidate, reference):
    """
    :param candidate:
    :param reference:
    :return:
    """
    rouge = Rouge()
    scores = rouge.get_scores(candidate, reference)
    print(scores)


# BLEU metric
def calculate_bleu(candidate, reference):
    """
    :param candidate:
    :param reference:
    :return:
    """
    reference = word_tokenize(reference)
    candidate = word_tokenize(candidate)
    score = sentence_bleu(reference, candidate)
    print(score)


# SBERT metric
"""
all-MiniLM-L6-v2 is the model that will be used to calculate the SBERT metric over the generated text. 
Unfortunately inputs longer that 256 tokens are truncated, so a sliding window function has to be implemented.  
"""


def sliding_window(text, window_size=256, step_size=128):
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    tokens = tokenizer.tokenize(text)
    chunks = []
    for start in range(0, len(tokens), step_size):
        end = min(start + window_size, len(tokens))
        chunk = tokenizer.convert_tokens_to_string(tokens[start:end])
        chunks.append(chunk)
        if end == len(tokens):
            break
    return chunks


def calculate_sbert(candidate_path, reference_path):
    with open(candidate_path, 'r', encoding='utf-8') as file:
        candidate = file.read()

    with open(reference_path, 'r', encoding='utf-8') as file:
        reference = file.read()

    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    chunks_candidate = sliding_window(candidate)
    chunks_reference = sliding_window(reference)
    embeddings_candidate = model.encode(chunks_candidate, convert_to_tensor=True)
    embeddings_reference = model.encode(chunks_reference, convert_to_tensor=True)

    similarity_matrix = cosine_similarity(embeddings_candidate, embeddings_reference)
    mean_similarity = similarity_matrix.mean()

    with open(candidate_path, 'a', encoding='utf-8') as file:
        file.write(f"\n\n## Evaluation\n\nMean SBERT cosine similarity: {mean_similarity:}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate SBERT similarity between the generated text "
                                                 "and a reference text.")
    parser.add_argument("--candidate", required=True, help="Path to the candidate file")
    parser.add_argument("--reference", required=True, help="Path to the reference file")

    args = parser.parse_args()

    calculate_sbert(args.candidate, args.reference)
