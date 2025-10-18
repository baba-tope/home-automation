import logging
import os
import time
from datetime import datetime, time as dtime
from dotenv import load_dotenv

from device_control import hue, wiz, kasa
from config import TURN_ON_TIME, TURN_OFF_TIME

# Load environment variables from .env file
load_dotenv()

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if __name__ == "__main__":
    while True:
        current_time = datetime.now().time()
        on_off = TURN_ON_TIME <= current_time < TURN_OFF_TIME

        try:
            # Login to Wiz and Kasa if needed (unchanged)
            if not wiz.WIZ_ACCESS_TOKEN:
                wiz.WIZ_ACCESS_TOKEN = wiz.get_wiz_access_token()
            if not kasa.KASA_TOKEN:
                kasa.KASA_TOKEN = kasa.get_kasa_token()

            # Philips Hue Control
            hue_bridge = hue.Bridge(HUE_BRIDGE_IP)
            hue.control_hue_bulbs(hue_bridge, on_off)

            # Wiz Bulb Control
            wiz.control_wiz_bulbs(on_off) 

            # Kasa Outlet Control
            kasa.control_kasa_outlets(on_off)

        # Except Block for all error handling (unchanged)
        except Exception as e:  
        logging.error(f"An error occurred: {e}")
        time.sleep(60)  # Check every minute
