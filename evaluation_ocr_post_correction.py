import csv
import time
import os
import argparse
import torch
import logging
from datasets import load_metric
from transformers import (
    MBartForConditionalGeneration,
    MBartTokenizer,
    M2M100ForConditionalGeneration,
    M2M100Tokenizer
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data")
    parser.add_argument("-m", "--model")
    args = parser.parse_args()

    model_name, epochs = args.model.split('-')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    logging.info(f"Load and prepare {args.data}, {args.model}.")

    def read_data(data):
        temp_source, temp_ref = [], []
        with open(f"data/ocr_post_correction/raw_training_data/{data}.csv", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=",", quotechar="\"")
            next(reader)
            for row in reader:
                if len(row) < 2:
                    continue
                elif row[0] == '' or row[1] == '':
                    continue
                temp_source.append(row[0])
                temp_ref.append(row[1])
        return temp_source, temp_ref

    sources = []
    references = []
    if args.data == "1873":
        data_1873 = [
            "R_1873_Seite_721-729",
            "R_1873_Seite_730-739",
            "R_1873_Seite_740-749",
            "R_1873_Seite_750-759"
        ]
        for data in data_1873:
            temp_sources, temp_ref = read_data(data)
            sources += temp_sources
            references += temp_ref
    elif args.data == "1900":
        sources, references = read_data("R_1900")
    elif args.data == "1914":
        sources, references = read_data("R_1914_13_LP_Band_292_6601-6640")
    elif args.data == "1916": 
        sources, references = read_data("R_1916_Sitzung_36_Seite_819-839")
    else:
        raise ValueError("No data for evaluation")
            
    if os.path.isfile(f"{args.data}_{args.model}.txt"):
        with open(f"{args.data}_{args.model}.txt", 'w') as f:
            predictions = f.read().splitlines()
    else:
        if model_name == "m2m100_418M":
            model = M2M100ForConditionalGeneration.from_pretrained(
                f"data/models/{model_name}-for-ocr-post-correction-model-{epochs}").to(device)
            tokenizer = M2M100Tokenizer.from_pretrained(
                f"data/models/{model_name}-for-ocr-post-correction-tokenizer-{epochs}",
                src_lang="de",
                tgt_lang="de"
            )
        elif model_name == "mbart":
            model = MBartForConditionalGeneration.from_pretrained(
                f"data/models/{model_name}-for-ocr-post-correction-model-{epochs}").to(device)
            tokenizer = MBartTokenizer.from_pretrained(
                f"data/models/{model_name}-for-ocr-post-correction-tokenizer-{epochs}",
                src_lang="de_DE", 
                tgt_lang="de_DE"
            )
        else:
            raise ValueError("Invalid model")

        predictions = []
        start = time.time()

        for source in sources:
            tokenized_inputs = tokenizer(source, return_tensors="pt", padding="longest").to(device)
            
            if model_name == "m2m100_418M":
                translated_tokens = model.generate(
                    **tokenized_inputs,
                    forced_bos_token_id=tokenizer.get_lang_id("de")
                )
            elif model_name == "mbart":
                translated_tokens = model.generate(
                    **tokenized_inputs,
                    decoder_start_token_id=tokenizer.lang_code_to_id["de_DE"]
                )
            
            translated_tokens = translated_tokens.detach()
            output = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
            predictions.append(output[0])

        with open(f"{args.data}_{args.model}.txt", 'w') as f:
            for prediction in predictions:
                f.write(f"{prediction}\n")

        end = time.time()
        logging.info(f"process time in {end - start} seconds.")
    
    cer = load_metric("cer")
    cer_score = cer.compute(predictions=predictions, references=references)
    logging.info(f"cer score of {args.data}: {cer_score}")
    logging.info("Done!\n")
    

if __name__ == "__main__":
    main()

