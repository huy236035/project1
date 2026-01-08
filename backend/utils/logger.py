"""
Logging utility
"""
import logging
from datetime import datetime

def setup_logger(name: str = "route_finder", level: int = logging.INFO):
    """
    Setup logger
    
    Args:
        name: Tên logger
        level: Log level
    
    Returns:
        Logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# Logger mặc định
logger = setup_logger()

