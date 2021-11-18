from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
from o2x5xx import O2x5xxDevice
from PIL import Image
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

# This is the serialization format of binary data with header version 3.
serialization_format = {
    0x0000: ["CHUNK_TYPE", "Defines the type of the chunk.", 4],
    0x0004: ["CHUNK_SIZE", "Size of the whole image chunk in bytes.", 4],
    0x0008: ["HEADER_SIZE", "Number of bytes starting from 0x0000 until BINARY_DATA."
                            "The number of bytes must be a multiple of 16, and the minimum value is 0x40 (64).", 4],
    0x000C: ["HEADER_VERSION", "Version number of the header (=3).", 4],
    0x0010: ["IMAGE_WIDTH", "Image width in pixel. Applies only if BINARY_DATA contains an image. "
                            "Otherwise this is set to the length of BINARY_DATA.", 4],
    0x0014: ["IMAGE_HEIGHT", "Image height in pixel. Applies only if BINARY_DATA contains an image. "
                             "Otherwise this is set to 1.", 4],
    0x0018: ["PIXEL_FORMAT", "Pixel format. Applies only to image binary data. For generic binary data "
                             "this is set to FORMAT_8U unless specified otherwise for a particular chunk type.", 4],
    0x001C: ["TIME_STAMP", "Timestamp in uS", 4],
    0x0020: ["FRAME_COUNT", "Continuous frame count.", 4],
    0x0024: ["STATUS_CODE", "This field is used to communicate errors on the device.", 4],
    0x0028: ["TIME_STAMP_SEC", "Timestamp seconds", 4],
    0x002C: ["TIME_STAMP_NSEC", "Timestamp nanoseconds", 4],
    0x0030: ["META_DATA", "UTF-8 encoded null-terminated JSON object. The content of the JSON object is depending "
                          "on the CHUNK_TYPE.", 4]}

pcic_config = {
    "elements": [
        {
            "id": "start_string",
            "type": "string",
            "value": "star"
        },
        {
            "id": "delimiter",
            "type": "string",
            "value": ";"
        },
        {
            "elements": [
                {
                    "id": "ID",
                    "type": "uint8"
                },
                {
                    "id": "delimiter",
                    "type": "string",
                    "value": ";"
                }
            ],
            "id": "Images",
            "type": "records"
        },
        {
            "id": "end_string",
            "type": "string",
            "value": "stop"
        },
        {
            "elements": [
                {
                    "id": "jpeg_image",
                    "type": "blob"
                }
            ],
            "id": "Images",
            "type": "records"
        }
    ],
    "format": {
        "dataencoding": "ascii"
    },
    "layouter": "flexible"
}


class GrabO2x5xx(object):
    def __init__(self, sensor):
        self.sensor = sensor
        self.frames = None

        self.number_frames = None
        self.frame_ids = None

    def deserialize_image_chunck(self, data):
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
        # TODO Check with RPC which trigger state is configured
        ticket, answer = self.sensor.read_next_answer()
        # answer = self.sensor.execute_synchronous_trigger()

        self.frames = answer[19:]
        self.frames = self.deserialize_image_chunck(self.frames)
        # self.frames = self.sensor.request_last_image_taken_deserialized(1)
        self.number_frames = len(self.frames)

    def upload_image_configuration(self):
        # disable all result output
        self.sensor.turn_process_interface_output_on_or_off(0)

        # format string for all images
        self.sensor.upload_process_interface_output_configuration(pcic_config)

        # enable result output again
        self.sensor.turn_process_interface_output_on_or_off(7)

    def read_image_ids(self):
        # TODO Check with RPC which trigger state is configured
        ticket, answer = self.sensor.read_next_answer()
        # answer = self.sensor.execute_synchronous_trigger()

        frame_ids = answer[:19].decode()
        self.frame_ids = frame_ids.split(';')[1:-1]

# def update_fig(*args):
#     g = args[1]
#     g.read_next_frames()
#     subplots = args[2]
#
#     for i, a in enumerate(subplots):
#         plot = subplots[i]
#         plot.clear()
#         image_bytes = g.frames[i][1]
#         image_bytes = io.BytesIO(image_bytes)
#         # create image object
#         image = Image.open(image_bytes)
#         ax.imshow(image, cmap='gray', aspect='equal')
#         # if grabber.frame_ids:
#         #     ax.set_title('I{id}'.format(id=grabber.frame_ids[k]))
#         subplots[i] = ax
#
#     return subplots


