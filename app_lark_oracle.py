
from flask import Flask, jsonify
import json
from logger_config import get_loggers  

from config import get_tenant_access_token, create_vendor_bill_in_netsuite
from instance import get_current_and_past_week_timestamps, get_approval_instance_ids
from approval_detail import get_instance_details, extract_value, extract_fromId,extract_attachment_ext_names
from field_internel_id import mapping_date, mapping_entity_subsidiary, mapping_giro_paid,find_exist_PO
from file_util import download_file_as_base64
from request_body import generate_request_body

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return "Flask API is running!", 200


def handle_response(instance_id, response, success_message, success_logger, error_logger, formid, serial_number):
    """
    根据传入的formid决定记录到success.log还是error.log
    如果formid不是None，记录到success.log
    如果formid是None，记录到error.log，并提取并记录message字段内容
    """
    def contains_duplicate(obj):
        if isinstance(obj, dict):
            for value in obj.values():
                if contains_duplicate(value):
                    return True
        elif isinstance(obj, list):
            for item in obj:
                if contains_duplicate(item):
                    return True
        elif isinstance(obj, str):
            if 'duplicate' in obj.lower():
                return True
        return False

    # 递归检查响应中是否包含“duplicate”
    if contains_duplicate(response):
        # 检测到“duplicate”，不记录任何日志，直接返回
        return None, None  
    def contains_duplicate(obj, depth=0):
        indent = "  " * depth  # 用于格式化输出，使调试信息更易读
        if isinstance(obj, dict):
            # print(f"{indent}Checking a dictionary with {len(obj)} keys.")
            for key, value in obj.items():
                # print(f"{indent}  Checking key: {key}")
                if contains_duplicate(value, depth + 2):
                    return True
        elif isinstance(obj, list):
            # print(f"{indent}Checking a list with {len(obj)} items.")
            for index, item in enumerate(obj):
                # print(f"{indent}  Checking index {index}: {item}")
                if contains_duplicate(item, depth + 2):
                    return True
        elif isinstance(obj, str):
            # print(f"{indent}Checking a string: '{obj}'")
            if 'duplicate' in obj.lower():
                # print(f"{indent}  Found 'duplicate' in string.")
                return True
        # else:
        #     print(f"{indent}Encountered unsupported type: {type(obj)}")
        return False

    # 递归检查响应中是否包含“duplicate”
    if contains_duplicate(response):
        print("Duplicate detected in response. Exiting without logging.")
        # 检测到“duplicate”，不记录任何日志，直接返回
        return None, None
    else:
        print("No duplicates found in response.")

    if formid is not None:
        
        success_logger.info(success_message)
        return {"instance_id": instance_id, "response": response}, True
    else:
        
        message = "Unknown error"
        if 'error' in response:
            try:
                
               
                error_content = json.loads(response['error'])
                if 'message' in error_content.get('error', {}):
                    inner_error_message = error_content['error']['message']
                    
                    inner_error_content = json.loads(inner_error_message)
                    message = inner_error_content.get('message', message)
            except json.JSONDecodeError:
               
                message = response['error']
            except Exception as e:
             
                message = f"Error parsing message: {str(e)}"
        
     
        error_logger.error(f"Failed to process serial_number: {serial_number} - Message: {message}")
        return {"serial_number": serial_number, "response": message}, False


def process_bill_approvals():
    process_name = "bill"
    success_logger, error_logger = get_loggers(process_name)
    
    ACCESS_TOKEN = "Bearer " + get_tenant_access_token()
    APPROVAL_CODE = "CF9A8C73-2873-4ABA-BF7D-144DD29D9598"
    START_TIME, END_TIME = get_current_and_past_week_timestamps()
    
    instance_ids = get_approval_instance_ids(
        access_token=ACCESS_TOKEN,
        approval_code=APPROVAL_CODE,
        start_time=START_TIME,
        end_time=END_TIME
    )
    
    results = []
    for instance_id in instance_ids:
        try:
            print(instance_id)
            instance_response = get_instance_details(instance_id)
            result = generate_request_body(instance_response, "bill")
            
            if result is None:
                Serial_Number = extract_value(instance_response, "Serial no.")
                # 如果 generate_request_body 返回 None，记录错误并跳过
                error_message = f"Vendor bill is empty or Entity is DFS Asset Purchase Company Pte Ltd or SHANGHAI DALAI for Serial_Number : {Serial_Number}"
                error_logger.error(error_message)
                results.append({"instance_id": Serial_Number, "response": "generate_request_body returned None"})
                continue
     
            request_body, serial_number = result
            if request_body is None:
                continue
            
            response = create_vendor_bill_in_netsuite(request_body)
            formid = extract_fromId(response)
            # print(formid)
            result, is_success = handle_response(
                instance_id,
                response,
                f"Successfully processed bill serial_number: {serial_number}",
                success_logger,
                error_logger,
                formid,
                serial_number
            )
            results.append(result)
        except Exception as e:
            error_logger.error(f"Failed to process serial_number: {serial_number} - Exception: {str(e)}")
            results.append({"serial_number": serial_number, "response": str(e)})
    return results


