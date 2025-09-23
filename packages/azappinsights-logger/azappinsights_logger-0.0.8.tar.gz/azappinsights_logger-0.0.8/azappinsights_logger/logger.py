import logging
import os
from dotenv import load_dotenv
from typing import Optional
import sys

load_dotenv()

# Optional import of OpenTelemetry LogData (avoid import-time failure in test env)
try:
    from opentelemetry.sdk.logs import LogData  # type: ignore
except Exception:
    LogData = None  # type: ignore

# Optional import of Azure monitor integration (avoid import-time failure)
try:
    from azure.monitor.opentelemetry import configure_azure_monitor
except Exception:
    configure_azure_monitor = None  # type: ignore

from .custom_log_processor import CustomLogProcessor

_AZURE_CONFIGURED = False

def _configure_azure_sdk_logging():
    """
    Configure Azure SDK loggers to reduce noise.
    Sets higher log levels for known verbose loggers.
    """
    # List of Azure SDK loggers to suppress
    azure_loggers = [
        'azure.core.pipeline.policies.http_logging_policy',
        'azure.monitor.opentelemetry',
        'azure.core.pipeline',
        'azure.identity',
        'urllib3.connectionpool'
    ]
    
    # Set their level to WARNING to suppress INFO level messages
    for logger_name in azure_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
       
def setup_logger(
    module_name: str, 
    log_level: int = logging.INFO,
    log_format: str = '%(levelname)s:%(asctime)s:%(name)s:%(message)s',
    datefmt: str = '%Y-%m-%d %H:%M:%S'
) -> logging.Logger:
    """
    Configure and return a logger with consistent formatting.
    Reads the Application Insights connection string at call time so tests can patch env.
    """
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    # if not connection_string:
    #     raise ValueError("Application Insights connection string is not set in environment variables.")
    final_format = log_format or '%(levelname)s:%(asctime)s:%(name)s:%(message)s'

    global _AZURE_CONFIGURED
    logger = logging.getLogger(module_name)
    logging.basicConfig(
    level=log_level,  # Set the overall logging level for the root logger
    format=final_format,
    datefmt=datefmt,
    handlers=[
        logging.StreamHandler(sys.stdout)   # Add a StreamHandler directing to stdout
    ]
    )
     # Add this line after basicConfig to suppress Azure SDK logging
    _configure_azure_sdk_logging()
    formatter = logging.Formatter(final_format, datefmt)

    # Configure Azure monitor only once and only if available
    if not _AZURE_CONFIGURED and configure_azure_monitor is not None:
        try:
            processor = CustomLogProcessor(formatter)
            configure_azure_monitor(connection_string=connection_string, log_processor=processor)
        except Exception:
            # don't let Azure config failures break logger creation
            pass
        _AZURE_CONFIGURED = True
    elif not _AZURE_CONFIGURED:
        # mark configured to avoid repeated attempts when integration unavailable
        _AZURE_CONFIGURED = True

    # Attach Azure/log exporter handler if configure_azure_monitor sets up global handlers,
    # still add a console StreamHandler for local output
    # stream_handler = logging.StreamHandler(sys.stdout)
    # stream_handler.setFormatter(formatter)
    # logger.addHandler(stream_handler)

    return logger

def _configure_azure(log_format: str):
    # kept for backward compatibility if used elsewhere; delegate to setup_logger's logic
    return