if __name__ == '__main__':
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = '192.168.0.69'

    # create device
    device = O2x5xxDevice(address, 50010)

    # create figure and grabber instance and read initial frames and image ids
    # fig = plt.figure()
    # fig.suptitle('O2x5xx Image Viewer ({ip})'.format(ip=device.address))
    grabber = GrabO2x5xx(device)

    # config = device.retrieve_current_process_interface_configuration()

    # Upload the process interface configuration for retrieving image ids and image data
    grabber.upload_image_configuration()

    # Read the image ids
    grabber.read_image_ids()

    # Read next frames
    grabber.read_next_frames()

    # Subplots are organized in a rows x cols grid
    cols = 1
    if grabber.number_frames > cols:
        cols = 2
    if grabber.number_frames > cols:
        cols = 3

    # Compute rows required
    rows = grabber.number_frames // cols
    rows += grabber.number_frames % cols

    # for k in range(grabber.number_frames):
    #     ax = fig.add_subplot(rows, cols, k)

    fig, axs = plt.subplots(rows, cols)
    fig.suptitle('O2x5xx Image Viewer ({ip})'.format(ip=device.address))
    # if grabber.frame_ids:
    #     for k, ax in enumerate(np.array(axs)):
    #         ax.set_title('I{id}'.format(id=grabber.frame_ids[k-1]))
    image_list = []
    for k, ax in enumerate(np.array(axs)):
        img = plt.imshow(np.random.rand(imageHeight, imageWidth), cmap='gray', aspect='equal')
        image_list.append(img)

        # TODO Only for testing
        grabber.frame_ids = [1, 2, 3, 4, 5]
        if grabber.frame_ids:
            ax.set_title('I{id}'.format(id=grabber.frame_ids[k]))


    # # add every single subplot to the figure with a for loop
    # ax_list = []
    # for k in range(1, grabber.number_frames + 1):
    #     ax = fig.add_subplot(rows, cols, k)
    #
    #     # create image object
    #     image_bytes = grabber.frames[k-1][1]
    #     image_bytes = io.BytesIO(image_bytes)
    #     image = Image.open(image_bytes)
    #
    #     ax.set_title('22222')
    #     ax.imshow(image, cmap='gray', aspect='equal', alpha=.5)
    #     ax.set_title('22222')
    #
    #     if grabber.frame_ids:
    #         plt.title('I{id}'.format(id=grabber.frame_ids[k-1]))
    #
    #     ax.axes.get_xaxis().set_visible(False)
    #     ax.axes.get_yaxis().set_visible(False)
    #     ax_list.append(ax)
    #
    # # add image id to frame as title
    # if grabber.frame_ids:
    #     for k, x in enumerate(ax_list):
    #         x.set_title('I{id}'.format(id=grabber.frame_ids[k]))
    #         x.title.set_text('I{id}'.format(id=grabber.frame_ids[k]))

    # plt.subplots_adjust(wspace=.05, hspace=.05)

    # def update_fig(*args):
    #     g = args[1]
    #     g.read_next_frames()
    #     subplots = args[2]
    #
    #     for k, a in enumerate(subplots):
    #         subplot = subplots[k]
    #         # _images = subplot.images
    #         # subplot.images = []
    #         subplot.clear()
    #
    #         # create plot title
    #         # TODO Only for testing
    #         grabber.frame_ids = [1, 2, 3, 4, 5]
    #         if grabber.frame_ids:
    #             subplot.set_title('I{id}'.format(id=grabber.frame_ids[k]))
    #
    #         # read image object
    #         image_bytes = g.frames[k][1]
    #         image_bytes = io.BytesIO(image_bytes)
    #         img = mpimg.imread(image_bytes, format='jpg')
    #         ax.imshow(img, cmap='gray', aspect='equal')
    #
    #         # subplots[i] = plot
    #         # subplots[k] = ax
    #
    #     return subplots

    def update_fig(*args):
        grabber.read_next_frames()

        for i, a in enumerate(axs):
            # _images = subplot.images
            # subplot.images = []
            # image.clear()

            # create plot title
            # TODO Only for testing
            # grabber.frame_ids = [1, 2, 3, 4, 5]
            # if grabber.frame_ids:
            #     subplot.set_title('I{id}'.format(id=grabber.frame_ids[ök]))

            # read image object
            image_bytes = grabber.frames[k][1]
            image_bytes = io.BytesIO(image_bytes)
            image_list[i].set_array(mpimg.imread(image_bytes, format='jpg'))
            # axs[i].imshow(img, cmap='gray', aspect='equal')
            print('x')
            # subplots[i] = plot
            # subplots[k] = ax

        return axs


    # ani = animation.FuncAnimation(fig, update_fig, interval=50, blit=True, fargs=[grabber, ax_list])
    ani = animation.FuncAnimation(fig, func=update_fig, interval=50, blit=True)

    plt.tight_layout()
    plt.show()
