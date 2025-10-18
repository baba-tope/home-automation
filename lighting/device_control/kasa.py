import json
import logging
import os
import time

import requests

from ..config import KASA_API_URL, KASA_OUTLETS

KASA_EMAIL = os.getenv("KASA_EMAIL")
KASA_PASSWORD = os.getenv("KASA_PASSWORD")
KASA_TOKEN = None

def get_kasa_token():
    """Obtains a Kasa token using the provided credentials."""
    try:
        response = requests.post(
            f"{KASA_API_URL}", 
            json={
                "method": "login", 
                "params": {
                    "appType": "Kasa_Android",
                    "cloudUserName": KASA_EMAIL, 
                    "cloudPassword": KASA_PASSWORD, 
                    "terminalUUID": "random_uuid"  # Generate a proper UUID here
                }
            }
        )
        response.raise_for_status()  # Raise an exception if the request fails
        return response.json()["result"]["token"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting Kasa token: {e}")
        return None  # Return None to indicate failure

def control_kasa_outlets(on_off):
    """Controls the Kasa outlets using the Kasa API with retries."""
    headers = {"Authorization": f"Bearer {KASA_TOKEN}"}
    for outlet in KASA_OUTLETS:
        state = 1 if on_off else 0  # Directly use 1 or 0 for state
        data = {
            "method": "passthrough",
            "params": {
                "deviceId": outlet,
                "requestData": json.dumps({"system": {"set_relay_state": {"state": state}}})
            }
        }
        num_retries = 3  # Number of retries
        for _ in range(num_retries):
            try:
                response = requests.post(KASA_API_URL, headers=headers, json=data)
                response.raise_for_status()
                break  # Exit the retry loop if successful
            except requests.exceptions.RequestException as e:
                logging.error("Error controlling Kasa outlet %s: %s", outlet, e)
                if _ == num_retries - 1:  # Check if it's the last retry
                    logging.error("Failed to control Kasa outlet %s after %d retries", outlet, num_retries)
                else:
                    time.sleep(5)  # Wait before retrying
