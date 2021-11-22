from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
from o2x5xx import ImageClient
import io
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation

imageWidth = 1280
imageHeight = 960

if __name__ == '__main__':
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = '192.168.0.69'

    # create grabber
    image_client = ImageClient(address, 50010)

    # create figures
    figs = [image_client.make_figure(i) for i in range(image_client.number_images)]

    def update_fig(*args):
        if args[2]:
            image_client.read_next_frames()
        im = args[1]
        # image_id = args[0]
        # print('Current image id is: {}'.format(image_id))
        # print('Arguments are: {}'.format(*args))
        # if args[1]:
        #     image_client.read_next_frames()

        image = mpimg.imread(io.BytesIO(image_client.frames[0][1]), format='jpg')
        im = plt.imshow(image, animated=True, cmap='gray', aspect='equal')

        return im,


    # List of Animation objects for tracking
    anim = []

    # Animate the figures
    read_answer_flag = True
    for i, frame_figure in enumerate(figs):
        fig, ax, im = frame_figure
        anim.append(animation.FuncAnimation(fig, update_fig, frames=2, interval=50, blit=True, fargs=[i, read_answer_flag]))
        # anim = animation.FuncAnimation(fig,  update_fig, interval=50, blit=True, fargs=[i, read_answer_flag])
        read_answer_flag = False

    # def update_fig(*args):
    #     image_id = args[0]
    #     image_client.read_next_frames()
    #
    #     image = mpimg.imread(io.BytesIO(image_client.frames[image_id][1]), format='jpg')
    #     im = plt.imshow(image, animated=True, cmap='gray', aspect='equal')
    #
    #     return im,
    #
    # for i, fig in enumerate(figs):
    #     print(i)
    # for i, fig in enumerate(figs):
    #     ani = animation.FuncAnimation(fig, update_fig, interval=50, blit=True, fargs=[i])

    plt.tight_layout()
    plt.show()
