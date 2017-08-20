NAME = "CocoNodz"

VERSION_MAJOR = 0
VERSION_MINOR = 0
VERSION_PATCH = 1

version_info = [str(VERSION_MAJOR), str(VERSION_MINOR), str(VERSION_PATCH)]
version = ".".join(version_info)
__version__ = version

__all__ = ["version", "version_info", "__version__"]