import json
from transformers import BertTokenizerFast, BertForTokenClassification
from transformers import TrainingArguments, Trainer
from datasets import Dataset
import torch

# 加载数据
with open('spanner_clean.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


# 转换为 Hugging Face Dataset
def to_datasets_format(data):
    texts = []
    entities_list = []
    for item in data:
        text = item['text']
        entities = item['entities']
        # 对于每个文本，我们只添加一次，但会记录所有的实体信息
        texts.append(text)
        entities_list.append(entities)  # 保持为列表格式，即使为空
    return texts, entities_list


texts, entities_list = to_datasets_format(data)
dataset = Dataset.from_dict({"text": texts, "entities": entities_list})

# 分词器和模型
tokenizer = BertTokenizerFast.from_pretrained('bert-base-chinese')


def validate_entity_position(text, span, start_pos, char_to_token_start, char_to_token_end, tokens):
    """
    验证实体位置是否正确
    """
    print(f"原文本: {text}")
    print(f"实体文本: {span}")
    print(f"字符起始位置: {start_pos}")
    print(f"字符结束位置: {start_pos + len(span) - 1}")
    print(f"Token起始位置: {char_to_token_start}")
    print(f"Token结束位置: {char_to_token_end}")

    if char_to_token_start is not None and char_to_token_end is not None:
        # 获取对应的tokens
        entity_tokens = tokens[char_to_token_start:char_to_token_end + 1]
        print(f"实体对应的Tokens: {entity_tokens}")

        # 检查是否匹配
        reconstructed = "".join(entity_tokens).replace("##", "")
        print(f"重构的实体: {reconstructed}")
        print(f"是否匹配: {span in reconstructed or reconstructed in span}")

    print("-" * 50)


def tokenize_and_align_labels(examples):
    """
    对输入文本进行分词并为每个token生成对应的标签

    参数:
        examples: 包含文本和实体信息的字典
                 - 'text': 原始文本列表
                 - 'entities': 每个文本对应的实体信息列表

    返回:
        tokenized_inputs: 包含分词结果和对应标签的字典
    """

    # 使用BERT分词器对文本进行分词处理
    # truncation=True: 自动截断超过最大长度的文本
    # is_split_into_words=False: 输入文本是完整句子而非已分词的单词列表
    # padding=True: 对短文本进行填充使其长度一致
    # max_length=512: 设置最大序列长度为512（BERT模型的最大限制）
    tokenized_inputs = tokenizer(examples['text'], truncation=True, is_split_into_words=False, padding=True,
                                 max_length=512)

    # 存储每个样本的标签
    labels = []

    # 遍历每个样本（文本和对应的实体信息）
    for i, entities in enumerate(examples['entities']):
        # 初始化标签数组，长度与当前样本的token数量一致
        # 全部初始化为0，表示所有token都是非实体（背景标签）
        label_ids = [0] * len(tokenized_inputs['input_ids'][i])

        # 遍历当前样本中的所有实体
        for entity in entities:
            # 获取实体的文本片段
            span = entity["span"]

            # 在原始文本中查找实体的位置（起始字符索引）
            # find方法返回子字符串在主字符串中的起始位置，-1表示未找到
            start_pos = examples['text'][i].find(span)

            # 如果找到了该实体在文本中的位置
            if start_pos != -1:
                # 将实体的字符位置转换为token位置
                # char_to_token方法将字符索引转换为对应的token索引
                char_to_token_start = tokenized_inputs.char_to_token(i, start_pos)
                # 计算实体结束字符对应的token索引
                char_to_token_end = tokenized_inputs.char_to_token(i, start_pos + len(span) - 1)

                # 验证实体位置映射是否正确（仅对前几个样本进行验证）
                if i < 3:  # 只验证前3个样本
                    tokens = tokenizer.convert_ids_to_tokens(tokenized_inputs['input_ids'][i])
                    validate_entity_position(examples['text'][i], span, start_pos,
                                             char_to_token_start, char_to_token_end, tokens)

                # 确保起始和结束位置都有效（不为None）
                if char_to_token_start is not None and char_to_token_end is not None:
                    # 将实体对应的token标记为1（表示是实体）
                    # 实体可能跨越多个token，所以需要将范围内的所有token都标记为1
                    for j in range(char_to_token_start, char_to_token_end + 1):
                        # 将对应位置的标签设置为1（表示实体标签）
                        label_ids[j] = 1

        # 将当前样本的标签添加到标签列表中
        labels.append(label_ids)

    # 将生成的标签添加到分词结果中
    # 这样分词结果就包含了每个token对应的标签信息
    tokenized_inputs['labels'] = labels

    # 返回包含分词结果和标签的字典
    return tokenized_inputs


def predict_entities(text, model, tokenizer, original_entities=None):
    """
    使用训练好的模型预测文本中的实体

    参数:
        text: 要预测的文本
        model: 训练好的模型
        tokenizer: 分词器
        original_entities: 原始实体信息，用于提取entity、value、unit

    返回:
        entities: 预测出的实体列表，包含entity、value、unit信息
    """
    # 对文本进行分词，包含offset_mapping用于字符位置映射
    encoding = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512,
        return_offsets_mapping=True
    )

    # 获取token列表用于后续处理
    tokens = tokenizer.convert_ids_to_tokens(encoding['input_ids'][0])
    offset_mapping = encoding.pop('offset_mapping')  # 从输入中移除offset_mapping，因为模型不需要

    # 确保输入数据和模型在相同的设备上
    device = next(model.parameters()).device
    encoding = {key: val.to(device) for key, val in encoding.items()}

    # 使用模型进行预测
    with torch.no_grad():
        outputs = model(**encoding)  # 注意这里不再包含offset_mapping
        predictions = torch.argmax(outputs.logits, dim=-1)

    # 获取预测标签
    predicted_labels = predictions[0].tolist()

    # 提取实体
    entities = []
    i = 0
    while i < len(predicted_labels):
        if predicted_labels[i] == 1:  # 发现实体开始
            # 找到实体的起始和结束位置
            start = i
            while i < len(predicted_labels) and predicted_labels[i] == 1:
                i += 1
            end = i - 1

            # 将token范围转换为字符范围
            try:
                char_start = offset_mapping[0][start][0].item()
                char_end = offset_mapping[0][end][1].item()

                # 提取实体文本
                entity_text = text[char_start:char_end]

                # 打印找到的实体文本用于调试
                print(f"找到实体: '{entity_text}' 位置: {char_start}-{char_end}")

                # 如果提供了原始实体信息，则匹配entity、value、unit
                if original_entities:
                    matched = False
                    for orig_entity in original_entities:
                        # 使用模糊匹配，检查实体文本是否在原始span中，或者原始span是否在实体文本中
                        if (orig_entity["span"] in entity_text or
                                entity_text in orig_entity["span"] or
                                abs(len(entity_text) - len(orig_entity["span"])) < 3):  # 允许小的长度差异
                            entities.append({
                                "entity": orig_entity["entity"],
                                "value": orig_entity["value"],
                                "unit": orig_entity["unit"]
                            })
                            matched = True
                            print(f"匹配成功: {orig_entity['entity']}")
                            break
                    if not matched:
                        # 如果没有匹配到，仍然添加实体但标记为未知
                        entities.append({
                            "entity": "未知实体",
                            "value": entity_text,
                            "unit": ""
                        })
                else:
                    # 如果没有提供原始实体信息，则只返回文本
                    entities.append({
                        "entity": "未知实体",
                        "value": entity_text,
                        "unit": ""
                    })
            except Exception as e:
                print(f"处理实体时出错: {e}")
                i += 1
        else:
            i += 1

    return entities


