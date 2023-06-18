import csv
import datetime

def writeLog(currentInternalTemperature, currentExternalTemperature, referenceTemperature, fanSignal, resistorSignal):
    with open('log.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)

        data = [datetime.datetime.now(), currentInternalTemperature, currentExternalTemperature, referenceTemperature, fanSignal, resistorSignal]
        writer.writerow(data)