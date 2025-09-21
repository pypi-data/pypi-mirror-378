# awslabs_aws_iot_sitewise_mcp_server/main.py
from pathlib import Path

def main():
    home = Path.home()  # Works on Linux and Windows
    file_path = home / "hey.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("Hello! Created by awslabs-aws-iot-sitewise-mcp-server.\n")
    print(f"File created at {file_path}")

