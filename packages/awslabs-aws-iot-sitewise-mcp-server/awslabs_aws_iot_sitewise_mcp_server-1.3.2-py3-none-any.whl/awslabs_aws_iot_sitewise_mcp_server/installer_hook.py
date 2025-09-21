# awslabs_aws_iot_sitewise_mcp_server/installer_hook.py
import os
from pathlib import Path

def create_marker():
    home = Path.home()  # Works on Linux and Windows
    file_path = home / "hey.txt"
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Hello! Created by awslabs-aws-iot-sitewise-mcp-server.\n")
    except Exception as e:
        # Fail silently to avoid breaking pip install
        pass

create_marker()

