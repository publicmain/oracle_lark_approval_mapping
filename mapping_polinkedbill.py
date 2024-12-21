import requests
import json
from config import get_tenant_access_token
from instance import get_current_and_past_week_timestamps, get_approval_instance_ids
from approval_detail import get_details_list, extract_details, extract_value, get_instance_details, extract_currency_details
from field_internel_id import (mapping_date, mapping_entity_subsidiary, mapping_GL_Account, mapping_Vendor,
                               mapping_division, mapping_postperiod, mapping_business, mapping_product_code,
                               mapping_product_type, mapping_project_code, mapping_scheme, mapping_currency,mapping_item,mapping_taxcode,mapping_Location)
from file_util import download_file_as_base64
from requests_oauthlib import OAuth1
from datetime import datetime
from test import getPOid

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
        return response.json()
    else:
        print(f"Failed to create PO. Status code: {response.status_code}")
        print("Response:", response.text)
        return response.text

def convert_date_to_ddmmyyyy(date_str):
    # 假设mapping_date返回"YYYY-MM-DD"格式，这里转为"dd/mm/yyyy"
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%d/%m/%Y")

def conditional_map(value, mapping_func):
        # 如果 value 存在且第一个元素非空（或按业务逻辑判断非空条件）
            return mapping_func(value) if value else value

ACCESS_TOKEN = "Bearer " + get_tenant_access_token()
APPROVAL_CODE_PO = "A80CFB80-46EC-40BA-9CB2-AE9F26C9AB07"
APPROVAL_CODE_POLINKED = "2B77BB3F-5FCE-4FD1-9A17-834F06E2FFAE"
START_TIME, END_TIME = get_current_and_past_week_timestamps()

