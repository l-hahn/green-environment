#!/usr/bin/env python3
"""
This module provides a class to interact with the Gies-O-Mat soil moisture
sensor from ramser-elektro.at and is considered mostly to be used on a
Raspberry Pi. With aprorpiate naming and if pigpio is also available,
this class might be used for other SoC like Arduino, Genuino etc.

This module can also be used as a standalone script to retrieve values from.
attached sensors.

Classes: GiesOMat
Functions: main
"""
import argparse
import time
import pigpio



class GiesOMat:
    """
    This class provides a set of functions and methods that can be used to
    interact with the Gies-O-Mat sensor. As values can be set/adjusted during
    runtime, there is no need to instantiate a new object for every config
    change. Multiple sensors can be handled at once by passing a list of
    GPIO pins.

    Methods:
        default_functor(values, **kwargs)
        __init__
        set_gpio(gpio)
        gpio()
        set_pulse(pulse)
        pulse()
        set_sample_rate(sample_rate)
        sample_rate()
        set_callback(call_back_id)
        callback()
        reset()
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
            **kwargs -- arguments that can be evaluated in another function
        """
        if not isinstance(values, list):
            print(values, **kwargs)
        else:
            print("\t".join(str(value) for value in values), **kwargs)

    def __init__(
            self, gpio, pulse=20, sample_rate=5,
            call_back_id=pigpio.RISING_EDGE):
        """
        Constructor to instantiate an object, that is able to handle multiple
        sensors at once.

        Keyword arguments:
            gpio (int, list of ints) -- GPIO pins that are connected to 'OUT'
            pulse (int, optional) -- The time for the charging wave. Defaults to 20.
            sample_rate (int, optional) -- Time span how long to count switches. Defaults to 5.
            call_back_id (int, optional) -- Callback id. Defaults to pigpio.RISING_EDGE.
        """
        self.set_gpio(gpio)
        self.set_pulse(pulse)
        self.set_sample_rate(sample_rate)
        self.set_callback(call_back_id)
        self._pin_mask = 0
        self.reset()

    def set_gpio(self, gpio: "list of ints" or int):
        """
        The function allows to set or update the GPIO pin list of a GiesOMat
        instance, so that pins can be changed/updated.

        Keyword arguments:
            gpio (int, list of ints) -- Sensor pins that are connected to "OUT".
        """
        self._gpio = gpio if isinstance(gpio, list) else [gpio]

    def gpio(self):
        """
        The function to get (by return) the current list of used GPIO pins
        where data is taken from.

        Returns:
            (list of ints) -- Returns the list of used GPIO pins.
        """
        return [gpio_pin for gpio_pin in self._gpio]

    def set_pulse(self, pulse: int):
        """
        Sets the pulse value (in µs) to the instance and on runtime.

        Keyword arguments:
            pulse (int) -- The pulse value in µs.
        """
        self._pulse = pulse

    def pulse(self):
        """
        The function to get (by return) the current pulse value.

        Returns:
            (int) -- The currently used pulse value.
        """
        return self._pulse

    def set_sample_rate(self, sample_rate: int or float):
        """
        Sets the sample_rate value (in deciseconds [10^-1 s])to the instance
        and on runtime.

        Keyword arguments:
            sample_rate (int) -- The sample_rate value in deciseconds.
        """
        self._sample_rate = sample_rate

    def sample_rate(self):
        """
        The function to get (by return) the current sample_rate value.

        Returns:
            (int) -- The currently used sample_rate value.
        """
        return self._sample_rate

    def set_callback(self, call_back_id: int):
        """
        Sets the used callback trigger (when to count, rising, falling switch
        point).

        Keyword arguments:
            call_back_id (int) -- The callback id, e.g. pigpio.RISING_EDGE.
        """
        self._call_back_id = call_back_id

    def callback(self):
        """
        The function to get (by return) the current callback_id value.

        Returns:
            (int) -- The callback_id, please relate to e.g. pigpio.RISING_EDGE.
        """
        return self._call_back_id

    def reset(self):
        """
        This functions resets all necessary runtime variables, so that after
        a configuration change, everything is correctly loaded.
        """
        self._pi = pigpio.pi()
        self._pi.wave_clear()
        for gpio_pin in self._gpio:
            self._pin_mask |= 1 << gpio_pin
            self._pi.set_mode(gpio_pin, pigpio.INPUT)
        self._pulse_gpio = [
            pigpio.pulse(self._pin_mask, 0, self._pulse),
            pigpio.pulse(0, self._pin_mask, self._pulse)
        ]
        self._pi.wave_add_generic(self._pulse_gpio)
        self._wave_id = self._pi.wave_create()
        self._call_backs = [
            self._pi.callback(
                gpio_pin, self._call_back_id
            ) for gpio_pin in self._gpio
        ]
        for callback in self._call_backs:
            callback.reset_tally()

    def get(self, iteration: int = 1):
        """
        Function to get a certain amount of measured values; there is no
        on-line handling. Values will be measured and returned.

        Keyword arguments:
            iteration (int, optional) -- Measured values amount. Defaults to 1.

        Returns:
            (list of list of ints or list of ints) -- The measured values
        """
        # initialise/reset once to have values with beginning!
        for call in self._call_backs:
            call.reset_tally()
        time.sleep(0.1 * self._sample_rate)
        iteration_values = []
        for _ in range(iteration):
            values = [call.tally() for call in self._call_backs]
            iteration_values.append(values)
            for call in self._call_backs:
                call.reset_tally()
            time.sleep(0.1 * self._sample_rate)
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
        # initialise/reset once to have values with beginning!
        for call in self._call_backs:
            call.reset_tally()
        time.sleep(0.1 * self._sample_rate)
        while iteration != 0:
            if iteration > 0:
                iteration -= 1
            values = [call.tally() for call in self._call_backs]
            functor(values, **kwargs)
            for call in self._call_backs:
                call.reset_tally()
            time.sleep(0.1 * self._sample_rate)

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
        description="A short programm to print values from Gies-O-Mat sensor."
    )
    parser.add_argument(
        "-g", metavar="G", nargs="+", type=int, required=True,
        help="GPIO pin number(s), where the OUT sensor(s) pin is/are attached to."
    )
    parser.add_argument(
        "-p", metavar="P", default=20, type=int, required=False,
        help="Set Pulse to P µs, default p = 20µs."
    )
    parser.add_argument(
        "-s", metavar="S", default=5, type=int, required=False,
        help="Set sample rate to S deciseconds [10^-1 s]; default s = 5."
    )
    parser.add_argument(
        "-i", metavar="I", default=10, type=int, required=False,
        help="Number of iterations to get a value; use -1 for infinity."
    )

    args = parser.parse_args()

    gpio_pins = args.g
    iterations = -1 if args.i < 0 else args.i
    pulse = args.p
    sample_rate = args.s

    connector = GiesOMat(
        gpio=gpio_pins,
        pulse=pulse,
        sample_rate=sample_rate,
    )
    connector.run(iterations)


if __name__ == "__main__":
    # execute only if run as a script
    main()
