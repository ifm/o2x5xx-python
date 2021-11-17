from o2x5xx.pcic.client import O2x5xxDevice
import time
import sys
from datetime import datetime

RECORD_DURATION_IN_SECONDS = 20
COUNTER = 0


def end_of_runtime(start, duration):
    current_time = time.time()
    end_of_time = start + duration
    if end_of_time < current_time:
        return True


if __name__ == '__main__':
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = '192.168.0.69'

    # create device
    device = O2x5xxDevice(address, 50010)

    # create and/or open a text file where to store the data from process interface
    text_file = open("myData.txt", "w+")

    start_time = time.time()

    print("Writing following rows to file:\n")

    while True:
        if not end_of_runtime(start_time, RECORD_DURATION_IN_SECONDS):

            # Trigger sensor synchronous
            answer = device.execute_synchronous_trigger()

            # Add a line index and a timestamp at the start of the line
            answer = str(COUNTER) + ";" + str(datetime.now()) + ";" + answer

            # Write answer to file
            text_file.write(answer + "\n")

            # Increment line counter
            COUNTER += 1
        else:
            text_file.close()
            print("---Runtime: %s seconds ---" % (time.time() - start_time))
            sys.exit(-1)
