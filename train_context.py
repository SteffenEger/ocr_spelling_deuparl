import csv
import time

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AdamW
from transformers import MBartForConditionalGeneration, MBartTokenizer

if __name__ == "__main__":

    print("Load tokenizer.")
    tokenizer = MBartTokenizer.from_pretrained("facebook/mbart-large-cc25", src_lang="de_DE", tgt_lang="de_DE")
    tokenizer.add_tokens(["\t"])
    device = torch.device("cuda")

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
    for ix in range(1, 12799):
        X_train.append(f"{X_data[ix - 1]} \t {X_data[ix]} \t {X_data[ix + 1]}")
        Y_train.append(f"{Y_data[ix - 1]} \t {Y_data[ix]} \t {Y_data[ix + 1]}")

    X_dev, Y_dev = [], []
    for ix in range(12801, 14399):
        X_dev.append(f"{X_data[ix - 1]} \t {X_data[ix]} \t {X_data[ix + 1]}")
        Y_dev.append(f"{Y_data[ix - 1]} \t {Y_data[ix]} \t {Y_data[ix + 1]}")

    X_test, Y_test = [], []
    for ix in range(14401, len(X_data) - 1):
        X_test.append(f"{X_data[ix - 1]} \t {X_data[ix]} \t {X_data[ix + 1]}")
        Y_test.append(f"{Y_data[ix - 1]} \t {Y_data[ix]} \t {Y_data[ix + 1]}")


    # do not include context windows in data
    # X_train, Y_train = X_data[:8000], Y_data[:8000]
    # X_dev, Y_dev = X_data[8000:12000], Y_data[8000:12000]
    # X_test, Y_test = X_data[12000:], Y_data[12000:]

    ########################################################################################################################
    # TRAINING PROCESS
    ########################################################################################################################
    class MyDataset(Dataset):
        def __init__(self, x_data, y_data):
            # tokenize the data
            self.x_tokenized = tokenizer(x_data, return_tensors="pt", padding="longest")

            with tokenizer.as_target_tokenizer():
                self.y_tokenized = tokenizer(y_data, return_tensors="pt", padding="longest")

        def __len__(self):
            return len(self.x_tokenized["input_ids"])

        def __getitem__(self, index):
            return self.x_tokenized["input_ids"][index].tolist(), \
                    self.x_tokenized["attention_mask"][index].tolist(), \
                    self.y_tokenized["input_ids"][index].tolist()


    class TrainingBatch:
        def __init__(self, instances):
            input_ids = []
            attention_mask = []
            labels = []
            for i, a, l in instances:
                input_ids.append(i)
                attention_mask.append(a)
                labels.append(l)

            self.input_ids = torch.LongTensor(input_ids).to(device)
            self.attention_mask = torch.LongTensor(attention_mask).to(device)
            self.labels = torch.LongTensor(labels).to(device)

        def __getitem__(self, item):
            return getattr(self, item)

    print("Load the dataset.")
    training_dataset = MyDataset(X_train, Y_train)
    eval_dataset = MyDataset(X_dev, Y_dev)

    print("Initialize model and optimizer.")
    model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-cc25").to(device)
    model.resize_token_embeddings(len(tokenizer))
    optimizer = AdamW(model.parameters(), lr=0.000005)

    print("Create dataloader.")
    dataloader = DataLoader(training_dataset, collate_fn=TrainingBatch, batch_size=8, shuffle=True)
    eval_dataloader = DataLoader(eval_dataset, collate_fn=TrainingBatch, batch_size=8)

    print("Train.")
    best_loss = -1
    for epoch in range(1, 50):  # FINDME: control number of epochs (or do not fine-tune at all)
        print(f"Epoch {epoch}.")
        tik = time.time()

        running_loss = 0
        for num, batch in enumerate(dataloader):
            result = model(input_ids=batch.input_ids, attention_mask=batch.attention_mask, labels=batch.labels)
            result.loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            running_loss += float(result.loss.item())  # float() to detach and not keep history (loss is differentiable!)

        print(f"Loss: {running_loss}")

        if best_loss < 0 or running_loss < best_loss:
            print("New best loss!")
            best_loss = running_loss
            model.save_pretrained("data/models/mbart-for-ocr-post-correction-model-50")
            tokenizer.save_pretrained("data/models/mbart-for-ocr-post-correction-tokenizer-50")

        tak = time.time()
        print(f"Completed epoch in {tak - tik} seconds.")

    if best_loss == -1:
        model.save_pretrained("data/models/mbart-for-ocr-post-correction-model")
        tokenizer.save_pretrained("data/models/mbart-for-ocr-post-correction-tokenizer")

    print("Done!")
