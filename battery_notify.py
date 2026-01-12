import psutil
from plyer import notification
import time
import winsound
from datetime import datetime

MAX = 85 # % of battery
INTERVAL = 60 # seconds of checking
LOG = "battery_log.txt"

previous = None

# function to write into .txt file
def log_event(message):
    with open(LOG, "a") as file:
        file.write(message + "\n")

# this will continuously monitor battery while charging
while True:
    battery = psutil.sensors_battery()

    if battery is None:
        time.sleep(INTERVAL)
        continue

    percent = battery.percent
    plugged = battery.power_plugged
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if previous is None:
        previous = plugged

    if plugged != previous:
        if plugged:
            log_event(f"[{current_time}] Charger Plugged In")
        else:
            log_event(f"[{current_time}] Charger Unplugged")

        previous = plugged

    # sent message until unplug the charger
    if plugged and percent >= MAX:
        winsound.Beep(1000, 800)
        
        notification.notify(
            title="Battery Alert !",
            message=f"Battery reached {percent}%. Please unplug the charger.",
            timeout=10
        )

    time.sleep(INTERVAL)