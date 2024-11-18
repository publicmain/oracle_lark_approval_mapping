import re
from difflib import get_close_matches

# 原始字典
subsidiary = {
    "Singapore Entity": 15,
    "CANDYPAY HOLDINGS PTE LTD": 16,
    "DCS FINTECH HOLDINGS PTE LTD.": 1,
    "DCS CARD CENTRE PTE. LTD.": 2,
    "DCS PAYALL PTE LTD": 3,
    "DCS PREMIER PTE. LTD.": 9,
    "DIGITAL INCLUSION PTE. LTD": 11,
    "SHANGHAI DALAI": 14,
    "zz Elim Diners Club (Singapore) Private": 8,
    "DCS INNOV PTE LTD": 6,
    "DCS SERV PTE LTD": 5,
    "EZY TECH PTE LTD": 4,
    "UBIQ Payment Solutions Pte.Ltd.": 10,
    "zz Elim EzyNet": 7
}

def normalize_string(s):
    """
    规范化字符串：
    - 转为小写
    - 移除标点符号
    - 移除多余的空格
    """
    s = s.lower()
    s = re.sub(r'[^\w\s]', '', s)  # 移除标点符号
    s = re.sub(r'\s+', ' ', s)     # 移除多余空格
    s = s.strip()
    return s

# 创建一个规范化后的字典映射
normalized_subsidiary = {normalize_string(k): v for k, v in subsidiary.items()}

def mapping_entity_subsidiary(entity):
    normalized_entity = normalize_string(entity)
    # 尝试直接匹配
    value = normalized_subsidiary.get(normalized_entity)
    if value is not None:
        return value
    else:
        # 如果直接匹配失败，尝试模糊匹配
        possible_matches = get_close_matches(normalized_entity, normalized_subsidiary.keys(), n=1, cutoff=0.8)
        if possible_matches:
            return normalized_subsidiary[possible_matches[0]]
        else:
            return None  # 或者根据需求返回一个默认值或抛出异常

# 示例使用
test_entities = [
    "UBIQ Payment Solutions Pte Ltd",
    "DCS payall pte ltd",
    "zz Elim EzyNet",
    "DCS SERV PTE. LTD.",
    "Unknown Entity"
]

for entity in test_entities:
    result = mapping_entity_subsidiary(entity)
    print(f"Entity: {entity} -> Subsidiary ID: {result}")
