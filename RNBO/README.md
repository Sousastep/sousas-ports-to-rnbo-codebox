# RNBO codebox~ ports

Paste the **entire contents of one `.txt` file** into one `codebox~` object
inside `rnbo~`. These are RNBO scripts, not Gen codebox or Max JavaScript.
All files use `in1`/`in2` and `out1`/`out2` for stereo audio.
BandbAss additionally uses `in3` (kick) and `in4` (optional second sidechain).
Wob-Wob additionally uses **in3 for continuous beat position in quarter notes**.
The LR4 filter has **four outlets**: in crossover mode out1/out2 are LP and
out3/out4 are HP. No external buffers, imports, or additional RNBO objects are needed.

Parameters are declared at the top of each file with their defaults. Send
messages such as `p_density 0.4`, `p_thresh 0.5`, or `effect 80` to the
codebox inlet, or use the corresponding exposed RNBO parameters in your patch.
Airwindows parameters retain **normalized 0–1 VST values**, not display units.
JSFX parameters retain their original slider units. The six new mrelwood ports
use the original names `sliderN`; send e.g. `slider5 -24` to GoldComp4.
Their coefficient setup runs on control changes at vector boundaries. Parameter/coefficient
updates happen once per RNBO signal vector; states persist across vectors.
Turning DSP off/on resets the vector cursor, not the effect history.

| File | Named controls (in original order) |
| --- | --- |
| `mrelwood_BandbAss.txt` | `crossover`, `threshold_kick`, `threshold_bass`, `attack`, `hold`, `release`, `depth`, `stereo`, `channel4`, `link_thresholds` |
| `RCInflator2_Ideal.txt` | `input_db`, `effect`, `curve`, `clip`, `band_split`, `effect_in`, `output_db` |
| `ClipOnly3.txt` | none |
| `ADClip9.txt` | `p_boost`, `p_match`, `p_noise`, `p_ceiling`, `p_mode` |
| `PaulWide.txt` | `p_quant`, `p_derez` |
| `Dynamics3.txt` | `p_thresh`, `p_attack`, `p_release`, `p_invwet` |
| `VariMu.txt` | `p_intensty`, `p_speed`, `p_output`, `p_drywet` |
| `Density3.txt` | `p_density`, `p_highpas`, `p_output`, `p_drywet` |
| `ZAcidLowpass.txt` | `p_cutoff`, `p_over`, `p_under`, `p_meltdwn`, `p_drive`, `p_output` |
| `X2Buss.txt` | `p_high`, `p_hmid`, `p_lmid`, `p_bass`, `p_highf`, `p_hmidf`, `p_lmidf`, `p_bassf`, `p_thresh`, `p_fader` |
| `TakeCare.txt` | `p_speed`, `p_rando`, `p_depth`, `p_regen`, `p_derez`, `p_buffer`, `p_output`, `p_drywet` |

## Generate test patchers with Max v8.codebox

`generate_test_patchers.js` is a **Max JavaScript** script, not RNBO DSP code.

1. Edit `SOURCE_DIRECTORY` at the top to your absolute `RNBO/` directory.
   POSIX paths or Max-style `Macintosh HD:/...` paths work; retain quotes.
2. Paste the whole script into **v8.codebox** in a normal Max patch.
3. Send **bang** (or `generate`). It scans that directory nonrecursively for
   `.txt` files, alphabetically, and creates one `rnbo~ @autobuild 0
   @annotation_name <filename-without-extension>` per effect in the same patch.
4. Double-click an effect's rnbo~. It contains an **empty** codebox~ (RNBO
   does not expose `code` as a writable attribute through the v8 engine),
   numbered `in~`/`out~` connections, and one `number → setparam → codebox~`
   chain per `@param`. Numbers use **Decimal (Floating-Point)**
   (`format 6`, RNBO `initialFormat float`) so fractional values are supported.    Literal defaults are sent once on patch load by a `loadmess <default>`
   object connected into each number box; computed defaults get no loadmess and
   their number boxes are not initialized. Paste the
   matching `.txt` file's entire contents into each codebox~ yourself before
   using the effect (see the instructions at the top of this README).
5. Inspect the patch and **build manually**: autobuild stays off. Connect your
   own test signals and monitoring outside the generated effects. No DAC or
   automatic DSP startup is created. Save the parent patch manually to retain
   the embedded effects.

Host objects are laid out below existing objects in three columns. Each effect
has signal I/O around a left-side codebox and a four-column parameter grid on
its right. Large control counts require scrolling (Wob-Wob has 60 controls).
`cancel` stops the batch and removes only the unfinished effect. Completed
objects remain. Re-running skips existing `rnbo_test_<effect>` scripting names;
remove or rename a generated host yourself if you want it recreated. The script
clears objects from a newly created RNBO default template, not existing patches.

