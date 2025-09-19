# -*- coding: utf-8 -*-
#
# test_greenstree.py
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

import numpy as np
import matplotlib.pyplot as pl

import os
import copy
import itertools

import pytest

from neat import SOVTree, GreensTree, GreensTreeTime, NeuronSimTree, GreensNode, Kernel
import neat.tools.kernelextraction as ke

import channelcollection_for_tests as channelcollection
import channel_installer

channel_installer.load_or_install_neuron_test_channels()

MORPHOLOGIES_PATH_PREFIX = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "test_morphologies")
)


class TestGreensTree:
    def load_T_tree(self):
        """
        Load the T-tree morphology in memory

          6--5--4--7--8
                |
                |
                1
        """
        fname = os.path.join(MORPHOLOGIES_PATH_PREFIX, "Tsovtree.swc")
        self.tree = GreensTree(fname, types=[1, 3, 4])
        self.tree.fit_leak_current(-75.0, 10.0)
        self.tree.set_comp_tree()

    def load_validation_tree(self):
        """
        Load the T-tree morphology in memory

        5---1---4
        """
        fname = os.path.join(MORPHOLOGIES_PATH_PREFIX, "sovvalidationtree.swc")
        self.tree = GreensTree(fname, types=[1, 3, 4])
        self.tree.fit_leak_current(-75.0, 10.0)
        self.tree.set_comp_tree()

    def load_sov_T_tree(self):
        """
        Load the T-tree morphology in memory

          6--5--4--7--8
                |
                |
                1
        """
        fname = os.path.join(MORPHOLOGIES_PATH_PREFIX, "Tsovtree.swc")
        self.sovtree = SOVTree(fname, types=[1, 3, 4])
        self.sovtree.fit_leak_current(-75.0, 10.0)
        self.sovtree.set_comp_tree()
        self.sovtree.calc_sov_equations()

    def load_sov_validation_tree(self):
        """
        Load the T-tree morphology in memory

        5---1---4
        """
        fname = os.path.join(MORPHOLOGIES_PATH_PREFIX, "sovvalidationtree.swc")
        self.sovtree = SOVTree(fname, types=[1, 3, 4])
        self.sovtree.fit_leak_current(-75.0, 10.0)
        self.sovtree.set_comp_tree()
        self.sovtree.calc_sov_equations()

    def test_string_representation(self):
        self.load_T_tree()

        # gmax as potential as float
        e_rev = 100.0
        g_max = 100.0
        channel = channelcollection.test_channel2()
        self.tree.add_channel_current(channel, g_max, e_rev)
        self.tree.set_comp_tree()
        self.tree.set_impedance(np.array([0.0, 100.0]) * 1j)

        with self.tree.as_original_tree:
            print(self.tree)

            print(repr(self.tree))
            str_str = (
                ">>> GreensTree\n"
                "    SomaGreensNode 1, Parent: None --- r_a = 0.0001 MOhm*cm, c_m = 1 uF/cm^2, v_ep = -75 mV, (g_L = 100 uS/cm^2, e_L = -75 mV), (g_test_channel2 = 100 uS/cm^2, e_test_channel2 = 100 mV)\n"
                "    GreensNode 4, Parent: 1 --- r_a = 0.0001 MOhm*cm, c_m = 1 uF/cm^2, v_ep = -75 mV, (g_L = 100 uS/cm^2, e_L = -75 mV), (g_test_channel2 = 100 uS/cm^2, e_test_channel2 = 100 mV)\n"
                "    GreensNode 5, Parent: 4 --- r_a = 0.0001 MOhm*cm, c_m = 1 uF/cm^2, v_ep = -75 mV, (g_L = 100 uS/cm^2, e_L = -75 mV), (g_test_channel2 = 100 uS/cm^2, e_test_channel2 = 100 mV)\n"
                "    GreensNode 6, Parent: 5 --- r_a = 0.0001 MOhm*cm, c_m = 1 uF/cm^2, v_ep = -75 mV, (g_L = 100 uS/cm^2, e_L = -75 mV), (g_test_channel2 = 100 uS/cm^2, e_test_channel2 = 100 mV)\n"
                "    GreensNode 7, Parent: 4 --- r_a = 0.0001 MOhm*cm, c_m = 1 uF/cm^2, v_ep = -75 mV, (g_L = 100 uS/cm^2, e_L = -75 mV), (g_test_channel2 = 100 uS/cm^2, e_test_channel2 = 100 mV)\n"
                "    GreensNode 8, Parent: 7 --- r_a = 0.0001 MOhm*cm, c_m = 1 uF/cm^2, v_ep = -75 mV, (g_L = 100 uS/cm^2, e_L = -75 mV), (g_test_channel2 = 100 uS/cm^2, e_test_channel2 = 100 mV)"
            )
            assert str(self.tree) == str_str

            repr_str = (
                "['GreensTree', "
                "\"{'node index': 1, 'parent index': -1, 'content': '{}', 'xyz': array([0., 0., 0.]), 'R': '10', 'swc_type': 1, 'currents': {'L': '(100, -75)', 'test_channel2': '(100, 100)'}, 'concmechs': {}, 'c_m': '1', 'r_a': '0.0001', 'g_shunt': '0', 'v_ep': '-75', 'conc_eps': {}, 'expansion_points': {}}\", "
                "\"{'node index': 4, 'parent index': 1, 'content': '{}', 'xyz': array([100.,   0.,   0.]), 'R': '1', 'swc_type': 4, 'currents': {'L': '(100, -75)', 'test_channel2': '(100, 100)'}, 'concmechs': {}, 'c_m': '1', 'r_a': '0.0001', 'g_shunt': '0', 'v_ep': '-75', 'conc_eps': {}, 'expansion_points': {}}\", "
                "\"{'node index': 5, 'parent index': 4, 'content': '{}', 'xyz': array([100. ,  50.5,   0. ]), 'R': '1', 'swc_type': 4, 'currents': {'L': '(100, -75)', 'test_channel2': '(100, 100)'}, 'concmechs': {}, 'c_m': '1', 'r_a': '0.0001', 'g_shunt': '0', 'v_ep': '-75', 'conc_eps': {}, 'expansion_points': {}}\", "
                "\"{'node index': 6, 'parent index': 5, 'content': '{}', 'xyz': array([100., 101.,   0.]), 'R': '0.5', 'swc_type': 4, 'currents': {'L': '(100, -75)', 'test_channel2': '(100, 100)'}, 'concmechs': {}, 'c_m': '1', 'r_a': '0.0001', 'g_shunt': '0', 'v_ep': '-75', 'conc_eps': {}, 'expansion_points': {}}\", "
                "\"{'node index': 7, 'parent index': 4, 'content': '{}', 'xyz': array([100. , -49.5,   0. ]), 'R': '1', 'swc_type': 4, 'currents': {'L': '(100, -75)', 'test_channel2': '(100, 100)'}, 'concmechs': {}, 'c_m': '1', 'r_a': '0.0001', 'g_shunt': '0', 'v_ep': '-75', 'conc_eps': {}, 'expansion_points': {}}\", "
                "\"{'node index': 8, 'parent index': 7, 'content': '{}', 'xyz': array([100., -99.,   0.]), 'R': '0.5', 'swc_type': 4, 'currents': {'L': '(100, -75)', 'test_channel2': '(100, 100)'}, 'concmechs': {}, 'c_m': '1', 'r_a': '0.0001', 'g_shunt': '0', 'v_ep': '-75', 'conc_eps': {}, 'expansion_points': {}}\""
                "]{'channel_storage': ['test_channel2'], 'freqs': array([0.  +0.j, 0.+100.j])}"
            )
            assert repr(self.tree) == repr_str

    def test_basic_properties(self):
        self.load_T_tree()
        # test Fourrier impedance matrix
        ft = ke.FourierQuadrature(np.arange(0.0, 100.0, 0.1))
        # set the impedances
        self.tree.set_impedance(ft.s)

        # sets of location
        locs_0 = [(6, 0.5), (8, 0.5)]
        zf = self.tree.calc_zf(*locs_0)
        locs_1 = [(1, 0.5), (4, 0.5), (4, 1.0), (5, 0.5), (6, 0.5), (7, 0.5), (8, 0.5)]
        locs_2 = [(7, 0.5), (8, 0.5)]
        self.tree.store_locs(locs_0, "0")
        self.tree.store_locs(locs_1, "1")
        self.tree.store_locs(locs_2, "2")
        # compute impedance matrices
        z_mat_0 = self.tree.calc_impedance_matrix("0")[ft.ind_0s]
        z_mat_1 = self.tree.calc_impedance_matrix("1")[ft.ind_0s]
        z_mat_2 = self.tree.calc_impedance_matrix("2")[ft.ind_0s]
        # check complex steady state component zero
        assert np.allclose(z_mat_0.imag, np.zeros_like(z_mat_0.imag))
        assert np.allclose(z_mat_1.imag, np.zeros_like(z_mat_1.imag))
        assert np.allclose(z_mat_2.imag, np.zeros_like(z_mat_2.imag))
        # check symmetry
        assert np.allclose(z_mat_0, z_mat_0.T)
        assert np.allclose(z_mat_1, z_mat_1.T)
        assert np.allclose(z_mat_2, z_mat_2.T)
        # check symmetry directly
        assert np.allclose(
            self.tree.calc_zf(locs_0[0], locs_0[1]),
            self.tree.calc_zf(locs_0[1], locs_0[0]),
        )
        assert np.allclose(
            self.tree.calc_zf(locs_1[0], locs_1[3]),
            self.tree.calc_zf(locs_1[3], locs_1[0]),
        )
        assert np.allclose(
            self.tree.calc_zf(locs_1[2], locs_1[5]),
            self.tree.calc_zf(locs_1[5], locs_1[2]),
        )
        # check transitivity
        z_14_ = (
            self.tree.calc_zf(locs_1[1], locs_1[3])
            * self.tree.calc_zf(locs_1[3], locs_1[4])
            / self.tree.calc_zf(locs_1[3], locs_1[3])
        )
        z_14 = self.tree.calc_zf(locs_1[1], locs_1[4])
        assert np.allclose(z_14, z_14_)
        z_06_ = (
            self.tree.calc_zf(locs_1[0], locs_1[5])
            * self.tree.calc_zf(locs_1[5], locs_1[6])
            / self.tree.calc_zf(locs_1[5], locs_1[5])
        )
        z_06 = self.tree.calc_zf(locs_1[0], locs_1[6])
        assert np.allclose(z_06, z_06_)
        z_46_ = (
            self.tree.calc_zf(locs_1[4], locs_1[2])
            * self.tree.calc_zf(locs_1[2], locs_1[6])
            / self.tree.calc_zf(locs_1[2], locs_1[2])
        )
        z_46 = self.tree.calc_zf(locs_1[4], locs_1[6])
        assert np.allclose(z_46, z_46_)
        z_n15_ = (
            self.tree.calc_zf(locs_1[1], locs_1[3])
            * self.tree.calc_zf(locs_1[3], locs_1[5])
            / self.tree.calc_zf(locs_1[3], locs_1[3])
        )
        z_15 = self.tree.calc_zf(locs_1[1], locs_1[5])
        assert not np.allclose(z_15, z_n15_)

    def test_values(self):
        # load trees
        self.load_T_tree()
        self.load_sov_T_tree()
        # test Fourrier impedance matrix
        ft = ke.FourierQuadrature(np.arange(0.0, 100.0, 0.1))
        # set the impedances
        self.tree.set_impedance(ft.s)
        # sets of location
        locs = [(1, 0.5), (4, 0.5), (4, 1.0), (5, 0.5), (6, 0.5), (7, 0.5), (8, 0.5)]
        self.tree.store_locs(locs, "locs")
        self.sovtree.store_locs(locs, "locs")
        # compute impedance matrices with both methods
        z_sov = self.sovtree.calc_impedance_matrix(loc_arg="locs", eps=1e-10)
        z_gf = self.tree.calc_impedance_matrix("locs")[ft.ind_0s].real
        assert np.allclose(z_gf, z_sov, atol=5e-1)
        z_gf2 = self.tree.calc_impedance_matrix("locs", explicit_method=False)[
            ft.ind_0s
        ].real
        assert np.allclose(z_gf2, z_gf, atol=5e-6)
        zf_sov = self.sovtree.calc_impedance_matrix(
            loc_arg="locs", eps=1e-10, freqs=ft.s
        )
        zf_gf = self.tree.calc_impedance_matrix("locs")
        assert np.allclose(zf_gf, zf_sov, atol=5e-1)
        zf_gf2 = self.tree.calc_impedance_matrix("locs", explicit_method=False)
        assert np.allclose(zf_gf2, zf_gf, atol=5e-6)

        # load trees
        self.load_validation_tree()
        self.load_sov_validation_tree()
        # test Fourrier impedance matrix
        ft = ke.FourierQuadrature(np.arange(0.0, 100.0, 0.1))
        # set the impedances
        self.tree.set_impedance(ft.s)
        # set of locations
        locs = [(1, 0.5), (4, 0.5), (4, 1.0), (5, 0.5), (5, 1.0)]
        self.tree.store_locs(locs, "locs")
        self.sovtree.store_locs(locs, "locs")
        # compute impedance matrices with both methods
        z_sov = self.sovtree.calc_impedance_matrix(loc_arg="locs", eps=1e-10)
        z_gf = self.tree.calc_impedance_matrix("locs")[ft.ind_0s].real
        assert np.allclose(z_gf, z_sov, atol=5e-1)
        z_gf2 = self.tree.calc_impedance_matrix("locs", explicit_method=False)[
            ft.ind_0s
        ].real
        assert np.allclose(z_gf2, z_gf, atol=5e-6)
        zf_sov = self.sovtree.calc_impedance_matrix(
            loc_arg="locs", eps=1e-10, freqs=ft.s
        )
        zf_gf = self.tree.calc_impedance_matrix("locs")
        assert np.allclose(zf_gf, zf_sov, atol=5e-1)
        zf_gf2 = self.tree.calc_impedance_matrix("locs", explicit_method=False)
        assert np.allclose(zf_gf2, zf_gf, atol=5e-6)


