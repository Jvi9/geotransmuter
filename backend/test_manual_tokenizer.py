import getpass
import os

# Use environment variables or a file first
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# If credentials aren't found in the environment, fall back to getpass
if not username or not password:
    print("No credentials found in environment variables. Please enter them manually.")
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

print(f"Username: {username}")
print("Password loaded securely.")