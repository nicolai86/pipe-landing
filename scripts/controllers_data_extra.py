"""
Phase 1 & Phase 2 built-in Lua controller post-processor documentation entries:
  - CandCNC CommandCNC (LinuxCNC + DTHC IV/V)
  - Lincoln Electric Torchmate VMD (Accumove MVC)
  - Proma Elektronika MyPlasm PRO / CNC
  - Hypertherm EDGE Connect / ProNest Industrial EIA
  - Starfire / Fangling Industrial EIA

Imported by `controllers_data.py` so `controllers_data.py` stays maintainable.
All user-facing copy follows the 5 RotaryCAM Golden Rules (0 em-dashes).
"""

EXTRA_CONTROLLERS = [
    {
        "slug": "CommandCNC",
        "is_scribing": False,
        "name": "CandCNC CommandCNC (DTHC IV / V)",
        "short_name": "CandCNC CommandCNC",
        "ext": ".ngc",
        "rotary_mode": "G94 (2D/HSS Flats) + G93 (4-Axis Rotary)",
        "ihs_summary": "2D: o&lt;touchoff&gt; call | 3D/4D: G38.2 + G1 Z#5063 + G10 L20 P0",
        "torch_summary": "M3 S100 (positive S required) / M5",
        "thc_summary": "M67 E0 Q10/Q20 (synced) &amp; M68 E0 Q### (DCC presets)",
        "sync_summary": "M68 E0 Q900/Q3xxx/Q5xx + G4 P0.1 pacing",
        "card_summary": "Ready-to-run .ngc files for CandCNC tables with o&lt;touchoff&gt;, DTHC IV/V M67/M68 E0 Q### presets, and 4-axis G93 rotary.",
        "badge_label": "CandCNC LinuxCNC &bull; DTHC IV / V (.ngc)",
        "meta_title": "CandCNC CommandCNC (DTHC IV/V) Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "CandCNC CommandCNC setup guide: o<touchoff> call vs G38.2 rotary probing, M3 S100 torch firing, M67/M68 E0 Q### DTHC IV/V control, and full 6-phase cut cycle.",
        "hero_title_html": 'CandCNC <span class="text-gradient-amber">CommandCNC Setup</span>',
        "subtitle_html": 'Ready-to-cut <code class="mono">.ngc</code> files for CandCNC LinuxCNC tables with DTHC IV and DTHC V. Uses <code class="mono">o&lt;touchoff&gt; call</code> on plate, <code class="mono">G38.2</code> probing on 4-axis tube, and synced <code class="mono">M67 E0 Q10/Q20</code> anti-dive.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.ngc</code>'},
            {"style": "", "html": '<strong>DTHC IV/V:</strong> <code class="mono">M68 E0 Q900</code> &bull; <code class="mono">M67 E0 Q10/Q20</code>'},
            {"style": "", "html": '<strong>Probing:</strong> <code class="mono">o&lt;touchoff&gt; call</code> (2D) &bull; <code class="mono">G38.2</code> (4D)'},
        ],
        "toc": [
            {"id": "dthc-dcc", "badge": "01", "label": "DTHC IV/V DCC Presets &amp; Synced Hold"},
            {"id": "probing-4d", "badge": "02", "label": "2D o&lt;touchoff&gt; vs. 4-Axis Rotary Probing"},
            {"id": "post-options", "badge": "03", "label": "Built-In Post Options"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G20|G21 G17 G40 G49 G90 G94", "desc": "Safe LinuxCNC startup header"},
                    {"code": "M68 E0 Q900 / Q3xxx / Q5xx", "desc": "DTHC global enable, volts &amp; delay (paced with G4 P0.1)"},
                    {"code": "G0 Z<safeZ> / G0 X Y A", "desc": "Clearance lift and rapid to pierce"},
                ],
                "note": "Every M68 E0 DCC preset is spaced with G4 P0.1 so your DTHC reads each setting without dropping commands.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "o<touchoff> call", "desc": "Default 2D flat ohmic/float touch-off subroutine"},
                    {"code": "G38.2 Z-<d> F<f> / G1 Z#5063", "desc": "Direct G38.2 probe on 4D rotary or when selected in options"},
                    {"code": "G10 L20 P0 Z<datum>", "desc": "Set exact work Z zero minus switch offset"},
                ],
                "note": "Switches back to G94 before probing so G38.2 and o<touchoff> never run in G93.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "G0 Z<pierceH>", "desc": "Lift to pierce height"},
                    {"code": "M67 E0 Q10", "desc": "Hold DTHC off during pierce &amp; small holes"},
                    {"code": "M3 S100", "desc": "Fire torch (positive S word required by CommandCNC)"},
                    {"code": "G4 P<sec>", "desc": "Pierce delay in seconds"},
                    {"code": "G1 Z<cutH> F<plunge>", "desc": "Plunge to cut height (or 3D ramp)"},
                ],
                "note": "CommandCNC needs S > 0 to trigger the torch relay, so every cut fires with M3 S100.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G1 / G2 / G3 X Y F<feed>", "desc": "G94 on plate; G93 inverse-time on 4-axis rotary"},
                    {"code": "M67 E0 Q20 / Q10", "desc": "Motion-synced DTHC unlock on straights / lock in corners"},
                    {"code": "G41.1 / G42.1 D<kerf>", "desc": "Optional controller kerf compensation"},
                ],
                "note": "Motion-synced M67 toggles DTHC on the fly without pausing gantry motion or leaving corner divots.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "M68 E0 Q10", "desc": "Immediate DTHC off before torch shutoff"},
                    {"code": "M5", "desc": "Extinguish plasma arc"},
                    {"code": "G40", "desc": "Cancel hardware kerf if active"},
                ],
                "note": "Sends immediate M68 E0 Q10 right before M5 so DTHC always latches off before the arc stops.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G94", "desc": "Restore units-per-minute mode"},
                    {"code": "G0 Z<safeZ>", "desc": "Lift to safe Z height"},
                    {"code": "G92 A<mod_360>", "desc": "Zero-spin rotary unwrap between parts"},
                    {"code": "M30", "desc": "End program and rewind"},
                ],
                "note": "Exits in G94 with DTHC off and the trailing newline LinuxCNC requires.",
            },
        ],
        "sections": [
            {
                "id": "dthc-dcc",
                "badge": "DTHC IV / V",
                "title": "DTHC DCC Presets &amp; Motion-Synced Anti-Dive",
                "body_html": """
            <p>
              CommandCNC runs your DTHC IV or DTHC V over LinuxCNC analog output <code class="mono">E0</code>. Setup presets stay separate from live cut locks so your gantry never stalls mid-cut:
            </p>
            <ul class="doc-bullet-list">
              <li><strong>Preamble DCC Registers (<code class="mono">M68 E0 Q###</code>):</strong> Turns on global DTHC (<code class="mono">Q900</code>) and sets cut voltage (<code class="mono">Q3xxx</code>, e.g. <code class="mono">Q3129</code> for 129 V) plus pierce delay (<code class="mono">Q5xx</code>). You can also send amps (<code class="mono">Q4xx</code>), air pressure (<code class="mono">Q8xx</code>), and tuning (<code class="mono">Q711</code> to <code class="mono">Q715</code>), each spaced with <code class="mono">G4 P0.1</code>.</li>
              <li><strong>Mid-Cut Anti-Dive (<code class="mono">M67 E0 Q10 / Q20</code>):</strong> Locks DTHC on lead-ins, corners, small holes, and kerf crossings with motion-synced <code class="mono">M67</code> so the torch never pauses or dives, then sends immediate <code class="mono">M68 E0 Q10</code> before <code class="mono">M5</code>.</li>
            </ul>""",
            },
            {
                "id": "probing-4d",
                "badge": "Probing & Rotary",
                "title": "2D <code class=\"mono\">o&lt;touchoff&gt; call</code> vs. 4-Axis Rotary Probing",
                "body_html": """
            <p>
              On flat sheet, your program calls CommandCNC's built-in <code class="mono">o&lt;touchoff&gt; call</code> routine so your existing ohmic sensor and switch offset keep working as set. On 4-axis pipe, HSS, angle, channel, and I-beam, it switches to <code class="mono">G38.2</code> + <code class="mono">G1 Z#5063</code> + <code class="mono">G10 L20 P0</code> probing in <code class="mono">G94</code> and cuts in <code class="mono">G93</code> inverse-time mode.
            </p>""",
            },
            {
                "id": "post-options",
                "badge": "Options",
                "title": "Built-In Post Options (Machines Modal)",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>IHS Mode:</strong> Use <code class="mono">o&lt;touchoff&gt; call</code> (2D default) or <code class="mono">G38.2</code> + <code class="mono">G10 L20 P0</code> probing on every cut.</li>
              <li><strong>DCC Cut Presets:</strong> Toggle <code class="mono">M68 E0</code> voltage, delay, amps, and PSI registers, set DTHC delay (seconds), and pick tuning level 1 to 5.</li>
              <li><strong>Centerline Z Datum:</strong> Optional centerline <code class="mono">Z=0</code> datum for 4-axis HSS and open-profile tube jobs.</li>
            </ul>""",
            },
        ],
    },
    {
        "slug": "TorchmateVMD",
        "is_scribing": False,
        "name": "Lincoln Electric Torchmate VMD (Accumove MVC)",
        "short_name": "Torchmate VMD",
        "ext": ".fgc",
        "rotary_mode": "2D Flat &amp; Concentric Round Y-Wrap (No A / Z)",
        "ihs_summary": "Controller-owned inside M64 (AVHC touch-off &amp; plunge)",
        "torch_summary": "M06 T1 (Plasma) / M06 T2 (Marker) + M64 (On) / M65 (Off)",
        "thc_summary": "Managed by Accumove VMD AVHC (zero Z words emitted)",
        "sync_summary": "G70/G71 units (never G20/G21), G04 D<ms>, explicit G00-G03, M02",
        "card_summary": "Native .fgc files for Torchmate 4400/4800/Growth Series with G70/G71 units, M64/M65 AVHC firing, G04 D&lt;ms&gt;, and Y-wrap round pipe.",
        "badge_label": "Lincoln Electric &bull; Torchmate VMD (.fgc)",
        "meta_title": "Lincoln Electric Torchmate VMD Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "Lincoln Electric Torchmate VMD (.fgc) setup guide: G70/G71 units, M06 T1/T2 tool select, M64/M65 AVHC torch firing, G04 D<ms> dwells, and Y-wrap round pipe.",
        "hero_title_html": 'Lincoln Electric <span class="text-gradient-amber">Torchmate VMD Setup</span>',
        "subtitle_html": 'Clean <code class="mono">.fgc</code> files for Torchmate 4400, 4800, 5100, and Accumove VMD tables using native <code class="mono">G70/G71</code> units, <code class="mono">M64/M65</code> AVHC cycles, and <code class="mono">M06 T1/T2</code> tool selection.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.fgc</code>'},
            {"style": "", "html": '<strong>Units &amp; End:</strong> <code class="mono">G70 / G71</code> &bull; <code class="mono">M02</code> (Zero <code class="mono">G20/M30</code>)'},
            {"style": "", "html": '<strong>Torch &amp; Marker:</strong> <code class="mono">M06 T1/T2</code> &bull; <code class="mono">M64 / M65</code>'},
        ],
        "toc": [
            {"id": "vmd-syntax", "badge": "01", "label": "VMD Syntax Rules (G70/G71, M64/M65, G04 D)"},
            {"id": "avhc-z", "badge": "02", "label": "Zero-Z AVHC Height Control &amp; Plate Marker"},
            {"id": "ywrap-limits", "badge": "03", "label": "Round-Pipe Y-Wrap &amp; Hardware Limits"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Position",
                "codes": [
                    {"code": "G70 | G71", "desc": "Inches (G70) or mm (G71); never G20/G21"},
                    {"code": "G90", "desc": "Absolute positioning"},
                    {"code": "M06 T1", "desc": "Select plasma torch tool"},
                    {"code": "G00 X<x> Y<y>", "desc": "G00 rapid to pierce point"},
                ],
                "note": "Comments use VMD apostrophes ('), and every move prints G00, G01, G02, or G03.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "(Owned by M64)", "desc": "Accumove AVHC probes surface automatically on M64"},
                ],
                "note": "Any Z word alongside M64 locks out Z on VMD, so the file never emits a Z coordinate.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "M64", "desc": "Touch-off, lift to pierce height, fire torch &amp; plunge"},
                    {"code": "G04 D<ms> (opt)", "desc": "Optional millisecond dwell when enabled in post options"},
                ],
                "note": "By default VMD uses its own cut-chart pierce delay; turn on G04 D<ms> in Post Options if you want to send dwell from CAM.",
            },
            {
                "num": 4,
                "title": "Cut & AVHC Control",
                "codes": [
                    {"code": "G01 / G02 / G03 X Y F<feed>", "desc": "G01/G02/G03 on every line (F word optional)"},
                ],
                "note": "Accumove VMD runs arc-voltage height tracking and anti-dive on its own during M64 cuts.",
            },
            {
                "num": 5,
                "title": "Torch Off",
                "codes": [
                    {"code": "M65", "desc": "Extinguish arc and retract Z via VMD"},
                ],
                "note": "VMD automatically lifts the torch to its configured transfer height on M65.",
            },
            {
                "num": 6,
                "title": "Program End",
                "codes": [
                    {"code": "M02", "desc": "Mandatory VMD program end (never M30)"},
                ],
                "note": "Every M64 is paired with M65 before M02 so the controller resets cleanly.",
            },
        ],
        "sections": [
            {
                "id": "vmd-syntax",
                "badge": "VMD Rules",
                "title": "Torchmate VMD Dialect Rules",
                "body_html": """
            <p>
              Torchmate VMD rejects standard G-code lines that run fine on other tables. Your <code class="mono">.fgc</code> file follows every VMD rule automatically:
            </p>
            <ul class="doc-bullet-list">
              <li><strong><code class="mono">G70 / G71</code> Units Only:</strong> On Torchmate VMD, <code class="mono">G20</code> is Program Scale, not inches. Your code always uses <code class="mono">G70</code> (inches) or <code class="mono">G71</code> (mm) and ends with <code class="mono">M02</code> (never <code class="mono">M30</code>).</li>
              <li><strong>Per-Line Motion Codes &amp; Apostrophe Comments:</strong> Every move includes <code class="mono">G00</code>, <code class="mono">G01</code>, <code class="mono">G02</code>, or <code class="mono">G03</code>. Comments start with <code class="mono">'</code>, and <code class="mono">G17</code>, <code class="mono">G94</code>, and <code class="mono">G91.1</code> are left out.</li>
              <li><strong>Optional <code class="mono">G04 D&lt;ms&gt;</code> &amp; Feedrate Toggle:</strong> Let VMD's cut chart control pierce delay and feedrate, or turn on <code class="mono">G04 D&lt;ms&gt;</code> and <code class="mono">F</code> words in Machines &rarr; Post Options.</li>
            </ul>""",
            },
            {
                "id": "avhc-z",
                "badge": "AVHC & Marker",
                "title": "Controller-Owned AVHC Height &amp; Plate Marker (<code class=\"mono\">M06 T2</code>)",
                "body_html": """
            <p>
              Accumove VMD runs touch-off, pierce height, cut height, and retract inside <code class="mono">M64</code> / <code class="mono">M65</code>. Zero <code class="mono">Z</code> words keep AVHC active. For plate marking, your program selects <code class="mono">M06 T2</code>, shifts XY coordinates by your marker offset, and fires the marker with <code class="mono">M64</code> / <code class="mono">M65</code>.
            </p>""",
            },
            {
                "id": "ywrap-limits",
                "badge": "Rotary",
                "title": "Concentric Round-Pipe Y-Wrap",
                "body_html": """
            <p>
              Flat plate and concentric round pipe wrap onto the <code class="mono">Y</code> axis. Square/rectangular HSS, angle iron, channel, I-beam, eccentric bevels, and 3D ramp lead-ins need live Z tracking and are blocked before export so you never crash a torch.
            </p>""",
            },
        ],
    },
    {
        "slug": "MyPlasm",
        "is_scribing": False,
        "name": "Proma Elektronika MyPlasm PRO / CNC",
        "short_name": "MyPlasm PRO / CNC",
        "ext": ".tap",
        "rotary_mode": "PRO FW 1.2/1.3+: 4-Axis A | Legacy 2D: Y-Wrap",
        "ihs_summary": "PRO FW 1.3+: G38.2 + G92.38 | FW 1.2: G38.2 + G92 Z",
        "torch_summary": "M3 I / M5 I + Arc-OK Wait (M66 Q# on FW 1.3+, M0 S# on FW 1.2)",
        "thc_summary": "M666 I (THC Off) / M667 I (THC On, optional P volts)",
        "sync_summary": "Strict metric G21, G4 P<int ms>, inline I flag, +/-3600 deg A limit",
        "card_summary": "Metric .tap post for Proma MyPlasm PRO (FW 1.2 &amp; 1.3+) and Legacy 2D with G92.38 probing, M666/M667 THC, and 4-axis A rotary.",
        "badge_label": "Proma Elektronika &bull; MyPlasm PRO / CNC (.tap)",
        "meta_title": "Proma MyPlasm PRO / CNC Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "Proma Elektronika MyPlasm PRO (FW 1.2 and 1.3+) and Legacy 2D setup guide: G21 metric output, G92.38 probing, M66 Q# vs M0 S# Arc-OK wait, and M666/M667 THC.",
        "hero_title_html": 'Proma <span class="text-gradient-amber">MyPlasm PRO Setup</span>',
        "subtitle_html": 'Ready-to-run <code class="mono">.tap</code> output for Proma Elektronika MyPlasm PRO (<code class="mono">FW 1.2</code> and <code class="mono">FW 1.3+</code>) and Legacy 2D tables with inline <code class="mono">I</code>-flagged <code class="mono">M666/M667</code> THC and <code class="mono">&plusmn;3600&deg;</code> rotary wrap protection.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.tap</code> (Metric <code class="mono">G21</code>)'},
            {"style": "", "html": '<strong>Firmware Modes:</strong> <code class="mono">PRO FW 1.3+</code> &bull; <code class="mono">PRO FW 1.2</code> &bull; <code class="mono">Legacy 2D</code>'},
            {"style": "", "html": '<strong>THC &amp; Scribe:</strong> <code class="mono">M666/M667 I</code> &bull; <code class="mono">M62/M63 P1..6</code>'},
        ],
        "toc": [
            {"id": "firmware-modes", "badge": "01", "label": "PRO FW 1.3+ vs. FW 1.2 vs. Legacy 2D"},
            {"id": "thc-arcok", "badge": "02", "label": "M666/M667 THC, Arc-OK Wait &amp; Inline I Flag"},
            {"id": "rotary-limits", "badge": "03", "label": "4-Axis Rotary &plusmn;3600&deg; Soft-Limit Protection"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G21 / G90", "desc": "Mandatory metric units (auto-converted even from inch projects)"},
                    {"code": "G0 Z<safeZ>", "desc": "Lift to clearance height"},
                    {"code": "G0 X<x> Y<y> A<a>", "desc": "Position to pierce (zero G17/G40/G94 header clutter)"},
                ],
                "note": "MyPlasm PRO always runs in metric G21; inch parts convert automatically so dimensions stay exact.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "G38.2 Z-<d> F<f>", "desc": "Touch-off probe down to stock surface"},
                    {"code": "G92.38 (FW 1.3+) | G92 Z<off> (FW 1.2)", "desc": "Reset Z datum with switch offset"},
                ],
                "note": "Legacy 2D mode skips G38.2 and lets the controller handle probing internally.",
            },
            {
                "num": 3,
                "title": "Pierce & Arc-OK Wait",
                "codes": [
                    {"code": "G0 Z<pierceH>", "desc": "Move to pierce height"},
                    {"code": "M666", "desc": "Disable THC before ignition (required on PRO)"},
                    {"code": "M3", "desc": "Fire plasma torch"},
                    {"code": "M66 Q<sec> (FW 1.3+) | M0 S<sec> (FW 1.2)", "desc": "Wait for Arc-OK transfer signal"},
                    {"code": "G4 P<int_ms>", "desc": "Integer millisecond pierce delay (e.g. G4 P500)"},
                    {"code": "G1 Z<cutH> F<plunge>", "desc": "Plunge to cut height"},
                ],
                "note": "Locks THC with M666 before M3 and waits for Arc-OK before gantry motion starts.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G1 / G2 / G3 X Y A F<feed>", "desc": "Modal G94 cutting (no G93/G94 words emitted)"},
                    {"code": "M667 I / M666 I", "desc": "Inline THC unlock on straights / lock in corners &amp; small holes"},
                ],
                "note": "Inline I keeps motion smooth without stopping; voltage presets P/A stay separate from bare I.",
            },
            {
                "num": 5,
                "title": "Torch Off & Scribe",
                "codes": [
                    {"code": "M666 I", "desc": "Lock THC before shutoff"},
                    {"code": "M5 I", "desc": "Extinguish plasma arc"},
                    {"code": "M62 P<1..6> / M63 P<1..6>", "desc": "Pneumatic air-scribe output control"},
                ],
                "note": "Pneumatic scribe offsets are built into XY moves so you never hit unsupported G52 alarms.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G0 Z<safeZ>", "desc": "Retract to safe height"},
                    {"code": "G92 A<mod_360>", "desc": "Reset A-axis wrap inside +/-3600 deg firmware limit"},
                    {"code": "M30", "desc": "End program and rewind"},
                ],
                "note": "Leaves out M02, G20, G93, and G94 to match MyPlasm PRO firmware rules.",
            },
        ],
        "sections": [
            {
                "id": "firmware-modes",
                "badge": "Firmware",
                "title": "Pick Your MyPlasm Controller Mode",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>PRO FW 1.3+ (Default):</strong> Uses <code class="mono">G38.2</code> + <code class="mono">G92.38</code> probing, <code class="mono">M66 Q&lt;sec&gt;</code> Arc-OK wait, and full 4-axis rotary <code class="mono">A</code> support across round, HSS, angle, channel, and I-beam.</li>
              <li><strong>PRO FW 1.2:</strong> Uses <code class="mono">G38.2</code> + <code class="mono">G92 Z&lt;offset&gt;</code> probing and <code class="mono">M0 S&lt;sec&gt;</code> Arc-OK wait for earlier PRO firmware builds.</li>
              <li><strong>Legacy 2D:</strong> Simplified 2-axis plate and concentric round Y-wrap output for classic MyPlasm CNC tables.</li>
            </ul>""",
            },
            {
                "id": "thc-arcok",
                "badge": "THC & Arc-OK",
                "title": "Inline <code class=\"mono\">I</code> Flag, <code class=\"mono\">M666/M667</code> THC &amp; Integer Millisecond Dwells",
                "body_html": """
            <p>
              MyPlasm PRO needs <code class="mono">M666</code> (THC off) before every <code class="mono">M3</code> start and integer milliseconds in <code class="mono">G4 P&lt;ms&gt;</code> (like <code class="mono">G4 P500</code> for 0.5 s). Mid-cut THC locks use <code class="mono">M666 I</code> and <code class="mono">M667 I</code> so your gantry keeps moving without pausing. Voltage presets (<code class="mono">M667 P&lt;volts&gt;</code>) sit on their own line without the <code class="mono">I</code> flag.
            </p>""",
            },
            {
                "id": "rotary-limits",
                "badge": "Rotary Safety",
                "title": "4-Axis Rotary <code class=\"mono\">&plusmn;3600&deg;</code> Soft-Limit Protection",
                "body_html": """
            <p>
              MyPlasm PRO has a <code class="mono">&plusmn;3600&deg;</code> (10-turn) soft limit on the rotary <code class="mono">A</code> axis. Your program tracks total tube rotation and adds modulo-360&deg; <code class="mono">G92 A</code> resets between features and parts so long sticks never trip a soft-limit fault mid-run.
            </p>""",
            },
        ],
    },
    {
        "slug": "HyperthermEIA",
        "is_scribing": False,
        "name": "Hypertherm EDGE Connect / ProNest (Industrial EIA)",
        "short_name": "Hypertherm EDGE Connect (EIA)",
        "ext": ".cnc",
        "rotary_mode": "2D Flat &amp; Concentric Round Y-Wrap (Zero Z / A)",
        "ihs_summary": "Controller-owned Sensor THC inside M07 / RF",
        "torch_summary": "M07 / M08 (default) or legacy RF / RT",
        "thc_summary": "M50 (Disable) / M51 (Enable, always restored before M08)",
        "sync_summary": "G70/G71 (opt G20/G21), opt G59 V509/V600-V603, G41/G42 + G43 D# X<kerf>",
        "card_summary": "Industrial .cnc EIA files for Hypertherm EDGE Connect, EDGE Pro, and MicroEDGE with M07/M08, M50/M51 THC, optional G59 cut charts, and Marker 1.",
        "badge_label": "Hypertherm EDGE Connect / Pro &bull; Industrial EIA (.cnc)",
        "meta_title": "Hypertherm EDGE Connect (EIA) Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "Hypertherm EDGE Connect and ProNest EIA (.cnc) setup guide: G70/G71 units, M07/M08 or RF/RT torch control, M50/M51 THC hold, G59 V### process variables, G43 kerf, and Marker 1.",
        "hero_title_html": 'Hypertherm <span class="text-gradient-amber">EDGE Connect (EIA) Setup</span>',
        "subtitle_html": 'Industrial <code class="mono">.cnc</code> EIA files for Hypertherm EDGE Connect, EDGE Pro, and MicroEDGE tables with Sensor THC <code class="mono">M07/M08</code> firing, <code class="mono">M50/M51</code> corner hold, optional <code class="mono">G59 V###</code> cut charts, and Marker 1 support.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.cnc</code>'},
            {"style": "", "html": '<strong>Torch &amp; THC:</strong> <code class="mono">M07 / M08</code> (or <code class="mono">RF / RT</code>) &bull; <code class="mono">M50 / M51</code>'},
            {"style": "", "html": '<strong>Optional Cut Chart:</strong> <code class="mono">G59 V509 / V600..V603</code> &bull; <code class="mono">G43 D# X&lt;kerf&gt;</code>'},
        ],
        "toc": [
            {"id": "eia-cycle", "badge": "01", "label": "EIA Torch, Sensor THC &amp; Zero-Z Discipline"},
            {"id": "g59-g43", "badge": "02", "label": "Optional G59 Cut-Chart Variables &amp; G43 Kerf"},
            {"id": "marker-options", "badge": "03", "label": "Marker 1, Plasma Marking &amp; Post Options"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Preamble & Rapid",
                "codes": [
                    {"code": "G70 | G71 (opt G20 | G21)", "desc": "EIA inch (G70) or metric (G71) unit mode"},
                    {"code": "G90 / G40", "desc": "Absolute positioning and cancel kerf"},
                    {"code": "G59 V509 / V600..V603 (opt)", "desc": "Optional EDGE Connect process ID, volts, pierce delay, heights"},
                    {"code": "G43 D<slot> X<kerf> (opt)", "desc": "Optional hardware kerf register"},
                    {"code": "G00 X<x> Y<y>", "desc": "Rapid to pierce point (zero Z or A words)"},
                ],
                "note": "Never emits G91.1, G90.1, M03, M05, or G59 V504/V505.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "(Owned by Sensor THC)", "desc": "EDGE Connect runs ohmic/stall IHS automatically inside M07"},
                ],
                "note": "Zero Z words keep Sensor THC fully in control of touch-off, pierce height, and retract.",
            },
            {
                "num": 3,
                "title": "Pierce & THC Hold",
                "codes": [
                    {"code": "M50 (if locked)", "desc": "Disable Sensor THC for small holes or lead-ins"},
                    {"code": "M07 (or RF)", "desc": "Start plasma cut cycle"},
                ],
                "note": "Sensor THC runs the pierce delay from the console cut chart or G59 V601.",
            },
            {
                "num": 4,
                "title": "Cut & Corner Hold",
                "codes": [
                    {"code": "G41 / G42 (opt)", "desc": "Optional controller kerf compensation"},
                    {"code": "G01 / G02 / G03 X Y F<feed>", "desc": "180-deg split arcs; F words optional if chart owns speed"},
                    {"code": "M51 / M50", "desc": "Enable THC on straight runs / disable in corners &amp; voids"},
                ],
                "note": "Full 360-degree circles split into two 180-degree arcs for reliable EIA cutting.",
            },
            {
                "num": 5,
                "title": "Torch Off & Restore",
                "codes": [
                    {"code": "M51 (if locked)", "desc": "Always restore THC enable before M08 so M50 never latches"},
                    {"code": "M08 (or RT)", "desc": "Extinguish plasma and retract head"},
                    {"code": "G40", "desc": "Cancel hardware kerf if active"},
                ],
                "note": "Restoring M51 before M08 prevents EDGE Connect from keeping THC disabled on the next cut.",
            },
            {
                "num": 6,
                "title": "Program End",
                "codes": [
                    {"code": "M12 (if marker used)", "desc": "Retract Marker 1"},
                    {"code": "M02 (or M30)", "desc": "End program (optional % tape framing &amp; N-numbers)"},
                ],
                "note": "Runs flat sheet and concentric round-pipe Y-wrap; blocks 4D HSS and open profiles before export.",
            },
        ],
        "sections": [
            {
                "id": "eia-cycle",
                "badge": "EIA Core",
                "title": "Sensor THC <code class=\"mono\">M07/M08</code> &amp; <code class=\"mono\">M50/M51</code> Hold",
                "body_html": """
            <p>
              Hypertherm EDGE Connect and EDGE Pro tables control touch-off, pierce height, and cut height through Sensor THC. Zero <code class="mono">Z</code> words keep Sensor THC active. Cuts fire with <code class="mono">M07</code> / <code class="mono">M08</code> (or legacy <code class="mono">RF</code> / <code class="mono">RT</code>), lock THC in holes and corners with <code class="mono">M50</code>, and always restore <code class="mono">M51</code> before <code class="mono">M08</code> so THC never stays off for the next pierce.
            </p>""",
            },
            {
                "id": "g59-g43",
                "badge": "Cut Chart",
                "title": "Optional <code class=\"mono\">G59 V###</code> Cut-Chart Variables &amp; <code class=\"mono\">G43</code> Kerf",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Safe <code class="mono">G59</code> Variables Only:</strong> When turned on in Post Options, your file sends <code class="mono">G59 V509 F&lt;id&gt;</code> (Process ID), <code class="mono">V600</code> (arc volts), <code class="mono">V601</code> (pierce delay), <code class="mono">V602</code> (pierce height %), and <code class="mono">V603</code> (cut height), never <code class="mono">V504</code> or <code class="mono">V505</code>.</li>
              <li><strong>Hardware Kerf (<code class="mono">G43 D# X&lt;kerf&gt;</code>):</strong> Loads your kerf into tool slot <code class="mono">D1..D99</code> alongside <code class="mono">G41/G42/G40</code> when enabled.</li>
            </ul>""",
            },
            {
                "id": "marker-options",
                "badge": "Marker & Options",
                "title": "Marker 1 (<code class=\"mono\">M11/M09/M10/M12</code>), XPR Marking &amp; Post Options",
                "body_html": """
            <p>
              Pneumatic marking selects Marker 1 with <code class="mono">M11</code>, fires with <code class="mono">M09</code> / <code class="mono">M10</code> (with XY offset included in the move), and lifts with <code class="mono">M12</code>. For XPR Argon/N2 plasma marking, set <strong>Plasma Marking Syntax</strong> to <code class="mono">M07/M08</code> in Machines &rarr; Post Options. You can also toggle <code class="mono">G20/G21</code> vs. <code class="mono">G70/G71</code>, <code class="mono">RF/RT</code>, <code class="mono">M30</code>, tape <code class="mono">%</code> framing, feedrate words, and <code class="mono">N10</code> line numbers.
            </p>""",
            },
        ],
    },
    {
        "slug": "StarfireFangling",
        "is_scribing": False,
        "name": "Starfire / Fangling Industrial EIA (SF-2100C / F2100B / F2300B)",
        "short_name": "Starfire / Fangling (EIA)",
        "ext": ".txt",
        "rotary_mode": "2D Flat &amp; Concentric Round Y-Wrap (2-Axis XY)",
        "ihs_summary": "Controller-owned inside M07 (console THC &amp; pierce)",
        "torch_summary": "M07 (Cut On) / M08 (Cut Off), zero-padded G00-G03 &amp; M02",
        "thc_summary": "Console default (none) or optional M38/M39 (never M50)",
        "sync_summary": "Drift-free quantized G91 incremental default, G21/G20, G92 X0 Y0, 180-deg arcs",
        "card_summary": "Shop-ready .txt EIA files for SF-2100C, F2100B, and F2300B panels with zero-drift G91 incremental moves, 180-deg arc splitting, and bare-EIA mode.",
        "badge_label": "Starfire SF-2100C &bull; Fangling F2100B/F2300B (.txt)",
        "meta_title": "Starfire / Fangling Industrial EIA Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "Starfire SF-2100C and Fangling F2100B/F2300B (.txt) setup guide: drift-free quantized G91 incremental output, G21/G20 units, M07/M08 firing, 180-deg arcs, and bare-EIA mode.",
        "hero_title_html": 'Starfire &amp; Fangling <span class="text-gradient-amber">Industrial EIA Setup</span>',
        "subtitle_html": 'Zero-drift <code class="mono">.txt</code> EIA files for Starfire (<code class="mono">SF-2100C</code> / <code class="mono">SF-2300S</code>) and Fangling (<code class="mono">F2100B</code> / <code class="mono">F2300B</code>) panels with quantized <code class="mono">G91</code> incremental moves, 180&deg; arc splitting, zero <code class="mono">%</code> framing, and optional comment-free output.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.txt</code> (Zero <code class="mono">%</code>)'},
            {"style": "", "html": '<strong>Coordinates:</strong> Quantized <code class="mono">G91</code> (Default) or <code class="mono">G90</code>'},
            {"style": "", "html": '<strong>Torch &amp; End:</strong> <code class="mono">M07 / M08</code> &bull; Mandatory <code class="mono">M02</code>'},
        ],
        "toc": [
            {"id": "quantized-g91", "badge": "01", "label": "Drift-Free Quantized G91 Incremental Coordinates"},
            {"id": "panel-rules", "badge": "02", "label": "SF-2100C / F2100B Dialect Rules &amp; Bare-EIA Mode"},
            {"id": "dwell-thc-scribe", "badge": "03", "label": "Dwells, Optional M38/M39 THC &amp; Scribing"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Header & Rapid",
                "codes": [
                    {"code": "G21 | G20", "desc": "Metric (G21) or inch (G20); never G70/G71"},
                    {"code": "G91 (default) | G90", "desc": "Incremental default so panel origin shifts work anywhere"},
                    {"code": "G92 X0 Y0 / G40", "desc": "Zero local origin &amp; cancel kerf"},
                    {"code": "G00 X<dx> Y<dy>", "desc": "Zero-padded rapid to pierce point (zero Z / A)"},
                ],
                "note": "No % characters anywhere in the file; comments are 7-bit ASCII UPPERCASE <= 80 chars or turned off completely.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "(Owned by Panel)", "desc": "Controller executes IHS and pierce height inside M07"},
                ],
                "note": "Strictly 2-axis XY output so your front panel owns Z height and collision recovery.",
            },
            {
                "num": 3,
                "title": "Pierce",
                "codes": [
                    {"code": "M38 (opt)", "desc": "Optional THC disable when M38/M39 mode is selected"},
                    {"code": "M07", "desc": "Start plasma cut"},
                    {"code": "G04 L<sec> | P<cs> (opt)", "desc": "Omitted by default (panel owns pierce delay)"},
                ],
                "note": "Most Starfire and Fangling panels time pierce delay from the front keypad; enable G04 only if your panel needs it.",
            },
            {
                "num": 4,
                "title": "Cut & 180&deg; Arcs",
                "codes": [
                    {"code": "G01 / G02 / G03 X<dx> Y<dy> I J", "desc": "Quantized G91 deltas with <= 180-deg arcs (or G01 linearized)"},
                    {"code": "M39 / M38 (opt)", "desc": "Optional THC enable/disable (never M50 or M10-M13)"},
                ],
                "note": "Whole-step move tracking guarantees closed contours return to the exact start point with zero drift.",
            },
            {
                "num": 5,
                "title": "Torch Off",
                "codes": [
                    {"code": "M39 (if M38 locked)", "desc": "Always restore THC before M08"},
                    {"code": "M08", "desc": "Extinguish arc and lift torch"},
                ],
                "note": "Every M07 is cleanly paired with M08 before the next rapid.",
            },
            {
                "num": 6,
                "title": "Program End",
                "codes": [
                    {"code": "M02", "desc": "Mandatory program end (never M30)"},
                ],
                "note": "Runs flat plate and concentric round-pipe Y-wrap; blocks 4D HSS and open profiles before export.",
            },
        ],
        "sections": [
            {
                "id": "quantized-g91",
                "badge": "Zero-Drift G91",
                "title": "Why Quantized <code class=\"mono\">G91</code> Incremental Coordinates Matter",
                "body_html": """
            <p>
              Starfire and Fangling panels default to <code class="mono">G91</code> incremental programs with <code class="mono">G92 X0 Y0</code> so you can jog to any spot on a sheet and hit Start. Standard incremental posts stack up rounding errors around curves and nested sheets. Tracking exact rounded grid positions (<code class="mono">delta = round(target) - cursor</code>) on every line and <code class="mono">G02/G03</code> arc keeps multi-part sheets dead-on from start to finish.
            </p>""",
            },
            {
                "id": "panel-rules",
                "badge": "Panel Hygiene",
                "title": "SF-2100C / F2100B Dialect Rules &amp; Bare-EIA Mode",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Clean Panel Code:</strong> Zero <code class="mono">%</code> characters, zero <code class="mono">G70/G71</code>, zero <code class="mono">M30</code>, zero <code class="mono">Z</code> words, and zero-padded <code class="mono">G00/G01/G02/G03/M07/M08/M02</code> codes.</li>
              <li><strong>180&deg; Arc Splitting (or <code class="mono">G01</code> Straight Segments):</strong> Full 360&deg; circles split into two 180&deg; arcs so older panels never drop a hole. Turn on <strong>Linearize Arcs (G01 Only)</strong> in Post Options for older controllers that need straight segments.</li>
              <li><strong>Comment-Free Mode:</strong> Turn off <strong>Emit Comments</strong> in Machines &rarr; Post Options to strip every <code class="mono">(...)</code> comment for panels that reject text lines.</li>
            </ul>""",
            },
            {
                "id": "dwell-thc-scribe",
                "badge": "Options",
                "title": "Dwells, Optional <code class=\"mono\">M38/M39</code> THC &amp; Scribe Modes",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Pierce Dwell:</strong> Left out by default so your front keypad controls pierce time. Turn on <code class="mono">G04 L&lt;sec&gt;</code> (Starfire seconds) or <code class="mono">G04 P&lt;cs&gt;</code> (Fangling integer centiseconds, like <code class="mono">P50</code> = 0.50 s) if needed.</li>
              <li><strong>THC Control:</strong> Uses panel THC by default (no THC M-codes), or enable <code class="mono">M38/M39</code> corner hold in Post Options. Never emits Hypertherm <code class="mono">M50</code> or <code class="mono">M10..M13</code>.</li>
              <li><strong>Scribing:</strong> Pick Fangling <code class="mono">M09/M10</code> or Starfire <code class="mono">M32/M33</code> with XY marker offsets already built into the coordinates.</li>
            </ul>""",
            },
        ],
    },
]
