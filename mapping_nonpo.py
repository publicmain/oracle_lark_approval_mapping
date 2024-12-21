from config import get_tenant_access_token,create_vendor_bill_in_netsuite
from instance import get_current_and_past_week_timestamps,get_approval_instance_ids
from approval_detail import get_instance_details
from request_body import generate_request_body
# 构建请求体并发送请求


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
def conditional_map(value, mapping_func):
        # 如果 value 存在且第一个元素非空（或按业务逻辑判断非空条件）
            return mapping_func(value) if value else value

for instance_id in instance_ids:
    if instance_id == "B1B24982-76B3-482F-ACA0-060D1C516D1E":
    # 获取审批实例详细信息
        instance_response = get_instance_details(instance_id)
        request_body = generate_request_body(instance_response, "bill")
        if request_body is None:
            continue
        response = create_vendor_bill_in_netsuite(request_body)
        print("------------------------------------------------------------")
        # instance_response = ["3D7FDD6E-FCE4-4A62-8532-4B9E75FFD4B3"]
        # 提取字段值
        # Entity = extract_value(instance_response, "Entity")
        # Serial_Number = extract_value(instance_response, "Serial no.")
        # Vendor = extract_value(instance_response, "Vendor").split()[0]
        # Invoice_number = extract_value(instance_response, "Invoice Number")
        # Date_of_Invoice = extract_value(instance_response, "Date of Invoice")
        # exchange_rate = extract_value(instance_response, "Exchange rate")
        # # print("exchange_rate:", exchange_rate)
        # Due_Date = extract_value(instance_response, "Due Date")
        # Location = extract_value(instance_response, "Location")
        # Giro_paid = extract_value(instance_response, "Giro Paid/Paid")
        # memo = extract_value(instance_response, "Memo")
        # details_list = extract_details(instance_response)
        # # details_list_currency = extract_currency_details(instance_response)
        # Currency = extract_value(instance_response, "Currency")
        # # print("Currency:", Currency)
        # Attachment = extract_value(instance_response, "Attachments")
        # GL_Account = get_details_list("GL Account", details_list)
        # Division_Code = get_details_list("Division Code", details_list)
        # Description = get_details_list("Description", details_list)
        # # Currency = get_details_list("Unit Price", details_list_currency)
        # Business = get_details_list("Business", details_list)
        # Scheme = get_details_list("Scheme", details_list)
        # Product_Type = get_details_list("Product Type", details_list)
        # Product_Code = get_details_list("Product Code", details_list)
        # Project_Code = get_details_list("Project Code", details_list)
        # Unit_Price = get_details_list("Unit Price", details_list)
        # Amounts = get_details_list("Amount(excl GST)", details_list)
        # tax_amounts = get_details_list("GST amount", details_list)
        # print("tax_amounts:", tax_amounts)
        # # Amount_incl_GST = get_details_list("Amount (incl GST)", details_list)
        # # GST_Amount = get_details_list("GST Amount", details_list)
        # taxcodes = get_details_list("GST Rate", details_list)
        # print(instance_id)
        # # if instance_id == "07303D5E-4E50-476E-9737-B59FD99F79E9":
        # # print("Amount_incl_GST:", Amount_incl_GST)
        # # print("Amount_excl_GST:", Amount_excl_GST)
        # # print("instance_id:", instance_id)
        # # print("Entity:", Entity)
        # # print("Vendor:", Vendor)
        # # print("Invoice Number:", Invoice_number)
        # # print("Date of Invoice:", Date_of_Invoice)
        # # print("Due Date:", Due_Date)
        # # print("Details:")
        # # print("Attachment:", Attachment)
        # # print("GL Account:", GL_Account)
        # # print("Division Code:", Division_Code)
        # # print("Description:", Description)
        # # print("Business:", Business)
        # # print("class:", Product_Code)
        # # print("Scheme:", Scheme)
        # # print("Product Type:", Product_Type)
        # # print("Product Code:", Product_Code)
        # # print("Project Code:", Project_Code)
        # # print("Unit Price:", Unit_Price)
        # # print("GST:", Gst)
        # # print("Amount (excl GST):", Amount_excl_GST)
        # # print("Amount (incl GST):", Amount_incl_GST)
        # # print("GST Amount:", GST_Amount)
        # # print("currency:", Currency)
        #     # 映射字段
        # if Entity == "DFS Asset Purchase Company Pte Ltd":
        #     continue
        # if memo:
        #      memo = memo
        # else:
        #     memo = "Generate from lark"
        # subsidiary_id = mapping_entity_subsidiary(Entity)
        # vendor_id = mapping_Vendor(Vendor)
        # #print(vendor_id)
        # # break
        # gl_account_ids = mapping_GL_Account(GL_Account)
        # #print("gl_account_ids",gl_account_ids)
        # trandate = mapping_date(Date_of_Invoice)
        # location = mapping_Location(Location) if Location else "2"
        # # location = mapping_Location()
        # duedate = mapping_date(Due_Date)
        # Date_of_Invoice = mapping_date(Date_of_Invoice)
        # # print(Date_of_Invoice)
        # divisions = mapping_division(Division_Code)
        # #print("divisions",divisions)
        # Business = mapping_business(Business)
        # #print("Business",Business)
        # Scheme = mapping_scheme(Scheme)
        # #print("Scheme",Scheme)
        # Product_Type = mapping_product_type(Product_Type)
        # #print("product type", Product_Type)
        # Product_Code = mapping_product_code(Product_Code)
        # #print("Product_Code",Product_Code)
        # Project_Code = mapping_project_code(Project_Code)
        # #print("Project_Code",Project_Code)
        # currency = conditional_map(Currency, mapping_currency)
        # giro_paid = mapping_giro_paid(Giro_paid)
        # taxcodes, rates = mapping_taxcode(taxcodes)
        # # print("currency",currency)
        # # print("------------------------------------------------------------")
        # # print(currency)
        # # print(subsidiary_id)
        # # print(vendor_id)
        # # print(gl_account_ids)
        # # print(trandate)
        # # print(duedate)
        # # # 处理附件
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
        #                 "encodeData": base64_attachment
        #             }
        #             attachment_info.append(attachment_item)
        # # print(files_info)
        # # print(files_info)
        # # 构建明细行
        # sublist = []
        # for i in range(len(details_list)):
        #     expense_line = {
        #         "sublistitemtype": "expense",
        #         "account": gl_account_ids[i],
        #         # "amount": Amount_excl_GST[i],
        #         "memo": Description[i],
        #         "department": divisions[i],
        #         # "class": Business[i],
        #         "taxcode":taxcodes[i],
        #         "taxrate": rates[i],
        #         "amount": Amounts[i],
        #         "taxamount": tax_amounts[i],
        #         "cseg_business": Business[i],  
        #         "cseg_scheme": Scheme[i],
        #         "cseg_pr_type": Product_Type[i],
        #         "class": Product_Code[i],
        #         "cseg1": Project_Code[i]
        #     }
        #     sublist.append(expense_line)
        #     # print(expense_line)


        #     # 构建请求体
        # request_body = {
        #     "posttype": "bill",
        #     "trandate": trandate,
        #     "duedate": duedate,
        #     "entity": vendor_id,
        #     "subsidiary": subsidiary_id,
        #     "location":location,
        #     "memo": memo,
        #     # "approvalstatus": "2",
        #     # "customform": "171",
        #     "currency": currency,
        #     "exchangerate": exchange_rate,
        #     "custbody_document_date": Date_of_Invoice,
        #     # "tranid":"for_testing(ignore)"+str(Serial_Number),
        #     "tranid": "test040",
        #     "custbody7": 6637,
        #     "custbody_giropaidorpaid": giro_paid,
        #     "sublist": sublist,
        #     "attachment": attachment_info
        # }
        
        # # 发送请求创建 Vendor Bill
        # # print(request_body)
        # # print(json.dumps(request_body, indent=4))
        
        # print("serial number:", Serial_Number)
        

