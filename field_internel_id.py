import pandas as pd
from datetime import datetime
import re
import requests
from config import base_url,oauth,headers
postperiod = {
    '157': 'Aug 2020',
    '158': 'Sep 2020',
    '159': 'Oct 2020',
    '161': 'Nov 2020',
    '162': 'Dec 2020',
    '101': 'FY 2021',
    '119': 'FY 2022',
    '137': 'FY 2023',
    '138': 'Q1 2023',
    '139': 'Jan 2023',
    '140': 'Feb 2023',
    '141': 'Mar 2023',
    '142': 'Q2 2023',
    '143': 'Apr 2023',
    '144': 'May 2023',
    '145': 'Jun 2023',
    '146': 'Q3 2023',
    '147': 'Jul 2023',
    '148': 'Aug 2023',
    '149': 'Sep 2023',
    '150': 'Q4 2023',
    '151': 'Oct 2023',
    '152': 'Nov 2023',
    '153': 'Dec 2023',
    '154': 'Adjust 2023 (12/31 - 12/31)',
    '296': 'FY 2024',
    '297': 'Q1 2024',
    '298': 'Jan 2024',
    '299': 'Feb 2024',
    '300': 'Mar 2024',
    '301': 'Q2 2024',
    '302': 'Apr 2024',
    '303': 'May 2024',
    '304': 'Jun 2024',
    '305': 'Q3 2024',
    '306': 'Jul 2024',
    '307': 'Aug 2024',
    '308': 'Sep 2024',
    '309': 'Q4 2024',
    '310': 'Oct 2024',
    '311': 'Nov 2024',
    '312': 'Dec 2024',
    '331': 'Adjust 2024 (12/31 - 12/31)',
    '313': 'FY 2025',
    '314': 'Q1 2025',
    '315': 'Jan 2025',
    '316': 'Feb 2025',
    '317': 'Mar 2025',
    '318': 'Q2 2025',
    '319': 'Apr 2025',
    '320': 'May 2025',
    '321': 'Jun 2025',
    '322': 'Q3 2025',
    '323': 'Jul 2025',
    '324': 'Aug 2025',
    '325': 'Sep 2025',
    '326': 'Q4 2025',
    '327': 'Oct 2025',
    '328': 'Nov 2025',
    '329': 'Dec 2025',
    '330': 'Adjust 2025 (12/31 - 12/31)',
    '366': 'FY 2026'
}
# currency_dict = {
#     1: "SGD",
#     2: "USD",
#     4: "EUR",
#     5: "GBP",
#     6: "AUD",
#     7: "JPY",
#     8: "CNY",
#     9: "INR",
#     10: "HKD",
#     11: "MYR"
# }

def extract_number(string):
    # 匹配字符串开头的连续数字部分
    match = re.match(r"^\d+", string)
    return match.group(0) if match else None

def normalize_string(s):
    """
    规范化字符串：
    - 转为小写
    - 移除标点符号
    - 移除多余的空格
    """
    if s:  
        s = s.lower()
        s = re.sub(r'[^\w\s]', '', s)  # 移除标点符号
        s = re.sub(r'\s+', ' ', s)     # 移除多余空格
        s = s.strip()
        return s
    else:
        return ""


def fetch_all_items(table_name, columns="*", order_by=None, limit=5000):
    """从指定表中一次性获取所有数据，返回列表。"""
    order_clause = f"ORDER BY {order_by}" if order_by else ""
    query = f"""
    SELECT {columns}
    FROM {table_name}
    {order_clause}
    FETCH NEXT {limit} ROWS ONLY
    """
    response = requests.post(base_url, headers=headers, json={"q": query}, auth=oauth)
    response.raise_for_status()
    data = response.json()
    return data.get("items", [])

def fetch_all_items_paged(table_name, columns="*", order_by="id", batch_size=1000):
    """从指定表中分批次获取所有数据并合并返回，用于数据量较大的表(如vendor)。"""
    all_items = []
    last_id = 0
    has_more = True

    while has_more:
        query = f"""
        SELECT {columns}
        FROM {table_name}
        WHERE id > {last_id}
        ORDER BY {order_by}
        FETCH NEXT {batch_size} ROWS ONLY
        """
        response = requests.post(base_url, headers=headers, json={"q": query}, auth=oauth)
        response.raise_for_status()
        data = response.json()

        items = data.get("items", [])
        all_items.extend(items)

        if len(items) < batch_size:
            has_more = False
        else:
            last_id = max(item["id"] for item in items)

    return all_items

def match_item(items, target, key, partial=False):
    """
    当 target 是字符串：
        - partial=False：返回与 target 全字匹配的首个 item（不区分大小写），没有则返回 None。
        - partial=True ：返回包含 target 子串的首个 item（不区分大小写），没有则返回 None。

    当 target 是列表：
        - partial=False：返回与列表中任意字符串全字匹配的所有 items 列表（不区分大小写）。
        - partial=True ：返回包含列表中任意字符串子串的所有 items 列表（不区分大小写）。
    """
    if isinstance(target, list):
        targets_lower = [normalize_string(t).lower() for t in target if isinstance(t, str)]

        if partial:
            return [next((item for item in items if normalize_string(tl) in normalize_string(item.get(key, "")).lower()), None) for tl in targets_lower]
        else:
            return [next((item for item in items if normalize_string(item.get(key, "")).lower() == tl), None) for tl in targets_lower]


    else: 
        # target 是字符串的情况
        target_lower = target.lower()
        if partial:
            return next((item for item in items if target_lower in normalize_string(item.get(key, "")).lower()), None)
        else:
            return next((item for item in items if normalize_string(item.get(key, "")).lower() == target_lower), None)
        
