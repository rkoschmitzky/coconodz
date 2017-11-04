import json
import logging
import os
import pprint
import sys

from coconodz import (Qt,
                      application
                     )


LOG = logging.getLogger(name="CocoNodz.nodegraph")


class Singleton(object):
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance


class SafeOpen(object):
    """ safer handler to open files

    """
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
    PALETTE_PATH = os.path.join(os.path.dirname(__file__), "palette.config")

    def __init__(self, parent):
        super(BaseWindow, self).__init__(parent)

        # apply the color palette
        set_application_palette(self.PALETTE_PATH, application)

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
    """ global context widget

    The context widget is the main class and it should be accessed in the nodegraph
    when pressing a mousebutton or key.

    For the moment we will use the QMenu for that, but the long running goal is to
    have a proper hotbox widget we can mixin or inherit from
    """
    signal_available_items_changed = Qt.QtCore.Signal()
    signal_opened = Qt.QtCore.Signal()

    def __init__(self, parent):
        super(ContextWidget, self).__init__(parent)

        self._items = None
        self._context = None
        self._expect_msg = "Expected type {0}, got {1} instead"

    @property
    def available_items(self):
        """ available items dictionary

        This will dependent on the subclass and can be anything like QActions, QButtons, list.
        We choose as dictionary as base, because it will be the most flexible approach

        Returns: dict

        """
        return self._items

    @available_items.setter
    def available_items(self, items_dict):
        self._items = items_dict
        self.signal_available_items_changed.emit()

    @property
    def context(self):
        """ holds the "real" context widget

        Returns: QWidget instance

        """
        return self._context

    @context.setter
    def context(self, context_widget):
        """ sets the "real" context widget

        Args:
            context_widget: QWidget instance

        Returns:

        """
        self._context = context_widget
        self._update_context()

    def _update_context(self):
        """ clears the underlying menu and replaces the default widget with set context

        Returns:

        """
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
        """ sets up the context and connects all signals

        Returns:

        """
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
        """ should rebuild the context when available items changed

        Returns:

        """
        self.setup_ui()

    def on_tree_double_clicked(self, index):
        """ defines whar will happen when the tree was double-clicked

        Args:
            index:

        Returns:

        """
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
    """ simple SearchField Widget we will use so search for nodes in the nodegraph

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


class RenameField(ContextWidget):
    """ simeple RenameField widget we will use in Nodegraph

    """
    signal_input_accepted = Qt.QtCore.Signal(str)

    VALIDATION_REGEX = "[A-Za-z0-9_]+"

    def __init__(self, parent):
        super(RenameField, self).__init__(parent)

        self._items = []
        self._validation_regex = self.VALIDATION_REGEX
        self.setup_ui()

    @property
    def validation_regex(self):
        """ holds the current regular expression pattern

        Returns:

        """
        return self._validation_regex

    @validation_regex.setter
    def validation_regex(self, regex_str):
        """ sets the validation regex that will be used in the mask

        Args:
            regex_str: string that holds the regular expression pattern

        Returns:

        """
        assert isinstance(regex_str, basestring)

        self._validation_regex = regex_str
        self.setup_ui()

    def setup_ui(self):
        """ create base widgets and connection internal signals

        Returns:

        """
        self.mask = Qt.QtWidgets.QLineEdit(self)
        self.mask.setValidator( Qt.QtGui.QRegExpValidator(Qt.QtCore.QRegExp(self.validation_regex)))
        self.context = self.mask
        self.mask.setFocus()

        self.mask.returnPressed.connect(self.on_accept)

    def on_accept(self):
        """ sends signal if input is accepted

        Returns:

        """
        rename_input = str(self.mask.text())
        self.signal_input_accepted.emit(rename_input)
        self.close()


class BackdropItem(Qt.QtWidgets.QGraphicsRectItem):
    """ Rectangle Item that visually groups nodes insides its bounds

    """

    def __init__(self, name, bounds=(0, 0, 200, 200), color=(255, 0, 0, 50), border_color=(255, 255, 255, 50), description=""):
        """

        Args:
            name: name of the backdrop that will be displayed as title
            bounds: tuple including x,y of the topleft corner width and height
            color: tuple including RGBA as integers from 0-255
            border_color: tuple including RGBA as integers from 0-255
        """
        super(BackdropItem, self).__init__(*bounds)

        self.name = name
        self._title_font_size = 12
        self._description_font_size = 10
        self._handle_size = 20
        self._minimum_width = 100
        self._resize_space = 25
        self._title_space = 5
        self._selection = []

        self._handle_in_use = False

        # flags
        self.setAcceptHoverEvents(True)
        self.setFlag(Qt.QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(Qt.QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(Qt.QtWidgets.QGraphicsItem.ItemIsFocusable, True)

        # style
        self._bg_color = Qt.QtGui.QColor(*color)
        self._border_color = Qt.QtGui.QColor(*border_color)
        self._bounds = list(bounds)

        self._bg_brush = Qt.QtGui.QBrush(self._bg_color, Qt.QtCore.Qt.SolidPattern)
        self._bg_pen = Qt.QtGui.QPen(Qt.QtCore.Qt.SolidLine)
        self._bg_pen.setJoinStyle(Qt.QtCore.Qt.RoundJoin)
        self._bg_pen.setWidth(1)
        self._bg_pen.setColor(self._border_color)

        self._bg_pen_selected = self._bg_pen
        self._bg_pen_selected.setWidth(2)

        self._handle_brush = Qt.QtGui.QBrush(self._bg_color, Qt.QtCore.Qt.BDiagPattern)
        # todo switch font size and type to config
        self._title_font = Qt.QtGui.QFont("Arial", self.title_font_size)
        self._title_font.setBold(True)

        self._description_font = Qt.QtGui.QFont("Arial", self.description_font_size)

        self.background = None
        self.title_bar = None
        self.title = None
        self.handle = None

        self.setup_ui()

        self.description_text = description

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def description_text(self):
        return self._description_text

    @description_text.setter
    def description_text(self, text):

        self._adjust_description(text)
        self._description_text = text

    @property
    def title_font_size(self):
        return self._title_font_size

    @title_font_size.setter
    def title_font_size(self, size):
        assert isinstance(size, int)

        self._title_font_size = size
        self._title_font.setPointSize(size)
        self.title.setFont(self._title_font)
        self.adjust_to_minimum_height()

    @property
    def description_font_size(self):
        return self._description_font_size

    @description_font_size.setter
    def description_font_size(self, size):
        assert isinstance(size, int)

        self._description_font_size = size
        self._description_font.setPointSize(size)
        self.description.setFont(self._description_font)
        self._adjust_description(self.description_text)

    @property
    def minimum_height(self):
        return self.description.boundingRect().height() +\
               self.title.boundingRect().height() +\
               self._title_space +\
               self._resize_space

    def setup_ui(self):
        """ creates the items and applies styles

        Returns:

        """
        self.setBrush(self._bg_brush)
        self.setPen(self._bg_pen)

        self.title_bar = Qt.QtWidgets.QGraphicsRectItem(self._bounds[0],
                                                        self._bounds[1],
                                                        self._bounds[2],
                                                        20,  # initial start value, will be overwritten later
                                                        parent=self)
        self.title_bar.setBrush(self._bg_brush)
        self.title_bar.setPen(self._bg_pen)

        self.title = Qt.QtWidgets.QGraphicsTextItem(self.name, parent=self.title_bar)
        self.title.setFont(self._title_font)
        self.title.setTextWidth(self._bounds[2])

        self.title.setX(self._bounds[0])
        self.title.setY(self._bounds[1] - 5)

        self.title_bar.setRect(self._bounds[0],
                               self._bounds[1],
                               self._bounds[2],
                               self.title.boundingRect().height())

        self.description = Qt.QtWidgets.QGraphicsTextItem(parent=self)
        self.description.setFont(self._description_font)
        self.description.setTextWidth(self._bounds[2])
        self.description.setX(self._bounds[0])
        self.description.setY(self._bounds[1] + self.title.boundingRect().height() + self._title_space)

        self.handle = Qt.QtWidgets.QGraphicsRectItem(self._bounds[0] + self._bounds[2] - self._handle_size,
                                                     self._bounds[1] + self._bounds[3] - self._handle_size,
                                                     self._handle_size,
                                                     self._handle_size,
                                                     parent=self)
        self.handle.setBrush(self._handle_brush)
        self.handle.setPen(self._bg_pen)

    def _adjust_description(self, text):
        """ adjusts the description text

        Handles the backdrop resizing if required
        Args:
            text: description text string

        Returns:

        """
        self.description.setPlainText(text)

        # resize backdrop if required
        if self.minimum_height >= self._bounds[3]:
            self.adjust_to_minimum_height()

    def get_contained_items(self):
        """ get all node taht

        Returns:

        """
        return self.scene().items(self.mapToScene(self.boundingRect()), mode=Qt.QtCore.Qt.IntersectsItemShape)

    def select_contained_items(self):
        """ we have to patch this later in the nodegraph class

        Returns:

        """
        items = self.get_contained_items()
        for item in items:
            item.setSelected(True)

    def _revert_selection(self):
        """ restores previous stored selection

        Returns:

        """
        for item in self.scene().items():
            item.setSelected(False)
        if self._selection:
            for node in self._selection:
                node.setSelected(True)
            self._selection = None

    def _store_selection(self):
        self._selection = [item for item in self.scene().items() if item.isSelected()]

    def _remove(self):
        """ _remove() gets called via Nodz, so we have to implement it here

        Returns:

        """
        scene = self.scene()
        scene.removeItem(self)
        scene.update()

    def get_items_in_bounds(self):
        raise NotImplementedError

    def _underlying_handle(self, point):
        """ checks if there is a handle under point

        Args:
            point: QPointF

        Returns: QGraphicRectItem instance

        """
        if self.handle.contains(point):
            return self.handle

    def _perform_resize(self, width_height):
        """ backdrop resize

        Args:
            width_height: QPointF

        Returns:

        """
        # and text sizes too
        self.title.setTextWidth(self._bounds[2])
        self.description.setTextWidth(self._bounds[2])

        if (width_height.x() > self._minimum_width) and \
           (width_height.y() - self._bounds[1] > self.description.boundingRect().height() + self.title.boundingRect().height() + self._resize_space):
            # x and y are always 0
            # we only have to consider width and height
            self._bounds[2] = width_height.x() - self._bounds[0]
            self._bounds[3] = width_height.y() - self._bounds[1]

            self.set_size(self._bounds[2], self._bounds[3])

    def set_size(self, width, height):
        """ adjusts width and height of item and all child nodes

        Args:
            width:
            height:

        Returns:

        """
        self.setRect(self._bounds[0], self._bounds[1], width, height)
        self.title_bar.setRect(self._bounds[0],
                               self._bounds[1],
                               width,
                               self.title.boundingRect().height())
        self.handle.setRect(self._bounds[0] + width - self._handle_size,
                            self._bounds[1] + height - self._handle_size,
                            self._handle_size,
                            self._handle_size)
        self._bounds[2] = width
        self._bounds[3] = height

        self.description.setY(self._bounds[1] + self.title.boundingRect().height() + self._title_space)

    def adjust_to_minimum_height(self):
        """ calculates minimum height and adjust height of the item

        This has to be called if the description text, title and their sizes will be changed
        Returns:

        """
        self.set_size(self._bounds[2], self.minimum_height)

    def mousePressEvent(self, event):
        """ initializes the backdrop resize procedure

        Args:
            event:

        Returns:

        """
        selected_handle = self._underlying_handle(event.pos())
        if selected_handle:
            self._handle_in_use = True
        else:
            self._store_selection()
            self.select_contained_items()
        super(BackdropItem, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """ end backdrop resize procedure

        Args:
            event:

        Returns:

        """
        # define status
        self._handle_in_use = False
        self._revert_selection()
        super(BackdropItem, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """ move backdrop or perform resize

        Args:
            event:

        Returns:

        """
        if self._handle_in_use:
            self._perform_resize(event.pos())
        else:
            self.setCursor(Qt.QtCore.Qt.ArrowCursor)
            super(BackdropItem, self).mouseMoveEvent(event)

        self.scene().updateScene()

    def hoverMoveEvent(self, event):
        """ if we hover over the handle change the cursor shape

        Args:
            event:

        Returns:

        """
        handle = self._underlying_handle(event.pos())
        if handle:
            self.setCursor(Qt.QtCore.Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.QtCore.Qt.ArrowCursor)
        super(BackdropItem, self).hoverEnterEvent(event)


class DotItem(Qt.QtWidgets.QGraphicsEllipseItem):

    def __init__(self, *args, **kwargs):
        super(DotItem, self).__init(*args, **kwargs)


class Menu(Qt.QtWidgets.QMenu):
    """ the main CocoNodz menu we will provide for each application integration

    """
    MENU_NAME = "CocoNodz"

    def __init__(self, menu_bar):
        super(Menu, self).__init__()

        self.menu_bar = menu_bar
        self.setTitle(self.MENU_NAME)

    def init(self):
        self.menu_bar.addMenu(self)

    def add_action(self, title, iconpath=None):

        assert os.path.exists(iconpath), "Icon path {} does not exist.".format(iconpath)

        action = self.addAction(title)
        if iconpath:
            action.setIcon(Qt.QtGui.QIcon(iconpath))

        return action


class ConfiguationMixin(object):
    """ configuration class that makes dict/json type data accessable through dot lookups

    """
    BASE_CONFIG_NAME = "nodegraph.config"
    BASE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), BASE_CONFIG_NAME)

    def __init__(self, *args, **kwargs):
        super(ConfiguationMixin, self).__init__(*args, **kwargs)

        config = os.environ.get("COCONODZ_CONFIG_PATH", 0)
        self.__base_configuration_file = self.BASE_CONFIG_PATH

        if config and not os.path.exists(config):
            LOG.error("Configuration path {0} doesn't exist. Loading default configuration.".format(config))
        elif config and os.path.exists(config):
            try:
                self.load_configuration(config)
                self.__base_configuration_file = config
            except:
                LOG.error("Confguration file {} not readable.Loading default configuration.".format(config),
                          exc_info=True)

        self.__data = None

    @property
    def configuration_file(self):
        """ holds the file the configuration is based on

        Returns:

        """
        return self.__base_configuration_file

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

    def initialize_configuration(self, *args):
        """ loads the predefined default configuration file and converts it to our proper configuration object

        Returns:

        """
        self.load_configuration(self.__base_configuration_file)

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


def set_application_palette(palette_filepath, application):
    """ applies color palette to application

    Args:
        palette_filepath: serialized color palette
        application: QApplication instance

    Returns:

    """
    if application:
        try:
            palette_dict = read_json(palette_filepath)
        except:
            LOG.error("Palette file '{}' not readable".format(palette_filepath))

        groups = ['Disabled',
                  'Active',
                  'Inactive',
                  'Normal']
        roles = ['Window',
                 'Background',
                 'WindowText',
                 'Foreground',
                 'Base',
                 'AlternateBase',
                 'ToolTipBase',
                 'ToolTipText',
                 'Text',
                 'Button',
                 'ButtonText',
                 'BrightText']

        palette = Qt.QtGui.QPalette()
        for role in roles:
            for group in groups:
                group_color = Qt.QtGui.QColor(palette_dict['{0}:{1}'.format(role, group)])
                group_group = getattr(Qt.QtGui.QPalette, group)
                group_role = getattr(Qt.QtGui.QPalette, role)
                palette.setColor(group_group, group_role, group_color)
        # we have to set the style to plastic otherwise
        # the palette will not applied to QMenus propery
        application.setStyle("plastique")
        application.setPalette(palette)
    else:
        LOG.info("Not running standalone. Inherit application palette")
