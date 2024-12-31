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
        client_key='22f7e356baa824586ad25ba0711d49a7e676233a6d972ee6c59c6a18c824285c',
        client_secret='85c540c74f8c08f629a4613b64060628b9757453404e095c66d47e4bb21a85f6',
        resource_owner_key='6db9953acfe25bf63bfa4335a538b3ec3568a4b39e593992c8bc5c0596f26335',
        resource_owner_secret='25f4ddd48d549925b1371f823016cab188e5be8f8175cb16356f19c4c50b741e',
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
        client_key='22f7e356baa824586ad25ba0711d49a7e676233a6d972ee6c59c6a18c824285c',
        client_secret='85c540c74f8c08f629a4613b64060628b9757453404e095c66d47e4bb21a85f6',
        resource_owner_key='6db9953acfe25bf63bfa4335a538b3ec3568a4b39e593992c8bc5c0596f26335',
        resource_owner_secret='25f4ddd48d549925b1371f823016cab188e5be8f8175cb16356f19c4c50b741e',
        realm='6227405',
        signature_method='HMAC-SHA256',
        signature_type='auth_header'
    )
    NETSUITE_RESTLET_URL = "https://6227405.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=2979&deploy=1"
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