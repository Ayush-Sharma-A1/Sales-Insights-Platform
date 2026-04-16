"""
Logging configuration for the application.
Provides structured logging with file and console handlers.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

class Logger:
    """Centralized logging management"""
    
    _loggers = {}
    
    @staticmethod
    def get_logger(name: str, log_dir: Optional[Path] = None) -> logging.Logger:
        """
        Get or create a logger instance with both file and console handlers.
        
        Args:
            name: Logger name (typically __name__)
            log_dir: Directory for log files
            
        Returns:
            Configured logger instance
        """
        if name in Logger._loggers:
            return Logger._loggers[name]
        
        from config.settings import config
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Formatter
        formatter = logging.Formatter(config.LOG_FORMAT)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        if log_dir is None:
            log_dir = config.LOGS_DIR
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"{name.replace('.', '_')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        Logger._loggers[name] = logger
        return logger
