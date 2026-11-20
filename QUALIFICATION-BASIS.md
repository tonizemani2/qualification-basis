# Qualification basis for wells and instruments above 375 °C, v1.0

20 November 2026 · open for comment · CC BY 4.0 · not a standard, not an
accreditation, not a certificate scheme. A proposed common language for
saying what a superhot well component or downhole instrument has been shown
to do, written so that a test run in one laboratory can be read, checked and
compared in another.

## 1. Why

Superhot wells are defined by the funding programmes as hotter than 375 °C
and above 22 MPa. The protocols in use were written for other duty:
ISO/TS 12835:2022 qualifies casing *connections* for thermal-recovery wells
cycling to "180 °C to 350 °C or above" and defines no duty classes for
375 to 500 °C wells and nothing for instruments; IEEE Std 323 gives the
qualification mechanics (margin, ageing, independence) for another industry.
Published reviews of supercritical wells record the same failures again:
casing collapse and connection breaks after heat-up and quench, cement that
does not support the pipe, instruments rated by a temperature with no hours
attached. Eight public awards of November 2026 fund new well materials and
test facilities; they will need to report results in a comparable form.

## 2. The duty-basis rule

**No temperature is stated without its basis, its duty state and its hours.**

- *Basis:* formation · fluid at the component · component body.
- *Duty state:* `operating` (performs its function) · `survival` (not
  damaged, function not required) · `transient` (a named event, with rate).
- *Hours* at that state, and the *number of cycles* between named states.

"450 °C rated" without the three is non-conformant language under this basis.
A momentary exposure is never reported as sustained duty. A survival result
is never reported as operating duty.

## 3. Duty classes

A class is a minimum envelope. A record states the class it was tested to and
any margin beyond it.

| Class | Sustained temperature (basis: fluid at the component) | Pressure | Endurance at temperature | Thermal cycles | Quench transient |
|---|---|---|---|---|---|
| **375** | 375 °C | ≥ 22 MPa | 500 h | 10 cycles 375 ↔ 100 °C | one cool-down of ≥ 250 K in ≤ 6 h |
| **450** | 450 °C | ≥ 22 MPa (30 MPa option) | 500 h | 10 cycles 450 ↔ 100 °C | one cool-down of ≥ 350 K in ≤ 6 h |
| **500** | 500 °C | ≥ 22 MPa (30 MPa option) | 500 h | 10 cycles 500 ↔ 100 °C | one cool-down of ≥ 400 K in ≤ 6 h |

Subject suffix: **W** well-construction hardware (casing, connection, cement,
liner, seal; as an assembly, never as loose parts) · **I** downhole
instruments (anything that reports a measurement). Example: `450-W`, `375-I`.

Endurance extensions are written `450-W/2000h`. Fluid class is stated
separately: `dry` (inert gas or air), `steam`, `brine` (composition given),
`acid gas` (HCl / H₂S partial pressures given).

All values are proposed (`assumption`): they are the envelopes the public
superhot programmes name, not demonstrated limits. They become demonstrated
for a subject only when a record under §6 exists.

## 4. Test methods

| Method | Purpose | Minimum evidence |
|---|---|---|
| **M1 isothermal endurance** | function held for the class hours at the class temperature | continuous temperature record at the subject from calibrated references; function measured at start, every 100 h and end |
| **M2 thermal cycling** | damage per cycle | every cycle's rate and extremes recorded; inspection or function check after cycles 1, 3 and 10 |
| **M3 quench** | the event that breaks superhot wells | cool-down rate at the subject measured, not inferred from the fluid; post-quench inspection |
| **M4 combined environment** | temperature with pressure and fluid | fluid composition before and after; pressure record |
| **M5 assembly test** (W) | casing, cement and connection together, axially restrained | restraint stiffness stated; axial load or strain measured; leak rate across the connection |
| **M6 accuracy under duty** (I) | the instrument's error while at duty, not before and after | reference instrument traceable and independent of the subject; error at every checkpoint; drift over the endurance hours |
| **M7 teardown** | what failed and why | sectioning or inspection record with photographs; failure attributed or stated as not attributed |

Pre-conditioning: the subject is cycled (M2, three cycles) before the
endurance hours start, so that endurance tests the aged condition.

**Instruments (I):** the stated accuracy is the largest error against the
reference at any checkpoint while at duty. An accuracy measured only at room
temperature before and after is a survival result.

**Well hardware (W):** a result on a free, unrestrained specimen is a
material result, not an assembly result. The constrained state is the duty.

## 5. Prediction before test

Before the test starts the qualifier records, hashes and time-stamps what the
subject is expected to do: the measured quantities, their predicted values or
bands, and the result that would count as failure. The record carries the hash
and the time-stamp. A test without a prior prediction can still be a valid
survival record; it is marked `no registered prediction`.

## 6. The witnessed record

A qualification claim under this basis exists only as a record
(`record-schema.json`, checked by `record_validator.py`) containing:

1. subject identification, drawing or build revision, material certificates;
2. the duty class claimed and every duty-state entry with basis, state, hours,
   cycles and a label;
3. the registered prediction (§5) or the mark that there was none;
4. calibration certificates of every reference instrument;
5. raw data files with their SHA-256 (temperatures at ≥ 1 sample per minute,
   pressures, the function measurement, the environment);
6. the deviation log: every departure from the approved procedure; a silent
   deviation voids the record;
7. the teardown report (M7);
8. the **witness**: a named person from an organisation other than the
   qualifier, who was present or reviewed the raw data, and who signs the
   envelope conclusion;
9. the conclusion in pinned form:
   `qualified: (class, duty state, hours, cycles, fluid class, pressure)`.

Every number in the record carries one label: `measured`, `vendor-stated`,
`simulated`, `assumption` or `unknown`. A simulated number can describe a
test; it cannot be the claim. Analysis alone does not qualify hardware.

**Claim bound.** The conclusion cannot exceed what the duty-state entries
labelled `measured` show: not hotter, not longer, not more cycles.

## 7. What this basis does not do

It sets no acceptance values for leak rate, accuracy or strain: those belong
to the buyer's specification. It does not certify laboratories (ISO/IEC 17025
does). It does not predict service life: a life claim beyond the tested hours
needs a stated damage model, its parameters measured on the subject, a
validation test and a margin, and is marked as extrapolation.

## 8. Open problem, published with the basis

A one-dimensional thermoelastic-plastic casing model with parameters fixed in
advance (`benchmark/`) was compared once with the published IDDP-1 and IDDP-2
casing failures. It fails both wells, and it also fails a fully cemented
320 °C well under the same quench: **it cannot separate the failed superhot
wells from conventional wells that stay in service.** See
`BENCHMARK-RESULT.md`. The basis therefore makes no claim that a simple model
predicts where a superhot well breaks. The duty classes rest on the published
envelopes, not on that model.

## 9. Comment

Comments are logged with their author's name in a later revision. Wanted
most: values for the quench transient from operators who have measured one;
the restraint stiffness that represents a cemented casing (M5); reference
instruments usable at 450 to 500 °C for M6.

| Rev | Date | Change |
|---|---|---|
| 1.0 | 2026-11-20 | First public issue: classes 375 / 450 / 500, methods M1 to M7, record contract, open benchmark problem |
