import os
import tempfile
import time
import unittest
from unittest.case import safe_repr

import coconodz
from coconodz import Nodzgraph, application
from coconodz.lib import (DictDotLookup,
                          read_json
                          )


class TestCase(unittest.TestCase):
    """ extending unittests.TestCase class

    """
    def assertHasAttribute(self, obj, name, msg=None):
        """Fail if the two objects are equal as determined by the '=='
           operator.
        """
        if hasattr(obj, name) == False:
            msg = self._formatMessage(msg, '%s has no attribute named %s' % (safe_repr(obj),
                                                                             safe_repr(name)
                                                                             )
                                      )
            raise self.failureException(msg)


class ConfigurationCase(TestCase):
    """ test the configuration

    """

    def test_has_configuration(self):
        self.assertHasAttribute(Nodzgraph, "configuration")

    def test_is_expected_instance(self):
        self.assertIsInstance(Nodzgraph.configuration, DictDotLookup)

    def test_parent_presets(self):
        self.assertHasAttribute(Nodzgraph.configuration, "output_verbosity")
        self.assertHasAttribute(Nodzgraph.configuration, "scene_width")
        self.assertHasAttribute(Nodzgraph.configuration, "scene_height")
        self.assertHasAttribute(Nodzgraph.configuration, "grid_size")
        self.assertHasAttribute(Nodzgraph.configuration, "antialiasing")
        self.assertHasAttribute(Nodzgraph.configuration, "antialiasing_boost")
        self.assertHasAttribute(Nodzgraph.configuration, "smooth_pixmap")
        self.assertHasAttribute(Nodzgraph.configuration, "attribute_order")
        self.assertHasAttribute(Nodzgraph.configuration, "available_node_types")
        self.assertHasAttribute(Nodzgraph.configuration, "default_attribute_name")
        self.assertHasAttribute(Nodzgraph.configuration, "default_attribute_data_type")
        self.assertHasAttribute(Nodzgraph.configuration, "default_socket")
        self.assertHasAttribute(Nodzgraph.configuration, "default_plug")
        self.assertHasAttribute(Nodzgraph.configuration, "node_font")
        self.assertHasAttribute(Nodzgraph.configuration, "node_font_size")
        self.assertHasAttribute(Nodzgraph.configuration, "attr_font")
        self.assertHasAttribute(Nodzgraph.configuration, "attr_font_size")
        self.assertHasAttribute(Nodzgraph.configuration, "mouse_bounding_box")
        self.assertHasAttribute(Nodzgraph.configuration, "node_width")
        self.assertHasAttribute(Nodzgraph.configuration, "node_height")
        self.assertHasAttribute(Nodzgraph.configuration, "node_radius")
        self.assertHasAttribute(Nodzgraph.configuration, "node_border")
        self.assertHasAttribute(Nodzgraph.configuration, "node_attr_height")
        self.assertHasAttribute(Nodzgraph.configuration, "connection_width")
        self.assertHasAttribute(Nodzgraph.configuration, "alternate_value")
        self.assertHasAttribute(Nodzgraph.configuration, "grid_color")
        self.assertHasAttribute(Nodzgraph.configuration, "slot_border")
        self.assertHasAttribute(Nodzgraph.configuration, "non_connectable_color")
        self.assertHasAttribute(Nodzgraph.configuration, "connection_inherit_datatype_color")
        self.assertHasAttribute(Nodzgraph.configuration, "connection_color")
        self.assertHasAttribute(Nodzgraph.configuration, "node_default")
        self.assertHasAttribute(Nodzgraph.configuration, "attr_default")
        self.assertHasAttribute(Nodzgraph.configuration, "datatype_default")

    def test_load_configuration(self):
        old_width = Nodzgraph.configuration.scene_width
        new_width = old_width + 100
        Nodzgraph.configuration.scene_width = new_width
        self.assertEqual(new_width, Nodzgraph.configuration.scene_width)

        Nodzgraph.load_configuration(os.path.join(os.path.dirname(coconodz.__file__), "nodegraph.config"))
        self.assertEqual(Nodzgraph.configuration.scene_width, old_width)

    def test_save_configuration(self):
        tmp_dir = tempfile.gettempdir()
        config_file = Nodzgraph.save_configuration(os.path.join(tmp_dir, str(time.time()) + "_coconodz.config"))
        self.assertTrue(os.path.exists(config_file))
        try:
            os.remove(config_file)
        except OSError:
            raise


