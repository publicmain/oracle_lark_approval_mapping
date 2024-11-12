import requests
app_id = "cli_a6b7352c1078502f"
app_secret = "cU1Red6loKSXkZ1iNje2CcNKnSXLs5tL"
def get_tenant_access_token():
    url = "https://open-sg.larksuite.com/open-apis/auth/v3/tenant_access_token/internal"
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            return data["tenant_access_token"]
        else:
            raise Exception(f"Error getting access token: {data['msg']}")
    else:
        raise Exception(f"HTTP request failed: {response.status_code}")