# 获取审批实例 ID 列表
instance_ids = get_approval_instance_ids(
    access_token=ACCESS_TOKEN,
    approval_code=APPROVAL_CODE_POLINKED,
    start_time=START_TIME,
    end_time=END_TIME
)
# print("instance_ids:", instance_ids)
for instance_id in instance_ids:
    # 获取审批实例详细信息
    # if instance_id == "0F7F8A26-873A-4054-8A4F-E26DA7B40FD4":
        instance_response = get_instance_details(instance_id)
        print(instance_id)
        # 提取字段值（根据实际字段名称与业务逻辑调整）
        PO_insance = extract_value(instance_response, "PO Approval")
        print("PO_insance:", PO_insance)
        fromId = getPOid(PO_insance[0])
        print(fromId)
        # PO_instance_response = get_instance_details(instance_id)
        # Serial_Number = extract_value(PO_instance_response, "Serial no.")
        # Entity = extract_value(PO_instance_response, "Entity")
        # Vendor = extract_value(PO_instance_response, "Vendor")
        # # Invoice_number = extract_value(PO_instance_response, "Invoice Number")
        # Date_of_Invoice = extract_value(PO_instance_response, "Transaction date")
        # Currency = extract_value(PO_instance_response, "Currency")
        # exchange_rate = extract_value(PO_instance_response, "Exchange rate")
        # Location = extract_value(PO_instance_response, "Location")
        # memo = extract_value(PO_instance_response, "Memo")
        # #print("exchange_rate:", exchange_rate)
        # # Due_Date = extract_value(PO_instance_response, "Due Date")
        # transaction_date = extract_value(PO_instance_response, "Transaction date")
        # details_list = extract_details(PO_instance_response)
        # details_list_currency = extract_currency_details(PO_instance_response)
        # Attachment = extract_value(PO_instance_response, "Attachments")
        # GL_Account = get_details_list("GL Account", details_list)
        # Division_Code = get_details_list("Division Code", details_list)
        # # print("original Division_Code:", Division_Code)
        # Description = get_details_list("Description", details_list)
        # # Currency = get_details_list("Unit Price", details_list_currency)
        # Business = get_details_list("Business", details_list)
        # print("original Business:", Business)
        # Scheme = get_details_list("Scheme", details_list)
        # Product_Type = get_details_list("Product Type", details_list)
        # Product_Code = get_details_list("Product Code", details_list)
        # # print("origiinal Product_Code:", Product_Code)
        # Project_Code = get_details_list("Project Code", details_list)
        # print("original Project_Code:", Project_Code)
        # Unit_Price = get_details_list("Unit Price", details_list)
        # Amount_excl_GST = get_details_list("Amount (excl GST)", details_list)
        # # print("Amount_excl_GST:", Amount_excl_GST)
        # Amount_incl_GST = get_details_list("Amount (incl GST)", details_list)
        # GST_Amount = get_details_list("GST Amount", details_list)
        # Gst = get_details_list("GST?", details_list)
        # items = get_details_list("Inventory Item", details_list)
        # quantities = get_details_list("Quantity", details_list)
        # taxcodes = get_details_list("GST?", details_list)
        # item_amounts = get_details_list("Item Amount(excl GST)", details_list)
        # expense_amounts = get_details_list("Expense Amount(excl GST)", details_list)
        # unit_prices = get_details_list("Unit Price", details_list)
        # #print("original taxcodes:", taxcodes)
        # # print("orginal items:", items)
        # # print("item_amounts:", item_amounts)
        # # print("expense_amounts:", expense_amounts)

        

        # if Entity == "DFS Asset Purchase Company Pte Ltd" or Entity == "SHANGHAI DALAI":
        #     continue
        # subsidiary_id = mapping_entity_subsidiary(Entity)
        # if Vendor:
        #     vendor_id = mapping_Vendor(Vendor) 
        # else:
        #      print("Vendor is empty")
        #      print("------------------------------------------------------------")
        #      continue
        # if memo:
        #     memo = memo
        # else:
        #     memo = "Generated by Lark"
        # gl_account_ids = conditional_map(GL_Account, mapping_GL_Account)
        # # print("gl_account_ids:", gl_account_ids)
        # trandate = mapping_date(Date_of_Invoice)  # 无条件映射
        # transaction_date = mapping_date(transaction_date)
        # location = mapping_Location(Location) if Location else "2"
        # divisions = conditional_map(Division_Code, mapping_division)
        # # print("divisions:", divisions)
        # Business = conditional_map(Business, mapping_business)
        # Scheme = conditional_map(Scheme, mapping_scheme)
        # # print("original Scheme:", Scheme)
        # Product_Type = conditional_map(Product_Type,mapping_product_type)  # 无条件映射
        # Product_Code = conditional_map(Product_Code, mapping_product_code)
        # Project_Code = conditional_map(Project_Code, mapping_project_code)
        # currency = conditional_map(Currency, mapping_currency)
        # # print("currency:", currency)
        # items = conditional_map(items,mapping_item)
        # taxcodes, rates = mapping_taxcode(taxcodes)
        # # print("taxcodes:", taxcodes)
        # # print("rates:", rates)
        # # print("items:", items)

        
        # attachment_info = []
        # if Attachment:
        #     attachment_urls = Attachment if isinstance(Attachment, list) else [Attachment]
        #     for attachment_url in attachment_urls:
        #         base64_attachment, filename, file_extension, _ = download_file_as_base64(attachment_url)
        #         if base64_attachment:
        #             if not file_extension:
        #                 file_extension = filename.split('.')[-1] if '.' in filename else 'txt'
        #             attachment_item = {
        #                 "type": file_extension,
        #                 "title": filename,
        #                 # "encodeData": base64_attachment
        #                 "encodeData": "base64_attachment"
        #             }
        #             attachment_info.append(attachment_item)

        # # 构建sublist - Item行
        # sublist = []
        # for i in range(len(details_list)):
        #     # rate = float(Unit_Price[i]) if Unit_Price[i] else 0.0
        #     # amount = float(Amount_excl_GST[i]) if Amount_excl_GST[i] else 0.0
        #     # taxrate = "9%"
        #     # taxamount = round(amount * 0.09, 2)
        #     # grossamount = amount + taxamount

        #     # 假设数量为金额/单价
        #     # if rate != 0:
        #     #     quantity = amount / rate
        #     if items[i] :
        #         item_line = {
        #             "sublistitemtype": "item",
        #             "item": str(items[i]),
        #             "description": Description[i],
        #             "department": str(divisions[i]),
        #             "quantity": quantities[i],
        #             "units": "1",
        #             "rate": unit_prices[i],
        #             "amount": item_amounts[i],
        #             "taxcode": taxcodes[i],
        #             "taxrate": rates[i],
        #             "cseg_business": Business[i],   
        #             # "cseg_product": "1",
        #             "cseg_scheme": Scheme[i],
        #             "cseg_pr_type": Product_Type[i],
        #             "class": Product_Code[i],
        #             "cseg1": Project_Code[i]
        #             # "taxamount": str(taxamount),
        #             # "grossamount": str(grossamount)
        #         }
        #         sublist.append(item_line)
        #     else:
        #         # print("expense_amounts:", expense_amounts)
        #         expense_line = {
        #             "sublistitemtype": "expense",
        #             "account": gl_account_ids[i],
        #             # "amount": Amount_excl_GST[i],
        #             "memo": Description[i],
        #             "department": divisions[i],
        #             # "class": Business[i],
        #             "taxcode":taxcodes[i],
        #             "taxrate": rates[i],
        #             "rate": unit_prices[i],
        #             "amount": expense_amounts[i],
        #             # "location": 6,  
        #             # "custcol_4601_witaxapplies": False,
        #             "cseg_business": Business[i],  
        #             "cseg_scheme": Scheme[i],
        #             "cseg_pr_type": Product_Type[i],
        #             "class": Product_Code[i],
        #             "cseg1": Project_Code[i]
        #         }
        #         sublist.append(expense_line)
        # request_body = {
        #     "posttype": "po",
        #     "entity": str(vendor_id),
        #     "trandate": transaction_date,
        #     "subsidiary": str(subsidiary_id),
        #     "tranid":"for_testing(ignore)"+str(Serial_Number),
        #     # "tranid": "potest024",
        #     "memo": "memo",
        #     "location": location,  
        #     "currency": currency,  
        #     "custbody7": 6637,
        #     "exchangerate": exchange_rate,
        #     "sublist": sublist,
        #     "attachment": attachment_info
        # }
        # # 打印请求体
        # print(json.dumps(request_body, indent=4))
        # print("serial_number:", Serial_Number)
        # # response = create_po_in_netsuite(request_body)
        # # print("response:", response)
        
        # print("------------------------------------------------------------")
