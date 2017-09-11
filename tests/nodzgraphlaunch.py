if __name__ == '__main__':
    # open Nodzgraph standalone
    from coconodz import (Nodzgraph,
                          application
                          )

    if application:
        Nodzgraph.open()
        Nodzgraph.graph.creation_field.available_items = ["test"]
        application.exec_()