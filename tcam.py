#! /usr/bin/python3
import board
import json
import busio
import sys
import os
from threading import Timer

import numpy as np
import adafruit_mlx90640
from w1thermsensor import W1ThermSensor
import schedule

import slave
import master
import debug


def reboot():
    os.system('reboot now')

np.set_printoptions(suppress=True, linewidth=200)

try:
    i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)  # setup I2C
    mlx = adafruit_mlx90640.MLX90640(i2c)  # begin MLX90640 with I2C comm
    mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ  # set refresh rate
except:
    pass
mlx_shape = (24, 32)  # mlx90640 shape
frame = np.zeros(mlx_shape[0]*mlx_shape[1])
sensor = W1ThermSensor()

with open(os.path.join(sys.path[0], 'config.json')) as f:
    config = json.load(f)
    thresholdOffset = config['tempThresholdOffset']
    rebootTime = config['rebootTime']
    if rebootTime != "":
        schedule.every().day.at(rebootTime).do(reboot)

try:
    with open(os.path.join(sys.path[0], 'map.csv'), 'r', encoding='utf-8-sig') as f:
        map = np.genfromtxt(f, dtype=float, delimiter=';')
except:
    map = np.ones(mlx_shape)



rebootTimer = None
def check_schedule():
    schedule.run_pending()
    rebootTimer = Timer(1, check_schedule)
    rebootTimer.start()

def get_frame():
    while True:
        try:
            mlx.getFrame(frame)
            return np.reshape(frame, mlx_shape)
        except Exception as e:
            print(e)


def get_frame_threshold():
    threshold = sensor.get_temperature() + thresholdOffset
    return np.where(get_frame() > threshold, 1, 0)


def get_frame_mapped():
    return np.multiply(map, get_frame_threshold())


def get_weighted_percentage():
    return 100*np.sum(get_frame_mapped())/np.sum(map)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        debug.run()
        return
    
    if rebootTime != "":
        check_schedule()

    mode = config['mode']
    if mode == 'slave':
        slave.run(config)
    elif mode == 'master':
        master.run(config)


if __name__ == "__main__":
    main()
