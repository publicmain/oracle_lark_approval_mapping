import requests
import time
from typing import List
from config import get_tenant_access_token
from config import base_url,oauth,headers
from typing import Optional
def fetch_purchase_orders_paged(batch_size: int = 1000) -> List[dict]:
    """
    从 transaction 表中分批次获取 type 为 'PurchOrd' 的 id 和 tranid，并合并返回。

    参数:
        batch_size (int): 每次请求获取的记录数。默认值为 1000。

    返回:
        List[dict]: 包含所有符合条件的记录。
    """
    all_items = []
    last_id = 0
    has_more = True
    table_name = "transaction"
    columns = "id, tranid"
    order_by = "id"

    while has_more:
        query = f"""
        SELECT {columns}
        FROM {table_name}
        WHERE type = 'PurchOrd' AND id > {last_id}
        ORDER BY {order_by}
        FETCH NEXT {batch_size} ROWS ONLY
        """
        try:
            response = requests.post(
                base_url,
                headers=headers,
                json={"q": query},
                auth=oauth
            )
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            all_items.extend(items)

            print(f"Fetched {len(items)} purchase orders. Total so far: {len(all_items)}")

            if len(items) < batch_size:
                has_more = False
            else:
                # 假设id是整数类型
                last_id = max(item["id"] for item in items)

            time.sleep(0.1)  # 防止请求过于频繁

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break
        except ValueError as ve:
            print(f"JSON decode failed: {ve}")
            break
        except KeyError as ke:
            print(f"Missing expected key in response: {ke}")
            break

    return all_items
from typing import List, Optional

def find_id_by_tranid(tranid: str, transactions: List[dict]) -> Optional[int]:
    """
    在给定的交易列表中精确匹配tranid，并返回对应的id。

    参数:
        tranid (str): 要匹配的tranid值。
        transactions (List[dict]): 包含交易记录的列表，每个记录是一个字典。

    返回:
        Optional[int]: 如果找到匹配的tranid，返回对应的id；否则，返回None。
    """
    for transaction in transactions:
        if transaction.get('tranid') == tranid:
            return transaction.get('id')
    return None

# 示例用法
if __name__ == "__main__":
    # 假设已经获取到所有采购订单
    purchase_orders = fetch_purchase_orders_paged(batch_size=1000)
    
    # 要查找的tranid
    target_tranid = "PR20241224000600"
    
    # 查找对应的id
    matched_id = find_id_by_tranid(target_tranid, purchase_orders)
    
    if matched_id is not None:
        print(f"找到tranid '{target_tranid}' 对应的id: {matched_id}")
    else:
        print(f"未找到tranid '{target_tranid}' 对应的id。")