def match_item_exact(items, target, key):
    """
    精确匹配函数：匹配 target 中的第一个编号与数据库项中的 key 字段精确匹配。
    """
    if isinstance(target, list):
        return [next((item for item in items if item.get(key).startswith(t.split()[0])), None) for t in target]
    else:
        return next((item for item in items if item.get(key).startswith(target.split()[0])), None)
    
def mapping_entity_subsidiary(target):
    #print("mapping_entity_subsidiary target",target)
    all_subsidiaries = fetch_all_items("subsidiary", columns="id, name")
    matched = match_item(all_subsidiaries, target, "name", partial=True)
    #print("subsidiary matched",matched)
    if matched:
        return matched["id"]
    else:
        print(f"Subsidiary with name containing '{target}' not found.")
        return None

def mapping_Vendor(target):

    print("mapping_Vendor target",target)
    all_vendors = fetch_all_items_paged("vendor", columns="id, entityid")
    matched = match_item_exact(all_vendors, target, "entityid")
    #print("Vendor matched",matched)
    if matched:
        if isinstance(matched, dict):
            return matched["id"]
        else:
            return [item["id"] for item in matched if item]
    else:
        return None

def mapping_Location(target):
    #print("mapping_Location target",target)
    all_locations = fetch_all_items("location", columns="id, name", order_by="id")
    matched = match_item(all_locations, target, "name", partial=False)
    #print("location matched",matched)
    if matched:
        return matched["id"]
    else:
        print(f"Location with name='{target}' not found.")
        return None

def mapping_GL_Account(target):
    print("mapping_GL_Account target", target)
    all_accounts = fetch_all_items("account", columns="id, accountsearchdisplayname", order_by="id")
    matched = match_item_exact(all_accounts, target, "accountsearchdisplayname")
    print("GL Account matched", matched)
    if matched:
        if isinstance(matched, dict):
            return matched["id"]
        else:
            return [item["id"] for item in matched if item]
    else:
        return None

def mapping_division(target):
    #print("division target",target)
    all_divisions = fetch_all_items("department", columns="id, name")
    matched = match_item(all_divisions, target, "name", partial=True)
    #print("division matched",matched)
    if matched[0]:
        ids = [item["id"] for item in matched]  # 提取每个匹配项的 id
        return ids
    else:
        return [None] * len(target)
    
def mapping_business(target):
    print("mapping_business target",target)
    all_accounts = fetch_all_items("CUSTOMRECORD_CSEG_BUSINESS", columns="id, name", order_by="id")
    matched = match_item(all_accounts, target, "name", partial=False)
    print("business matched",matched)
    if matched:
        ids = [item["id"] for item in matched]  # 提取每个匹配项的 id
        return ids
    else:
        return [None] * len(target)
    
def mapping_product_code(target):
    print("mapping_product_code target",target)
    all_accounts = fetch_all_items("classification", columns="id, name", order_by="id")
    matched = match_item(all_accounts, target, "name", partial=True)
    print("product code matched",matched)
    if matched:
        ids = [item["id"] for item in matched]  # 提取每个匹配项的 id
        return ids
    else:
        return [None] * len(target)
        

def mapping_product_type(target):
    print("mapping_product_type target",target)
    all_accounts = fetch_all_items("CUSTOMRECORD_CSEG_PR_TYPE", columns="id, name", order_by="id")
    matched = match_item(all_accounts, target, "name", partial=True)
    print("product type matched",matched)
    if matched:
        ids = [item["id"] for item in matched]  # 提取每个匹配项的 id
        return ids
    else:
        return [None] * len(target)
    
def mapping_project_code(target):
    print("mapping_project_code target",target)
    all_accounts = fetch_all_items("CUSTOMRECORD_CSEG1", columns="id, name", order_by="id")
    matched = match_item(all_accounts, target, "name", partial=True)
    print("project code matched",matched)
    if matched:
        ids = [item["id"] for item in matched]  # 提取每个匹配项的 id
        return ids
    else:
        return [None] * len(target)
    
def mapping_scheme(target):
    print("mapping_project_code target",target)
    all_accounts = fetch_all_items("CUSTOMRECORD_CSEG_SCHEME", columns="id, name", order_by="id")
    matched = match_item(all_accounts, target, "name", partial=True)
    print("scheme matched",matched)
    if matched:
        ids = [item["id"] for item in matched]  # 提取每个匹配项的 id
        return ids
    else:
        return [None] * len(target)
    
def mapping_currency(target):
    print("mapping_currency target",target)
    all_accounts = fetch_all_items("currency", columns="id, name", order_by="id")
    matched = match_item(all_accounts, target, "name", partial=False)
    print("currency matched",matched)
    if matched[0]:
        ids = [item["id"] for item in matched]  # 提取每个匹配项的 id
        return ids
    else:
        return [None] * len(target)
    
# 映射日期格式
def mapping_date(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    formatted_date = date_obj.strftime("%d/%m/%Y")
    return formatted_date



def mapping_postperiod(input_date):
    """
    根据输入日期（格式为 DD/MM/YYYY）在字典中查找匹配的键。
    
    :param input_date: 输入的日期字符串，例如 '11/20/2024'
    :param id_period_dict: 包含 Internal ID 和 Period Name 的字典
    :return: 匹配的键，如果未找到则返回 None
    """
    # 将输入日期字符串解析为 datetime 对象
    date_object = datetime.strptime(input_date, "%d/%m/%Y")
    
    # 格式化日期为 'Mon YYYY' 格式
    formatted_date = date_object.strftime("%b %Y")
    
    # 遍历字典查找匹配的值并返回键
    for key, value in postperiod.items():
        if formatted_date == value:
            return key
    return None
    









