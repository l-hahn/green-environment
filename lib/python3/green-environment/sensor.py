import pigpio
import time


class giesomat:

    def default_functor(values, **kwargs):
        if type(values) not in (int, float, list):
            raise ValueError("values not a list or number")
        if type(values) == list:
            for value in values:
                if type(value) not in (int, float):
                    raise ValueError("GPIO needs to be integer!")
            print("\t".join(str(value) for value in values), **kwargs)
        else:
            print(values, **kwargs)

    def __init__(
            self, gpio, pulse=20, sample_rate=5,
            call_back_id=pigpio.RISING_EDGE):
        self.set_gpio(gpio)
        self.set_pulse(pulse)
        self.set_sample_rate(sample_rate)
        self.set_callback(call_back_id)
        self._pin_mask = 0
        self.reset()

    def set_gpio(self, gpio):
        if type(gpio) not in (int, list):
            raise ValueError("GPIO not a list or integer")
        if type(gpio) == list:
            for gpio_pin in gpio:
                if type(gpio_pin) != int:
                    raise ValueError("GPIO needs to be integer!")
        self._gpio = gpio if type(gpio) == list else [gpio]

    def gpio(self):
        return [gpio_pin for gpio_pin in self._gpio]

    def set_pulse(self, pulse):
        if type(pulse) not in (int, float):
            raise ValueError("Pulse needs to be integer!")
        self._pulse = pulse

    def pulse(self):
        return self._pulse

    def set_sample_rate(self, sample_rate):
        if type(sample_rate) not in (int, float):
            raise ValueError("Sample rate needs to be integer or float!")
        self._sample_rate = sample_rate

    def sample_rate(self):
        return self._sample_rate

    def set_callback(self, call_back_id):
        if type(call_back_id) != int:
            raise ValueError("Call_back_id needs to be integer!")
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

    def get(self, iteration):
        iteration_values = []
        if type(iteration) != int:
            raise ValueError("Iteration needs to be integer!")
        for counter in range(iteration):
            values = [call.tally() for call in self._call_backs]
            for call in self._call_backs:
                call.reset_tally()
            time.sleep(0.1 * self._sample_rate)
            iteration_values.append(values)
        return iteration_values

    def run(self, iteration=1, functor=default_functor, **kwargs):
        if type(iteration) != int:
            raise ValueError("Iteration needs to be integer!")
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
