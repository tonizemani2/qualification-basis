"""Check a witnessed record against the qualification basis v1.0. Standard library only.

    python3 record_validator.py examples/record-450-W.json

Prints the verdict and every finding. The schema (record-schema.json) fixes the
structure; the rules below are the parts a schema cannot express.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABELS = {'measured', 'vendor-stated', 'simulated', 'assumption', 'unknown'}
CLASSES = {'375': 375.0, '450': 450.0, '500': 500.0}
CLASS_HOURS, CLASS_CYCLES = 500.0, 10
STATES = {'operating', 'survival', 'transient'}
BASES = {'formation', 'fluid at the component', 'component body'}
SHA = re.compile(r'^[0-9a-f]{64}$')
REQUIRED = ('record_id', 'date', 'subject', 'duty_class', 'qualifier', 'witness', 'prediction',
            'duty_entries', 'calibration', 'raw_data', 'deviations', 'teardown', 'conclusion')


def findings(record):
    out = []
    for key in REQUIRED:
        if key not in record:
            out.append(f'missing field: {key}')
    if out:
        return out
    match = re.fullmatch(r'(375|450|500)-(W|I)(/\d+h)?', record['duty_class'])
    if not match:
        return [f"duty_class {record['duty_class']!r} is not of the form 450-W or 375-I/2000h"]
    class_t = CLASSES[match.group(1)]

    # duty-basis rule: basis, state, hours, label on every entry
    measured_hours, measured_cycles, measured_quench = 0.0, 0, 0.0
    for i, e in enumerate(record['duty_entries']):
        where = f'duty_entries[{i}]'
        for key in ('temperature_c', 'basis', 'state', 'hours', 'label'):
            if key not in e:
                out.append(f'{where}: no {key}: a temperature needs basis, duty state and hours')
        if e.get('label') not in LABELS:
            out.append(f'{where}: label must be one of {sorted(LABELS)}')
        if e.get('state') not in STATES:
            out.append(f'{where}: state must be one of {sorted(STATES)}')
        if e.get('basis') not in BASES:
            out.append(f'{where}: basis must be one of {sorted(BASES)}')
        if e.get('state') == 'transient' and e.get('hours', 0) > 6:
            out.append(f'{where}: a transient longer than 6 h is sustained duty; state it as such')
        if e.get('label') == 'measured' and e.get('temperature_c', 0) >= class_t:
            if e.get('state') == 'operating':
                measured_hours += e.get('hours', 0)
            measured_cycles += e.get('cycles', 0) if e.get('state') in ('operating', 'survival') else 0
        if e.get('label') == 'measured' and e.get('state') == 'transient':
            measured_quench = max(measured_quench, e.get('cooldown_k', 0.0))

    # witness independence
    w, q = record['witness'], record['qualifier']
    if not w.get('name') or not w.get('organisation'):
        out.append('witness: name and organisation required')
    elif w['organisation'].strip().lower() == q.get('organisation', '').strip().lower():
        out.append('witness: must come from an organisation other than the qualifier')
    if not w.get('signed'):
        out.append('witness: conclusion not signed')

    # prediction before test
    p = record['prediction']
    if p.get('registered'):
        if not SHA.match(p.get('sha256', '')):
            out.append('prediction: registered but no SHA-256')
        if not p.get('timestamp_utc') or p['timestamp_utc'] >= record.get('test_start_utc', ''):
            out.append('prediction: time-stamp must precede the test start')
    elif p.get('mark') != 'no registered prediction':
        out.append('prediction: either registered with hash and time-stamp, or marked "no registered prediction"')

    # evidence
    for i, c in enumerate(record['calibration']):
        if not c.get('instrument') or not c.get('certificate') or not c.get('valid_until'):
            out.append(f'calibration[{i}]: instrument, certificate and validity required')
        elif c['valid_until'] < record['date']:
            out.append(f'calibration[{i}]: certificate expired before the record date')
    if not record['calibration']:
        out.append('calibration: at least one reference instrument')
    if not record['raw_data']:
        out.append('raw_data: at least one file')
    for i, r in enumerate(record['raw_data']):
        if not SHA.match(r.get('sha256', '')):
            out.append(f'raw_data[{i}]: SHA-256 required')
    for i, d in enumerate(record['deviations']):
        if not d.get('disposition'):
            out.append(f'deviations[{i}]: every deviation needs a disposition')
    if not record['teardown'].get('performed') and not record['teardown'].get('reason_not_performed'):
        out.append('teardown: performed, or the reason it was not')

    # claim bound
    c = record['conclusion']
    if c.get('label') != 'measured':
        out.append('conclusion: a claim must rest on measured entries; analysis alone does not qualify hardware')
    if c.get('duty_state') == 'operating':
        if c.get('hours', 0) > measured_hours:
            out.append(f"conclusion: claims {c.get('hours')} h operating, measured entries at class temperature show {measured_hours} h")
        if measured_hours < CLASS_HOURS:
            out.append(f'conclusion: class needs {CLASS_HOURS:.0f} h operating at {class_t:.0f} C; measured {measured_hours} h')
    if c.get('cycles', 0) > measured_cycles:
        out.append(f"conclusion: claims {c.get('cycles')} cycles, measured {measured_cycles}")
    if measured_cycles < CLASS_CYCLES:
        out.append(f'conclusion: class needs {CLASS_CYCLES} cycles; measured {measured_cycles}')
    if measured_quench < class_t - 100.0:
        out.append(f'conclusion: class needs one measured cool-down of at least {class_t - 100:.0f} K; largest measured {measured_quench} K')
    return out


def judge(record):
    found = findings(record)
    return {'record_id': record.get('record_id'), 'conformant': not found, 'findings': found}


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'examples/record-450-W.json'
    verdict = judge(json.loads(path.read_text()))
    print(json.dumps(verdict, indent=1))
    return 0 if verdict['conformant'] else 1


if __name__ == '__main__':
    sys.exit(main())
