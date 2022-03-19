import collections
import glob
import os
from natsort import natsorted
import re

import tqdm

if __name__ == "__main__":

    bucket_folders = list(natsorted(glob.glob("data/2_preprocessed/Bundestag/*/")))

    count_per_bucket = collections.Counter()
    for bucket_folder in tqdm.tqdm(bucket_folders):
        bucket_name = int(bucket_folder[bucket_folder[:-1].rindex("/") + 1:-1])  # Bundestag -> bucket name is term number

        if not os.path.isdir(f"data/3_ocr_post_corrected_spelling_normalization/Bundestag/{bucket_name}/"):
            os.makedirs(f"data/3_ocr_post_corrected_spelling_normalization/Bundestag/{bucket_name}/")

        file_paths = list(natsorted(glob.glob(bucket_folder + "*.txt")))

        for file_path in file_paths:
            with open(file_path, encoding="utf-8") as file:
                text = file.readlines()   

            lines = [re.sub(r'daß$', 'dass', line).strip() for line in text]             
            lines = [re.sub(r'uß$', 'uss', line).strip() for line in text]
            lines = [re.sub(r'(ußt)', 'usst', line).strip() for line in text]

            count_per_bucket[bucket_name] += 1
            with open(f"data/3_ocr_post_corrected_spelling_normalization/Bundestag/{bucket_name}/{count_per_bucket[bucket_name]}.txt", "w", encoding="utf-8") as file:
                for line in lines:
                    file.write(line + "\n")
