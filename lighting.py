import json  # For handling JSON responses
import logging  # For logging errors
import os  # For environment variables
import time
from datetime import datetime
from datetime import time as dtime

import phue
import requests
from dotenv import load_dotenv  # For loading credentials from .env file

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Use secure code best practices!
HUE_BRIDGE_IP = "20.20.20.20"
HUE_BULB_IPS = ["2.2.2.2", "3.3.3.3", "4.4.4.4"]

# Sample Wiz and Kasa device info (replace with actual data if available)
WIZ_DEVICES = ["office_bulb1", "office_bulb2"]  
KASA_OUTLETS = ["outlet1", "outlet2", "outlet3", "outlet4", "outlet5"] 

# Automation Schedule (Use secure code best practices)
TURN_ON_TIME = dtime(
    hour=int(os.getenv(key="TURN_ON_HOUR", default=20)),
    minute=int(os.getenv(key="TURN_ON_MINUTE", default=0))
)
TURN_OFF_TIME = dtime(
    hour=int(os.getenv(key="TURN_OFF_HOUR", default=4)),
    minute=int(os.getenv(key="TURN_OFF_MINUTE", default=0))
)

# Wiz API Configuration (Use secure code best practices)
WIZ_API_URL = "https://api.wizconnected.com/v2"
WIZ_USERNAME = os.getenv("WIZ_USERNAME")
WIZ_PASSWORD = os.getenv("WIZ_PASSWORD")
WIZ_ACCESS_TOKEN = None

# Kasa API Configuration (Use secure code best practices)
KASA_API_URL = "https://wap.tplinkcloud.com"
KASA_EMAIL = os.getenv("KASA_EMAIL")
KASA_PASSWORD = os.getenv("KASA_PASSWORD")
KASA_TOKEN = None  # Will be fetched during login

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --- Functions ---
def get_wiz_access_token():
    """Obtains a Wiz access token using the provided credentials."""
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

def control_hue_bulbs(bridge, on_off):
    """Controls the Philips Hue bulbs."""
    try:
        for bulb_ip in HUE_BULB_IPS:
            command = {'on': True, 'bri': 254} if on_off else {'on': False}  # Full brightness when on
            bridge.set_light(bulb_ip, command)
    except phue.PhueRegistrationException as e:
        logging.error("Hue bridge registration error: %s", e)
    except phue.PhueRequestTimeout as e:
        logging.error("Timeout occurred while controlling Hue bulbs: %s", e)
    except requests.exceptions.RequestException as e:
        logging.error("Error making API request: %s", e)
    except KeyError as e:
        logging.error("Missing key in API response: %s", e)
    except json.JSONDecodeError as e:
        logging.error("Error decoding JSON response: %s", e)
    except Exception as e:
        logging.error("Unexpected error occurred: %s", e)

def control_wiz_bulbs(on_off):
    """Controls the Wiz bulbs using the Wiz API."""
    headers = {"Authorization": f"Bearer {WIZ_ACCESS_TOKEN}"}
    for bulb in WIZ_DEVICES:
        state = "on" if on_off else "off"
        data = {"method": "setPilot", "params": {"state": state}}
        response = requests.post(f"{WIZ_API_URL}/lights/{bulb}/state", headers=headers, json=data)
        response.raise_for_status()

        # Retry logic in case of failure
        if response.status_code != 200:
            logging.error("Failed to control Wiz bulb %s with status code %d", bulb, response.status_code)
            time.sleep(5)  # Wait for 5 seconds before retrying
            continue    # Wiz API Call with Retries

def control_kasa_outlets(on_off):
    """Controls the Kasa outlets using the Kasa API."""
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
        try:
            response = requests.post(f"{KASA_API_URL}", headers=headers, json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error controlling Kasa outlet {outlet}: {e}")

# --- Main Automation Loop ---
if __name__ == "__main__":
    while True:
        current_time = datetime.now().time()

        try:
            # Login to Wiz and Kasa if needed
            if not WIZ_ACCESS_TOKEN:
                WIZ_ACCESS_TOKEN = get_wiz_access_token()
            if not KASA_TOKEN:
                KASA_TOKEN = get_kasa_token()

            # Philips Hue Control
            hue_bridge = phue.Bridge(HUE_BRIDGE_IP)
            if TURN_ON_TIME <= current_time < TURN_OFF_TIME:
                control_hue_bulbs(hue_bridge, on_off=True) 
            else:
                control_hue_bulbs(hue_bridge, on_off=False)

            # Wiz Bulb Control 
            control_wiz_bulbs(on_off=(TURN_ON_TIME <= current_time < TURN_OFF_TIME))

            # Kasa Outlet Control 
            control_kasa_outlets(on_off=(TURN_ON_TIME <= current_time < TURN_OFF_TIME))

        # Except Block for all error handling
        except (requests.exceptions.RequestException, phue.PhueRegistrationException, KeyError, json.JSONDecodeError, Exception) as e:  
            logging.error("An error occurred: %s", e)  

        time.sleep(60)  # Check every minute.
