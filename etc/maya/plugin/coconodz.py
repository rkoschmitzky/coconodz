import logging
import os
import sys

PACKAGE_NAME = "coconodz"
VAR_NAME = "{0}_STARTUP".format(PACKAGE_NAME.upper())

_LOG = logging.getLogger("Coconodz.startup.Maya")
_LOG.info("Launching startup Script")


# adding python paths
if VAR_NAME in os.environ:
    COCONODZ_PARENT = os.path.normpath(os.environ[VAR_NAME].split(PACKAGE_NAME, 1)[0].strip(";"))
    sys.path.append(COCONODZ_PARENT)
    sys.path.append(os.path.join(COCONODZ_PARENT, PACKAGE_NAME))
    sys.path.append(os.path.join(COCONODZ_PARENT, PACKAGE_NAME, "site-packages"))


import maya.OpenMayaMPx as ommpx

from etc.maya.qtutilities import maya_menu_bar
from etc.maya.nodegraph import Nodzgraph
from lib import Menu
import version


PLUGIN_NAME = version.NAME
PLUGIN_VERSION = "0.1.0"
COCONODZ_VERSION = version.version

LOG = logging.getLogger("CocoNodz.maya.plugin")


class MayaMenu(Menu):

    NODZGRAPH = Nodzgraph()

    def __init__(self, menu_bar=maya_menu_bar()):
        super(MayaMenu, self).__init__(menu_bar)

        self.menu_bar = menu_bar

        # add all actions and connect them
        open_nodzgraph_action = self.add_action("Open Nodzgraph")
        open_nodzgraph_action.triggered.connect(self.NODZGRAPH.open)


MENU = MayaMenu()


def _to_plugin(mobject):
    return ommpx.MFnPlugin(mobject, PLUGIN_NAME, PLUGIN_VERSION)


def initializePlugin(mobject):
    LOG.info("Initializing CocoNodz")
    _to_plugin(mobject)
    # add CocoNodz menu
    MENU.init()
    # if there are not events registered reinitialize them
    if not MENU.NODZGRAPH.events.registered_events:
        MENU.NODZGRAPH.register_events()


def uninitializePlugin(mobject):
    LOG.info("Uninitialize CocoNodz")
    _to_plugin(mobject)
    # remove CocoNodz menu
    MENU.deleteLater()
    # remove all registered events
    MENU.NODZGRAPH.events.remove_all_events()

    # close open Nodegraph instance
    # @todo remove all instances
    MENU.NODZGRAPH.window.close()