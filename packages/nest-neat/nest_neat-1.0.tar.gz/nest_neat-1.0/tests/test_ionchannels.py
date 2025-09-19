# -*- coding: utf-8 -*-
#
# test_ionchannels.py
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
import sympy as sp

import pytest
import pickle
import os, shutil

from neat import IonChannel

import channelcollection_for_tests as channelcollection


class test_channels:
    def test_basic(self):
        tcn = channelcollection.test_channel()
        v_arr = np.linspace(-80.0, -10.0, 10)

        factors = np.array([5.0, 1.0])
        powers = np.array([[3, 3, 1], [2, 2, 1]])

        varnames = np.array(
            [
                [sp.symbols("a00"), sp.symbols("a01"), sp.symbols("a02")],
                [sp.symbols("a10"), sp.symbols("a11"), sp.symbols("a12")],
            ]
        )

        # state variable asymptotic values
        def varinf(v):
            aux = np.ones_like(v) if isinstance(v, np.ndarray) else 1.0
            return np.array(
                [
                    [
                        1.0 / (1.0 + np.exp((v - 30.0) / 100.0)),
                        1.0 / (1.0 + np.exp((-v + 30.0) / 100.0)),
                        -10.0 * aux,
                    ],
                    [
                        2.0 / (1.0 + np.exp((v - 30.0) / 100.0)),
                        2.0 / (1.0 + np.exp((-v + 30.0) / 100.0)),
                        -30.0 * aux,
                    ],
                ]
            )

        # state variable functions
        def dvarinf_dv(v):
            aux = np.ones_like(v) if isinstance(v, np.ndarray) else 1.0
            vi_aux = varinf(v)
            return np.array(
                [
                    [
                        -vi_aux[0, 0, :] * (1 - vi_aux[0, 0, :]) / 100.0,
                        vi_aux[0, 1, :] * (1 - vi_aux[0, 1, :]) / 100.0,
                        0.0 * aux,
                    ],
                    [
                        -vi_aux[1, 0, :] * (1 - vi_aux[1, 0, :] / 2.0) / 100.0,
                        vi_aux[1, 1, :] * (1 - vi_aux[1, 1, :] / 2.0) / 100.0,
                        0.0 * aux,
                    ],
                ]
            )

        # state variable relaxation time scale
        def taurel(v):
            aux = np.ones_like(v) if isinstance(v, np.ndarray) else 1.0
            return np.array(
                [[1.0 * aux, 2.0 * aux, 1.0 * aux], [2.0 * aux, 2.0 * aux, 3.0 * aux]]
            )

        # test whether activations are correct
        var_inf = varinf(v_arr)
        var_inf_chan = tcn.compute_varinf(v_arr)
        for ind, varname in np.ndenumerate(varnames):
            assert np.allclose(var_inf[ind], var_inf_chan[varname])

        # test whether open probability is correct
        p_open = np.sum(
            factors[:, np.newaxis] * np.product(var_inf ** powers[:, :, np.newaxis], 1),
            0,
        )
        p_open_ = tcn.compute_p_open(v_arr)
        assert np.allclose(p_open_, p_open)

        # test whether derivatives are correct
        dp_dx_chan, df_dv_chan, df_dx_chan = tcn.compute_derivatives(v_arr)

        # first: derivatives of open probability
        for ind, varname in np.ndenumerate(varnames):
            dp_dx = (
                factors[ind[0]]
                * powers[ind]
                * np.prod(var_inf[ind[0]] ** powers[ind[0]][:, np.newaxis], 0)
                / var_inf[ind]
            )
            assert np.allclose(dp_dx_chan[varname], dp_dx)

        # second: derivatives of state variable functions to voltage
        df_dv = dvarinf_dv(v_arr) / taurel(v_arr)
        for ind, varname in np.ndenumerate(varnames):
            assert np.allclose(df_dv[ind], df_dv_chan[varname])

        # third: derivatives of state variable functions to state variables
        df_dx = -1.0 / taurel(v_arr)
        for ind, varname in np.ndenumerate(varnames):
            assert np.allclose(df_dx[ind], df_dx_chan[varname])


