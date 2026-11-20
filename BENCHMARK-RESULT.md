# Thermoelastic benchmark against IDDP-1 and IDDP-2: result, run once

20 November 2026 · `[MODEL]` · parameters and comparison rule fixed and
time-stamped before the run (`PLAN.md`). Reproduce:
`python3 benchmark/run_benchmark.py`.

## Result: the benchmark claim is **not made**

| | Comparison | Result |
|---|---|---|
| B1 | onset of connection failure on quench against IDDP-1's reported heating | model onset: heating of **224 K** above cement set (peak 304 °C). Within 15 % of the reported lower bound (200 K, "<100 °C … to >300 °C"); 39 % below the 370 K implied by 450 °C fluid. The model fails IDDP-1 at its inputs. **Pass, weakly**; the source gives bounds, not an onset |
| B2 | shallowest failed depth against "below ~1600 m" | the model fails connections over the **whole cemented column**, not only the unsupported interval below 1,490 m. **Fail** |
| B3 | IDDP-2 unsupported section buckles on heat-up | **Pass** |
| B4 | no intact-class well fails under the same event | 240 °C: intact (tension use 0.49). 280 °C: intact (0.81). **320 °C: fails (1.13).** **Fail** |
| B5 | ±10 % on connection efficiency, yield derating, cement-set temperature | onset moves 212 to 237 K; the 320 °C well fails in all six variations |
| B6 | 30 days, 10-minute steps, 100 nodes | under 5 s. Pass |

## What it means

A constrained, cemented K55 string heated more than about 224 K above its
cement-set temperature and then quenched to 30 °C reaches the tensile limit
of its connections in this model. That is true at 450 °C, and also at 320 °C.
Conventional high-temperature wells are in service at 320 °C. So either they
are not quenched this way, or their connections and cement give what the
model holds rigid, or yield derating and connection strength differ from the
handbook values used. The model cannot say which, and no parameter was moved
to find out.

**Open problem, stated plainly:** with public data, a one-dimensional
thermoelastic model does not separate the superhot wells that broke from the
hot wells that did not. Separating them needs at least one of: a measured
cool-down history at the casing of an intact well; the axial compliance of a
real cemented interval; connection tensile strength at temperature after
compressive yielding. These are the measurements the duty classes ask for
(methods M3 and M5).

## Limits

One dimension; no radial or hoop stress, no cement failure model, no creep,
no corrosion. IDDP inputs are from two review papers (Kibikas et al.,
Stanford Geothermal Workshop 2026; Friðleifsson et al., World Geothermal
Congress 2020), not from the well files. The intact class is a class, not a
named well.
