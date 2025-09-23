"""
Custom Logger Package - Professional Object-Oriented Logger for Python

A feature-rich, object-oriented logger that follows SOLID principles and best practices.
Perfect for Django applications, web services, and any Python project requiring
sophisticated logging capabilities.

Main Components:
- CustomLogger: Main logger class with singleton pattern
- LogLevel: Enum for type-safe log levels
- LoggerConfig: Configuration management
- LogFormatter: Message formatting
- LogHandler: Abstract handler for different output types
- ConsoleLogHandler: Console output handler
- CallerInfo: Caller information extraction

Features:
- Object-oriented design following SOLID principles
- Singleton pattern for global access
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL, SUCCESS)
- Colored output with colorama
- Configurable caller information
- Timestamps and detailed formatting
- Extensible architecture for custom handlers
- Full backward compatibility with functional interface

Usage:
    # Traditional usage
    from custom_logger import info, debug
    info("Your message")

    # Object-oriented usage
    from custom_logger import CustomLogger, LogLevel
    logger = CustomLogger.get_instance()
    logger.info("Your message")
    logger.log("Direct enum usage", LogLevel.INFO)

For more examples, see: examples/
"""

__version__ = "1.0.0"
__author__ = "Custom Logger Developer"
__email__ = "contact@example.com"
__license__ = "MIT"

# Import main components for easy access
from .logger import (
    CustomLogger,
    LogLevel,
    LoggerConfig,
    LogFormatter,
    LogHandler,
    ConsoleLogHandler,
    CallerInfo,
    debug,
    info,
    warning,
    error,
    critical,
    success,
    custom_logger
)

__all__ = [
    # Main classes
    'CustomLogger',
    'LogLevel',
    'LoggerConfig',
    'LogFormatter',
    'LogHandler',
    'ConsoleLogHandler',
    'CallerInfo',
    # Convenience functions
    'debug',
    'info',
    'warning',
    'error',
    'critical',
    'success',
    'custom_logger',
    # Metadata
    '__version__',
    '__author__',
    '__email__',
    '__license__',
]
