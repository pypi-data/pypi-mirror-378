import hashlib
import shutil

import phylodata

EXPERIMENT_IDS = [
    # add experiment ids here
]

for experiment_id in EXPERIMENT_IDS:
    try:
        shutil.rmtree("data")
    except FileNotFoundError:
        ...

    try:
        experiment = phylodata.load_experiment(experiment_id, force_download=True)
    except ValueError as err:
        print("Mismatch (lerr):", experiment_id, err)

        continue

    for file in experiment.files:
        if not file.local_path or not file.local_path.exists():
            print("Mismatch (fnf):", experiment_id, file.name)
            continue

        with open(str(file.local_path), "rb") as file_to_check:
            md5 = hashlib.md5(file_to_check.read()).hexdigest()

        if md5 != file.md5:
            print("Mismatch (md5):", experiment_id, file.name)
            continue
