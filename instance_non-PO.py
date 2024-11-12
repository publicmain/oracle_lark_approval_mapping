import requests
import time
from typing import List, Optional
from datetime import datetime, timedelta
from config import get_tenant_access_token
API_URL = "https://open.larksuite.com/open-apis/approval/v4/instances"

def get_current_and_past_week_timestamps() -> tuple[int, int]:
    """
    获取当前时间和一周前的时间，转换为毫秒级时间戳。

    返回:
        Tuple[int, int]: (start_time, end_time)
    """
    end_time_dt = datetime.now()
    start_time_dt = end_time_dt - timedelta(weeks=1)
    START_TIME = int(start_time_dt.timestamp() * 1000)
    END_TIME = int(end_time_dt.timestamp() * 1000)

    return START_TIME, END_TIME

def get_approval_instance_ids(
    access_token: str,
    approval_code: str,
    start_time: int,
    end_time: int,
    page_size: int = 100
) -> List[str]:
    """
    根据 approval_code 批量获取审批实例的 instance_code。

    参数:
        access_token (str): 租户访问令牌，格式为 "Bearer access_token"。
        approval_code (str): 审批定义唯一标识。
        start_time (int): 审批实例创建时间区间的起始时间（毫秒）。
        end_time (int): 审批实例创建时间区间的结束时间（毫秒）。
        page_size (int, optional): 每页返回的审批实例数量。默认值为 100。

    返回:
        List[str]: 包含所有审批实例 ID 的列表。
    """
    headers = {
        "Authorization": access_token
    }

    params = {
        "approval_code": approval_code,
        "start_time": str(start_time),
        "end_time": str(end_time),
        "page_size": page_size
    }

    instance_codes = []
    page_token: Optional[str] = None
    has_more = True

    while has_more:
        if page_token:
            params["page_token"] = page_token
        else:
            params.pop("page_token", None) 

        try:
            response = requests.get(API_URL, headers=headers, params=params)
            response_data = response.json()

            if response_data.get("code") != 0:
                print(f"Error {response_data.get('code')}: {response_data.get('msg')}")
                break

            data = response_data.get("data", {})
            instance_code_list = data.get("instance_code_list", [])
            instance_codes.extend(instance_code_list)

            has_more = data.get("has_more", False)
            page_token = data.get("page_token", None)

            print(f"Fetched {len(instance_code_list)} instances. Total so far: {len(instance_codes)}")

            time.sleep(0.1)

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break

    return instance_codes

if __name__ == "__main__":
    ACCESS_TOKEN = "Bearer "+get_tenant_access_token()
    APPROVAL_CODE = "CF9A8C73-2873-4ABA-BF7D-144DD29D9598"
    START_TIME, END_TIME = get_current_and_past_week_timestamps()
    instance_ids = get_approval_instance_ids(
        access_token=ACCESS_TOKEN,
        approval_code=APPROVAL_CODE,
        start_time=START_TIME,
        end_time=END_TIME
    )

    print("\n所有审批实例 ID:")
    for idx, instance_id in enumerate(instance_ids, start=1):
        print(f"{idx}. {instance_id}")
