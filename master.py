import json
import base64

import requests
import RPi.GPIO
import numpy

import tcam


def run(config):
    tempThreshold = config['tempThreshold']
    percentageThreshold = config['percentageThreshold']

    while True:
        frames = []
        try:
            frames.append(tcam.update())
        except:
            continue

        for address in config['slaves']:
            r = requests.get(address + '/data')
            encodedFrame = json.loads(r.text)
            dataType = numpy.dtype(encodedFrame[0])
            dataArray = numpy.frombuffer(
                base64.b64decode(encodedFrame[1]), dataType)
            dataArray.reshape(encodedFrame[2])

            frames.append(dataArray)

        frame = frames[0]

        print(frame)
        print(numpy.where(frame > tempThreshold, 1, 0))
        print(tempThreshold)
        print(numpy.average(numpy.where(frame > tempThreshold, 1, 0))
              * 100)
