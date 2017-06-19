from collections import namedtuple
import json
import logging
import os

_LOG = logging.getLogger(name="CocoNodz.nodegraph")


class SafeOpen(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.f = None

    def __enter__(self):
        try:
            self.f = open(*self.args, **self.kwargs)
            return self.f
        except:
            raise IOError('Could not open %s' % self.args)

    def __exit__(self, *exc_info):
        if self.f:
            self.f.close()


class ConfiguationMixin(object):

    BASE_CONFIG_NAME = "nodegraph.config"

    def __init__(self):
        self.__base_configuation_file = os.path.join(os.path.abspath("."), self.BASE_CONFIG_NAME)
        self.__data = {}

        # initialize data
        self.restore_configuration()

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        assert isinstance(value, dict), "Expected type dict. Got {0}".format(type(value))
        self.__data = _namedtuplify(value, "configuration")

    def load_configuration(self, configuration_file):
        _LOG.warning("Loading base configuration from {0}".format(configuration_file))
        data = read_json(configuration_file)
        self.data = data

    def restore_configuration(self):
        self.load_configuration(self.__base_configuation_file)


def _namedtuplify(mapping, name='NT'):
    """ Convert mappings to namedtuples recursively. """

    if isinstance(mapping, dict):
        for key, value in list(mapping.items()):
            mapping[key] = _namedtuplify(value)
        return _namedtuple_wrapper(name, **mapping)
    elif isinstance(mapping, list):
        return [_namedtuplify(item) for item in mapping]
    return mapping


def _namedtuple_wrapper(name, **kwargs):
    wrap = namedtuple(name, kwargs)
    return wrap(**kwargs)


def write_json(filepath, data):
    with SafeOpen(filepath, 'w') as f:
        f.write(json.dumps(data))


def read_json(filepath):
    with SafeOpen(filepath, 'r') as f:
        data = None
        try:
            data = json.loads(f.read())
            return data
        except ValueError:
            return data