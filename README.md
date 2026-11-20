# Qualification basis for wells and instruments above 375 °C, v1.0

Superhot geothermal wells (above 375 °C and 22 MPa) have no shared way of
saying what a casing assembly or a downhole instrument has been shown to do.
This repository proposes one, small enough to read in ten minutes and strict
enough to check by machine.

| File | What |
|---|---|
| `QUALIFICATION-BASIS.md` | duty classes **375 / 450 / 500** for well hardware (W) and instruments (I), test methods M1 to M7, the witnessed-record contract |
| `record-schema.json`, `record_validator.py` | the record format and the checker for the rules a schema cannot express: basis-state-hours on every temperature, witness independence, prediction before test, claim bound |
| `examples/record-450-W.json` | a synthetic record that passes |
| `benchmark/` | an open thermoelastic-plastic casing model and its one comparison with the IDDP-1 and IDDP-2 failures |
| `BENCHMARK-RESULT.md` | the result: **the model does not separate failed superhot wells from intact 320 °C wells.** Published as an open problem |

    python3 record_validator.py examples/record-450-W.json
    python3 benchmark/run_benchmark.py
    python3 -m unittest test_record_validator
    (cd benchmark && python3 -m unittest test_thermoelastic)

Python standard library only.

## The one rule

No temperature without its **basis**, its **duty state** and its **hours**.
"Rated 450 °C" says nothing; "operating, 500 h, 450 °C fluid at the component,
10 cycles, witnessed" says what was shown.

## Status

A proposal for comment. Every class value is the envelope public superhot
programmes name, labelled `assumption` until a witnessed record exists. No
record under this basis exists yet. Comments from laboratories and operators
are logged by name in the next revision.

## Related

Release 1, the open forecast and audit record for Project Red, scored every
month: https://github.com/tonizemani2/forecast-audit
(DOI [10.5281/zenodo.24396505](https://doi.org/10.5281/zenodo.24396505)).

Zemanium: https://zemanium.com

## Citation

See `CITATION.cff`, or use the "Cite this repository" button on GitHub.

## Licence

Code: MIT. Text and schema: CC BY 4.0. Details in `LICENSE`.
