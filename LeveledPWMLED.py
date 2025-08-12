from itertools import repeat, cycle, chain
import time

from gpiozero import PWMLED

class LeveledPWMLED(PWMLED):
    def __init__(self, *args, levels_count, levels=None, **kwargs):
        if levels is None:
            min_brightness = 1 / 100
            max_brightness = 1
            levels_count -= 1
            levels = [min_brightness * pow(max_brightness / min_brightness, i / (levels_count - 1)) for i in range(levels_count)]
            levels = [0, *levels]
        self._levels = levels

        super().__init__(*args, **kwargs)

    @property
    def levels(self):
        return self._levels

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, value):
        brightness = self.levels[value]
        super(__class__, self.__class__).value.__set__(self, brightness)

if __name__ == '__main__':
    n = 4
    led = ScaledPWMLED("GPIO5", levels_count = n)
    for level in range(n):
        led.value = level
        time.sleep(1)