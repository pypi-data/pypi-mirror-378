"""Situation features."""

import math

from cohmetrixBR.utils import ModelPool, safe_div

pool = ModelPool()


def _incidence(count: int, size: int, ref: int = 1000) -> float:
    divisor = math.ceil(size / ref)
    return safe_div(count, divisor)


def SMINTEp(text: str):
    doc = pool.nlp(text)
    intentional_verb = 0
    for token in doc:
        if token.lemma_ in pool.intentional_verbs:
            intentional_verb = intentional_verb + 1

    return _incidence(intentional_verb, len(text.split()))


def SMINTEp_sentence(text: str):
    sentences = pool.sent_tokenize(text)
    intentional_verb_sentences = 0

    for s in sentences:
        if SMINTEp(s) > 0:
            intentional_verb_sentences = intentional_verb_sentences + 1

    return intentional_verb_sentences


def SMINTEr(text: str):
    intentional_verb = SMINTEp(text)
    intentional_sentences = SMINTEp_sentence(text)
    return intentional_sentences / (intentional_verb + 1)


def SMCAUSwn(text: str):
    doc = pool.nlp(text)
    verbs = [word.lemma_ for word in doc if word.pos_ == "VERB"]

    if len(verbs) == 0:
        return 0

    synonyms = []
    for verb in verbs:
        for word_set in pool.wordnet:
            if word_set.__contains__(verb):
                synonyms.extend(word_set)

    synonyms = [x.lower() for x in synonyms]
    intersection = len(list(set(synonyms) & set(verbs)))
    return _incidence(intersection, len(text.split()))


FEATURES = [
    SMINTEp,
    SMINTEp_sentence,
    SMINTEr,
    SMCAUSwn,
]
