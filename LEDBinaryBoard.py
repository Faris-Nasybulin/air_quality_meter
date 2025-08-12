import math
import time

from gpiozero import LEDCollection

class LEDBinaryBoard(LEDCollection):
    UNSIGNED_MODE = 'UNSIGNED_MODE'
    SIGNED_WITH_MAGNITUDE_MODE = 'SIGNED_WITH_MAGNITUDE_MODE'
    SIGNED_ONES_COMPLEMENT_MODE = 'SIGNED_ONES_COMPLEMENT_MODE'
    SIGNED_TWOS_COMPLEMENT_MODE = 'SIGNED_TWOS_COMPLEMENT_MODE'
    MODES = (
        UNSIGNED_MODE,
        SIGNED_WITH_MAGNITUDE_MODE,
        SIGNED_ONES_COMPLEMENT_MODE,
        SIGNED_TWOS_COMPLEMENT_MODE
    )
    COMPLEMENT_MODES = (
        SIGNED_ONES_COMPLEMENT_MODE,
        SIGNED_TWOS_COMPLEMENT_MODE
    )
    SIGNED_ZERO_MODES = (
        SIGNED_WITH_MAGNITUDE_MODE,
        SIGNED_ONES_COMPLEMENT_MODE
    )
    SIGNED_MODES = (
        SIGNED_WITH_MAGNITUDE_MODE,
        SIGNED_ONES_COMPLEMENT_MODE,
        SIGNED_TWOS_COMPLEMENT_MODE
    )

    def __init__(self, *args, initial_value=0, mode=UNSIGNED_MODE, **kwargs):
        self.mode = mode
        super().__init__(*args, **kwargs)
        try:
            self.value = initial_value
        except:
            self.close()
            raise

    @property
    def value(self):
        negative_q = self.sign_bit_count and super().value[0]
        sign = -1 if negative_q else 1
        bits = super().value[-self.value_bits_count:]
        magnitude = sum(
            bit * pow(2, index)
            for index, bit in enumerate(reversed(bits))
        )
        if negative_q and self.mode in self.COMPLEMENT_MODES:
            magnitude = self._complement - magnitude
        if sign == -1 and magnitude == 0:
            # return -0.0 if platform support
            sign = -1.0
        return sign * magnitude

    @value.setter
    def value(self, new_value):
        if not self.numeric_q(new_value):
            raise TypeError('Value must be a numeric.')

        if new_value < self.lower_bound:
            raise ValueError('Value could not be displayed at led binary board since lower than lower bound.')

        if new_value >= self.upper_bound:
            raise ValueError('Value could not be displayed at led binary board since greater or equal than upper bound')

        bits = self._to_bits(new_value)
        super(__class__, self.__class__).value.__set__(self, bits)

        self._not_normalized_value = new_value

    def numeric_q(self, value):
        return isinstance(value, (int, float))

    @property
    def upper_bound(self):
        return pow(2, self.value_bits_count)

    @property
    def lower_bound(self):
        return self.upper_bound - self.range

    @property
    def range(self):
        return pow(2, len(self)) - self.signed_zero_mode_q

    @property
    def sign_bit_count(self):
        return self.mode in self.SIGNED_MODES

    @property
    def value_bits_count(self):
        return len(self) - self.sign_bit_count

    @property
    def signed_zero_mode_q(self):
        return self.mode in self.SIGNED_ZERO_MODES

    def _to_bits(self, value):
        negative_allowed_q = value != 0 or self.signed_zero_mode_q
        # Specical comparing for signed zero
        negative_q = math.copysign(1, value) < 0 and negative_allowed_q

        normalized_value = int(value // 1)
        if negative_q and self.mode in self.COMPLEMENT_MODES:
            normalized_value += self._complement
        magnitude_str_bits = "{:+0{n}b}".format(normalized_value, n=self.value_bits_count+1)[-self.value_bits_count:]

        sign_str_bit = ''
        if self.sign_bit_count:
            sign_str_bit = '1' if negative_q else '0'

        return map(int, sign_str_bit + magnitude_str_bits)

    @property
    def not_normalized_value(self):
        return self._not_normalized_value

    def _check_mode(self, mode):
        if mode not in self.MODES:
            raise ValueError('Incorrect mode.')

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._check_mode(mode)
        previous_mode = getattr(self, 'mode', None)
        self._mode = mode
        try:
            self._refresh()
        except:
            if previous_mode is not None:
                self._mode = previous_mode
            raise

    def _refresh(self):
        if hasattr(self, 'not_normalized_value'):
            self.value = self.not_normalized_value

    @property
    def _first_complement(self):
        return self.upper_bound - 1

    @property
    def _second_complement(self):
        return self.mode == self.SIGNED_TWOS_COMPLEMENT_MODE

    @property
    def _complement(self):
        return self._first_complement + self._second_complement


if __name__ == '__main__':
    pins = [
        "GPIO5",
#         "GPIO6",
#         "GPIO13",
#         "GPIO19",
        "GPIO16",
        "GPIO20",
        "GPIO21"
    ]
    for mode in LEDBinaryBoard.MODES:
        ledBinaryBoard = LEDBinaryBoard(*pins, initial_value=1, mode=mode)

        print('mode', mode)
#         ledBinaryBoard.value = math.copysign(10, -1)
#         print(list(LEDCollection.value.__get__(ledBinaryBoard)), ledBinaryBoard.value)
#         try:
#             ledBinaryBoard.mode = LEDBinaryBoard.UNSIGNED_MODE
#             print('without ledBinaryBoard.mode', ledBinaryBoard.mode, ledBinaryBoard.value)
#         except:
#             pass
#         print('ledBinaryBoard.mode', ledBinaryBoard.mode, ledBinaryBoard.value)
#         print(list(LEDCollection.value.__get__(ledBinaryBoard)), ledBinaryBoard.value)

        time.sleep(3)
        ledBinaryBoard.value = False
        time.sleep(3)

        for value in [*range(ledBinaryBoard.lower_bound, ledBinaryBoard.upper_bound), math.copysign(0,-1)]:
            ledBinaryBoard.value = value
            print('value', value, 'ledBinaryBoard.value', ledBinaryBoard.value, ledBinaryBoard.value == value, list(LEDCollection.value.__get__(ledBinaryBoard)))
            time.sleep(0.2)

        ledBinaryBoard.close()