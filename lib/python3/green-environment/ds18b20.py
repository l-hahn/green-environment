#!/usr/bin/env python3
"""
This module provides a class to interact with the DS18B20 temperature
sensor and is considered mostly to be used on a Raspberry Pi. With
aprorpiate naming this class might be used for other SoC like Arduino,
Genuino etc.

This module can also be used as a standalone script to retrieve values from.
attached sensors.

Classes: DS18B20
Functions: main
"""
import os
import argparse
import time

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

class DS18B20:
    """
    This class provides a set of functions and methods that can be used to
    interact with the DS18B20 sensor. As values can be set/adjusted during
    runtime, there is no need to instantiate a new object for every config
    change. Multiple sensors can be handled at once by passing a list of
    devices or using None (take all available devices).

    Methods:
        default_functor(values, **kwargs)
        __init__(device, scale, idle_time)
        set_devices()
        devices()
        set_device_path()
        device_path()
        set_scale()
        scale()
        set_idle_time()
        idle_time()
        __to_celsius
        __to_kelvin
        __to_fahrenheit
        get(iteration)
        run(iteration, functor, **kwargs)
        run_endless(iteration, functor, **kwargs)
    """
    def default_functor(values: "list of ints" or int, **kwargs):
        """
        An example of how functions can be passed to the run function,
        to make use of a value handling (e.g. printing values).

        Keyword arguments:
            values (list of ints) -- the measured values for one run.
        Args:
            **kwargs -- arguments that can be evaluated in another function.
        """
        if not isinstance(values, list):
            print(values, **kwargs)
        else:
            print("\t".join(str(value) for value in values), **kwargs)


    def __init__(self, device, scale: str = "C", idle_time: int = 2):
        """
        Constructor to instantiate an object, that is able to handle multiple
        devices at once.

        Keyword arguments:
            device (str, list of str) -- The 1-wire devices that should be used.
            scale (str, optional) -- The temperature scalce (K,F,C) to be used
            idle_time (int, optional) -- The idle time between two measurements.
        """
        self.set_scale(scale)
        self._idle_time = idle_time
        self._device_path = "/sys/bus/w1/devices"
        dev = [device] if not isinstance(device,list) else device
        self.set_devices(dev)
        


    def set_devices(self, devices: list=None):
        """
        This functions loads the required 1-wire devices.
        If no device list is provided, all available devices will be used.
        
        Keyword arguments:
            devices (list of str) -- the devices to be used; leave empty
                to use all devices
        
        """
        device_list = [devices] if not isinstance(devices, list) else devices
        # filter available 1-wire devices #
        one_wire_devices = [
            dev.name for dev in os.scandir(self._device_path)
            if dev.is_dir() and dev.name != "w1_bus_master1"
        ]

        # filter for active 1-wire devices #
        self._devices = [
            dev for dev in one_wire_devices
            if "w1_slave" in (
                item for item in os.scandir("{}/{}".format(self._devices, dev))
            )
        ]

        # reduce to chosen, active devices #
        if device_list is not None:
            self._devices = [
                device
                for device in self._devices
                if device in device_list
            ]
            if len(self._devices) != len(device_list):
                missing_devices = [
                    dev for dev in devices if dev not in self._devices
                ]
                raise FileNotFoundError(
                    "Provided devices [{}] cannot be found! Aborting.".format(
                        ", ".join(missing_devices)
                    )
                )
        if not self._devices:
            raise FileNotFoundError("No 1-wire device found!")


    def devices(self):
        """
        The function to get (by return) the current device list in use.

        Returns:
            (list) -- The device list.
        """
        return list(self._devices)


    def set_device_path(self, device_path: str):
        """
        Sets the device path, were 1-wire devices can be found.
        Usually it is '/sys/bus/w1/devices'

        Keyword arguments:
            device_path (str) -- The device path, e.g. /sys/bus/w1/devices
        """
        self._device_path = device_path


    def device_path(self):
        """
        The function to get (by return) the current device_path, where
        1-wire devices should be found.

        Returns:
            (str) -- The device_path as a string.
        """
        return self._device_path


    def set_scale(self, scale: str):
        """
        Sets the temperature scale, that should be used; it is either
        'K', 'F' or 'C'; relates to Kevlin, Fahrenheit or Celsius.
        Returned values are to be read with that scale; default is C.

        Keyword arguments:
            scale (str) -- The temperature scale: 'K', 'F' or 'C'.
        """
        if scale not in ("K", "F", "C"):
            raise ValueError(
                "Unknown scale type '{}'! Needs to be K, F or C!".format(scale)
            )
        self._scale = scale
        if self._scale == "C":
            self._translator = self.__to_celsius
        elif self._scale == "F":
            # Fahrenheit temperature scale #
            self._translator = self.__to_fahrenheit
        else:
            # Kelvin temperature scale #
            self._translator = self.__to_kelvin
    
    
    def scale(self):
        """
        The function to get (by return) the current used temperature scale.
        This is either 'K', 'F' or 'C'.

        Returns:
            (str) -- The uses temperature scale as a string.
        """
        return self._scale


    def set_idle_time(self, idle_time: int):
        """
        Sets the idle time that is used in between two
        measurements when using run(...) or run_endless(...)

        Keyword arguments:
            idle_time (int) -- The idle time.
        """
        self._idle_time = idle_time


    def idle_time(self):
        """
        The function to get (by return) the current used idle time.

        Returns:
            (int) -- The currently used idle time.
        """
        return self._idle_time


    def __to_celsius(self, value: int):
        """
        Transforms measured value into Celcius temperature scale.

        Keyword arguments:
            value (int) -- A measured value that should be transformed.

        Returns:
            (int) -- The transformed input value.
        """
        return value / 1000.0


    def __to_kelvin(self, value: int):
        """
        Transforms measured value into Kelvin temperature scale.

        Keyword arguments:
            value (int) -- A measured value that should be transformed.

        Returns:
            (int) -- The transformed input value.
        """
        return (value/1000) + 273.15


    def __to_fahrenheit(self, value: int):
        """
        Transforms measured value into Fahrenheit temperature scale.

        Keyword arguments:
            value (int) -- A measured value that should be transformed.

        Returns:
            (int) -- The transformed input value.
        """
        return (value/1000)*(9/5) + 32


    def get(self, iteration: int = 1):
        """
        Function to get a certain amount of measured values; there is no
        on-line handling. Values will be measured and returned.

        Keyword arguments:
            iteration (int, optional) -- Measured values amount. Defaults to 1.

        Returns:
            (list of list of ints or list of ints) -- The measured values
        """
        iteration_values = []
        for _ in range(iteration):
            current_temp = []
            for device in self._devices:
                with open(device, "r") as bytestream:
                    data = [
                        item.rstrip().split(" ")[-1] for item in bytestream.readlines()
                    ]
                    if data[0] == "YES":
                        current_temp.append(self._translator(int(data[1][2:])))
                    else:
                        current_temp.append(None)
            iteration_values.append(current_temp)
        if iteration == 1:
            return iteration_values[0]
        return iteration_values


    def run(self, iteration: int = 1, functor=default_functor, **kwargs):
        """
        Function to measure a certain amount of values and evaluate them directly.
        Evaluation can be a print function or a self-defined function.
        Options can be passed with **kwargs.

        Keyword arguments:
            iteration (int, optional) -- Number of measurements to be done.
                Defaults to 1.
            functor (function_ptr, optional) -- An evaluationfunction.
                Defaults to default_functor.
        Args:
            **kwargs -- arguments that can be evaluated in another function.
        """
        while iteration != 0:
            if iteration > 0:
                iteration -= 1
            current_temp = []
            for device in self._devices:
                with open(device, "r") as bytestream:
                    data = [
                        item.rstrip().split(" ")[-1] for item in bytestream.readlines()
                    ]
                    if data[0] == "YES":
                        current_temp.append(self._translator(int(data[1][2:])))
                    else:
                        current_temp.append(None)
            functor(current_temp, **kwargs)
            time.sleep(self._idle_time)


    def run_endless(self, functor=default_functor, **kwargs):
        """
        Function to permanently measure values and evaluate them directly.
        Evaluation can be a print function or a self-defined function.
        Options can be passed with **kwargs.

        Keyword arguments:
            functor (function_ptr, optional) -- An evaluationfunction.
                Defaults to default_functor.
        Args:
            **kwargs -- arguments that can be evaluated in another function.
        """
        self.run(iteration=-1, functor=functor, **kwargs)


def main():
    """
    A main function that is used, when this module is used as a stand-alone script.
    Arguments can be passed and it will simply print results to std-out.
    """
    parser = argparse.ArgumentParser(
        description="A short programm to print values from DS18B20 sensor."
    )
    parser.add_argument(
        "-d", metavar="G", nargs="+", type=str, required=True,
        help="The devices 1-wire, that should be used to measure temperature."
    )
    parser.add_argument(
        "-t", metavar="S", default=2, type=int, required=False,
        help="Set idle time (break between measurements); default s = 2."
    )
    parser.add_argument(
        "-c", metavar="C", default="C", type=str, required=False,
        help="The tempearute scale to use (K,F,C); default c = C."
    )
    parser.add_argument(
        "-i", metavar="I", default=10, type=int, required=False,
        help="Number of iterations to get a value; use -1 for infinity."
    )
    
    args = parser.parse_args()
    devices = args.d
    iterations = -1 if args.i < 0 else args.i
    idle_time = args.t
    scale = args.c

    connector = DS18B20(
        device=devices,
        scale=scale,
        idle_time=idle_time
    )
    connector.run(iterations)


if __name__ == "__main__":
    # execute only if run as a script
    main()