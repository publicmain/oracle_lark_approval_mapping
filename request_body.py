import requests
import json
from config import get_tenant_access_token
from instance import get_current_and_past_week_timestamps, get_approval_instance_ids
from approval_detail import get_details_list, extract_details, extract_value,extract_attachment_ext_names
from field_internel_id import (mapping_date, mapping_entity_subsidiary, mapping_GL_Account, mapping_Vendor,
                               mapping_division, mapping_postperiod, mapping_giro_paid,mapping_business, mapping_product_code,
                               mapping_product_type, mapping_project_code, mapping_scheme, mapping_currency,mapping_item,mapping_taxcode,mapping_Location)
from file_util import download_file_as_base64
from requests_oauthlib import OAuth1
from datetime import datetime

def convert_date_to_ddmmyyyy(date_str):
    # 假设mapping_date返回"YYYY-MM-DD"格式，这里转为"dd/mm/yyyy"
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%d/%m/%Y")

def conditional_map(value, mapping_func):
        # 如果 value 存在且第一个元素非空（或按业务逻辑判断非空条件）
            return mapping_func(value) if value else value

def generate_request_body(instance_response,type):
    Serial_Number = extract_value(instance_response, "Serial no.")
    Entity = extract_value(instance_response, "Entity")
    Vendor = extract_value(instance_response, "Vendor")
    Invoice_number = extract_value(instance_response, "Invoice Number")
    Date_of_Invoice_PO = extract_value(instance_response, "Transaction date")
    Date_of_Invoice_bill = extract_value(instance_response, "Date of Invoice")
    Currency = extract_value(instance_response, "Currency")
    exchange_rate = extract_value(instance_response, "Exchange rate")
    Location = extract_value(instance_response, "Location")
    memo = extract_value(instance_response, "Memo")
    Giro_paid = extract_value(instance_response, "Giro Paid/Paid")
    #print("exchange_rate:", exchange_rate)
    duedate = extract_value(instance_response, "Due Date")
    transaction_date = extract_value(instance_response, "Transaction date")
    details_list = extract_details(instance_response)
    Attachment = extract_value(instance_response, "Attachments")
    Attachment_names = extract_attachment_ext_names(instance_response)
    GL_Account = get_details_list("GL Account", details_list)
    Division_Code = get_details_list("Division Code", details_list)
    # print("original Division_Code:", Division_Code)
    Description = get_details_list("Description", details_list)
    # Currency = get_details_list("Unit Price", details_list_currency)
    Business = get_details_list("Business", details_list)
    # print("original Business:", Business)
    Scheme = get_details_list("Scheme", details_list)
    Product_Type = get_details_list("Product Type", details_list)
    Product_Code = get_details_list("Product Code", details_list)
    # print("origiinal Product_Code:", Product_Code)
    Project_Code = get_details_list("Project Code", details_list)
    # print("original Project_Code:", Project_Code)
    Unit_Price = get_details_list("Unit Price", details_list)
    Amount_excl_GST = get_details_list("Amount (excl GST)", details_list)
    # print("Amount_excl_GST:", Amount_excl_GST)
    Amount_incl_GST = get_details_list("Amount (incl GST)", details_list)
    GST_Amount = get_details_list("GST Amount", details_list)
    Gst = get_details_list("GST?", details_list)
    items = get_details_list("Inventory Item", details_list)
    quantities = get_details_list("Quantity", details_list)
    taxcodes_po = get_details_list("GST?", details_list)
    taxcodes_bill = get_details_list("GST Rate", details_list)
    Amounts = get_details_list("Amount(excl GST)", details_list)
    item_amounts = get_details_list("Item Amount(excl GST)", details_list)
    expense_amounts = get_details_list("Expense Amount(excl GST)", details_list)
    unit_prices = get_details_list("Unit Price", details_list)
    tax_amounts = get_details_list("GST amount", details_list)
    # print("tax_amounts:", tax_amounts)
    #print("original taxcodes:", taxcodes)
    # print("orginal items:", items)
    # print("item_amounts:", item_amounts)
    # print("expense_amounts:", expense_amounts)

    

    if Entity == "DFS Asset Purchase Company Pte Ltd" or Entity == "SHANGHAI DALAI":
        print(f"Entity '{Entity}' 被排除，返回 None")
        return None
    subsidiary_id = mapping_entity_subsidiary(Entity)
    if Vendor:
        vendor_id = mapping_Vendor(Vendor) 
    else:
            print("Vendor is empty")
            print("------------------------------------------------------------")
            return None
    if memo:
        memo = memo
    else:
        memo = "Generated by Lark"
    gl_account_ids = conditional_map(GL_Account, mapping_GL_Account)
    # print("gl_account_ids:", gl_account_ids)
    trandate_PO = mapping_date(Date_of_Invoice_PO)
    trandate_bill = mapping_date(Date_of_Invoice_bill)
    duedate= mapping_date(duedate)
    transaction_date = mapping_date(transaction_date)
    location = mapping_Location(Location) if Location else "2"
    divisions = conditional_map(Division_Code, mapping_division)
    # print("divisions:", divisions)
    Business = conditional_map(Business, mapping_business)
    Scheme = conditional_map(Scheme, mapping_scheme)
    # print("original Scheme:", Scheme)
    Product_Type = conditional_map(Product_Type,mapping_product_type)  # 无条件映射
    Product_Code = conditional_map(Product_Code, mapping_product_code)
    Project_Code = conditional_map(Project_Code, mapping_project_code)
    currency = conditional_map(Currency, mapping_currency)
    # print("currency:", currency)
    items = conditional_map(items,mapping_item)
    taxcodes_po, rates_po = mapping_taxcode(taxcodes_po)
    taxcodes_bill, rates_bill = mapping_taxcode(taxcodes_bill)
    giro_paid = mapping_giro_paid(Giro_paid)
    # print("taxcodes:", taxcodes)
    # print("rates:", rates)
    # print("items:", items)

    
    attachment_info = []
    if Attachment:
        attachment_urls = Attachment if isinstance(Attachment, list) else [Attachment]
        for i in range(len(attachment_urls)):
            base64_attachment, filename, file_extension, _ = download_file_as_base64(attachment_urls[i])
            # print("filename:", Attachment_names[i])
            if base64_attachment:
                if not file_extension:
                    file_extension = filename.split('.')[-1] if '.' in filename else 'txt'
                attachment_item = {
                    "type": file_extension,
                    "title": Attachment_names[i],
                    # "encodeData": base64_attachment
                    "encodeData": base64_attachment
                }
                attachment_info.append(attachment_item)

    # 构建sublist - Item行
    if type == "po":
        sublist = []
        for i in range(len(details_list)):
            if items[i] :
                item_line = {
                    "sublistitemtype": "item",
                    "item": str(items[i]),
                    "description": Description[i],
                    "department": str(divisions[i]),
                    "quantity": quantities[i],
                    "units": "1",
                    "rate": unit_prices[i],
                    "amount": item_amounts[i],
                    "taxcode": taxcodes_po[i],
                    "taxrate": rates_po[i],
                    "cseg_business": Business[i],   
                    # "cseg_product": "1",
                    "cseg_scheme": Scheme[i],
                    "cseg_pr_type": Product_Type[i],
                    "class": Product_Code[i],
                    "cseg1": Project_Code[i],
                    "taxamount": tax_amounts[i],
                    # "grossamount": str(grossamount)
                }
                sublist.append(item_line)
            else:
                # print("expense_amounts:", expense_amounts)
                expense_line = {
                    "sublistitemtype": "expense",
                    "account": gl_account_ids[i],
                    # "amount": Amount_excl_GST[i],
                    "memo": Description[i],
                    "department": divisions[i],
                    # "class": Business[i],
                    "taxcode":taxcodes_po[i],
                    "taxrate": rates_po[i],
                    "rate": unit_prices[i],
                    "amount": expense_amounts[i],
                    "taxamount": tax_amounts[i],
                    # "location": 6,  
                    # "custcol_4601_witaxapplies": False,
                    "cseg_business": Business[i],  
                    "cseg_scheme": Scheme[i],
                    "cseg_pr_type": Product_Type[i],
                    "class": Product_Code[i],
                    "cseg1": Project_Code[i]
                }
                sublist.append(expense_line)
        
            request_body = {
                "posttype": "po",
                "entity": str(vendor_id),
                "trandate": transaction_date,
                "subsidiary": str(subsidiary_id),
                "tranid":"for_testing(ignore)"+str(Serial_Number)+"11",
                # "tranid": "potest024",
                "memo": memo,
                "location": location,  
                "currency": currency,  
                "custbody7": 6637,
                "exchangerate": exchange_rate,
                "sublist": sublist,
                "attachment": attachment_info
            }
    if type == "bill":
        sublist = []
        for i in range(len(details_list)):
            if items[i] :
                item_line = {
                    "sublistitemtype": "item",
                    "item": str(items[i]),
                    "description": Description[i],
                    "department": str(divisions[i]),
                    "quantity": quantities[i],
                    "units": "1",
                    "rate": unit_prices[i],
                    "amount": item_amounts[i],
                    "taxcode": taxcodes_po[i],
                    "taxrate": rates_bill[i],
                    "cseg_business": Business[i],   
                    # "cseg_product": "1",
                    "cseg_scheme": Scheme[i],
                    "cseg_pr_type": Product_Type[i],
                    "class": Product_Code[i],
                    "cseg1": Project_Code[i],
                    "taxamount": tax_amounts[i],
                    # "grossamount": str(grossamount)
                }
                sublist.append(item_line)
            else:
                # print("expense_amounts:", expense_amounts)
                expense_line = {
                    "sublistitemtype": "expense",
                    "account": gl_account_ids[i],
                    # "amount": Amount_excl_GST[i],
                    "memo": Description[i],
                    "department": divisions[i],
                    # "class": Business[i],
                    "taxcode":taxcodes_bill[i],
                    "taxrate": rates_bill[i],
                    "rate": unit_prices[i],
                    "amount": Amounts[i],
                    "taxamount": tax_amounts[i],
                    # "location": 6,  
                    # "custcol_4601_witaxapplies": False,
                    "cseg_business": Business[i],  
                    "cseg_scheme": Scheme[i],
                    "cseg_pr_type": Product_Type[i],
                    "class": Product_Code[i],
                    "cseg1": Project_Code[i]
                }
                sublist.append(expense_line)
        
        request_body = {
            "posttype": "bill",
            "trandate": trandate_bill,
            "duedate": duedate,
            "entity": vendor_id,
            "subsidiary": subsidiary_id,
            "location":location,
            "memo": memo,
            # "approvalstatus": "2",
            # "customform": "171",
            "currency": currency,
            "exchangerate": exchange_rate,
            "custbody_document_date": trandate_bill,
            "tranid":"for_testing(ignore)"+str(Serial_Number)+"1",
            # "tranid": "test042",
            "custbody7": 6637,
            "custbody_giropaidorpaid": giro_paid,
            "sublist": sublist,
            "attachment": attachment_info
        }
        
    # 打印请求体
    # print(json.dumps(request_body, indent=4))
    print("serial_number:", Serial_Number)
    # from_id = extract_fromId(instance_response)
    return request_body

