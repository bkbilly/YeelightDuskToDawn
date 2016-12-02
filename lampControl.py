#!/usr/bin/python

import socket
import json
import datetime
import pytz
import time
from astral import Astral


bulb_ip = '192.168.2.131'
port = 55443


def getDuskDawnTimes():
    a = Astral()
    a.solar_depression = 'nautical'  # civil, nautical, astronomical
    nowTime = datetime.datetime.now(pytz.timezone('Europe/Athens'))
    sunToday = a['Athens'].sun(date=nowTime, local=True)
    sunTomorrow = a['Athens'].sun(date=nowTime + datetime.timedelta(days=1), local=True)

    timeUntilDusk = int((sunToday['dusk'] - nowTime).total_seconds())
    if timeUntilDusk < 0:
        timeUntilDusk = int((sunTomorrow['dusk'] - nowTime).total_seconds())
    timeUntilDawn = int((sunToday['dawn'] - nowTime).total_seconds())
    if timeUntilDawn < 0:
        timeUntilDawn = int((sunTomorrow['dawn'] - nowTime).total_seconds())
    # duskToDawn = int((sunTomorrow['dawn'] - sunToday['dusk']).total_seconds() / 60)

    print sunToday['dusk']
    print sunTomorrow['dawn']
    return timeUntilDusk, timeUntilDawn  # Minutes, Seconds


def controlBulb(command):
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        msg = json.dumps(command) + "\r\n"
        tcp_socket.connect((bulb_ip, int(port)))
        tcp_socket.send(msg)
        data = tcp_socket.recv(1024)
        print data
        tcp_socket.close()
    except Exception as e:
        print "Unexpected error:", e


while True:
    # TOGGLE = {"id": 1, "method": "toggle", "params": []}
    ON = {"id": 1, "method": "set_power", "params": ["on", "smooth", 500]}  # milliseconds
    OFF = {"id": 1, "method": "set_power", "params": ["off", "smooth", 500]}  # milliseconds

    timeUntilDusk, timeUntilDawn = getDuskDawnTimes()
    print timeUntilDusk, timeUntilDawn

    if (timeUntilDawn < timeUntilDusk):
        setBulbState = "OFF"
        sleeptime = timeUntilDawn
        controlBulb(ON)
    else:
        setBulbState = "ON"
        sleeptime = timeUntilDusk
        controlBulb(OFF)

    print "In %d minutes the bulb is going to be %s" % (sleeptime / 60, setBulbState)
    time.sleep(sleeptime)

    msgCtrl = OFF
    if setBulbState == "ON":
        msgCtrl = ON

    controlBulb(msgCtrl)
    time.sleep(2)
