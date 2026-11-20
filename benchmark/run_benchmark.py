"""Run the well cases of PLAN.md section 4 once and judge comparisons B1-B6.

    python3 run_benchmark.py [--out DIR]

Standard library only. Output: benchmark-results.json. Everything is [MODEL].
"""
import argparse
import copy
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import thermoelastic as te                                             # noqa: E402

CASES = [
    {'name': 'IDDP-1', 'grade': 'K55', 'size': '13-3/8', 't_max_c': 450.0, 'shoe_m': 1950.0, 'unsupported': [(1490.0, 1950.0)],
     'published': 'multiple breaks below ~1600 m; heated from <100 C to >300 C (450 C fluid while flowing), then quenched'},
    {'name': 'IDDP-2', 'grade': 'L80', 'size': '9-5/8', 't_max_c': 426.0, 'shoe_m': 2900.0, 'unsupported': [(2300.0, 2400.0)],
     'published': 'uncemented section of more than 100 m below ~2300 m buckled and collapsed during early recovery'},
    {'name': 'intact-240', 'grade': 'K55', 'size': '13-3/8', 't_max_c': 240.0, 'shoe_m': 1500.0},
    {'name': 'intact-280', 'grade': 'K55', 'size': '13-3/8', 't_max_c': 280.0, 'shoe_m': 1500.0},
    {'name': 'intact-320', 'grade': 'K55', 'size': '13-3/8', 't_max_c': 320.0, 'shoe_m': 1500.0},
]
REPORTED_DT_K = {'lower bound, "<100 to >300 C"': 200.0, 'from 450 C fluid and 80 C set': 370.0}
REPORTED_DEPTH_M = 1600.0


def judge(p=te.PARAMETERS):
    results = {c['name']: te.well_case(c, p) for c in CASES}
    onset = te.onset_heating_dt('K55', p)
    intact_fail = [n for n in ('intact-240', 'intact-280', 'intact-320') if results[n]['fails']]
    return results, onset, intact_fail


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('.'))
    args = parser.parse_args()
    results, onset, intact_fail = judge()
    within = {k: abs(onset - v) / v <= 0.15 for k, v in REPORTED_DT_K.items()}
    iddp1, iddp2 = results['IDDP-1'], results['IDDP-2']
    depth = iddp1['shallowest_buckled_m']
    robustness = []
    for name in ('connection_efficiency', 'derating_at_400c', 't_set_c'):
        for factor in (0.9, 1.1):
            p = copy.deepcopy(te.PARAMETERS)
            p[name] = min(p[name] * factor, 1.0) if name != 't_set_c' else p[name] * factor
            _, o, bad = judge(p)
            robustness.append({'parameter': name, 'factor': factor, 'onset_heating_dt_k': o, 'intact_cases_failing': bad})
    fluid = [80 + 370 * (0.5 + 0.5 * math.sin(i / 200.0)) for i in range(30 * 24 * 6)]
    started = time.time()
    casing = te.lagged(fluid, 1 / 6, 80.0)
    for _ in range(100):
        te.run_history('K55', casing)
    speed = time.time() - started
    comparisons = {
        'B1_onset_dt': {'model_onset_heating_dt_k': onset, 'model_onset_peak_c': te.PARAMETERS['t_set_c'] + onset,
                        'reported_dt_k': REPORTED_DT_K, 'within_15pct_of': within, 'model_fails_IDDP1_at_its_inputs': iddp1['fails'],
                        'pass': iddp1['fails'] and any(within.values()),
                        'limit': 'the source gives bounds on the heating, not a failure onset'},
        'B2_depth': {'model_shallowest_unsupported_failure_m': depth, 'model_shallowest_failure_any_mode_m': iddp1['shallowest_failed_m'],
                     'reported_m': REPORTED_DEPTH_M,
                     'pass': depth is not None and abs(depth - REPORTED_DEPTH_M) / REPORTED_DEPTH_M <= 0.15 and iddp1['shallowest_failed_m'] == depth,
                     'limit': 'depth of the unsupported interval is an input; the cemented column above it is judged by the connection rule'},
        'B3_iddp2_buckles': {'pass': 'buckled on heat-up' in iddp2['modes'], 'modes': iddp2['modes']},
        'B4_separation': {'intact_cases_failing': intact_fail, 'pass': not intact_fail},
        'B5_robustness': robustness,
        'B6_speed': {'seconds_30_days_100_nodes': speed, 'pass': speed < 5.0},
    }
    claim = all(comparisons[k]['pass'] for k in ('B1_onset_dt', 'B2_depth', 'B3_iddp2_buckles', 'B4_separation'))
    out = {'label': '[MODEL] one-dimensional thermoelastic-plastic benchmark; parameters fixed before the run (PLAN.md section 3)',
           'parameters': {k: v for k, v in te.PARAMETERS.items()}, 'comparisons': comparisons,
           'benchmark_claim': 'made' if claim else 'NOT made: published as an open problem',
           'cases': {n: {k: v for k, v in r.items() if k != 'nodes'} for n, r in results.items()}}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'benchmark-results.json').write_text(json.dumps(out, indent=1) + '\n')
    for name, r in out['cases'].items():
        print(f"{name:11s} peak {r['peak_casing_c']:.0f} C  fails {r['fails']}  {r['modes']}  tension use {r['tension_utilisation_cemented']:.2f}  shallowest {r['shallowest_failed_m']}")
    print('onset heating dT', round(onset, 1), 'K; within 15 %:', within)
    for k in ('B1_onset_dt', 'B2_depth', 'B3_iddp2_buckles', 'B4_separation', 'B6_speed'):
        print(k, 'PASS' if comparisons[k]['pass'] else 'FAIL')
    print('robustness:', [(r['parameter'], r['factor'], round(r['onset_heating_dt_k']), r['intact_cases_failing']) for r in robustness])
    print('benchmark claim:', out['benchmark_claim'])


if __name__ == '__main__':
    main()
