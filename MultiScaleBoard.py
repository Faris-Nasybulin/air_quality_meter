from gpiozero import OutputDevice, CompositeOutputDevice

class MultiScaleBoard:
    _level = None

    def __init__(self, *, levelBoard, valueBoard, offsets, scales):
        if not isinstance(levelBoard, (OutputDevice, CompositeOutputDevice)):
            raise TypeError('levelBoard must be OutputDevice or CompositeOutputDevice')
        self.levelBoard = levelBoard

        if not isinstance(valueBoard, (OutputDevice, CompositeOutputDevice)):
            raise TypeError('valueBoard must be OutputDevice or CompositeOutputDevice')
        self.valueBoard = valueBoard

        self.offsets = tuple(offsets)
        self.scales = tuple(scales)
        levels_count = len(self.offsets)
        if len(self.scales) != levels_count:
            raise ValueError('`offsets` and `scales` must be the same length.')
        if levels_count  == 0:
            raise ValueError('`offsets` and `scales` must be not empty.')

        self.bounds = sorted([
            sorted([
                self.offsets[level] + self.scales[level] * valueBoard.lower_bound,
                self.offsets[level] + self.scales[level] * valueBoard.upper_bound
            ])
            for level in range(levels_count)
        ])

        lower, upper = self._get_bounds()
        self.lower_bound = lower
        self.upper_bound = upper

    def _get_bounds(self):
        min_lower_bound, max_upper_bound = self.bounds[0]
        for lower, upper in self.bounds[1:]:
            if lower <= max_upper_bound:
                max_upper_bound = max(upper, max_upper_bound)
            else:
                raise ValueError('The union of interval of all levels must be one interval.')

        return (min_lower_bound, max_upper_bound)

    @property
    def value(self):
        return self.offset + self.scale * self.valueBoard.value

    @value.setter
    def value(self, value):
        """i_level: value = offset + scale * displayed

        0 level: value =   -1 +   5 * displayed |    -1 |   319 |
        1 level: value =  300 +   2 * displayed |   300 |   428 |
        2 level: value =  400 +  10 * displayed |   400 |  1040 |
        3 level: value = 1000 +  20 * displayed |  1000 |  2280 |
        4 level: value = 2000 +  50 * displayed |  2000 |  5200 |
        5 level: value = 5000 + 100 * displayed |  5000 | 11400 |

        displayed for 6 LEDs can be between 0 and 63 (pow(2, 6) - 1)
        therefore:
        offset <= value <= offset + scale * 63"""
        self._level = self._determine_level(value)
        self.valueBoard.value = (value - self.offset) // self.scale
        self.levelBoard.value = self.level


    @property
    def offset(self):
        return self.offsets[self.level]

    @property
    def scale(self):
        return self.scales[self.level]

    @property
    def level(self):
        return self._level

    def _determine_level(self, value):
        if self.level is not None:
            lower, upper = self.bounds[self.level]
            if lower <= value < upper:
                # Return the same level due to hysteresis
                return self.level

        level_with_min_scale = None
        for level, (lower_bound, upper_bound) in enumerate(self.bounds):
            if lower_bound <= value < upper_bound:
                if level_with_min_scale is None or self.scales[level] < self.scales[level_with_min_scale]:
                    level_with_min_scale = level

        if level_with_min_scale is None:
            if value < self.lower_bound:
                raise ValueError('Provided value is lower than lower_bound that can be displayed.')
            elif value >= self.upper_bound:
                raise ValueError('Provided value is greater than upper_bound that can be displayed.')
            else:
                raise Exception('Unexpected behavior.')

        return level_with_min_scale

if __name__ == "__main__":
    import time
    from LEDBinaryBoard import LEDBinaryBoard
    from MultiValuePWMLED import MultiValuePWMLED
    from ScaledPWMLED import ScaledPWMLED

    offsets, scales = zip(
        (200, 10),
        (800, 20),
        (2000, 50),
        (5000, 100)
    )

    valuePins = [
        "GPIO6",
        "GPIO13",
        "GPIO19",
        "GPIO16",
        "GPIO20",
        "GPIO21"
    ]
    valueBoard = LEDBinaryBoard(*valuePins)
#    levelBoard = LEDBinaryBoard(*levelPins)
#    levelBoard = MultiValuePWMLED('GPIO5', levels_count = 5, cycle_duration_s = 4)
    levelBoard = ScaledPWMLED('GPIO5', levels_count=len(offsets))
    print(levelBoard.levels)

    multiScaleBoard = MultiScaleBoard(
        valueBoard=valueBoard,
        levelBoard=levelBoard,
        offsets=offsets,
        scales=scales
    )

    multiScaleBoard.value = 320
    print('multiScaleBoard.level', multiScaleBoard.level)
    while True:
        for bound in multiScaleBoard.bounds:
            lower, upper = bound
            print(bound)
            multiScaleBoard.value = (lower + upper) / 2
            time.sleep(1)
