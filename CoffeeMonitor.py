# Jacob Westra (jbw23)
# CS-326 Final Project: Coffee Monitor
# 4/16/23

# MQTT libraries
import paho.mqtt.client as mqtt

# temperature sensor libraries
import smbus
import time
import sys
import os

# buzzer libraries
import RPi.GPIO as GPIO

# MQTT configuration
BROKER = 'mqtt.eclipseprojects.io'          # broker
PORT = 8883                                 # port
TOPIC = 'jbw23/coffeemonitor'               # topic
CERTS = '/etc/ssl/certs/ca-certificates.crt'# certicfication
USERNAME = 'jbw23'                          # username
PASSWORD = 'coffeemonitor'                  # password

# Temperature sensor configuration
BUS = 1                                     # I2C bus number
ADDRESS = 0x48                              # TC74 I2C bus address
bus = smbus.SMBus(BUS)

# Buzzer configuration
GPIO.setwarnings(False)                     # silence warnings before program starts
GPIO.setmode(GPIO.BCM)
buzzer = 23                                 # buzzer connected to GPIO 23 (see Fritzing diagram)
GPIO.setup(buzzer,GPIO.OUT)                 # setup buzzer

# Coffee maker configuration
last_turned_on = round(time.time()*1000)    # get time, convert to milliseconds
on = 0                                      # tracks if the coffee maker is on (temp > 30ºc)
alert_status = 0                            # tracks if the coffee maker has been on for >30 minutes
alerted = 0                                 # tracks if the alarm has already been sounded, so it's not constantly going off
temp_calibration = 10                       # temperature readings were always off by approximately this amount

# Returns the Unix Epoch time, in milliseconds
def get_epoch_time():
    return round(time.time()*1000)

# update all variables
def update_status():
    # make variables global so they can be accessed in the function
    global last_turned_on
    global on
    global alert_status
    global alerted
    if temp > 30 and on == 0: # if temp is greater than 30ºc (86ºf), consider it on
        on = 1
        last_turned_on = get_epoch_time()

    if temp < 30 and on == 1: # if below the threshold, consider it off
        on = 0

    alert_time = (30 * 60 * 1000) # 1000 milleseconds, 60 seconds, 30 minutes

    if (get_epoch_time() - last_turned_on) > alert_time and (on == 1): # if time on is greater than 30 minutes
        alert_status = 1
    else:
        alert_status = 0

    if alert_status == 1 and alerted == 0:
        alarm()
        alerted = 1

# alarm() sounds the buzzer, called when coffee maker has been on for 30 minutes
def alarm():
    for x in range(5): # buzz 5 times
        GPIO.output(buzzer, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(buzzer, GPIO.LOW)
        time.sleep(0.1)

try:
    client = mqtt.Client()
    client.username_pw_set(USERNAME, password=PASSWORD)
    client.tls_set(CERTS)
    client.connect(BROKER, PORT, 60)                        # attempt connection
    while (True):                                           # run indefinitely
        time.sleep(1)                                       # run this loop every second
        temp = bus.read_byte(ADDRESS) - temp_calibration    # read temperature from sensor
        current_time = get_epoch_time()                     # get the current time (in milliseconds)
        update_status()                                     # update all the variables
        message = 'COFFEEMQTTHEADER-' + str(temp) + "-" + str(current_time) + "-" + str(on) + "-" + str(last_turned_on) + "-" + str(alert_status) # assemble the message with all the variables. 16 byte header
        print(message)                                      # print message before sending (for debugging purposes)
        client.publish(TOPIC, message)                      # send that message over the network
except KeyboardInterrupt:                                   # when program terminated
    GPIO.output(buzzer, GPIO.LOW)                           # make sure buzzer is not buzzing when program stopped
    bus.close()
