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

def _import_expected(module_name):
    """ checks if an import of a specified module is possible

    Args:
        module_name: string name of the module it will try to import

    Returns: True if an import was successful, False if not

    """
    try:
        exec "import {0}".format(module_name)
        return True
    except:
        return False

def initialize_nodegraph():
    """ initializes the proper class for the detected host

    """
    _LOG.info("Initializing version {0}".format(version))

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
    _LOG.debug("Executable: {0}".format(sys.executable))
    if exec_filename:
        exec_name = os.path.splitext(exec_filename)[0]

        # detect executable by name
        # there might be launch process that will wrap the execution process
        # in that case we will check if we are able to import some required
        # modules to detect the host application
        if exec_name and "maya" in exec_name:
            if _import_expected("maya"):
                _LOG.info("Initializing Nodegraph Configuration for Maya")
        elif exec_name and "katana" in exec_name:
            if _import_expected("Katana"):
                _LOG.info("Initializing Nodegraph Configuration for Katana")
        else:
            hosts = _get_hosts()
            if len(hosts) != 1:
                raise NotImplementedError, "Not able to detect proper host. {0}".format(_ERROR_MSG)


initialize_nodegraph()
