from __future__ import (absolute_import, division, print_function)
from builtins import *
from .client import O2x5xxPCICDevice
from ..static.formats import serialization_format, ChunkType
from ..static.configs import images_config
import struct
import io
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np


SOCKET_TIMEOUT = 10


class ImageClient(O2x5xxPCICDevice):
	def __init__(self, address, port, timeout=SOCKET_TIMEOUT):
		super(ImageClient, self).__init__(address=address, port=port, timeout=timeout)

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
			delimiter = answer.find(b'stop')
			if delimiter == -1:
				print("stop identifier not found in result")
				return []
			ids = answer[5:delimiter].decode()
			return ids.split(';')[0:-1]

	@staticmethod
	def _deserialize_image_chunk(data):
		"""
		Function for deserializing the PCIC image output.

		:param data: PCIC image output
		:return: deserialized results
		"""
		results = {}
		length = len(data)
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
			chunk_type = int(header['CHUNK_TYPE'])
			# check end decode image depending on chunk type
			if chunk_type == ChunkType.JPEG_IMAGE:
				# Check that we have received chunk type JPEG_IMAGE
				# Convert jpeg data to image data
				image = mpimg.imread(io.BytesIO(image_hex), format='jpg')
				results[counter].append(image)
			elif chunk_type == ChunkType.MONOCHROME_2D_8BIT:
				# Check that we have received chunk type MONOCHROME_2D_8BIT
				# Read pixel data and reshape to width/height
				image = np.frombuffer(image_hex, dtype=np.uint8) \
					.reshape((header["IMAGE_HEIGHT"], header["IMAGE_WIDTH"]))
				results[counter].append(image)
			else:
				image = None
				print("Unknown image chunk type", header['CHUNK_TYPE'])
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
			delimiter = answer.find(b'stop')
			if delimiter == -1:
				print("stop identifier not found in result")
				self.frames = []
			result = self._deserialize_image_chunk(data=answer[delimiter+4:])
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
