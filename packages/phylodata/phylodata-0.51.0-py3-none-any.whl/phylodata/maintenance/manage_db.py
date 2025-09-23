import requests


def update_db_for_experiment(experiment_id: str):
    """
    Updates the DB entry for the given experiment ID.
    """
    response = requests.get(
        f"https://phylodata.com/api/updateExperiment/{experiment_id}"
    )

    if response.status_code != 200:
        raise ValueError(
            f"Failed to update the DB entry for experiment {experiment_id}"
        )
