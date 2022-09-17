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
                r = requests.get(address, verify=False, timeout=5)
                percentages.append(float(r.text))
            except Exception as e:
                failedAddresses.append(address + ": " + str(e))
                percentages.append(0)

        if failedAddresses:
            numFailures += 1

            if numFailures >= config['errorCount']:
                GPIO.output(errorGpio, False)
                if numFailures % config['errorCount'] == 0:
                    updateFailureLog(failedAddresses)
            print("error active " + str(failedAddresses)) 
        else:
            numFailures = 0
            GPIO.output(errorGpio, True)
            print("error inactive")

        for i, rule in enumerate(rules):
            if eval(rule['check'].format(*percentages)):
                counts[i]+=1
            else:
                counts[i]=0

            GPIO.output(rule['gpio'], counts[i]<rule['count'])
            print(str(i) + " inactive" if str(counts[i]<rule['count']) else " active")

        time.sleep(timeStep)
