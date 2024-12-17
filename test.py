import requests
from requests_oauthlib import OAuth1
# 需要替换为您的数据：例如通过 OAuth2 获取的 token、URL、查询语句等
base_url = "https://6227405.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
oauth = OAuth1(
        client_key='c562603650f92936a15174b910d95837bf7184922c717846b84521c8bcf16ccd',
        client_secret='61945f0ac123e3bec725c8d30319926e612f32c2bbac96bfeb566826380e18c1',
        resource_owner_key='aa01830becaddba8834618b250b190414d812c55167e3ae33351646920458804',
        resource_owner_secret='85663e84d1f32c8bcab37b52a9c6c8ca6a60ab03600410448c0a960aacb1fe4b',
        realm='6227405',
        signature_method='HMAC-SHA256',
        signature_type='auth_header'
    )
headers = {
    "Content-Type": "application/json",
    "Prefer": "transient"
}
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
    在给定的items列表中，根据key字段进行匹配，target为要匹配的值。
    partial为True时，为包含匹配（不区分大小写）；否则为全字匹配（不区分大小写）。
    """
    target_lower = target.lower()
    if partial:
        return next((item for item in items if target_lower in item.get(key, "").lower()), None)
    else:
        return next((item for item in items if item.get(key, "").lower() == target_lower), None)
    

def mapping_GL_Account(target):
    all_accounts = fetch_all_items("account", columns="id, accountsearchdisplayname", order_by="id")
    matched = match_item(all_accounts, target, "accountsearchdisplayname", partial=False)
    if matched:
        return matched["id"]
    else:
        print(f"Account with name='{target}' not found.")
        return None
# 示例调用
print(mapping_GL_Account("70020001 Rebates Exp"))
