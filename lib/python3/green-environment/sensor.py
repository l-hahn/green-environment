import argparse
import pigpio
import time


class GiesOMat:

    def default_functor(values: "list of ints" or int, **kwargs):
        if type(values) != list:
            print(values, **kwargs)
        else:
            print("\t".join(str(value) for value in values), **kwargs)

    def __init__(
            self, gpio, pulse=20, sample_rate=5,
            call_back_id=pigpio.RISING_EDGE):
        self.set_gpio(gpio)
        self.set_pulse(pulse)
        self.set_sample_rate(sample_rate)
        self.set_callback(call_back_id)
        self._pin_mask = 0
        self.reset()

    def set_gpio(self, gpio: "list of ints" or int):
        self._gpio = gpio if type(gpio) == list else [gpio]

    def gpio(self):
        return [gpio_pin for gpio_pin in self._gpio]

    def set_pulse(self, pulse: int):
        self._pulse = pulse

    def pulse(self):
        return self._pulse

    def set_sample_rate(self, sample_rate: int or float):
        self._sample_rate = sample_rate

    def sample_rate(self):
        return self._sample_rate

    def set_callback(self, call_back_id: int):
        self._call_back_id = call_back_id

    def callback(self):
        return self._call_back_id

    def reset(self):
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

    def get(self, iteration: int):
        iteration_values = []
        for counter in range(iteration):
            values = [call.tally() for call in self._call_backs]
            for call in self._call_backs:
                call.reset_tally()
            time.sleep(0.1 * self._sample_rate)
            iteration_values.append(values)
        return iteration_values

    def run(self, iteration: int=1, functor=default_functor, **kwargs):
        while iteration != 0:
            if iteration > 0:
                iteration -= 1
            values = [call.tally() for call in self._call_backs]
            functor(values, **kwargs)
            for call in self._call_backs:
                call.reset_tally()
            time.sleep(0.1 * self._sample_rate)

    def run_endless(self, functor=default_functor, **kwargs):
        self.run(iteration=-1, **kwargs)


def main():
    parser = argparse.ArgumentParser(
        description="A short programm to print values from Gies-O-Mat sensor."
    )
    parser.add_argument(
        "-g", metavar="G", nargs="+",type=int,required=True,
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