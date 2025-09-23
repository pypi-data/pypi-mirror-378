def contains_sequence(sequence: str):
    return any([ch for ch in sequence if ch.isalpha()])


def contains_non_placeholder_characters(sequence: str):
    return 0 < len(set(sequence) - PLACEHOLDER_CHARACTERS)


def remove_placeholder_characters(sequence: str):
    return "".join(c for c in sequence if c.isalpha())


def is_amino_acid_sequence(sequence: str):
    characters = {c.lower() for c in sequence}
    return characters.issubset(AA_CHARACTERS)


def is_dna_sequence(sequence: str):
    characters = {c.lower() for c in sequence}
    return characters.issubset(DNA_CHARACTERS)


def is_rna_sequence(sequence: str):
    characters = {c.lower() for c in sequence}
    return characters.issubset(RNA_CHARACTERS)


def split_into_subsequences(
    sequence: str, subsequence_length: int, max_num_subsequences: int
):
    """Splits the given sequence into subsequences of the given length.
    The subsequences will be no longer than the given maximum number of subsequences
    and spread evenly over the sequence."""
    sequence_length = len(sequence)
    num_subsquences = min(max_num_subsequences, sequence_length // subsequence_length)

    match num_subsquences:
        case 0:
            # subsequence_length is greater than sequence_length
            return [sequence]
        case 1:
            # there is only one subsequence possible
            return [sequence[:subsequence_length]]

    step_size = max(
        1,
        (sequence_length - subsequence_length) // (num_subsquences - 1),
    )

    subsequences = []
    for i in range(num_subsquences):
        start_idx = i * step_size
        end_idx = min(start_idx + subsequence_length, sequence_length)

        if start_idx >= sequence_length:
            break

        subsequence = sequence[start_idx:end_idx]
        subsequences.append(subsequence)

    return subsequences


PLACEHOLDER_CHARACTERS = {
    "*",
    "?",
    "-",
}
DNA_CHARACTERS = {
    "a",
    "t",
    "c",
    "g",
    "r",
    "y",
    "s",
    "w",
    "k",
    "m",
    "b",
    "d",
    "h",
    "v",
    "n",
} | PLACEHOLDER_CHARACTERS
RNA_CHARACTERS = (DNA_CHARACTERS - {"t"}) | {"u"}
AA_CHARACTERS = {
    "a",
    "r",
    "n",
    "d",
    "c",
    "e",
    "q",
    "g",
    "h",
    "i",
    "l",
    "k",
    "m",
    "f",
    "p",
    "s",
    "t",
    "w",
    "y",
    "v",
    "u",
    "o",
} | PLACEHOLDER_CHARACTERS
