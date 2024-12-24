# app.py

from flask import Flask, jsonify
import json
from logger_config import get_loggers  # 导入共享的日志配置

from config import get_tenant_access_token, create_vendor_bill_in_netsuite
from instance import get_current_and_past_week_timestamps, get_approval_instance_ids
from approval_detail import get_instance_details, extract_value, extract_fromId
from field_internel_id import mapping_date, mapping_entity_subsidiary, mapping_giro_paid
from file_util import download_file_as_base64
from request_body import generate_request_body

app = Flask(__name__)

# 添加根路由进行测试
@app.route('/', methods=['GET'])
def home():
    return "Flask API is running!", 200

# 通用的响应处理函数
def handle_response(serial_number, response, success_message, success_logger, error_logger):
    """
    根据响应内容决定记录到success.log还是error.log
    仅提取并记录嵌套的message字段内容到error.log
    """
    if response.get('status_code', 200) >= 400 or 'error' in response:
        print("error")
        message = "Unknown error"
        if 'error' in response:
            try:
                # 解析外层的error JSON字符串
                error_content = json.loads(response['error'])
                if 'message' in error_content.get('error', {}):
                    inner_error_message = error_content['error']['message']
                    # 解析内层的message JSON字符串
                    inner_error_content = json.loads(inner_error_message)
                    message = inner_error_content.get('message', message)
            except json.JSONDecodeError:
                # 如果解析失败，记录原始的error字符串
                message = response['error']
            except Exception as e:
                # 捕获其他可能的异常
                message = f"Error parsing message: {str(e)}"
        error_logger.error(f"Failed to process serial_number: {serial_number} - Message: {message}")
        return {"serial_number": serial_number, "response": message}, False
    else:
        print("success")
        success_logger.info(success_message)
        return {"serial_number": serial_number, "response": response}, True

# 处理一般审批实例并创建供应商账单（bill接口）
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
        if instance_id == "8F292381-5054-4F17-9424-C9D4CFFA596D":
            try:
                instance_response = get_instance_details(instance_id)
                request_body, serial_number = generate_request_body(instance_response, "bill")
                if request_body is None:
                    continue
                response = create_vendor_bill_in_netsuite(request_body)
                result, is_success = handle_response(
                    serial_number,
                    response,
                    f"Successfully processed bill serial_number: {serial_number}",
                    success_logger,
                    error_logger
                )
                results.append(result)
            except Exception as e:
                error_logger.error(f"Failed to process serial_number: {serial_number} - Exception: {str(e)}")
                results.append({"serial_number": serial_number, "response": str(e)})
    return results

# 处理PO审批实例并创建供应商账单（po接口）
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
        if instance_id == "500A0B09-E31D-4CA9-8D98-66EB5306D9B2":
            try:
                instance_response = get_instance_details(instance_id)
                request_body, serial_number= generate_request_body(instance_response, "po")
                if request_body is None:
                    continue
                response = create_vendor_bill_in_netsuite(request_body)
                fromId = extract_fromId(response)
                
                # 检查fromId是否存在，决定是否记录为成功
                if not fromId:
                    error_logger.error(f"Failed to extract fromId for serial_number: {serial_number} - Response: {response}")
                    results.append({"serial_number": serial_number, "response": "Failed to extract fromId."})
                    continue
                
                success_message = f"Successfully processed PO serial_number: {serial_number}, fromId: {fromId}"
                result, is_success = handle_response(
                    instance_id,
                    response,
                    success_message,
                    success_logger,
                    error_logger
                )
                results.append(result)
            except Exception as e:
                error_logger.error(f"Failed to process PO serial_number: {serial_number} - Exception: {str(e)}")
                results.append({"serial_number": serial_number, "response": str(e)})
    return results