Progress and failures are printed to the console and sent from the script's
outlet. A failed effect's partial host is removed and the batch continues.The `done created skipped failed` message summarizes the run. Generated
codebox~ boxes are left empty by design; the script never attempts the
unsupported v8 `code` attribute, so there is no embedded-source readback
guarantee — paste and compile manually. Codebox parsing errors may still be
reported separately by Max.

The script needs Max 9's v8 engine and RNBO. It uses native Max File/Folder/Task
APIs; no Node for Max, dependencies, output directory or file writes. UTF-8 is
decoded within the script, without requiring `TextDecoder` (unavailable in some
Max v8 versions). Unicode notices are preserved; invalid UTF-8 is reported.
Parameter
and I/O discovery ignores comments/quoted strings and accepts the declarations
in all 26 checked-in ports. List ports are deliberately rejected because this
is a signal-effect generator. This is metadata discovery, not a DSP compiler.

Verification: `node --check RNBO/generate_test_patchers.js` and
`node tools/test_generate_test_patchers.cjs` pass. The latter drives the delivered
script's **bang interface** with a simulated Max API and actual `.txt` files,
verifying exact source embedding, counts, Decimal controls, connections, layout,
reruns, cancellation, default-template clearing and failure cleanup. It also tests
Unicode and invalid UTF-8 with `TextDecoder` absent from the runtime. **Actual
Max scripting/compilation has not been run.** In particular, verify your RNBO
version exposes `code` through Max's attribute API and that each number's
Inspector displays Decimal floating-point. Start with quiet monitoring.

## Additional 15 ports

| File | Controls (source order; original labels are also in each file) |
| --- | --- |
| `TapeHack2.txt` | `p_input`, `p_output`, `p_drywet` |
| `ToTape9.txt` | `p_input`, `p_tilt`, `p_shape`, `p_flutter`, `p_flutspd`, `p_bias`, `p_headbmp`, `p_headfrq`, `p_output` |
| `VerbTiny.txt`, `VerbThic.txt` | `p_replace`, `p_derez`, `p_filter`, `p_wider`, `p_drywet` |
| `Ultralight2.txt` | `p_damping`, `p_unsolid`, `p_unreflc`, `p_predlay`, `p_drywet`, `p_distnce` |
| `ButterComp2.txt` | `p_compress`, `p_output`, `p_drywet` |
| `PurestSquish.txt` | `p_squish`, `p_bassblm`, `p_output`, `p_drywet` |
| `ChannelX.txt` | `p_consoletype`, `p_drive`, `p_output` |
| `ZOutputStage.txt` | `p_input`, `p_output` |
| `mrelwood_GoldComp4.txt` | `slider2` L/R–M/S, `3` link, `4` side threshold offset, `5` threshold dB, `6` knee dB, `7` attack ms/12dB, `8` ratio, `9` release ms/12dB, `10` FET–opto, `11` oversampling 0–6, `12` RMS target, `13` output dB, `15` limiter, `16` detector HP Hz, `17` mix %, `20` tilt dB, `21` negative expansion ratio |
| `mrelwood_Sky_is_the_limit_3v2_BETA.txt` | `slider1` M/S, `2` link, `5` tilt dB, `6` punch, `7` saturation, `10` boost dB, `11` safe–soft, `51` lookahead, `53` pre-comp, `60` ceiling dB, `62` link threshold/volume |
| `mrelwood_DubStep_Wob-Wob.txt` | `slider1` min Hz, `2` max Hz, `3` offset beats, `4` steepness; `sliderstep1`…`sliderstep56` pattern buttons (0/1) |
| `mrelwood_Chmahastic_Reverb_2.txt` | `slider1` room %, `2` decay %, `3` dampen %, `4` predelay ms, `5` attack %, `6` LP kHz, `7/8` high-mid dB/Hz, `9/10` mid dB/Hz, `11/12` low-mid dB/Hz, `13` HP Hz, `14` width %, `15` mix %, `16` volume dB |
| `mrelwood_GateIQ.txt` | `slider1` threshold dB, `2` range dB, `4/5/6/7` hi/high-mid/low-mid/lo threshold offsets dB |
| `mrelwood_HP-LP_LR4_Filters.txt` | `slider2` poles selector, `3` frequency scale, `4` resonance dB, `5` LP invert, `6` HP invert, `8` mode (0 off/1 LP/2 HP/3 crossover), `20` output dB |

### Additional source quirks and adaptations

