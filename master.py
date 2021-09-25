import time

import requests
import RPi.GPIO as GPIO


failureLogFilename = '/home/pi/Documents/errorlog.txt'


def updateFailureLog(newItems):
    t = time.asctime()

    failureLogFile = open(failureLogFilename, "a")
    for item in newItems:
        failureLogFile.write(t + ": " + item + '\n')
    failureLogFile.close()


def run(config):
    slaves = config['slaves']
    errorGpio = config['errorGpio']
    timeStep = config['timeStep']
    rules = config['rules']

    for rule in rules:
        GPIO.setup(rule['gpio'], GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(errorGpio, GPIO.OUT, initial=GPIO.LOW)

    numFailures = 0

    while True:
        percentages = []
        failedAddresses = []

        for address in slaves:
            try:
                r = requests.get(address + '/data')
                percentages.append(float(r.text))
            except:
                failedAddresses.append(address)

        if failedAddresses:
            numFailures += 1

            for rule in rules:
                GPIO.output(rule['gpio'], False)

            if numFailures >= config['errorCount']:
                GPIO.output(errorGpio, True)
                if numFailures % config['errorCount'] == 0:
                    updateFailureLog(failedAddresses)

            time.sleep(timeStep)
            continue
        else:
            numFailures = 0
            GPIO.output(errorGpio, False)

        for rule in rules:
            enabled = False

            if rule['check'] == 'any':
                for slave in range(len(slaves)):
                    if percentages[slave] > rule['percentage']:
                        enabled = True
            elif rule['check'] == 'all':
                enabled = True
                for slave in range(len(slaves)):
                    if percentages[slave] < rule['percentage']:
                        enabled = False

            GPIO.output(rule['gpio'], enabled)

        time.sleep(timeStep)
