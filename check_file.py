import os

file_to_check = "config.yaml"

if os.path.exists(file_to_check):
    print(f"✅ The file '{file_to_check}' exists.")
else:
    print(f"❌ The file '{file_to_check}' does not exist.")