# Qualification basis v1.0 and thermoelastic benchmark: plan, fixed parameters, comparison rule

20 November 2026 · frozen before the benchmark was run on any well case.
Labels: `measured` /
`vendor-stated` / `[MODEL]` / `SIMULATED` / `assumption` / `TBD`.

## 1. What ships

1. `QUALIFICATION-BASIS.md` v1.0: duty classes 375 / 450 / 500 °C for well
   construction hardware and for downhole instruments, test methods, the
   witnessed-record contract. Open, CC BY 4.0.
2. `record-schema.json` and `record_validator.py`: the record format and its
   checker, with example records.
3. `benchmark/`: an open one-dimensional thermoelastic-plastic model of a
   cased, cemented well through heat-up, production and quench, standard
   library only, with the well cases below.

The release contains no instrument design and no well operating or control
method.

## 2. Benchmark physics (fixed)

Per depth node, casing axial direction. Cemented node: total mechanical strain
held (`ε = 0` after cement set at `T_set`), elastic-perfectly-plastic steel
with temperature-dependent modulus and yield:
`σ = E(T)·(−α(T − T_set) − ε_p)`, return-mapped to `|σ| ≤ σ_y(T)`.
Connection in tension fails when `σ ≥ η·σ_y(T)` (`η` = connection tensile
efficiency). Unsupported interval of length `L_u` between cemented ends:
Euler buckling when thermal compressive strain exceeds
`π² r_g² / (0.5·L_u)²` (fixed ends), flagged `buckled`.
Casing temperature follows the fluid history with a first-order lag.

## 3. Parameters, fixed before any case is run (`assumption` unless sourced)

| Quantity | Value |
|---|---|
| `α` | 12.5 × 10⁻⁶ /K |
| `E(T)` | 200 GPa × (1 − 4 × 10⁻⁴·(T − 20)) |
| yield at 20 °C | K55 379 MPa, L80 552 MPa (API 5CT minimums) |
| yield derating | linear to 0.80 at 400 °C, continued at the same slope |
| connection tensile efficiency `η` | 0.85 |
| cement set temperature `T_set` | 80 °C |
| quench end temperature | 30 °C |
| thermal lag of the casing | 2 h |
| radius of gyration, 13 3/8-inch casing | 0.117 m; 9 5/8-inch 0.083 m |

## 4. Cases (inputs fixed here; sources read 2026-11-20)

| Case | Inputs | Published outcome |
|---|---|---|
| IDDP-1 (Krafla) | K55; heated to 450 °C (fluid temperature while flowing, WGC 2020 paper 37000); rapid cooling after surface valve failure; unsupported below 1,490 m (Kibikas et al., SGW 2026) | "multiple breaks below ~1600 m in intervals that were either uncemented below ~1490 m or only poorly supported", after heating "from <100 °C during cementing to >300 °C during recovery and then cooled again during quenching" |
| IDDP-2 (Reykjanes) | L80; 426 °C measured; unsupported section of 100 m below 2,300 m | during early recovery the uncemented section "experienced sufficient thermally-induced stress and buckling that the casing collapsed" |
| Intact class | K55, fully cemented, heated to 240, 280 and 320 °C, **same quench to 30 °C** | conventional high-temperature wells in service (class, not a named well) |

## 5. Comparison, run once

- **B1 onset ΔT.** Model onset of connection tensile failure on quench,
  expressed as heating ΔT above `T_set`, against IDDP-1's reported heating
  (lower bound 200 K from "<100 → >300 °C"; 370 K from 450 °C). Pass: the
  model fails IDDP-1 at its inputs **and** its onset ΔT is within ±15 % of a
  reported value. The source gives bounds, not an onset; that limit is stated
  with the result.
- **B2 depth.** Shallowest node the model fails in IDDP-1 against 1,600 m,
  within ±15 %. Stated limit: depth follows the cement-support input.
- **B3 IDDP-2.** The unsupported section buckles during heat-up.
- **B4 separation.** No intact-class case fails under the same event. If any
  does, the benchmark cannot separate failed from intact wells without
  tuning: that is published as an open problem and the basis ships without a
  benchmark claim.
- **B5 robustness.** B4 repeated with each of `η`, the derating end value and
  `T_set` moved by ±10 %. Reported, not a gate.
- **B6 speed.** A 30-day history at 10-minute steps on 100 nodes in under 5 s.

Nothing is re-run with changed parameters to obtain a pass.

## 6. Verification before the comparison

Exact checks: elastic constrained bar `σ = −EαΔT`; residual tension after a
heat-cool cycle beyond yield equals `E·(αΔT − σ_y,hot/E)` capped at yield;
plastic shakedown (no new plastic strain on the second identical cycle when
the cycle is inside twice yield); Euler strain for a pinned-pinned column
with the stated length factor; lag response against the analytic exponential.

## 7. Release checks

One command (`python3 run_benchmark.py`) from a clean copy outside the
repository, standard library only; unit tests green.
