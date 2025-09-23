from urllib.parse import quote

import requests


def copy_file_to_version(
    experiment_id: str, file_name: str, old_version: int, new_version: int
):
    """
    Copies a file from one version of an experiment to another version.

    Args:
        experiment_id (str): The human-readable ID of the experiment.
        file_name (str): The name of the file to copy.
        old_version (int): The version number to copy the file from.
        new_version (int): The version number to copy the file to.

    Raises:
        ValueError: If the file could not be copied.
    """
    encoded_file_name = quote(file_name)
    response = requests.get(
        f"https://phylodata.com/api/copyFileToVersion/{experiment_id}/{encoded_file_name}/{old_version}/{new_version}"
    )

    if response.status_code != 200:
        raise ValueError(
            f"Failed to copy the file {file_name} for experiment {experiment_id}"
        )


def upload_file(file: bytes, experiment_id: str, file_name: str, version: int):
    """
    Uploads a file to a specific version of an experiment.

    Args:
        file (bytes): The file content as bytes.
        experiment_id (str): The human-readable ID of the experiment.
        file_name (str): The name of the file to upload.
        version (int): The version number to upload the file to.

    Raises:
        ValueError: If the upload URL could not be obtained or the upload fails.
    """
    encoded_file_name = quote(file_name)
    upload_url = requests.get(
        f"https://phylodata.com/api/getUploadLink/{experiment_id}/{encoded_file_name}/{version}"
    )

    if upload_url.status_code != 200:
        raise ValueError(
            f"Failed to get the upload URL for the file {file_name} for experiment {experiment_id}"
        )

    response = requests.put(upload_url.text, data=file)

    if response.status_code != 200:
        raise ValueError(
            f"Failed to upload the file {file_name} for experiment {experiment_id}"
        )
