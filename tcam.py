#! /usr/bin/python3
import board
import json
import busio
import numpy as np
import adafruit_mlx90640

import slave
import master


i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)  # setup I2C
mlx = adafruit_mlx90640.MLX90640(i2c)  # begin MLX90640 with I2C comm
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ  # set refresh rate
mlx_shape = (24, 32)  # mlx90640 shape
frame = np.zeros(mlx_shape[0]*mlx_shape[1])


def update():
    while True:
        try:
            mlx.getFrame(frame)
            return frame
        except:
            pass


def main():
    with open('config.json') as f:
        config = json.load(f)

    mode = config['mode']
    if mode == 'slave':
        slave.run(config)
    elif mode == 'master':
        master.run(config)


if __name__ == "__main__":
    main()
