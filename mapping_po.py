import requests
import json
from config import get_tenant_access_token
from instance import get_current_and_past_week_timestamps, get_approval_instance_ids
from approval_detail import get_details_list, extract_details, extract_value, get_instance_details, extract_currency_details
from field_internel_id import (mapping_date, mapping_entity_subsidiary, mapping_GL_Account, mapping_Vendor,
                               mapping_division, mapping_postperiod, mapping_business, mapping_product_code,
                               mapping_product_type, mapping_project_code, mapping_scheme, mapping_currency)
from file_util import download_file_as_base64
from requests_oauthlib import OAuth1
from datetime import datetime

def create_po_in_netsuite(request_body):
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
    response = requests.post(NETSUITE_RESTLET_URL, headers=headers, json=request_body, auth=oauth)
    if response.status_code == 200:
        print("PO created successfully.")
        print("Response data:", response.json())
    else:
        print(f"Failed to create PO. Status code: {response.status_code}")
        print("Response:", response.text)

def convert_date_to_ddmmyyyy(date_str):
    # 假设mapping_date返回"YYYY-MM-DD"格式，这里转为"dd/mm/yyyy"
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%d/%m/%Y")

ACCESS_TOKEN = "Bearer " + get_tenant_access_token()
APPROVAL_CODE = "A80CFB80-46EC-40BA-9CB2-AE9F26C9AB07"
START_TIME, END_TIME = get_current_and_past_week_timestamps()

# 获取审批实例 ID 列表
instance_ids = get_approval_instance_ids(
    access_token=ACCESS_TOKEN,
    approval_code=APPROVAL_CODE,
    start_time=START_TIME,
    end_time=END_TIME
)

for instance_id in instance_ids:
    # 获取审批实例详细信息
    instance_response = get_instance_details(instance_id)

    # 提取字段值（根据实际字段名称与业务逻辑调整）
    Entity = extract_value(instance_response, "Entity")
    Vendor = extract_value(instance_response, "Vendor").split()[0]
    Invoice_number = extract_value(instance_response, "Invoice Number")
    Date_of_Invoice = extract_value(instance_response, "Transaction date")
    Due_Date = extract_value(instance_response, "Due Date")
    details_list = extract_details(instance_response)
    details_list_currency = extract_currency_details(instance_response)
    Attachment = extract_value(instance_response, "Attachments")
    GL_Account = get_details_list("GL Account", details_list)
    Division_Code = get_details_list("Division Code", details_list)
    Description = get_details_list("Description", details_list)
    Currency = get_details_list("Unit Price", details_list_currency)
    Business = get_details_list("Business", details_list)
    Scheme = get_details_list("Scheme", details_list)
    Product_Type = get_details_list("Product Type", details_list)
    Product_Code = get_details_list("Product Code", details_list)
    Project_Code = get_details_list("Project Code", details_list)
    Unit_Price = get_details_list("Unit Price", details_list)
    Amount_excl_GST = get_details_list("Amount(excl GST)", details_list)
    Amount_incl_GST = get_details_list("Amount (incl GST)", details_list)
    GST_Amount = get_details_list("GST Amount", details_list)
    Gst = get_details_list("GST?", details_list)

    print(instance_id)

    if Entity == "DFS Asset Purchase Company Pte Ltd":
        continue
    subsidiary_id = mapping_entity_subsidiary(Entity)
    vendor_id = mapping_Vendor(Vendor)
    # 对PO来说，可能不需要GL_Account作为item line的字段，这里依然映射但未使用
    gl_account_ids = mapping_GL_Account(GL_Account)
    trandate = mapping_date(Date_of_Invoice)  
    # trandate = convert_date_to_ddmmyyyy(trandate)
    # duedate = mapping_date(Due_Date) 
    # duedate = convert_date_to_ddmmyyyy(duedate)
    divisions = mapping_division(Division_Code)
    Business = mapping_business(Business)
    Scheme = mapping_scheme(Scheme)
    Product_Type = mapping_product_type(Product_Type)
    Product_Code = mapping_product_code(Product_Code) # 假定此函数返回item内部ID
    Project_Code = mapping_project_code(Project_Code)
    currency = mapping_currency(Currency)

    
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
                    # "encodeData": base64_attachment
                    "encodeData": "base64_attachment"
                }
                attachment_info.append(attachment_item)

    # 构建sublist - Item行
    sublist = []
    for i in range(len(details_list)):
        rate = float(Unit_Price[i]) if Unit_Price[i] else 0.0
        amount = float(Amount_excl_GST[i]) if Amount_excl_GST[i] else 0.0
        taxrate = "9%"
        taxamount = round(amount * 0.09, 2)
        grossamount = amount + taxamount

        # 假设数量为金额/单价
        quantity = 1
        if rate != 0:
            quantity = amount / rate

        item_line = {
            "sublistitemtype": "item",
            "item": str(Product_Code[i]),
            "description": Description[i],
            "department": str(divisions[i]),
            "quantity": str(quantity),
            "units": "1",
            "rate": str(rate),
            "amount": str(amount),
            "taxcode": "486",
            "taxrate": taxrate,
            "taxamount": str(taxamount),
            "grossamount": str(grossamount)
        }
        sublist.append(item_line)

    request_body = {
        "posttype": "po",
        "entity": str(vendor_id),
        "trandate": trandate,
        "tranid": instance_id + "xx",
        "subsidiary": str(subsidiary_id),
        "memo": "Generated PO from Lark Approval",
        "location": "2",  
        "currency": "1",  
        "exchangerate": "1",
        "sublist": sublist,
        "attachment": attachment_info
    }
    # 打印请求体
    print(json.dumps(request_body, indent=4))

    # create_po_in_netsuite(request_body)
    print("------------------------------------------------------------")
