if __name__ == '__main__':
    # open Nodzgraph standalone
    from coconodz import (Nodzgraph,
                          application
                          )

    if application:
        Nodzgraph.open()
        application.exec_()
