import collections
import glob
import os

import tqdm

if __name__ == "__main__":

    bucket_folders = list(sorted(glob.glob("data/5_postprocessed/Bundestag/*/")))

    idx_per_slice = collections.Counter()
    for bucket_folder in tqdm.tqdm(bucket_folders):
        bucket_name = int(bucket_folder[bucket_folder[:-1].rindex("/") + 1:-1])  # Bundestag -> bucket name is term number

        bucket_to_slice = {
            "1": "5-CDU1",
            "2": "5-CDU1",
            "3": "5-CDU1",
            "4": "5-CDU1",
            "5": "5-CDU1",
            "6": "6-SPD1",
            "7": "6-SPD1",
            "8": "6-SPD1",
            "9": "6-SPD1",
            "10": "7-CDU2",
            "11": "7-CDU2",
            "12": "7-CDU2",
            "13": "7-CDU2",
            "14": "8-SPD2",
            "15": "8-SPD2",
            "16": "9-CDU3",
            "17": "9-CDU3",
            "18": "9-CDU3",
            "19": "9-CDU3"
        }

        slice_name = bucket_to_slice[str(bucket_name)]

        if not os.path.isdir(f"data/6_sliced/{slice_name}/"):
            os.makedirs(f"data/6_sliced/{slice_name}/")

        file_paths = list(sorted(glob.glob(bucket_folder + "*.txt")))

        for file_path in file_paths:
            with open(file_path, encoding="utf-8") as file:
                text = file.read()

            idx_per_slice[slice_name] += 1
            with open(f"data/6_sliced/{slice_name}/{idx_per_slice[slice_name]}.txt", "w", encoding="utf-8") as file:
                file.write(text)
