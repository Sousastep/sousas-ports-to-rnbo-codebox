# Validation

## Latest batch: 15 additional effects

All requested artifacts are present in `RNBO/` with exact source basenames and
`.txt` extensions (Chmahastic replaces `.jsfx` with `.txt`). Sources are untouched.
The RNBO reference, examples 1–16, this guide and all three original tools were
read before implementation. New source-driven JSFX tooling is described below.

Executed on the final delivered arithmetic:

- `node tools/check_rnbo.cjs --semantic`: **26/26 pass**, including the original
  11 and all 15 new scripts, with the installed RNBO 1.4.5 grammar and
  name/operator checker. This is not full DSP code generation/typechecking.
- `python3 tools/test_ports.py`: **648 Airwindows comparisons pass** (18 effects
  × 3 rates × 3 vectors × 4 configurations), including **324 new comparisons**.
  Rates: 44100/48000/96000 Hz; vectors: 1/64/256. Each case uses 16384 samples
  (TakeCare 65536), silence, impulses, composite tones, overload and parameter
  changes at sample 8192. Existing Inflator/BandbAss checks also pass.
- Measured maximum absolute errors in the new Airwindows cases:
  TapeHack2, ToTape9, VerbTiny, VerbThic, ButterComp2, PurestSquish, ChannelX and
  ZOutputStage: **0** in this local C++ harness; Ultralight2: **2.38419e−7**.
  Acceptance tolerances are 2e−10 except Ultralight2 (2e−5), whose original
  float intermediates/fused multiply-add differ from RNBO's arithmetic.
  These results do not imply bit-exact Max output.
- `python3 tools/test_jsfx_ports.py`: **486 safety/smoke cases pass** (6 effects
  × 3 rates × 3 vectors × 9 control cases). Includes all-min/all-max, all seven
  GoldComp4 oversampling modes, Sky lookahead, Wob-Wob pattern buttons, LR4
  numerical modes and silence following audio. Zero-output endpoint settings
  are permitted, not mistaken for failures.
- Independent equation comparisons pass for **18 LR4 configurations**, GateIQ
  at **3 rates**, and Wob-Wob's one-button pattern curve/cookbook filter.
  Additional checks pass for GateIQ active mono/stereo bypass, crossover HP
  outlets, GoldComp4 dry mix/automation/rate restart, Sky lookahead changes/rate
  restart, and Chmahastic's impulse tail/predelay changes.
- Both C++ harnesses use bounds-checked fixed arrays, Clang C++17,
  AddressSanitizer and UndefinedBehaviorSanitizer. No sanitizer failures.
  Airwindows compilation emits 12 unused-expression warnings from unchanged
  VariMu/ButterComp2/PurestSquish references. JSFX compilation emits six
  redundant-parentheses warnings. No warning suppressions are used.

### Accommodations and limits for this batch

- Reference RNG seeds match the ports. ButterComp2's legacy signed-overflow
  residue noise is omitted in reference and port, as previously done for VariMu.
- ToTape9 preserves float32 rounding of `H*H`; Ultralight2 preserves float32
  delay arrays and scalar assignment rounding. RNBO lacks `fma`; multiplication
  plus addition is used. C++ long doubles become RNBO numbers.
- JSFX namespace functions are specialized per instance by `tools/port_jsfx.py`;
  this retains separate detector/oversampler/filter histories. The generator
  removes graphical/host-only code and adds explicit EEL division/silence guards.
  RAM indices truncate to integers as in EEL. Chmahastic delay regions are
  enlarged to avoid the source's right-hand line overlaps (intentional fix).
- JSFX smoke tests are **not full REAPER/EEL null tests**. GoldComp4, Sky and
  Chmahastic have not been compared sample-by-sample against an EEL engine.
  Chmahastic uses RNBO random rather than REAPER's RNG.
- No Max paste/compile, export, playback or listening test has been performed;
  the user will run those manually. Parser and arithmetic checks cannot prove
  downstream RNBO type inference, generated precision, CPU cost or sound.
  Large generated JSFX scripts especially need that final Max check.
