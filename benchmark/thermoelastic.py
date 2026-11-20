"""One-dimensional thermoelastic-plastic casing model. Standard library only. [MODEL]

Per depth node, casing axial direction. A cemented node holds its total
mechanical strain after cement set; steel is elastic-perfectly-plastic with
temperature-dependent modulus and yield. An unsupported interval between
cemented ends buckles as an Euler column with fixed ends. Parameters are the
frozen values of PLAN.md section 3; each is an assumption unless sourced.
"""
import math

PARAMETERS = {
    'alpha_per_k': 12.5e-6,
    'e_20_pa': 200e9, 'e_slope_per_k': 4e-4,
    'yield_20_pa': {'K55': 379e6, 'L80': 552e6},
    'derating_at_400c': 0.80,
    'connection_efficiency': 0.85,
    't_set_c': 80.0,
    't_quench_c': 30.0,
    'lag_h': 2.0,
    'radius_of_gyration_m': {'13-3/8': 0.117, '9-5/8': 0.083},
}


def modulus(t_c, p=PARAMETERS):
    return p['e_20_pa'] * (1 - p['e_slope_per_k'] * (t_c - 20.0))


def yield_stress(grade, t_c, p=PARAMETERS):
    slope = (1 - p['derating_at_400c']) / 380.0
    return p['yield_20_pa'][grade] * (1 - slope * max(t_c - 20.0, 0.0))


def euler_strain(unsupported_m, size, p=PARAMETERS):
    """Critical compressive strain of a fixed-fixed column (effective length factor 0.5)."""
    return (math.pi * p['radius_of_gyration_m'][size] / (0.5 * unsupported_m)) ** 2


def lagged(fluid_c, dt_h, start_c, p=PARAMETERS):
    """Casing temperature following the fluid history with a first-order lag (exact step update)."""
    out, t = [], start_c
    k = 1 - math.exp(-dt_h / p['lag_h'])
    for f in fluid_c:
        t += (f - t) * k
        out.append(t)
    return out


class Node:
    """One cemented casing node."""

    def __init__(self, grade, p=PARAMETERS):
        self.grade, self.p = grade, p
        self.plastic = 0.0
        self.cumulative_plastic = 0.0
        self.max_tension_utilisation = 0.0
        self.connection_failed_at_c = None
        self.stress = 0.0

    def step(self, t_c):
        p = self.p
        e = modulus(t_c, p)
        trial = e * (-p['alpha_per_k'] * (t_c - p['t_set_c']) - self.plastic)
        limit = yield_stress(self.grade, t_c, p)
        if abs(trial) > limit:
            change = (abs(trial) - limit) / e * (1 if trial > 0 else -1)
            self.plastic += change
            self.cumulative_plastic += abs(change)
            trial = limit if trial > 0 else -limit
        self.stress = trial
        if trial > 0:
            use = trial / (p['connection_efficiency'] * limit)
            self.max_tension_utilisation = max(self.max_tension_utilisation, use)
            if use >= 1 and self.connection_failed_at_c is None:
                self.connection_failed_at_c = t_c
        return trial


def run_history(grade, casing_c, p=PARAMETERS):
    node = Node(grade, p)
    stresses = [node.step(t) for t in casing_c]
    return node, stresses


def event(t_max_c, hold_h=72.0, heat_h=48.0, quench_h=6.0, dt_h=0.25, p=PARAMETERS):
    """Fluid history: cement set, heat-up to t_max, hold, quench to the quench temperature, hold cold."""
    n_heat, n_hold, n_q = int(heat_h / dt_h), int(hold_h / dt_h), int(quench_h / dt_h)
    fluid = [p['t_set_c'] + (t_max_c - p['t_set_c']) * (i + 1) / n_heat for i in range(n_heat)]
    fluid += [t_max_c] * n_hold
    fluid += [t_max_c + (p['t_quench_c'] - t_max_c) * (i + 1) / n_q for i in range(n_q)]
    fluid += [p['t_quench_c']] * int(24 / dt_h)
    return fluid, dt_h


def onset_heating_dt(grade, p=PARAMETERS):
    """Smallest heating above cement set for which the connection fails on the standard quench, K."""
    lo, hi = 0.0, 600.0
    for _ in range(40):
        mid = (lo + hi) / 2
        fluid, dt = event(p['t_set_c'] + mid, p=p)
        node, _ = run_history(grade, lagged(fluid, dt, p['t_set_c'], p), p)
        if node.connection_failed_at_c is None:
            lo = mid
        else:
            hi = mid
    return hi


def well_case(case, p=PARAMETERS):
    """Evaluate a well: nodes every 50 m; unsupported intervals buckle on heat-up if past the Euler strain."""
    fluid, dt = event(case['t_max_c'], p=p)
    casing = lagged(fluid, dt, p['t_set_c'], p)
    peak = max(casing)
    node, _ = run_history(case['grade'], casing, p)
    unsupported = case.get('unsupported', [])
    rows, failures = [], []
    depth = 0.0
    while depth <= case['shoe_m']:
        interval = next((u for u in unsupported if u[0] <= depth < u[1]), None)
        row = {'depth_m': depth, 'supported': interval is None}
        if interval is None:
            row['mode'] = 'connection tension on quench' if node.connection_failed_at_c is not None else None
            row['tension_utilisation'] = node.max_tension_utilisation
        else:
            strain = p['alpha_per_k'] * (peak - p['t_set_c'])
            critical = euler_strain(interval[1] - interval[0], case['size'], p)
            row['mode'] = 'buckled on heat-up' if strain > critical else None
            row['thermal_strain_over_critical'] = strain / critical
        if row['mode']:
            failures.append(row)
        rows.append(row)
        depth += 50.0
    buckled = [r for r in failures if r['mode'].startswith('buckled')]
    return {'case': case['name'], 'peak_casing_c': peak, 'fails': bool(failures),
            'modes': sorted({r['mode'] for r in failures}),
            'shallowest_failed_m': failures[0]['depth_m'] if failures else None,
            'shallowest_buckled_m': buckled[0]['depth_m'] if buckled else None,
            'plastic_strain_cemented': node.cumulative_plastic,
            'tension_utilisation_cemented': node.max_tension_utilisation, 'nodes': rows}
