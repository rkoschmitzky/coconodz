import logging
import os
import sys

from version import version

__author__ = "Rico Koschmitzky"
__email__ = "contact@ricokoschmitzky.com"

sys.path.append(os.path.join(os.path.abspath("."), "site-packages"))

#todo remove temporary adding of Nodz
sys.path.append(os.path.join(os.path.abspath(".."), "Nodz"))


_ERROR_MSG = "Looks like you want to run CocoNodz in a unknown environment." + \
            "Please email the author {0} : {1}".format(__author__, __email__)

_LOG = logging.getLogger(name="CocoNodz")
_LOG.addHandler(logging.StreamHandler())
_LOG.setLevel(logging.DEBUG)

def initialize_nodegraph():

    _LOG.info("Initializing version {0}".format(version))

    exec_filename = os.path.basename(sys.executable)
    if exec_filename:
        exec_name = os.path.splitext(exec_filename)[0]
        if exec_name and exec_name == "maya" or exec_name == "mayapy":
            _LOG.info("Initializing Maya Nodegraph")
        elif exec_name and exec_name == "katanaBin":
            _LOG.info("Initializing Katana Nodegraph")
        else:
            raise NotImplementedError, _ERROR_MSG


initialize_nodegraph()
