import csv
import time
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AdamW
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

if __name__ == "__main__":

    print("Load tokenizer.")
    tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M", src_lang="de", tgt_lang="de")
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

    # do not include context windows in data
    X_train, Y_train = X_data[:12000], Y_data[:12000]
    X_dev, Y_dev = X_data[12000:14000], Y_data[12000:14000]
    X_test, Y_test = X_data[14000:], Y_data[14000:]
    
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

    print("Initialize model and optimizer.")
    model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M").to(device)
    optimizer = AdamW(model.parameters(), lr=0.000005)

    print("Create dataloader.")
    dataloader = DataLoader(training_dataset, collate_fn=TrainingBatch, batch_size=8, shuffle=True)

    print(f"Train.")
    best_loss = -1
    for epoch in range(1, 50):
        model.train()
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
            model.save_pretrained("data/models/m2m100_418M-for-ocr-post-correction-model-50")
            tokenizer.save_pretrained("data/models/m2m100_418M-for-ocr-post-correction-tokenizer-test-50")

        tak = time.time()
        print(f"Completed epoch in {tak - tik} seconds.")

    print("m2m100_418M")
    print("Done! Training")
    