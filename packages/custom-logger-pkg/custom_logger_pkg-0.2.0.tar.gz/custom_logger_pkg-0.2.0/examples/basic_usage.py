"""
Basic usage examples for the Custom Logger package.

This file demonstrates the core functionality and different ways
to use the logger in your Python applications.
"""

from logger import CustomLogger, LogLevel, LoggerConfig, debug, info, warning, error, success, critical

def basic_usage():
    """Basic usage examples using module-level functions."""
    print("=== Basic Usage Examples ===")

    debug("This is a debug message - for development")
    info("Application started successfully")
    success("Configuration loaded successfully")
    warning("This is a warning - something to watch")
    error("An error occurred during processing")
    critical("Critical error - system might be unstable")

    print()

def oop_usage():
    """Object-oriented usage with configuration."""
    print("=== Object-Oriented Usage Examples ===")

    # Get singleton instance
    logger = CustomLogger.get_instance()

    # Use object-oriented methods
    logger.debug("Debug from OOP logger")
    logger.info("Info from OOP logger")
    logger.warning("Warning from OOP logger")
    logger.error("Error from OOP logger")
    logger.critical("Critical from OOP logger")
    logger.success("Success from OOP logger")

    print()

def custom_config_usage():
    """Usage with custom configuration."""
    print("=== Custom Configuration Examples ===")

    # Create configuration for development
    dev_config = LoggerConfig(
        show_caller=True,        # Show caller information
        show_timestamp=True,     # Show timestamps
        color_output=True,       # Enable colors
        level=LogLevel.DEBUG     # Show all log levels including debug
    )

    # Create logger with custom config
    dev_logger = CustomLogger(dev_config)

    dev_logger.debug("Debug with caller info")
    dev_logger.info("Info message with timestamp")
    dev_logger.success("Success message")

    print()

def enum_usage():
    """Direct enum usage examples."""
    print("=== Enum-Based Logging Examples ===")

    logger = CustomLogger.get_instance()

    # Using enums directly
    logger.log("Direct enum usage - INFO level", LogLevel.INFO)
    logger.log("Direct enum usage - ERROR level", LogLevel.ERROR)
    logger.log("Direct enum usage - DEBUG level", LogLevel.DEBUG)

    print()

def production_config():
    """Production-ready configuration."""
    print("=== Production Configuration Example ===")

    # Configure for production (minimal output, no colors for log files)
    prod_config = LoggerConfig(
        show_caller=False,       # Don't show caller info in production
        show_timestamp=True,     # But do show timestamps
        color_output=False,      # No colors for log files
        level=LogLevel.WARNING   # Only show warnings and above
    )

    prod_logger = CustomLogger(prod_config)
    prod_logger.warning("Warning level log")
    prod_logger.error("Error level log")
    prod_logger.critical("Critical level log")
    # Debug and info won't show with WARNING level minimum

    print()

if __name__ == "__main__":
    """Run all examples."""
    basic_usage()
    oop_usage()
    custom_config_usage()
    enum_usage()
    production_config()

    print("=== All examples completed! ===")
    print("\nFor Django integration examples, see: examples/django_integration.py")
    print("For custom handler examples, see: examples/custom_handlers.py")
