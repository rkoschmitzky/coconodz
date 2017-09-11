from coconodz import application


def get_katana_main_window():
    for widget in application.topLevelWidgets():
        if widget.objectName() == "mainWindow":
            return widget
