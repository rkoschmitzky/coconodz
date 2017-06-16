try:
    from shiboken import wrapInstance
except:
    from shiboken2 import wrapInstance


def wrapinstance(*args, **kwargs):
    return wrapInstance(*args, **kwargs)