import time

import requests
import RPi.GPIO as GPIO


failureLogFilename = ''


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
    global failureLogFilename
    failureLogFilename = config['logFile']

    for rule in rules:
        GPIO.setup(rule['gpio'], GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(errorGpio, GPIO.OUT, initial=GPIO.HIGH)

    numFailures = 0
    counts = [0] * len(rules)

    while True:
        percentages = []
        failedAddresses = []

        for address in slaves:
            try:
                r = requests.get(address)
                percentages.append(float(r.text))
            except Exception as e:
                failedAddresses.append(address + ": " + str(e))

        if failedAddresses:
            numFailures += 1

            for rule in rules:
                GPIO.output(rule['gpio'], True)

            if numFailures >= config['errorCount']:
                GPIO.output(errorGpio, False)
                if numFailures % config['errorCount'] == 0:
                    updateFailureLog(failedAddresses)

            time.sleep(timeStep)
            continue
        else:
            numFailures = 0
            GPIO.output(errorGpio, True)

        for i, rule in enumerate(rules):
            if eval(rule['check'].format(*percentages)):
                counts[i]+=1
            else:
                counts[i]=0

            GPIO.output(rule['gpio'], counts[i]<rule['count'])

        time.sleep(timeStep)
