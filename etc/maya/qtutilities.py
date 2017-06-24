try:
    from shiboken import wrapInstance
except:
    from shiboken2 import wrapInstance
#todo add logging

from Qt import QtWidgets

import maya.OpenMayaUI as omui


def wrapinstance(*args, **kwargs):
    """ shiboken and shiboken2 compatible wrapInstance function

    Args:
        *args:
        **kwargs:

    Returns:

    """
    return wrapInstance(*args, **kwargs)


def maya_main_window():
    """ gets Mayas Main Window

    Returns: QMainWindow

    """

    ptr = omui.MQtUtil.mainWindow()
    if not ptr:
        raise RuntimeError('No Maya window found.')
    window = wrapinstance(long(ptr), QtWidgets.QMainWindow)
    return window


def maya_menu_bar():
    """ gets Mayas Main Menu Bar

    Returns: QMenuBar

    """
    for child in maya_main_window().children():
        if isinstance(child, QtWidgets.QMenuBar):
            return child


