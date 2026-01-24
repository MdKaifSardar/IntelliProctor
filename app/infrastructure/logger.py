import logging
import sys
from app.config import settings

def setup_logger(name: str = "proctor_app") -> logging.Logger:
    """
    Sets up a structured logger that outputs to console.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(settings.log_level)
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(settings.log_level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
    return logger

# Create a default logger instance for easy import
logger = setup_logger()
