import xmlrpc.client


class Simulation(object):
    """
    Simulation Mode object
    """

    def __init__(self, editURL, sessionAPI, mainAPI):
        self.url = editURL
        self.sessionAPI = sessionAPI
        self.mainAPI = mainAPI
        self.rpc = xmlrpc.client.ServerProxy(self.url)

    @staticmethod
    def createPayloadList(image_paths: [str, list]) -> list:
        """
        TODO

        :param image_paths:
        :return:
        """
        payloadList = []
        if isinstance(image_paths, list):
            for path in image_paths:
                with open(r"{p}".format(p=path), "rb") as fh:
                    buf = fh.read()
                    payloadList.append(xmlrpc.client.Binary(buf))
        else:
            with open(r"{p}".format(p=image_paths), "rb") as fh:
                buf = fh.read()
                payloadList.append(xmlrpc.client.Binary(buf))
        return payloadList

    def processImageSequence(self, image_sequence: list, force_trigger: bool) -> None:
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
        self.rpc.processImageSequence(image_sequence, force_trigger)

    def __getattr__(self, name):
        # Forward otherwise undefined method calls to XMLRPC proxy
        return getattr(self.rpc, name)
