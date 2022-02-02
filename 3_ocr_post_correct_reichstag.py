import collections
import glob
import os

import torch
from natsort import natsorted
from transformers import MBartTokenizer, MBartForConditionalGeneration
import tqdm

device = torch.device("cuda")

if __name__ == "__main__":
    model = MBartForConditionalGeneration.from_pretrained("data/models/mbart-for-ocr-post-correction-model-10").to(device)
    tokenizer = MBartTokenizer.from_pretrained("data/models/mbart-for-ocr-post-correction-tokenizer-10", src_lang="de_DE", tgt_lang="de_DE")
    bucket_folders = list(natsorted(glob.glob("data/2_preprocessed/Reichstag/*/")))

    count_per_bucket = collections.Counter()
    for bucket_folder in tqdm.tqdm(bucket_folders):
        bucket_name = int(bucket_folder[-5:-1])  # Reichstag -> bucket name is year

        if not os.path.isdir(f"data/3_ocr_post_corrected/Reichstag/{bucket_name}/"):
            os.makedirs(f"data/3_ocr_post_corrected/Reichstag/{bucket_name}/")

        file_paths = list(natsorted(glob.glob(bucket_folder + "*.txt")))

        for file_path in file_paths:

            if os.path.isfile(f"data/3_ocr_post_corrected/Reichstag/{bucket_name}/{count_per_bucket[bucket_name]}.txt"):
                continue

            with open(file_path, encoding="utf-8") as file:
                text = file.readlines()

            # TODO: do the OCR post correction here
            batch_size = 4
            outputs = []
            for i in range(0, len(text), batch_size):
                src_list = text[i: i + batch_size]
                tokenized_inputs = tokenizer(src_list, return_tensors="pt", padding="longest")
                tokenized_inputs = tokenized_inputs.to(device)
                translated_tokens = model.generate(**tokenized_inputs, decoder_start_token_id=tokenizer.lang_code_to_id["de_DE"])
                translated_tokens = translated_tokens.detach()
                output = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
                outputs += output

            count_per_bucket[bucket_name] += 1
            with open(f"data/3_ocr_post_corrected/Reichstag/{bucket_name}/{count_per_bucket[bucket_name]}.txt", "w", encoding="utf-8") as file:
                for line in outputs:
                    file.write(line + "\n")