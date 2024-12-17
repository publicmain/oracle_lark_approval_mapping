import requests
import json
from config import get_tenant_access_token
from instance import get_current_and_past_week_timestamps,get_approval_instance_ids
from approval_detail import get_details_list,extract_details,extract_value,get_instance_details,extract_currency_details
from field_internel_id import mapping_date,mapping_entity_subsidiary,mapping_GL_Account,mapping_Vendor,mapping_division,mapping_postperiod,mapping_business,mapping_product_code,mapping_product_type,mapping_project_code,mapping_scheme,mapping_currency
from file_util import download_file_as_base64
from requests_oauthlib import OAuth1
# 构建请求体并发送请求
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
    NETSUITE_RESTLET_URL = "https://6227405.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=2954&deploy=2"
    headers = {
        "Content-Type": "application/json"
    }
    # response = requests.post(NETSUITE_RESTLET_URL, headers=headers, json=request_body, auth=oauth)
    # if response.status_code == 200:
    #     print("Vendor Bill created successfully.")
    #     print("Response data:", response.json())
    # else:
    #     print(f"Failed to create Vendor Bill. Status code: {response.status_code}")
    #     print("Response:", response.text)

ACCESS_TOKEN = "Bearer "+get_tenant_access_token()
APPROVAL_CODE = "CF9A8C73-2873-4ABA-BF7D-144DD29D9598"
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
    # instance_response = ["3D7FDD6E-FCE4-4A62-8532-4B9E75FFD4B3"]
    # 提取字段值
    Entity = extract_value(instance_response, "Entity")
    Vendor = extract_value(instance_response, "Vendor").split()[0]
    Invoice_number = extract_value(instance_response, "Invoice Number")
    Date_of_Invoice = extract_value(instance_response, "Date of Invoice")
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
    # if instance_id == "07303D5E-4E50-476E-9737-B59FD99F79E9":
    # print("Amount_incl_GST:", Amount_incl_GST)
    # print("Amount_excl_GST:", Amount_excl_GST)
    # print("instance_id:", instance_id)
    # print("Entity:", Entity)
    # print("Vendor:", Vendor)
    # print("Invoice Number:", Invoice_number)
    # print("Date of Invoice:", Date_of_Invoice)
    # print("Due Date:", Due_Date)
    # print("Details:")
    # print("Attachment:", Attachment)
    # print("GL Account:", GL_Account)
    # print("Division Code:", Division_Code)
    # print("Description:", Description)
    # print("Business:", Business)
    # print("class:", Product_Code)
    # print("Scheme:", Scheme)
    # print("Product Type:", Product_Type)
    # print("Product Code:", Product_Code)
    # print("Project Code:", Project_Code)
    # print("Unit Price:", Unit_Price)
    # print("GST:", Gst)
    # print("Amount (excl GST):", Amount_excl_GST)
    # print("Amount (incl GST):", Amount_incl_GST)
    # print("GST Amount:", GST_Amount)
    # print("currency:", Currency)
        # 映射字段
    if Entity == "DFS Asset Purchase Company Pte Ltd":
        continue
    subsidiary_id = mapping_entity_subsidiary(Entity)
    vendor_id = mapping_Vendor(Vendor)
    #print(vendor_id)
    # break
    gl_account_ids = mapping_GL_Account(GL_Account)
    #print("gl_account_ids",gl_account_ids)
    trandate = mapping_date(Date_of_Invoice)
    # location = mapping_Location()
    duedate = mapping_date(Due_Date)
    Date_of_Invoice = mapping_date(Date_of_Invoice)
    print(Date_of_Invoice)
    divisions = mapping_division(Division_Code)
    #print("divisions",divisions)
    Business = mapping_business(Business)
    #print("Business",Business)
    Scheme = mapping_scheme(Scheme)
    #print("Scheme",Scheme)
    Product_Type = mapping_product_type(Product_Type)
    #print("product type", Product_Type)
    Product_Code = mapping_product_code(Product_Code)
    #print("Product_Code",Product_Code)
    Project_Code = mapping_project_code(Project_Code)
    #print("Project_Code",Project_Code)
    currency = mapping_currency(Currency)
    # print("currency",currency)
    # print("------------------------------------------------------------")
    # print(currency)
    # print(subsidiary_id)
    # print(vendor_id)
    # print(gl_account_ids)
    # print(trandate)
    # print(duedate)
    # # 处理附件
    files_info = []
    if Attachment:
        attachment_urls = Attachment if isinstance(Attachment, list) else [Attachment]

        for attachment_url in attachment_urls:
            base64_attachment, filename, _, _ = download_file_as_base64(attachment_url)
            if base64_attachment:
                file_info = {
                            "name": filename,
                            "contents": base64_attachment,
                            "folder": 11944,
                            # "file_extension": file_extension,
                            # "mime_type": mime_type
                        }
                files_info.append(file_info)
            else:
                files_info = files_info
    # print(files_info)
    # print(files_info)
    # 构建明细行
    expenses = []
    for i in range(len(details_list)):
        expense_line = {
            "account": gl_account_ids[i],
            "amount": Amount_excl_GST[i],
            "memo": Description[i],
            "department": divisions[i],
            # "class": Business[i],
            "taxcode":486,
            "location": 6,  
            "custcol_4601_witaxapplies": False,
            "cseg_business": Business[i],   
            "cseg_product": "1",
            "cseg_scheme": Scheme[i],
            "cseg_pr_type": Product_Type[i],
            "class": Product_Code[i],
            "cseg1": Project_Code[i]
        }
        expenses.append(expense_line)
        # print(expense_line)


        # 构建请求体
        request_body = {
            "tranDate": trandate,
            "dueDate": duedate,
            "entity": vendor_id,
            "subsidiary": subsidiary_id,
            "memo": "Generated from Lark Approval",
            # "approvalstatus": "2",
            # "customform": "171",
            "exchangeRate": 1.0,
            # "account": "694",
            "location": "6",
            # "custbody4": False,
            # "currency": currency,
            # "custbody5": False,
            # "custbody6": False,
            # "custbody7": "3",
            # "custbody_4601_entitytype": "1",
            # "custbody_atlas_no_hdn": "2",
            # "custbody_atlas_yes_hdn": "1",
            # "custbody_cash_register": False,
            # "custbody_approval_delegate": "4747",
            "custbody_document_date": Date_of_Invoice,
            # "custbody_edoc_gen_trans_pdf": False,
            # "custbody_ei_ds_txn_identifier": False,
            # "custbody_level1": "3",
            # "custbody_nondeductible_processed": False,
            "tranid": instance_id+"xx",
            # "billaddress": "6 MANDAI LINK\nSingapore 728652",
            # "terms": "13",
            "custbody_stc_amount_after_discount": 3600.0,
            "custbody_stc_tax_after_discount": 288.0,
            "custbody_stc_total_after_discount": 3888.0,
            "expenses": expenses,
            "files": files_info
        }
        
        # 发送请求创建 Vendor Bill
        # print(request_body)
    create_vendor_bill_in_netsuite(request_body)
    print("------------------------------------------------------------")

