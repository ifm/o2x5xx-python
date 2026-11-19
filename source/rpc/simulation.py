import xmlrpc.client

class Simulation(object):
    """
    Simulation Mode object
    """

    def __init__(self, simulationProxy, device):
        self._simulationProxy = simulationProxy
        self._device = device

    @staticmethod
    def createPayloadList(imagePaths: list = [str, list]) -> list:
        """
        Creates a list of xmlrpc.client.Binary objects from a list of image paths or a single image path.
        The images should be in the format as generated in the service report (JPEG, 1280 x 960, grayscale 8 bit).

        :param imagePaths: list of image paths or a single image path
        :return:
        """
        payloadList = []
        if isinstance(imagePaths, list):
            for path in imagePaths:
                with open(r"{p}".format(p=path), "rb") as fh:
                    buf = fh.read()
                    payloadList.append(xmlrpc.client.Binary(buf))
        else:
            with open(r"{p}".format(p=imagePaths), "rb") as fh:
                buf = fh.read()
                payloadList.append(xmlrpc.client.Binary(buf))
        return payloadList

    def processImageSequence(self, imageSequence: list, forceTrigger: bool = True) -> None:
        """
        Sends an Image Sequence and decode them.
        An additional parameter exists to define if a software trigger should be generated.
        Notice that the number of images in the image sequence should match the number of image configurations
        defined in the currently active application.
        An "Image sequence" is a list of images that are meant to be decoded by the device in Simulation-Operating Mode.
        Each image in the list should have the same format. Supported format for the images is:

        \* JPEG format as generated in the service report

        \* Size as generated in the service report: 1280 x 960

        \* Color format as generated in the service report: grayscale 8 bit

        :return: None
        """
        self._simulationProxy.proxy.processImageSequence(imageSequence, forceTrigger)