class NodegraphCase(TestCase):
    """ test the nodegraphs functionality

    """

    @classmethod
    def setUpClass(cls):
        _test_data_dir = os.path.join(os.path.dirname(coconodz.__file__), "tests", "nodegraph", "ref")
        cls._test_attrs_data = read_json(os.path.join(_test_data_dir, "attrs.json"))
        cls._test_cons_data = read_json(os.path.join(_test_data_dir, "cons.json"))

    def setUp(self):
        Nodzgraph.clear()

    def test_is_expected_instance(self):
        self.assertIsInstance(Nodzgraph, coconodz.nodegraph.Nodegraph)

    def test_no_nodes(self):
        self.assertListEqual([], Nodzgraph.all_nodes)

    def test_all_nodes(self):
        self.assertListEqual([_create_test_node()], Nodzgraph.all_nodes)

    def test_create_node(self):
        _create_test_node()
        self.assertEqual(int(1), len(Nodzgraph.graph.scene().nodes.keys()))

    def test_selected_nodes(self):
        _node = _create_test_node()
        _node.setSelected(True)
        self.assertListEqual([_node], Nodzgraph.selected_nodes)

    def test_get_node_by_name(self):
        name = "test_name"
        self.assertEqual(_create_test_node(name=name), Nodzgraph.get_node_by_name(name))
        name = "another_test_name"
        self.assertEqual(_create_test_node(name=name), Nodzgraph.get_node_by_name(name))

    def test_creation_field_input_accepted(self):
        self.assertIsInstance(Nodzgraph.creation_field.available_items, list)
        node_type = "some_node_type"
        Nodzgraph.graph.creation_field.available_items = [node_type]
        Nodzgraph.creation_field.signal_input_accepted.emit(node_type)
        self.assertEqual(node_type, Nodzgraph.all_nodes[0].node_type)

    def test_search_field_available_items(self):
        self.assertIsInstance(Nodzgraph.search_field.available_items, list)
        name = "test_search_field"
        node = _create_test_node(name)

        # mimic search_field open
        Nodzgraph.on_search_field_opened()
        self.assertListEqual([node.name], Nodzgraph.search_field.available_items)

        Nodzgraph.search_field.signal_input_accepted.emit(name)
        self.assertTrue(node.isSelected())

    def test_default_attribute(self):
        name = Nodzgraph.configuration.default_attribute_name
        data_type = Nodzgraph.configuration.default_attribute_data_type
        node = _create_test_node()
        if Nodzgraph.configuration.default_plug:
            self.assertIn(name, node.plugs)
            self.assertEqual(node.plugs[name].dataType, data_type)
        if Nodzgraph.configuration.default_socket:
            self.assertIn(name, node.sockets)
            self.assertEqual(node.sockets[name].dataType, data_type)

    def test_create_attributes(self):
        node_setup = _create_nodes_setup()
        x = Nodzgraph.all_node_names
        # create the attributes
        Nodzgraph._create_attributes(self._test_attrs_data)
        # compare created attributes with the expected from _test_attrs_data
        # only considering nodes in node_to_create
        for attr, attr_data in self._test_attrs_data.iteritems():
            node_name = attr.split(".")[0]
            attr_name = attr.split(".")[1]
            if node_name in node_setup:
                self.assertIn(node_name, Nodzgraph.nodes_dict)
                node = Nodzgraph.get_node_by_name(node_name)
                if attr_data["type"] == ("plug" or "slot"):
                    self.assertIn(attr_name, node.plugs)
                    self.assertEqual(node.plugs[attr_name].dataType,  attr_data["data_type"])
                if attr_data["type"] == ("socket" or "slot"):
                    self.assertIn(attr_name, node.sockets)
                    self.assertEqual(node.sockets[attr_name].dataType, attr_data["data_type"])

    def test_create_connections(self):
        node_setup = _create_nodes_setup()
        Nodzgraph._create_attributes(self._test_attrs_data)
        Nodzgraph._create_connections(self._test_cons_data)

        expected_connections = [(x, y) for x, y in self._test_cons_data.iteritems()
                                if (x.split(".")[0] in node_setup and y.split(".")[0] in node_setup)]

        self.assertListEqual(sorted(expected_connections), sorted(Nodzgraph.graph.evaluateGraph()))

    #@unittest.SkipTest
    def test_display_host_nodes(self):
        """ visual testing

        Returns:

        """
        Nodzgraph.display_host_nodes(_nodes_setup(),
                                     self._test_attrs_data,
                                     self._test_cons_data)

        Nodzgraph.open()
        application.exec_()


def _create_test_node(name="some", node_type="some"):
    return Nodzgraph.graph.create_node(name=name, node_type=node_type)


def _nodes_setup():
    node_types = ["lambert", "blinn", "surfaceShader", "shadingEngine", "file", "place2dTexture"]
    # hardcoded attributes testing
    # have to exist within the _test_attrs_data
    return {"lambert1": node_types[0],
            "lambert2": node_types[0],
            "blinn1": node_types[1],
            "surfaceShader1": node_types[2],
            "surfaceShader1SG": node_types[3],
            "file1": node_types[4],
            "lambert2SG": node_types[3],
            "blinn1SG": node_types[3],
            "place2dTexture1": node_types[4]
            }


def _create_nodes_setup():
    _setup = _nodes_setup()
    # define possible (and for attr creation expected nodetypes)
    Nodzgraph.creation_field.available_items = list(set(_nodes_setup().keys()))

    for key, value in _setup.iteritems():
        Nodzgraph.graph.create_node(key, node_type=value)

    return _setup