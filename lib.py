import json
import logging
import os
import pprint
import sys

from coconodz import Qt


LOG = logging.getLogger(name="CocoNodz.nodegraph")


class Singleton(object):
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance


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


class BaseWindow(Qt.QtWidgets.QMainWindow):
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
        self._central_widget = Qt.QtWidgets.QWidget(self.__parent)
        self._central_layout = Qt.QtWidgets.QVBoxLayout()
        self.setWindowTitle(self.TITLE)
        self.setCentralWidget(self.central_widget)
        if not os.name == 'nt':
            self.setWindowFlags(Qt.QtCore.Qt.Tool)

        self.central_widget.setLayout(self.central_layout)


class ContextWidget(Qt.QtWidgets.QMenu):

    signal_available_items_changed = Qt.QtCore.Signal()
    signal_opened = Qt.QtCore.Signal()

    def __init__(self, parent):
        super(ContextWidget, self).__init__(parent)

        self._items = None
        self._context = None
        self._expect_msg = "Expected type {0}, got {1} instead"

    @property
    def available_items(self):
        return self._items

    @available_items.setter
    def available_items(self, items_dict):
        self._items = items_dict
        self.signal_available_items_changed.emit()

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context_widget):
        self._context = context_widget
        self._update_context()

    def _update_context(self):
        self.clear()
        action = Qt.QtWidgets.QWidgetAction(self)
        action.setDefaultWidget(self.context)
        self.addAction(action)

    def setup_ui(self):
        """ connect overall signals

        Returns:

        """
        self.signal_available_items_changed.connect(self.on_available_items_changed)

    def open(self):
        """ opens widget on cursor position

        Returns:

        """
        self.signal_opened.emit()
        pos = Qt.QtGui.QCursor.pos()
        self.move(pos.x(), pos.y())
        self.exec_()


class GraphContext(ContextWidget):

    def __init__(self, parent):
        super(GraphContext, self).__init__(parent)

        # defining items as empty list, because we want to loop trough
        # in the setup_ui method
        self.available_items = list()
        self.setup_ui()

    def add_button(self, button):
        """ allows the addition of QPushButton instances to main layout only

        Args:
            button:

        Returns:

        """
        assert isinstance(button, Qt.QtWidgets.QPushButton), \
            self._expect_msg.format(Qt.QtWidgets.QPushButton, type(button))
        self.central_layout.addWidget(button)
        LOG.info("Added button {0}".format(button))

    def setup_ui(self):
        super(GraphContext, self).setup_ui()
        widget = Qt.QtWidgets.QWidget(self)
        layout = Qt.QtWidgets.QVBoxLayout(widget)
        for button in self.available_items:
            layout.addWidget(button)
        self.context = widget

    def on_available_items_changed(self):
        """ actions that should run if items have changed

        Returns:

        """
        self.setup_ui()


