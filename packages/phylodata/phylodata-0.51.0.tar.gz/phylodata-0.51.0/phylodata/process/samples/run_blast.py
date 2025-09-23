import concurrent
import re
from dataclasses import dataclass
from random import random
from time import sleep

import requests
from loguru import logger

from phylodata.errors import BlastError

BLAST_URL = "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi"
WAIT_TIME_S = 30
MAX_BATCH_SIZE = 32


@dataclass
class BlastHit:
    taxon_id: int
    bit_score: float


def run_blast(sequences: list[str], parameters: dict) -> list:
    """Runs BLAST for the given sequences and parameters.
    Note that the QUERY parameter is added by this method.
    Returns the BLAST API results."""
    parameters["tool"] = "phylodata.com"
    parameters["email"] = "tobia.ochsner@inf.ethz.ch"

    batches = [
        sequences[i : i + MAX_BATCH_SIZE]
        for i in range(0, len(sequences), MAX_BATCH_SIZE)
    ]

    def process_batch(batch: list[str], parameters: dict) -> list:
        """Process a single batch of sequences through BLAST."""
        sleep(
            random() * WAIT_TIME_S
        )  # we space the requests to avoid overloading the server

        fasta_data = build_fasta_data(batch)
        batch_parameters = parameters.copy()
        batch_parameters["QUERY"] = fasta_data

        request_id, _ = initiate_blast_request(fasta_data, batch_parameters)
        wait_until_ready(request_id)

        return fetch_results(request_id)["BlastOutput2"]

    logger.info(f"Processing {len(batches)} batches of sequences...")

    with concurrent.futures.ThreadPoolExecutor() as executor:  # type: ignore
        batch_results = list(
            executor.map(lambda batch: process_batch(batch, parameters), batches)
        )
        flattened_results = [item for batch in batch_results for item in batch]
        return flattened_results


def build_fasta_data(sequences: list[str]) -> str:
    fasta_data = ""

    for i, seq in enumerate(sequences):
        fasta_data += f">{i}\n{seq}\n"

    return fasta_data


def initiate_blast_request(fasta_data: str, parameters: dict) -> tuple[str, int]:
    response = requests.post(BLAST_URL, data=parameters)
    if response.status_code != 200:
        logger.error("BLAST submission failed: " + response.text)
        raise BlastError("BLAST submission failed.")

    request_id = re.search(r"RID = (\S+)", response.text)
    wait_time_s = re.search(r"RTOE = (\d+)", response.text)

    if not request_id or not wait_time_s:
        logger.error("Failed to parse BLAST response: " + response.text)
        raise BlastError("Failed to parse BLAST response.")

    request_id = request_id.group(1)
    wait_time_s = int(wait_time_s.group(1))

    return request_id, wait_time_s


def wait_until_ready(request_id: str):
    result_params = {
        "CMD": "Get",
        "RID": request_id,
    }

    while True:
        response = requests.get(BLAST_URL, params=result_params)
        status = re.findall("Status=(.*)", response.text)[0]

        match status:
            case "READY":
                return
            case "WAITING":
                logger.info(f"Keep waiting for BLAST results... ({request_id})")
                sleep(WAIT_TIME_S)
            case _:
                logger.error(
                    f"BLAST submission failed with status {status}: {response.text}"
                )
                raise BlastError(f"BLAST submission failed: {status}")


def fetch_results(request_id: str) -> dict:
    result_params = {
        "CMD": "Get",
        "RID": request_id,
        "FORMAT_TYPE": "JSON2_S",
        "ALIGNMENTS": 1,
        "DESCRIPTIONS": 1,
    }

    response = requests.get(BLAST_URL, params=result_params)

    try:
        result = response.json()
    except Exception:
        logger.error(f"Failed to parse BLAST results: {response.text}")
        raise BlastError("Failed to parse BLAST results.")

    return result


def extract_taxon_ids(batch_blast_json: list) -> list[list[int | None]]:
    taxon_ids = []

    for result in batch_blast_json:
        current_taxon_ids = []

        if len(result["report"]["results"]["search"]["hits"]) == 0:
            logger.error("No hits found in BLAST result.")

        for hit in result["report"]["results"]["search"]["hits"]:
            try:
                taxon_id = hit["description"][0]["taxid"]
                taxon_id = int(taxon_id)
            except (KeyError, IndexError):
                logger.error(f"Failed to look up extract ID: {hit}")
                taxon_id = None

            current_taxon_ids.append(taxon_id)

        taxon_ids.append(current_taxon_ids)

    return taxon_ids


def extract_blast_hits(batch_blast_json: list) -> list[list[BlastHit | None]]:
    batch_blast_hits = []

    for result in batch_blast_json:
        current_blast_hits = []

        if len(result["report"]["results"]["search"]["hits"]) == 0:
            logger.error("No hits found in BLAST result.")

        for raw_hit in result["report"]["results"]["search"]["hits"]:
            try:
                blast_hit = BlastHit(
                    taxon_id=int(raw_hit["description"][0]["taxid"]),
                    bit_score=float(raw_hit["hsps"][0]["bit_score"]),
                )
            except (KeyError, IndexError):
                logger.error(f"Failed to look up extract ID: {raw_hit}")
                blast_hit = None

            current_blast_hits.append(blast_hit)

        batch_blast_hits.append(current_blast_hits)

    return batch_blast_hits
