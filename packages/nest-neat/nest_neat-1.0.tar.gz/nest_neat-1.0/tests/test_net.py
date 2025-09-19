# -*- coding: utf-8 -*-
#
# test_net.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

import matplotlib.pyplot as pl
import numpy as np
import pytest

from neat import Kernel, NETNode, NET


class TestNET:
    def load_tree(self, reinitialize=0):
        if not hasattr(self, "net") or reinitialize:
            alphas = np.array([1.0])
            gammas = np.array([1.0])
            # define nodes
            node_r = NETNode(0, [0, 1, 2, 3, 4, 5], [], z_kernel=(alphas, gammas))
            node_s = NETNode(1, [0], [0], z_kernel=(alphas, gammas))
            node_b1 = NETNode(2, [1, 2, 3, 4, 5], [1], z_kernel=(alphas, gammas))
            node_b2 = NETNode(3, [2, 3, 4], [2], z_kernel=(alphas, gammas))
            node_l3 = NETNode(4, [3], [3], z_kernel=(alphas, gammas))
            node_l4 = NETNode(5, [4], [4], z_kernel=(alphas, gammas))
            node_l5 = NETNode(6, [5], [5], z_kernel=(alphas, gammas))
            # add nodes to tree
            self.net = NET()
            self.net.set_root(node_r)
            self.net.add_node_with_parent(node_s, node_r)
            self.net.add_node_with_parent(node_b1, node_r)
            self.net.add_node_with_parent(node_b2, node_b1)
            self.net.add_node_with_parent(node_l3, node_b2)
            self.net.add_node_with_parent(node_l4, node_b2)
            self.net.add_node_with_parent(node_l5, node_b1)

    def test_string_representation(self):
        self.load_tree()

        assert (
            str(self.net) == f">>> NET\n"
            f"    NETNode 0, Parent: None ---  loc inds: [0, 1, 2, 3, 4, 5], newloc inds: [], z_bar = 1.0 MOhm\n"
            f"    NETNode 1, Parent: 0 ---  loc inds: [0], newloc inds: [0], z_bar = 1.0 MOhm\n"
            f"    NETNode 2, Parent: 0 ---  loc inds: [1, 2, 3, 4, 5], newloc inds: [1], z_bar = 1.0 MOhm\n"
            f"    NETNode 3, Parent: 2 ---  loc inds: [2, 3, 4], newloc inds: [2], z_bar = 1.0 MOhm\n"
            f"    NETNode 4, Parent: 3 ---  loc inds: [3], newloc inds: [3], z_bar = 1.0 MOhm\n"
            f"    NETNode 5, Parent: 3 ---  loc inds: [4], newloc inds: [4], z_bar = 1.0 MOhm\n"
            f"    NETNode 6, Parent: 2 ---  loc inds: [5], newloc inds: [5], z_bar = 1.0 MOhm"
        )

    def test_node_functionalities(self):
        self.load_tree()
        node_r = self.net.root
        node_b = self.net[3]
        node_l = self.net[5]
        # test contains
        assert 1 in node_r
        assert 1 not in node_b and 2 in node_b
        assert 1 not in node_l and 4 in node_l

    def test_kernels(self):
        # kernel 1
        a1 = np.array([1.0, 10.0])
        c1 = np.array([2.0, 20.0])
        k1 = Kernel((a1, c1))
        # kernel 2
        a2 = np.array([1.0, 10.0])
        c2 = np.array([4.0, 40.0])
        k2 = Kernel({"a": a2, "c": c2})
        # kernel 3
        k3 = Kernel(1.0)
        # kbar
        assert np.abs(k1.k_bar - 4.0) < 1e-12
        assert np.abs(k2.k_bar - 8.0) < 1e-12
        assert np.abs(k3.k_bar - 1.0) < 1e-12
        # temporal kernel
        t_arr = np.array([0.0, np.inf])
        assert np.allclose(k1(t_arr), np.array([22.0, 0.0]))
        assert np.allclose(k2(t_arr), np.array([44.0, 0.0]))
        assert np.allclose(k3(t_arr), np.array([1.0, 0.0]))
        # frequency kernel
        s_arr = np.array([0.0 * 1j, np.inf * 1j])
        assert np.allclose(
            k1.ft(s_arr), np.array([4.0 + 0j, np.nan * 1j]), equal_nan=True
        )
        assert np.allclose(
            k2.ft(s_arr), np.array([8.0 + 0j, np.nan * 1j]), equal_nan=True
        )
        assert np.allclose(
            k3.ft(s_arr), np.array([1.0 + 0j, np.nan * 1j]), equal_nan=True
        )
        # test addition
        k4 = k1 + k2
        assert np.abs(k4.k_bar - 12.0) < 1e-12
        assert len(k4.a) == 2
        k5 = k1 + k3
        assert np.abs(k5.k_bar - 5.0) < 1e-12
        assert len(k5.a) == 3
        # test subtraction
        k6 = k2 - k1
        assert len(k6.a) == 2
        assert np.allclose(k6.c, np.array([2.0, 20]))
        assert np.abs(k6.k_bar - 4.0) < 1e-12
        k7 = k1 - k3
        assert len(k7.a) == 3
        assert np.allclose(k7.c, np.array([2.0, 20.0, -1.0]))
        assert np.abs(k7.k_bar - 3.0) < 1e-12

    def test_basic(self):
        self.load_tree()
        net = self.net
        assert net.get_loc_idxs() == [0, 1, 2, 3, 4, 5]
        assert net.get_loc_idxs(3) == [2, 3, 4]
        assert net.get_leaf_loc_node(0).index == 1
        assert net.get_leaf_loc_node(1).index == 2
        assert net.get_leaf_loc_node(2).index == 3
        assert net.get_leaf_loc_node(3).index == 4
        assert net.get_leaf_loc_node(4).index == 5
        assert net.get_leaf_loc_node(5).index == 6
        # create reduced net
        net_reduced = net.get_reduced_tree([4, 5])
        node_r = net_reduced[0]
        node_4 = net_reduced.get_leaf_loc_node(4)
        node_5 = net_reduced.get_leaf_loc_node(5)
        assert node_r.z_bar == (net[0].z_kernel + net[2].z_kernel).k_bar
        assert node_4.z_bar == (net[3].z_kernel + net[5].z_kernel).k_bar
        assert node_5.z_bar == net[6].z_bar
        # test Iz
        Izs = net.calc_i_z([1, 3, 5])
        assert np.abs(Izs[(1, 3)] - 0.5) < 1e-12
        assert np.abs(Izs[(1, 5)] - 0.25) < 1e-12
        assert np.abs(Izs[(3, 5)] - 0.75) < 1e-12
        with pytest.raises(KeyError):
            Izs[(5, 3)]
        assert isinstance(net.calc_i_z([4, 5]), float)
        # test impedance matrix calculation
        z_mat_control = np.array([[4.0, 2.0], [2.0, 3.0]])
        assert np.allclose(net_reduced.calc_impedance_matrix(), z_mat_control)

    def test_compartmentalization(self):
        self.load_tree()
        net = self.net
        comps = net.calc_compartmentalization(Iz=0.1)
        assert comps == [[1], [4], [5], [6]]
        comps = net.calc_compartmentalization(Iz=0.5)
        assert comps == [[1], [2]]
        comps = net.calc_compartmentalization(Iz=1.0)
        assert comps == [[3]]
        comps = net.calc_compartmentalization(Iz=3.0)
        assert comps == []
        comps = net.calc_compartmentalization(Iz=5.0)
        assert comps == []

    def test_plotting(self, pshow=0):
        self.load_tree()
        pl.figure("dendrograms")
        ax = pl.subplot(221)
        self.net.plot_dendrogram(ax)
        ax = pl.subplot(222)
        self.net.plot_dendrogram(
            ax,
            plotargs={"lw": 2.0, "color": "DarkGrey"},
            labelargs={"marker": "o", "ms": 6.0, "c": "r"},
            textargs={"size": "small"},
        )
        ax = pl.subplot(223)
        self.net.plot_dendrogram(
            ax,
            plotargs={"lw": 2.0, "color": "DarkGrey"},
            labelargs={
                -1: {"marker": "o", "ms": 6.0, "c": "r"},
                2: {"marker": "o", "ms": 10.0, "c": "y"},
            },
            textargs={"size": "small"},
        )
        ax = pl.subplot(224)
        self.net.plot_dendrogram(
            ax,
            plotargs={"lw": 2.0, "color": "DarkGrey"},
            labelargs={
                -1: {"marker": "o", "ms": 6.0, "c": "r"},
                2: {"marker": "o", "ms": 10.0, "c": "y"},
            },
            textargs={"size": "xx-small"},
            nodelabels=None,
            cs_comp={1: 0.05, 4: 0.35, 5: 0.75, 6: 0.95},
        )
        if pshow:
            pl.show()


if __name__ == "__main__":
    tnet = TestNET()
    tnet.test_string_representation()
    # tnet.test_node_functionalities()
    # tnet.test_kernels()
    # tnet.test_basic()
    # tnet.test_compartmentalization()
    # tnet.test_plotting(pshow=1)
