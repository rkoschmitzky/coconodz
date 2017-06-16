try:
    from shiboken import wrapInstance
except:
    from shiboken2 import wrapInstance
#todo add logging

from Qt import QtWidgets

import maya.OpenMayaUI as omui


def wrapinstance(*args, **kwargs):
    return wrapInstance(*args, **kwargs)


def maya_main_window():
    """ Return the QMainWindow for the Maya main Window """

    ptr = omui.MQtUtil.mainWindow()
    if not ptr:
        raise RuntimeError('No Maya window found.')
    window = wrapinstance(long(ptr), QtWidgets.QMainWindow)
    return window


def maya_menu_bar():
    """ Maya menubar for """

    for child in maya_main_window().children():
        if isinstance(child, QtWidgets.QMenuBar):
            return child


