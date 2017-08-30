import pymel.core as pmc


def get_attribute_tree(node):
    """ traverses attributes on given node and gets dict in form the attribute tree widget expects

    Args:
        node: PyNode

    Returns: dict

    """
    parents = {}
    for attr in node.listAttr():

        if not attr.isChild() and not attr.isMulti():
            # add children
            if not attr.longName() in parents:
                parents[attr.longName()] = []
                for _attr in attr.iterDescendants():
                    parents[attr.longName()].append(_attr.longName())
        # for some reason the iterDescentants method is not returning the proper children
        elif attr.isMulti():
            parents[attr.longName()] = [_attr.longName() for _attr in attr.children()]

    return parents


def get_attributes_dict(selection):

    get_connected_attributes_in_node_tree(selection)


def get_connected_attributes_in_node_tree(node, node_types=None):

    all_connections = []

    def _get_connections(node):

        connections = node.listConnections(connections=True)
        for connection in connections:
            for _ in _get_connections(connection[0].node()):
                all_connections.append(_)

    _get_connections(node)
    print all_connections