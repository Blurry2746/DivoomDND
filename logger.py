
import logging
import os

# Logger setup: sets up a file logger.

LOG_FILENAME = "divoomdnd.log"
LOG_LEVEL = logging.DEBUG  # Adjust as necessary

# Create a custom logger
logger = logging.getLogger('DivoomDND')
logger.setLevel(LOG_LEVEL)

# Create handlers if not already added (avoid duplicate handlers if logger called multiple times)
if not logger.handlers:
    # Create file handler
    file_handler = logging.FileHandler(LOG_FILENAME, mode='a')  # Append mode
    file_handler.setLevel(LOG_LEVEL)
    
    # Create formatter and add to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)

# Also redirect errors to stderr
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
