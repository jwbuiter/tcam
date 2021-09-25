#! /usr/bin/python3
import board
import json
import busio
import sys
import os

import numpy as np
import adafruit_mlx90640

import slave
import master
import debug

np.set_printoptions(suppress=True, linewidth=200)

try:
    i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)  # setup I2C
    mlx = adafruit_mlx90640.MLX90640(i2c)  # begin MLX90640 with I2C comm
    mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ  # set refresh rate
except:
    pass
mlx_shape = (24, 32)  # mlx90640 shape
frame = np.zeros(mlx_shape[0]*mlx_shape[1])

with open(os.path.join(sys.path[0], 'config.json')) as f:
    config = json.load(f)

with open(os.path.join(sys.path[0], 'map.csv'), 'r', encoding='utf-8-sig') as f:
    map = np.genfromtxt(f, dtype=float, delimiter=';')


def get_frame():
    while True:
        try:
            mlx.getFrame(frame)
            return np.reshape(frame, mlx_shape)
        except Exception as e:
            print(e)


def get_frame_threshold():
    return np.where(get_frame() > 30, 1, 0)


def get_weighted_percentage():
    return 100*np.sum(get_frame_threshold())/np.sum(map)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        debug.run()
        return

    mode = config['mode']
    if mode == 'slave':
        slave.run(config)
    elif mode == 'master':
        master.run(config)


if __name__ == "__main__":
    main()
