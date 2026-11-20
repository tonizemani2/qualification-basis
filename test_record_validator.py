"""Run: python3 -m unittest test_record_validator -v"""
import copy
import json
import unittest
from pathlib import Path

import record_validator as rv

GOOD = json.loads((Path(__file__).resolve().parent / 'examples/record-450-W.json').read_text())


def broken(change):
    record = copy.deepcopy(GOOD)
    change(record)
    return rv.judge(record)


class Rules(unittest.TestCase):
    def test_example_is_conformant(self):
        self.assertEqual(rv.judge(GOOD)['findings'], [])

    def test_witness_from_the_qualifier_is_rejected(self):
        v = broken(lambda r: r['witness'].update(organisation='example laboratory a'))
        self.assertTrue(any('other than the qualifier' in f for f in v['findings']))

    def test_temperature_without_hours_is_rejected(self):
        v = broken(lambda r: r['duty_entries'][0].pop('hours'))
        self.assertTrue(any('basis, duty state and hours' in f for f in v['findings']))

    def test_simulated_hours_do_not_count(self):
        v = broken(lambda r: r['duty_entries'][0].update(label='simulated'))
        self.assertTrue(any('measured entries at class temperature show 0' in f for f in v['findings']))

    def test_survival_hours_are_not_operating_hours(self):
        v = broken(lambda r: r['duty_entries'][0].update(state='survival'))
        self.assertFalse(v['conformant'])

    def test_claim_cannot_exceed_measured_hours(self):
        v = broken(lambda r: r['conclusion'].update(hours=2000))
        self.assertTrue(any('claims 2000 h' in f for f in v['findings']))

    def test_long_transient_is_not_a_transient(self):
        v = broken(lambda r: r['duty_entries'][2].update(hours=30))
        self.assertTrue(any('sustained duty' in f for f in v['findings']))

    def test_quench_must_be_measured_and_large_enough(self):
        v = broken(lambda r: r['duty_entries'][2].update(cooldown_k=200))
        self.assertTrue(any('cool-down of at least 350 K' in f for f in v['findings']))

    def test_prediction_after_the_test_started_is_rejected(self):
        v = broken(lambda r: r['prediction'].update(timestamp_utc='2027-06-02T00:00:00Z'))
        self.assertTrue(any('precede the test start' in f for f in v['findings']))

    def test_unpredicted_test_is_allowed_when_marked(self):
        v = broken(lambda r: r.update(prediction={'registered': False, 'mark': 'no registered prediction'}))
        self.assertTrue(v['conformant'])

    def test_raw_data_needs_a_hash_and_deviations_a_disposition(self):
        self.assertFalse(broken(lambda r: r['raw_data'][0].update(sha256='abc'))['conformant'])
        self.assertFalse(broken(lambda r: r['deviations'][0].update(disposition=''))['conformant'])

    def test_expired_calibration_is_rejected(self):
        self.assertFalse(broken(lambda r: r['calibration'][0].update(valid_until='2027-01-01'))['conformant'])

    def test_class_temperature_must_be_reached(self):
        v = broken(lambda r: r['duty_entries'][0].update(temperature_c=440))
        self.assertFalse(v['conformant'])


if __name__ == '__main__':
    unittest.main()
