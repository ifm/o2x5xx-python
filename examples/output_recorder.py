from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from o2x5xx import O2x5xxDevice
except ModuleNotFoundError:
    from o2x5xx.device.client import O2x5xxDevice
from datetime import datetime
import time
import sys
import os

COUNTER = 0


def end_of_runtime(start, duration):
    if duration == -1:
        return False
    current_time = time.time()
    end_of_time = start + duration
    if end_of_time < current_time:
        return True


if __name__ == '__main__':
    try:
        address = sys.argv[1]
        file_name = sys.argv[2]
        duration_in_seconds = int(sys.argv[3])
    except IndexError:
        raise ValueError("Argument(s) are missing. Here is an example for recoding for one hour: "
                         "python output_recorder.py 192.168.0.69 myFile.txt 3600")

    # create device
    device = O2x5xxDevice(address, 50010)

    # create a text file where to store the data from process interface
    if not os.path.exists(os.path.dirname(file_name)):
        try:
            os.makedirs(os.path.dirname(file_name))
        except OSError:
            print("Creation of the directory %s failed" % file_name)
        else:
            print("Successfully created the directory %s " % file_name)

        text_file = open(file_name, "w+")
        text_file.close()

    start_time = time.time()

    print("\n--- Starting recording PCIC output ---\n")

    while True:
        if not end_of_runtime(start_time, duration_in_seconds):

            # Trigger sensor synchronous
            ticket, answer = device.read_next_answer()

            if ticket == b"0000":
                # Add a line index and a timestamp at the start of the line
                answer = str(COUNTER) + ";" + answer.decode() + ";" + str(datetime.now())
                print(answer)

                # Write answer to file
                with open(file_name, 'a') as out_file:
                    out_file.write(answer + "\n")

                # Increment line counter
                COUNTER += 1
        else:
            out_file.close()
            print("\n--- End recording ---")
            print("\n---Runtime: %s seconds ---" % (time.time() - start_time))
            sys.exit(-1)
