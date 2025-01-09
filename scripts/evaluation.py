from nltk import word_tokenize
from nltk.translate.bleu_score import sentence_bleu
from rouge import Rouge
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_rouge(candidate, reference):
    """
    :param candidate:
    :param reference:
    :return:
    """
    rouge = Rouge()
    scores = rouge.get_scores(candidate, reference)
    print(scores)


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


# SBERT
def calculate_sbert(candidate, reference):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings_candidate = model.encode([candidate])
    embeddings_reference = model.encode([reference])
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


