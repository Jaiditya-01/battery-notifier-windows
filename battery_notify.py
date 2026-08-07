import argparse
import csv
import time
import winsound # for notifications
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil
from plyer import notification #for accessing the windows notifications

from pathlib import Path

# This gets the exact folder where your python script is saved
SCRIPT_DIR = Path(__file__).resolve().parent

# This creates the log file in the exact same folder as your script
DEFAULT_LOG_FILE = SCRIPT_DIR / "battery_log.csv"


DEFAULT_HIGH_PERCENT = 85 # change this according to your suitablility
DEFAULT_LOW_PERCENT = 30
DEFAULT_INTERVAL_SECONDS = 60
DEFAULT_ALERT_COOLDOWN_SECONDS = 60


@dataclass(frozen=True)
class BatteryConfig:
    high_percent: int
    low_percent: int
    interval_seconds: int
    alert_cooldown_seconds: int
    log_file: Path
    sound_enabled: bool
    once: bool


def parse_args() -> BatteryConfig:
    parser = argparse.ArgumentParser(
        description="Monitor battery level and alert when charging limits are reached."
    )
    parser.add_argument(
        "--max",
        type=int,
        default=DEFAULT_HIGH_PERCENT,
        help=f"Alert while plugged in at or above this percentage. Default: {DEFAULT_HIGH_PERCENT}.",
    )
    parser.add_argument(
        "--min",
        type=int,
        default=DEFAULT_LOW_PERCENT,
        help=f"Alert while unplugged at or below this percentage. Default: {DEFAULT_LOW_PERCENT}.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL_SECONDS,
        help=f"Seconds between battery checks. Default: {DEFAULT_INTERVAL_SECONDS}.",
    )
    parser.add_argument(
        "--cooldown",
        type=int,
        default=DEFAULT_ALERT_COOLDOWN_SECONDS,
        help=f"Seconds to wait before repeating the same alert. Default: {DEFAULT_ALERT_COOLDOWN_SECONDS}.",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=Path(DEFAULT_LOG_FILE),
        help=f"CSV log file path. Default: {DEFAULT_LOG_FILE}.",
    )
    parser.add_argument(
        "--no-sound",
        action="store_true",
        help="Disable the short Windows alert sound.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Print the current battery status and exit.",
    )

    args = parser.parse_args()
    validate_args(args)

    return BatteryConfig(
        high_percent=args.max,
        low_percent=args.min,
        interval_seconds=args.interval,
        alert_cooldown_seconds=args.cooldown,
        log_file=args.log,
        sound_enabled=not args.no_sound,
        once=args.once,
    )


def validate_args(args: argparse.Namespace) -> None:
    if not 1 <= args.min <= 100:
        raise SystemExit("--min must be between 1 and 100.")
    if not 1 <= args.max <= 100:
        raise SystemExit("--max must be between 1 and 100.")
    if args.min >= args.max:
        raise SystemExit("--min must be lower than --max.")
    if args.interval < 5:
        raise SystemExit("--interval must be at least 5 seconds.")
    if args.cooldown < args.interval:
        raise SystemExit("--cooldown must be greater than or equal to --interval.")


def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_battery_status() -> Any | None:
    return psutil.sensors_battery()


def format_power_status(is_plugged: bool) -> str:
    return "plugged in" if is_plugged else "unplugged"


def ensure_log_header(log_file: Path) -> None:
    if log_file.exists() and log_file.stat().st_size > 0:
        return

    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "event", "percent", "power_status", "message"])


def log_event(config: BatteryConfig, event: str, percent: int | float, plugged: bool, message: str) -> None:
    ensure_log_header(config.log_file)
    with config.log_file.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([get_timestamp(), event, percent, format_power_status(plugged), message])


def play_alert_sound(enabled: bool) -> None:
    if enabled:
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)


def send_notification(title: str, message: str, sound_enabled: bool) -> None:
    notification.notify(title=title, message=message, timeout=8)
    play_alert_sound(sound_enabled)


def maybe_send_alert(
    config: BatteryConfig,
    alert_key: str,
    title: str,
    message: str,
    last_alert_at: dict[str, float],
) -> bool:
    now = time.monotonic()
    previous_alert = last_alert_at.get(alert_key, 0)

    if now - previous_alert < config.alert_cooldown_seconds:
        return False

    send_notification(title, message, config.sound_enabled)
    last_alert_at[alert_key] = now
    return True


def print_status(percent: int | float, plugged: bool, secsleft: int | None) -> None:
    status = format_power_status(plugged)
    time_left = "unknown"

    if secsleft not in (None, psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN):
        hours, remainder = divmod(secsleft, 3600)
        minutes = remainder // 60
        time_left = f"{hours}h {minutes}m"

    print(f"Battery: {percent}% | Power: {status} | Time remaining: {time_left}")


def monitor(config: BatteryConfig) -> None:
    previous_plugged: bool | None = None
    last_alert_at: dict[str, float] = {}

    while True:
        battery = get_battery_status()

        if battery is None:
            print("No battery detected. Waiting for the next check...")
            time.sleep(config.interval_seconds)
            continue

        percent = battery.percent
        plugged = battery.power_plugged

        if config.once:
            print_status(percent, plugged, battery.secsleft)
            return

        if previous_plugged is None:
            previous_plugged = plugged
            log_event(
                config,
                "startup",
                percent,
                plugged,
                f"Monitoring started while charger was {format_power_status(plugged)}.",
            )

        if plugged != previous_plugged:
            event = "charger_plugged_in" if plugged else "charger_unplugged"
            message = f"Charger {format_power_status(plugged)} at {percent}%."
            log_event(config, event, percent, plugged, message)
            previous_plugged = plugged
            last_alert_at.clear()

        if plugged and percent >= config.high_percent:
            message = f"Battery reached {percent}%. Please unplug the charger."
            if maybe_send_alert(config, "high", "Battery Full Alert", message, last_alert_at):
                log_event(config, "high_battery_alert", percent, plugged, message)

        if not plugged and percent <= config.low_percent:
            message = f"Battery is down to {percent}%. Please plug in the charger."
            if maybe_send_alert(config, "low", "Low Battery Alert", message, last_alert_at):
                log_event(config, "low_battery_alert", percent, plugged, message)

        time.sleep(config.interval_seconds)


def main() -> None:
    config = parse_args()
    monitor(config)


if __name__ == "__main__":
    main() # calls the final function
