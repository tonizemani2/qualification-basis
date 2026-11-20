"""Exact checks of PLAN.md section 6. Run: python3 -m unittest test_thermoelastic -v"""
import copy
import math
import time
import unittest

import thermoelastic as te

FLAT = copy.deepcopy(te.PARAMETERS)          # constant properties for the closed forms
FLAT.update(e_slope_per_k=0.0, derating_at_400c=1.0)


class Exact(unittest.TestCase):
    def test_elastic_constrained_bar(self):
        node = te.Node('K55', FLAT)
        stress = node.step(FLAT['t_set_c'] + 100.0)
        self.assertAlmostEqual(stress, -200e9 * 12.5e-6 * 100.0, delta=1.0)
        self.assertEqual(node.plastic, 0.0)

    def test_residual_tension_after_heating_beyond_yield(self):
        dT, sy = 250.0, FLAT['yield_20_pa']['K55']
        node = te.Node('K55', FLAT)
        node.step(FLAT['t_set_c'] + dT)
        residual = node.step(FLAT['t_set_c'])
        self.assertAlmostEqual(residual, min(200e9 * (12.5e-6 * dT - sy / 200e9), sy), delta=1.0)

    def test_shakedown_inside_twice_yield(self):
        node = te.Node('K55', FLAT)
        hot = FLAT['t_set_c'] + 250.0            # 625 MPa of elastic range needed, below 2 x 379
        for _ in range(2):
            node.step(hot)
            node.step(FLAT['t_set_c'])
        first = node.cumulative_plastic
        node.step(hot)
        node.step(FLAT['t_set_c'])
        self.assertAlmostEqual(node.cumulative_plastic, first, delta=1e-12)

    def test_ratchet_free_alternating_plasticity_beyond_twice_yield(self):
        node = te.Node('K55', FLAT)
        hot = FLAT['t_set_c'] + 400.0            # 1000 MPa > 2 x 379
        node.step(hot); node.step(FLAT['t_set_c'])
        first = node.cumulative_plastic
        node.step(hot); node.step(FLAT['t_set_c'])
        per_cycle = 2 * (12.5e-6 * 400.0 - 2 * 379e6 / 200e9)
        self.assertAlmostEqual(node.cumulative_plastic - first, per_cycle, delta=1e-9)

    def test_euler_strain(self):
        self.assertAlmostEqual(te.euler_strain(100.0, '13-3/8'), (math.pi * 0.117 / 50.0) ** 2, delta=1e-15)

    def test_lag_matches_the_exponential(self):
        series = te.lagged([100.0] * 40, 0.25, 0.0)
        self.assertAlmostEqual(series[-1], 100.0 * (1 - math.exp(-10.0 / 2.0)), delta=1e-9)

    def test_onset_closed_form_with_constant_properties(self):
        p = FLAT
        expected = (1 + p['connection_efficiency']) * p['yield_20_pa']['K55'] / (p['e_20_pa'] * p['alpha_per_k']) \
            - (p['t_set_c'] - p['t_quench_c'])
        self.assertAlmostEqual(te.onset_heating_dt('K55', p), expected, delta=3.0)   # lag leaves < 3 K


class Speed(unittest.TestCase):
    def test_thirty_day_history_on_100_nodes_under_5_s(self):
        fluid = [80 + 370 * (0.5 + 0.5 * math.sin(i / 200.0)) for i in range(30 * 24 * 6)]
        started = time.time()
        casing = te.lagged(fluid, 1 / 6, 80.0)
        for _ in range(100):
            te.run_history('K55', casing)
        self.assertLess(time.time() - started, 5.0)


if __name__ == '__main__':
    unittest.main()