# 处理PO链接审批实例并创建供应商账单（polinkedbill接口）
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
    for instance_id in instance_ids:
        if instance_id == "F0D8B55F-01DD-49E2-99BF-5269565C7F4B":
            try:
                instance_response = get_instance_details(instance_id)
                Entity = extract_value(instance_response, "Entity")
                duedate = extract_value(instance_response, "Due Date")
                Giro_paid = extract_value(instance_response, "Giro Pay / Paid")
                trandate = extract_value(instance_response, "Date of Invoice")
                Serial_Number = extract_value(instance_response, "Serial no.")
                Attachment = extract_value(instance_response, "Attachments")
        
                subsidiary_id = mapping_entity_subsidiary(Entity)
                duedate = mapping_date(duedate)
                trandate = mapping_date(trandate)
                giro_paid = mapping_giro_paid(Giro_paid)
        
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
                
                request_body_bill = generate_request_body(instance_response, "polinkedbill")
                PO_insance = extract_value(instance_response, "PO Approval")
                instance_response_po = get_instance_details(PO_insance[0])
                request_body_po, Serial_Number = generate_request_body(instance_response_po, "po")
                if request_body_po is None:
                    continue
                response_po = create_vendor_bill_in_netsuite(request_body_po)
                fromId = extract_fromId(response_po)
                
                if not fromId:
                    error_logger.error(f"Failed to extract fromId for Polinked serial_number: {Serial_Number} - Response: {response_po}")
                    results.append({"Serial_Number": Serial_Number, "response": "Failed to extract fromId."})
                    continue
                
                request_body_final = {
                    "posttype": "polinkedbill",
                    "fromId": fromId,
                    "duedate": duedate,
                    "custbody_document_date": trandate,
                    "tranid": "for_testing(ignore)" + str(Serial_Number),
                    "custbody7": 6637,
                    "custbody_giropaidorpaid": giro_paid,
                    "attachment": attachment_info
                }
                response_final = create_vendor_bill_in_netsuite(request_body_final)
                success_message = f"Successfully processed Polinked Serial_Number: {Serial_Number}, fromId: {fromId}"
                result, is_success = handle_response(
                    instance_id,
                    response_final,
                    success_message,
                    success_logger,
                    error_logger
                )
                results.append(result)
            except Exception as e:
                error_logger.error(f"Failed to process Polinked Serial_Number: {Serial_Number} - Exception: {str(e)}")
                results.append({"Serial_Number": Serial_Number, "response": str(e)})
    return results

# API端点：/api/bill
@app.route('/api/bill', methods=['GET'])
def api_bill():
    """
    处理bill审批实例并创建供应商账单
    """
    try:
        results = process_bill_approvals()
        return jsonify({"status": "success", "data": results}), 200
    except Exception as e:
        # 这里使用bill的error_logger
        bill_success_logger, bill_error_logger = get_loggers("bill")
        bill_error_logger.error(f"API /api/bill encountered an error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# API端点：/api/po
@app.route('/api/po', methods=['GET'])
def api_po():
    """
    处理po审批实例并创建供应商账单
    """
    try:
        results = process_po_approvals()
        return jsonify({"status": "success", "data": results}), 200
    except Exception as e:
        # 这里使用po的error_logger
        po_success_logger, po_error_logger = get_loggers("po")
        po_error_logger.error(f"API /api/po encountered an error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# API端点：/api/polinked
@app.route('/api/polinked', methods=['GET'])
def api_polinked():
    """
    处理polinkedbill审批实例并创建供应商账单
    """
    try:
        results = process_polinked_approvals()
        return jsonify({"status": "success", "data": results}), 200
    except Exception as e:
        # 这里使用polinkedbill的error_logger
        polinkedbill_success_logger, polinkedbill_error_logger = get_loggers("polinkedbill")
        polinkedbill_error_logger.error(f"API /api/polinked encountered an error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 全局异常处理器，捕获所有未处理的异常
@app.errorhandler(Exception)
def handle_exception(e):
    # 根据需要，选择一个默认的日志记录器，例如error_logger
    default_success_logger, default_error_logger = get_loggers("default")
    default_error_logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({"status": "error", "message": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