class AttributeContext(ContextWidget):
    """ simple tree view widget we will use to display node attributes in nodegraph

    """

    signal_input_accepted = Qt.QtCore.Signal(str, str)

    def __init__(self, parent, mode=""):
        super(AttributeContext, self).__init__(parent)

        # defining items as empty list, because we want to pass dictionary-like data
        # within the tree widget in the setup_ui method
        self.available_items = dict()
        self._mode = mode
        self._tree_widget = None
        self._mask_widget = None
        self._column = 0
        self.setup_ui()

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        assert isinstance(value, basestring), self._expect_msg.format("string", type(value))
        self._mode = value

    @property
    def tree_widget(self):
        return self._tree_widget

    @tree_widget.setter
    def tree_widget(self, tree_widget):
        self._tree_widget = tree_widget

    @property
    def mask_widget(self):
        return self._mask_widget

    @mask_widget.setter
    def mask_widget(self, line_edit_widget):
        self._mask_widget = line_edit_widget

    def _populate_tree(self, tree_widget):
        """ based on the dictionary data this will add all the items

        Args:
            tree_widget: QTreeWidget

        Returns:

        """
        tree_items = []
        # recursive items addition
        def _add_items(parent, data):
            for key, value in data.iteritems():
                tree_item = Qt.QtWidgets.QTreeWidgetItem(parent)
                tree_item.setText(0, key)
                tree_widget.addTopLevelItem(tree_item)
                tree_items.append(tree_item)
                if value:
                    if isinstance(value, (basestring, int, float, bool)):
                        value = list([value])
                    if isinstance(value, (list, tuple)):
                        for member in value:
                            child = Qt.QtWidgets.QTreeWidgetItem(tree_item)
                            child.setText(0, member)
                            tree_item.addChild(child)
                            tree_items.append(child)
                    if isinstance(value, dict):
                        if not isinstance(parent, Qt.QtWidgets.QTreeWidget):
                            parent.addChild(tree_item)
                        else:
                            _add_items(tree_item, value)

        # add all items
        _add_items(tree_widget, self.available_items)

    def setup_ui(self):
        super(AttributeContext, self).setup_ui()

        widget = Qt.QtWidgets.QWidget(self)
        filter_layout = Qt.QtWidgets.QHBoxLayout()
        label = Qt.QtWidgets.QLabel("Filter:")
        mask = Qt.QtWidgets.QLineEdit()
        filter_layout.addWidget(label)
        filter_layout.addWidget(mask)

        layout = Qt.QtWidgets.QVBoxLayout(widget)
        layout.addLayout(filter_layout)

        tree = Qt.QtWidgets.QTreeWidget()
        tree.setColumnCount(self._column + 1)
        tree.setHeaderLabels([self.mode])
        tree.sortItems(self._column, Qt.QtCore.Qt.AscendingOrder)

        layout.addWidget(tree)
        self._populate_tree(tree)

        tree.doubleClicked.connect(self.on_tree_double_clicked)
        mask.textChanged.connect(self.on_filter_changed)

        self.context = widget
        self.tree_widget = tree
        self.mask_widget = mask

    def on_available_items_changed(self):
        """ actions that should run if items have changed

        Returns:

        """
        self.setup_ui()

    def on_tree_double_clicked(self, index):
        if self.tree_widget:
            self.signal_input_accepted.emit(self.property("node_name"),
                                            self.tree_widget.itemFromIndex(index).text(self._column))

    def on_filter_changed(self):
        """ look for item text matches based on the filter string and display only matched items

        Returns:

        """
        # couldn't find an easy way to get a list of currently
        # displayed items, therefore this implementations has to hide all items first
        # looking for string matched on all items
        # and unhide all matched items and all their parents recursively

        # recursively enabling item visibilities upstream
        def _unhide_parent(item):
            item.setHidden(False)
            if item.parent():
                _unhide_parent(item.parent())

        iterator = Qt.QtWidgets.QTreeWidgetItemIterator(self.tree_widget, Qt.QtWidgets.QTreeWidgetItemIterator.All)
        while iterator.value():
            iterator.value().setHidden(True)
            iterator += 1

        # look for matches and show them
        input_string = str(self.mask_widget.text())
        if input_string != "":
            matched_items = self.tree_widget.findItems(input_string,
                                             (Qt.QtCore.Qt.MatchContains | Qt.QtCore.Qt.MatchRecursive | Qt.QtCore.Qt.MatchCaseSensitive))
            for item in matched_items:
                _unhide_parent(item)
        else:
            # unfortunately an empty string returns a match for all items
            # in this case we will show all items again
            iterator = Qt.QtWidgets.QTreeWidgetItemIterator(self.tree_widget, Qt.QtWidgets.QTreeWidgetItemIterator.All)
            while iterator.value():
                iterator.value().setHidden(False)
                iterator += 1


class SearchField(ContextWidget):
    """ simple SearchField Widget we will use in the nodegraph

    """
    signal_input_accepted = Qt.QtCore.Signal(str)

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
        completer = Qt.QtWidgets.QCompleter(self.available_items)
        completer.setCompletionMode(Qt.QtWidgets.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(Qt.QtCore.Qt.CaseInsensitive)
        line_edit_widget.setCompleter(completer)

    def setup_ui(self):
        """ extends the setup ui method

        This should create the base widgets and connect signals
        """
        super(SearchField, self).setup_ui()
        # set search field
        self.mask = Qt.QtWidgets.QLineEdit(self)
        self.context = self.mask
        self.mask.setFocus()

        self.mask.returnPressed.connect(self.on_accept)

    def on_accept(self):
        """ sends signal if input is one of the available items

        Returns:

        """
        search_input = str(self.mask.text())
        if search_input in self.available_items:
            self.signal_input_accepted.emit(search_input)
            self.close()

    def on_available_items_changed(self):
        """ actions that should run if items have changed

        Returns:

        """
        self._setup_completer(self.mask)


class BackdropItem(Qt.QtWidgets.QGraphicsRectItem):

    def __init__(self, *args, **kwargs):
        super(BackdropItem, self).__init(*args, **kwargs)

        raise NotImplementedError


class Menu(Qt.QtWidgets.QMenu):

    MENU_NAME = "CocoNodz"

    def __init__(self, menu_bar):
        super(Menu, self).__init__()

        self.menu_bar = menu_bar
        self.setTitle(self.MENU_NAME)

    def init(self):
        self.menu_bar.addMenu(self)

    def add_action(self, title, icon=None):
        if icon:
            raise NotImplementedError

        return self.addAction(title)


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
        LOG.warning("Loading base configuration from {0}".format(configuration_file))
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
        return filepath


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


def reload_modules(namespace):
    """

    Args:
        namespace:

    Returns:

    """
    modules = [sys.modules[_module] for _module in sys.modules if _module.startswith(namespace) if sys.modules[_module]]
    for module in modules:
        reload(module)
        LOG.info("Reloaded module '{0}'".format(module))