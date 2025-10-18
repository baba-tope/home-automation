import json
import logging
import os
import time

import requests

from ..config import WIZ_API_URL, WIZ_DEVICES

WIZ_USERNAME = os.getenv("WIZ_USERNAME")
WIZ_PASSWORD = os.getenv("WIZ_PASSWORD")
WIZ_ACCESS_TOKEN = None

def get_wiz_access_token():
    """Obtains a Wiz access token."""
    try:
        response = requests.post(
            f"{WIZ_API_URL}/user/login",
            json={"email": WIZ_USERNAME, "password": WIZ_PASSWORD},
        )
        response.raise_for_status()
        return response.json()["result"]["accessToken"]
    except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
        logging.error("Error getting Wiz access token: %s", e)
        return None

def control_wiz_bulbs(on_off):
    """Controls Wiz bulbs using the API with retries."""
    global WIZ_ACCESS_TOKEN
    headers = {"Authorization": f"Bearer {WIZ_ACCESS_TOKEN}"}
    for bulb in WIZ_DEVICES:
        state = "on" if on_off else "off"
        data = {"method": "setPilot", "params": {"state": state}}
        num_retries = 3  # Number of retries
        for _ in range(num_retries):
            try:
                response = requests.post(f"{WIZ_API_URL}/lights/{bulb}/state", headers=headers, json=data)
                response.raise_for_status()
                break  # Exit the retry loop if successful
            except requests.exceptions.RequestException as e:
                if response.status_code == 401:
                    logging.warning("Wiz token expired, re-authenticating...")
                    WIZ_ACCESS_TOKEN = get_wiz_access_token()
                    headers = {"Authorization": f"Bearer {WIZ_ACCESS_TOKEN}"}
                else:
                    logging.error("Error controlling Wiz bulb %s: %s", bulb, e)
                if _ == num_retries - 1:  # Check if it's the last retry
                    logging.error("Failed to control Wiz bulb %s after %d retries", bulb, num_retries)
                else:
                    time.sleep(5)  # Wait before retrying
