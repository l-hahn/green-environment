#!/usr/bin/env python3
import os
import argparse
from time import sleep

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

class DS18B20:
    def __init__(self, device, scale="C", idle_time=2):
        self._scale = scale
        self._idle_time = idle_time
        self._device_path = "/sys/bus/w1/devices"


    def load_devices(self):
        directory = os.scandir(self._device_path)
        self._devices = [
            dev.name for dev in directory
            if dev.is_dir() and dev.name != "w1_bus_master1"
        ]
        directory.close()


    def reset(self):
        self.load_devices()
        


    def devices(self):
        return list(self._devices)


    def set_device_path(self, device_path):
        self._device_path = device_path


    def device_path(self):
        return self._device_path


    def set_scale(self, scale):
        if scale not in ("K", "F", "C"):
            raise ValueError(
                "Unknown scale type '{}'! Needs to be K, F or C!".format(scale)
            )
        self._scale = scale
    
    
    def scale(self):
        return self._scale


    def set_idle_time(self, idle_time):
        self._idle_time = idle_time


    def idle_time(self):
        return self._idle_time

    def get(self):
        current_temp = None
        with open(self._devices, "r") as bytestream:
            data = [
                item.rstrip().split(" ")[-1] for item in bytestream.readlines()
            ]
            if data[0] == "YES":
                temp_raw = int(data[1][2:])
                if temp_raw == -1:
                    return None
                if self._scale == "C":
                    # Celsius temperature scale #
                    current_temp = temp_raw / 1000.0
                elif self._scale == "F":
                    # Fahrenheit temperature scale #
                    current_temp = (temp_raw / 1000.0) * (9/5) + 32.0
                else:
                    # Kelvin temperature scale #
                    current_temp = (temp_raw / 1000.0) + 273.15
        return current_temp


def main():
    """
    A main function that is used, when this module is used as a stand-alone script.
    Arguments can be passed and it will simply print results to std-out.
    """
    pass


if __name__ == "__main__":
    # execute only if run as a script
    main()