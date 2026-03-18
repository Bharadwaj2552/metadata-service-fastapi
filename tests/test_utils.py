"""Unit tests for graph utilities"""

import pytest
from app.utils import has_cycle, get_upstream_datasets, build_lineage_graphs


class TestCycleDetection:
    """Test cycle detection in lineage graphs"""

    def test_has_cycle_simple_cycle(self):
        """Test detection of simple 2-node cycle"""
        graph = {1: [2], 2: [1]}
        assert has_cycle(graph, 1, 2) is True

    def test_has_cycle_chain_no_cycle(self):
        """Test chain without cycle"""
        graph = {1: [2], 2: [3], 3: [4]}
        assert has_cycle(graph, 4, 1) is False

    def test_has_cycle_potential_cycle(self):
        """Test potential cycle A->B->C, trying to add C->A"""
        graph = {1: [2], 2: [3]}
        assert has_cycle(graph, 3, 1) is True

    def test_has_cycle_no_path(self):
        """Test when no path exists"""
        graph = {1: [2], 3: [4]}
        assert has_cycle(graph, 4, 2) is False

    def test_has_cycle_empty_graph(self):
        """Test empty graph"""
        graph = {}
        assert has_cycle(graph, 1, 2) is False

    def test_has_cycle_self_loop(self):
        """Test self-loop detection"""
        graph = {}
        assert has_cycle(graph, 1, 1) is True


class TestLineageGraphBuilding:
    """Test building lineage graphs"""

    def test_build_lineage_graphs_simple(self):
        """Test building graphs from simple edges"""
        edges = [(1, 2), (2, 3)]
        forward, reverse = build_lineage_graphs(edges)

        assert forward == {1: [2], 2: [3]}
        assert reverse == {2: [1], 3: [2]}

    def test_build_lineage_graphs_empty(self):
        """Test building graphs from empty edges"""
        edges = []
        forward, reverse = build_lineage_graphs(edges)

        assert forward == {}
        assert reverse == {}

    def test_build_lineage_graphs_complex(self):
        """Test building graphs from complex relationships"""
        edges = [(1, 2), (1, 3), (2, 4), (3, 4)]
        forward, reverse = build_lineage_graphs(edges)

        assert forward[1] == [2, 3]
        assert forward[2] == [4]
        assert forward[3] == [4]
        assert reverse[2] == [1]
        assert reverse[3] == [1]
        assert reverse[4] == [2, 3]


class TestUpstreamDatasets:
    """Test finding upstream datasets"""

    def test_get_upstream_datasets_simple(self):
        """Test getting upstream datasets in simple chain"""
        graph = {1: [2], 2: [3]}
        upstream = get_upstream_datasets(graph, 3)
        assert upstream == {2, 1}

    def test_get_upstream_datasets_no_upstream(self):
        """Test dataset with no upstream"""
        graph = {1: [2]}
        upstream = get_upstream_datasets(graph, 1)
        assert upstream == set()

    def test_get_upstream_datasets_complex(self):
        """Test getting upstream in complex graph"""
        graph = {1: [2], 2: [4], 3: [4]}
        upstream = get_upstream_datasets(graph, 4)
        assert upstream == {1, 2, 3}
