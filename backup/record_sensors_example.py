from o2x5xx.pcic.client import O2x5xxDevice
import time
import sys
import os
from datetime import datetime

COUNTER = 0


def end_of_runtime(start, duration):
    current_time = time.time()
    end_of_time = start + duration
    if end_of_time < current_time:
        return True


if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        sys.exit(-1)

    o2i5xx_address = "192.168.0.100"
    o2d5xx_address = "192.168.0.69"

    # create device
    o2i5xx = O2x5xxDevice(o2i5xx_address, 50010)
    o2d5xx = O2x5xxDevice(o2d5xx_address, 50010)

    # create a text file where to store the data from process interface
    if not os.path.exists(file_name):
        text_file = open(file_name, "w+")
        text_file.close()

    print("Writing following rows to file:\n")

    while True:

        # Wait for answer from O2d5xx sensor
        answer_o2d5xx = o2d5xx.read_next_answer()[1].decode()
        time.sleep(1)
        answer_o2i5xx = o2i5xx.execute_synchronous_trigger()

        # Add a line index and a timestamp at the start of the line
        answer = str(COUNTER) + ";" + str(datetime.now()) + ";O2I5XX;" + answer_o2i5xx + ";O2D5xx;" + answer_o2d5xx
        print(answer)

        # Write answer to file
        with open(file_name, 'a') as out_file:
            out_file.write(answer + "\n")

        # Increment line counter
        COUNTER += 1
