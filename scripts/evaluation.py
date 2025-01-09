from rouge import Rouge
from nltk.translate.bleu_score import sentence_bleu
from nltk import word_tokenize

rouge = Rouge()


def calculate_rouge(candidate, reference):
    """
    candidate, reference: generated and ground-truth sentences
    """
    scores = rouge.get_scores([candidate], reference)
    return scores



def calculate_bleu(candidate, reference):
    '''
    candidate, reference: generated and ground-truth sentences
    '''
    reference = word_tokenize(reference)
    candidate = word_tokenize(candidate)
    score = sentence_bleu(reference, candidate)
    return score

from nltk.translate import meteor

def calculate_meteor(candidate, reference):
  '''
  candidate, reference: tokenized list of words in the sentence
  '''
  reference = word_tokenize(reference)
  candidate = word_tokenize(candidate)
  meteor_score = round(meteor([candidate],reference), 4)
  return meteor_score


import numpy as np
import copy

def get_bleu_score(sentence, remaining_sentences):
    lst = []
    for i in remaining_sentences:
        bleu = sentence_bleu(sentence, i)
        lst.append(bleu)
    return lst


def calculate_selfBleu(sentences):
    """
    The lower the value of the self-bleu score, the higher the diversity in the generated text. Long text
    generation tasks like story generation, news generation, etc. could be a good fit to keep an eye on such
    metrics, helping evaluate the redundancy and monotonicity in the model.
    :param sentences:
    :return:
    """
    bleu_scores = []

    for i in sentences:
        sentences_copy = copy.deepcopy(sentences)
        remaining_sentences = sentences_copy.remove(i)
        print(sentences_copy)
        bleu = get_bleu_score(i,sentences_copy)
        bleu_scores.append(bleu)

    return np.mean(bleu_scores)

calculate_selfBleu(sentences)