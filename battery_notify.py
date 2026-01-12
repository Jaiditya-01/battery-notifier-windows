import psutil
from plyer import notification
import time
import winsound

MAX = 85
INTERVAL = 60

notified = False

while True:
    battery = psutil.sensors_battery()

    if battery is None:
        time.sleep(INTERVAL)
        continue

    percent = battery.percent
    plugged = battery.power_plugged

    if plugged and percent >= MAX and not notified:
        try:
            winsound.Beep(1000, 800)

            notification.notify(
                title="Battery Alert !",
                message=f"Battery reached {percent}%. Please unplug the charger.",
                timeout=10
            )

            notified = True

        except:
            notified = False 

    if percent <= MAX - 3:
        notified = False

    time.sleep(INTERVAL)
