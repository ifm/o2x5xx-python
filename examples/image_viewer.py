from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
from o2x5xx.pcic.client import O2x5xxDevice
from PIL import Image
import io
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation

imageWidth = 1280
imageHeight = 960


class GrabO2x5xx(object):
    def __init__(self, sensor):
        self.sensor = sensor
        self.frames = None

        self.number_frames = None
        self.frame_ids = None

    def read_next_frames(self):
        self.frames = self.sensor.request_last_image_taken_decoded(1)
        self.number_frames = len(self.frames)

    def read_frame_ids(self):
        # disable all result output
        self.sensor.turn_process_interface_output_on_or_off(0)

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
                            "type": "uint32"
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
                }
            ],
            "format": {
                "dataencoding": "ascii"
            },
            "layouter": "flexible"
        }

        # format string for all images
        self.sensor.upload_process_interface_output_configuration(pcic_config)

        # enable result output again
        self.sensor.turn_process_interface_output_on_or_off(7)

        answer = self.sensor.execute_synchronous_trigger()
        self.frame_ids = answer.split(';')[1:-1]


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
    grabber.read_next_frames()
    grabber.read_frame_ids()

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
