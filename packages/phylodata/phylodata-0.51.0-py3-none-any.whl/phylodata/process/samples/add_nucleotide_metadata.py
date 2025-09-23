from collections import defaultdict

from loguru import logger

from phylodata.data_types import ClassificationEntry, DataType, Sample
from phylodata.errors import BlastError
from phylodata.process.samples.run_blast import BlastHit, extract_blast_hits, run_blast
from phylodata.process.samples.sample_name_matching import match
from phylodata.process.samples.sequence_utils import (
    contains_non_placeholder_characters,
    remove_placeholder_characters,
    split_into_subsequences,
)
from phylodata.process.samples.taxon_classification import look_up_taxon_classification

MAX_SEQ_LENGTH_CONSIDERED = 5000
MAX_NUM_SUBSEQUENCES_CONSIDERED = 4
NUM_BLAST_HITS_CONSIDERED = 5


def add_nucleotide_metadata(samples: list[Sample]) -> list[Sample]:
    """Tries to add metadata to all samples for which we have nucleotide
    sequences."""
    if not samples:
        return []

    sequences, sample_idx = _collect_nucleotide_sequences(samples)
    batch_ranked_taxon_ids = _fetch_blast_hits(sequences)
    taxon_id_classifications = _fetch_classifications(batch_ranked_taxon_ids)
    _add_classifications_by_voting(
        samples, sample_idx, batch_ranked_taxon_ids, taxon_id_classifications
    )

    return samples


def _collect_nucleotide_sequences(samples: list[Sample]) -> tuple[list[str], list[int]]:
    """Collects all nucleotide sequences from the given samples. If necessary,
    long sequences will split up into smaller subsequences."""
    nucleotide_sequences: list[str] = []
    nucleotide_sequence_idx: list[int] = []

    for sample_idx, sample in enumerate(samples):
        if sample.classification:
            # we already have found a classification for this sample
            continue

        for data in sample.sample_data:
            sequence = remove_placeholder_characters(data.data)

            if data.type not in [
                DataType.RNA,
                DataType.DNA,
            ] or not contains_non_placeholder_characters(sequence):
                continue

            for subsequence in split_into_subsequences(
                sequence,
                MAX_SEQ_LENGTH_CONSIDERED,
                MAX_NUM_SUBSEQUENCES_CONSIDERED,
            ):
                nucleotide_sequences.append(subsequence)
                nucleotide_sequence_idx.append(sample_idx)

    return nucleotide_sequences, nucleotide_sequence_idx


def _fetch_blast_hits(
    sequences: list[str],
) -> list[list[BlastHit | None]]:
    if not sequences:
        return []

    blast_params = {
        "CMD": "Put",
        "PROGRAM": "blastn",
        "MEGABLAST": True,
        "DATABASE": "core_nt",
        "HITLIST_SIZE": NUM_BLAST_HITS_CONSIDERED,
    }

    try:
        blast_results = run_blast(sequences, blast_params)
    except BlastError:
        return [[None]] * len(sequences)

    return extract_blast_hits(blast_results)


def _fetch_classifications(
    batch_ranked_blast_hits: list[list[BlastHit | None]],
) -> dict[int, list[ClassificationEntry] | None]:
    unique_taxon_ids = {
        blast_hit.taxon_id
        for ranked_blast_hits in batch_ranked_blast_hits
        for blast_hit in ranked_blast_hits
        if blast_hit
    }

    classifications = {}
    for taxon_id in unique_taxon_ids:
        try:
            classifications[taxon_id] = look_up_taxon_classification(taxon_id)
        except Exception as e:
            logger.error(f"Taxon look up failed: {e}")
            classifications[taxon_id] = None

    return classifications


def _add_classifications_by_voting(
    samples: list[Sample],
    batch_sample_idx: list[int],
    batch_ranked_blast_hits: list[list[BlastHit | None]],
    taxon_id_classifications: dict[int, list[ClassificationEntry] | None],
):
    ranked_blast_hits_by_sample_idx: dict[int, list[list[BlastHit | None]]] = (
        defaultdict(list)
    )

    for sample_idx, ranked_blast_hits in zip(batch_sample_idx, batch_ranked_blast_hits):
        ranked_blast_hits_by_sample_idx[sample_idx].append(ranked_blast_hits)

    for i, sample in enumerate(samples):
        ranked_blast_hits = ranked_blast_hits_by_sample_idx[i]

        # we first check if there is a perfect match based on the sample_id

        if classification := _get_perfect_name_match(
            ranked_blast_hits, taxon_id_classifications, sample.sample_id
        ):
            sample.scientific_name = classification[0].scientific_name
            sample.common_name = classification[0].common_name
            sample.classification = classification
            continue

        # otherwise, we use the ranking of the top BLAST and perform a voting

        votes_per_taxon_id = defaultdict(int)
        for ranked_blast_hits in ranked_blast_hits_by_sample_idx[i]:
            if not ranked_blast_hits:
                continue

            taxon_ids_used = set()

            num_votes = NUM_BLAST_HITS_CONSIDERED
            last_bit_score = None

            for blast_hit in ranked_blast_hits:
                if not blast_hit or blast_hit.taxon_id in taxon_ids_used:
                    continue

                if not last_bit_score:
                    last_bit_score = blast_hit.bit_score
                elif last_bit_score > blast_hit.bit_score:
                    last_bit_score = blast_hit.bit_score
                    num_votes -= 1

                if blast_hit and blast_hit.taxon_id not in taxon_ids_used:
                    votes_per_taxon_id[blast_hit.taxon_id] += num_votes
                    taxon_ids_used.add(blast_hit.taxon_id)

        if not votes_per_taxon_id:
            continue

        best_taxon_id = max(votes_per_taxon_id.items(), key=lambda x: x[1])[0]
        if classification := taxon_id_classifications.get(best_taxon_id):
            sample.scientific_name = classification[0].scientific_name
            sample.common_name = classification[0].common_name
            sample.classification = classification


def _get_perfect_name_match(
    batch_blast_hites: list[list[BlastHit | None]],
    taxon_id_classifications: dict[int, list[ClassificationEntry] | None],
    sample_id: str,
) -> list[ClassificationEntry] | None:
    unique_taxon_ids = {
        blast_hit.taxon_id
        for ranked_blast_hits in batch_blast_hites
        for blast_hit in ranked_blast_hits
        if blast_hit
    }

    matches = []

    for taxon_id in unique_taxon_ids:
        if not (classification := taxon_id_classifications.get(taxon_id)):
            continue

        scientific_name = classification[0].scientific_name
        score_scientific_name = match(sample_id, scientific_name)
        len_diff_scientific_name = abs(len(sample_id) - len(scientific_name))
        if score_scientific_name < 0.05:
            matches.append(
                (
                    (score_scientific_name, len_diff_scientific_name),
                    classification,
                )
            )

        common_name = classification[0].common_name
        if common_name:
            score_common_name = match(sample_id, common_name)
            len_diff_common_name = abs(len(sample_id) - len(common_name))
            if score_common_name < 0.05:
                matches.append(
                    (
                        (score_common_name, len_diff_common_name),
                        classification,
                    )
                )

    if matches:
        return min(matches, key=lambda x: x[0])[1]

    return None
