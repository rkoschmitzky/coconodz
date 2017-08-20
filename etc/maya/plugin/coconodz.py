import logging
import os
import sys

_PACKAGE_NAME = "coconodz"
_VAR_NAME = "{0}_STARTUP".format(_PACKAGE_NAME.upper())

_LOG = logging.getLogger("Coconodz.startup.Maya")
_LOG.info("Launching startup Script")


# adding python paths
if _VAR_NAME in os.environ:
    COCONODZ_PARENT = os.path.normpath(os.environ[_VAR_NAME].split(_PACKAGE_NAME, 1)[0].strip(";"))
    sys.path.append(COCONODZ_PARENT)
    sys.path.append(os.path.join(COCONODZ_PARENT, _PACKAGE_NAME))
    sys.path.append(os.path.join(COCONODZ_PARENT, _PACKAGE_NAME, "site-packages"))


import maya.OpenMayaMPx as ommpx

from etc.maya.qtutilities import maya_menu_bar
from etc.maya.nodegraph import Nodzgraph
from lib import Menu
import version


plugin_name = version.NAME
plugin_version = "0.1.0"
coconodz_version = version.version

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


def _toplugin(mobject):
    return ommpx.MFnPlugin(mobject, plugin_name, plugin_version)


def initializePlugin(mobject):
    LOG.info("Initializing CocoNodz")
    _toplugin(mobject)
    # add CocoNodz menu
    MENU.init()
    # if there are not events registered reinitialize them
    if not MENU.NODZGRAPH.events.registered_events:
        MENU.NODZGRAPH.register_events()


def uninitializePlugin(mobject):
    LOG.info("Uninitialize CocoNodz")
    _toplugin(mobject)
    # remove CocoNodz menu
    MENU.deleteLater()
    # remove all registered events
    MENU.NODZGRAPH.events.remove_all_events()

    # close open Nodegraph instance
    # @todo remove all instances
    MENU.NODZGRAPH.window.close()