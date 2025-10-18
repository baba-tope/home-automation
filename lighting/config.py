import os
from datetime import time as dtime

# Philips Hue
HUE_BRIDGE_IP = "20.20.20.20"
HUE_BULB_IPS = ["2.2.2.2", "3.3.3.3", "4.4.4.4"]

# Wiz
WIZ_API_URL = "https://api.wizconnected.com/v2"
WIZ_DEVICES = ["office_bulb1", "office_bulb2"]

# Kasa
KASA_API_URL = "https://wap.tplinkcloud.com"
KASA_OUTLETS = ["outlet1", "outlet2", "outlet3", "outlet4", "outlet5"]

# Automation Schedule
TURN_ON_TIME = dtime(
    hour=int(os.getenv(key="TURN_ON_HOUR", default=20)),
    minute=int(os.getenv(key="TURN_ON_MINUTE", default=0))
)
TURN_OFF_TIME = dtime(
    hour=int(os.getenv(key="TURN_OFF_HOUR", default=4)),
    minute=int(os.getenv(key="TURN_OFF_MINUTE", default=0))
)
