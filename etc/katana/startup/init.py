import logging
import os
import sys

PACKAGE_NAME = "coconodz"
VAR_NAME = "{0}_STARTUP".format(PACKAGE_NAME.upper())

_LOG = logging.getLogger("Coconodz.startup.Katana")

# adding python paths
if VAR_NAME in os.environ:
    COCONODZ_PARENT = os.path.normpath(os.environ[VAR_NAME].split(PACKAGE_NAME, 1)[0].strip(";"))
    sys.path.append(COCONODZ_PARENT)