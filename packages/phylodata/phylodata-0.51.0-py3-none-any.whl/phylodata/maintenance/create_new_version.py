import msgspec

from phylodata.data_types import FileType
from phylodata.maintenance.manage_db import update_db_for_experiment
from phylodata.maintenance.manage_files import copy_file_to_version, upload_file
from phylodata.paper_with_experiment import PaperWithExperiment
from phylodata.version import __version__

EDITABLE_METADATA_FILE = "editable_phylodata_metadata.json"
NON_EDITABLE_METADATA_FILE = "non_editable_phylodata_metadata"


def create_new_version(paper_with_experiments: PaperWithExperiment):
    """
    Creates a new version of an experiment.

    The new version will have the version number incremented by one, but the metadata and files should otherwise
    reflect all changes intended for the new version. Note that the `version` field in the input
    `paper_with_experiments` should remain as the old version; this function will update it internally.

    Currently, only changes to the metadata files (`editable_phylodata_metadata.json` and
    `non_editable_phylodata_metadata`) are supported. Changes to other files are not yet supported and will
    not be reflected in the new version.
    """
    experiment_id = paper_with_experiments.experiment.human_readable_id
    old_version = paper_with_experiments.experiment.version
    new_version = old_version + 1

    paper_with_experiments.metadata.evo_data_pipeline_version = __version__

    _remove_local_file_paths(paper_with_experiments)
    paper_with_experiments.experiment.version = new_version

    editable_paper, non_editable_paper = paper_with_experiments.to_partial()

    editable_metadata_file = msgspec.json.format(
        msgspec.json.encode(editable_paper), indent=2
    )
    non_editable_metadata_file = msgspec.json.encode(non_editable_paper)

    upload_file(
        editable_metadata_file,
        experiment_id,
        EDITABLE_METADATA_FILE,
        new_version,
    )
    upload_file(
        non_editable_metadata_file,
        experiment_id,
        NON_EDITABLE_METADATA_FILE,
        new_version,
    )

    for file in paper_with_experiments.files:
        if file.type == FileType.PHYLO_DATA_EXPERIMENT:
            continue

        copy_file_to_version(
            experiment_id,
            file.name,
            old_version,
            new_version,
        )

    update_db_for_experiment(experiment_id)


def _remove_local_file_paths(paper_with_experiments: PaperWithExperiment):
    for file in paper_with_experiments.files:
        if file.local_path:
            file.local_path = None
