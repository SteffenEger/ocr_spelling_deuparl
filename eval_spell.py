import csv
import time
import torch
from datasets import load_metric
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

device = torch.device("cuda")
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

X_train, Y_train = X_data[:12000], Y_data[:12000]
X_dev, Y_dev = X_data[12000:14000], Y_data[12000:14000]
X_test, Y_test = X_data[14000:], Y_data[14000:]

model = M2M100ForConditionalGeneration.from_pretrained(
    "data/models/m2m100_418M-for-ocr-post-correction-norma-model-50"
).to(device)

tokenizer = M2M100Tokenizer.from_pretrained(
    "data/models/m2m100_418M-for-ocr-post-correction-norma-tokenizer-50",
    src_lang="de",
    tgt_lang="de"
)
dev_predictions = []
start = time.time()

for dev in X_dev:
    tokenized_inputs = tokenizer(dev, return_tensors="pt", padding="longest").to(device)
    
    translated_tokens = model.generate(
        **tokenized_inputs,
        forced_bos_token_id=tokenizer.get_lang_id("de")
    )
    
    translated_tokens = translated_tokens.detach()
    output = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
    dev_predictions.append(output[0])

with open(f"m2m100_418M_norma_dev.txt", 'w') as f:
    for prediction in dev_predictions:
        f.write(f"{prediction}\n")

end = time.time()
print(f"process time in {end - start} seconds.")

cer = load_metric("cer")
cer_score = cer.compute(predictions=dev_predictions, references=Y_dev)
print(f"cer score of dev: {cer_score}")
print("Done dev!\n")

test_predictions = []
start = time.time()

for test in X_test:
    tokenized_inputs = tokenizer(test, return_tensors="pt", padding="longest").to(device)
    
    translated_tokens = model.generate(
        **tokenized_inputs,
        forced_bos_token_id=tokenizer.get_lang_id("de")
    )
    
    translated_tokens = translated_tokens.detach()
    output = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
    test_predictions.append(output[0])

with open(f"m2m100_418M_norma_test.txt", 'w') as f:
    for prediction in test_predictions:
        f.write(f"{prediction}\n")

end = time.time()
print(f"process time in {end - start} seconds.")

cer = load_metric("cer")
cer_score = cer.compute(predictions=test_predictions, references=Y_test)
print(f"cer score of test: {cer_score}")
print("Done test!\n")
