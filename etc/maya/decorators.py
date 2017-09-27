import maya.utils


def execute_deferred(func):
    """ decorator that allows to execute the passed function deferred

    Args:
        func: function callable

    Returns: result

    """
    def inner(*args, **kwargs):
        result = maya.utils.executeDeferred(func, *args, **kwargs)
        return result

    return inner
