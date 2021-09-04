import time

import requests
import RPi.GPIO as GPIO


def run(config):
    for rule in config['rules']:
        GPIO.setup(rule['gpio'], GPIO.OUT, initial=GPIO.LOW)

    while True:
        percentages = []
        for address in config['slaves']:
            r = requests.get(address + '/data')
            percentages.append(float(r.text))

        for rule in config['rules']:
            enabled = False

            if rule['check'] == 'any':
                for slave in rule['slaves']:
                    if percentages[slave] > rule['percentage']:
                        enabled = True
            elif rule['check'] == 'all':
                enabled = True
                for slave in rule['slaves']:
                    if percentages[slave] < rule['percentage']:
                        enabled = False

            GPIO.output(rule['gpio'], enabled)

        time.sleep(1)
