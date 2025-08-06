import os

file_to_delete = "config.yaml"

if os.path.exists(file_to_delete):
    os.remove(file_to_delete)
    print(f"Successfully deleted {file_to_delete}")
else:
    print(f"{file_to_delete} not found.")