# def generate_request_body(instance_response, type):
#     print("=== 开始生成请求体 ===")
#     print(f"输入参数 - type: {type}")
#     print(f"instance_response: {instance_response}")
    
#     # 提取各个字段的值
#     Serial_Number = extract_value(instance_response, "Serial no.")
#     print(f"Serial_Number: {Serial_Number}")
    
#     Entity = extract_value(instance_response, "Entity")
#     print(f"Entity: {Entity}")
    
#     Vendor = extract_value(instance_response, "Vendor")
#     print(f"Vendor: {Vendor}")
    
#     Invoice_number = extract_value(instance_response, "Invoice Number")
#     print(f"Invoice_number: {Invoice_number}")
    
#     Date_of_Invoice_PO = extract_value(instance_response, "Transaction date")
#     print(f"Date_of_Invoice_PO: {Date_of_Invoice_PO}")
    
#     Date_of_Invoice_bill = extract_value(instance_response, "Date of Invoice")
#     print(f"Date_of_Invoice_bill: {Date_of_Invoice_bill}")
    
#     Currency = extract_value(instance_response, "Currency")
#     print(f"Currency: {Currency}")
    
#     exchange_rate = extract_value(instance_response, "Exchange rate")
#     print(f"exchange_rate: {exchange_rate}")
    
