from config import get_tenant_access_token,create_vendor_bill_in_netsuite
from instance import get_current_and_past_week_timestamps,get_approval_instance_ids
from approval_detail import get_instance_details
from request_body import generate_request_body

ACCESS_TOKEN = "Bearer "+get_tenant_access_token()
APPROVAL_CODE = "CF9A8C73-2873-4ABA-BF7D-144DD29D9598"
START_TIME, END_TIME = get_current_and_past_week_timestamps()

instance_ids = get_approval_instance_ids(
    access_token=ACCESS_TOKEN,
    approval_code=APPROVAL_CODE,
    start_time=START_TIME,
    end_time=END_TIME
)
# print("instance_ids:", instance_ids)
for instance_id in instance_ids:
    # if instance_id == "8F292381-5054-4F17-9424-C9D4CFFA596D":
    # 获取审批实例详细信息
        print(instance_id)
        instance_response = get_instance_details(instance_id)
        request_body = generate_request_body(instance_response, "bill")
        if request_body is None:
            continue
        response = create_vendor_bill_in_netsuite(request_body)
        print("------------------------------------------------------------")
        