from __future__ import (absolute_import, division, print_function, unicode_literals)
from o2x5xx.pcic.image_client import ImageClient
from PIL import Image
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


def check_or_make_dir(path):
    if not os.path.exists(path):
        # Create a new directory because it does not exist
        os.makedirs(path)


if __name__ == '__main__':
    try:
        address = sys.argv[1]
        folder_path = sys.argv[2]
        duration_in_seconds = int(sys.argv[3])
    except IndexError:
        raise ValueError("Argument(s) are missing.\n"
                         "Here is an example for recoding images for one hour: "
                         "python image_recorder.py 192.168.0.69 ./my_folder 3600 \n"
                         "Here is an example for recoding images endless: "
                         "python image_recorder.py 192.168.0.69 ./my_folder -1 \n")

    image_client = ImageClient(address, 50010)

    # Check or make a directory where to store the images
    check_or_make_dir(path=folder_path)

    # Set start time for timer
    start_time = time.time()

    print("\n--- Starting recording {nr} image(s) from sensor ---\n".format(nr=str(image_client.number_images)))

    while True:
        if not end_of_runtime(start_time, duration_in_seconds):

            # Read next frames from sensor
            image_client.read_next_frames()

            timestamp = time.strftime("%Y%m%d-%H%M%S")

            for index, image in enumerate(image_client.frames, start=1):
                image_filename = '{dt}_image_ID_{nr}_number_{cnt}.jpg'.format(dt=timestamp,
                                                                              nr=str(index),
                                                                              cnt=str(COUNTER).zfill(6))
                im = Image.fromarray(image)
                full_save_path = os.path.join(folder_path, image_filename)
                im.save(full_save_path)

            print('Saved image here: {path}'.format(path=str(full_save_path)))

            COUNTER += 1

        else:
            print("\n--- End recording ---")
            print("\n---Runtime: %s seconds ---" % (time.time() - start_time))
            sys.exit(-1)
