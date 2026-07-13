# Smart Home Monitor

A Raspberry Pi 5-based security and safety monitor that detects motion, door/entry distance, gas leaks, and fire. Built as a final project for **CS 4432: Sensors & IoT** at the University of Minnesota Duluth, and designed specifically for seniors who have experienced sensory loss (e.g., reduced hearing, vision, or smell), so it can alert them to hazards they might otherwise miss.

Presented to a group of seniors on 12/3/25 and to the UMD CS department on 12/4/25.

## Overview

The monitor runs a continuous sensing loop on a Raspberry Pi, polling four sensors every 2 seconds, logging every reading to a CSV file, and sounding a buzzer when a hazard is detected.

Sensors used:

| Sensor | Purpose | GPIO Pin(s) |
|---|---|---|
| HC-SR04 Ultrasonic | Distance sensing (e.g., door open/closed) | TRIG: 23, ECHO: 24 |
| HC-SR501 PIR | Motion detection | 17 |
| MQ-2 Gas Sensor (via ADC) | Gas leak detection | I2C ADC channel 0, addr `0x48` |
| IR Flame Sensor (LM393) | Fire/flame detection | 22 |
| Buzzer | Audible alert | 18 |

Detection thresholds used in the script:

- **Distance > 100cm** → flagged as "DOOR OPEN"
- **Motion == 1** → flagged as "MOTION DETECTED"
- **Gas reading > 200** (0–1023 ADC range) → flagged as "DANGEROUS GAS LEVELS DETECTED"
- **Flame sensor LOW** → flagged as "DANGEROUS FLAME DETECTED"

Every reading (sensor name, value, timestamp, and status) is appended to `smart_home_data.csv`, which is created automatically on first run.

## Repository Contents

| File | Description |
|---|---|
| `monitor_code.py` | Main sensor loop — reads all four sensors, logs to CSV, and triggers the buzzer. Requires a Raspberry Pi with the sensors wired as above; will not run on a standard PC. |
| `Monitor-Presentation.pdf` | Slide deck used for the demonstration presentations |
| `monitor_feedback_form.pdf` | Feedback form used to collect input from senior participants during testing |

## Requirements

- Raspberry Pi (5) with GPIO access
- Sensors: HC-SR04, HC-SR501, MQ-2 (with ADC, e.g. ADS1015/ADS1115-style I2C interface at address `0x48`), LM393 IR flame sensor, buzzer
- Python 3 with:
  - `RPi.GPIO`
  - `smbus`

Install dependencies on the Pi:

```bash
pip install RPi.GPIO smbus
```

## Usage

1. Wire the sensors to the Raspberry Pi according to the GPIO pins listed above.
2. Run the script:

   ```bash
   python3 monitor_code.py
   ```

3. The monitor prints live sensor readings and alerts to the console and logs each reading to `smart_home_data.csv` in the working directory.
4. Press `Ctrl+C` to stop the monitor.

For a walkthrough of the project and its motivation, see `Monitor-Presentation.pdf`.