- GoldComp4 retains all 0/2x/4x/8x detector paths, including the source's
  independent subphase compressor histories and outer minimum-phase downsampling.
  It does **not** oversample the audio waveform. GUI/RMS display calculations
  and the read-only GR slider14 are omitted. RMS target slider12 controls the
  original calculated makeup gain, not a newly added RMS controller.
- GoldComp4's `attdb` is zero in the active source (its assignment is commented
  out); that source behavior is retained. Its wide tilt shelves, detector HP,
  negative expansion and post-mix limiter are retained.
- Sky retains its initially zero limiter histories. `slider53` and `slider62`
  exist in the original UI but do not affect the active audio equations; no new
  behavior is invented. Its shelf coefficient setup uses the source's stored
  sine/cosine values before refreshing them. Lookahead scans up to 256 cells
  per active detector per sample: check CPU in Max. Actual audio delay is
  **bufsz−1** samples, despite the source reporting 2×bufsz to REAPER; RNBO does
  not automatically communicate that REAPER latency metadata.
- Wob-Wob pattern slots 1–32 are spaced 1/32 of four beats; slots 33–56 use
  the source's subsequent 1/24 spacing. All default off, so enable e.g.
  `sliderstep1 1` and drive inlet 3 with a continuous beat ramp. There is no
  internal free-running tempo clock or REAPER pattern serialization.
- GateIQ intentionally sums the input to mono when active and applies each
  band's gain **twice**, matching the source. Threshold −96 bypasses in stereo.
  Read-only meter sliders 10–13 are omitted.
- LR4 preserves all six numerical pole-selector values, even though its source
  only labels four. Selector 3 uses **seven** cascaded biquads, not the labeled
  twelve poles. Selectors 4/5 use seven LP and four HP stages. No corrected
  textbook crossover is substituted. Off mode passes stereo at unity; only
  crossover mode updates the auxiliary HP outlets.
- Chmahastic retains the full 50-line, five-by-five feedback network, nonlinear
  feedback, undersampling/interpolation, input attack and all EQs. Its EEL RAM
  regions are enlarged to prevent the source's right-hand delays (8% longer)
  from overlapping adjacent lines; this deliberately repairs source memory
  aliasing rather than emulating it. RAM is 160000 doubles (~1.22 MiB).
  Predelay retains its 4800-sample ceiling and write/advance/read order (so
  positive delays are one sample shorter). Predelay changes clear its buffers.
  Its commented-out highpass variable stays zero; damping RNG uses RNBO random,
  not REAPER's implementation. GUI-only parameter bound arrays are omitted.
- EEL divide-by-zero behavior is explicitly emulated; detector logarithms use a
  1e−30 floor to avoid nonfinite silence states. Graphical interfaces, mouse
  interactions, meters, REAPER host metadata and serialization are not ported.
- Ultralight2 retains float32 delay storage and rounds float scalar assignments.
  RNBO has no C++ `fma`: ChannelX/Ultralight2 use multiply-plus-add. C++ long
  double intermediates become RNBO numbers. These are numerical, not topology,
  differences. ButterComp2's overflowing legacy residue-noise block is omitted
  as in VariMu; its compression is preserved.
- ZOutputStage has fixed 15.5 kHz filters: use sample rates **above 31 kHz**.
  ChannelX console selections are floor(`p_consoletype`×4.999), 0–4.

## Fidelity and source quirks

- Airwindows ports follow `processDoubleReplacing`, retaining the original
  signal path, update order, random-dependent clipping/dither algorithms,
  nonlinear polynomials, and vector-length parameter ramps where present.
  Output floating-point dither is disabled in that source path. Its active
  random updates and near-zero denormal noise remain (except VariMu below).
- Xorshift32 uses explicit unsigned wrapping and fixed seeds for reproducible
  tests. VST constructors choose random seeds, so separate instances will not
  null exactly unless their seeds are matched. PaulWide's audible dither and
  stereo decorrelation are preserved; this is not a conventional stereo widener.
- VariMu's legacy, roughly `1e-16` residue noise is omitted. It depended on
  overflowing signed C++ arithmetic and static state shared between instances.
  The compressor and alternating coefficient/speed histories are preserved.
- X2Buss source permits spacing up to 32 but allocates only 18 intermediate
  and 34 slew entries. The port allocates **33/65**, preventing out-of-bounds
  access. The source's forward shift order is intentionally not changed;
  its comments are not reliable latency specifications.
- ADClip9 source does not initialize `lastDryL/R`; the port initializes both
  to zero. `p_mode`: below `1/2.999` = Boost; below `2/2.999` = Match;
  otherwise ClipOnly (difference signal). `p_boost` and `p_match` map to 0–18 dB.