#     Location = extract_value(instance_response, "Location")
#     print(f"Location: {Location}")
    
#     memo = extract_value(instance_response, "Memo")
#     print(f"memo: {memo}")
    
#     Giro_paid = extract_value(instance_response, "Giro Paid/Paid")
#     print(f"Giro_paid: {Giro_paid}")
    
#     duedate = extract_value(instance_response, "Due Date")
#     print(f"duedate: {duedate}")
    
#     transaction_date = extract_value(instance_response, "Transaction date")
#     print(f"transaction_date: {transaction_date}")
    
#     # 提取详细信息列表
#     details_list = extract_details(instance_response)
#     print(f"details_list: {details_list}")
    
#     # 检查 details_list 是否为 None
#     # if details_list is None:
#     #     print("错误: details_list 是 None")
#     #     return []
    
#     # 提取附件信息
#     Attachment = extract_value(instance_response, "Attachments")
#     print(f"Attachment: {Attachment}")
    
#     # 获取各个详细字段
#     GL_Account = get_details_list("GL Account", details_list)
#     print(f"GL_Account: {GL_Account}")
    
#     Division_Code = get_details_list("Division Code", details_list)
#     print(f"Division_Code: {Division_Code}")
    
#     Description = get_details_list("Description", details_list)
#     print(f"Description: {Description}")
    
