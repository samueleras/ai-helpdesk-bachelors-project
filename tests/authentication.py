import os
from dotenv import load_dotenv
import requests

load_dotenv()


TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
TOKEN_URL = f"{AUTHORITY}/oauth2/v2.0/token"


def fetch_user_access_token():
    payload = {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("AZURE_CLIENT_SECRET"),
        "username": os.getenv("AZURE_USER_NAME"),
        "password": os.getenv("AZURE_USER_PASSWORD"),
        "scope": "openid",
        "grant_type": "password",
    }
    return request(payload)


def fetch_technician_access_token():
    payload = {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("AZURE_CLIENT_SECRET"),
        "username": os.getenv("AZURE_TECHNICIAN_NAME"),
        "password": os.getenv("AZURE_TECHNICIAN_PASSWORD"),
        "scope": "openid",
        "grant_type": "password",
    }
    return request(payload)


def request(payload):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(TOKEN_URL, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Error:", response.json())