def sp_exp(x):
    return sp.exp(x, evaluate=False)


def test_ionchannel_simplified(remove=True):
    if not os.path.exists("mech/"):
        os.mkdir("mech/")

    na = channelcollection.Na_Ta()

    p_o = na.compute_p_open(-35.0)
    assert np.allclose(p_o, 0.002009216860105564)

    l_s = na.compute_lin_sum(-35.0, 0.0, 50.0)
    assert np.allclose(l_s, -0.00534261017220376)

    na.write_mod_file("mech/")

    sk = channelcollection.SK()
    sk.write_mod_file("mech/")

    if remove:
        shutil.rmtree("mech/")


def test_pickling():
    # pickle and restore
    na_ta_channel = channelcollection.Na_Ta()
    s = pickle.dumps(na_ta_channel)
    new_na_ta_channel = pickle.loads(s)

    # multiple pickles
    s = pickle.dumps(na_ta_channel)
    s = pickle.dumps(na_ta_channel)
    new_na_ta_channel = pickle.loads(s)

    assert True  # reaching this means we didn't encounter an error


def test_broadcasting():
    na_ta = channelcollection.Na_Ta()

    v = np.array([-73.234, -50.325, -25.459])
    s = np.array([0.0, 10.0, 20.0, 40.0]) * 1j

    # error must be raised if arguments are not broadcastable
    with pytest.raises(ValueError):
        na_ta.compute_lin_sum(v, s)

    # check if broadcasting rules are applied correctly for voltage and frequency
    ll = na_ta.compute_lin_sum(v[:, None], s[None, :])
    l1 = na_ta.compute_linear(v[:, None], s[None, :])
    l2 = na_ta.compute_p_open(v[:, None])

    assert ll.shape == (3, 4)
    assert l1.shape == (3, 4)
    assert l2.shape == (3, 1)
    assert np.allclose(ll, (na_ta._get_reversal(None) - v[:, None]) * l1 - l2)

    # check if broadcasting rules are applied correctly for state variables
    sv = {"m": 0.2, "h": 0.4}
    ll = na_ta.compute_lin_sum(v[:, None], s[None, :], **sv)
    assert ll.shape == (3, 4)

    sv = {"m": np.array([0.1, 0.2, 0.3]), "h": np.array([0.9, 0.6, 0.3])}
    with pytest.raises(ValueError):
        ll = na_ta.compute_lin_sum(v[:, None], s[None, :], **sv)

    sv_ = {"m": sv["m"][:, None], "h": sv["h"][:, None]}
    ll = na_ta.compute_lin_sum(v[:, None], s[None, :], **sv_)
    assert ll.shape == (3, 4)

    sv__ = {"m": sv["m"][:, None, None], "h": sv["h"][None, None, :]}
    l_ = na_ta.compute_lin_sum(v[:, None, None], s[None, :, None], **sv__)
    assert l_.shape == (3, 4, 3)
    for ii in range(4):
        assert np.allclose(
            [ll[0, ii], ll[1, ii], ll[2, ii]],
            [l_[0, ii, 0], l_[1, ii, 1], l_[2, ii, 2]],
        )

    # test braodcasting for piecewise channel
    pwc = channelcollection.PiecewiseChannel()
    varinf = pwc.compute_varinf(v)
    tauinf = pwc.compute_tauinf(v)

    assert np.allclose(varinf["a"], np.array([0.1, 0.1, 0.9]))
    assert np.allclose(varinf["b"], np.array([0.8, 0.8, 0.2]))
    assert np.allclose(tauinf["a"], np.array([10.0, 10.0, 20.0]))
    assert np.allclose(tauinf["b"], np.array([0.1, 0.1, 50.0]))


if __name__ == "__main__":
    tcns = test_channels()
    tcns.test_basic()
    test_ionchannel_simplified()
    test_broadcasting()
