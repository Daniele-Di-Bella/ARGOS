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
Unfortunately inputs longer that 256 tokens  
"""


def sliding_window_split(text, window_size=256, step_size=128):
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


def calculate_sbert(candidate, reference):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings_candidate = model.encode(candidate)
    embeddings_reference = model.encode(reference)
    similarity = cosine_similarity(embeddings_candidate, embeddings_reference)
    print(f"Cosine similarity SBERT: {similarity[0][0]}")


if __name__ == "__main__":
    candidate_path = r"C:\Users\danie\PycharmProjects\TDarkRAG\outputs\test\What is UGGT_ Which is its function_.md"
    reference_path = r"C:\Users\danie\PycharmProjects\TDarkRAG\outputs\test\reference_text.md"

    with open(candidate_path, 'r', encoding='utf-8') as file:
        candidate = file.read()

    with open(reference_path, 'r', encoding='utf-8') as file:
        reference = file.read()

    calculate_rouge(candidate, reference)
    calculate_sbert(candidate, reference)
