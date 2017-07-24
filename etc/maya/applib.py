import pymel.core as pmc


def get_attribute_tree(node):
    """ traverses attributes on given node and gets dict in form the attribute tree widget expects

    Args:
        node: PyNode

    Returns: dict

    """
    parents = {}
    for attr in node.listAttr():
        _parent = attr.getParent(arrays=True)
        if not _parent and not attr.name() in parents:
            if not attr.isArray() and not attr.isChild():
                parents[attr.longName()] = []
            elif attr.isArray():
                parents[attr.longName()] = [attr.longName() for attr in attr.children()]
        elif _parent and _parent.longName() in parents:
            parents[_parent.longName()].append(attr.longName())
    return parents


