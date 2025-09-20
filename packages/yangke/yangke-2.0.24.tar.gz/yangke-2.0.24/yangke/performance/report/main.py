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
    entity_positions = []  # 记录所有实体的位置

    # 首先收集所有实体的位置
    while i < len(predicted_labels):
        if predicted_labels[i] == 1:  # 发现实体开始
            # 找到实体的起始和结束位置
            start = i
            while i < len(predicted_labels) and predicted_labels[i] == 1:
                i += 1
            end = i - 1

            # 记录实体位置
            try:
                char_start = offset_mapping[0][start][0].item()
                char_end = offset_mapping[0][end][1].item()
                entity_positions.append((char_start, char_end))
            except Exception as e:
                print(f"处理实体位置时出错: {e}")
        else:
            i += 1

    # 合并重叠或相邻的实体
    if entity_positions:
        merged_positions = [entity_positions[0]]
        for pos in entity_positions[1:]:
            last_pos = merged_positions[-1]
            # 如果当前实体与上一个实体重叠或相邻，则合并
            if pos[0] <= last_pos[1] + 1:  # 允许一个字符的间隔
                merged_positions[-1] = (last_pos[0], max(last_pos[1], pos[1]))
            else:
                merged_positions.append(pos)

        # 对每个合并后的实体进行处理
        for start, end in merged_positions:
            try:
                entity_text = text[start:end]
                print(f"找到实体: '{entity_text}' 位置: {start}-{end}")

                # 如果提供了原始实体信息，则匹配entity、value、unit
                if original_entities:
                    matched = False
                    for orig_entity in original_entities:
                        # 检查是否匹配（使用更宽松的匹配条件）
                        if (orig_entity["span"] in entity_text or
                                entity_text in orig_entity["span"] or
                                abs(len(entity_text) - len(orig_entity["span"])) < 5):  # 允许更大的长度差异
                            entities.append({
                                "entity": orig_entity["entity"],
                                "value": orig_entity["value"],
                                "unit": orig_entity["unit"]
                            })
                            matched = True
                            print(f"匹配成功: {orig_entity['entity']}")
                            break
                    if not matched:
                        # 如果没有匹配到，添加为未知实体
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
sample_text = "（10）50%负荷联合循环试验工况下，燃机输出毛功率为162.835MW，燃机的试验热耗率为10352.5kJ/(kW.h)，试验热效率为34.77%。经过修正后的燃机输出毛功率为165.607MW，修正后的燃机热耗率为10246.4kJ/(kW.h)，修正后的燃机热效率为35.13%。"
original_entities = None

# 查找包含相似实体的原始数据
best_match = None
best_match_count = 0

for item in data:
    match_count = 0
    # 计算与示例文本的匹配度
    if "抵达现场" in item["text"] or "试验完成" in item["text"]:
        match_count += 1
    if "2025年" in item["text"]:
        match_count += 1
    if match_count > best_match_count:
        best_match_count = match_count
        best_match = item

if best_match:
    original_entities = best_match["entities"]

entities = predict_entities(sample_text, model, tokenizer, original_entities)
print("发现的实体:")
# 去重
seen_entities = set()
unique_entities = []
for entity in entities:
    entity_key = (entity['entity'], entity['value'], entity['unit'])
    if entity_key not in seen_entities:
        seen_entities.add(entity_key)
        unique_entities.append(entity)

for entity in unique_entities:
    print(f"  实体名称: {entity['entity']}")
    print(f"  值: {entity['value']}")
    print(f"  单位: {entity['unit']}")
    print()