tokenized_datasets = dataset.map(tokenize_and_align_labels, batched=True, remove_columns=dataset.column_names)

# 将数据集分割为训练集和测试集
train_test_split = tokenized_datasets.train_test_split(test_size=0.2)
train_dataset = train_test_split['train']
eval_dataset = train_test_split['test']

# 训练参数
training_args = TrainingArguments(
    output_dir='./results',
    eval_strategy='epoch',
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir='./logs',
)

# 模型
model = BertForTokenClassification.from_pretrained('bert-base-chinese', num_labels=2)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

# 训练
trainer.train()

# 使用示例：
# 查找包含相同实体的原始数据以获取entity、value、unit信息
sample_text = "西安热工研究院有限公司技术人员于2025年6月20日抵达现场，开始1号联合循环机组的性能试验准备工作，全部试验于2025年6月25日完成。"
original_entities = None

# 更灵活地查找匹配的原始实体
for item in data:
    if ("抵达现场" in item["text"] and "试验完成" in item["text"] and
        len(item["entities"]) >= 2):
        original_entities = item["entities"]
        break

# 如果没有找到完全匹配的，至少找一个包含实体的
if not original_entities:
    for item in data:
        if len(item["entities"]) > 0:
            original_entities = item["entities"]
            break

entities = predict_entities(sample_text, model, tokenizer, original_entities)
print("发现的实体:")
for entity in entities:
    print(f"  实体名称: {entity['entity']}")
    print(f"  值: {entity['value']}")
    print(f"  单位: {entity['unit']}")
    print()