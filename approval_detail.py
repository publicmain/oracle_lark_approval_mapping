import requests
import json
import os
from config import get_tenant_access_token
from datetime import datetime, timezone
def get_instance_details(instance):
    base_url = "https://open.larksuite.com"  
    endpoint = "/open-apis/approval/v4/instances/{instance}"
    url = base_url + endpoint.format(instance=instance)

 
    headers = {
        "Authorization": "Bearer "+get_tenant_access_token()  
    }


    response = requests.get(url, headers=headers)
    if response.status_code == 200:
       return response
    else:

        return response.text
response = get_instance_details("509EC1B1-D194-4F7D-93DA-AA1CB95C17C1").json()
# print(response)


def extract_details(response):
    details = extract_value(response, 'Details')
    if not details:
        #print("未找到 'Details' 信息")
        return
    
    details_list = []
    for detail_idx, detail in enumerate(details, 1):
        if not isinstance(detail, list):
            #print(f"跳过非列表的 detail[{detail_idx}]: {detail}")
            continue
        detail_dict = {}
        for field in detail:
            if not isinstance(field, dict):
                #print(f"跳过非字典的 field: {field}")
                continue
            field_name = field.get('name')
            field_value = field.get('value')
            if field_name:
                detail_dict[field_name] = field_value
        details_list.append(detail_dict)
    
    return details_list
def extract_currency_details(response):

    details = extract_value(response, 'Details')
    if not details:
        #print("未找到 'Details' 信息")
        return

    currency_list = []
    for detail_idx, detail in enumerate(details, 1):
        if not isinstance(detail, list):
            #print(f"跳过非列表的 detail[{detail_idx}]: {detail}")
            continue
        currency_dict = {}
        for field in detail:
            if not isinstance(field, dict):
                #print(f"跳过非字典的 field: {field}")
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
    details = extract_value(response, 'Details')
    if not details:
        #print("未找到 'Details' 信息")
        return
    
    details_list = []
    for detail_idx, detail in enumerate(details, 1):
        if not isinstance(detail, list):
            #print(f"跳过非列表的 detail[{detail_idx}]: {detail}")
            continue
        detail_dict = {}
        for field in detail:
            if not isinstance(field, dict):
                #print(f"跳过非字典的 field: {field}")
                continue
            field_name = field.get('name')
            field_value = field.get('value')
            if field_name:
                detail_dict[field_name] = field_value
        details_list.append(detail_dict)
    
    return details_list


def extract_attachment_ext_names(response):
    """
    提取 JSON 中 'Attachments' 字段的 'ext' 值，按逗号分割并去除文件后缀，返回文件名列表。
    
    参数:
        response (requests.Response): 包含 JSON 数据的响应对象。
    
    返回:
        list 或 None: 文件名列表或在出错时返回 None。
    """
    if response:
        try:
            data = response.json()
            form = data.get('data', {}).get('form', [])
            

            if isinstance(form, str):
                try:
                    form = json.loads(form)
                except json.JSONDecodeError as e:
                    #print(f"解析 'form' 字段时出错: {e}")
                    return None
            elif not isinstance(form, list):
                #print(f"未知的 'form' 字段类型: {type(form)}")
                return None

            for item in form:
                if isinstance(item, dict) and item.get('name') == 'Attachments':
                    ext_str = item.get('ext')
                    if not ext_str:
                        #print("未找到 'ext' 字段或其值为空。")
                        return None
                    
            
                    ext_list = ext_str.split(',')
                    
                   
                    names = [os.path.splitext(name)[0] for name in ext_list]
                    return names
            
            #print("未找到 'Attachments' 字段。")
            return None
        
        except json.JSONDecodeError as e:
            #print(f"响应不是有效的 JSON: {e}")
            return None
        except Exception as e:
            #print(f"发生错误: {e}")
            return None
    else:
        #print("响应为空。")
        return None
    
def extract_value(response,name):
    if response:
        try:
            data = response.json()
            form = data.get('data', {}).get('form', [])
            if isinstance(form, str):
                try:
                    form = json.loads(form)
                except json.JSONDecodeError as e:
                    #print(f"解析 'form' 字段时出错: {e}")
                    return None
            elif isinstance(form, list):
                pass 
            else:
                #print(f"未知的 'form' 字段类型: {type(form)}")
                return None
            for item in form:
                if isinstance(item, dict) and item.get('name') == name:
                    return item.get('value')
            #print("未找到"+str(name)+"字段。")
            return None
        except requests.exceptions.JSONDecodeError as e:
            #print(f"响应不是有效的 JSON: {e}")
            return None
        except Exception as e:
            #print(f"发生错误: {e}")
            return None
        

        except requests.exceptions.JSONDecodeError as e:
            #print(f"响应不是有效的 JSON: {e}")
            return None
        except Exception as e:
            #print(f"发生错误: {e}")
            return None
    else:
        #print("未找到 "+str(response)+"字段")
        return None
def extract_end_time(response):
    """
    从实例详情中提取最顶层的 'end_time' 字段。

    :param instance: 实例ID
    :return: 'end_time' 的值（str）或错误信息
    """
    if isinstance(response, requests.Response):
        data = response.json()
        end_time = data['data']['end_time']
        return end_time
    else:
        return None
def extract_fromId(response):

    if isinstance(response, dict) and 'id' in response:
        id_value = response['id']
        
        # 确保 id 是非空字符串，并且包含 '+'
        if isinstance(id_value, str) and '+' in id_value:
            id_value = id_value.split('+')[0]
            return id_value
        else:
            return None 
    else:
        #print("response 不是有效的字典，或者没有 'id' 字段")
        return None
    
def get_details_list(name,details_list):
    if details_list is None:
        return []
    result = []
    for idx, detail in enumerate(details_list, 1):
        result.append(detail.get(name))
    return result
def get_details_list_currency(name,details_list):
    result = []
    for idx, detail in enumerate(details_list, 1):
        result.append(detail.get(name))
    return result