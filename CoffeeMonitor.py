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

# The python aspect of this really did take up most of my time, but unfortunately, github displays this project as majority-html - which looks pretty bad. So, here's the beginning of the bee movie script:

# According to all known laws
# of aviation,

# there is no way a bee
# should be able to fly.

# Its wings are too small to get
# its fat little body off the ground.

# The bee, of course, flies anyway

# because bees don't care
# what humans think is impossible.

# Yellow, black. Yellow, black.
# Yellow, black. Yellow, black.

# Ooh, black and yellow!
# Let's shake it up a little.

# Barry! Breakfast is ready!

# Coming!
# Hang on a second.

# Hello?
# - Barry?
# - Adam?
# - Can you believe this is happening?
# - I can't. I'll pick you up.
# Looking sharp.
# Use the stairs. Your father
# paid good money for those.

# Sorry. I'm excited.
# Here's the graduate.
# We're very proud of you, son.
# A perfect report card, all B's.
# Very proud.
# Ma! I got a thing going here.

# You got lint on your fuzz.
# - Ow! That's me!
# - Wave to us! We'll be in row 118,000.
# - Bye!
# Barry, I told you,
# stop flying in the house!

# - Hey, Adam.
# - Hey, Barry.
# - Is that fuzz gel?
# - A little. Special day, graduation.
# Never thought I'd make it.
# Three days grade school,
# three days high school.
# Those were awkward.
# Three days college. I'm glad I took
# a day and hitchhiked around the hive.
# You did come back different.
# - Hi, Barry.
# - Artie, growing a mustache? Looks good.
# - Hear about Frankie?
# - Yeah.
# - You going to the funeral?
# - No, I'm not going.
# Everybody knows,
# sting someone, you die.
# Don't waste it on a squirrel.
# Such a hothead.
# I guess he could have
# just gotten out of the way.
# I love this incorporating
# an amusement park into our day.
# That's why we don't need vacations.
# Boy, quite a bit of pomp...
# under the circumstances.
# - Well, Adam, today we are men.
# - We are!
# - Bee-men.
# - Amen!
# Hallelujah!
# Students, faculty, distinguished bees,
# please welcome Dean Buzzwell.
# Welcome, New Hive Oity
# graduating class of...
# ...9:15.
# That concludes our ceremonies.
# And begins your career
# at Honex Industries!
# Will we pick ourjob today?
# I heard it's just orientation.
# Heads up! Here we go.

