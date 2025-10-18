import phue
import logging
from ..config import HUE_BRIDGE_IP, HUE_BULB_IPS

def control_hue_bulbs(bridge, on_off):
    """Controls Philips Hue bulbs."""
    try:
        for bulb_ip in HUE_BULB_IPS:
            command = {'on': True, 'bri': 254} if on_off else {'on': False}
            bridge.set_light(bulb_ip, command)
    except phue.PhueRequestTimeout:
        logging.error("Timeout occurred while controlling Hue bulbs.")
    except Exception as e:  
        logging.error("An error occurred while controlling Hue bulbs: %s", e) 