- No performance claims or resource benchmarks are made. Sky lookahead scans
  buffers at sample rate. Exact source quirks, supported interfaces and memory
  adaptations are listed in README.md.

### Reproduce the latest batch

```bash
python3 tools/port_airwindows.py TapeHack2 ToTape9 VerbTiny VerbThic Ultralight2 ButterComp2 PurestSquish ChannelX ZOutputStage
python3 tools/port_jsfx.py
node tools/check_rnbo.cjs --semantic
python3 tools/test_ports.py
python3 tools/test_jsfx_ports.py
```

## Previous batch (historical results)

## Checks executed on the final ports

- `node tools/check_rnbo.cjs --semantic`: **11/11 pass** using the expression
  grammar and semantic/name/operator parser from installed **RNBO 1.4.5**.
  These checks caught and corrected boolean state defaults, unsupported Int
  function return annotations and a nonconstant `const` declaration.
- `python3 tools/test_ports.py`: **pass**. The harness translates the arithmetic
  in the delivered `.txt` files into C++ (with bounds-checked fixed arrays) and
  compares it to the checked-in Airwindows `processDoubleReplacing` routines.
  Compiled with Clang C++17, AddressSanitizer and UndefinedBehaviorSanitizer.
- **324 Airwindows comparisons**: 9 effects × 3 sample rates (44100, 48000,
  96000 Hz) × 3 vector sizes (1, 64, 256) × 4 initial control configurations
  (defaults, all zero, all one, mixed). Parameter changes at sample 8192 also
  exercise vector-boundary coefficient updates and the original parameter ramps.
  Inputs include silence, stereo impulses, composite tones and overloads.
  Each comparison uses 16384 samples; TakeCare uses 65536 to exercise its delay
  network. Maximum permitted absolute error is `2e-10`; all cases pass.
- **36 independent Inflator equation comparisons**, covering band split,
  clipping, curve endpoints/center, and effect 0/50/100 with non-unity gains.
  Tolerance `1e-12`; all pass.
- Both JSFX ports pass finite-output smoke tests at all 3 rates/vector sizes.
  Additional tests verify Inflator's partial bypass, BandbAss channel-four auto
  detection/disable, parameter changes, stereo operation and five-second sleep.

Reference-harness accommodations are explicit: RNG seeds are matched; ADClip9
lastDry is initialized; X2Buss arrays are enlarged; VariMu legacy residue noise
is omitted. These are the same deviations documented in README.md. PaulWide
preserves float32 rounding of its scale factor through a FixedFloat32Array;
otherwise its quantizer can diverge by a whole step at boundary samples.

The test compile emits four unused-expression warnings from the **unchanged
VariMu reference** pointer-increment statements. No suppressions are applied.
No sanitizer failures were reported.

## Limits

These are **not full Max codebox~ compilation, export or listening results**.
The RNBO parser checks syntax, symbols and operators; it does not prove all
later code-generation/type-inference stages. The C++ harness verifies delivered
DSP arithmetic, not RNBO's generated code or Max's host behavior. No claim of
bit-exactness across RNBO precision modes, CPU speed, or subjective sound is made.

BandbAss has not been run in an EEL/REAPER reference engine for sample-by-sample
comparison. Its active filter/envelope/compressor equations were ported and
reviewed against the source; behavioral/silence tests are not a full EEL null test.

Follow README.md's manual Max checklist. If compilation fails, provide the
file name, RNBO version and exact console error/line so the target-specific
issue can be repaired.

## Reproduction

```bash
# Recreate all 18 Airwindows ports (original two JSFX ports are hand-written).
python3 tools/port_airwindows.py
# Set RNBO_DIR if Max/RNBO is installed elsewhere.
node tools/check_rnbo.cjs --semantic
python3 tools/test_ports.py
```

The tools use existing local Max/RNBO parser modules and the system C++ compiler;
no new dependencies or changes to the Max installation are required.