#     Business = get_details_list("Business", details_list)
#     print(f"Business: {Business}")
    
#     Scheme = get_details_list("Scheme", details_list)
#     print(f"Scheme: {Scheme}")
    
#     Product_Type = get_details_list("Product Type", details_list)
#     print(f"Product_Type: {Product_Type}")
    
#     Product_Code = get_details_list("Product Code", details_list)
#     print(f"Product_Code: {Product_Code}")
    
#     Project_Code = get_details_list("Project Code", details_list)
#     print(f"Project_Code: {Project_Code}")
    
#     Unit_Price = get_details_list("Unit Price", details_list)
#     print(f"Unit_Price: {Unit_Price}")
    
#     Amount_excl_GST = get_details_list("Amount (excl GST)", details_list)
#     print(f"Amount_excl_GST: {Amount_excl_GST}")
    
#     Amount_incl_GST = get_details_list("Amount (incl GST)", details_list)
#     print(f"Amount_incl_GST: {Amount_incl_GST}")
    
#     GST_Amount = get_details_list("GST Amount", details_list)
#     print(f"GST_Amount: {GST_Amount}")
    
#     Gst = get_details_list("GST?", details_list)
#     print(f"Gst: {Gst}")
    
#     items = get_details_list("Inventory Item", details_list)
#     print(f"items: {items}")
    
#     quantities = get_details_list("Quantity", details_list)
#     print(f"quantities: {quantities}")
    
#     taxcodes_po = get_details_list("GST?", details_list)
#     print(f"taxcodes_po: {taxcodes_po}")
    
#     taxcodes_bill = get_details_list("GST Rate", details_list)
#     print(f"taxcodes_bill: {taxcodes_bill}")
    
#     Amounts = get_details_list("Amount(excl GST)", details_list)
#     print(f"Amounts: {Amounts}")
    
#     item_amounts = get_details_list("Item Amount(excl GST)", details_list)
#     print(f"item_amounts: {item_amounts}")
    
#     expense_amounts = get_details_list("Expense Amount(excl GST)", details_list)
#     print(f"expense_amounts: {expense_amounts}")
    
#     unit_prices = get_details_list("Unit Price", details_list)
#     print(f"unit_prices: {unit_prices}")
    
#     tax_amounts = get_details_list("GST amount", details_list)
#     print(f"tax_amounts: {tax_amounts}")
    
#     print("=== 字段提取完成 ===")
    
#     # 检查 Entity 是否需要跳过
#     if Entity == "DFS Asset Purchase Company Pte Ltd" or Entity == "SHANGHAI DALAI":
#         print(f"Entity '{Entity}' 被排除，返回 None")
#         return None
    
#     # 映射 Entity 到 subsidiary_id
#     subsidiary_id = mapping_entity_subsidiary(Entity)
#     print(f"subsidiary_id: {subsidiary_id}")
    
#     # 检查 Vendor 是否存在并映射到 vendor_id
#     if Vendor:
#         vendor_id = mapping_Vendor(Vendor)
#         print(f"vendor_id: {vendor_id}")
#     else:
#         print("错误: Vendor 是空的")
#         print("------------------------------------------------------------")
#         return None
    
#     # 处理 memo 字段
#     if memo:
#         print(f"使用提供的 memo: {memo}")
#     else:
#         memo = "Generated by Lark"
#         print(f"memo 是空的，使用默认值: {memo}")
    
#     # 映射 GL_Account
#     gl_account_ids = conditional_map(GL_Account, mapping_GL_Account)
#     print(f"gl_account_ids: {gl_account_ids}")
    
