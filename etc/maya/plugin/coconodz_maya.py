import logging
import os
import sys

import maya.OpenMayaMPx as ommpx

PACKAGE_NAME = "coconodz"
VAR_NAME = "{0}_STARTUP".format(PACKAGE_NAME.upper())

LOG = logging.getLogger("CocoNodz.maya.plugin")
LOG.info("Launching {0}".format(PACKAGE_NAME))

# adding python paths
if VAR_NAME in os.environ:
    COCONODZ_PARENT = os.path.normpath(os.environ[VAR_NAME].split(PACKAGE_NAME, 1)[0].strip(";"))
    sys.path.append(COCONODZ_PARENT)

from coconodz import Qt
from coconodz import Nodzgraph as NODZGRAPH
from coconodz.etc.maya.ae.hooks import rebuild_attribute_editor
from coconodz.etc.maya.qtutilities import maya_menu_bar
from coconodz.lib import (Menu,
                          reload_modules)
from coconodz.version import version


PLUGIN_NAME = PACKAGE_NAME
PLUGIN_VERSION = "0.1.0"
COCONODZ_VERSION = version
COCONODZ_ICON = os.path.abspath(os.path.join(os.path.dirname(Qt.__file__), "..", "..", "icons", "coconodz.png"))


class MayaMenu(Menu):
    def __init__(self, menu_bar=maya_menu_bar()):
        super(MayaMenu, self).__init__(menu_bar)

        self.menu_bar = menu_bar

        # add all actions and connect them
        open_nodzgraph_action = self.add_action("Open Nodzgraph", COCONODZ_ICON)
        open_nodzgraph_action.triggered.connect(NODZGRAPH.open)
        #reload_coconodz_action = self.add_action("Reload CocoNodz")
        #reload_coconodz_action.triggered.connect(self.on_reload_coconodz_triggerd)

    def on_reload_coconodz_triggerd(self):
        reload_modules(PACKAGE_NAME)


MENU = MayaMenu()


def _to_plugin(mobject):
    return ommpx.MFnPlugin(mobject, PLUGIN_NAME, PLUGIN_VERSION)


def initializePlugin(mobject):
    LOG.info("Initializing CocoNodz")
    _to_plugin(mobject)
    # add CocoNodz menu
    MENU.init()
    # if there are not events registered reinitialize them
    if not NODZGRAPH.events.registered_events:
        NODZGRAPH.register_events()
    # refresh the attribute editor
    rebuild_attribute_editor()


def uninitializePlugin(mobject):
    LOG.info("Uninitialize CocoNodz")
    _to_plugin(mobject)
    # remove CocoNodz menu
    MENU.deleteLater()
    # remove all registered events
    NODZGRAPH.events.remove_all_events()
    # close open Nodzgraph instance
    NODZGRAPH.window.close()