import requests
from requests_oauthlib import OAuth1
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
query_payload = {
    "q": "SELECT id, entityid, companyname FROM vendor ORDER BY id"
}

def create_vendor_bill_in_netsuite(request_body):
    oauth = OAuth1(
        client_key='c562603650f92936a15174b910d95837bf7184922c717846b84521c8bcf16ccd',
        client_secret='61945f0ac123e3bec725c8d30319926e612f32c2bbac96bfeb566826380e18c1',
        resource_owner_key='aa01830becaddba8834618b250b190414d812c55167e3ae33351646920458804',
        resource_owner_secret='85663e84d1f32c8bcab37b52a9c6c8ca6a60ab03600410448c0a960aacb1fe4b',
        realm='6227405',
        signature_method='HMAC-SHA256',
        signature_type='auth_header'
    )
    NETSUITE_RESTLET_URL = "https://6227405.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=2953&deploy=1"
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(NETSUITE_RESTLET_URL, headers=headers, json=request_body, auth=oauth)
        if response.status_code == 200:
            # print("instance created successfully.")
            # print("Response data:", response.json())
            return response.json()
        else:
            # print(f"Failed to create instance. Status code: {response.status_code}")
            # print("Response:", response.text)
            return {"error": response.text, "status_code": response.status_code}
    except Exception as e:
        # print(f"Exception occurred during API call: {e}")
        return {"error": str(e)}