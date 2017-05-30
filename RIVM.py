#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import requests
from requests.exceptions import ConnectionError

domoticz_devicesIdx = {"PM10": 50,
                       "O3": 51,
                       "NO": 52,
                       "CO": 53,
                       "SO2": 54,
                       "NH3": 55,
                       "NO2": 56
                       }

domoticz_server = "http://localhost"
domoticz_port = 8080


class AirQuality:

    def __init__(self, location):
        self.link = "http://www.lml.rivm.nl/xml/actueel.xml"
        self.location = location
        timedata = "http://www.lml.rivm.nl/xml/actueel-update.xml"
        z = requests.get(timedata)
        f = ET.fromstring(z.content)
        data = f.getchildren()[0].getchildren()[0].getchildren()
        year = data[0].text
        month = data[1].text
        day = data[2].text
        hour = data[3].text
        self.fetch()

        print "Fetching data from: %s/%s/%s, hour: %s" % (day, month, year, hour)

    def push(self, device, value):
        try:
            requests.get(
                "%s:%d/json.htm?type=command&param=udevice&idx=%d&nvalue=0&svalue=%s" %
                (domoticz_server, domoticz_port, device, value))
        except ConnectionError:
            print "I wasn't able to contact the domoticz server, is it up?"

    def fetch(self):
        # fetch the data and push it
        z = requests.get(self.link)
        elements = ET.fromstring(z.content).getchildren()[0].getchildren()
        components = {}
        for element in elements:
            data = element.getchildren()
            station = data[2].text
            component = data[3].text
            unit = data[4].text
            value = data[5].text
            if not (station.lower() == self.location.lower()):
                continue

            components[component] = '%s%s' % (value, unit)

        for component in domoticz_devicesIdx.keys():
            device = domoticz_devicesIdx[component]
            try:
                value = components[component]
            except KeyError:
                value = "n/a"

            self.push(device, value)


AirQuality("NL01489")
