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


def get_used_attribute_type(attribute):
    """ gets the currently used attribute type

    Args:
        attribute:

    Returns: Corresponding our attribute naming it will return "socket" if an attribute
    has incoming and outgoing connections, "plug" if it

    """
    sources = attribute.listConnections(s=True, d=False)
    destinations = attribute.listConnections(s=False, d=True)

    if sources and destinations:
        return "slot"
    elif sources:
        return "socket"
    else:
        return "plug"


def get_connected_attributes_in_node_tree(node_or_nodes, node_types=None):
    """ gets all attributes, its type, the node_type and data_type

    Args:
        node_or_nodes: all connected attributes belonging to the node or nodes
        node_types: if unspecified it will only add the node of the given node_types

    Returns: dict {attribute: {"node_type": "some_node_type",
                               "data_type": "some_data_type",
                               "type": "some_attribute_type"
                               }
                  }
    """
    # find all nodes connected in tree and remove doubled
    tree_nodes = list(set(pmc.listHistory(node_or_nodes, f=True, ac=True) + pmc.listHistory(node_or_nodes, ac=True)))
    all_connected_attributes = []

    # checks if the attribute is a relevant attribute by checking
    # the node types of the nodes connected to it
    def _check_node_type(attribute):
        if node_types:
            is_relevant = False
            if attribute.nodeType() in node_types:
                dependencies = attribute.connections(p=True)
                if dependencies:
                    for dependency in dependencies:
                        if not is_relevant and dependency.nodeType() in node_types:
                            is_relevant = True
            if is_relevant:
                all_connected_attributes.append(attribute)
        else:
            all_connected_attributes.append(attribute)

    # based on all nodes in tree get all related attributes
    # do the filtering and check if the attribute is relevant
    for connection in pmc.listConnections(tree_nodes, c=True, p=True):
        source, destination = connection
        if source not in all_connected_attributes:
            _check_node_type(source)
        if destination not in all_connected_attributes:
            _check_node_type(destination)

    # subdict skeleton every keys value in attribute should have
    subdict = {"node_type": None,
               "data_type": None,
               "type": None}

    attribute_dict = {}
    for attribute in all_connected_attributes:
        _ = subdict.copy()
        _["node_type"] = attribute.nodeType()
        _["data_type"] = attribute.type()
        _["type"] = get_used_attribute_type(attribute)
        attribute_dict[attribute.name()] = _

    return attribute_dict


def get_connections(node_or_nodes):
    """ gets all connections for a single or multiple nodes

    Args:
        node_or_nodes: node name or PyNode instance (list)

    Returns: dict {slot: slot}

    """
    # find all nodes connected in tree and remove doubled
    tree_nodes = list(set(pmc.listHistory(node_or_nodes, f=True, ac=True) + pmc.listHistory(node_or_nodes, ac=True)))
    return {str(x): str(y) for x, y in pmc.listConnections(tree_nodes, c=True, p=True, s=False)}
