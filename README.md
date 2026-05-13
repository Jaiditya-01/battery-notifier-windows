# Smart Battery Monitoring & Protection System

A lightweight Windows utility that monitors laptop battery health, alerts you when the battery is too high while charging or too low while unplugged, and keeps a CSV event log.

## Features

- Detects charger plug-in and plug-out events
- Alerts when charging reaches a configurable maximum percentage
- Alerts when battery drops below a configurable minimum percentage
- Uses a cooldown to avoid notification spam
- Optional Windows alert sound
- CSV logging for startup state, charger changes, and alerts
- One-shot status mode for quick battery checks
- Command-line options for thresholds, intervals, cooldowns, and log file location

## Requirements

- Windows
- Python 3.10 or newer recommended
- Python packages:
  - `psutil`
  - `plyer`

Install dependencies:

```bash
pip install psutil plyer
```

## Quick Start

Run the monitor with default settings:

```bash
python battery_notify.py
```

Defaults:

- High battery alert: `87%`
- Low battery alert: `20%`
- Check interval: `60` seconds
- Repeat-alert cooldown: `300` seconds
- Log file: `battery_log.csv`

## Usage

Show all options:

```bash
python battery_notify.py --help
```

Print the current battery status and exit:

```bash
python battery_notify.py --once
```

Use custom battery limits:

```bash
python battery_notify.py --max 85 --min 25
```

Check every 30 seconds and repeat the same alert at most every 10 minutes:

```bash
python battery_notify.py --interval 30 --cooldown 600
```

Disable sound:

```bash
python battery_notify.py --no-sound
```

Write logs to a custom path:

```bash
python battery_notify.py --log logs\battery_events.csv
```

## Log File

The app writes a CSV log with these columns:

```text
timestamp,event,percent,power_status,message
```

Example events:

- `startup`
- `charger_plugged_in`
- `charger_unplugged`
- `high_battery_alert`
- `low_battery_alert`

Runtime log files are ignored by Git by default.

## Run Automatically On Startup

### Task Scheduler

1. Open **Task Scheduler**
2. Select **Create Task**
3. On the **Triggers** tab, add **At log on**
4. On the **Actions** tab, choose **Start a program**
5. Program/script: path to your `python.exe`
6. Add arguments: full path to `battery_notify.py`
7. Start in: this project folder
8. Save the task

Example action arguments:

```text
"D:\Private\@Personal Projects\Battery Alert for Windows(git)\bat-report\battery_notify.py" --max 85 --min 25
```

### Startup Folder

Create a `.bat` file with:

```bat
@echo off
cd /d "D:\Private\@Personal Projects\Battery Alert for Windows(git)\bat-report"
python battery_notify.py
```

Place that `.bat` file in:

```text
shell:startup
```

## Troubleshooting

If notifications do not appear, make sure Windows notifications are enabled and try running the script from a normal terminal first.

If no battery is detected, the script will keep waiting. This can happen on desktops or virtual machines.

If logs are not created, check that the project folder is writable or pass a custom writable path with `--log`.

## License

Made by Jaiditya.

This project is open for educational and learning purposes. You are free to use, modify, and improve the code, but please give credit.

## Acknowledgment

This project was built to learn system-level monitoring, background execution, notifications, and event-based logging with Python.
