import json
import logging
import os
import pprint

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
        super(ConfiguationMixin, self).__init__()
        self.__base_configuation_file = os.path.join(os.path.abspath("."), self.BASE_CONFIG_NAME)
        self.__data = None

        # initialize data
        self.restore_configuration()

    @property
    def configuration(self):
        return self.__data

    @configuration.setter
    def configuration(self, value):
        assert isinstance(value, DictDotLookup), "Expected type DictDotLookup. Got {0}".format(type(value))
        self.__data = value

    def load_configuration(self, configuration_file):
        _LOG.warning("Loading base configuration from {0}".format(configuration_file))
        data = read_json(configuration_file)
        self.configuration = DictDotLookup(data)

    def restore_configuration(self):
        self.load_configuration(self.__base_configuation_file)

    def save_configuration(self, filepath):
        _dir = os.path.dirname(filepath)
        assert os.path.exists(_dir), "Directory {0} doesn't exist.".format(_dir)

        write_json(filepath, self.configuration)


class DictDotLookup(object):
    """ Creates objects that behave much like a dictionaries, but allow nested
    key access using object dot lookups.

    """
    def __init__(self, d):
        for k in d:
            if isinstance(d[k], dict):
                self.__dict__[k] = DictDotLookup(d[k])
            elif isinstance(d[k], (list, tuple)):
                l = []
                for v in d[k]:
                    if isinstance(v, dict):
                        l.append(DictDotLookup(v))
                    else:
                        l.append(v)
                self.__dict__[k] = l
            else:
                self.__dict__[k] = d[k]

    def __getitem__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

    def __iter__(self):
        return iter(self.__dict__.keys())

    def __repr__(self):
        return pprint.pformat(self.__dict__)


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