import csv
import time

import torch
from transformers import (
    MBartTokenizer,
    MBartForConditionalGeneration,
    M2M100ForConditionalGeneration,
    M2M100Tokenizer,
    BartForConditionalGeneration,
    BartTokenizer
)

print("Load tokenizer and model.")
device = torch.device("cuda")

model = M2M100ForConditionalGeneration.from_pretrained("data/models/m2m100_418M-for-ocr-post-correction-model-50").to(device)
tokenizer = M2M100Tokenizer.from_pretrained("data/models/m2m100_418M-for-ocr-post-correction-tokenizer-50", src_lang="de", tgt_lang="de")


########################################################################################################################
# LOAD AND PREPARE DATA
########################################################################################################################
print("Load and prepare data.")
X_data = []
Y_data = []
with open("data/ocr_post_correction/data_norma.csv", encoding="utf-8") as file:
    reader = csv.reader(file, delimiter=",", quotechar="\"")
    for row in reader:
        X_data.append(row[0])
        Y_data.append(row[1])

# do not include context windows in data
X_train, Y_train = X_data[:12800], Y_data[:12800]
X_dev, Y_dev = X_data[12800:14400], Y_data[12800:14400]
X_test, Y_test = X_data[14400:], Y_data[14400:]

start = time.time()
for X, Y in zip(X_dev, Y_dev):
    print("Tokenize data.")
    tik = time.time()
    tokenized_inputs = tokenizer(X, return_tensors="pt", padding="longest")
    tak = time.time()
    print(f"tokenize in {tak - tik} seconds.")
    tokenized_inputs = tokenized_inputs.to(device)

    print("Run data through model.")
    tik = time.time()
    #m2m100
    translated_tokens = model.generate(**tokenized_inputs, forced_bos_token_id=tokenizer.get_lang_id("de"))
    
    #mbart
    #translated_tokens = model.generate(**tokenized_inputs, decoder_start_token_id=tokenizer.lang_code_to_id["de_DE"])
    
    #bart
    #translated_tokens = model.generate(**tokenized_inputs)
    
    tak = time.time()
    print(f"generate in {tak - tik} seconds.")
    translated_tokens = translated_tokens.detach()

    print("Detokenize data.")
    outputs = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)

    with open('m2m100_418M-for-ocr-post-correction-50-dev.txt', 'a') as f:
        f.write(f"{X}\t")
        f.write(f'{Y}\t')
        f.write(f'{outputs[0]}\n')

end = time.time()
print(f"process time in {end-start} seconds.")

print("Done!")
