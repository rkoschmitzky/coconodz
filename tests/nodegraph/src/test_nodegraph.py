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
import unittest

import coconodz
from coconodz import Nodzgraph


class NodegraphCase(unittest.TestCase):

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
        _name = "test_name"
        self.assertEqual(_create_test_node(name=_name), Nodzgraph.get_node_by_name(_name))
        _name = "another_test_name"
        self.assertEqual(_create_test_node(name=_name), Nodzgraph.get_node_by_name(_name))

    def test_creation_field_input_accepted(self):
        self.assertIsInstance(Nodzgraph.creation_field.available_items, list)
        _node_type = "some_node_type"
        Nodzgraph.graph.creation_field.available_items = [_node_type]
        Nodzgraph.creation_field.signal_input_accepted.emit(_node_type)
        self.assertEqual(_node_type, Nodzgraph.all_nodes[0].node_type)

    def test_search_field_available_items(self):
        self.assertIsInstance(Nodzgraph.search_field.available_items, list)
        _name = "test_search_field"
        node = _create_test_node()

        # mimic search_field open
        Nodzgraph.on_search_field_opened()
        self.assertListEqual([node.name], Nodzgraph.search_field.available_items)

        Nodzgraph.search_field.signal_input_accepted.emit(_name)
        self.assertTrue(node.isSelected())



def _create_test_node(name="some", node_type="some"):
    return Nodzgraph.graph.create_node(name=name, node_type=node_type)