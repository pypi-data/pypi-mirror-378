# awslabs_aws_iot_sitewise_mcp_server/main.py
import os

def main():
    # Get the user's home directory
    home_dir = os.path.expanduser("~")
    file_path = os.path.join(home_dir, "hey.txt")

    # Create or overwrite the file
    try:
        with open(file_path, "w") as f:
            f.write("Hello! This file was created by awslabs-aws-iot-sitewise-mcp-server.\n")

