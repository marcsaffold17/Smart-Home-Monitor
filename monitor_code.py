import RPi.GPIO as GPIO
from smbus import SMBus

import time
import csv
import os
from datetime import datetime

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

PIR = 17  # HC-SR501 PIR Motion Sensor
FLAME = 22  # IR Flame Sensor (LM393 Module)
BUZZER = 18  # Buzzer Module
ULTRASONIC_TRIG = 23  # HC-SR04 Ultrasonic Sensor TRIG
ULTRASONIC_ECHO = 24  # HC-SR04 Ultrasonic Sensor ECHO

# ADC Config              MQ-2 Gas Sensor
bus = SMBus(1)
ADDR = 0x48
GAS = 0  # AIN0

GPIO.setup(PIR, GPIO.IN)
GPIO.setup(FLAME, GPIO.IN)

GPIO.setup(ULTRASONIC_TRIG, GPIO.OUT)
GPIO.setup(ULTRASONIC_ECHO, GPIO.IN)

GPIO.setup(BUZZER, GPIO.OUT)
GPIO.output(BUZZER, GPIO.LOW)

CSV_FILE = 'smart_home_data.csv'
CSV_HEADER = ['Timestamp', 'Sensor', 'Value', 'Detection Status']


def adc(ch: int) -> int:
    bus.write_byte(ADDR, 0x40 | (ch & 0x03))
    bus.read_byte(ADDR)
    return bus.read_byte(ADDR)


# both ultrasonic sensors
def read_distance():
    GPIO.output(ULTRASONIC_TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(ULTRASONIC_TRIG, GPIO.LOW)

    while GPIO.input(ULTRASONIC_ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ULTRASONIC_ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = round(pulse_duration * 17150, 2)

    return distance


# pir
def read_motion():
    return GPIO.input(PIR)


def read_gas():
    return adc(GAS)


def read_flame():
    return GPIO.input(FLAME)


# could change buzzer duration
def activate_buzzer(duration=10):
    GPIO.output(BUZZER, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(BUZZER, GPIO.LOW)


def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(CSV_HEADER)
        print(f"Created new CSV file: {CSV_FILE}")


def insert_to_csv(sensor, value, status):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(CSV_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, sensor, value, status])


# main loop
print("\nSmart home monitor is activated! (Press Ctrl+C to exit)")
initialize_csv()

try:
    while True:
        alert_triggered = False
        distance = read_distance()
        # 0 - 400cm
        if distance > 100:
            status = "DOOR OPEN"
            alert_triggered = True
            print(f"ALERT: DISTANCE DETECTED! Distance: {distance}cm")
        else:
            status = "Door closed"
        insert_to_csv("HC-SR04 Ultrasonic Sensor", distance, status)
        print(f"Distance: {distance}cm - {status}")

        motion = read_motion()
        # 0 - 1
        if motion == 1:
            status = "MOTION DETECTED"
            alert_triggered = True
            print(f"ALERT: MOTION DETECTED!")
        else:
            status = "No motion"
        insert_to_csv("HC-SR501 PIR Motion Sensor", motion, status)
        print(f"Motion: {status} - {motion}")

        gas = read_gas()
        # 0 - 1023
        if gas > 200:
            status = "DANGEROUS GAS LEVELS DETECTED"
            alert_triggered = True
            print(f"ALERT: GAS DETECTED! {gas}")
        else:
            status = "Gas not detected"
        insert_to_csv("MQ-2 Gas Sensor", gas, status)
        print(f"Gas: {gas} - {status}")

        flame = read_flame()
        # 0 - 1
        if flame == GPIO.HIGH:
            status = "Flame not detected"
            print(f"No fire detected")
        else:
            alert_triggered = True
            status = "DANGEROUS FLAME DETECTED"
            print(f"Fire detected")
        insert_to_csv("IR Flame Sensor", flame, status)

        if not alert_triggered:
            GPIO.output(BUZZER, GPIO.HIGH)
        else:
            GPIO.output(BUZZER, GPIO.LOW)

        time.sleep(2)

except KeyboardInterrupt:
    print("\nSmart home monitor shutting down...")
finally:
    bus.close()