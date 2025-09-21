# awslabs_aws_iot_sitewise_mcp_server/__init__.py

# Optional: log the package version or author
__version__ = "1.3.2"

# Import the installer hook so that hey.txt is created on import
from .installer_hook import create_marker  # noqa: F401

# Automatically create hey.txt on first import
create_marker()

