import pandas as pd
from datetime import datetime
import re
from difflib import get_close_matches
# 读取供应商和科目的映射关系
vendor_file_path = 'vendor.csv' 
gl_account_file_path = 'glaccount.csv'
division_file_path = 'division.csv'
product_code_file_path = 'product_code.csv'
product_type_file_path = 'product_type.csv'
project_code_file_path = 'project_code.csv'
scheme_file_path = 'scheme.csv'
df_vendor = pd.read_csv(vendor_file_path)
df_product_code = pd.read_csv(product_code_file_path)
df_product_type = pd.read_csv(product_type_file_path)
df_project_code = pd.read_csv(project_code_file_path)
df_scheme = pd.read_csv(scheme_file_path)
df_GL = pd.read_csv(gl_account_file_path)
df_division = pd.read_csv(division_file_path)
vendor = df_vendor.set_index('Internal ID')['ID'].to_dict()
GL_account = df_GL.set_index('Internal ID')['Number'].to_dict()
division = df_division.set_index('Internal ID')['Name'].to_dict()
product_code_dict = df_product_code.set_index('Internal ID')['Name'].to_dict()
product_type_dict = df_product_type.set_index('Internal ID')['Name'].to_dict()
project_code_dict = df_project_code.set_index('Internal ID')['Name'].to_dict()
scheme_dict = df_scheme.set_index('Internal ID')['Name'].to_dict()
business = {
    "Acquiring" : 2,
    "Issuing" : 3
}
subsidiary = {
    "Singapore Entity": 15,
    "CANDYPAY HOLDINGS PTE LTD": 16,
    "DCS FINTECH HOLDINGS PTE LTD.": 1,
    "DCS CARD CENTRE PTE LTD": 2,
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
currency_dict = {
    1: "SGD",
    2: "USD",
    4: "EUR",
    5: "GBP",
    6: "AUD",
    7: "JPY",
    8: "CNY",
    9: "INR",
    10: "HKD",
    11: "MYR"
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

# 映射 Vendor
def mapping_Vendor(Vendor):
    name = str(Vendor).split()[0]
    for key, value in vendor.items():
        if name in value:
            return key
    return None
def mapping_currency(currency):
    for key, value in currency_dict.items():
        if currency[0] in value:
            return key
    return None

# 映射 GL Account
def mapping_GL_Account(GL_Account):
    result = []
    for account in GL_Account:
        if isinstance(account, (str, int, float)):
            name = str(account).split()[0]
            result.append(name)
        else:
            result.append(None)
    Key = []
    for i in result:
        if i is None:
            Key.append(None)
            continue
        found = False  
        for key, value in GL_account.items():
            if isinstance(value, str) and i in value:
                Key.append(key)
                found = True
                break  
        if not found:
            Key.append(None) 
    return Key

def mapping_division(division_codes):
    """
    从输入字符串列表中提取代码，并在字典中查找对应的键。
    
    :param division_codes: 输入的字符串列表，例如 ['80110 Mgmt Accounting & Reporting', ...]
    :param division_dict: 要搜索的字典
    :return: 对应的键的列表，如果未找到则为 None
    """
    mapped_keys = []
    
    for division_code in division_codes:
        # 去除前后空白字符
        trimmed_str = division_code.strip()
        
        # 初始化代码变量
        code = ''
        
        # 遍历字符串字符，提取开头的数字部分
        for char in trimmed_str:
            if char.isdigit():
                code += char
            else:
                break
        
        if not code:
            mapped_keys.append(None)
            continue
        
        # 遍历字典查找值以提取的代码开头的项
        key_found = None
        for key, value in division.items():
            if value.startswith(code):
                key_found = key
                break
        mapped_keys.append(key_found)
    
    return mapped_keys

# 映射日期格式
def mapping_date(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    formatted_date = date_obj.strftime("%d/%m/%Y")
    return formatted_date

from datetime import datetime

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

def mapping_business(business_list):
    mapped_list = []
    for business_name in business_list:
        value = business.get(str(business_name))
        mapped_list.append(value)
    return mapped_list


def mapping_product_code(product_codes):
    Key = []
    for i in product_codes:
        if i is None:
            Key.append(None)
            continue
        found = False  
        for key, value in product_code_dict.items():
            if isinstance(value, str) and i in value:
                Key.append(key)
                found = True  
                break  
        if not found:
            Key.append(None) 
    return Key
    

def mapping_product_type(product_types):
    Key = []
    for p_type in product_types:
        found = False
        if isinstance(p_type, (str, int, float)):
            name = str(p_type).strip()
            for internal_id, full_name in product_type_dict.items():
                if isinstance(full_name, str) and full_name.endswith(name):
                    Key.append(internal_id)
                    found = True
                    break
        if not found:
            Key.append(None)
    return Key


def mapping_project_code(project_codes):
    Key = []
    for code in project_codes:
        found = False
        if isinstance(code, (str, int, float)):
            name = str(code).strip()
            for internal_id, full_name in project_code_dict.items():
                if full_name.endswith(name):
                    Key.append(internal_id)
                    found = True
                    break
        if not found:
            Key.append(None)
    return Key



def mapping_scheme(scheme_list):
    Key = []
    for scheme in scheme_list:
        found = False
        if isinstance(scheme, (str, int, float)):
            name = str(scheme).strip()
            for internal_id,full_name in scheme_dict.items():
                if full_name.endswith(name):
                    Key.append(internal_id)
                    found = True
                    break
        if not found:
            Key.append(None)
    return Key

