# if __name__ == '__main__':
#     # open Nodzgraph standalone
#     from coconodz import (Nodzgraph,
#                           application
#                           )
#
#     if application:
#
#
#         Nodzgraph.graph.creation_field.available_items = ["lambert", "blinn", "surfaceShader", "shadingEngine"]
#
#
#         Nodzgraph.graph.create_node("lambert1", node_type="lambert")
#         Nodzgraph.graph.create_node("lambert2", node_type="lambert")
#         Nodzgraph.graph.create_node("blinn1", node_type="blinn")
#         Nodzgraph.graph.create_node("surfaceShader1", node_type="surfaceShader")
#         Nodzgraph.graph.create_node("shadingEngine1", node_type="shadingEngine")
#
#         Nodzgraph.open()
#         application.exec_()
#
import os
import tempfile
import time
import unittest
from unittest.case import safe_repr

import coconodz
from coconodz import Nodzgraph
from coconodz.lib import DictDotLookup


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


def _create_test_node(name="some", node_type="some"):
    return Nodzgraph.graph.create_node(name=name, node_type=node_type)