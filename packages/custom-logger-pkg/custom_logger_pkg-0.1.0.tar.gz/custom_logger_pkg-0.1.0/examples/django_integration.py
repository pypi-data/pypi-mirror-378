"""
Django integration examples for the Custom Logger package.

This file shows how to use the logger within Django applications,
including settings configuration and custom handlers.
"""
from django.utils import timezone
from django.db import models
from logger import CustomLogger, LogLevel, LoggerConfig, custom_logger
from logger import LogHandler  # For custom handler example


class DjangoModelHandler(LogHandler):
    """
    Custom log handler that integrates with Django's ORM.

    This example shows how to create a custom handler that
    stores log messages in the database using Django models.
    """
    from django.db import models
    from django.utils import timezone

    class LogEntry(models.Model):
        """Django model for storing log entries."""
        level = models.CharField(max_length=20)
        message = models.TextField()
        caller_info = models.CharField(max_length=255, blank=True)
        timestamp = models.DateTimeField(default=timezone.now)

        class Meta:
            ordering = ['-timestamp']

        def __str__(self):
            return f"{self.level}: {self.message[:50]}..."

    def handle(self, formatted_message: str, level: LogLevel) -> None:
        """
        Store the log message in the database.
        This would normally parse the formatted message to extract components.
        """

        caller = custom_logger.CallerInfo()
        caller_info = caller.get_detailed_caller_info()

        # In a real implementation, parse formatted_message properly
        self.LogEntry.objects.create(
            level=level.name,
            message=formatted_message,
            caller_info=caller_info or ""
        )

def configure_django_logging():
    """Configure Django to use the custom logger."""
    import os

    # Development configuration
    dev_config = LoggerConfig(
        show_caller=True,
        show_timestamp=True,
        color_output=True,  # Keep colors in development
        level=LogLevel.DEBUG
    )

    # Production configuration
    is_production = os.getenv('DJANGO_SETTINGS_MODULE', '').endswith('production')

    if is_production:
        prod_config = LoggerConfig(
            show_caller=False,  # Reduce verbosity in production
            show_timestamp=True,
            color_output=False,  # No colors in production logs
            level=LogLevel.WARNING  # Only warnings and above
        )
        CustomLogger.configure(prod_config)
    else:
        CustomLogger.configure(dev_config)


def django_middleware_example():
    """
    Example of using the logger in Django middleware.
    """
    # This would be in your Django middleware
    class LoggingMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response
            self.logger = CustomLogger.get_instance()

        def __call__(self, request):
            # Log incoming request
            self.logger.info(f"Incoming {request.method} {request.path}")

            response = self.get_response(request)

            # Log response status
            self.logger.info(f"Response {response.status_code} for {request.path}")

            return response

def django_view_example():
    """
    Example of using the logger in Django views.
    """
    def example_view(request):
        logger = CustomLogger.get_instance()

        try:
            logger.info(f"User {request.user} accessed example view")

            # Your view logic here
            result = some_business_logic()

            logger.success("Example view executed successfully")
            return {"status": "success", "data": result}

        except Exception as e:
            logger.error(f"Error in example view: {str(e)}")
            logger.error(f"Error details: {e.__traceback__}")
            return {"status": "error", "message": str(e)}

def django_model_example():
    """
    Example of using the logger in Django models (managers or signals).
    """
    from django.db import models

    class ExampleModel(models.Model):
        name = models.CharField(max_length=100)
        created = models.DateTimeField(auto_now_add=True)

        def save(self, *args, **kwargs):
            logger = CustomLogger.get_instance()
            logger.debug(f"Saving {self.__class__.__name__}: {self.name}")

            try:
                super().save(*args, **kwargs)
                logger.success(f"{self.__class__.__name__} saved successfully")
            except Exception as e:
                logger.error(f"Failed to save {self.__class__.__name__}: {e}")
                raise

        class Meta:
            app_label = 'your_app'

def some_business_logic():
    """Placeholder for business logic."""
    logger = CustomLogger.get_instance()
    logger.info("Business logic execution started")

    # Simulate some work
    result = "Business logic completed"

    logger.info("Business logic execution finished")
    return result


def django_signal_example():
    """
    Example of using the logger in Django signals.
    """
    from django.db.models.signals import post_save
    from django.dispatch import receiver

    @receiver(post_save)
    def log_model_changes(sender, instance, created, **kwargs):
        logger = CustomLogger.get_instance()

        if created:
            logger.info(f"New {sender.__name__} created: {instance}")
        else:
            logger.info(f"{sender.__name__} updated: {instance}")


def demonstrate_django_integration():
    """Run Django integration examples."""
    print("=== Django Integration Examples ===")

    # These would normally be called during Django setup
    configure_django_logging()

    # Test the configuration
    logger = CustomLogger.get_instance()
    logger.info("Django logger configured successfully")

    # In real Django app, these would be in actual views/models
    result = some_business_logic()
    print(f"Result: {result}")

    print("\n=== Django Examples Completed ===")
    print("Note: This is for demonstration only.")
    print("In real Django apps:")
    print("- Configure in settings.py")
    print("- Use in views, models, middleware, signals")
    print("- Create custom handlers for database storage")


if __name__ == "__main__":
    demonstrate_django_integration()
