import re

import rapidfuzz.distance
from rapidfuzz import process


def match(query, reference):
    """Returns whether the query string matches the reference string."""
    tokenized_query = _tokenize(query)
    tokenized_reference = _tokenize(reference)

    scores = []

    for reference_token in tokenized_reference:
        match = process.extractOne(
            reference_token,
            tokenized_query,
            scorer=rapidfuzz.distance.JaroWinkler.normalized_distance,
            score_cutoff=0.25,
        )
        if not match:
            scores.append(1.0)
        else:
            scores.append(match[1])

    return sum(scores) / len(scores)


def _tokenize(word):
    """
    Tokenize a string by splitting on non-alphabetic characters and camelCase boundaries.

    Args:
        word (str): The input string to tokenize

    Returns:
        list: List of tokens (all lowercase)
    """
    # split on non-alphabetic characters
    tokens = re.split(r"[^a-zA-Z]+", word)

    # split each token on camelCase boundaries (lowercase to uppercase)
    final_tokens = []
    for token in tokens:
        # Split on boundaries where a lowercase letter is followed by an uppercase letter
        camel_split = re.split(r"(?<=[a-z])(?=[A-Z])", token)
        final_tokens.extend(camel_split)

    # convert all tokens to lowercase and remove any remaining empty strings
    final_tokens = [token.lower() for token in final_tokens if token]

    return final_tokens
