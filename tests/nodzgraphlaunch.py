from coconodz import (Nodzgraph,
                      application,
                      Qt
                      )
from coconodz.lib import Backdrop


if __name__ == '__main__':
    # open Nodzgraph standalone
    if application:

        text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."

        Nodzgraph.open()
        Nodzgraph.graph.creation_field.available_items = ["test", "backdrop"]
        backdrop = Backdrop("test")
        #backdrop_two = BackdropItem("aaaa", bounds=(0, 0, 150, 150), color=(0, 255, 255, 100))
        Nodzgraph.graph.scene().addItem(backdrop)
        application.exec_()