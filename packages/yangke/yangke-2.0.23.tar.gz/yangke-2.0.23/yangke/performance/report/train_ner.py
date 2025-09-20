# 训练AI模型，提取word文档中试验数值的位置和含义
from transformers import BertTokenizerFast, BertForTokenClassification, Trainer, TrainingArguments
from datasets import load_dataset, Dataset
import torch

# 1. 加载 tokenizer
model_name = "bert-base-chinese"
tokenizer = BertTokenizerFast.from_pretrained(model_name)

# 2. 加载数据
def load_conll(path):
    sentences, labels = [], []
    sent, label = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "":
                if sent:
                    sentences.append(sent)
                    labels.append(label)
                    sent, label = [], []
            else:
                char, tag = line.split()
                sent.append(char)
                label.append(tag)
    return sentences, labels

train_sentences, train_labels = load_conll("train.txt")
val_sentences, val_labels = load_conll("dev.txt")

# 3. 标签映射
label_list = sorted(set(sum(train_labels, [])))
label2id = {l: i for i, l in enumerate(label_list)}
id2label = {i: l for l, i in label2id.items()}

# 4. 编码函数
def encode(sentences, labels):
    encodings = tokenizer(sentences, is_split_into_words=True, truncation=True, padding=True)
    new_labels = []
    for i, label in enumerate(labels):
        word_ids = encodings.word_ids(batch_index=i)
        prev_word_id = None
        label_ids = []
        for word_id in word_ids:
            if word_id is None:
                label_ids.append(-100)
            elif word_id != prev_word_id:
                label_ids.append(label2id[label[word_id]])
            else:
                label_ids.append(-100)
            prev_word_id = word_id
        new_labels.append(label_ids)
    encodings["labels"] = new_labels
    return encodings

train_encodings = encode(train_sentences, train_labels)
val_encodings = encode(val_sentences, val_labels)

train_dataset = Dataset.from_dict(train_encodings)
val_dataset = Dataset.from_dict(val_encodings)

# 5. 模型
model = BertForTokenClassification.from_pretrained(
    model_name,
    num_labels=len(label_list),
    id2label=id2label,
    label2id=label2id
)

# 6. 训练参数
training_args = TrainingArguments(
    output_dir="./ner_model",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=10,
    weight_decay=0.01,
    logging_dir="./logs",
)

# 7. Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
)

# 8. 训练
trainer.train()
trainer.save_model("./ner_model")