#     # 映射日期字段
#     trandate_PO = mapping_date(Date_of_Invoice_PO)
#     print(f"trandate_PO: {trandate_PO}")
    
#     trandate_bill = mapping_date(Date_of_Invoice_bill)
#     print(f"trandate_bill: {trandate_bill}")
    
#     duedate = mapping_date(duedate)
#     print(f"duedate: {duedate}")
    
#     transaction_date = mapping_date(transaction_date)
#     print(f"transaction_date: {transaction_date}")
    
#     # 映射 Location
#     location = mapping_Location(Location) if Location else "2"
#     print(f"location: {location}")
    
#     # 映射 Division_Code
#     divisions = conditional_map(Division_Code, mapping_division)
#     print(f"divisions: {divisions}")
    
#     # 映射 Business
#     Business = conditional_map(Business, mapping_business)
#     print(f"Business: {Business}")
    
#     # 映射 Scheme
#     Scheme = conditional_map(Scheme, mapping_scheme)
#     print(f"Scheme: {Scheme}")
    
#     # 映射 Product_Type
#     Product_Type = conditional_map(Product_Type, mapping_product_type)
#     print(f"Product_Type: {Product_Type}")
    
#     # 映射 Product_Code
#     Product_Code = conditional_map(Product_Code, mapping_product_code)
#     print(f"Product_Code: {Product_Code}")
    
#     # 映射 Project_Code
#     Project_Code = conditional_map(Project_Code, mapping_project_code)
#     print(f"Project_Code: {Project_Code}")
    
#     # 映射 Currency
#     currency = conditional_map(Currency, mapping_currency)
#     print(f"currency: {currency}")
    
#     # 映射 items
#     items = conditional_map(items, mapping_item)
#     print(f"mapped items: {items}")
    
#     # 映射 taxcodes_po 和 rates_po
#     taxcodes_po, rates_po = mapping_taxcode(taxcodes_po)
#     print(f"taxcodes_po: {taxcodes_po}")
#     print(f"rates_po: {rates_po}")
    
#     # 映射 taxcodes_bill 和 rates_bill
#     taxcodes_bill, rates_bill = mapping_taxcode(taxcodes_bill)
#     print(f"taxcodes_bill: {taxcodes_bill}")
#     print(f"rates_bill: {rates_bill}")
    
#     # 映射 Giro_paid
#     giro_paid = mapping_giro_paid(Giro_paid)
#     print(f"giro_paid: {giro_paid}")
    
#     # 处理附件信息
#     attachment_info = []
#     if Attachment:
#         print("处理附件信息")
#         attachment_urls = Attachment if isinstance(Attachment, list) else [Attachment]
#         print(f"attachment_urls: {attachment_urls}")
#         for attachment_url in attachment_urls:
#             print(f"下载附件: {attachment_url}")
#             base64_attachment, filename, file_extension, _ = download_file_as_base64(attachment_url)
#             print(f"base64_attachment: {base64_attachment[:30]}...")  # 只打印前30个字符
#             print(f"filename: {filename}")
#             print(f"file_extension: {file_extension}")
#             if base64_attachment:
#                 if not file_extension:
#                     file_extension = filename.split('.')[-1] if '.' in filename else 'txt'
#                     print(f"自动推断 file_extension: {file_extension}")
#                 attachment_item = {
#                     "type": file_extension,
#                     "title": filename,
#                     "encodeData": base64_attachment
#                 }
#                 print(f"添加附件项: {attachment_item}")
#                 attachment_info.append(attachment_item)
#     else:
#         print("没有附件信息")
    