def process_po_approvals():
    process_name = "po"
    success_logger, error_logger = get_loggers(process_name)
    
    ACCESS_TOKEN = "Bearer " + get_tenant_access_token()
    APPROVAL_CODE_PO = "A80CFB80-46EC-40BA-9CB2-AE9F26C9AB07"
    START_TIME, END_TIME = get_current_and_past_week_timestamps()
    
    instance_ids = get_approval_instance_ids(
        access_token=ACCESS_TOKEN,
        approval_code=APPROVAL_CODE_PO,
        start_time=START_TIME,
        end_time=END_TIME
    )
    
    results = []
    for instance_id in instance_ids:
        # print(instance_id)
        # if instance_id == "A709021D-E0A1-46E8-A0E8-0F5AF1C550EF":
            try:
                instance_response = get_instance_details(instance_id)
                
                result = generate_request_body(instance_response, "po")
                if result is None:
                    
                    Serial_Number = extract_value(instance_response, "Serial no.")
                    # 如果 generate_request_body 返回 None，记录错误并跳过
                    
                    error_message = f"Vendor bill is empty or Entity is DFS Asset Purchase Company Pte Ltd or SHANGHAI DALAI for Serial_Number : {Serial_Number}"
                    error_logger.error(error_message)
                    results.append({"instance_id": Serial_Number, "response": "generate_request_body returned None"})
                    continue
                
             
                request_body, serial_number = result
                print("serial_number:", serial_number)
                if request_body is None:
                    continue
                response = create_vendor_bill_in_netsuite(request_body)
                fromId = extract_fromId(response)
  
                success_message = f"Successfully processed PO serial_number: {serial_number}, fromId: {fromId}"
                result, is_success = handle_response(
                    instance_id,
                    response,
                    success_message,
                    success_logger,
                    error_logger,
                    fromId,
                    serial_number
                )
                results.append(result)
            except Exception as e:
                error_logger.error(f"Failed to process PO serial_number: {serial_number} - Exception: {str(e)}")
                results.append({"serial_number": serial_number, "response": str(e)})
    return results


