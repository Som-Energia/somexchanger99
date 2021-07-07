import io
import logging
import os
import re


logger = logging.getLogger(__name__)


class ReaderCapabilities:

    def open(self):
        pass

    def readData(self) -> dict:
        pass

    def close(self):
        pass


class WriterCapabilities:

    def open(self):
        pass

    def writeData(self) -> dict:
        pass

    def close(self):
        pass
