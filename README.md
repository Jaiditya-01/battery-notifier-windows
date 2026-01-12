# Smart Battery Monitoring & Protection System

A simple Python-based background utility that monitors laptop battery status, sends repeated alerts to prevent overcharging, and logs charger plug-in and plug-out events with timestamps.

---

## Features

- **Detects charger plugged-in and unplugged status**
- **Sends repeated notifications** when battery reaches a safe limit
- **Logs date and time** of charging events in a text file
- **Runs continuously** in the background
- Can be configured to **start automatically on system startup**

---

## Requirements

- **Python 3**
- Required libraries:
  - `psutil`
  - `plyer`

Install dependencies using:
```bash
pip install psutil plyer
```

> This project is intended for **Windows systems**.

---

## How to Run

1. Download or clone the repository  
2. Open a terminal inside the project folder  
3. Run the script:

```bash
python battery_notifier.py
```

The program will now monitor the battery at regular intervals.

---

## Log File

- A file named **`battery_log.txt`** is created automatically  
- It stores timestamps when:
  - Charger is plugged in
  - Charger is unplugged

**Example:**
```
[YYYY-MM-DD HH:MM:SS] Charger Plugged In
[YYYY-MM-DD HH:MM:SS] Charger Unplugged
```

---

## Configuration

You can modify the following values inside the script:

```python
MAX = 85        # Safe battery percentage
INTERVAL = 60   # Time interval in seconds
```

---

## Run Automatically on Startup

### Method 1: Task Scheduler (Recommended)

1. Open **Task Scheduler**
2. Create a new task
3. Set trigger as **When user logs in**
4. Set action to **Start a program**
5. Select `python.exe`
6. Pass the script file as an argument
7. Set the project folder as the start location

---

### Method 2: Startup Folder

1. Create a `.bat` file that runs the Python script  
2. Place the `.bat` file in the system Startup folder  
3. Ensure Python is added to system PATH  

---

## Troubleshooting

**Log file not created?**
- The file is created only when a charger plug/unplug event occurs  
- Ensure the script is run from the intended folder  

**No notification received?**
- Check if the battery percentage has crossed the set limit  
- Run the terminal as administrator if required  

---

## License

Made by Jaiditya!!
This project is open for educational and learning purposes.  
You are free to use, modify, and improve the code but don't forget to give credit :)

---

## Acknowledgment

This project was developed to understand **system-level monitoring**, **background execution**, and **event-based logging** using Python.