import collections
import glob
import os

import tqdm

if __name__ == "__main__":

    bucket_folders = list(sorted(glob.glob("data/2_preprocessed/Reichstag/*/")))

    count_per_bucket = collections.Counter()
    for bucket_folder in tqdm.tqdm(bucket_folders):
        bucket_name = int(bucket_folder[-5:-1])  # Reichstag -> bucket name is year

        if not os.path.isdir(f"data/3_ocr_post_corrected/Reichstag/{bucket_name}/"):
            os.makedirs(f"data/3_ocr_post_corrected/Reichstag/{bucket_name}/")

        file_paths = list(sorted(glob.glob(bucket_folder + "*.txt")))

        for file_path in file_paths:
            with open(file_path, encoding="utf-8") as file:
                text = file.read()

            # TODO: do the OCR post correction here

            count_per_bucket[bucket_name] += 1
            with open(f"data/3_ocr_post_corrected/Reichstag/{bucket_name}/{count_per_bucket[bucket_name]}.txt", "w", encoding="utf-8") as file:
                file.write(text)