def process_polinked_approvals():
    process_name = "polinkedbill"
    success_logger, error_logger = get_loggers(process_name)
    
    ACCESS_TOKEN = "Bearer " + get_tenant_access_token()
    APPROVAL_CODE_POLINKED = "2B77BB3F-5FCE-4FD1-9A17-834F06E2FFAE"
    START_TIME, END_TIME = get_current_and_past_week_timestamps()
    
    instance_ids = get_approval_instance_ids(
        access_token=ACCESS_TOKEN,
        approval_code=APPROVAL_CODE_POLINKED,
        start_time=START_TIME,
        end_time=END_TIME
    )
    
    results = []
    # print("instance_ids:", instance_ids)
    for instance_id in instance_ids:
            
        # if instance_id == "9886CB55-F8E0-412D-B3EE-618F34CF0936":
            try:
                instance_response = get_instance_details(instance_id)
                Entity = extract_value(instance_response, "Entity")
                Invoice_Number = extract_value(instance_response, "Invoice Number")
                print("Invoice_Number:", Invoice_Number)
                duedate = extract_value(instance_response, "Due Date")
                Giro_paid = extract_value(instance_response, "Giro Pay / Paid")
                trandate = extract_value(instance_response, "Date of Invoice")
                Serial_Number = extract_value(instance_response, "Serial no.")
                Attachment = extract_value(instance_response, "Attachments")
                Attachment_names = extract_attachment_ext_names(instance_response)
                # print("Polinked bill Serial_Number:", Serial_Number)
                subsidiary_id = mapping_entity_subsidiary(Entity)
                duedate = mapping_date(duedate)
                trandate = mapping_date(trandate)
                giro_paid = mapping_giro_paid(Giro_paid)
        
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
                
                request_body_bill = generate_request_body(instance_response, "polinkedbill")
                PO_insance = extract_value(instance_response, "PO Approval")
                instance_response_po = get_instance_details(PO_insance[0])
                serial_number_po = extract_value(instance_response_po, "Serial no.")
                matched_id = find_exist_PO(serial_number_po)
                if matched_id is None:
                    result = generate_request_body(instance_response_po, "po")

                    if result is None:
                        Serial_Number = extract_value(instance_response, "Serial no.")
                        # 如果 generate_request_body 返回 None，记录错误并跳过
                        error_message = f"Vendor bill is empty or Entity is DFS Asset Purchase Company Pte Ltd or SHANGHAI DALAI for Serial_Number : {Serial_Number}"
                        error_logger.error(error_message)
                        results.append({"instance_id": Serial_Number, "response": "generate_request_body returned None"})
                        continue
                    
                    
                    request_body_po, serial_number = result
                    if request_body_po is None:
                        continue
                    response_po = create_vendor_bill_in_netsuite(request_body_po)
                    fromId = extract_fromId(response_po)
                    
                    if not fromId:
                        error_logger.error(f"Failed to extract fromId for Polinked serial_number: {Serial_Number} - Response: {response_po}")
                        results.append({"serial_number": Serial_Number, "response": "Failed to extract fromId."})
                        continue
                    
                    request_body_final = {
                        "posttype": "polinkedbill",
                        "fromId": fromId,
                        "duedate": duedate,
                        "custbody_document_date": trandate,
                        # "tranid": "for_testing(ignore)" + str(Serial_Number) + "2",
                        "tranid":Serial_Number,
                        "custbody7": 6637,
                        "custbody_giropaidorpaid": giro_paid,
                        "attachment": attachment_info
                    }
                else:
                    request_body_final = {
                        "posttype": "polinkedbill",
                        "fromId": matched_id,
                        "duedate": duedate,
                        "custbody_document_date": trandate,
                        # "tranid": "for_testing(ignore)" + str(Serial_Number) + "2",
                        "tranid":Invoice_Number,
                        "custbody7": 6637,
                        "custbody_giropaidorpaid": giro_paid,
                        "attachment": attachment_info
                    }
                # formatted_request_body = json.dumps(request_body_final, indent=4, ensure_ascii=False)
                # print("request_body:\n", formatted_request_body)
                response_final = create_vendor_bill_in_netsuite(request_body_final)
                formid_final = extract_fromId(response_final)
                success_message = f"Successfully processed Polinked serial_number: {Serial_Number}"
                result, is_success = handle_response(
                    instance_id,
                    response_final,
                    success_message,
                    success_logger,
                    error_logger,
                    formid_final,
                    Serial_Number
                )
                results.append(result)
            except Exception as e:
                error_logger.error(f"Failed to process Polinked Serial_Number: {Serial_Number} - Exception: {str(e)}")
                results.append({"instance_id": instance_id, "response": str(e)})
    return results

@app.route('/api/bill', methods=['GET'])
def api_bill():
    """
    处理bill审批实例并创建供应商账单
    """
    try:
        results = process_bill_approvals()
        return jsonify({"status": "success", "data": results}), 200
    except Exception as e:
        bill_success_logger, bill_error_logger = get_loggers("bill")
        bill_error_logger.error(f"API /api/bill encountered an error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/po', methods=['GET'])
def api_po():
    """
    处理po审批实例并创建供应商账单
    """
    try:
        results = process_po_approvals()
        return jsonify({"status": "success", "data": results}), 200
    except Exception as e:
        po_success_logger, po_error_logger = get_loggers("po")
        po_error_logger.error(f"API /api/po encountered an error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/polinked', methods=['GET'])
def api_polinked():
    """
    处理polinkedbill审批实例并创建供应商账单
    """
    try:
        results = process_polinked_approvals()
        return jsonify({"status": "success", "data": results}), 200
    except Exception as e:
        polinkedbill_success_logger, polinkedbill_error_logger = get_loggers("polinkedbill")
        polinkedbill_error_logger.error(f"API /api/polinked encountered an error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 全局异常处理器，捕获所有未处理的异常
@app.errorhandler(Exception)
def handle_exception(e):
    default_success_logger, default_error_logger = get_loggers("default")
    default_error_logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({"status": "error", "message": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10083, debug=True)
