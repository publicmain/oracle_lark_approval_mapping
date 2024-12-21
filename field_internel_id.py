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

GST_dict = {
    "TX-N33-SG": {"Internal ID": 19, "Rate": "7.00%"},
    "TX-E33-SG": {"Internal ID": 18, "Rate": "7.00%"},
    "SRRC-SG": {"Internal ID": 26, "Rate": "0.00%"},
    "SROVR-SG": {"Internal ID": 27, "Rate": "7.00%"},
    "SG-Out of Scope Supplies": {"Internal ID": 11, "Rate": "0.00%"},
    "SG-GST Purchase Out of Scope": {"Internal ID": 14, "Rate": "0.00%"},
    "SG-GST Exempt Supplies R33": {"Internal ID": 8, "Rate": "0.00%"},
    "SG-GST 9% Std Rate": {"Internal ID": 485, "Rate": "9.00%"},
    "SG-GST 9% Purchase": {"Internal ID": 486, "Rate": "9.00%"},
    "SG-GST 8% Std Rate": {"Internal ID": 433, "Rate": "8.00%"},
    "SG-GST 8% Purchase": {"Internal ID": 434, "Rate": "8.00%"},
    "SG-GST 7% Std Rate": {"Internal ID": 6, "Rate": "7.00%"},
    "SG-GST 7% Purchase": {"Internal ID": 17, "Rate": "7.00%"},
    "SG-GST 0% ZR Supplies": {"Internal ID": 7, "Rate": "0.00%"},
    "SG-GST 0% ZR Purchase": {"Internal ID": 21, "Rate": "0.00%"},
    "NR-SG": {"Internal ID": 12, "Rate": "0.00%"},
    "Not Applicable": {"Internal ID": 198, "Rate": "0.00%"},
    "GST 9% N/Claimable": {"Internal ID": 484, "Rate": "9.00%"},
    "GST 8% N/Claimable": {"Internal ID": 460, "Rate": "8.00%"},
    "GST 7% N/Claimable": {"Internal ID": 22, "Rate": "7.00%"},
    "ESN33-SG": {"Internal ID": 9, "Rate": "0.00%"},
    "CN-VAT 1%": {"Internal ID": 490, "Rate": "1.00%"}
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
    target = re.sub(r'\s*\(fka[^)]*\)', '', target)
    all_subsidiaries = fetch_all_items("subsidiary", columns="id, name")
    matched = match_item(all_subsidiaries, target, "name", partial=True)
    #print("subsidiary matched",matched)
    if matched:
        return matched["id"]
    else:
        print(f"Subsidiary with name containing '{target}' not found.")
        return None

def mapping_Vendor(target):

    #print("mapping_Vendor target",target)
    if target:
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
    else:
        return None

def mapping_Location(target):
    #print("mapping_Location target",target)
    all_locations = fetch_all_items("location", columns="id, name", order_by="id")
    matched = match_item(all_locations, target, "name", partial=False)
    #print("location matched",matched)
    if isinstance(target, list):
        if matched and any(matched):
            ids = [item["id"] if item else None for item in matched]
            return ids
        else:
            return [None] * len(target)
    else:
        if matched:
            return matched["id"]
        else:
            return None

def mapping_GL_Account(target):
    #print("mapping_GL_Account target", target)

    # 记录原始列表的长度
    length = len(target)

    # 分离非 None 的条目及其索引
    non_none_items = []
    non_none_indices = []
    for i, t in enumerate(target):
        if t is not None:
            non_none_items.append(t)
            non_none_indices.append(i)

    all_accounts = fetch_all_items("account", columns="id, accountsearchdisplayname", order_by="id")

    # 针对非 None 的内容进行匹配
    matched_non_none = match_item_exact(all_accounts, non_none_items, "accountsearchdisplayname")
    # matched_non_none 与 non_none_items 等长，每个元素要么是匹配的 dict，要么是 None

    # 准备结果列表，与输入 target 一样长
    result = [None] * length

    # 将匹配结果回填到相应位置
    for idx, val in zip(non_none_indices, matched_non_none):
        if val is not None:
            # val 是一个字典
            result[idx] = val["id"]
        else:
            # 未匹配到，保持 None
            result[idx] = None

    #print("GL Account matched result:", result)
    return result

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
    cleaned_list = []

    for item in target:
        if item is None:
            # Retain None if the element is None
            cleaned_list.append(None)
        elif isinstance(item, str):
            # Find the first occurrence of ':' and extract the part after it
            parts = item.split(":", 1)
            
            if len(parts) > 1:
                # Strip any leading or trailing whitespace from the part after the colon
                cleaned_list.append(parts[1].strip())
            else:
                # If there is no colon, return the original string
                cleaned_list.append(item.strip())
        else:
            # If the item is not a string or None, append None
            cleaned_list.append(None)
    #print("mapping_business target",target)
    all_accounts = fetch_all_items("CUSTOMRECORD_CSEG_BUSINESS", columns="id, name", order_by="id")
    matched = match_item(all_accounts, cleaned_list, "name", partial=False)
    #print("business matched",matched)
    if isinstance(target, list):
        if matched and any(matched):
            ids = [item["id"] for item in matched if item]
            return ids
        else:
            return [None] * len(target)
    else:
        if matched:
            return matched["id"]
        else:
            return None
    
def mapping_product_code(target):
    #print("mapping_product_code target",target)
    all_accounts = fetch_all_items("classification", columns="id, name", order_by="id")
    matched = match_item(all_accounts, target, "name", partial=True)
    #print("product code matched",matched)
    if isinstance(target, list):
        if matched and any(matched):
            ids = [item["id"] if item else None for item in matched]
            return ids
        else:
            return [None] * len(target)
    else:
        if matched:
            return matched["id"]
        else:
            return None
        

def mapping_product_type(target):
    #print("mapping_product_type target",target)
    cleaned_list = []

    for item in target:
        if item is None:
            # Retain None if the element is None
            cleaned_list.append(None)
        elif isinstance(item, str):
            # Find the first occurrence of ':' and extract the part after it
            parts = item.split(":", 1)
            
            if len(parts) > 1:
                # Strip any leading or trailing whitespace from the part after the colon
                cleaned_list.append(parts[1].strip())
            else:
                # If there is no colon, return the original string
                cleaned_list.append(item.strip())
        else:
            # If the item is not a string or None, append None
            cleaned_list.append(None)
    all_accounts = fetch_all_items("CUSTOMRECORD_CSEG_PR_TYPE", columns="id, name", order_by="id")
    matched = match_item(all_accounts, cleaned_list, "name", partial=True)
    #print("product type matched",matched)
    if isinstance(target, list):
        if matched and any(matched):
            ids = [item["id"] if item else None for item in matched]
            return ids
        else:
            return [None] * len(target)
    else:
        if matched:
            return matched["id"]
        else:
            return None
    
def mapping_project_code(target):
    #print("mapping_project_code target",target)
    all_accounts = fetch_all_items("CUSTOMRECORD_CSEG1", columns="id, name", order_by="id")
    matched = match_item(all_accounts, target, "name", partial=True)
    #print("project code matched",matched)
    if isinstance(target, list):
        if matched and any(matched):
            ids = [item["id"] if item else None for item in matched]
            return ids
        else:
            return [None] * len(target)
    else:
        if matched:
            return matched["id"]
        else:
            return None
    
def mapping_scheme(target):
    #print("mapping_scheme target", target)
    cleaned_list = []

    for index, item in enumerate(target):
        if item is None:
            # Retain None if the element is None
            cleaned_list.append(None)
        elif isinstance(item, str):
            # Split the string by ':' and strip whitespace from each part
            parts = [part.strip() for part in item.split(':')]

            if parts:
                # Extract the last part as the desired scheme name
                scheme_name = parts[-1]
                cleaned_list.append(scheme_name)
            else:
                # If splitting results in an empty list, append an empty string
                cleaned_list.append("")
        else:
            # If the item is neither None nor a string, append None
            cleaned_list.append(None)

    all_accounts = fetch_all_items("CUSTOMRECORD_CSEG_SCHEME", columns="id, name", order_by="id")
    matched = match_item(all_accounts, cleaned_list, "name", partial=True)
    #print("scheme matched", matched)
    
    if isinstance(target, list):
        if matched and any(matched):
            ids = [item["id"] if item else None for item in matched]
            return ids
        else:
            return [None] * len(target)
    else:
        if matched:
            return matched["id"]
        else:
            return None
    
def mapping_currency(target):
    print("mapping_currency target",target)
    all_accounts = fetch_all_items("currency", columns="id, name", order_by="id")
    matched = match_item(all_accounts, target, "name", partial=False)
    print("currency matched",matched)
    if isinstance(target, list):
        if matched and any(matched):
            ids = [item["id"] if item else None for item in matched]
            return ids
        else:
            return [None] * len(target)
    else:
        if matched:
            return matched["id"]
        else:
            return None
    
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

def mapping_taxcode(target):
    """
    根据给定的 Name 列表，返回对应的 Internal ID 列表和 Rate 列表。

    参数:
        names_list (list): 包含多个 Name 的列表。

    返回:
        tuple: (ids_list, rates_list)
            - ids_list (list): 对应的 Internal ID 列表。
            - rates_list (list): 对应的 Rate 列表。
    """
    ids_list = []
    rates_list = []
    
    for name in target:
        info = GST_dict.get(name)
        if info:
            ids_list.append(info["Internal ID"])
            rates_list.append(info["Rate"])
        else:
            ids_list.append(None)  
            rates_list.append(None)
    
    return ids_list, rates_list

def mapping_item(target):
    result = []
    
    for item in target:
        if item is None:
            result.append(None) 
        else:
            first_word = item.split()[0] if item.strip() else ""
            result.append(first_word)
    
    return result

def mapping_giro_paid(target):
    """
    根据输入的字符串，返回对应的 Internal ID。

    参数:
        target (str): 输入的字符串。

    返回:
        int: 对应的 Internal ID。
    """
    if target:
        if target == "Yes":
            return 1
        else:
            return 2
    else:
        print(f"Giro Paid with name containing '{target}' not found.")
        return None
    
# def mapping_item(target):
#     """
#     实现对item的匹配逻辑：
#     1. 获取所有items (id, itemid)
#     2. 对于每个target(可以是单字符串或列表):
#        - 拆分单词，从第一个词开始匹配，如果找不到就加下一个词，一直加到整句。
#        - 匹配时都做normalize处理，并在获取的items中查询清洗后的名称是否存在。
#        - 找到匹配则返回对应的id；若没找到返回None。
       
#     返回值： 
#     - 若 target 是字符串：返回找到的 item 的 id 或 None
#     - 若 target 是列表：返回与列表中每个元素对应的 id 或 None 的列表
#     """
#     def fetch_and_build_item_dict():
#         all_items = fetch_all_items_paged("item", columns="id, itemid")
#         item_dict = {}
#         for itm in all_items:
#             # normalize itemid
#             normalized = normalize_string(itm["itemid"])
#             item_dict[normalized] = itm
#         return item_dict

#     item_dict = fetch_and_build_item_dict()

#     def match_single_item(t):
#         if not t:
#             return None
#         words = t.split()
#         for i in range(1, len(words) + 1):
#             candidate_str = " ".join(words[:i])
#             cleaned_candidate = normalize_string(candidate_str)
#             if cleaned_candidate in item_dict:
#                 return item_dict[cleaned_candidate]["id"]
#         return None

#     if isinstance(target, list):
#         # 使用条件表达式，确保每个元素都有对应的输出
#         return [match_single_item(t) if t else None for t in target]
#     else:
#         return match_single_item(target)
# if __name__ == "__main__":
#     # 要测试的所有Lark items
#     lark_items = [
#         "IAPAS001 AIRLINE PILOT ASSOC OF SPORE",
#         "IIE001 THE INST OF ELECTRICAL ENGR SPORE CTR",
#         "IIEEE001 INST OF ELECTRICAL&ELECTRONIC ENGR",
#         "IIES001 THE INSTITUTION OF ENGINEERS SPORE",
#         "IIFPAS001 INS & FIN PRAC ASSOC OF SPORE",
#         "INAA001 NGEE ANN ALUMNI",
#         "ISEEU001 SPORE ENGRG CO ENGR & EXEC UNION",
#         "ISHRI001 SPORE HUMAN RESOURCE INSTITUTE",
#         "ISIASU001 SPORE AIRLINES STAFF UNION",
#         "ISMOU001 SPORE MARITIME OFFICERS UNION",
#         "DCS D-Lite Corporate Card MC2604 DCS D-Lite Corporate Card MC2604",
#         "DCS Flex Visa Platinum Card Basic VC2006 DCS Flex Visa Platinum Card Basic VC2006",
#         "DCS Flex Visa Platinum Card Limited Ed VC2007 DCS Flex Visa Platinum Card Limited Ed VC2007",
#         "DCS imToken Cobrand Card MV3505 DCS imToken Cobrand Card MV3505",
#         "DCS UPI D-Lite UV3502 DCS UPI D-Lite UV3502",
#         "DCS UPI Ultimate Platinum UC2004 DCS UPI Ultimate Platinum UC2004",
#         "Full Metal Dual Interface Card MC2008 Full Metal Dual Interface Card MC2008",
#         "IACE001 ACE CREDIT CARD",
#         "ICBK001 CASHBACK CARD",
#         "ICOU001 COURTS REBATE CARD",
#         "ICRE001 CREDIT CARD",
#         "ICRIN001 NATURE'S FARM COBRAND CARD",
#         "IDCT001 DELIVERY CHINATOWN COBRAND CARD",
#         "IDON001 DON DON DONKI COBRAND CARD",
#         "IHYD001 HYDEFI COBRAND CARD",
#         "IJP001 JP PEPPERDINE COBRAND CARD",
#         "ILB001 LONG BEACH COBRAND CARD",
#         "IMC D-Lite 3503 PCC017-MC D-Lite 3503",
#         "IMC Ultimate Platinum PCC015-MC Ultimate Platinum MC2005",
#         "Imperium World Elite MC2008 Imperium World Elite MC2008",
#         "IMUS001 MUSTAFA COBRAND CARD",
#         "INSK001 NUSKIN COBRAND CARD",
#         "IPC001 CHARGE PHOTOCARD",
#         "IPCRE001 CREDIT PHOTOCARD",
#         "IPOP001 POPULAR COBRAND CARD",
#         "IRML001 RAFFLES MARINA COBRAND CARD",
#         "IS001 CHARGE CARD",
#         "ISS001 SHENG SIONG COBRAND CARD",
#         "IVIC001 VICOM COBRAND CARD",
#         "MC COURTS - MC2112 DCS Courts Cobrand Card (MasterCard)",
#         "MC Platinum Dragon - MV3510 MC Platinum Dragon (Doo Cobrand Card)",
#         "UPI Platinum Dragon - UV3509 UPI Platinum Dragon (Doo Cobrand Card)",
#         "D Visa Platinum (VUSD/VDLT)",
#         "XIAOMI SMART BAND 8 ACTIVE",
#         "CATERPILLAR 24\" luggage",
#         "MC DECARD MV3788 LUMINARIES",
#         "MC DECARD MV3788 PINK",
#         "MC DECARD MV3788 BLUE",
#         "MC DECARD MV3788 GREEN"
#     ]

    # # 测试匹配
    # success_count = 0
    # fail_count = 0
    # total = len(lark_items)

    # print("------------------------------------------------------------")
    # print(f"[TEST START] 开始测试 {total} 个Lark items")
    # print("------------------------------------------------------------")

    # for l_item in lark_items:
    #     found_id = mapping_item(l_item)
    #     if found_id:
    #         print(f"[SUCCESS] Lark item: '{l_item}' => Oracle item ID: {found_id}")
    #         success_count += 1
    #     else:
    #         print(f"[FAIL] Lark item: '{l_item}' => 未找到匹配条目")
    #         fail_count += 1

    # print("------------------------------------------------------------")
    # print(f"[SUMMARY] 共测试 {total} 个Lark items")
    # print(f"[SUMMARY] 匹配成功：{success_count} 个")
    # print(f"[SUMMARY] 匹配失败：{fail_count} 个")
    # print("------------------------------------------------------------")




# if __name__ == "__main__":
#     # 输入的 Name 列表
#     input_names = [
#         "SG-GST 9% Std Rate",
#         "TX-E33-SG",
#         "NR-SG",
#         "SG-GST 8% Purchase"  # 示例中不存在的 Name
#     ]
    
#     # 获取对应的 Internal ID 和 Rate 列表
#     internal_ids, rates = mapping_taxcode(input_names)
    
#     print("Internal IDs:", internal_ids)
#     print("Rates:", rates)