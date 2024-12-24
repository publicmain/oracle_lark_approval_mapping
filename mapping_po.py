from config import get_tenant_access_token,create_vendor_bill_in_netsuite
from instance import get_current_and_past_week_timestamps, get_approval_instance_ids
from approval_detail import get_instance_details, extract_fromId
from request_body import generate_request_body



ACCESS_TOKEN = "Bearer " + get_tenant_access_token()
APPROVAL_CODE_PO = "A80CFB80-46EC-40BA-9CB2-AE9F26C9AB07"
APPROVAL_CODE_POLINKED = "2B77BB3F-5FCE-4FD1-9A17-834F06E2FFAE"
START_TIME, END_TIME = get_current_and_past_week_timestamps()

# 获取审批实例 ID 列表
instance_ids = get_approval_instance_ids(
    access_token=ACCESS_TOKEN,
    approval_code=APPROVAL_CODE_PO,
    start_time=START_TIME,
    end_time=END_TIME
)
# print("instance_ids:", instance_ids)
for instance_id in instance_ids:
    # if instance_id == "500A0B09-E31D-4CA9-8D98-66EB5306D9B2":
        instance_response = get_instance_details(instance_id)
        print(instance_id)
        request_body = generate_request_body(instance_response, "po")
        if request_body is None:
            continue
        response = create_vendor_bill_in_netsuite(request_body)
        print(response)
        fromId = extract_fromId(response)
        print(fromId)
        
                                                                         
        
        print("------------------------------------------------------------")
