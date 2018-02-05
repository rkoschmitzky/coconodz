import logging
import os
import sys


__author__ = "Rico Koschmitzky"
__email__ = "contact@ricokoschmitzky.com"


ERROR_MSG = "Looks like you want to run CocoNodz in a unknown environment." + \
            "Please email the author {0} : {1}".format(__author__, __email__)

LOG = logging.getLogger(name="CocoNodz")
LOG.addHandler(logging.StreamHandler(sys.__stdout__))
LOG.setLevel(logging.WARNING)

from coconodz.version import version

# appending relevant submodule paths for CocoNodz
try:
    _path = os.path.join(__path__[0], "site-packages")
    sys.path.append(_path)
    sys.path.append(os.path.join(_path, "Qt.py"))
except:
    pass

import Qt as Qt
from eventsmanager import (Manager,
                           SuppressEvents
                           )

# check if we can have a for standalone execution QApplication
try:
    application = Qt.QtWidgets.QApplication([])
except:
    application = None
    LOG.debug("Retrieving QApplication")


def _import_expected(module_name):
    """ checks if an import of a specified module is possible

    Args:
        module_name: string name of the module it will try to import

    Returns: True if an import was successful, False if not

    """
    try:
        __import__(module_name)
        return True
    except ImportError:
        LOG.error("Not able to import expected host modules.", exc_info=True)
        return False


LOG.info("Initializing version {0}".format(version))

hosts = []

# find hosts by module imports
def _get_hosts():
    module = "maya"
    if _import_expected(module):
        hosts.append(module)
    module = "Katana"
    if _import_expected(module):
        hosts.append(module)
    return hosts

exec_filename = os.path.basename(sys.executable)
LOG.debug("Executable: {0}".format(sys.executable))

if exec_filename:
    exec_name = os.path.splitext(exec_filename)[0]

    # detect executable by name
    # there might be launch process that will wrap the execution process
    # in that case we will check if we are able to import some required
    # modules to detect the host application
    if exec_name and "maya" in exec_name:
        if _import_expected("maya"):
            LOG.info("Initializing Nodegraph Configuration for Maya")
            host = "maya"
    elif exec_name and "katana" in exec_name:
        if _import_expected("Katana"):
            LOG.info("Initializing Nodegraph Configuration for Katana")
            host = "katana"

    # set to no host when required
    if os.environ.get("COCONODZ_IGNORE_HOST", 0):
        host = "no_host"
    else:
        hosts = _get_hosts()
        if len(hosts) != 1:
            raise NotImplementedError("Not able to detect proper host. {0}".format(ERROR_MSG))

        elif len(hosts) == 1:
                host = hosts[0]
        else:
            host = "no_host"

    if host == "maya":
        from coconodz.etc.maya.nodegraph import Nodzgraph as _Nodzgraph
        Nodzgraph = _Nodzgraph()
    elif host == "katana":
        from coconodz.etc.katana.nodegraph import Nodzgraph as _Nodzgraph
        Nodzgraph = _Nodzgraph()
    elif host == "no_host":
        from coconodz import nodegraph
        Nodzgraph = nodegraph.Nodegraph()