class TestGreensTreeTime:
    def _init_ft(self):
        self.dt = 0.025
        self.tmax = 100.0
        # for frequency derivation
        self.ft = ke.FourierQuadrature(np.arange(0.0, self.tmax, self.dt))

    def load_T_tree(self):
        """
        Load the T-tree morphology in memory

          6--5--4--7--8
                |
                |
                1
        """
        self._init_ft()
        fname = os.path.join(MORPHOLOGIES_PATH_PREFIX, "Tsovtree.swc")
        self.tree = GreensTreeTime(fname, types=[1, 3, 4])
        self.tree.fit_leak_current(-75.0, 10.0)
        # set equilibirum potententials
        self.tree.set_v_ep(-75.0)
        self.tree.set_comp_tree()

    def load_axon_tree(self):
        """
        Parameters taken from a BBP SST model for a subset of ion channels
        """
        self.tree = GreensTreeTime(
            os.path.join(MORPHOLOGIES_PATH_PREFIX, "ball_and_axon.swc"),
            types=[1, 2, 3, 4],
        )
        # capacitance and axial resistance
        self.tree.set_physiology(1.0, 100.0 / 1e6)
        # ion channels
        k_chan = channelcollection.SKv3_1()
        self.tree.add_channel_current(
            k_chan, 0.653374 * 1e6, -85.0, node_arg=[self.tree[1]]
        )
        self.tree.add_channel_current(k_chan, 0.196957 * 1e6, -85.0, node_arg="axonal")
        na_chan = channelcollection.NaTa_t()
        self.tree.add_channel_current(
            na_chan, 0.001 * 1e6, 50.0, node_arg=[self.tree[1]]
        )
        self.tree.add_channel_current(na_chan, 3.418459 * 1e6, 50.0, node_arg="axonal")
        ca_chan = channelcollection.Ca_HVA()
        self.tree.add_channel_current(
            ca_chan, 0.000792 * 1e6, 132.4579341637009, node_arg=[self.tree[1]]
        )
        self.tree.add_channel_current(
            ca_chan, 0.000138 * 1e6, 132.4579341637009, node_arg="axonal"
        )
        self.tree.fit_leak_current(-75.0, 10.0)
        # set equilibirum potententials
        self.tree.set_v_ep(-75.0)
        self.tree.set_comp_tree()

    def load_ball(self, is_active):
        """
        Load point neuron model
        """
        self.tree = GreensTreeTime(os.path.join(MORPHOLOGIES_PATH_PREFIX, "ball.swc"))
        # capacitance and axial resistance
        self.tree.set_physiology(0.8, 100.0 / 1e6)
        if is_active:
            # ion channels
            k_chan = channelcollection.Kv3_1()
            self.tree.add_channel_current(k_chan, 0.766 * 1e6, -85.0)
            ca_chan = channelcollection.Ca_HVA()
            self.tree.add_channel_current(ca_chan, 0.792 * 1e6, 132.4579341637009)
            ca_chan = channelcollection.h()
            self.tree.add_channel_current(ca_chan, 0.008 * 1e6, -43.0)
            na_chan = channelcollection.Na_Ta()
            self.tree.add_channel_current(na_chan, 1.71 * 1e6, 50.0)
        # fit leak current
        self.tree.fit_leak_current(-75.0, 10.0)
        # set equilibirum potententials
        self.tree.set_v_ep(-75.0)
        # set computational tree
        self.tree.set_comp_tree()

    def test_string_representation(self):
        self.load_ball(1)

        repr_str = (
            "['GreensTreeTime', "
            "\"{'node index': 1, 'parent index': -1, 'content': '{}', 'xyz': array([0., 0., 0.]), 'R': '12', 'swc_type': 1, 'currents': {'Kv3_1': '(766000, -85)', 'Ca_HVA': '(792000, 132.458)', 'h': '(8000, -43)', 'Na_Ta': '(1.71e+06, 50)', 'L': '(20, -3493.27)'}, 'concmechs': {}, 'c_m': '0.8', 'r_a': '0.0001', 'g_shunt': '0', 'v_ep': '-75', 'conc_eps': {}, 'expansion_points': {}}\""
            "]{'channel_storage': ['Ca_HVA', 'Kv3_1', 'Na_Ta', 'h'], 'freqs': None, 't': None}"
        )
        assert repr(self.tree) == repr_str

    def test_passive_kernels(self, pplot=False):
        self._init_ft()
        self.load_T_tree()
        greens_tree = GreensTree(self.tree)
        sim_tree = NeuronSimTree(self.tree)

        locs = [(1, 0.5), (4, 0.5), (4, 1.0), (5, 0.5), (6, 0.5), (7, 0.5), (8, 0.5)]
        self.tree.set_impedance(self.ft)

        zt_mat_gtt = self.tree.calc_impulse_response_matrix(locs)
        zt_mat_quad = self.tree.calc_impulse_response_matrix(locs, method="quadrature")
        zt_mat_expf = self.tree.calc_impulse_response_matrix(locs, method="exp fit")

        # compute impedance matrix with Green's function
        greens_tree.set_impedance(self.ft.s)
        zf_mat_gtf = greens_tree.calc_impedance_matrix(locs)
        # convert impedance matrix to time domain
        zt_mat_expl = np.zeros((len(self.ft.t), len(locs), len(locs)))
        for ii, jj in itertools.product(list(range(len(locs))), list(range(len(locs)))):
            zt_mat_expl[:, ii, jj] = (
                self.ft.ft_inv(zf_mat_gtf[:, ii, jj])[1].real * 1e-3
            )
        # simulate the temporal matrix
        tk, zt_mat_sim = sim_tree.calc_impulse_response_matrix(
            locs,
            t_max=self.tmax,
            dt_pulse=0.1,
            dstep=-2,
            i_amp=0.001,
            factor_lambda=1.0,
            t_calibrate=0.0,
            dt=0.025,
            v_init=-75.0,
        )

        nt = min(len(tk), len(self.ft.t))
        t_arr = self.ft.t[:nt]
        zt_mat_gtt = zt_mat_gtt[:nt]
        zt_mat_quad = zt_mat_quad[:nt]
        zt_mat_expf = zt_mat_expf[:nt]
        zt_mat_expl = zt_mat_expl[:nt]
        zt_mat_sim = zt_mat_sim[:nt]

        assert np.allclose(
            zt_mat_expl[int(1.5 / self.dt) :, :, :],
            zt_mat_gtt[int(1.5 / self.dt) :, :, :],
            atol=0.50,
        )
        assert np.allclose(
            zt_mat_sim[int(1.5 / self.dt) :, :, :],
            zt_mat_gtt[int(1.5 / self.dt) :, :, :],
            atol=0.25,
        )

        if pplot:
            colours = list(pl.rcParams["axes.prop_cycle"].by_key()["color"])
            pl.figure("zt", figsize=(12, 4))
            ax0 = pl.subplot(131)
            ax1 = pl.subplot(132)

            kk = 0
            for (ii, loc1), (jj, loc2) in itertools.product(
                enumerate(locs), enumerate(locs)
            ):
                ax = ax0 if ii == jj else ax1
                ax.plot(
                    t_arr,
                    zt_mat_gtt[:, ii, jj],
                    c=colours[kk % len(colours)],
                    ls="-",
                    lw=0.7,
                )
                ax.plot(t_arr, zt_mat_expl[:, ii, jj], c="k", ls="--", lw=1)
                ax.plot(
                    t_arr,
                    zt_mat_sim[:, ii, jj],
                    c=colours[kk % len(colours)],
                    ls=":",
                    lw=3,
                )
                kk += 1

            pl.show()

        # test derivatives
        zt_mat, dz_dt_mat = self.tree.calc_impulse_response_matrix(
            locs, compute_time_derivative=True
        )
        dz_dt_second_order = (zt_mat[2:] - zt_mat[:-2]) / (2.0 * self.dt)

        assert np.allclose(
            dz_dt_mat[int(1.5 / self.dt + 1) : -1, :, :],
            dz_dt_second_order[int(1.5 / self.dt) :, :, :],
            atol=0.20,
        )

        if pplot:
            ax2 = pl.subplot(133)

            kk = 0
            for (ii, loc1), (jj, loc2) in itertools.product(
                enumerate(locs), enumerate(locs)
            ):
                ax2.plot(
                    self.ft.t[1:-1],
                    dz_dt_second_order[:, ii, jj],
                    c=colours[kk % len(colours)],
                    ls="-",
                    lw=0.7,
                )
                ax2.plot(
                    self.ft.t[1:-1],
                    dz_dt_mat[1:-1, ii, jj],
                    c=colours[kk % len(colours)],
                    ls="--",
                    lw=2,
                )
                kk += 1

            pl.show()

    def test_active_kernels(self, pplot=False):
        self._init_ft()
        self.load_axon_tree()
        greens_tree = GreensTree(self.tree)
        sim_tree = NeuronSimTree(self.tree)

        locs = [(1, 0.5), (5, 0.95)]
        self.tree.set_impedance(self.ft)

        zt_mat_gtt = self.tree.calc_impulse_response_matrix(locs)
        zt_mat_quad = self.tree.calc_impulse_response_matrix(locs, method="quadrature")
        zt_mat_expf = self.tree.calc_impulse_response_matrix(locs, method="exp fit")

        # compute impedance matrix with Green's function
        greens_tree.set_impedance(self.ft.s)
        zf_mat_gtf = greens_tree.calc_impedance_matrix(locs)
        # convert impedance matrix to time domain
        zt_mat_expl = np.zeros((len(self.ft.t), len(locs), len(locs)))
        for ii, jj in itertools.product(list(range(len(locs))), list(range(len(locs)))):
            zt_mat_expl[:, ii, jj] = (
                self.ft.ft_inv(zf_mat_gtf[:, ii, jj])[1].real * 1e-3
            )
        # simulate the temporal matrix
        tk, zt_mat_sim = sim_tree.calc_impulse_response_matrix(
            locs,
            t_max=self.tmax,
            dt_pulse=0.1,
            dstep=-2,
            i_amp=0.001,
            factor_lambda=1.0,
            t_calibrate=0.0,
            dt=0.025,
            v_init=-75.0,
        )

        nt = min(len(tk), len(self.ft.t))
        t_arr = self.ft.t[:nt]
        zt_mat_gtt = zt_mat_gtt[:nt]
        zt_mat_quad = zt_mat_quad[:nt]
        zt_mat_expf = zt_mat_expf[:nt]
        zt_mat_expl = zt_mat_expl[:nt]
        zt_mat_sim = zt_mat_sim[:nt]

        assert np.allclose(
            zt_mat_expl[int(1.5 / self.dt) :, :, :],
            zt_mat_gtt[int(1.5 / self.dt) :, :, :],
            atol=2.8,
        )
        assert np.allclose(
            zt_mat_sim[int(1.5 / self.dt) :, :, :],
            zt_mat_gtt[int(1.5 / self.dt) :, :, :],
            atol=2.8,
        )

        if pplot:
            colours = list(pl.rcParams["axes.prop_cycle"].by_key()["color"])
            pl.figure("zt_inp")
            ax0 = pl.subplot(121)
            ax1 = pl.subplot(122)
            pl.figure("zt_trans")
            ax2 = pl.gca()

            kk = 0
            for (ii, loc1), (jj, loc2) in itertools.product(
                enumerate(locs), enumerate(locs)
            ):
                if ii == jj and ii == 0:
                    ax = ax0
                elif ii == jj and ii == 1:
                    ax = ax1
                elif ii != jj:
                    ax = ax2
                else:
                    raise NotImplementedError("No ax defined for this case")
                ax.plot(
                    t_arr,
                    zt_mat_gtt[:, ii, jj],
                    c=colours[kk % len(colours)],
                    ls="-",
                    lw=0.7,
                )
                # ax.plot(t_arr, zt_mat_quad[:,ii,jj], c="grey", ls="--", lw=1)
                # ax.plot(t_arr, zt_mat_expf[:,ii,jj], c="grey", ls=":", lw=1)
                ax.plot(t_arr, zt_mat_expl[:, ii, jj], c="k", ls="--", lw=1)
                ax.plot(
                    t_arr,
                    zt_mat_sim[:, ii, jj],
                    c=colours[kk % len(colours)],
                    ls=":",
                    lw=3,
                )
                kk += 1

            pl.show()

    def test_channel_responses(self, pplot=False):
        self._init_ft()
        self.load_axon_tree()
        self.tree.set_impedance(self.ft)
        sim_tree = NeuronSimTree(self.tree)

        locs = [(1, 0.05), (5, 0.45), (5, 0.5)]
        nl = len(locs)
        idxs_out = [0, 1, 2]
        idx_in = 2

        crt_01 = [
            self.tree.calc_channel_response_t(
                locs[idx_in], locs[idx_out], compute_time_derivative=0, method=""
            )
            for idx_out in idxs_out
        ]
        crt_01_quad = [
            self.tree.calc_channel_response_t(
                locs[idx_in],
                locs[idx_out],
                compute_time_derivative=0,
                method="quadrature",
            )
            for idx_out in idxs_out
        ]
        crt_01_expf = [
            self.tree.calc_channel_response_t(
                locs[idx_in], locs[idx_out], compute_time_derivative=0, method="exp fit"
            )
            for idx_out in idxs_out
        ]
        crt_mat = self.tree.calc_channel_response_matrix(locs)
        zt_mat_gtt = self.tree.calc_impulse_response_matrix(locs)

        # simulate
        i_amp = 0.001  # nA
        dt_pulse = 0.1  # ms
        delay_pulse = 10.0  # ms
        tmax = self.tmax + delay_pulse
        sim_tree.init_model(dt=self.dt, t_calibrate=10.0, factor_lambda=100)
        sim_tree.add_i_clamp(locs[idx_in], i_amp, delay_pulse, dt_pulse)
        sim_tree.store_locs(locs, "rec locs", warn=False)
        # simulate
        res = sim_tree.run(tmax, record_from_channels=True)
        sim_tree.delete_model()

        slice_sim = np.s_[int((delay_pulse + dt_pulse) / self.dt - 2) :]
        t_sim = res["t"][slice_sim] - (delay_pulse + dt_pulse)

        v_resps = [
            (res["v_m"][idxs_out[ii]][slice_sim] - res["v_m"][idxs_out[ii]][0])
            / (i_amp * dt_pulse)
            for ii in range(nl)
        ]

        if pplot:
            pl.figure("v")
            ax0 = pl.subplot(121)
            ax1 = pl.subplot(122)
            lss = ["-", "--", ":", "-."]
            css = ["r", "b", "g", "y"]
            lws = ["1", "2", "2.5", "1.5"]

            for ii, idx_out in enumerate(idxs_out):
                ax0.plot(res["t"], res["v_m"][idxs_out[ii]], c=css[ii], lw=1.0, ls="-")

                ax1.plot(t_sim, v_resps[ii], c=css[ii], lw=1.0, ls="-")
                ax1.plot(
                    self.ft.t[1:],
                    zt_mat_gtt[1:, idxs_out[ii], idx_in],
                    c=css[ii],
                    lw=2,
                    ls="--",
                )

        slice_time = np.s_[int(1.5 / self.dt) :]
        for ii in range(nl):
            if pplot:
                print(
                    "zt vs sim:",
                    np.max(
                        np.abs(
                            v_resps[ii][slice_time]
                            - zt_mat_gtt[slice_time, idxs_out[ii], idx_in]
                        )
                    )
                    / np.max(np.abs(v_resps[ii][slice_time])),
                )
            assert np.allclose(
                v_resps[ii][slice_time],
                zt_mat_gtt[slice_time, idxs_out[ii], idx_in],
                atol=0.015 * np.max(np.abs(v_resps[ii][slice_time])),
            )

        # compute state variable deflections
        for channel_name in self.tree.get_channels_in_tree():

            if pplot:
                pl.figure(channel_name)
                axes = [pl.subplot(int(f"1{nl}{ii+1}")) for ii in range(nl)]
                for ii in range(nl):
                    axes[ii].set_title(f"rec loc {ii}")

            for svar_name in list(crt_01[0][channel_name].keys()):
                for idx_out in idxs_out:
                    # simulated channel response
                    q_sim = res["chan"][channel_name][svar_name][idx_out]
                    q_sim = q_sim[slice_sim] - q_sim[0]
                    q_sim /= i_amp * dt_pulse
                    # computed channel response
                    q_calc = crt_mat[idx_out][channel_name][svar_name][:, idx_in]

                    # compare `calc_channel_response_t()` and `calcChannelResponsMatrix()`
                    q_calc_ = crt_01[idx_out][channel_name][svar_name]
                    assert np.allclose(q_calc, q_calc_)

                    # compare `method="exp fit"` and `method="quadrature"`
                    q_calc_expf = crt_01_expf[idx_out][channel_name][svar_name]
                    q_calc_quad = crt_01_quad[idx_out][channel_name][svar_name]
                    if pplot:
                        print(
                            f"exp fit vs quadrature {channel_name}:",
                            np.max(
                                np.abs(
                                    q_calc_expf[slice_time] - q_calc_quad[slice_time]
                                )
                            )
                            / np.max(np.abs(q_calc_quad[slice_time])),
                        )
                    # exp fit does not work well for Ca_HVA response for some reason
                    if channel_name != "Ca_HVA":
                        assert np.allclose(
                            q_calc_expf[slice_time],
                            q_calc_quad[slice_time],
                            atol=0.15 * np.max(np.abs(q_calc_quad[slice_time])),
                        )

                    # compare `calcChannelResponsMatrix()` and simulation
                    if pplot:
                        print(
                            "qt vs sim:",
                            np.max(np.abs(q_calc - q_sim)) / np.max(np.abs(q_sim)),
                        )
                    assert np.allclose(q_calc, q_sim, atol=0.40 * np.max(np.abs(q_sim)))

                    if pplot:
                        axes[idx_out].plot(
                            self.ft.t[1:], q_calc[1:], c="r", ls="-", lw=1.0
                        )
                        axes[idx_out].plot(
                            self.ft.t[1:], q_calc_[1:], c="b", ls="--", lw=1.0
                        )
                        axes[idx_out].plot(
                            self.ft.t[1:], q_calc_expf[1:], c="grey", ls="--", lw=1.0
                        )
                        axes[idx_out].plot(
                            self.ft.t[1:], q_calc_quad[1:], c="grey", ls="-.", lw=2.0
                        )
                        axes[idx_out].plot(t_sim, q_sim, c="k", ls=":", lw=2.0)

        if pplot:
            pl.show()

    def test_exponential_derivative(self, pplot=False):
        self._init_ft()
        # test passive case
        self.load_ball(is_active=False)
        self.tree.as_passive_membrane()
        self.tree.set_comp_tree()
        self.tree.set_impedance(self.ft)

        loc = (1, 0.5)
        zt, dzt_dt = self.tree.calc_zt(loc, loc, compute_time_derivative=1)

        a_soma = 4.0 * np.pi * self.tree[1].R ** 2 * 1e-8  # cm^2
        c_soma = self.tree[1].c_m * a_soma  # uF
        g_soma = self.tree[1].currents["L"][0] * a_soma  # uS

        c_fit = np.linalg.lstsq(dzt_dt[5:, None], -g_soma * zt[5:] * 1e-3, rcond=None)[
            0
        ][0]

        # check fit result
        assert np.allclose(c_soma, c_fit, rtol=1e-4)
        # check whether fit arrays are sufficiently uniform
        assert np.allclose(c_soma * dzt_dt[5:], -g_soma * zt[5:] * 1e-3, rtol=5e-3)

        # test active case
        self.load_ball(is_active=True)
        self.tree.set_impedance(self.ft)
        zt, dzt_dt = self.tree.calc_zt(loc, loc, compute_time_derivative=1, method="")
        zt_, dzt_dt_ = self.tree.calc_zt(
            loc, loc, compute_time_derivative=1, method="quadrature"
        )
        crt, dcrt_dt = self.tree.calc_channel_response_t(
            loc, loc, compute_time_derivative=1, method=""
        )
        crt_ = self.tree.calc_channel_response_t(
            loc, loc, compute_time_derivative=0, method="quadrature"
        )

        # simulate the temporal matrix
        sim_tree = NeuronSimTree(self.tree)
        tk, zt_mat_sim = sim_tree.calc_impulse_response_matrix([(1, 0.5)])

        soma = self.tree[1]
        a_soma = 4.0 * np.pi * soma.R**2 * 1e-8  # cm^2
        c_soma = self.tree[1].c_m * a_soma  # uF
        g_soma = 0
        svar_terms = {}
        for channel_name in soma.currents:
            # for channel_name in ['L']:
            g, e = soma.currents[channel_name]

            if channel_name == "L":
                g_soma -= g * a_soma
                break

            # recover the ionchannel object
            channel = self.tree.channel_storage[channel_name]

            # get voltage(s), state variable expansion point(s) and
            # concentration(s) around which to linearize the channel
            v, sv = soma._construct_channel_args(channel)

            # add open probability to total conductance
            g_soma -= g * a_soma * channel.compute_p_open(v)

            # add linearized channel contribution to membrane conductance
            dp_dx = channel.compute_derivatives(v)[0]

            svar_terms[channel_name] = {}
            for svar, dp_dx_ in dp_dx.items():
                svar_terms[channel_name][svar] = g * a_soma * dp_dx_ * (e - v)

        if pplot:
            pl.figure("z(t)")
            ax1 = pl.subplot(121)
            ax1.set_title("z(t)")
            ax1.plot(self.ft.t[1:], zt[1:])
            ax1.plot(self.ft.t[1:], zt_[1:], "k--")
            ax1.plot(tk, zt_mat_sim[:, 0, 0], ":", c="Grey", lw=2)
            ax2 = pl.subplot(122)
            ax2.set_title("dz_dt(t)")
            ax2.plot(self.ft.t[1:], dzt_dt[1:])
            ax2.plot(self.ft.t[1:], dzt_dt_[1:], "k--")

        ef = ke.ExpFitter()

        if pplot:
            for channel_name in crt:
                pl.figure(f"{channel_name}")
                for svar, resp in crt[channel_name].items():
                    pl.plot(self.ft.t[1:], resp[1:], label=str(svar))
                    pl.plot(
                        self.ft.t[1:],
                        crt_[channel_name][svar][1:],
                        label=str(svar),
                        c="Grey",
                        ls=":",
                        lw=2,
                    )

                    a, c, rms = ef.PronyExpFit(20, self.ft.t, resp)
                    kresp = Kernel({"a": -a, "c": c})(self.ft.t)

                    pl.plot(self.ft.t[1:], kresp[1:], "k--")

                pl.legend(loc=0)

        # construct product of system matrix with impedance kernel matrix
        arr_aux = g_soma * zt
        for channel_name in crt:
            for svar_name in crt[channel_name]:
                arr_aux += (
                    svar_terms[channel_name][svar_name] * crt[channel_name][svar_name]
                )

        if pplot:
            pl.figure()
            ax1 = pl.subplot(121)
            ax1.plot(self.ft.t[1:], arr_aux[1:] / c_soma)
            ax1.plot(self.ft.t[1:], dzt_dt[1:] * 1e3, "k--")
            ax2 = pl.subplot(122)
            ax2.plot(self.ft.t[1:], arr_aux[1:] / dzt_dt[1:] * 1e-3)
            ax2.axhline(c_soma, ls="--", c="k")
            ax2.set_ylim((-2e-5, 2e-5))

        c_fit = np.linalg.lstsq(dzt_dt[5:, None], arr_aux[5:] * 1e-3, rcond=None)[0][0]
        if pplot:
            print(f"c_soma = {c_soma} uF, c_fit = {c_fit} uF")

        # check fit result
        assert np.allclose(c_soma, c_fit, rtol=5e-2)

        if pplot:
            pl.show()


if __name__ == "__main__":
    tgt = TestGreensTree()
    tgt.test_string_representation()
    tgt.test_basic_properties()
    tgt.test_values()

    tgtt = TestGreensTreeTime()
    tgtt.test_string_representation()
    tgtt.test_passive_kernels(pplot=True)
    tgtt.test_active_kernels(pplot=True)
    tgtt.test_channel_responses()
    tgtt.test_exponential_derivative()
