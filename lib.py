import json
import logging
import os
import pprint

from Qt import (QtWidgets,
                QtGui,
                QtCore
               )


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


class BaseWindow(QtWidgets.QMainWindow):
    """ Sets up a simple Base window

    """
    TITLE = "CocoNodz Nodegraph"

    def __init__(self, parent):
        super(BaseWindow, self).__init__(parent)
        self.__parent = parent

        self._setup_ui()

    @property
    def central_widget(self):
        """ gets the set central widget

        Returns: QWidget

        """
        return self._central_widget

    @property
    def central_layout(self):
        """ gets the set central layout

        Returns: QVBoxLayout

        """
        return self._central_layout

    def _setup_ui(self):
        """ creates all widgets and actions and connects signals

        Returns:

        """
        self._central_widget = QtWidgets.QWidget(self.__parent)
        self._central_layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle(self.TITLE)
        self.setCentralWidget(self.central_widget)
        if not os.name == 'nt':
            self.setWindowFlags(QtCore.Qt.Tool)

        self.central_widget.setLayout(self.central_layout)


class BaseField(QtWidgets.QMenu):

    signal_available_items_changed = QtCore.Signal()

    def __init__(self, parent):
        super(BaseField, self).__init__(parent)

        self._items = None

    @property
    def available_items(self):
        return self._items

    @available_items.setter
    def available_items(self, items_dict):
        self._items = items_dict
        self.signal_available_items_changed.emit()

    def setup_ui(self):
        """ connect overall signals

        Returns:

        """
        self.signal_available_items_changed.connect(self.on_available_items_changed)

    def open(self):
        """ opens widget on cursor position

        Returns:

        """
        pos = QtGui.QCursor.pos()
        self.move(pos.x(), pos.y())
        self.exec_()


class AttributesField(BaseField):
    """ simple tree view widget we will use to display node attributes in nodegraph

    """

    signal_input_accepted = QtCore.Signal(str)

    def __init__(self, parent):
        super(AttributesField, self).__init__(parent)

        self._items = {}

    def _setup_tree_widget(self):
        pass

    def on_mask_accept(self):
        pass


class SearchField(BaseField):
    """ simple SearchField Widget we will use in the nodegraph

    """
    signal_input_accepted = QtCore.Signal(str)

    def __init__(self, parent):
        super(SearchField, self).__init__(parent)

        self._items = []
        self.setup_ui()

    def _setup_completer(self, line_edit_widget):
        """ creates a QCompleter and sets it to the given widget

        Args:
            line_edit_widget: QLineEdit

        Returns:

        """
        self.completer = QtWidgets.QCompleter(self.available_items)
        self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        line_edit_widget.setCompleter(self.completer)

    def setup_ui(self):
        """ extends the setup ui method

        This should create the base widgets and connect signals
        """
        super(SearchField, self).setup_ui()
        # set search field
        self.mask = QtWidgets.QLineEdit(self)
        self.action = QtWidgets.QWidgetAction(self)
        self.action.setDefaultWidget(self.mask)
        self.addAction(self.action)
        self.mask.setFocus()

        self.mask.returnPressed.connect(self.on_accept)

    @QtCore.Slot()
    def on_available_items_changed(self):
        """ actions that should run if items have changed

        Returns:

        """
        self._setup_completer(self.mask)

    def on_accept(self):
        """ sends signal if input is one of the available items

        Returns:

        """
        search_input = str(self.mask.text())
        if search_input in self.available_items:
            self.signal_input_accepted.emit(search_input)
            self.close()


class ConfiguationMixin(object):
    """ configuration class that makes dict/json type data accessable through dot lookups

    """
    BASE_CONFIG_NAME = "nodegraph.config"

    def __init__(self, *args, **kwargs):
        super(ConfiguationMixin, self).__init__(*args)
        self.__base_configuation_file = os.path.join(os.path.dirname(__file__), self.BASE_CONFIG_NAME)
        self.__data = None

    @property
    def configuration(self):
        """ holds the configuration

        Returns: DictDotLookup

        """
        return self.__data

    @configuration.setter
    def configuration(self, value):
        """ sets the coniguration

        Args:
            value: dict

        Returns:

        """
        assert isinstance(value, DictDotLookup), "Expected type DictDotLookup. Got {0}".format(type(value))
        self.__data = value

    @property
    def configuration_data(self):
        """ holds the configuration data as dictionary

        Returns: dict

        """
        return self.configuration.get_original()

    def load_configuration(self, configuration_file):
        """ loads any json schema file and converts it to our proper configuration object

        Args:
            configuration_file: filepath

        Returns:

        """
        _LOG.warning("Loading base configuration from {0}".format(configuration_file))
        data = read_json(configuration_file)
        self.configuration = DictDotLookup(data)

    def initialize_configuration(self):
        """ loads the predifined default configuration file and converts it to our proper configurarion object

        Returns:

        """
        self.load_configuration(self.__base_configuation_file)

    def save_configuration(self, filepath):
        """ saves the current configuration as json schema

        Args:
            filepath: filepath

        Returns:

        """
        _dir = os.path.dirname(filepath)
        assert os.path.exists(_dir), "Directory {0} doesn't exist.".format(_dir)

        write_json(filepath, self.configuration_data)


class DictDotLookup(object):
    """ Creates objects that behave much like a dictionaries, but allow nested
    key access using object dot lookups.

    """
    def __init__(self, d):
        self.__original_data = d
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

    def get_original(self):
        return self.__original_data


def write_json(filepath, data):
    """ helper to save data to json

    Args:
        filepath: filepath
        data: json serializable data, e.g. dict

    Returns:

    """
    with SafeOpen(filepath, 'w') as f:
        f.write(json.dumps(data))


def read_json(filepath):
    """ helper to parse json schema files

    Args:
        filepath: filepath

    Returns: dict

    """
    with SafeOpen(filepath, 'r') as f:
        data = None
        try:
            data = json.loads(f.read())
            return data
        except ValueError:
            return data