#     # 构建 sublist
#     if type == "po":
#         print("构建 PO 类型的 sublist")
#         sublist = []
#         for i in range(len(details_list)):
#             print(f"处理 PO sublist 第 {i+1} 项")
#             if items[i]:
#                 print(f"构建 item_line: {i+1}")
#                 item_line = {
#                     "sublistitemtype": "item",
#                     "item": str(items[i]),
#                     "description": Description[i],
#                     "department": str(divisions[i]),
#                     "quantity": quantities[i],
#                     "units": "1",
#                     "rate": unit_prices[i],
#                     "amount": item_amounts[i],
#                     "taxcode": taxcodes_po[i],
#                     "taxrate": rates_po[i],
#                     "cseg_business": Business[i],   
#                     "cseg_scheme": Scheme[i],
#                     "cseg_pr_type": Product_Type[i],
#                     "class": Product_Code[i],
#                     "cseg1": Project_Code[i],
#                     "taxamount": tax_amounts[i],
#                 }
#                 print(f"item_line: {item_line}")
#                 sublist.append(item_line)
#             else:
#                 print(f"构建 expense_line: {i+1}")
#                 expense_line = {
#                     "sublistitemtype": "expense",
#                     "account": gl_account_ids[i],
#                     "memo": Description[i],
#                     "department": divisions[i],
#                     "taxcode": taxcodes_po[i],
#                     "taxrate": rates_po[i],
#                     "rate": unit_prices[i],
#                     "amount": expense_amounts[i],
#                     "taxamount": tax_amounts[i],
#                     "cseg_business": Business[i],  
#                     "cseg_scheme": Scheme[i],
#                     "cseg_pr_type": Product_Type[i],
#                     "class": Product_Code[i],
#                     "cseg1": Project_Code[i]
#                 }
#                 print(f"expense_line: {expense_line}")
#                 sublist.append(expense_line)
        
#         request_body = {
#             "posttype": "po",
#             "entity": str(vendor_id),
#             "trandate": transaction_date,
#             "subsidiary": str(subsidiary_id),
#             "tranid": f"for_testing(ignore){Serial_Number}7",
#             "memo": memo,
#             "location": location,  
#             "currency": currency,  
#             "custbody7": 6637,
#             "exchangerate": exchange_rate,
#             "sublist": sublist,
#             "attachment": attachment_info
#         }
#         print("构建的 PO request_body:")
#         print(json.dumps(request_body, indent=4))
    
#     elif type == "bill":
#         print("构建 Bill 类型的 sublist")
#         sublist = []
#         for i in range(len(details_list)):
#             print(f"处理 Bill sublist 第 {i+1} 项")
#             if items[i]:
#                 print(f"构建 item_line: {i+1}")
#                 item_line = {
#                     "sublistitemtype": "item",
#                     "item": str(items[i]),
#                     "description": Description[i],
#                     "department": str(divisions[i]),
#                     "quantity": quantities[i],
#                     "units": "1",
#                     "rate": unit_prices[i],
#                     "amount": item_amounts[i],
#                     "taxcode": taxcodes_po[i],
#                     "taxrate": rates_bill[i],
#                     "cseg_business": Business[i],   
#                     "cseg_scheme": Scheme[i],
#                     "cseg_pr_type": Product_Type[i],
#                     "class": Product_Code[i],
#                     "cseg1": Project_Code[i],
#                     "taxamount": tax_amounts[i],
#                 }
#                 print(f"item_line: {item_line}")
#                 sublist.append(item_line)
#             else:
#                 print(f"构建 expense_line: {i+1}")
#                 expense_line = {
#                     "sublistitemtype": "expense",
#                     "account": gl_account_ids[i],
#                     "memo": Description[i],
#                     "department": divisions[i],
#                     "taxcode": taxcodes_bill[i],
#                     "taxrate": rates_bill[i],
#                     "rate": unit_prices[i],
#                     "amount": Amounts[i],
#                     "taxamount": tax_amounts[i],
#                     "cseg_business": Business[i],  
#                     "cseg_scheme": Scheme[i],
#                     "cseg_pr_type": Product_Type[i],
#                     "class": Product_Code[i],
#                     "cseg1": Project_Code[i]
#                 }
#                 print(f"expense_line: {expense_line}")
#                 sublist.append(expense_line)
        
#         request_body = {
#             "posttype": "bill",
#             "trandate": trandate_bill,
#             "duedate": duedate,
#             "entity": vendor_id,
#             "subsidiary": subsidiary_id,
#             "location": location,
#             "memo": memo,
#             "currency": currency,
#             "exchangerate": exchange_rate,
#             "custbody_document_date": trandate_bill,
#             "tranid": "test041",
#             "custbody7": 6637,
#             "custbody_giropaidorpaid": giro_paid,
#             "sublist": sublist,
#             "attachment": attachment_info
#         }
#         print("构建的 Bill request_body:")
#         print(json.dumps(request_body, indent=4))
    
#     # 打印序列号和请求体
#     print("serial_number:", Serial_Number)
#     print("=== 请求体生成完成 ===")
    
#     # 提取 from_id
#     from_id = extract_fromId(instance_response)
#     print(f"from_id: {from_id}")
    
#     return request_body, from_id
