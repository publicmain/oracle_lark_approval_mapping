import requests
import json
from config import get_tenant_access_token
# Base URL and endpoint
base_url = "https://open.larksuite.com"  # Replace with actual base URL if applicable
endpoint = "/open-apis/approval/v4/instances/{instance_id}"

# Instance ID (replace with actual ID if necessary)
instance_id = "30533677-F13A-49B0-BAF0-0480F5CDC964"

# Complete URL with the path parameter
url = base_url + endpoint.format(instance_id=instance_id)

# Headers
headers = {
    "Authorization": "Bearer "+get_tenant_access_token()  # Replace with actual token as needed
}

# Making the GET request
response = requests.get(url, headers=headers)

# Handling the response
if response.status_code == 200:
    print("Response data:", response.json())
else:
    print(f"Request failed with status code {response.status_code}")
    print("Response:", response.text)

import requests
import json

def extract_value(response,name):
    try:
        # 使用 response.json() 解析整个响应
        data = response.json()
        
        # 获取 'form' 字段
        form = data.get('data', {}).get('form', [])

        # 检查 'form' 的类型
        if isinstance(form, str):
            try:
                # 如果 'form' 是字符串，尝试将其解析为 JSON 列表
                form = json.loads(form)
            except json.JSONDecodeError as e:
                print(f"解析 'form' 字段时出错: {e}")
                return None
        elif isinstance(form, list):
            pass  # 'form' 已经是列表，无需解析
        else:
            print(f"未知的 'form' 字段类型: {type(form)}")
            return None
        for item in form:
            if isinstance(item, dict) and item.get('name') == name:
                return item.get('value')
        
        # 如果未找到 'Entity' 字段
        print("未找到"+str(name)+"字段。")
        return None

    except requests.exceptions.JSONDecodeError as e:
        print(f"响应不是有效的 JSON: {e}")
        return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None

value = extract_value(response,"Invoice Number")
if value:
    print(f"value: {value}")
else:
    print("未能提取到 'value' 字段。")