- ZAcidLowpass retains its fixed 15.5 kHz opamp filters. Use sample rates
  **above 31 kHz**; the original filter design is not valid below Nyquist.
- TakeCare retains all **18 × 32772 double delay cells** (~4.5 MiB), the
  unusual cross-channel feedback, signed wet output, modulation and variable
  buffer length. No simplified reverb is substituted. Its long initialization
  runs only on object creation, never at audio rate.
- BandbAss omits graphics, meter accumulation, mouse logic and unused legacy
  envelope functions. Default main mode is **Mono**; Stereo uses the left main
  detector for both channels. `channel4`: -1 disabled, 0 auto (default), 1 enabled.
  Auto detects over 100 nonzero sidechain-four samples and latches on at the
  next vector boundary; change `channel4` to reset the mode.
- BandbAss's `link_thresholds` explicitly links the bass threshold to the kick
  threshold. In JSFX linking exists only in mouse-drag code, not in the DSP;
  for independent threshold automation use `link_thresholds 0`.
  Division-by-zero cases are explicitly guarded for silence. The original
  zero-initialized compressor gains and five-second sleep behavior are retained.
  With no kick, its gain eventually returns to unity: the source does **not**
  implement the standalone compressor claimed in its description.
- Inflator's Effect In switch bypasses only the waveshaper, **not** input/output
  gains or input clipping. Band split uses the original 240/2400 Hz crossover.

## Manual Max checklist

1. Paste each file into a fresh RNBO `codebox~`; check the Max console and
   confirm compilation, inlet/outlet counts and parameter names.
2. Start with quiet test signals and a low monitor level. Check silence,
   left-only/right-only impulses, a bass sine, full-band music and overloads.
3. Compare against the original effects at matching controls and sample rates
   (44.1, 48 and 96 kHz). Test DSP restart and vector sizes 1, 64 and 256.
4. Exercise parameter endpoints and all switches. Test Inflator with band split
   on/off, BandbAss with kick/ch4 disconnected and connected, ADClip9's three
   modes, Dynamics3's inverted/wet control and PaulWide's 16/24-bit settings
   (`p_quant 0`/`1`). Density3 is unity-shaped at `p_density 0.2` with HP off;
   its source default of zero is **not** bypass.
5. For TakeCare let the delay network fill before judging output; test a reverb
   tail and changes to buffer, derez and regen. `p_drywet 0` should pass dry audio
   after the source's one-vector ramp. Check CPU in your actual Max patch.

### Manual checks for the additional batch

- GoldComp4: test threshold −24, all seven `slider11` values, detector HP/tilt,
  M/S endpoints, negative expansion and limiter; test `slider17 0` with limiter
  off for dry audio. First-run output histories follow the source initialization.
- Sky: test safe/soft endpoints, punch/saturation, M/S/link, `slider51 0/1`,
  ceiling and DSP restart. A source UI control may be inert as documented above.
- Wob-Wob: connect a beat-position ramp to inlet 3, enable `sliderstep1 1`, then
  several pattern buttons and beat offsets. With no buttons it remains at min Hz.
- Chmahastic: use an impulse and listen through the entire tail; change room,
  decay, predelay and width (including negative) while running. At `slider15 0`
  dry output retains the original mix-law attenuation; it is not unity bypass.
- GateIQ: test active mono, threshold −96 stereo bypass, range 0/48 and each
  band's threshold offset. The twice-applied band gain is intentional.
- LR4: connect all four outputs, test LP/HP/crossover/off, both inversions and
  each numerical slope selector. Crossover outputs are not automatically summed.
- VerbTiny/VerbThic/Ultralight2: let the full delay tail develop; test wet/dry,
  derez/filter/width or predelay/distance extremes. Compare separately—the two
  Verb variants have different delay times and nonlinear/output equations.
- ToTape9: test flutter, bias, head bump frequency and output clipping. ChannelX:
  test all five console types and drive extremes. ZOutputStage input mapping is
  fourth-power gain, so start near its 0.1 default, not 0.5.

The scripts can be checked locally with `node tools/check_rnbo.cjs --semantic`
when Max's RNBO installation is available (`RNBO_DIR` can override its path).
This uses RNBO's actual expression grammar and name/operator checks, but is
**not** a full Max DSP compile or playback test. See `VALIDATION.md` for executed checks and limitations.

Airwindows copyright and MIT permission notices are included in each port.
JSFX author credits and available source license notices are retained.
GoldComp4 and HP/LP LR4 contain GPL notices; the other new JSFX sources do not
supply an explicit license grant. Do not assume the Airwindows MIT license
applies to JSFX ports.
