from __future__ import (absolute_import, division, print_function)
from builtins import *
from o2x5xx.pcic.client import O2x5xxDevice
from o2x5xx.static.formats import serialization_format
from o2x5xx.static.configs import images_config
import binascii
import struct
import io
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


class ImageClient(O2x5xxDevice):
	def __init__(self, address, port):
		super(ImageClient, self).__init__(address, port)

		# disable all result output
		self.turn_process_interface_output_on_or_off(0)

		# format string for all images
		answer = self.upload_process_interface_output_configuration(images_config)
		if answer != "*":
			raise

		# enable result output again
		self.turn_process_interface_output_on_or_off(1)

		# read the image ids
		self.image_IDs = self.read_image_ids()

		# read first frames
		self.frames = []
		self.read_next_frames()

	@property
	def number_images(self):
		"""
		A function for which returns the number of images from application.

		:return: (int) number of images
		"""
		return self.image_IDs.__len__()

	def read_image_ids(self):
		"""
		A function for reading the PCIC image output and parsing the image IDs.
		The image IDs are stored in property self.image_IDs

		:return: list of image ids
		"""
		ticket, answer = self.read_next_answer()

		if ticket == b"0000":
			delimiter = str(answer).find('stop')
			ids = answer[:delimiter-12].decode()
			return ids.split(';')[1:-1]

	@staticmethod
	def _deserialize_image_chunk(data):
		"""
		Function for deserializing the PCIC image output.

		:param data: PCIC image output
		:return: deserialized results
		"""
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
			image = mpimg.imread(io.BytesIO(image_hex), format='jpg')
			results[counter].append(image)

			length -= header['CHUNK_SIZE']
			data = data[header['CHUNK_SIZE']:]
			counter += 1

		return results

	def read_next_frames(self):
		"""
		Function for reading next asynchronous frames.
		Frames are stored in property self.frames

		:return: None
		"""
		# look for asynchronous output
		ticket, answer = self.read_next_answer()

		if ticket == b"0000":
			delimiter = str(answer).find('stop')
			result = self._deserialize_image_chunk(data=answer[delimiter-8:])
			self.frames = [result[i][1] for i in result]

	def make_figure(self, idx):
		"""
		Function for making figure object and using parsed image ID as subtitle.

		:param idx: (int) list index of self.image.IDs property <br />
					e.g. idx == 0 would read string value '2'
					from self.image.IDs = ['2', '4']

		:return: Syntax: [&lt;fig>, &lt;ax>, &lt;im>] <br />
						- &lt;fig>: matplotlib figure object <br />
						- &lt;ax>: AxesSubplot instance of figure object <br />
						- &lt;im>: AxesImage instance of figure object
		"""
		if idx+1 > self.number_images:
			raise ValueError("Only {} images available. Use an idx value between 0 and {}".format(self.number_images, self.number_images-1))
		fig = plt.figure()
		fig.suptitle('Image: I{}'.format(self.image_IDs[idx]))
		ax = fig.add_subplot(1, 1, 1)

		im = ax.imshow(self.frames[idx], animated=True, cmap='gray', aspect='equal')

		return fig, ax, im
