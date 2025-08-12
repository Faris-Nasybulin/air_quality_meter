import time

if __name__ == '__main__':
    from button import btn
    from precise_board import preciseBoard
    from s8_sensor import s8_sensor

    while True:
        value = s8_sensor.value
        print(value, 'ppm', time.time())
        preciseBoard.value = value
        time.sleep(4)