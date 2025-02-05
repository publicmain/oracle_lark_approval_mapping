import requests
import json
from config import get_tenant_access_token
from instance import get_current_and_past_week_timestamps, get_approval_instance_ids
from approval_detail import get_details_list, extract_details, extract_end_time,extract_value,extract_attachment_ext_names,get_instance_details
from field_internel_id import (mapping_date, mapping_entity_subsidiary, mapping_GL_Account, mapping_Vendor,
                               mapping_division, mapping_end_time,mapping_giro_paid,mapping_business, mapping_product_code,
                               mapping_product_type, mapping_project_code, mapping_scheme, mapping_currency,mapping_item,mapping_taxcode,mapping_Location)
from file_util import download_file_as_base64
from datetime import datetime

def convert_date_to_ddmmyyyy(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%d/%m/%Y")

def conditional_map(value, mapping_func):
            return mapping_func(value) if value else value

def generate_request_body(instance_response,type):
    # print("instance_response:", instance_response)
    Serial_Number = extract_value(instance_response, "Serial no.")
    Entity = extract_value(instance_response, "Entity")
    Vendor = extract_value(instance_response, "Vendor")
    Invoice_number = extract_value(instance_response, "Invoice Number")
    end_time = extract_end_time(instance_response)
    if Invoice_number:
        if len(Invoice_number) > 45:
            Invoice_number = Invoice_number[:44]
    
    # print("Invoice_number", Invoice_number)
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
    # print("original GL_Account:", GL_Account)
    Division_Code = get_details_list("Division Code", details_list)
    # print("original Division_Code:", Division_Code)
    Description = get_details_list("Description", details_list)
    # Currency = get_details_list("Unit Price", details_list_currency)
    Business = get_details_list("Business", details_list)
    # print("Business:", Business)
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
        # print(f"Entity '{Entity}' 被排除，返回 None")
        return None
    #V001597 Nguyen Ngo A Binh is not exist in Netsuite
    #70240 Settlement & Transaction Processing is not exist in Netsuite
    ##"Platform-Singtel Dash","Platform-Grab","Platform-PAYNOW","DCI","UPI" is not in Netsuite
    subsidiary_id = mapping_entity_subsidiary(Entity)
    if Vendor:
        vendor_id = mapping_Vendor(Vendor) 
    else:
            # print("Vendor is empty")
            # print("------------------------------------------------------------")
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
    # print("Business:", Business)
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
    end_time = mapping_end_time(end_time)
    # print("end_time:", end_time)
    # print("start_time:", start_time)
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
                # print("items:", items[i])
                # print("description:", Description[i])
                # print("department:", divisions[i])
                # print("taxcode:", taxcodes_po[i])
                # print("taxrate:", rates_po[i])
                # print("rate:", unit_prices[i])
                # print("amount:", item_amounts[i])
                # print("taxamount:", tax_amounts[i])
                # # print("cseg_business:", Business[i])
                # # print("cseg_scheme:", Scheme[i])
                # print("cseg_pr_type:", Product_Type[i])
                # print("class:", Product_Code[i])
                # print("cseg1:", Project_Code[i])
                # print("quantity:", quantities[i])
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
                # print("gl_account_ids:", gl_account_ids[i])
                # print("description:", Description[i])
                # print("department:", divisions[i])
                # print("taxcode:", taxcodes_po[i])
                # print("taxrate:", rates_po[i])
                # print("rate:", unit_prices[i])
                # print("amount:", expense_amounts[i])
                # print("taxamount:", tax_amounts[i])
                # print("cseg_business:", Business[i])
                # print("cseg_scheme:", Scheme[i])
                # print("cseg_pr_type:", Product_Type[i])
                # print("class:", Product_Code[i])
                # print("cseg1:", Project_Code[i])

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
                "trandate": end_time,
                "subsidiary": str(subsidiary_id),
                # "tranid":"for_testing(ignore  2)" + str(Serial_Number),
                "tranid":Serial_Number,
                # "tranid": "potest024",
                "memo": memo,
                "location": location,  
                "currency": currency,  
                "custbody7": 6637,
                "exchangerate": exchange_rate,
                "sublist": sublist,
                "attachment": attachment_info
                # "attachment": []
            }
            
            # formatted_request_body = json.dumps(request_body, indent=4, ensure_ascii=False)
            # print("request_body:\n", formatted_request_body)
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
            "trandate": end_time,
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
            "tranid":"for_testing(ignor e)"+str(Serial_Number),
            # "tranid":Invoice_number,
            # "tranid": "test042",
            "custbody7": 6637,
            "custbody_giropaidorpaid": giro_paid,
            "sublist": sublist,
            "attachment": attachment_info
        }

    # print("serial_number:", Serial_Number)
    return request_body, Serial_Number

if __name__ == "__main__":
    instanse = get_instance_details("660D7BAD-0BB5-4360-BEBF-EFA92F7BFCB7")
    request_body, Serial_Number = generate_request_body(instanse,"bill")
    # print("request_body:", json.dumps(request_body, indent=4))
    # print("Serial_Number:", Serial_Number)
    #如果说出现了invalid tax code，说明trandate是01/01/1970，就意味着这个bill还没有完成审批流程，还是在under review状态
       