from coconodz import Qt

import maya.OpenMayaUI as omui


def maya_main_window():
    """ gets Mayas Main Window

    Returns: QMainWindow

    """

    ptr = omui.MQtUtil.mainWindow()
    if not ptr:
        raise RuntimeError('No Maya window found.')
    window = Qt.QtCompat.wrapInstance(long(ptr), Qt.QtWidgets.QMainWindow)
    return window


def maya_menu_bar():
    """ gets Mayas Main Menu Bar

    Returns: QMenuBar

    """
    for child in maya_main_window().children():
        if isinstance(child, Qt.QtWidgets.QMenuBar):
            return child


