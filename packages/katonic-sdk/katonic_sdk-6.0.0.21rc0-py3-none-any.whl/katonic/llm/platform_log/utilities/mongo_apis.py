import requests
from routes.utilities.constants import SERVER_DOMAIN, PERMISSION_FIND

def find_permission(user_email):
    ENDPOINT = SERVER_DOMAIN + PERMISSION_FIND
    product_type = "ace"
    payload = { 
        "userEmail": user_email,
        "productType": product_type
        }
    response = requests.post(ENDPOINT, json=payload)
    response.raise_for_status()
    return response.json()