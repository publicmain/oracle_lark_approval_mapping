from config import get_tenant_access_token,create_vendor_bill_in_netsuite
from instance import get_current_and_past_week_timestamps, get_approval_instance_ids
from approval_detail import extract_value, get_instance_details, extract_fromId
from field_internel_id import mapping_date, mapping_entity_subsidiary, mapping_giro_paid
from file_util import download_file_as_base64
from request_body import generate_request_body


ACCESS_TOKEN = "Bearer " + get_tenant_access_token()
APPROVAL_CODE_POLINKED = "2B77BB3F-5FCE-4FD1-9A17-834F06E2FFAE"
START_TIME, END_TIME = get_current_and_past_week_timestamps()

# 获取审批实例 ID 列表
instance_ids = get_approval_instance_ids(
    access_token=ACCESS_TOKEN,
    approval_code=APPROVAL_CODE_POLINKED,
    start_time=START_TIME,
    end_time=END_TIME
)
for instance_id in instance_ids:
    if instance_id == "F0D8B55F-01DD-49E2-99BF-5269565C7F4B":
        instance_response = get_instance_details(instance_id)
        Entity = extract_value(instance_response, "Entity")
        duedate = extract_value(instance_response, "Due Date")
        Giro_paid = extract_value(instance_response, "Giro Pay / Paid")
        trandate = extract_value(instance_response, "Date of Invoice")
        Serial_Number = extract_value(instance_response, "Serial no.")
        Attachment = extract_value(instance_response, "Attachments")

        subsidiary_id = mapping_entity_subsidiary(Entity)
        duedate= mapping_date(duedate)
        trandate = mapping_date(trandate)
        giro_paid = mapping_giro_paid(Giro_paid)
        print("giro_paid:", giro_paid)

        attachment_info = []
        if Attachment:
            attachment_urls = Attachment if isinstance(Attachment, list) else [Attachment]
            for attachment_url in attachment_urls:
                base64_attachment, filename, file_extension, _ = download_file_as_base64(attachment_url)
                if base64_attachment:
                    if not file_extension:
                        file_extension = filename.split('.')[-1] if '.' in filename else 'txt'
                    attachment_item = {
                        "type": file_extension,
                        "title": filename,
                        "encodeData": base64_attachment
                    }
                    attachment_info.append(attachment_item)
        
        request_body_bill = generate_request_body(instance_response,"polinkedbill")
        PO_insance = extract_value(instance_response, "PO Approval")
        # print("PO_insance:", PO_insance[0])
        instance_response = get_instance_details(PO_insance[0])
        request_body = generate_request_body(instance_response,"po")
        if request_body is None:
            continue
        response = create_vendor_bill_in_netsuite(request_body)
        fromId = extract_fromId(response)
        # print(fromId)
        request_body = {
            "posttype": "polinkedbill",
            "fromId": fromId,
            "duedate": duedate,
            # "approvalstatus": "2",
            # "customform": "171",,
            "custbody_document_date": trandate,
            # "tranid":"for_testing(ignore)"+str(Serial_Number),
            "tranid":"for_testing(ignore)"+str(Serial_Number)+"2",
            "custbody7": 6637,
            "custbody_giropaidorpaid": giro_paid,
            "attachment": attachment_info
        }
        response = create_vendor_bill_in_netsuite(request_body)
        print(response)
        


        
        