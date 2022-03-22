import torch
from typing import List
from transformers import (
    M2M100ForConditionalGeneration,
    M2M100Tokenizer,
)
import argparse
import logging
import os


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


class Reischtag():
    def __init__(self, year, session) -> None:
        self.year = year
        self.session = session
        with open(f"data/1_collected/Reichstag/{year}/{session}.txt", 'r') as f:
            self.text = f.read()

    def get_clean(self) -> List[str]:
        with open(f"data/2_preprocessed/Reichstag/{self.year}/{self.session}.txt", 'r') as f:
            cleaned = f.read()
        return cleaned

    @staticmethod
    def generate_ocr_norma(year, session):
        device = torch.device("cuda")

        model = M2M100ForConditionalGeneration.from_pretrained(
            "data/models/m2m100_418M-for-ocr-post-correction-norma-model-50"
        ).to(device)
        tokenizer = M2M100Tokenizer.from_pretrained(
            "data/models/m2m100_418M-for-ocr-post-correction-norma-tokenizer-50",
            src_lang="de",
            tgt_lang="de"
        )
        try:
            with open(f"data/2_preprocessed/Reichstag/{year}/{session}.txt", encoding="utf-8") as file:
                text = file.readlines()
        except Exception:
            raise Exception(f"{year} or {session} is not processed yet")
        
        batch_size = 4
        outputs = []
        print(f"Starting Reichstag {year} {session} pls wait")
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
        os.makedirs(f"data/3_ocr_post_corrected_spelling_normalization/Reichstag/{year}", exist_ok=True)
        with open(
            f"data/3_ocr_post_corrected_spelling_normalization/Reichstag/{year}/{session}.txt",
            "w", 
            encoding="utf-8"
        ) as file:
            for line in outputs:
                file.write(line + "\n")
        print(f"Done generate Reichstag {year} {session}")

    def get_post_ocr_norma(self) -> List[str]:
        try:
            with open(f"data/3_ocr_post_corrected_spelling_normalization/Reichstag/{self.year}/{self.session}.txt", 'r') as f:
                ocr_spell = f.read()
        except Exception:
            raise Exception(f"{self.year} or {self.session} is not generated yet")        
        return ocr_spell

    def get_slices(self) -> List[str]:
        pass

class Bundestag():
    def __init__(self, period, session) -> None:
        self.sessions = session
        self.period = period
        with open(f"data/1_collected/Bundestag/{period}/{session}.txt", 'r') as f:
            self.text = f.read()

    def get_clean(self) -> List[str]:
        with open(f"data/2_preprocessed/Bundestag/{self.period}/{self.session}.txt", 'r') as f:
            cleaned = f.read()
        return cleaned

    def get_normalized(self) -> List[str]:
        try:
            with open(f"data/3_ocr_post_corrected_spelling_normalization/Bundestag/{self.period}/{self.session}.txt", 'r') as f:
                spell = f.read()
        except Exception:
            raise Exception(f"{self.period} or {self.session} is not generated yet")
        return spell

    def get_slices(self) -> List[str]:
        pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--years", nargs="+")
    parser.add_argument("-s", "--session")
    args = parser.parse_args()
    for year in args.years:
        logging.info(f"Start {year}")
        Reischtag.generate_ocr_norma(year, args.session)
        logging.info(f"Done {year} {args.session}")


if __name__ == "__main__":
    main()
