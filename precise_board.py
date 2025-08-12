from LEDBinaryBoard import LEDBinaryBoard
from LeveledPWMLED import LeveledPWMLED
from MultiScaleBoard import MultiScaleBoard

valuePins = [
    "GPIO6",
    "GPIO13",
    "GPIO19",
    "GPIO16",
    "GPIO20",
    "GPIO21"
]
levelPin = "GPIO5"
offsets, scales = zip(
    (200, 10),
    (800, 20),
    (2000, 50),
    (5000, 100)
)

valueBoard = LEDBinaryBoard(*valuePins)
levelBoard = LeveledPWMLED(levelPin, levels_count=len(scales))
preciseBoard = MultiScaleBoard(
    valueBoard=valueBoard,
    levelBoard=levelBoard,
    offsets=offsets,
    scales=scales
)