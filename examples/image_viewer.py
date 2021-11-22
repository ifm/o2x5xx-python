from __future__ import (absolute_import, division, print_function, unicode_literals)
# from builtins import *
from o2x5xx import O2x5xxDevice
from o2x5xx.static.formats import serialization_format
import io
import sys
import binascii
import struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation

imageWidth = 1280
imageHeight = 960


class GrabO2x5xx(object):
    def __init__(self, sensor):
        self.sensor = sensor
        self.frame_ids = self.read_frame_ids()

        self.image1 = np.zeros((imageHeight, imageWidth), dtype='uint8')
        self.image2 = np.zeros((imageHeight, imageWidth), dtype='uint8')
        self.image3 = np.zeros((imageHeight, imageWidth), dtype='uint8')
        self.image4 = np.zeros((imageHeight, imageWidth), dtype='uint8')
        self.image5 = np.zeros((imageHeight, imageWidth), dtype='uint8')

    @staticmethod
    def deserialize_image_chunk(data):
        results = {}
        length = int(data.__len__())
        data = binascii.unhexlify(data.hex())
        counter = 0

        while length:
            # get header information
            header = {}
            for key, value in serialization_format.items():
                hex_val = data[key: key + value[2]]
                dec_val = struct.unpack('<i', hex_val)[0]
                header[value[0]] = dec_val

            # append header
            results.setdefault(counter, []).append(header)
            # append image
            image_hex = data[header['HEADER_SIZE']:header['CHUNK_SIZE']]
            results[counter].append(image_hex)

            length -= header['CHUNK_SIZE']
            data = data[header['CHUNK_SIZE']:]
            counter += 1

        return results

    def read_next_frames(self):
        ticket, answer = self.sensor.read_next_answer()
        frames = self.deserialize_image_chunk(answer[19:])
        images = [mpimg.imread(io.BytesIO(frames[f][1]), format='jpg') for f in frames]
        return images

    def upload_image_configuration(self):
        # disable all result output
        self.sensor.turn_process_interface_output_on_or_off(0)

        # format string for all images
        self.sensor.upload_process_interface_output_configuration(pcic_config)

        # enable result output again
        self.sensor.turn_process_interface_output_on_or_off(7)

    def read_frame_ids(self):
        ticket, answer = self.sensor.read_next_answer()
        frame_ids = answer[:19].decode()
        frame_ids = frame_ids.split(';')[1:-1]
        return frame_ids


def updatefig(*args):
    g = args[1]
    frames = g.read_next_frames()

    images = args[2]
    [i.set_array(frames[x] / 255) for x, i in enumerate(images)]

    # image1 = images[0]
    # image1.set_array(g.image1 / 255)
    #
    # image2 = images[1]
    # image2.set_array(g.image2 / 255)
    #
    # image3 = images[2]
    # image3.set_array(g.image3 / 255)
    #
    # image4 = images[3]
    # image4.set_array(g.image4 / 255)
    #
    # image5 = images[4]
    # image5.set_array(g.image5 / 255)
    #
    # return image1, image2, image3, image4, image5,
    return images[0], images[1], images[2], images[3], images[4],


def main():
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = '192.168.0.69'

    # create device
    device = O2x5xxDevice(address, 50010)

    # create figure
    fig = plt.figure()
    fig.suptitle('O2x5xx Image Viewer ({ip})'.format(ip=device.address))

    # create grabber
    grabber = GrabO2x5xx(device)

    # Upload the process interface configuration for retrieving image ids and image data
    grabber.upload_image_configuration()

    # Subplots are organized in a rows x cols grid
    cols = 1
    if len(grabber.frame_ids) > cols:
        cols = 2
    if len(grabber.frame_ids) > cols:
        cols = 3

    # Compute rows required
    rows = len(grabber.frame_ids) // cols
    rows += len(grabber.frame_ids) % cols

    axs = [fig.add_subplot(rows, cols, i+1) for i in range(len(grabber.frame_ids)+1)]

    # ax1 = fig.add_subplot(2, 3, 1)
    # ax2 = fig.add_subplot(2, 3, 2)
    # ax3 = fig.add_subplot(2, 3, 3)
    # ax4 = fig.add_subplot(2, 3, 4)
    # ax5 = fig.add_subplot(2, 3, 5)

    images = [a.imshow(np.zeros((imageHeight, imageWidth)), animated=True, cmap='gray', aspect='equal')
              for a in axs]

    # image1 = ax1.imshow(np.zeros((imageHeight, imageWidth), dtype='uint8'), animated=True, cmap='gray', aspect='equal')
    # image2 = ax2.imshow(np.zeros((imageHeight, imageWidth), dtype='uint8'), animated=True, cmap='gray', aspect='equal')
    # image3 = ax3.imshow(np.zeros((imageHeight, imageWidth), dtype='uint8'), animated=True, cmap='gray', aspect='equal')
    # image4 = ax4.imshow(np.zeros((imageHeight, imageWidth), dtype='uint8'), animated=True, cmap='gray', aspect='equal')
    # image5 = ax5.imshow(np.zeros((imageHeight, imageWidth), dtype='uint8'), animated=True, cmap='gray', aspect='equal')

    ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True, fargs=[grabber, images])

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
