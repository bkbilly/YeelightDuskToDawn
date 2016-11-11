#!/usr/bin/python

import socket
import json
import datetime
import pytz
import time
from astral import Astral


bulb_ip = '192.168.2.64'
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
    duskToDawn = int((sunTomorrow['dawn'] - sunToday['dusk']).total_seconds() / 60)

    return duskToDawn, timeUntilDusk


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
    duskToDawn, timeUntilDusk = getDuskDawnTimes()
    print timeUntilDusk
    time.sleep(timeUntilDusk)

    # TOGGLE = {"id": 1, "method": "toggle", "params": []}
    ON = {"id": 1, "method": "set_power", "params": ["on", "smooth", 500]}  # milliseconds
    CRON = {"id": 2, "method": "cron_add", "params": [0, duskToDawn]}  # Minutes
    CRON_GET = {"id": 2, "method": "cron_get", "params": [0]}

    controlBulb(ON)
    controlBulb(CRON)
    controlBulb(CRON_GET)
    time.sleep(2)
