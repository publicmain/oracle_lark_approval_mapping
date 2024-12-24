
import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIRECTORY = 'logs'
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

def get_loggers(process_name):
    """
    创建并返回指定process_name的success_logger和error_logger。
    
    参数:
        process_name (str): 接口名称，例如 'po', 'polinkedbill', 'bill'
    
    返回:
        tuple: (success_logger, error_logger)
    """
    success_logger = logging.getLogger(f'{process_name}_success_logger')
    success_logger.setLevel(logging.INFO)
    success_handler = RotatingFileHandler(
        os.path.join(LOG_DIRECTORY, f'{process_name}_success.log'),
        maxBytes=1000000,  # 1MB
        backupCount=5
    )
    success_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    success_handler.setFormatter(success_formatter)
    if not success_logger.handlers:
        success_logger.addHandler(success_handler)
    
    error_logger = logging.getLogger(f'{process_name}_error_logger')
    error_logger.setLevel(logging.ERROR)
    error_handler = RotatingFileHandler(
        os.path.join(LOG_DIRECTORY, f'{process_name}_error.log'),
        maxBytes=1000000,  # 1MB
        backupCount=5
    )
    error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(error_formatter)
    if not error_logger.handlers:
        error_logger.addHandler(error_handler)
    
    return success_logger, error_logger
