import requests
import json
from config import get_tenant_access_token
# Base URL and endpoint
def get_instance_details(instance):
    base_url = "https://open.larksuite.com"  # Replace with actual base URL if applicable
    endpoint = "/open-apis/approval/v4/instances/{instance}"
    # Complete URL with the path parameter
    url = base_url + endpoint.format(instance=instance)

    # Headers
    headers = {
        "Authorization": "Bearer "+get_tenant_access_token()  # Replace with actual token as needed
    }

    # Making the GET request
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
       return response
    else:
        print(f"Request failed with status code {response.status_code}")
        return response.text
# print(get_instance_details("BF5EDFEA-EFD9-4C02-B4A3-79961C9B234F").json())

# Handling the response

def extract_details(response):
    # 使用 extract_value 函数提取 'Details' 字段的值
    details = extract_value(response, 'Details')
    if not details:
        print("未找到 'Details' 信息")
        return
    
    details_list = []
    for detail_idx, detail in enumerate(details, 1):
        if not isinstance(detail, list):
            print(f"跳过非列表的 detail[{detail_idx}]: {detail}")
            continue
        detail_dict = {}
        for field in detail:
            if not isinstance(field, dict):
                print(f"跳过非字典的 field: {field}")
                continue
            field_name = field.get('name')
            field_value = field.get('value')
            if field_name:
                detail_dict[field_name] = field_value
        details_list.append(detail_dict)
    
    return details_list
def extract_currency_details(response):
    # 使用 extract_value 函数提取 'Details' 字段的值
    details = extract_value(response, 'Details')
    if not details:
        print("未找到 'Details' 信息")
        return

    currency_list = []
    for detail_idx, detail in enumerate(details, 1):
        if not isinstance(detail, list):
            print(f"跳过非列表的 detail[{detail_idx}]: {detail}")
            continue
        currency_dict = {}
        for field in detail:
            if not isinstance(field, dict):
                print(f"跳过非字典的 field: {field}")
                continue
            field_name = field.get('name')
            field_ext = field.get('ext')
            if not isinstance(field_ext, dict):
                field_ext = {}
            currency = field_ext.get('currency')
            if field_name and currency:
                currency_dict[field_name] = currency
        if currency_dict:
            currency_list.append(currency_dict)

    return currency_list

def extract_details(response):
    # 使用 extract_value 函数提取 'Details' 字段的值
    details = extract_value(response, 'Details')
    if not details:
        print("未找到 'Details' 信息")
        return
    
    details_list = []
    for detail_idx, detail in enumerate(details, 1):
        if not isinstance(detail, list):
            print(f"跳过非列表的 detail[{detail_idx}]: {detail}")
            continue
        detail_dict = {}
        for field in detail:
            if not isinstance(field, dict):
                print(f"跳过非字典的 field: {field}")
                continue
            field_name = field.get('name')
            field_value = field.get('value')
            if field_name:
                detail_dict[field_name] = field_value
        details_list.append(detail_dict)
    
    return details_list

def print_details(details_list):
    if not details_list:
        print("没有可打印的 Details 信息。")
        return
    
    for idx, detail in enumerate(details_list, 1):
        print(f"Detail {idx}:")
        for key, value in detail.items():
            print(f"{key}: {value}")
        print("-" * 40)

def extract_value(response,name):
    try:
        data = response.json()
        form = data.get('data', {}).get('form', [])
        if isinstance(form, str):
            try:
                form = json.loads(form)
            except json.JSONDecodeError as e:
                print(f"解析 'form' 字段时出错: {e}")
                return None
        elif isinstance(form, list):
            pass 
        else:
            print(f"未知的 'form' 字段类型: {type(form)}")
            return None
        for item in form:
            if isinstance(item, dict) and item.get('name') == name:
                return item.get('value')
        print("未找到"+str(name)+"字段。")
        return None
    except requests.exceptions.JSONDecodeError as e:
        print(f"响应不是有效的 JSON: {e}")
        return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None
    

    except requests.exceptions.JSONDecodeError as e:
        print(f"响应不是有效的 JSON: {e}")
        return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None
    
def get_details_list(name,details_list):
    result = []
    for idx, detail in enumerate(details_list, 1):
        result.append(detail.get(name))
    return result
def get_details_list_currency(name,details_list):
    result = []
    for idx, detail in enumerate(details_list, 1):
        result.append(detail.get(name))
    return result