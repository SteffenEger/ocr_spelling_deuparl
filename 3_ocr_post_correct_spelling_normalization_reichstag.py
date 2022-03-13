import collections
import glob
import os

import torch
from natsort import natsorted
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import tqdm

device = torch.device("cuda")

if __name__ == "__main__":
    model = M2M100ForConditionalGeneration.from_pretrained(
        "data/models/m2m100_418M-for-ocr-post-correction-norma-model-50").to(device)
    tokenizer = M2M100Tokenizer.from_pretrained(
        "data/models/m2m100_418M-for-ocr-post-correction-norma-tokenizer-50",
        src_lang="de",
        tgt_lang="de")
    bucket_folders = list(natsorted(glob.glob("data/2_preprocessed/Reichstag/*/")))

    count_per_bucket = collections.Counter()
    for bucket_folder in tqdm.tqdm(bucket_folders):
        bucket_name = int(bucket_folder[-5:-1])  # Reichstag -> bucket name is year

        if not os.path.isdir(f"data/3_ocr_post_corrected_spelling_normalization/Reichstag/{bucket_name}/"):
            os.makedirs(f"data/3_ocr_post_corrected_spelling_normalization/Reichstag/{bucket_name}/")

        file_paths = list(natsorted(glob.glob(bucket_folder + "*.txt")))

        for file_path in file_paths:

            if os.path.isfile(
                f"data/3_ocr_post_corrected_spelling_normalization/Reichstag/{bucket_name}/{count_per_bucket[bucket_name]}.txt"
            ):
                count_per_bucket[bucket_name] += 1
                continue

            with open(file_path, encoding="utf-8") as file:
                text = file.readlines()

            batch_size = 4
            outputs = []
            for i in range(0, len(text), batch_size):
                src_list = text[i: i + batch_size]
                tokenized_inputs = tokenizer(src_list, return_tensors="pt", padding="longest")
                tokenized_inputs = tokenized_inputs.to(device)
                translated_tokens = model.generate(
                    **tokenized_inputs,
                    forced_bos_token_id=tokenizer.get_lang_id("de")
                )
                translated_tokens = translated_tokens.detach()
                output = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
                outputs += output

            count_per_bucket[bucket_name] += 1
            with open(
                f"data/3_ocr_post_corrected_spelling_normalization/Reichstag/{bucket_name}/{count_per_bucket[bucket_name]}.txt",
                "w", 
                encoding="utf-8"
            ) as file:
                for line in outputs:
                    file.write(line + "\n")