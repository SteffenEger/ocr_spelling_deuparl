import collections
import glob
import os

import tqdm

if __name__ == "__main__":

    bucket_folders = list(sorted(glob.glob("data/5_postprocessed/Reichstag/*/")))

    idx_per_slice = collections.Counter()
    for bucket_folder in tqdm.tqdm(bucket_folders):
        year = int(bucket_folder[-5:-1])  # Reichstag -> bucket name is year

        # this is not completely precise
        if year < 1890:
            slice_name = "1-KR1"
        elif year < 1918:
            slice_name = "2-KR2"
        elif year < 1933:
            slice_name = "3-WR"
        else:
            slice_name = "4-NS"

        if not os.path.isdir(f"data/6_sliced/{slice_name}/"):
            os.makedirs(f"data/6_sliced/{slice_name}/")

        file_paths = list(sorted(glob.glob(bucket_folder + "*.txt")))

        for file_path in file_paths:
            with open(file_path, encoding="utf-8") as file:
                text = file.read()

            idx_per_slice[slice_name] += 1
            with open(f"data/6_sliced/{slice_name}/{idx_per_slice[slice_name]}.txt", "w", encoding="utf-8") as file:
                file.write(text)
