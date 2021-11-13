import csv

import torch
from transformers import MBartTokenizer, MBartForConditionalGeneration

print("Load tokenizer and model.")
device = torch.device("cuda")

# use trained tokenizer and model
tokenizer = MBartTokenizer.from_pretrained("data/models/mbart-for-ocr-post-correction-tokenizer", src_lang="de_DE", tgt_lang="de_DE")
model = MBartForConditionalGeneration.from_pretrained("data/models/mbart-for-ocr-post-correction-model").to(device)

########################################################################################################################
# LOAD AND PREPARE DATA
########################################################################################################################
print("Load and prepare data.")
X_data = []
Y_data = []
with open("data/ocr_post_correction/data.csv", encoding="utf-8") as file:
    reader = csv.reader(file, delimiter=",", quotechar="\"")
    for row in reader:
        X_data.append(row[0])
        Y_data.append(row[1])

# include context windows in data
X_train, Y_train = [], []
for ix in range(1, 7999):
    X_train.append(f"{X_data[ix - 1]} <line-break> {X_data[ix]} <line-break> {X_data[ix + 1]}")
    Y_train.append(f"{Y_data[ix - 1]} <line-break> {Y_data[ix]} <line-break> {Y_data[ix + 1]}")

X_dev, Y_dev = [], []
for ix in range(8001, 11999):
    X_dev.append(f"{X_data[ix - 1]} <line-break> {X_data[ix]} <line-break> {X_data[ix + 1]}")
    Y_dev.append(f"{Y_data[ix - 1]} <line-break> {Y_data[ix]} <line-break> {Y_data[ix + 1]}")

X_test, Y_test = [], []
for ix in range(12001, len(X_data) - 1):
    X_test.append(f"{X_data[ix - 1]} <line-break> {X_data[ix]} <line-break> {X_data[ix + 1]}")
    Y_test.append(f"{Y_data[ix - 1]} <line-break> {Y_data[ix]} <line-break> {Y_data[ix + 1]}")


# do not include context windows in data
# X_train, Y_train = X_data[:8000], Y_data[:8000]
# X_dev, Y_dev = X_data[8000:12000], Y_data[8000:12000]
# X_test, Y_test = X_data[12000:], Y_data[12000:]

########################################################################################################################
# INFERENCE ON DATA
########################################################################################################################

print("Tokenize data.")
tokenized_inputs = tokenizer(X_dev[:10], return_tensors="pt", padding="longest")
tokenized_inputs = tokenized_inputs.to(device)

print("Run data through model.")
translated_tokens = model.generate(**tokenized_inputs, decoder_start_token_id=tokenizer.lang_code_to_id["de_DE"])
translated_tokens = translated_tokens.detach()

print("Detokenize data.")
outputs = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)

for y, output in zip(Y_dev[:10], outputs):
    print()
    print(f"Y:\t{y}")
    print(f"P:\t{output}")

print("Done!")
