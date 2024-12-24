import requests
import base64
import mimetypes
import os
from urllib.parse import urlsplit, urlunsplit

def download_file_as_base64(original_url):
    """
    处理给定的URL，下载文件内容，并将其编码为Base64字符串，同时获取文件名、扩展名和MIME类型。

    步骤：
    1. 替换\\u0026为&
    2. 移除URL中的片段标识符（#及其后的部分）
    3. 下载文件内容
    4. 提取文件名、扩展名和MIME类型
    5. 将文件内容进行Base64编码

    参数：
    - original_url (str): 原始的文件URL

    返回：
    - tuple:
        - base64_encoded (str): 文件内容的Base64编码字符串
        - filename (str): 文件名
        - file_extension (str): 文件扩展名
        - mime_type (str): 文件的MIME类型

    异常：
    - 如果下载失败或编码过程中出错，将抛出相应的异常
    """

    processed_url = original_url.replace('\\u0026', '&')

    split_url = urlsplit(processed_url)
    cleaned_url = urlunsplit((split_url.scheme, split_url.netloc, split_url.path, split_url.query, ''))

    try:
        response = requests.get(cleaned_url)
        response.raise_for_status()  
        file_content = response.content
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"下载文件时出错: {e}")

    try:
  
        content_disposition = response.headers.get('Content-Disposition', '')
        filename = ''
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"')
        else:
      
            filename = os.path.basename(split_url.path)

        file_extension = os.path.splitext(filename)[1].lower()
        if not file_extension:

            mime_type = response.headers.get('Content-Type')
            file_extension = mimetypes.guess_extension(mime_type) or ''


        mime_type = response.headers.get('Content-Type') or mimetypes.guess_type(filename)[0] or 'application/octet-stream'


        base64_encoded = base64.b64encode(file_content).decode('utf-8')

        return base64_encoded, filename, file_extension, mime_type
    except Exception as e:
        raise RuntimeError(f"处理文件时出错: {e}")
