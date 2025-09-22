"""
Centralized logging module for HATS framework.
Provides consistent logging configuration across all modules.
"""

import logging
import os
from datetime import datetime
from typing import Optional


class HATSFormatter(logging.Formatter):
    """Custom formatter for HATS logging."""
    
    def __init__(self):
        super().__init__()
        self.fmt = "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s"
        self.datefmt = "%Y-%m-%d %H:%M:%S"
    
    def format(self, record):
        """Format log record with color coding for different levels."""
        # Color codes for different log levels
        colors = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m'  # Magenta
        }
        reset = '\033[0m'
        
        # Add color to level name
        if record.levelname in colors:
            record.levelname = f"{colors[record.levelname]}{record.levelname}{reset}"
        
        formatter = logging.Formatter(self.fmt, self.datefmt)
        return formatter.format(record)


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name (str): Logger name (usually __name__)
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        # Set level
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(HATSFormatter())
        logger.addHandler(console_handler)
        
        # Create file handler
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_filename = os.path.join(log_dir, f"hats_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        
        # File handler uses a different format (no colors)
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Prevent propagation to avoid duplicate logs
        logger.propagate = False
    
    return logger


def set_log_level(level: str):
    """
    Set the global log level for all HATS loggers.
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Update all existing HATS loggers
    for logger_name in logging.Logger.manager.loggerDict:
        if logger_name.startswith('hats'):
            logger = logging.getLogger(logger_name)
            logger.setLevel(log_level)
            for handler in logger.handlers:
                handler.setLevel(log_level)


def enable_debug_logging():
    """Enable debug logging for troubleshooting."""
    set_log_level("DEBUG")


def disable_console_logging():
    """Disable console output (keep only file logging)."""
    for logger_name in logging.Logger.manager.loggerDict:
        if logger_name.startswith('hats'):
            logger = logging.getLogger(logger_name)
            # Remove console handlers
            logger.handlers = [h for h in logger.handlers if not isinstance(h, logging.StreamHandler)]


def log_execution_time(func):
    """
    Decorator to log function execution time.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} completed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {str(e)}")
            raise
    
    return wrapper


def log_tool_execution(tool_name: str, target: str, command: str):
    """
    Log tool execution details.
    
    Args:
        tool_name (str): Name of the tool being executed
        target (str): Target of the tool
        command (str): Command being executed
    """
    logger = get_logger("hats.execution")
    logger.info(f"Executing {tool_name} on {target}")
    logger.debug(f"Command: {command}")


def log_tool_result(tool_name: str, success: bool, execution_time: float, output_size: int = 0):
    """
    Log tool execution results.
    
    Args:
        tool_name (str): Name of the tool
        success (bool): Whether execution was successful
        execution_time (float): Execution time in seconds
        output_size (int): Size of output in characters
    """
    logger = get_logger("hats.execution")
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"{tool_name} {status} - Time: {execution_time:.2f}s, Output: {output_size} chars")


class LogContext:
    """Context manager for logging with additional context."""
    
    def __init__(self, logger: logging.Logger, context: str):
        """
        Initialize log context.
        
        Args:
            logger (logging.Logger): Logger instance
            context (str): Context description
        """
        self.logger = logger
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        """Enter the context."""
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.context}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"Completed {self.context} in {duration:.2f} seconds")
        else:
            self.logger.error(f"Failed {self.context} after {duration:.2f} seconds: {str(exc_val)}")
        
        # Don't suppress exceptions
        return False
