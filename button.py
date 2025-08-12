#!/usr/bin/python3
import math
from signal import pause
from subprocess import check_call
import time

from gpiozero import Button, InputDevice

class HoldButton(Button):
    _press_time_s = 0

SHUTDOWN_BTN_PIN = 'GPIO26'
HOLD_TIME_S = 0.25
BOUNCE_TIME_MS = 25
PULL_UP = None
ACTIVE_STATE = False
SHOT_DOWN_HOLD_TIME_S = 10
CONFIRM_TIME_S = 3

MS_IN_S = 1000
BOUNCE_TIME_S = BOUNCE_TIME_MS / MS_IN_S

btn = HoldButton(
    SHUTDOWN_BTN_PIN,
    pull_up=PULL_UP,
    active_state=ACTIVE_STATE,
    bounce_time=BOUNCE_TIME_S,
    hold_time=HOLD_TIME_S,
    hold_repeat=True
)

shutdown_already_q = False
def shutdown(self):
    global shutdown_already_q
    if self.active_time > SHOT_DOWN_HOLD_TIME_S and not shutdown_already_q:
        print('shutdown')
        shutdown_already_q = True
        check_call(['sudo', 'poweroff'])

def when_pressed(self):
    print('pressed')
    self._press_time_s = 0

def when_released(self):
    print('released', self._press_time_s)
    if self._press_time_s > CONFIRM_TIME_S:
        print('confirmed')

def when_held(self):
    self._press_time_s = self.active_time
    print('held', self._press_time_s)
    shutdown(self)

btn.when_pressed = when_pressed
btn.when_released = when_released
btn.when_held = when_held


if __name__ == "__main__":
    pause()
