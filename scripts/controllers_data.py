"""
Single-source-of-truth registry of all 14 CNC controller post-processors
plus Scribing (Coaxial EasyScribe vs. Pneumatic Air-Scribe) for:
  - docs/machine-configuration.html (Step 6 comparison table & card grid)
  - docs/machine-configuration/<Slug>/index.html (per-controller setup + 6-phase cut cycle)

Every G-code, M-code, parameter register, and checklist item is verified directly
against pipe-macos/PostProcessor/Dialects/*.swift.
"""

CONTROLLERS = [
    {
        "slug": "LinuxCNC",
        "is_scribing": False,
        "name": "LinuxCNC 2.9+ QTPlasmaC",
        "short_name": "LinuxCNC QTPlasmaC",
        "ext": ".ngc",
        "rotary_mode": "G94 (2D/HSS Flats) + G93 (Rotary)",
        "ihs_summary": "2D: plasmac internal | 3D/4D: G91/G38.2/G90/G1 Z#5063/G10 L20 P0",
        "torch_summary": "M3 $0 S1 / M5 $0 (+ G94 G1 Z on 3D/4D)",
        "thc_summary": "M62 P1/P2 (Lock) / M63 P1/P2 (Unlock)",
        "sync_summary": "(o=0, ...) or M190 P<n> -> M66 P3 L3 Q2",
        "card_summary": "Three clean regimes (2D flat, #&lt;tube_cut&gt;=1 rotary/3D, non-M3 scribe) with M62/M63 kerf void protection.",
        "badge_label": "LinuxCNC 2.9+ &bull; QTPlasmaC (.ngc)",
        "meta_title": "LinuxCNC 2.9+ QTPlasmaC Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "LinuxCNC 2.9+ QTPlasmaC setup guide: rotary tube_cut=1 mode, G38.2 and G10 L20 P0 probing, M62/M63 kerf void lock, and full 6-phase cut cycle.",
        "hero_title_html": 'LinuxCNC 2.9+ <span class="text-gradient-amber">QTPlasmaC Setup</span>',
        "subtitle_html": 'How RotaryCAM drives <code class="mono">.ngc</code> files across 2D flat plate, 4-axis rotary <code class="mono">#&lt;tube_cut&gt;=1</code> cuts, and non-<code class="mono">M3</code> drag scribes without QTPlasmaC fighting your Z axis.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.ngc</code>'},
            {"style": "", "html": '<strong>Regimes:</strong> 2D Internal Z / Rotary &amp; 3D <code class="mono">#&lt;tube_cut&gt;=1</code> / Scribe <code class="mono">#&lt;keep-z-motion&gt;=1</code>'},
            {"style": "", "html": '<strong>THC &amp; Void:</strong> <code class="mono">M62/M63 P1/P2</code> &bull; <code class="mono">M67 E3 Q60</code>'},
        ],
        "toc": [
            {"id": "regimes", "badge": "01", "label": "Three QTPlasmaC Regimes"},
            {"id": "materials-thc", "badge": "02", "label": "Materials, Void Lock &amp; Small Holes"},
            {"id": "checklist", "badge": "03", "label": "INI / HAL Checklist"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G94", "desc": "Units-per-minute positioning"},
                    {"code": "G0 X<x> Y<y> A<a>", "desc": "Omits Z & A on 2D flat; omits stationary A with lookahead"},
                    {"code": "G0 Z<safeZ>", "desc": "Rotary/3D clearance (omitted on pure 2D)"},
                ],
                "note": "2D flat sheet emits zero Z or A words so plasmac owns Z completely.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "G91 / G38.2 Z-<d> F<f>", "desc": "3D/Rotary explicit touch probe"},
                    {"code": "G90 / G1 Z#5063 F<f>", "desc": "Settle onto exact tripped Z"},
                    {"code": "G10 L20 P0 Z<datum>", "desc": "Zero Z minus float switch offset"},
                ],
                "note": "Pure 2D skips G38.2 because M3 $0 S1 runs QTPlasmaC's internal ohmic/float probe.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "G0 Z<pierceH>", "desc": "3D/Rotary move to pierce height"},
                    {"code": "M62 P2", "desc": "Lock THC for lead-in / small hole"},
                    {"code": "M67 E3 Q60", "desc": "60% feed on holes <= 25.4 mm"},
                    {"code": "M3 $0 S1", "desc": "Fire plasma (QTPlasmaC owns dwell pd)"},
                    {"code": "G94 G1 Z<cutH> F<p>", "desc": "Non-ramp plunge to cut height"},
                ],
                "note": "QTPlasmaC executes pierce delay pd from (o=0, ...) or M190 material inside M3 $0 S1.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G94 / G93", "desc": "G94 on 2D & HSS flats; G93 when A moves"},
                    {"code": "F#<_hal[plasmac.cut-feed-rate]>", "desc": "2D flat reads live QTPlasmaC cut speed"},
                    {"code": "M63 P2 / M62 P2", "desc": "Synced THC unlock / corner lock"},
                    {"code": "M62 P1 / M63 P1", "desc": "Ignore / restore Arc OK over kerf voids"},
                ],
                "note": "Rotary lookahead stays in G94 on flat HSS faces and switches to G93 only during A rotation.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "M63 P1", "desc": "Restore Arc OK if void-ignored"},
                    {"code": "M5 $0", "desc": "Extinguish plasma arc"},
                    {"code": "M67 E3 Q0", "desc": "Restore 100% feedrate after small hole"},
                    {"code": "M63 P2", "desc": "Unlock THC after 4D dynamic-Z cut"},
                ],
                "note": "M67 E3 Q0 cancels 60% small-hole speed scaling cleanly at cut end.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G94", "desc": "Restore G94 before retract"},
                    {"code": "G0 Z<safeZ>", "desc": "Retract (omitted on pure 2D flat)"},
                    {"code": "G0 A<360*k> / G92 A0", "desc": "Pack/EOF unwind to nearest rev"},
                    {"code": "M190 P-1 / M52 P0 / M30", "desc": "Restore material & end program"},
                ],
                "note": "Unrolled Pack Mode re-probes surface Z on every part to cancel stick bow.",
            },
        ],
        "sections": [
            {
                "id": "regimes",
                "badge": "Regimes",
                "title": "Three QTPlasmaC Regimes",
                "body_html": """
            <p>
              LinuxCNC 2.9+ <code class="mono">QTPlasmaC</code> switches how it handles Z motion, probing, and path blending depending on what you cut. RotaryCAM outputs <code class="mono">.ngc</code> files matched to three regimes so <code class="mono">plasmac</code> never fights your rotary chuck, 3D ramps, or drag scribe:
            </p>
            <ul class="doc-bullet-list">
              <li>
                <strong>Regime 1: 2D Flat Sheet (No <code class="mono">#&lt;tube_cut&gt;</code>, No <code class="mono">#&lt;keep-z-motion&gt;</code>, Zero Z/A Words):</strong>
                On flat plate, <code class="mono">plasmac</code> owns probing and THC inside <code class="mono">M3 $0 S1</code> and <code class="mono">M5 $0</code>. RotaryCAM emits zero <code class="mono">Z</code> or <code class="mono">A</code> words, sets <code class="mono">F#&lt;_hal[plasmac.cut-feed-rate]&gt;</code>, runs <code class="mono">G64 P0.1 Q0.02</code> blending with <code class="mono">M52 P1</code> adaptive feed, and sets <code class="mono">#&lt;holes&gt;=0</code> so QTPlasmaC never double-scales CAM bolt holes.
              </li>
              <li>
                <strong>Regime 2: Rotary &amp; 3D Ramps (<code class="mono">#&lt;tube_cut&gt;=1</code> Before Motion):</strong>
                For 4-axis pipe saddles, square/rectangular HSS tubes, open beams, and 3D ramp lead-ins, RotaryCAM injects <code class="mono">#&lt;tube_cut&gt;=1</code> before motion so QTPlasmaC hands explicit Z probing and motion back to your program. It probes with <code class="mono">G91</code> / <code class="mono">G38.2</code> / <code class="mono">G90</code> / <code class="mono">G1 Z#5063</code> / <code class="mono">G10 L20 P0</code>, fires <code class="mono">M3 $0 S1</code>, executes a <code class="mono">G94 G1 Z</code> plunge/ramp, uses <code class="mono">G64 P0.25 Q0.05</code>, switches between <code class="mono">G94</code> (HSS flats) and <code class="mono">G93</code> (<code class="mono">A</code> moves), and ends with <code class="mono">M190 P-1</code>.
              </li>
              <li>
                <strong>Regime 3: Non-<code class="mono">M3</code> Scribes &amp; Markers (<code class="mono">#&lt;keep-z-motion&gt;=1</code> Restricted):</strong>
                <code class="mono">#&lt;keep-z-motion&gt;=1</code> is restricted strictly to non-<code class="mono">M3</code> drag scribes (such as coaxial EasyScribe) where no plasma arc fires. Never use <code class="mono">#&lt;keep-z-motion&gt;=1</code> on <code class="mono">M3</code> plasma cuts. Multi-tool jobs use <code class="mono">M3 $0 S1</code> (plasma), <code class="mono">M3 $1 S1</code> / <code class="mono">M5 $1</code> (pneumatic air-scribe), and <code class="mono">M3 $2 S1</code> (center-point dimple).
              </li>
            </ul>""",
            },
            {
                "id": "materials-thc",
                "badge": "Cut Charts & THC",
                "title": "Materials, Kerf Void Protection &amp; Small Holes",
                "body_html": """
            <ul class="doc-bullet-list">
              <li>
                <strong>Inline Cut Chart (<code class="mono">(o=0, ...)</code>) vs. Catalog (<code class="mono">M190 P&lt;n&gt;</code> &rarr; <code class="mono">M66 P3 L3 Q2</code>):</strong>
                The two material modes are strictly mutually exclusive. Default inline mode writes the active cut chart in the header:
                <pre><code class="language-gcode">(o=0, na=45A Mild Steel 3mm, ph=3.8, pd=0.25, ch=1.5, fr=2800, kw=1.5, th=1, ca=45, cv=115, pe=0.5, gp=75, cm=1)</code></pre>
                Enabling <em>Use Controller Material Table</em> swaps to <code class="mono">M190 P&lt;n&gt;</code> + <code class="mono">M66 P3 L3 Q2</code> without emitting <code class="mono">(o=0, ...)</code>.
              </li>
              <li>
                <strong>Kerf Void &amp; Anti-Dive Lock (<code class="mono">M62 P1/P2</code> &amp; <code class="mono">M63 P1/P2</code>):</strong>
                When crossing cut voids or decelerating around corners, RotaryCAM emits <code class="mono">M62 P1</code> (Ignore Arc OK ON) and <code class="mono">M62 P2</code> (THC Disable ON), then restores checking and tracking with <code class="mono">M63 P1</code> and <code class="mono">M63 P2</code>.
              </li>
              <li>
                <strong>True Hole Velocity Scaling (<code class="mono">M67 E3 Q60</code> / <code class="mono">Q0</code>):</strong>
                On enclosed bolt holes <code class="mono">&le; 25.4 mm</code> (<code class="mono">1"</code>), <code class="mono">M67 E3 Q60</code> drops feed to 60% alongside THC lock, then <code class="mono">M67 E3 Q0</code> restores 100% feed at cut end.
              </li>
            </ul>""",
            },
            {
                "id": "checklist",
                "badge": "Checklist",
                "title": "LinuxCNC 2.9+ INI / HAL Commissioning Checklist",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong><code class="mono">[TRAJ] SPINDLES=3</code>:</strong> Enable 3 spindles in your <code class="mono">.ini</code> file so <code class="mono">M3 $0</code> (plasma), <code class="mono">M3 $1</code> (air scribe), and <code class="mono">M3 $2</code> (center spot) work without alarms.</li>
              <li><strong><code class="mono">[AXIS_Z] OFFSET_AV_RATIO=0.5</code> + Doubled Z Limits:</strong> Set <code class="mono">OFFSET_AV_RATIO = 0.5</code> and double your <code class="mono">[AXIS_Z]</code> <code class="mono">MAX_VELOCITY</code> (at least <code class="mono">&ge; 100 mm/s</code> so both G-code Z plunges and THC offsets keep <code class="mono">&ge; 50 mm/s</code> physical speed) and <code class="mono">MAX_ACCELERATION</code>.</li>
              <li><strong><code class="mono">[RS274NGC] HAL_PIN_VARS=1</code>:</strong> Required so <code class="mono">F#&lt;_hal[plasmac.cut-feed-rate]&gt;</code> can read QTPlasmaC's live cut speed pin in 2D flat-sheet programs.</li>
              <li><strong>Unrolled Pack Mode Clearance:</strong> Because rotary pack programs re-probe surface height on every part, verify hold-downs, tailstock pins, and chuck jaws clear the probe path between parts.</li>
            </ul>""",
            },
        ],
    },
    {
        "slug": "FireControl",
        "is_scribing": False,
        "name": "Langmuir Systems FireControl v1.6+ / v24.1.6",
        "short_name": "Langmuir FireControl",
        "ext": ".tap",
        "rotary_mode": "G94 Y-WRAP / X-WRAP (+ L_rev)",
        "ihs_summary": "G92 Z0 -> G38.2 -> G38.4 -> 0.020\" Backlash + Springback",
        "torch_summary": "M3 / M5 (>= 0.55s 3D ramp dwell + Post-Cut Settle)",
        "thc_summary": "H0 (Off) / H1 (On after ramp)",
        "sync_summary": "(v1.6-sc) header + (PS<feed>) strictly final line",
        "card_summary": "Hardened .tap output for CrossFire, PRO &amp; XR with dual G38.2/G38.4 IHS, 0.55s 3D ramp dwell &amp; Y/X-WRAP.",
        "badge_label": "CrossFire, PRO &amp; XR &bull; v1.6+ to v24.1.6 (.tap)",
        "meta_title": "FireControl v1.6+ / v24.1.6 Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "Langmuir FireControl setup for CrossFire, PRO, and XR: v1.6-sc sentinels, G38.2/G38.4 IHS probing, 0.55s ramp dwell, H0/H1 THC, and Y/X-WRAP.",
        "hero_title_html": 'Langmuir <span class="text-gradient-amber">FireControl Setup</span>',
        "subtitle_html": 'Hardened <code class="mono">.tap</code> output for CrossFire, CrossFire PRO, and CrossFire XR (<code class="mono">v1.6+</code> to <code class="mono">v24.1.6</code>) with two-stage <code class="mono">G38.2/G38.4</code> probing, <code class="mono">0.55 s</code> 3D ramp dwell, and <code class="mono">Y-WRAP</code> / <code class="mono">X-WRAP</code>.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.tap</code>'},
            {"style": "", "html": '<strong>Sentinels:</strong> <code class="mono">(v1.6-sc)</code> &amp; <code class="mono">(PS&lt;feed&gt;)</code>'},
            {"style": "", "html": '<strong>Rotary:</strong> 3-Axis <code class="mono">G94</code> <code class="mono">Y-WRAP</code> / <code class="mono">X-WRAP</code>'},
        ],
        "toc": [
            {"id": "ihs-ramp", "badge": "01", "label": "Dual-Stage IHS &amp; 0.55s Ramp Dwell"},
            {"id": "serial-hygiene", "badge": "02", "label": "Parser Sentinels &amp; Speed Caps"},
            {"id": "wrap-rotary", "badge": "03", "label": "Y-WRAP / X-WRAP &amp; L_rev Chuck"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G90 G94 / G17 / G20|G21", "desc": "Modal startup with H0"},
                    {"code": "G0 Z<safeZ>", "desc": "Retract to Safe Z"},
                    {"code": "G0 X<x> Y<y>", "desc": "Round pipe unwrapped to X-WRAP or Y-WRAP"},
                ],
                "note": "Caps speeds at 300 IPM XY and 150 IPM Z; filters < 0.025 mm (< 0.001\") micro-moves.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "H0 / G92 Z0", "desc": "Lock THC & zero before probe"},
                    {"code": "G38.2 Z-<d> F<probe>", "desc": "Fast touch-off probe down"},
                    {"code": "G38.4 Z12.7 F508", "desc": "Slow retract until switch opens"},
                    {"code": "G0 Z<0.508 + springback>", "desc": "0.020\" backlash (+ thin sheet springback)"},
                    {"code": "G92 Z0", "desc": "Establish true plate Z=0"},
                ],
                "note": "Springback auto-zeroes on pipe, tubing, and plate >= 3/16\" (4.7625 mm) so SMARTV reads true height.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "G0 Z<pierceH>", "desc": "Lift to pierce height"},
                    {"code": "M3", "desc": "Fire plasma torch"},
                    {"code": "G4 P<sec>", "desc": "Pierce + Arc Transfer + Loop 1 extra (>= 0.55s on 3D ramps)"},
                    {"code": "G1 Z<cutH> F<plunge>", "desc": "Plunge to cut height (or 3D ramp)"},
                    {"code": "H0", "desc": "Hold THC off across entry / ramp"},
                ],
                "note": "Mandatory >= 0.55s dwell on 3D ramps prevents 'Torch Moving Before Cutting Voltage Sensed' faults.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G1 / G2 / G3 X Y F<feed>", "desc": "G94 cut motion (Z omitted unless dynamic)"},
                    {"code": "H1", "desc": "Activate SMARTV THC on straight runs / post-ramp"},
                    {"code": "H0", "desc": "Disable THC in corners & small holes"},
                ],
                "note": "Refreshes modal F after plunges; dynamic Z emits relative (currZm - pierceZm) + cutHeight.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "H0", "desc": "Lock THC before M5"},
                    {"code": "M5", "desc": "Extinguish torch"},
                    {"code": "G4 P<postCutSec>", "desc": "Optional inverter post-flow settle dwell"},
                ],
                "note": "Post-Cut Settle Dwell lets inverters like Bestarc BTC800XP finish post-flow before next IHS.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G0 Z<safeZ>", "desc": "Retract to Safe Z clearance"},
                    {"code": "H0 / M30", "desc": "Disable THC & end program"},
                    {"code": "(PS<unscaled_feed>)", "desc": "Strictly final line for speed slider"},
                ],
                "note": "No A-axis unwind needed; (PS<feed>) keeps unscaled surface speed for FireControl's UI.",
            },
        ],
        "sections": [
            {
                "id": "ihs-ramp",
                "badge": "IHS & Ramps",
                "title": "Two-Stage IHS Backlash, Springback &amp; 0.55 s 3D Ramp Dwell",
                "body_html": """
            <p>
              FireControl's two-stage IHS probe (<code class="mono">G38.2</code> + <code class="mono">G38.4</code>) separates mechanical <code class="mono">0.020"</code> (<code class="mono">0.508 mm</code>) <strong>IHS Backlash</strong> from <strong>Thin-Sheet Springback</strong>. Springback automatically drops to <code class="mono">0</code> on rigid pipe, structural tubing, and heavy plate (<code class="mono">&ge; 3/16&Prime;</code> / <code class="mono">4.7625 mm</code>) so <code class="mono">SMARTV</code> never samples an inflated cut height:
            </p>
            <div class="doc-code-block">
              <div class="doc-code-bar">
                <span class="doc-code-title"><span class="dot"></span> FireControl Touch-Off &amp; 3D Ramp Sequence</span>
                <span class="doc-code-lang">GCODE (.tap)</span>
              </div>
              <pre><code>H0
G0 X25.000 Y10.000
G92 Z0
G38.2 Z-127.0 F2540.0   (Fast ohmic/switch touch probe down)
G38.4 Z12.7 F508.0      (Slow retract until switch un-trips)
G92 Z0
G0 Z0.508               (0.020 in IHS backlash + sheet springback if thin)
G92 Z0
G0 Z3.800               (Retract to Pierce Height)
M3                      (Torch Fire)
G4 P0.550               (Min 0.55s dwell on 3D ramps + Arc Transfer / Loop 1 extra)
G1 X27.500 Y10.000 Z1.500 F2800.0  (3D ramp or plunge with H0 held)
H1                      (THC Active only after reaching Cut Height)</code></pre>
            </div>
            <ul class="doc-bullet-list">
              <li><strong>0.55 s 3D Ramp Minimum Dwell:</strong> CrossFire Gen2 tables have no hardware Arc OK wire and look for cutting voltage shortly after <code class="mono">M3</code>. RotaryCAM enforces <code class="mono">&ge; 0.55 s</code> after <code class="mono">M3</code> on 3D ramps, holds <code class="mono">H0</code> across the diagonal ramp, and emits <code class="mono">H1</code> only at cut height.</li>
              <li><strong>Timing &amp; Settle Controls:</strong> Dial in <strong>Arc Transfer Latency</strong>, <strong>Loop 1 Extra Pierce Delay</strong>, and <strong>Post-Cut Settle Dwell</strong> (<code class="mono">G4 P</code> after <code class="mono">M5</code>).</li>
            </ul>""",
            },
            {
                "id": "serial-hygiene",
                "badge": "Parser Rules",
                "title": "Parser Sentinels &amp; GRBL Serial Hygiene",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Required Sentinels:</strong> Line 1 starts with <code class="mono">(v1.6-sc)</code> and the strict final line after <code class="mono">M30</code> emits <code class="mono">(PS&lt;feed&gt;)</code> (unscaled surface speed, e.g. <code class="mono">(PS110)</code> or <code class="mono">(PS2800)</code>) for FireControl's speed slider.</li>
              <li><strong>Comment &amp; Block Sanitization:</strong> Allows at most one <code class="mono">(...)</code> comment per line (nested parens become <code class="mono">[...]</code>; semicolons <code class="mono">;</code>, slashes <code class="mono">/</code>, <code class="mono">%</code>, and <code class="mono">#</code> are stripped).</li>
              <li><strong>Micro-Move &amp; Speed Caps:</strong> Filters <code class="mono">&lt; 0.025 mm</code> (<code class="mono">&lt; 0.001"</code>) micro-moves while preserving vertical plunges, refreshes modal feedrates after plunges, and caps CrossFire PRO/XR speeds at <code class="mono">300 IPM</code> XY and <code class="mono">150 IPM</code> Z.</li>
            </ul>""",
            },
            {
                "id": "wrap-rotary",
                "badge": "Rotary Wrap",
                "title": "Round-Tube Y-WRAP / X-WRAP &amp; Fixed-Calibration Chuck (L_rev)",
                "body_html": """
            <p>
              FireControl is a 3-axis (<code class="mono">X, Y, Z</code>) controller with no native 4th rotary axis (<code class="mono">A</code>) or <code class="mono">G93</code> mode. RotaryCAM unwraps round pipe into linear <code class="mono">G94</code> travel and prints <code class="mono">(FIRECONTROL ROTARY Y-WRAP: OD=...)</code> or <code class="mono">X-WRAP</code> in the header.
            </p>
            <ul class="doc-bullet-list">
              <li><strong>Tube Along Y (<code class="mono">X-WRAP</code>):</strong> On dual-Y CrossFire PRO/XR tables where shops swap the single <strong>X-axis motor</strong> onto the rotary, select <strong>Tube Along Y</strong> for automatic <code class="mono">X-WRAP</code> mapping.</li>
              <li><strong>Fixed-Calibration Chuck (<code class="mono">L_rev</code>):</strong> Enter your geared rotary's calibrated <strong>Travel / Rev (<code class="mono">L_rev</code>)</strong> to scale cylindrical <code class="mono">G94</code> DRO travel across any pipe diameter without changing FireControl steps/mm, while <code class="mono">(PS&lt;feed&gt;)</code> remains at true unscaled surface speed.</li>
            </ul>
            <div class="doc-callout warning">
              <div class="doc-callout-title">&#9888; Round Tubing Only on Motor-Swap Rotary</div>
              <p>
                Because a motor-swap setup replaces one lateral gantry axis with pipe rotation, the torch cannot translate sideways across a flat wall while rotating. Round pipe saddles, miters, and holes cut cleanly; square/rectangular HSS, angle iron, and C-channel require 4 independent axes (<code class="mono">X, Y, Z, A</code>).
              </p>
            </div>""",
            },
        ],
    },
    {
        "slug": "Mach4",
        "is_scribing": False,
        "name": "ArtSoft Mach4 + Warp9 ESS / TMC3in1",
        "short_name": "Mach4 + ESS / TMC3in1",
        "ext": ".tap",
        "rotary_mode": "G93 Inverse-Time (strokes only)",
        "ihs_summary": "G31.0-G31.3 + switch offset + G92 Z (+ m2020 Lua sync)",
        "torch_summary": "M62/M63 P3 + M65 P3 fail-safe (or OB1 m3/m5)",
        "thc_summary": "M63 P4 / M62 P4 (TMC3in1) or M63 P2 / M62 P2 (ESS)",
        "sync_summary": "W9_HC m2020 (...) + G04 P0.100 Lua sync",
        "card_summary": "Modal G90/G91.1 separation, G31.0-G31.3 + refDistance skip-probe, Output #4 TMC3in1 THC &amp; M62/M63 P3 torch.",
        "badge_label": "ArtSoft Mach4 &bull; Warp9 ESS &amp; TMC3in1 (.tap)",
        "meta_title": "Mach4 + Warp9 ESS / TMC3in1 Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "Mach4 + Warp9 ESS and TMC3in1 setup: G90/G91.1 mode split, G31 probing with refDistance, M62/M63 P3 torch vs m3/m5, Output #4 THC, and m2020.",
        "hero_title_html": 'ArtSoft Mach4 + <span class="text-gradient-amber">Warp9 ESS / TMC3in1</span>',
        "subtitle_html": 'Hardened <code class="mono">.tap</code> output for Standard ESS (Proma/PriceCNC) and Warp9 TMC3in1 / WarpRunner boards with clean <code class="mono">G31</code> probing, <code class="mono">m2020</code> Lua sync, and zero-pause <code class="mono">M62/M63</code> switching.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.tap</code>'},
            {"style": "", "html": '<strong>Pathways:</strong> TMC3in1 (<code class="mono">m2020</code> + <code class="mono">P4/P3</code>) / Standard ESS (<code class="mono">M62/M63</code> or <code class="mono">m3/m5</code>)'},
            {"style": "", "html": '<strong>Framing:</strong> <code class="mono">G92.1</code>, <code class="mono">M30</code>, <code class="mono">%</code>'},
        ],
        "toc": [
            {"id": "framing", "badge": "01", "label": "Preamble, G94/G93 &amp; Probing"},
            {"id": "ess-vs-tmc", "badge": "02", "label": "Standard ESS vs. TMC3in1 Setup"},
            {"id": "checklist", "badge": "03", "label": "Mach4 Hygiene &amp; Dwell Rules"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G94 F<feed>", "desc": "Linear positioning feed active"},
                    {"code": "G0 X<x> Y<y> A<a>", "desc": "Rapid at Safe Z to next pierce"},
                    {"code": "refDistance", "desc": "Tracks travel to skip close probes"},
                ],
                "note": "Preamble separates G00 G90 G17 G54 G40 G49 G80 and G91.1 onto two lines.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "G31.<0-3> Z<tgt> F<p>", "desc": "Probe on selected G31 channel"},
                    {"code": "G91 G00 Z<offset> / G90", "desc": "Incremental switch backoff"},
                    {"code": "G92 Z<datum>", "desc": "Set surface datum"},
                    {"code": "m2020 (HC_WORK_Z_ZEROED=1)", "desc": "TMC3in1 Lua sync + G04 P0.100"},
                ],
                "note": "Skips redundant probing inside refDistance unless a rotary unwind occurred.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "G0 Z<prePierce>", "desc": "Pre-pierce Z + G04 P0.0011 settle"},
                    {"code": "M63 P4 / M63 P2", "desc": "Lock THC (TMC3in1 P4 / ESS P2)"},
                    {"code": "M62 P3 / M3", "desc": "Synced M62 P3 torch ON (or OB1 M3)"},
                    {"code": "G1 Z<pierceZ> / G04 P<sec>", "desc": "Drop to pierce + dwell (or ESS delay)"},
                    {"code": "G1 Z<cutZ> F<plunge>", "desc": "3-step plunge to cut height"},
                ],
                "note": "In M62/M63 mode, M62 P3 fires synchronously on the G1 Z<pierceZ> motion block.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G93", "desc": "Inverse-time during rotary strokes"},
                    {"code": "M62 P4 / M63 P4", "desc": "TMC3in1 Output #4 active-low THC"},
                    {"code": "M62 P2 / M63 P2", "desc": "Standard ESS external THC unlock/lock"},
                ],
                "note": "4D dynamic-Z cuts and eccentric round bevels hold THC locked for the entire contour.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "M63 P4 / M63 P2", "desc": "Lock THC before extinguishing"},
                    {"code": "M63 P3 / M5", "desc": "Synced torch OFF (or OB1 M5)"},
                    {"code": "G91 G00 Z0.050 / G04 P<s>", "desc": "Optional post-cut Z micro-move + dwell"},
                ],
                "note": "Final cut segment splits cleanly before M5/M63 P3 when THC is unlocked.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G94 F<feed>", "desc": "Restore G94 before retract"},
                    {"code": "G0 Z<safeZ>", "desc": "Retract to Safe Z"},
                    {"code": "M65 P3", "desc": "Torch Fire Fail-Safe OFF (sync mode)"},
                    {"code": "G0 A<360*k> / G92 A0", "desc": "Modulo unwind (G92.1 at EOF + M30 + %)"},
                ],
                "note": "Modulo-360 resets mid-pack never call G92.1 so active G92 Z stays intact.",
            },
        ],
        "sections": [
            {
                "id": "framing",
                "badge": "Lifecycle & IHS",
                "title": "Preamble, G94/G93 Lifecycle &amp; G31.0-G31.3 Probing",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Separate <code class="mono">G90</code> &amp; <code class="mono">G91.1</code> Blocks:</strong> Emits <code class="mono">G00 G90 G17 G54 G40 G49 G80</code> followed by <code class="mono">G91.1</code> on its own line so Mach4 never rejects combined distance and arc-center modes.</li>
              <li><strong><code class="mono">G94</code> to <code class="mono">G93</code> Stroke Switching:</strong> Starts in <code class="mono">G94</code> for positioning and probing, switches to <code class="mono">G93</code> strictly during rotary cut strokes, and restores <code class="mono">G94 F&lt;feed&gt;</code> before retracts.</li>
              <li><strong><code class="mono">G31.0</code>-<code class="mono">G31.3</code> + Incremental Backoff:</strong> Probes on your chosen <code class="mono">G31.0</code>-<code class="mono">G31.3</code> input, backs off with <code class="mono">G91 G00 Z&lt;switchOffset&gt;</code> &rarr; <code class="mono">G90</code> &rarr; <code class="mono">G92 Z&lt;datum&gt;</code>, and skips redundant probes within <code class="mono">refDistance</code>.</li>
              <li><strong>Modulo-360 Wrap Resets &amp; EOF:</strong> Resets rotary wrap with <code class="mono">G92 A0.000</code> mid-pack without <code class="mono">G92.1</code>, then closes at EOF with <code class="mono">G92.1</code>, <code class="mono">M30</code>, and trailing <code class="mono">%</code>.</li>
            </ul>""",
            },
            {
                "id": "ess-vs-tmc",
                "badge": "ESS vs TMC3in1",
                "title": "Standard ESS Pathways vs. Warp9 TMC3in1 / WarpRunner",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Standard ESS Pathway A (Synced <code class="mono">M62/M63</code>):</strong> Fires/stops torch with <code class="mono">M62 P3</code> / <code class="mono">M63 P3</code> plus <code class="mono">M65 P3</code> fail-safe at retract, and toggles external THC (Proma 150, PriceCNC) via <code class="mono">M62 P2</code> / <code class="mono">M63 P2</code> without emitting <code class="mono">m2020</code>.</li>
              <li><strong>Standard ESS Pathway B (OB1 <code class="mono">m3/m5</code> Fallback):</strong> Uses standard <code class="mono">M3</code> / <code class="mono">M5</code> for OB1 relay boards without synced <code class="mono">M62/M63</code> outputs.</li>
              <li><strong>TMC3in1 Output #4 Active-Low THC (<code class="mono">M63 P4</code> Lock / <code class="mono">M62 P4</code> Unlock):</strong> Moves TMC3in1 THC lock to Output #4 active-low, avoiding legacy <code class="mono">P2</code> output conflicts.</li>
              <li><strong>Full <code class="mono">W9_HC</code> <code class="mono">m2020</code> Setup &amp; Rotary <code class="mono">AD3</code> Disable:</strong> Pushes <code class="mono">AD1</code> delay, voltage/deadband bands, ATV buffer, HC Z min/max, <code class="mono">ESS_DELAY_AFTER_ARC_OKAY</code>, <code class="mono">AD2_M62_M63_ENABLED=1</code>, and <code class="mono">TARGET_TIP_VOLTS</code> + <code class="mono">G04 P0.100</code>. Automatically forces <code class="mono">AD3_VELOCITY_ENABLED=0</code> on rotary cuts so <code class="mono">G93</code> speed changes never trip velocity anti-dive.</li>
              <li><strong>TMC3in1 Work-Z Sync &amp; 3-Step Drop:</strong> Emits <code class="mono">m2020 (HC_WORK_Z_ZEROED=1)</code> + <code class="mono">G04 P0.100</code> after probes (including EasyScribe) and executes a 3-step pierce drop with <code class="mono">G04 P0.0011</code> pre-pierce settle.</li>
            </ul>""",
            },
            {
                "id": "checklist",
                "badge": "Hygiene",
                "title": "Mach4 Macro Hygiene &amp; Dwell Rules",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Decimal-Second Dwells:</strong> All <code class="mono">G04 P&lt;sec&gt;</code> dwells emit in decimal seconds (e.g. <code class="mono">G04 P0.100</code>).</li>
              <li><strong>4D Dynamic-Z &amp; Post-Ramp Unlock:</strong> Keeps THC locked across 4D dynamic-Z tube cuts to prevent <code class="mono">HC Z Delta</code> desync, and unlocks THC only after 3D ramp lead-ins reach cut height.</li>
              <li><strong>Pneumatic Scribe:</strong> Supports <code class="mono">G52 X&lt;dx&gt; Y&lt;dy&gt;</code> work-offset shifts for pneumatic air scribes, cancelled cleanly before plasma cuts.</li>
            </ul>""",
            },
        ],
    },
    {
        "slug": "MASSO",
        "is_scribing": False,
        "name": "MASSO G3 + DTHC v5.x",
        "short_name": "MASSO G3 + DTHC",
        "ext": ".nc",
        "rotary_mode": "G93 Inverse-Time",
        "ihs_summary": "G200 + M3 (Auto-IHS) or Bare G200 + G38.2 (4D / Ext THC)",
        "torch_summary": "M3 / M5 (T112 M6 Plasma | T111 M6 Scribe)",
        "thc_summary": "M666 (Off) / M667 F<zFeed> (On, F always required)",
        "sync_summary": "G200 F P D<ms> C V A0 O<0|1> S<0|1>",
        "card_summary": "T112 M6 plasma mode, 3 THC modes, mandatory M667 F<zFeed> anti-dive, Bare G200 vs Hybrid C=P ramps &amp; modulo-360 A reset.",
        "badge_label": "MASSO G3 &amp; Touch &bull; DTHC v5.x (.nc)",
        "meta_title": "MASSO G3 + DTHC v5.x Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "MASSO G3 + DTHC v5.x setup guide: 3 THC hardware modes, G200 probing, M667/M666 anti-dive, Hybrid C=P 3D ramps, Template C HSS, and M30 L feed.",
        "hero_title_html": 'MASSO G3 + <span class="text-gradient-amber">DTHC Setup</span>',
        "subtitle_html": 'Hardened <code class="mono">.nc</code> output built around MASSO firmware rules: <code class="mono">T112 M6</code> plasma mode, <code class="mono">G200</code> / <code class="mono">G38.2</code> probing, buffered <code class="mono">M666</code> / <code class="mono">M667 F&lt;thcFeed&gt;</code> anti-dive, and integer-millisecond dwells.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.nc</code>'},
            {"style": "", "html": '<strong>Dwell Units:</strong> Integer <code class="mono">ms</code> (<code class="mono">D400</code>, <code class="mono">G04 P400</code>)'},
            {"style": "", "html": '<strong>Tools:</strong> <code class="mono">T112 M6</code> Plasma &bull; <code class="mono">T111 M6</code> Air Scribe'},
        ],
        "toc": [
            {"id": "thc-modes", "badge": "01", "label": "3 THC Modes &amp; G200 Rules"},
            {"id": "ramps-hss", "badge": "02", "label": "3D Ramps (B2 vs B1) &amp; 4D HSS"},
            {"id": "checklist", "badge": "03", "label": "F1 Setup &amp; Bar-Advance Checklist"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G53 G0 Z0 / T112 M6", "desc": "Home Z & select MASSO Plasma Tool 112"},
                    {"code": "G200 ... / G200", "desc": "Parameterized G200 or Bare G200"},
                    {"code": "G0 X<x> Y<y> A<a>", "desc": "Rapid at Safe Z (omitted before #1 in G200 Auto-IHS)"},
                ],
                "note": "Auto-IHS skips Safe Z before feature #1 because work Z=0 is unset until the first M3.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "M3 (G200 Auto-IHS)", "desc": "O0 Touch Switch or O1 Ohmic probing"},
                    {"code": "G38.2 Z<tgt> F<p>", "desc": "Bare G200 (4D HSS / Ext THC / Option B2 ramps)"},
                    {"code": "G92 Z0 / G0 Z<off> / G92 Z", "desc": "Switch offset compensation"},
                ],
                "note": "Bare G200 cancels canned auto-IHS so 4D HSS, bevels, and 3D ramps keep explicit Z control.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "G0 Z<pierceH>", "desc": "Bare G200 lifts to pierce height"},
                    {"code": "M3", "desc": "Fire torch (G200 runs P, D<ms>, C internally)"},
                    {"code": "G04 P<ms>", "desc": "Bare G200 integer ms dwell (>= 400ms on ramps)"},
                    {"code": "M666", "desc": "Lock DTHC for lead-in / ramp / 4D Z"},
                    {"code": "G1 Z<cutH> F<plunge>", "desc": "Plunge to cut height (non-ramp)"},
                ],
                "note": "Hybrid Option B1 sets C=P inside G200 so M3 holds at pierce height before ramping down.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G93", "desc": "Inverse-time rotary cut strokes"},
                    {"code": "M667 F<thcFeed>", "desc": "DTHC ON (F word ALWAYS included: 75-600 mm/min)"},
                    {"code": "M666", "desc": "DTHC OFF on corners, small holes, 4D HSS"},
                ],
                "note": "Omitting F on M667 breaks THC Z tracking on MASSO; RotaryCAM always emits M667 F<zFeed>.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "M666", "desc": "Lock DTHC before torch off"},
                    {"code": "M5", "desc": "Extinguish plasma arc"},
                    {"code": "G94", "desc": "Restore G94 before Safe Z retract"},
                ],
                "note": "Final cut segment splits cleanly before M5 when DTHC is active.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G0 Z<safeZ> / G92.1", "desc": "Retract & clear temporary Z offset"},
                    {"code": "G53 G0 Z0", "desc": "EOF retract to machine Z top"},
                    {"code": "G92 A<mod_360>", "desc": "Safe modulo-360 A reset (no G28 A)"},
                    {"code": "M30 / M30 L<count>", "desc": "End or chuck-fed bar-advance loop"},
                ],
                "note": "Uses safe modulo-360 A-axis software resets instead of mechanical G28 A homing on clamped tubes.",
            },
        ],
        "sections": [
            {
                "id": "thc-modes",
                "badge": "THC & G200",
                "title": "3 THC Hardware Modes, G200 Probing &amp; Mandatory M667 F",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>MASSO DTHC (<code class="mono">G200</code> Auto-IHS):</strong> Emits full <code class="mono">G200 F&lt;probe&gt; P&lt;pierce&gt; D&lt;ms&gt; C&lt;cut&gt; V&lt;volts&gt; A0 O&lt;0|1&gt; S&lt;0|1&gt;</code> blocks on flat sheet and round pipe. <code class="mono">O0</code> selects Touch Switch; <code class="mono">O1</code> selects Plasma Ohmic; <code class="mono">S0</code> runs continuous; <code class="mono">S1</code> pauses for Slag-Stop.</li>
              <li><strong>External Up/Down THC (Bare <code class="mono">G200</code> + <code class="mono">G38.2</code>):</strong> Cancels canned auto-IHS with a bare <code class="mono">G200</code> line, probes with <code class="mono">G38.2</code>, and drives pierce-to-cut Z moves directly.</li>
              <li><strong>Fixed Height / No THC:</strong> Uses <code class="mono">M666</code> locked height (never emitting <code class="mono">M667</code>) so the torch holds programmed Z cut height.</li>
              <li><strong>Mandatory <code class="mono">M667 F&lt;thcFeed&gt;</code> &amp; <code class="mono">M666</code> Anti-Dive:</strong> MASSO firmware does not implement the <code class="mono">A</code> anti-dive percentage inside <code class="mono">G200</code>. RotaryCAM emits buffered <code class="mono">M666</code> / <code class="mono">M667 F&lt;thcFeed&gt;</code> (<code class="mono">75-600 mm/min</code> in <code class="mono">G21</code>, or <code class="mono">3-24 IPM</code> in <code class="mono">G20</code>).</li>
            </ul>""",
            },
            {
                "id": "ramps-hss",
                "badge": "3D & 4D Rules",
                "title": "3D Ramp Lead-Ins (Option B2 vs. Hybrid B1) &amp; Template C 4D HSS",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Option B2 (Bare <code class="mono">G200</code> 3D Ramps, Default):</strong> Drops canned <code class="mono">G200</code> parameters and runs explicit <code class="mono">G38.2</code>, <code class="mono">M3</code>, <code class="mono">G04 P&lt;ms&gt;</code>, and a diagonal XYZ ramp to cut height without MASSO overriding Z.</li>
              <li><strong>Opt-In Option B1 (Hybrid <code class="mono">C=P</code>):</strong> Sets <code class="mono">G200</code> cut height equal to pierce height (<code class="mono">C=P</code>) so MASSO runs auto-IHS and ignites at pierce height before ramping down under <code class="mono">M666</code>. Requires explicit target voltage (<code class="mono">V &gt; 0</code>, never <code class="mono">V0</code> auto-sampling).</li>
              <li><strong>Template C (Continuous 4D HSS Tubes):</strong> Square/rectangular tubes and eccentric bevels run <code class="mono">Bare G200</code> + <code class="mono">G38.2</code> + <code class="mono">G92 Z</code> + <code class="mono">G92.1</code> + <code class="mono">M666</code> so 4D Z corner climbs track cleanly.</li>
            </ul>""",
            },
            {
                "id": "checklist",
                "badge": "F1 Checklist",
                "title": "MASSO F1-Setup Checklist &amp; Bar-Advance Looping",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Keep <code class="mono">T112 M6</code> for Plasma (<code class="mono">T111 M6</code> for Air Scribe):</strong> Switching away from <code class="mono">T112</code> exits MASSO plasma mode; zero out multi-head X/Y/Z tool offsets on <code class="mono">T112</code> in F1 Setup.</li>
              <li><strong>Millisecond Dwells:</strong> Both <code class="mono">D</code> in <code class="mono">G200</code> and <code class="mono">G04 P</code> run in integer milliseconds (<code class="mono">D400</code> = 0.4 s).</li>
              <li><strong>Firmware Version:</strong> Avoid <code class="mono">v5.100b BETA Phase 1</code> firmware.</li>
              <li><strong>Bar-Advance Looping (<code class="mono">M30 L&lt;count&gt;</code>):</strong> On single-part rotary jobs, enable <code class="mono">M30 L&lt;count&gt;</code> to park at <code class="mono">X0 Y0 A0</code>, prompt to advance the bar to the stop, and loop cleanly.</li>
            </ul>""",
            },
        ],
    },
    {
        "slug": "Mach3",
        "is_scribing": False,
        "name": "ArtSoft Mach3 R3.043.062",
        "short_name": "ArtSoft Mach3",
        "ext": ".tap",
        "rotary_mode": "G93 Inverse-Time (Use Radius OFF)",
        "ihs_summary": "G31 (ESS 100-127 mm) or G28.1 Z (LPT) + G92 Z",
        "torch_summary": "M3 / M5 + immediate G94 restore",
        "thc_summary": "M11Px/M10Px, CandCNC S900/S10/S20, M102/M101, or M7/M9",
        "sync_summary": "(CONFIG: ...) header + one-click .xml setup import",
        "card_summary": "4 THC hardware topologies, ESS G31 vs LPT G28.1 probing, G54-baked scribe offsets, % framing &amp; .xml import.",
        "badge_label": "ArtSoft Mach3 R3.043.062 &bull; ESS / CandCNC / Proma (.tap)",
        "meta_title": "ArtSoft Mach3 R3.043.062 Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "ArtSoft Mach3 R3.043.062 setup: 4 THC wiring modes, ESS G31 vs LPT G28.1 probing, G93 Use Radius rules, .xml profile import, and 6-phase cut cycle.",
        "hero_title_html": 'ArtSoft Mach3 <span class="text-gradient-amber">R3.043.062 Setup</span>',
        "subtitle_html": 'Hardened <code class="mono">.tap</code> output for Mach3 tables with 4 THC hardware topologies, <code class="mono">G31</code> ESS probing, <code class="mono">G54</code>-baked scribe offsets, and one-click <code class="mono">.xml</code> setup import.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.tap</code>'},
            {"style": "", "html": '<strong>XML Importer:</strong> Auto-fills units, XYZA limits &amp; <a href="#import-warnings-faq" style="color: var(--cyan-400); text-decoration: underline;">Import Warnings FAQ</a>'},
            {"style": "", "html": '<strong>Framing:</strong> <code class="mono">%</code> &hellip; <code class="mono">M30 / %</code>'},
        ],
        "toc": [
            {"id": "thc-topologies", "badge": "01", "label": "4 Mach3 THC Hardware Topologies"},
            {"id": "probing-g93", "badge": "02", "label": "ESS G31 Probing &amp; G54 Scribing"},
            {"id": "checklist", "badge": "03", "label": "Mach3 R3.043.062 Console Checklist"},
            {"id": "import-warnings-faq", "badge": "FAQ", "label": "Mach3 (.xml) Import Warnings FAQ"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G90 G91.1 G17 G40 G49 G64", "desc": "Incremental IJ + CV without syntax-breaking P"},
                    {"code": "G94", "desc": "Units-per-minute positioning"},
                    {"code": "G0 X<x> Y<y> A<a>", "desc": "Rapid at Safe Z (0.002 mm G93 deadband)"},
                ],
                "note": "Header prints (CONFIG: ...) checklist summarizing dwell, LookAhead, Use Radius, and THC pins.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "G31 Z<tgt> F<probe>", "desc": "ESS Straight Probe (set 100-127 mm / 4-5\" depth)"},
                    {"code": "G28.1 Z10", "desc": "LPT floating-head homing (legacy option)"},
                    {"code": "G92 Z0 / G0 Z<off> / G92 Z", "desc": "Switch offset compensation"},
                ],
                "note": "Proma Compact SD forces G31 touch-off before every single pierce.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "G0 Z<pierceH>", "desc": "Move to pierce height"},
                    {"code": "M102 / M101 or M7", "desc": "Pre-M3 lock (Proma150/SD) if required"},
                    {"code": "M3 / G04 P<sec>", "desc": "Fire torch + decimal-second dwell"},
                    {"code": "G1 Z<cutH> F<plunge>", "desc": "Plunge to cut height"},
                    {"code": "M11 P# / M10 P#", "desc": "Synced M11/M10 lock (after plunge or G93)"},
                ],
                "note": "In M11/M10 mode, RotaryCAM emits G93 before M11 so synced pin fires cleanly on first cut move.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G93", "desc": "Inverse-time rotary cut strokes"},
                    {"code": "M10 P# / M11 P#", "desc": "Motion-synced zero-pause THC (Pins 1-6)"},
                    {"code": "S20 / S10", "desc": "CandCNC DTHC DCC zero-pause toggle"},
                ],
                "note": "Proma 150/TMC3in1 and Proma SD disable mid-contour modulation on holes, ramps, and 4D cuts.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "S10 / S20", "desc": "CandCNC DTHC OFF before M5 if unlocked"},
                    {"code": "M5", "desc": "Extinguish plasma arc"},
                    {"code": "G94", "desc": "Immediate G94 restore after M5"},
                    {"code": "M102 / M9", "desc": "Proma150 lock / Proma SD bypass OFF"},
                ],
                "note": "Never leaves a stranded M11 immediately before M5.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G0 Z<safeZ>", "desc": "Retract to Safe Z clearance"},
                    {"code": "G94", "desc": "Restore G94 for footer"},
                    {"code": "M30 / %", "desc": "% framing with trailing newline"},
                ],
                "note": "Pneumatic scribe offsets bake directly into G54 coordinates to avoid G52 vs G92 register conflicts.",
            },
        ],
        "sections": [
            {
                "id": "thc-topologies",
                "badge": "THC Topologies",
                "title": "4-Topology Mach3 THC Hardware Selector",
                "body_html": """
            <p>
              Standard <code class="mono">M101/M102</code> VBScript macros force Mach3 to stop dead before toggling pins, burning blowout holes. Pick the topology matching your cabinet:
            </p>
            <ul class="doc-bullet-list">
              <li><strong><code class="mono">M11Px / M10Px</code> Motion-Synced (Pins 1-6 + Polarity Invert):</strong> Fires <code class="mono">M11 P#</code> / <code class="mono">M10 P#</code> at the exact microsecond the next axis move starts. Emits <code class="mono">G93</code> before <code class="mono">M11</code> and never strands <code class="mono">M11</code> before <code class="mono">M5</code>.</li>
              <li><strong>CandCNC DTHC DCC (<code class="mono">S900/S10/S20</code> + Optional <code class="mono">S3xx</code> Voltage + Polarity Invert):</strong> Commands CandCNC digital THC lock, unlock, and target arc voltage via <code class="mono">S</code> words without motion pauses.</li>
              <li><strong>ESS Proma 150 / TMC3in1:</strong> Emits stationary <code class="mono">M102/M101</code> before <code class="mono">M3</code> and forces <code class="mono">M102</code> lock on small bolt holes, 3D ramps, and 4D rotary cuts.</li>
              <li><strong>ESS Proma Compact THC SD:</strong> Enforces <code class="mono">G31</code> touch-off on every pierce and toggles the auxiliary bypass relay (<code class="mono">M7/M9</code>) on holes, ramps, and 4D cuts.</li>
            </ul>""",
            },
            {
                "id": "probing-g93",
                "badge": "Probing & Framing",
                "title": "ESS G31 Probing, Bowed Stock &amp; G54 Scribe Offsets",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>ESS <code class="mono">G31</code> vs. LPT <code class="mono">G28.1</code>:</strong> On a Warp9 Ethernet SmoothStepper (ESS), always use <code class="mono">G31</code> Straight Probe instead of legacy <code class="mono">G28.1</code> (which can hang ESS). Set probe search depth to <strong><code class="mono">100-127 mm</code> (<code class="mono">4-5 in</code>)</strong> so touch-offs never air-fault on bowed sheet or warped tubing.</li>
              <li><strong><code class="mono">G54</code> Scribe Offsets &amp; <code class="mono">%</code> Framing:</strong> Every <code class="mono">.tap</code> file wraps with <code class="mono">%</code> framing and <code class="mono">M30\\n%\\n</code>, restores <code class="mono">G94</code> immediately after <code class="mono">M5</code>, filters sub-<code class="mono">0.002 mm</code> (<code class="mono">0.0001 in</code>) <code class="mono">G93</code> noise, and bakes pneumatic scribe XY offsets into <code class="mono">G54</code> coordinates (zero <code class="mono">G52</code> vs. <code class="mono">G92</code> conflict).</li>
            </ul>""",
            },
            {
                "id": "checklist",
                "badge": "Console Checklist",
                "title": "Mach3 R3.043.062 Console Checklist &amp; .xml Import",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>One-Click <code class="mono">.xml</code> Import:</strong> Click <span class="ui-chip">Import Mach3 Setup (.xml)</span> in the Machines modal to auto-fill units and XYZA limits. Any flagged warnings link straight to the <a href="#import-warnings-faq" style="color: var(--cyan-400);">Mach3 XML Import Warnings FAQ</a> below.</li>
              <li><strong>Licensed <code class="mono">R3.043.062</code>:</strong> Run an active license (Demo mode caps at 500 lines and can drop rotary motion).</li>
              <li><strong>Dwells &amp; Trajectory Blending:</strong> Leave <code class="mono">G04 Dwell in ms</code> <strong>UNCHECKED</strong>, set <strong>LookAhead</strong> to <code class="mono">200</code>, uncheck <strong>Plasma Mode</strong> and <strong>CV Dist Tolerance</strong>, and keep <strong>CV Feedrate OFF</strong>.</li>
              <li><strong><code class="mono">Use Radius for Feedrate</code> Rule:</strong> Keep <strong>Use Radius for Feedrate UNCHECKED</strong> during <code class="mono">G93</code> rotary cuts (and uncheck <code class="mono">Rot 360 rollover</code> &amp; <code class="mono">Ang Short Rot on G0</code>).</li>
            </ul>""",
            },
        ],
    },
    {
        "slug": "Acorn",
        "is_scribing": False,
        "name": "Centroid Acorn CNC12 v5.4+",
        "short_name": "Centroid Acorn CNC12",
        "ext": ".nc",
        "rotary_mode": "G94 (2D) / G93.1 Smoothed (3D/4D)",
        "ihs_summary": "2D: M61 (0 Z words) | 3D/4D: M150 (M115 + G92 Z)",
        "torch_summary": "2D: M61 / M62 | 3D/4D: M3 / M5",
        "thc_summary": "2D: 15% Voltage Anti-Dive | 3D/4D: M36 Hold (M35 unlock)",
        "sync_summary": "G64 ON + M65 + ; comments (0 parens) + P220=1/P225=1",
        "card_summary": "Dual-regime CNC12 v5.4+ post: canned M61/M62 2D plate vs. M150/M36/G93.1 3D &amp; 4D rotary with semicolon-only comments.",
        "badge_label": "Centroid Acorn &amp; AcornSix &bull; CNC12 v5.4+ (.nc)",
        "meta_title": "Centroid Acorn CNC12 v5.4+ Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "Centroid Acorn CNC12 v5.4+ setup guide: 2D M61/M62 zero-Z vs 3D/4D M150 macro, M36 ATHC Hold, G93.1 inverse-time, Dual-Y AcornSix, and P220/P225.",
        "hero_title_html": 'Centroid Acorn <span class="text-gradient-amber">CNC12 v5.4+ Setup</span>',
        "subtitle_html": 'Two native <code class="mono">.nc</code> regimes for Acorn and AcornSix: hands-off <code class="mono">M61/M62</code> canned macros on 2D plate, and explicit <code class="mono">M150</code> + <code class="mono">M36</code> ATHC hold + <code class="mono">G93.1</code> smoothed inverse-time on 3D ramps and 4D rotary tubing.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.nc</code>'},
            {"style": "", "html": '<strong>Comments:</strong> Semicolon <code class="mono">;</code> ONLY (0 parens)'},
            {"style": "", "html": '<strong>Parameters:</strong> <code class="mono">P220=1</code> &bull; <code class="mono">P225=1</code>'},
        ],
        "toc": [
            {"id": "regimes", "badge": "01", "label": "Regime A (2D) vs. Regime B (3D/4D)"},
            {"id": "checklist", "badge": "02", "label": "CNC12 v5.4+ Commissioning Checklist"},
            {"id": "marking", "badge": "03", "label": "Center Dimple (M64) &amp; Scribe (M39/M40)"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G64 ON / M65", "desc": "Plasma smoothing + load CNC12 Profile"},
                    {"code": "M36 ; Hold ATHC", "desc": "Regime B (3D/4D) holds ATHC before motion"},
                    {"code": "G0 X<x> Y<y> A<a>", "desc": "Rapid (zero Z words on Regime A 2D)"},
                ],
                "note": "Regime B sets G54 centerline Z=0 (optional) and retracts to Safe Z; Regime A emits zero Z words.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "M61 (Regime A 2D)", "desc": "CNC12 M61 owns touch-off & pierce"},
                    {"code": "M150 ; Touch-off", "desc": "Regime B calls mfunc150.mac (M115 probe)"},
                    {"code": "G92 Z<datum + offset>", "desc": "Zero Z at surface or centerline"},
                ],
                "note": "M150 prevents M61 from hijacking your Z datum on 3D ramps and 4D HSS corners.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "G0 Z<pierceH>", "desc": "Regime B moves to pierce height"},
                    {"code": "M36 ; Hold ATHC", "desc": "Lock Auto THC before ignition"},
                    {"code": "M3 / G4 P<sec>", "desc": "Fire torch + dwell [0.01, 327.67] s"},
                    {"code": "G1 Z<cutH> F<plunge>", "desc": "Regime B plunge to cut height"},
                ],
                "note": "Regime A delegates touch-off, pierce, dwell, and cut height drop entirely to M61.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G94 (2D) / G93.1 (3D/4D)", "desc": "Smoothed G93.1 inverse-time on rotary"},
                    {"code": "M36 ; Hold ATHC", "desc": "Regime B holds ATHC across 3D/4D cuts"},
                    {"code": "15% Anti-Dive (2D)", "desc": "CNC12 internal voltage anti-dive"},
                ],
                "note": "Regime B sets explicit Z = zOrigin + currZm + cutHeight; M35 unlocks ATHC when needed.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "M62 (Regime A 2D)", "desc": "CNC12 torch off + retract macro"},
                    {"code": "G94 F<feed>", "desc": "Regime B restores G94 BEFORE M5"},
                    {"code": "M5", "desc": "Regime B torch off"},
                ],
                "note": "Restoring G94 before M5 ensures rotary mode never bleeds into retract or next M150 probe.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G0 Z<safeZ>", "desc": "Regime B retract (omitted on Regime A)"},
                    {"code": "G0 A<360*k> / G92 A0", "desc": "Exact 360 deg rotary unwind"},
                    {"code": "G64 OFF / M30", "desc": "Disable plasma smoothing & end program"},
                ],
                "note": "Entire file uses semicolon ; comments strictly with zero parentheses anywhere.",
            },
        ],
        "sections": [
            {
                "id": "regimes",
                "badge": "Two Regimes",
                "title": "Regime A (2D Flat Plate) vs. Regime B (3D Ramps &amp; 4D Rotary)",
                "body_html": """
            <ul class="doc-bullet-list">
              <li>
                <strong>Regime 1: 2D Flat Plate (<code class="mono">G64 ON</code>, <code class="mono">M65</code>, <code class="mono">M61/M62</code>, Zero Z Words):</strong>
                Emits <code class="mono">G64 ON</code> smoothing and <code class="mono">M65</code> to load your CNC12 Material Profile, then calls <code class="mono">M61</code> (probe, pierce, dwell, cut height) and <code class="mono">M62</code> (arc off, retract) with zero <code class="mono">Z</code> words and CNC12's 15% Voltage Anti-Dive active.
              </li>
              <li>
                <strong>Regime 2: 3D Ramps &amp; 4D Rotary (<code class="mono">Z=0</code> Centerline, <code class="mono">M150</code>, <code class="mono">M36</code>, <code class="mono">G93.1</code>):</strong>
                References tube centerline <code class="mono">Z=0</code> under <code class="mono">G54</code>, probes via <code class="mono">M150</code> (<code class="mono">mfunc150.mac</code>: <code class="mono">M115</code> + <code class="mono">G92 Z</code>), holds ATHC with <code class="mono">M36</code> before <code class="mono">M3</code>, cuts rotary strokes in smoothed <code class="mono">G93.1</code> inverse-time, and restores <code class="mono">G94</code> before <code class="mono">M5</code>. Outputs standalone <code class="mono">G4 P</code> dwells, 360&deg; <code class="mono">G92 A0</code> resets, and semicolon <code class="mono">;</code> comments only.
              </li>
            </ul>""",
            },
            {
                "id": "checklist",
                "badge": "Checklist",
                "title": "CNC12 v5.4+ Commissioning Checklist",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>License Tier (Plasma Pro / Ultimate):</strong> Free/base CNC12 caps files at <code class="mono">50 KB</code>. Rotary HSS and saddle jobs routinely exceed <code class="mono">50 KB</code>, so run <strong>CNC12 Plasma Pro</strong> or <strong>Ultimate</strong>.</li>
              <li><strong>AcornSix for Dual-Y + A:</strong> Standard 4-axis Acorn boards run out of motor channels on Dual-Y gantries with a rotary chuck. Use <strong>Centroid AcornSix</strong> whenever pairing Dual-Y motors with an <code class="mono">A</code> axis.</li>
              <li><strong><code class="mono">mfunc150.mac</code> Setup:</strong> Install <code class="mono">mfunc150.mac</code> in your CNC12 macro folder strictly on <code class="mono">M115</code> + <code class="mono">G92 Z</code> (avoid <code class="mono">M38</code> Laser Interlock or reserved <code class="mono">OUTPUT1-5</code> relays).</li>
              <li><strong>Onboard Fast Inputs (~5 ms vs. Ether1616 ~100 ms):</strong> Wire touch-off and Arc OK to <strong>Acorn onboard fast inputs</strong> (~<code class="mono">5 ms</code>) rather than Ether1616 (~<code class="mono">100 ms</code>) so <code class="mono">M115</code> stops immediately on contact.</li>
              <li><strong>Parameters (<code class="mono">P220=1</code> &amp; <code class="mono">P225=1</code>):</strong> Set <code class="mono">P220=1</code> and <code class="mono">P225=1</code> in CNC12 Setup Parameters for smoothed <code class="mono">G93.1</code> and plasma macro timing.</li>
            </ul>""",
            },
            {
                "id": "marking",
                "badge": "Scribing & Dimples",
                "title": "Center-Point Dimples (<code class=\"mono\">M64</code>) &amp; Pneumatic Scribe (<code class=\"mono\">M39/M40</code>)",
                "body_html": """
            <p>
              <code class="mono">M64</code> triggers CNC12's automated low-power plasma center-point dimple cycle, while <code class="mono">M39</code> (extend and apply offset) and <code class="mono">M40</code> (retract) drive pneumatic air scribes. Scribe offsets bake directly into <code class="mono">G54</code> coordinates when needed.
            </p>""",
            },
        ],
    },
    {
        "slug": "grblHAL",
        "is_scribing": False,
        "name": "grblHAL 32-Bit Plasma + Rotary",
        "short_name": "grblHAL 32-Bit Plasma",
        "ext": ".nc",
        "rotary_mode": "G94 (2D / Y-Wrap) / G93 (4-Axis)",
        "ihs_summary": "G38.2 + switch offset + G92 Z (M190 P-1 explicit CAM Z)",
        "torch_summary": "M3 / M5 + G94 F (+ M65 P3 inhibit clear)",
        "thc_summary": "$674 P2: M64/M62 P2 (Lock) / M63/M65 P2 (Enable)",
        "sync_summary": "M190 P-1 + M68/M67 E3 feed override + $674 virtual ports",
        "card_summary": "Standalone-line $674 virtual ports (P2/P3/E3), M190 P-1 explicit Z, Core #1027 G94-before-G38.2 safety &amp; <= 80-char blocks.",
        "badge_label": "Teensy 4.1, ESP32, STM32, RP2040 &bull; Core 20261015+ (.nc)",
        "meta_title": "grblHAL 32-Bit Plasma + Rotary Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "grblHAL 32-bit plasma and rotary setup: $674 virtual ports P2/P3/E3, M190 P-1 Z, Core #1027 M5 safety, EEPROM settings ($376/$133), and Y-wrap.",
        "hero_title_html": 'grblHAL <span class="text-gradient-amber">32-Bit Plasma + Rotary</span>',
        "subtitle_html": 'Hardened <code class="mono">.nc</code> output for grblHAL core <code class="mono">20261015+</code> and Nov 2026+ <code class="mono">Plugin_plasma</code> with standalone <code class="mono">$674</code> virtual-port blocks, <code class="mono">M190 P-1</code> explicit Z, and <code class="mono">G93</code>/<code class="mono">G94</code> safety.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.nc</code>'},
            {"style": "", "html": '<strong>Virtual Ports (<code class="mono">$674</code>):</strong> <code class="mono">P2</code> THC &bull; <code class="mono">P3</code> Inhibit &bull; <code class="mono">E3</code> Feed'},
            {"style": "", "html": '<strong>Line Limit:</strong> <code class="mono">&le; 80</code> chars (<code class="mono">? ! ~</code> stripped)'},
        ],
        "toc": [
            {"id": "virtual-ports", "badge": "01", "label": "$674 Virtual Ports (Standalone Blocks)"},
            {"id": "z-safety", "badge": "02", "label": "M190 P-1 Z &amp; Core #1027 Safety"},
            {"id": "checklist", "badge": "03", "label": "EEPROM &amp; Serial Checklist"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "M190 P-1 / M65 P3", "desc": "Explicit CAM Z + clear torch inhibit"},
                    {"code": "M68 E3 Q100", "desc": "Ensure 100% feedrate override"},
                    {"code": "G0 X<x> Y<y> A<a>", "desc": "Rapid at Safe Z (or Y-wrap linear)"},
                ],
                "note": "Every M-code sits on its own line (combining M-codes triggers grblHAL error:36).",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "G94 F<feed>", "desc": "Ensure G94 before probing"},
                    {"code": "G38.2 Z<tgt> F<probe>", "desc": "Touch-off probe down"},
                    {"code": "G92 Z0 / G0 Z<off> / G92 Z", "desc": "Switch offset compensation"},
                ],
                "note": "M190 P-1 keeps Plugin_plasma pierce_height=0 so CAM owns all Z probing & heights.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "G0 Z<pierceH>", "desc": "Move to pierce height"},
                    {"code": "M64 P2", "desc": "Immediate THC Lock (or M63 P0 legacy)"},
                    {"code": "M67 E3 Q60", "desc": "Synced 60% speed on small holes"},
                    {"code": "M3 / G4 P<sec>", "desc": "Fire torch + float-second dwell"},
                    {"code": "G1 Z<cutH> F<plunge>", "desc": "Plunge to cut height (non-ramp)"},
                ],
                "note": "Enters G93 on rotary jobs immediately after plunge/pierce.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G93 / G94", "desc": "G93 inverse-time on 4-axis rotary"},
                    {"code": "M63 P2 / M62 P2", "desc": "Synced THC unlock / corner lock"},
                    {"code": "M64 P2 (3D/4D)", "desc": "Continuous hold on ramps & 4D HSS"},
                ],
                "note": "3D ramps and 4D HSS lock THC for the full feature so voltage never fights Z.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "M64 P2", "desc": "Lock THC if unlocked"},
                    {"code": "M68 E3 Q100", "desc": "Restore 100% feed if small hole"},
                    {"code": "M5", "desc": "Extinguish plasma arc"},
                    {"code": "G94 F<feed>", "desc": "Immediate G94 restore after G93"},
                ],
                "note": "Immediate G94 F after M5 avoids grblHAL Core Issue #1027 (G38.2 crash in G93 mode).",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G0 Z<safeZ>", "desc": "Retract to Safe Z"},
                    {"code": "G92 A<mod_360>", "desc": "Modulo-360 reset (zero G92.1)"},
                    {"code": "M65 P2 / M30", "desc": "Enable THC port & end program"},
                ],
                "note": "Lines <= 80 chars; strips ?, !, ~ real-time command characters from comments.",
            },
        ],
        "sections": [
            {
                "id": "virtual-ports",
                "badge": "$674 Ports",
                "title": "$674 Virtual Ports (P2, P3, E3) on Standalone Blocks",
                "body_html": """
            <p>
              RotaryCAM drives <code class="mono">Plugin_plasma</code> through <code class="mono">$674</code> virtual ports rather than raw pin numbers. Each virtual-port M-code sits on its own standalone line (never mixed with motion or other M-codes):
            </p>
            <ul class="doc-bullet-list">
              <li><strong><code class="mono">P2</code> (Active-High THC Disable):</strong> <code class="mono">M64 P2</code> (immediate) or <code class="mono">M62 P2</code> (motion-synced) locks THC; <code class="mono">M65 P2</code> (immediate) or <code class="mono">M63 P2</code> (motion-synced) enables THC.</li>
              <li><strong><code class="mono">P3</code> (Torch Inhibit Clear):</strong> <code class="mono">M65 P3</code> clears the plugin's torch inhibit before firing.</li>
              <li><strong><code class="mono">E3</code> (Feedrate Override):</strong> <code class="mono">M68 E3 Q100</code> restores 100% feed immediately, and <code class="mono">M67 E3 Q60</code> applies motion-synced 60% small-hole speed scaling.</li>
            </ul>""",
            },
            {
                "id": "z-safety",
                "badge": "Z & G93 Safety",
                "title": "Explicit CAM Z (<code class=\"mono\">M190 P-1</code>) &amp; Core Issue #1027 Safety",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Preamble <code class="mono">M190 P-1</code>:</strong> Keeps <code class="mono">Plugin_plasma</code> <code class="mono">pierce_height = 0</code> so <code class="mono">G38.2</code> probing, switch-offset <code class="mono">G92 Z</code>, pierce height, and plunge/ramp Z moves stay under explicit CAM control.</li>
              <li><strong>Continuous <code class="mono">M64 P2</code> on 3D/4D:</strong> Holds <code class="mono">M64 P2</code> active throughout 3D ramp entries and 4D HSS contours.</li>
              <li><strong>Safe <code class="mono">G93</code> Exit (<code class="mono">M5</code> + <code class="mono">G94 F</code>):</strong> Emits <code class="mono">M5</code> followed immediately by <code class="mono">G94 F&lt;feed&gt;</code> after <code class="mono">G93</code> segments so inverse-time mode never carries into the next <code class="mono">G38.2</code> probe (avoiding grblHAL Core Issue #1027).</li>
              <li><strong>Rotary <code class="mono">G93</code> &amp; Optional Y-Wrap:</strong> Full 4-axis <code class="mono">G93</code> inverse-time coordinates A with linear travel, or unrolls round pipe into <code class="mono">G94</code> <code class="mono">Y = R &middot; A_rad</code> for 3-axis motor-swap boards.</li>
            </ul>""",
            },
            {
                "id": "checklist",
                "badge": "Checklist",
                "title": "Firmware, EEPROM &amp; Serial Hygiene Checklist",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Firmware Build:</strong> grblHAL core <code class="mono">20261015+</code> paired with Nov 2026+ <code class="mono">Plugin_plasma</code>.</li>
              <li><strong>Required EEPROM Settings:</strong> <code class="mono">$376=1</code>, <code class="mono">$133=0</code>, <code class="mono">$384=1</code>, <code class="mono">$674</code> (<code class="mono">virtual_ports=1</code>, <code class="mono">sync_pos=1</code>), and <code class="mono">$350</code>.</li>
              <li><strong>Modulo Unwinds &amp; Float Dwells:</strong> Resets rotary wrap with modulo <code class="mono">G92 A&lt;mod_360&gt;</code> (never <code class="mono">G92.1</code>) and emits <code class="mono">G4 P&lt;sec&gt;</code> pierces in floating-point seconds.</li>
              <li><strong>Serial Line Limits:</strong> Caps lines at <code class="mono">&le; 80</code> characters and strips <code class="mono">?</code>, <code class="mono">!</code>, and <code class="mono">~</code> real-time command characters from comments.</li>
            </ul>""",
            },
        ],
    },
    {
        "slug": "UCCNC",
        "is_scribing": False,
        "name": "CNCdrive UCCNC v1.2115+",
        "short_name": "CNCdrive UCCNC",
        "ext": ".nc",
        "rotary_mode": "G93 Inverse-Time (strokes only)",
        "ihs_summary": "G31 + G92 Z<Zm-offset>, Neuron Lite, or Legacy M31",
        "torch_summary": "M3 / M5 + G94 F (UC100 >= 0.2s dwell floor)",
        "thc_summary": "M205-M212 ArcOK-safe handshake (+ M206 bilateral lock)",
        "sync_summary": "Checkbox 212 (sec/ms) + G20/G21 suppress + Z >= 500 mm/s2",
        "card_summary": "Integrated G31 / Neuron Lite / M31 modes, ArcOK-safe M205-M212 handshake, 0.200 mm check move + M206 &amp; Checkbox 212.",
        "badge_label": "UC100, UC300ETH, UC400ETH &amp; AXBB-E (.nc)",
        "meta_title": "CNCdrive UCCNC v1.2115+ Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "CNCdrive UCCNC v1.2115+ setup: Integrated G31 vs Neuron Lite vs M31, ArcOK-safe M205-M212, M206 THC lock, UC100 0.2s dwell floor, and Checkbox 212.",
        "hero_title_html": 'CNCdrive <span class="text-gradient-amber">UCCNC Setup</span>',
        "subtitle_html": 'Hardened <code class="mono">.nc</code> output for <code class="mono">UC100</code>, <code class="mono">UC300ETH</code>, <code class="mono">UC400ETH</code>, and <code class="mono">AXBB-E</code> with ArcOK-safe <code class="mono">M205-M212</code> THC handshakes, <code class="mono">Checkbox 212</code> dwell matching, and <code class="mono">G93</code> rotary feeds.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.nc</code>'},
            {"style": "", "html": '<strong>IHS Modes:</strong> Integrated <code class="mono">G31</code> / <code class="mono">Neuron Lite</code> / <code class="mono">M31</code>'},
            {"style": "", "html": '<strong>Dwell:</strong> <code class="mono">Checkbox 212</code> (sec or ms) &bull; <code class="mono">UC100</code> &ge; 0.2s'},
        ],
        "toc": [
            {"id": "ihs-modes", "badge": "01", "label": "3 Touch-Off &amp; Hardware Modes"},
            {"id": "m205-m212", "badge": "02", "label": "ArcOK-Safe M205-M212 &amp; M206 Lock"},
            {"id": "checklist", "badge": "03", "label": "UC100 Floor &amp; Checkbox 212 Checklist"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G90 G91.1 G17 G40 G49 G64", "desc": "Startup (+ optional G20/G21 & M205/M207/M209/M211)"},
                    {"code": "G94 F<feed>", "desc": "Linear positioning feed"},
                    {"code": "G0 X<x> Y<y> A<a>", "desc": "Rapid at Safe Z to pierce"},
                ],
                "note": "Header prints Checkbox 212 dwell unit, hardware board, and Z accel >= 500 mm/s2 check.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "G31 Z<tgt> F<probe>", "desc": "Default Integrated G31 touch probe"},
                    {"code": "G92 Z<Zm - offset>", "desc": "Direct single-line switch offset"},
                    {"code": "M31 / Neuron Lite", "desc": "Legacy M31 (flat/round) or external Z"},
                ],
                "note": "Direct G92 Z<Zm - offset> avoids extra post-trip bounce on floating heads.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "G0 Z<pierceH>", "desc": "Move to pierce height"},
                    {"code": "M205 / M207 / M209 / M211", "desc": "Arm THC + anti-dive before M3 (never M206)"},
                    {"code": "M3 / G04 P<sec|ms>", "desc": "Fire torch + dwell (>= 0.2s on UC100)"},
                    {"code": "G1 Z<cutH> F<plunge>", "desc": "Plunge to cut height (non-ramp)"},
                ],
                "note": "M206 is never emitted before M3 so UCCNC's ArcOK wait gate completes cleanly.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G93", "desc": "Inverse-time rotary cut strokes"},
                    {"code": "M212 / M211", "desc": "Flat/Round anti-dive OFF/ON modulation"},
                    {"code": "0.200 mm -> M206", "desc": "3D/4D check move then bilateral THC lock"},
                ],
                "note": "On 3D ramps and 4D profiles, a 0.200 mm initial cut move verifies ArcOK before M206 locks Z.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "M211 (if unlocked)", "desc": "Enable anti-dive before torch off"},
                    {"code": "M5", "desc": "Extinguish plasma arc"},
                    {"code": "G94 F<feed>", "desc": "Restore G94 feedrate"},
                    {"code": "M205 / M209 / M211", "desc": "Reset state after M206 bilateral lock"},
                ],
                "note": "Final cut segment splits cleanly before M5 when direct-Z THC is active.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G0 Z<safeZ>", "desc": "Retract to Safe Z clearance"},
                    {"code": "G0 A<360*k> / G92 A0", "desc": "Modulo unwind between pack pieces"},
                    {"code": "G92.1 / M30", "desc": "Clear temporary offsets & end program"},
                ],
                "note": "Pneumatic air scribe uses G52 X<dx> Y<dy> offsets cleared with G52 X0 Y0 before plasma.",
            },
        ],
        "sections": [
            {
                "id": "ihs-modes",
                "badge": "IHS Modes",
                "title": "Touch-Off &amp; Hardware Modes (Pick One of Three)",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Integrated <code class="mono">G31</code> + <code class="mono">G92 Z&lt;Zm - SwitchOffset&gt;</code> (Default):</strong> Probes with <code class="mono">G31</code> and applies direct switch-offset compensation before retracting to pierce height. Works on flat plate, round pipe, 3D ramps, and 4D HSS.</li>
              <li><strong><code class="mono">Neuron Lite</code> (XY-Only External Z):</strong> Leaves all Z motion and touch-off to the Neuron controller, emitting XY(A) contours and <code class="mono">M3/M5</code> only.</li>
              <li><strong>Legacy <code class="mono">M31</code> Macro (Flat / Concentric Round Only):</strong> Calls UCCNC's built-in <code class="mono">M31</code> probe macro (not supported on 3D ramps or 4D HSS corners).</li>
            </ul>""",
            },
            {
                "id": "m205-m212",
                "badge": "THC Handshake",
                "title": "ArcOK-Safe M205-M212 THC Handshake &amp; 0.200 mm Check Move",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Pre-<code class="mono">M3</code> Baseline:</strong> Emits <code class="mono">M205</code>, <code class="mono">M207</code>, <code class="mono">M209</code>, and <code class="mono">M211</code> before <code class="mono">M3</code> (never <code class="mono">M206</code> before <code class="mono">M3</code>) so UCCNC's ArcOK wait gate clears cleanly.</li>
              <li><strong>Flat &amp; Concentric Round:</strong> Modulates <code class="mono">M211</code> (Anti-Dive ON / Lock) and <code class="mono">M212</code> (Anti-Dive OFF / Unlock) across tight corners and speed drops.</li>
              <li><strong>3D Ramps &amp; 4D Profiles:</strong> Executes a <code class="mono">0.200 mm</code> check move after pierce before locking THC bilaterally with <code class="mono">M206</code>, then resets <code class="mono">M205</code>/<code class="mono">M209</code>/<code class="mono">M211</code> after <code class="mono">M5</code>.</li>
            </ul>""",
            },
            {
                "id": "checklist",
                "badge": "Checklist",
                "title": "UC100 Dwell Floor, Checkbox 212 &amp; Z Acceleration",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong><code class="mono">UC100</code> vs. Ethernet / <code class="mono">AXBB-E</code>:</strong> Selecting <code class="mono">UC100</code> enforces a <code class="mono">0.2 s / 200 ms</code> minimum pierce dwell floor for USB buffering; <code class="mono">UC300ETH</code>, <code class="mono">UC400ETH</code>, and <code class="mono">AXBB-E</code> allow full short-dwell precision.</li>
              <li><strong><code class="mono">Checkbox 212</code> (<code class="mono">G04 P</code> Units):</strong> Match UCCNC <em>Configuration &rarr; General Settings &rarr; Checkbox 212</em> (unchecked = decimal seconds <code class="mono">G04 P0.5</code>; checked = integer milliseconds <code class="mono">G04 P500</code>).</li>
              <li><strong>Unit Suppression &amp; Z Accel:</strong> Enable <strong>Suppress <code class="mono">G20/G21</code></strong> if your profile locks units via <code class="mono">Steps/unit</code>. Set Z-axis acceleration to <strong><code class="mono">&ge; 500 mm/s&sup2;</code></strong> for 4D tube motion.</li>
            </ul>""",
            },
        ],
    },
    {
        "slug": "FlashCut",
        "is_scribing": False,
        "name": "FlashCut CNC Plasma",
        "short_name": "FlashCut CNC",
        "ext": ".nc / .gc",
        "rotary_mode": "G93 Inverse-Time (2D/3D/4D)",
        "ihs_summary": "Mode 1: M80 internal G605 | Mode 2: Explicit G605",
        "torch_summary": "Mode 1: M80/M81 | Mode 2: M50 + M101 I<n> / M51",
        "thc_summary": "G602 (Suspend THC) / G603 (Resume THC)",
        "sync_summary": "Setup.xml import + #fabhead.mode=Cut vs G631/G630",
        "card_summary": "Fabrication Head Cut2D (Mode 1) vs Explicit Dynamic-Z G631/G605/M50/M101/G630 (Mode 2), G04 X<sec> &amp; Setup.xml import.",
        "badge_label": "FlashCut CNC &amp; Fabrication Head (.nc / .gc)",
        "meta_title": "FlashCut CNC Plasma Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "FlashCut CNC Plasma setup guide: Mode 1 FabHead Cut2D vs Mode 2 Dynamic-Z (G631/G602/M50/M101/G603/G630), G04 X dwells, and Setup.xml import.",
        "hero_title_html": 'FlashCut CNC <span class="text-gradient-amber">Plasma Setup</span>',
        "subtitle_html": 'Built for FlashCut Fabrication Head systems with automatic Mode 1 (<code class="mono">#fabhead.mode = Cut</code>) vs. Mode 2 Explicit Dynamic-Z (<code class="mono">G631/G605/M50/M101/G630</code>) switching and <code class="mono">Setup.xml</code> import.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extensions:</strong> <code class="mono">.nc</code> / <code class="mono">.gc</code>'},
            {"style": "", "html": '<strong>XML Importer:</strong> Auto-fills <code class="mono">Hplasma&lt;n&gt;</code>, <code class="mono">M101 I&lt;n&gt;</code> &amp; <a href="#faq-flashcut-zero-lift" style="color: var(--cyan-400); text-decoration: underline;">ZeroLift FAQ</a>'},
            {"style": "", "html": '<strong>Dwell:</strong> <code class="mono">G04 X&lt;sec&gt;</code>'},
        ],
        "toc": [
            {"id": "mode1-vs-mode2", "badge": "01", "label": "Mode 1 (Cut2D) vs. Mode 2 (Explicit Z)"},
            {"id": "thc-dwells", "badge": "02", "label": "G602/G603 THC &amp; G04 X Dwells"},
            {"id": "xml-import", "badge": "03", "label": "Setup.xml Import &amp; Rotary Mapping"},
            {"id": "import-warnings-faq", "badge": "FAQ", "label": "FlashCut (Setup.xml) Warnings FAQ"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "M106 Hplasma<id>", "desc": "Select active Fabrication Head"},
                    {"code": "#fabhead.mode = Cut | G631", "desc": "Mode 1 (Cut2D) vs Mode 2 (Dynamic Z)"},
                    {"code": "G0 X<x> Y<y> A<a>", "desc": "Rapid (Safe Z omitted in Mode 1)"},
                ],
                "note": "Mode 1 lets FabHead manage SafeHeight; Mode 2 emits explicit G0 Z<safeZ> clearance.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "M80 (Mode 1 Cut2D)", "desc": "First G1/G2/G3 triggers internal G605"},
                    {"code": "G605 (Mode 2 Dynamic Z)", "desc": "Explicit probe & surface Z=0 reset"},
                ],
                "note": "Mode 2 requires ZeroLiftAxisPositionAfterTouchOff enabled in FlashCut Setup.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "M50 (Mode 2)", "desc": "Ignite torch (Mode 1 runs inside M80)"},
                    {"code": "M101 I<arcIn>", "desc": "Wait for Arc Transfer input"},
                    {"code": "G04 X<sec>", "desc": "Pierce dwell in X-word seconds"},
                    {"code": "G1 Z<cutH> F<plunge>", "desc": "Mode 2 plunge (or 3D ramp with G602)"},
                ],
                "note": "Mode 1 never emits M50 or G04 directly; Mode 2 drives explicit M50 + M101 + G04 X.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G93 / G94", "desc": "G93 inverse-time on 4-axis rotary"},
                    {"code": "G602 (Suspend THC)", "desc": "Lock THC on corners, holes, ramps, 4D HSS"},
                    {"code": "G603 (Resume THC)", "desc": "Resume optical voltage THC on steady runs"},
                ],
                "note": "Mode 1 omits Z words; Mode 2 outputs Z = cutHeight + (currZm - pierceSurfaceZm).",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "M81 (Mode 1 Cut2D)", "desc": "Next G0 triggers G600 + M51 + retract"},
                    {"code": "G602 / M51 (Mode 2)", "desc": "Suspend THC then extinguish torch"},
                ],
                "note": "Mode 2 never emits G600 or G601 so explicit Z control stays uninterrupted.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G0 Z<safeZ> (Mode 2)", "desc": "Retract to Safe Z above HSS corners"},
                    {"code": "G600 / M51 (Mode 1 EOF)", "desc": "Close Cut2D cycle at program end"},
                    {"code": "G94 / G630 / M30", "desc": "Restore G94, exit Dynamic-Z & end"},
                ],
                "note": "Supports Tube Along Y for gantry-parallel outboard pipe troughs via Setup.xml.",
            },
        ],
        "sections": [
            {
                "id": "mode1-vs-mode2",
                "badge": "Mode 1 vs Mode 2",
                "title": "Mode 1 (FabHead Cut2D) vs. Mode 2 (Explicit Dynamic-Z)",
                "body_html": """
            <ul class="doc-bullet-list">
              <li>
                <strong>Mode 1: Constant-Z Cut2D (<code class="mono">#fabhead.mode = Cut</code>):</strong>
                Used on flat plate and concentric round pipe without 3D ramps or eccentric bevels. Emits <code class="mono">M106 Hplasma&lt;id&gt;</code> and <code class="mono">#fabhead.mode = Cut</code>, letting FlashCut's <code class="mono">M80</code> / <code class="mono">M81</code> cycle execute <code class="mono">G605</code>, <code class="mono">M50</code>, <code class="mono">M101</code>, pierce dwell, and retracts automatically on <code class="mono">G1</code> and <code class="mono">G0</code> moves (zero <code class="mono">Z</code> words emitted).
              </li>
              <li>
                <strong>Mode 2: Explicit Dynamic-Z (<code class="mono">G631 &rarr; G602 &rarr; G605 &rarr; M50 &rarr; M101 &rarr; Z &rarr; G603 &rarr; M51 &rarr; G0 Z &rarr; G630</code>):</strong>
                Engages automatically for 3D Ramp Lead-Ins, square/rectangular HSS, angle iron, channel, and eccentric bevels without emitting <code class="mono">G601</code>/<code class="mono">G600</code>. <code class="mono">G631</code> enters Dynamic-Z, <code class="mono">G605</code> zeroes the surface, <code class="mono">M50</code> + <code class="mono">M101 I&lt;n&gt;</code> fires and waits for arc transfer, the torch plunges/ramps to <code class="mono">+cutHeight</code>, <code class="mono">M51</code> stops the arc, and <code class="mono">G630</code> exits at EOF.
              </li>
            </ul>""",
            },
            {
                "id": "thc-dwells",
                "badge": "THC & Dwells",
                "title": "THC Suspend/Resume (<code class=\"mono\">G602/G603</code>) &amp; <code class=\"mono\">G04 X</code> Dwells",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Native THC Anti-Dive:</strong> <code class="mono">G602 (Suspend THC)</code> locks height tracking around corners, small holes, ramps, and 4D HSS cuts; <code class="mono">G603 (Resume THC)</code> restores voltage tracking on straight runs.</li>
              <li><strong>FlashCut Dwell Syntax (<code class="mono">G04 X&lt;sec&gt;</code>):</strong> FlashCut uses <code class="mono">X</code> instead of <code class="mono">P</code> for dwell times in decimal seconds.</li>
              <li><strong>Rotary Feedrates:</strong> Full 4-axis <code class="mono">G93</code> inverse-time keeps surface speed uniform across tube corners and saddle contours.</li>
            </ul>""",
            },
            {
                "id": "xml-import",
                "badge": "XML Import",
                "title": "One-Click Setup.xml Import &amp; Checklist",
                "body_html": """
            <p>
              Upload your FlashCut <code class="mono">Setup.xml</code> inside the <strong>Machines</strong> modal to auto-fill your <code class="mono">M101 I&lt;n&gt;</code> arc-transfer input, plasma head ID (<code class="mono">Hplasma1</code>), <code class="mono">M50/M51</code> codes, <code class="mono">Tube Along X/Y</code> orientation, and verify <code class="mono">ZeroLiftAxisPositionAfterTouchOff</code>. See the <a href="#import-warnings-faq" style="color: var(--cyan-400);">FlashCut XML Import Warnings FAQ</a> below if any flag appears.
            </p>""",
            },
        ],
    },
    {
        "slug": "EdingCNC",
        "is_scribing": False,
        "name": "EdingCNC Plasma",
        "short_name": "EdingCNC Plasma",
        "ext": ".nc",
        "rotary_mode": "G93 Inverse-Time (0.005 mm deadband)",
        "ihs_summary": "Guarded G38.2 (#5380/#5397) + #5067 miss check + G92 Z",
        "torch_summary": "M3 / M5 + optional M56 P<n> L1 Arc-OK + post-M5 dwell",
        "thc_summary": "M21 (Lock) / M20 (Unlock) + M22/M23 Q<volts>",
        "sync_summary": "If [#5150==2] 4THMILL guard + G64 R + MOD 360 unwind",
        "card_summary": "CNC720/760 post with #5150 4THMILL guard, #5067 probe miss check, M22/M23 voltage, M56 Arc-OK &amp; M20/M21 THC.",
        "badge_label": "EdingCNC CNC720, CNC760 &amp; Legacy (.nc)",
        "meta_title": "EdingCNC Plasma Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "EdingCNC CNC720 and CNC760 setup: #5150 4THMILL guard, G64 tolerance, guarded G38.2 with #5067 check, M22/M23 volts, M56 Arc-OK, and MOD 360 unwind.",
        "hero_title_html": 'EdingCNC <span class="text-gradient-amber">Plasma Setup</span>',
        "subtitle_html": 'Hardened <code class="mono">.nc</code> programs for CNC720 and CNC760 with <code class="mono">#5150</code> 4THMILL guards, <code class="mono">#5067</code> probe miss checks, <code class="mono">M22/M23</code> arc voltage, optional <code class="mono">M56</code> Arc-OK handshakes, and <code class="mono">G64 R</code> blending.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.nc</code>'},
            {"style": "", "html": '<strong>Guards:</strong> <code class="mono">#5150 != 2</code> &bull; <code class="mono">#5067 != 0</code> &bull; <code class="mono">G64 R&lt;tol&gt;</code>'},
            {"style": "", "html": '<strong>Max Line:</strong> 256 chars &bull; <code class="mono">M30</code> / <code class="mono">M60</code>'},
        ],
        "toc": [
            {"id": "guards-probing", "badge": "01", "label": "Preamble Guards &amp; #5067 Probing"},
            {"id": "thc-arcok", "badge": "02", "label": "M20-M23 THC &amp; M56 Arc-OK"},
            {"id": "checklist", "badge": "03", "label": "EdingCNC Commissioning Checklist"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G90 G17 G40 G49 G64 R<tol>", "desc": "Path tolerance via R (never G64 P)"},
                    {"code": "If [#5150 == 2] Errmsg", "desc": "Block 4THMILL Y-to-A mapping"},
                    {"code": "G10 L20 P#5220 A0.000", "desc": "Zero rotary A at startup"},
                    {"code": "G0 X<x> Y<y> A<a>", "desc": "Rapid at Safe Z (0.005 mm deadband)"},
                ],
                "note": "Startup locks THC (M21) and turns torch off (M5) in G94 before positioning.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "If [[#5380==0] AND [#5397==0]]", "desc": "Skip probe during dry/unrendered sim"},
                    {"code": "G38.2 Z<tgt> F<probe>", "desc": "Touch-off search"},
                    {"code": "If [#5067 == 0] Errmsg", "desc": "Abort cleanly if probe misses stock"},
                    {"code": "G92 Z<datum - offset>", "desc": "Apply switch offset (or centerline Z0)"},
                ],
                "note": "Direct G92 Z compensation avoids mechanical switch bounce.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "G0 Z<pierceH>", "desc": "Move to pierce height"},
                    {"code": "M22 Q<V> / M23 Q<V>", "desc": "Optional programmable voltage setpoint"},
                    {"code": "M21 / M3 / G4 P<sec>", "desc": "Lock THC, fire torch, decimal-sec dwell"},
                    {"code": "M56 P<n> L1 Q<t> (#5399)", "desc": "Optional Arc-OK wait + timeout abort"},
                    {"code": "G1 Z<cutH> F<plunge>", "desc": "Plunge to cut height (non-ramp)"},
                ],
                "note": "Supports polarity inversion (M20/M21) and measuredIsSetpoint=1 material auto-sample.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G93", "desc": "Inverse-time rotary cut strokes"},
                    {"code": "M20 / M21", "desc": "Unlock / lock THC on flat & round"},
                    {"code": "M21 (4D Default)", "desc": "Held on 4D Z (optional 4D flat-face THC)"},
                ],
                "note": "Unlocks with M20 after 3D ramp lead-ins finish when contour Z is flat/round.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "M21", "desc": "Lock THC before M5"},
                    {"code": "M5", "desc": "Extinguish plasma arc"},
                    {"code": "G4 P<postCutSec>", "desc": "Optional post-M5 anti-dive dwell"},
                    {"code": "G94 F<feed>", "desc": "Restore G94 before Safe Z retract"},
                ],
                "note": "Final cut segment splits cleanly before M5 when THC is unlocked.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G0 Z<safeZ>", "desc": "Retract to Safe Z clearance"},
                    {"code": "G10 L20 P#5220 A[#5004 MOD 360.0]", "desc": "Modulo-360 unwind (zero G92.1)"},
                    {"code": "M30 / M60", "desc": "End program (M60 optional UI Nesting)"},
                ],
                "note": "Flattens comments under EdingCNC's 256-character line limit.",
            },
        ],
        "sections": [
            {
                "id": "guards-probing",
                "badge": "Guards & IHS",
                "title": "Preamble Guards, <code class=\"mono\">G64 R</code> &amp; Guarded <code class=\"mono\">G38.2</code> Probing",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Startup &amp; 4THMILL Guard:</strong> Starts safely in <code class="mono">G94</code> with <code class="mono">M21</code> (THC OFF) and <code class="mono">M5</code>, checks <code class="mono">If [#5150 == 2] Errmsg</code> so Y-to-A 4THMILL mapping never conflicts with XYZA, and zeroes A via <code class="mono">G10 L20 P#5220 A0.000</code>.</li>
              <li><strong>Path Tolerance (<code class="mono">G64 R&lt;tol&gt;</code>) &amp; Line Hygiene:</strong> Uses <code class="mono">G64 R</code> (never <code class="mono">G64 P</code>), caps lines at 256 chars, filters rotary steps under <code class="mono">0.005 mm</code>, and resets wrap via <code class="mono">A[#5004 MOD 360.0]</code> without <code class="mono">G92.1</code>.</li>
              <li><strong>Guarded Probing (<code class="mono">#5067</code> Miss Check):</strong> Wraps touch-offs in <code class="mono">If [[#5380 == 0] AND [#5397 == 0]]</code>, aborts cleanly if <code class="mono">#5067 == 0</code>, applies <code class="mono">G92 Z[datum - switchOffset]</code>, and supports centerline WCS <code class="mono">Z0</code> on HSS tubes.</li>
            </ul>""",
            },
            {
                "id": "thc-arcok",
                "badge": "THC & Arc-OK",
                "title": "Voltage Control (<code class=\"mono\">M22/M23</code>), <code class=\"mono\">M56</code> Arc-OK &amp; <code class=\"mono\">M20/M21</code> THC",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Voltage Setpoint vs. Auto-Sample:</strong> Emit programmable <code class="mono">M22 Q&lt;volts&gt;</code> / <code class="mono">M23 Q&lt;volts&gt;</code> target voltage or run <code class="mono">measuredIsSetpoint = 1</code> material auto-sample mode.</li>
              <li><strong>Optional <code class="mono">M56</code> Arc-OK Handshake:</strong> Verifies <code class="mono">M56 P&lt;port&gt; L1 Q&lt;timeout&gt;</code> with explicit <code class="mono">#5399 == -1</code> timeout abort.</li>
              <li><strong>Anti-Dive &amp; 4D Default:</strong> Holds <code class="mono">M21</code> (THC OFF) by default on 4D dynamic-Z cuts, unlocks with <code class="mono">M20</code> after 3D ramps finish, locks corners and small holes, and adds optional post-<code class="mono">M5</code> dwell before retracting.</li>
            </ul>""",
            },
            {
                "id": "checklist",
                "badge": "Checklist",
                "title": "EdingCNC Commissioning Checklist",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Disable 4THMILL:</strong> Turn off EdingCNC's 4THMILL Y-to-A mapping so rotary moves drive the <code class="mono">A</code> chuck without tripping <code class="mono">#5150 == 2</code>.</li>
              <li><strong>Disable <code class="mono">G4 ms</code>:</strong> Keep millisecond dwell mode unchecked so <code class="mono">G4 P&lt;sec&gt;</code> executes in decimal seconds.</li>
              <li><strong>Disable Pause on Unexpected Probe Trigger:</strong> Uncheck pause-on-unexpected-probe in setup so IHS contact transitions never stall runs.</li>
              <li><strong>CNC720 <code class="mono">P2/P3</code> FLOOD/MIST Ports &amp; <code class="mono">macro.cnc ;@unit</code>:</strong> Verify <code class="mono">P2/P3</code> output mapping for auxiliary relays and confirm <code class="mono">macro.cnc</code> declares <code class="mono">;@unit mm</code> or <code class="mono">inch</code> matching <code class="mono">G21/G20</code>.</li>
            </ul>""",
            },
        ],
    },
    {
        "slug": "PlanetCNC",
        "is_scribing": False,
        "name": "PlanetCNC TNG Plasma",
        "short_name": "PlanetCNC TNG",
        "ext": ".nc",
        "rotary_mode": "G93 Inverse-Time (optional G94 lookahead)",
        "ihs_summary": "G38.2 (+ optional 2-stage) + AL Axis-Lock G91 G01 backoff + G92 Z",
        "torch_summary": "M3 / M5 + G04 P<sec> + G94 F restore",
        "thc_summary": "M54 P0 (Lock) / M54 P1 Q<spd> R1 (2D) / M54 P1 R1 (4D Round)",
        "sync_summary": "G90.2 + M55/56/57 P0 + ; comments + (status, ...)",
        "card_summary": "G90.2 rotary absolute mode, AL Axis-Lock G91 G01 probe backoff, lookahead M54 P1 Q R1 THC &amp; semicolon comment safety.",
        "badge_label": "PlanetCNC Mk3, Mk3/4 &amp; TNG (.nc)",
        "meta_title": "PlanetCNC TNG Plasma Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "PlanetCNC TNG plasma setup: G90.2 startup, semicolon vs status comment safety, AL Axis-Lock G38.2 probing, M54 lookahead THC, and commissioning.",
        "hero_title_html": 'PlanetCNC <span class="text-gradient-amber">TNG Plasma Setup</span>',
        "subtitle_html": 'Hardened <code class="mono">.nc</code> output for PlanetCNC Mk3, Mk3/4, and TNG with <code class="mono">G90.2</code> rotary mode, <code class="mono">AL</code> Axis-Lock IHS clearing, lookahead <code class="mono">M54 P1 Q R1</code> THC, and active-comment protection.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.nc</code>'},
            {"style": "", "html": '<strong>Comments:</strong> <code class="mono">; ...</code> safe (<code class="mono">(status, ...)</code> optional)'},
            {"style": "", "html": '<strong>End Code:</strong> Selectable <code class="mono">M02</code> / <code class="mono">M30</code>'},
        ],
        "toc": [
            {"id": "lifecycle-comments", "badge": "01", "label": "G90.2 Lifecycle &amp; Comment Safety"},
            {"id": "ihs-thc", "badge": "02", "label": "AL Axis-Lock IHS &amp; M54 THC"},
            {"id": "checklist", "badge": "03", "label": "PlanetCNC TNG Checklist"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G90 G90.2 G91.1 G17 G40 G49 G64", "desc": "Rotary absolute mode + startup"},
                    {"code": "M54 P0 / M55-M57 P0", "desc": "THC OFF & cancel Transform/Warp/Swap"},
                    {"code": "G0 X<x> Y<y> A<a>", "desc": "Rapid at Safe Z in G94"},
                ],
                "note": "General notes emit as ; comments so none of TNG's 38 parenthetical keywords fire accidentally.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "G38.2 Z<tgt> F<probe>", "desc": "Fast touch (+ optional slow 2-stage latch)"},
                    {"code": "G91 G01 Z<off> F<p> / G90", "desc": "Clears AL Axis-Lock without losing pos"},
                    {"code": "G92 Z<datum>", "desc": "Surface or HSS centerline Z=0"},
                ],
                "note": "Avoids pre-retract G92 Z0 so TNG never loses the probed surface coordinate.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "G0 Z<pierceH>", "desc": "Move to pierce height"},
                    {"code": "M54 P0 ; Lock THC", "desc": "Hold THC off for pierce & lead-in"},
                    {"code": "M3 / G04 P<sec>", "desc": "Fire torch + decimal-second dwell"},
                    {"code": "G1 Z<cutH> F<plunge>", "desc": "Plunge to cut height (non-ramp)"},
                ],
                "note": "Switches to G93 for rotary strokes unless stationary-A lookahead keeps G94 active.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G93 / G94", "desc": "G93 on A moves; G94 on flat"},
                    {"code": "M54 P1 Q<spd> R1", "desc": "2D/Y-Wrap speed-gated lookahead THC"},
                    {"code": "M54 P1 R1", "desc": "4-axis round THC (omits Q speed gate)"},
                    {"code": "M54 P0", "desc": "Held continuously on 4D dynamic-Z"},
                ],
                "note": "Omitting Q on 4-axis round cuts stops G93 speed changes from tripping flat-plane anti-dive.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "M54 P0 ; Lock THC", "desc": "Lock THC before M5"},
                    {"code": "M5", "desc": "Extinguish plasma arc"},
                    {"code": "G94 F<feed>", "desc": "Restore G94 before Safe Z retract"},
                ],
                "note": "Final cut segment splits cleanly before M5 when THC is active.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G0 Z<safeZ>", "desc": "Retract to Safe Z clearance"},
                    {"code": "G92 A<mod_360>", "desc": "Modulo-360 reset (zero G92.1)"},
                    {"code": "M54 P0 / M02 or M30", "desc": "THC OFF & selectable M02/M30 end"},
                ],
                "note": "Optional (status, ...) lines report piece progress in TNG's status bar.",
            },
        ],
        "sections": [
            {
                "id": "lifecycle-comments",
                "badge": "Lifecycle",
                "title": "Preamble, <code class=\"mono\">G94/G93</code> Lifecycle &amp; Active-Comment Safety",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Preamble &amp; Clean State:</strong> Starts with <code class="mono">G90 G90.2</code> (rotary absolute mode), initial <code class="mono">M54 P0</code> (THC OFF), and <code class="mono">M55 P0 M56 P0 M57 P0</code> to cancel residual Transform, Warp, and Swap offsets. Restores <code class="mono">G94 F...</code> before retracts and footer.</li>
              <li><strong>Active-Comment Safety (<code class="mono">; ...</code> vs. <code class="mono">(status, ...)</code>):</strong> TNG treats 38 parenthetical keywords as live commands. General notes emit as <code class="mono">; ...</code> semicolon comments, reserving <code class="mono">(status, ...)</code> strictly for intentional UI progress.</li>
            </ul>""",
            },
            {
                "id": "ihs-thc",
                "badge": "IHS & THC",
                "title": "AL Axis-Lock IHS, Two-Stage Probing &amp; <code class=\"mono\">M54</code> Lookahead THC",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>AL Axis-Lock Clearing IHS:</strong> Probes with <code class="mono">G38.2</code> (plus optional slow second-stage latch re-probe), then clears TNG's AL Axis-Lock via <code class="mono">G91 G01 Z&lt;switchOffset&gt;</code> &rarr; <code class="mono">G90</code> &rarr; <code class="mono">G92 Z&lt;datum&gt;</code>, supporting HSS centerline <code class="mono">Z=0</code>.</li>
              <li><strong>Lookahead-Preserving THC (<code class="mono">M54</code>):</strong> Uses <code class="mono">M54 P1 Q&lt;speed&gt; R1</code> on 2D flat/Y-wrap cuts and <code class="mono">M54 P1 R1</code> (omitting <code class="mono">Q</code>) on 4-axis round pipe so <code class="mono">G93</code> feeds never trip flat-plane speed gating. Holds <code class="mono">M54 P0</code> across 4D dynamic-Z cuts and unlocks after 3D ramps.</li>
            </ul>""",
            },
            {
                "id": "checklist",
                "badge": "Checklist",
                "title": "PlanetCNC TNG Commissioning Checklist",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Disable Probe Lock:</strong> Turn off <strong>Probe Lock</strong> under TNG <em>Jogging</em> settings so IHS switch trips do not lock out subsequent moves.</li>
              <li><strong>Zero Spindle Delays:</strong> Set <code class="mono">#&lt;_spindle_delay_start&gt;</code> and <code class="mono">#&lt;_spindle_delay_stop&gt;</code> to <code class="mono">0</code> so TNG does not stack extra delays onto <code class="mono">G04</code> pierces.</li>
              <li><strong>Disable A Soft Limits:</strong> Turn off soft limits on the <code class="mono">A</code> rotary axis so modulo-360 cuts and <code class="mono">G92 A</code> resets never trip a soft-limit alarm.</li>
              <li><strong>Verify <code class="mono">#&lt;_thc_speed&gt;</code> &amp; Audit <code class="mono">Scripts/M3.gcode</code>:</strong> Confirm <code class="mono">#&lt;_thc_speed&gt;</code> is set in units/s (not units/min) and ensure <code class="mono">Scripts/M3.gcode</code> does not inject conflicting touch-off or THC commands.</li>
            </ul>""",
            },
        ],
    },
    {
        "slug": "WinCNC",
        "is_scribing": False,
        "name": "ShopSabre WinCNC + SideKick Rotary",
        "short_name": "ShopSabre WinCNC",
        "ext": ".tap",
        "rotary_mode": "G93 Inverse-Time (A / W / B letter)",
        "ihs_summary": "Pattern 1: M61 (+ G92 Z on 4D) | Pattern 2: G31 + G92 Z",
        "torch_summary": "Pattern 1: M61 / M62 | Pattern 2: L38 T0.0 P100 / M62",
        "thc_summary": "L37.2 D1/D0 + inline D1/D0 (or Legacy L37/L36)",
        "sync_summary": "G22 mm (NEVER G21!) + [...] comments + L38.1 + L28.1/L92/M66",
        "card_summary": "G22 mm / G20 in (never G21!), configurable A/W/B SideKick letter, L37.2 D1/D0 inline THC, L38.1 params &amp; M61/L38 patterns.",
        "badge_label": "ShopSabre &amp; SideKick Rotary &bull; v3.1.06d+ (.tap)",
        "meta_title": "WinCNC + SideKick Rotary Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "ShopSabre WinCNC + SideKick setup: G22 mm vs G20 in, A/W/B rotary axis letter, L37.2 D1/D0 THC, L38.1 cut params, M61 patterns, and L28.1/L92.",
        "hero_title_html": 'ShopSabre <span class="text-gradient-amber">WinCNC + SideKick Setup</span>',
        "subtitle_html": 'Built for ShopSabre plasma tables and SideKick rotary attachments (<code class="mono">v3.1.06d+</code> and legacy), emitting <code class="mono">G22</code> mm / <code class="mono">G20</code> in, <code class="mono">[bracket]</code> comments, <code class="mono">L37.2 D1/D0</code> inline THC, and <code class="mono">L28.1/L92/M66</code> framing.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.tap</code>'},
            {"style": "", "html": '<strong>Metric Unit:</strong> <code class="mono">G22</code> mm (Never <code class="mono">G21</code> = cm!)'},
            {"style": "", "html": '<strong>Comments:</strong> <code class="mono">[square brackets]</code> ONLY'},
        ],
        "toc": [
            {"id": "units-axis", "badge": "01", "label": "G22 Units, SideKick Axis &amp; Framing"},
            {"id": "thc-patterns", "badge": "02", "label": "L37.2 / L38.1 &amp; M61 vs. L38 Patterns"},
            {"id": "scribe", "badge": "03", "label": "Pneumatic Scribe &amp; Pack L92"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G22 | G20 / G90 G40 [G9 S10]", "desc": "G22 mm or G20 in + M65 + G94"},
                    {"code": "L38.1 T<V> F<f> Z<p> R<c> C<a>", "desc": "Optional v3.1.06d+ cut-parameter block"},
                    {"code": "G0 X<x> Y<y> <A|W|B><ang>", "desc": "Rapid using WINCNC.INI rotary letter"},
                ],
                "note": "Check WINCNC.INI (A, W, or B) so rotary moves and L28.1 command the right SideKick motor.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "M61 (Pattern 1)", "desc": "WinCNC touch-off & pierce (+ G92 Z on 4D)"},
                    {"code": "G31 Z<tgt> F<probe> (Pattern 2)", "desc": "Explicit G31 + G92 Z surface datum"},
                ],
                "note": "Pattern 2 L38 bypass engages automatically on 3D ramps if L38.1 is off or legacy mode is active.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "L37.2 D1 / D0", "desc": "Set THC latch (or Legacy L37/L36)"},
                    {"code": "M61 (P1) | L38 T0.0 P100 (P2)", "desc": "Canned M61 or direct L38 ignition"},
                    {"code": "G04 X<sec>", "desc": "X-word sec dwell (P1 ramp/forced or P2)"},
                    {"code": "G1 Z<cutH> F<plunge>", "desc": "Pattern 2 plunge to cut height"},
                ],
                "note": "Pattern 1 suppresses duplicate G04 dwells unless 3D ramp (L38.1 Z==R) or forced G04.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G93 / G94", "desc": "G93 inverse-time on rotary strokes"},
                    {"code": "L37.2 D1 / D0 + inline D1/D0", "desc": "v3.1.06d+: D1=Disabled, D0=Enabled"},
                    {"code": "L37 / L36", "desc": "Legacy build THC Off / On"},
                ],
                "note": "On v3.1.06d+, inline D1/D0 rides directly on motion blocks for mid-cut THC modulation.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "G94", "desc": "Restore G94 BEFORE M62"},
                    {"code": "M62", "desc": "WinCNC torch off & Z retract"},
                ],
                "note": "Clean M62 exit keeps torch off and Z clear before next rapid.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G0 Z<safeZ>", "desc": "Retract to Safe Z clearance"},
                    {"code": "L28.1 / G92 <A|W|B>0.000", "desc": "Modulo 0-360 rotary wrap reset"},
                    {"code": "[L92] / M66", "desc": "Pack-only L92 + M66 program end"},
                ],
                "note": "L92 emits in Pack Mode only so single-part jobs auto-restore pre-job G92 cleanly.",
            },
        ],
        "sections": [
            {
                "id": "units-axis",
                "badge": "Units & SideKick",
                "title": "G22 Metric Units, SideKick Axis Letter &amp; Bracket Comments",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Units (<code class="mono">G22</code> Metric vs. <code class="mono">G20</code> Imperial, Never <code class="mono">G21</code>):</strong> WinCNC reads <code class="mono">G21</code> as <em>centimeters</em> (10x scale error). RotaryCAM strictly outputs <code class="mono">G22</code> for millimeters and <code class="mono">G20</code> for inches.</li>
              <li><strong>SideKick Axis Letter (<code class="mono">WINCNC.INI</code>: <code class="mono">A</code>, <code class="mono">W</code>, or <code class="mono">B</code>):</strong> Check <code class="mono">Help &rarr; About</code> (targets <code class="mono">v3.1.06d+</code> by default) and confirm your SideKick axis letter in <code class="mono">WINCNC.INI</code> so rotary moves, <code class="mono">G93</code> feeds, and <code class="mono">L28.1</code> wraps match.</li>
              <li><strong>Strict <code class="mono">[square bracket]</code> Comments &amp; Framing:</strong> Zero parentheses or semicolons; emits <code class="mono">M65</code> init, optional <code class="mono">G9 S10</code> smoothing, <code class="mono">G4 X&lt;sec&gt;</code> dwells, <code class="mono">L28.1</code> wraps, and Pack-only <code class="mono">L92</code> before <code class="mono">M66</code>.</li>
            </ul>""",
            },
            {
                "id": "thc-patterns",
                "badge": "THC & Patterns",
                "title": "Continuous THC (<code class=\"mono\">L37.2 D#</code>), <code class=\"mono\">L38.1</code> &amp; <code class=\"mono\">M61/L38</code> Patterns",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong><code class="mono">v3.1.06d+</code> Continuous THC (<code class="mono">L37.2 D1/D0</code>):</strong> Emits <code class="mono">L37.2 D1/D0</code> and inline <code class="mono">D1</code> (Disabled) / <code class="mono">D0</code> (Enabled) on motion lines. Older installs can toggle legacy <code class="mono">L37/L36</code>.</li>
              <li><strong>Decoupled <code class="mono">L38.1</code> Cut-Parameter Injection:</strong> Enable <code class="mono">L38.1</code> to push <code class="mono">T</code> volts, <code class="mono">F</code> feed, <code class="mono">S</code> dwell, <code class="mono">Z</code> pierce, <code class="mono">R</code> cut, <code class="mono">L</code> lift, <code class="mono">N</code> plunge, and <code class="mono">C</code> amps, or disable it to use your WinCNC material table.</li>
              <li><strong>Pattern 1 (<code class="mono">M61</code>) vs. Pattern 2 (<code class="mono">L38</code> Bypass):</strong> Pattern 1 runs <code class="mono">M61</code> (with centerline <code class="mono">G92 Z</code> on 4D HSS and ramps); Pattern 2 bypasses <code class="mono">M61</code> with explicit <code class="mono">G31</code> + <code class="mono">L38 T0.0 P100</code> and engages automatically on 3D ramps if <code class="mono">L38.1</code> is off or legacy mode is active.</li>
            </ul>""",
            },
            {
                "id": "scribe",
                "badge": "Scribe & Pack",
                "title": "Pneumatic Scribe (<code class=\"mono\">G54</code> Baking) &amp; Pack <code class=\"mono\">L92</code>",
                "body_html": """
            <p>
              Pneumatic air-scribe XY offsets bake directly into <code class="mono">G54</code> coordinates with zero <code class="mono">G52</code>, <code class="mono">G53</code>, or <code class="mono">G56</code> conflicts. In Pack Mode, <code class="mono">L92</code> preserves indexed stick <code class="mono">G92 X</code> offsets at program end before <code class="mono">M66</code>.
            </p>""",
            },
        ],
    },
    {
        "slug": "SimCNC",
        "is_scribing": False,
        "name": "CSLab SimCNC 3.5 & 3.6+ G93",
        "short_name": "CSLab SimCNC",
        "ext": ".nc",
        "rotary_mode": "3.5: 4D Spoofed G94 | 3.6+: Hardened G93",
        "ihs_summary": "Managed inside SimCNC m3.py macro (#1110-#1114 / #1090-#1092)",
        "torch_summary": "M3 S1 (ExtTrajSyncOut1 M62 P1) / M63 P1 + M5",
        "thc_summary": "M63 P0 (Lock) / M62 P0 (Unlock) / #4061",
        "sync_summary": "config.xml import + G64 P0.3/0.4 + 0.002mm feather + M112",
        "card_summary": "Hardware-verified SimCNC post: config.xml import, G69/G64 P0.3-0.4, 0.002 mm feathering, #1110/#1113 3D ramps &amp; M62/M63 sync.",
        "badge_label": "CSLab CSMIO/IP-M &amp; IP-S &bull; Hardware Verified (.nc)",
        "meta_title": "CSLab SimCNC 3.5 & 3.6+ G93 Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "CSLab SimCNC 3.5 & 3.6+ setup: config.xml import, G69 and G64 smoothing, 0.002 mm feathering, #1110/#1090 m3.py handshake, and M62/M63 P0/P1 sync.",
        "hero_title_html": 'CSLab SimCNC <span class="text-gradient-amber">3.5 &amp; 3.6+ G93 Setup</span>',
        "subtitle_html": 'Hardware-verified <code class="mono">.nc</code> output for CSMIO/IP-M and IP-S controllers with one-click <code class="mono">config.xml</code> import, hardened <code class="mono">G93</code> inverse-time (<code class="mono">3.6+</code>) or 4D spoofed <code class="mono">G94</code> (<code class="mono">3.5</code>), and <code class="mono">M62/M63 P0/P1</code> motion-synced torch &amp; THC.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.nc</code> &bull; <code class="mono">Hardware Verified</code>'},
            {"style": "", "html": '<strong>XML Importer:</strong> <code class="mono">config.xml</code> + <a href="#import-warnings-faq" style="color: var(--cyan-400); text-decoration: underline;">Import Warnings FAQ</a>'},
            {"style": "", "html": '<strong>Deep Dive:</strong> <a href="../../simcnc-motion-sync.html" style="color: var(--amber-400); text-decoration: underline;">Tutorial 07: SimCNC Motion-Sync</a>'},
        ],
        "toc": [
            {"id": "blending-g93", "badge": "01", "label": "G64 Blending, Feathering &amp; Guardrails"},
            {"id": "macro-sync", "badge": "02", "label": "m3.py &amp; m5.py Snippets (IHS &amp; M62/M63)"},
            {"id": "3d-ramp-leadin", "badge": "03", "label": "3D Ramp Lead-Ins (#1113 &amp; #1110)"},
            {"id": "tab-cutting", "badge": "04", "label": "Tab Cutting (m35.py &amp; m33.py)"},
            {"id": "xml-links", "badge": "05", "label": "config.xml Import &amp; Guides"},
            {"id": "import-warnings-faq", "badge": "FAQ", "label": "SimCNC (config.xml) Warnings FAQ"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G90 G17 G40 G49 G69 G64 P0.3|0.4", "desc": "Metric G64 P (even in G20); bans G61"},
                    {"code": "G0 X<x> Y<y> (Flat)", "desc": "Flat rapid (#1123/#1124 plate Z reuse)"},
                    {"code": "G93 -> G1 X Y A F<1/t> -> G94", "desc": "3.6+ coordinated rotary pre-pierce"},
                ],
                "note": "3.5 uses G0 XY + G1 A F<rotFeed>; 3.6+ uses G93 coordinated pre-pierce then restores G94.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "; SimCNC M3 handles IHS", "desc": "Managed inside m3.py macro"},
                    {"code": "#1110=<t> #1111=<A> #1112=<psi>", "desc": "Thickness, amps & gas pressure"},
                    {"code": "#1090=<V> #1091=<pd> #1092=<F>", "desc": "Arc voltage, pierce dwell & feed"},
                    {"code": "#1113=<0|1> #1114=<mode>", "desc": "3D ramp flag & process mode"},
                ],
                "note": "Modal tracking omits unchanged registers between features; flat plate reuses Z if #1124=1.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "M63 P0 (or #4061=100)", "desc": "Lock THC before firing torch"},
                    {"code": "M3 S1", "desc": "m3.py probes, lifts, fires M62 P1, waits ArcOK"},
                    {"code": "G4 P1", "desc": "1 ms sync boundary on flat before THC unlock"},
                ],
                "note": "When #1113=1 (3D ramp), m3.py holds at pierce height and skips stationary plunge.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G93 F<.4f> (3.6+) | G94 (3.5)", "desc": "4-dec G93 (0.0001 floor) + 0.002mm feather"},
                    {"code": "Z#3 / Z[#3 +/- off]", "desc": "Z anchored to m3.py probe register #3"},
                    {"code": "M62 P0 / M63 P0", "desc": "Synced THC unlock / corner lock"},
                    {"code": "M63 P0 + M63 P1", "desc": "Zero-overburn early extinguish on-the-fly"},
                ],
                "note": "Coalesces <0.05 mm / 0.02 deg micro-moves and inserts 0.002 mm feathering on axis switches.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "G94 F<feed>", "desc": "Finalize feathering & restore G94"},
                    {"code": "G17", "desc": "Restore XY arc plane"},
                    {"code": "M5", "desc": "Extinguish arc (if not M63 P1 early off)"},
                    {"code": "M63 P<pin> / [G4 P<ms>]", "desc": "Disable THC + optional STM32 unwind dwell"},
                ],
                "note": "Motion-sync M63 P1 stops the arc at full speed before closure with zero pause divots.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G0 Z<safeZ>", "desc": "Retract to Safe Z clearance"},
                    {"code": "#4061 = #50 / M<unlock>", "desc": "Reset THC & dynamic #1111/#1112/#1090"},
                    {"code": "M112 / G1 Y0 / M30 / %", "desc": "EOF A-axis homing macro, recenter & end"},
                ],
                "note": "Phase-preserving G92 A unwinds (never G92.1); enforces #1999 parameter ceiling (#4061 allowlist).",
            },
        ],
        "sections": [
            {
                "id": "blending-g93",
                "badge": "G93 & Guardrails",
                "title": "Trajectory Blending, Micro-Move Coalescing &amp; Guardrails",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Blending &amp; <code class="mono">G93</code> Precision:</strong> Emits <code class="mono">G69</code> plus metric <code class="mono">G64 P0.3</code> (flat/round) or <code class="mono">P0.4</code> (HSS) even inside <code class="mono">G20</code> inch files (banning <code class="mono">G61</code>), and formats <code class="mono">G93 F</code> to <code class="mono">4</code> decimals with a <code class="mono">0.0001</code> floor.</li>
              <li><strong>Micro-Move Coalescing &amp; Axial Feathering:</strong> Coalesces sub-<code class="mono">0.05 mm</code> / <code class="mono">0.02&deg;</code> segments and inserts <code class="mono">0.002 mm</code> (<code class="mono">0.0026 mm</code> in <code class="mono">G20</code>) axial feathering between pure-XYZ and pure-ABC strokes to prevent SimCNC planner stalls.</li>
              <li><strong>Dwell, Parameter &amp; Arc Guardrails:</strong> Suppresses sub-<code class="mono">1 ms</code> dwells (<code class="mono">G4 P&ge;1</code> ms), limits lines to 1 <code class="mono">(...)</code> comment, enforces the <code class="mono">#1999</code> parameter ceiling (with <code class="mono">#4061</code> THC allowlist and <code class="mono">G4 P1</code> sync), formats <code class="mono">G20</code> arcs to <code class="mono">5</code> decimals (splitting full circles, no <code class="mono">G90.1/G91.1</code>), and runs phase-preserving <code class="mono">G92 A</code> unwinds (no <code class="mono">G92.1</code>).</li>
              <li><strong>Physics, THC &amp; Air-Scribe Routing:</strong> Locks THC below <code class="mono">85%</code> speed, unlocks THC right after lead-in ramps on larger flat/round features, clamps Z on flat faces with ADLS, and runs Crown-IHS lead-in ramps on eccentric round bevels. Pneumatic offset air-scribes use <code class="mono">G52</code> + <code class="mono">M8</code>/<code class="mono">M9</code>, keeping <code class="mono">#1114=3</code> strictly for Coaxial EasyScribe with an <code class="mono">M0</code> swap pause.</li>
            </ul>""",
            },
            {
                "id": "macro-sync",
                "badge": "m3.py & m5.py",
                "title": "Macro Handshake (<code class=\"mono\">m3.py</code> &amp; <code class=\"mono\">m5.py</code> Snippets)",
                "body_html": """
            <p>
              Before <code class="mono">M3 S1</code>, your G-code sets modal registers for thickness (<code class="mono">#1110</code>), target arc voltage (<code class="mono">#1090</code>), pierce delay (<code class="mono">#1091</code>), calculated surface feed (<code class="mono">#1092</code>), 3D ramp flag (<code class="mono">#1113</code>), and process mode (<code class="mono">#1114</code>).
            </p>
            <p>
              SimCNC binds two trajectory-synchronized outputs in <code class="mono">___CONF.py</code>: <code class="mono">P0</code> (<code class="mono">ExtTrajSyncOut0</code>) locks/unlocks hardware THC (<code class="mono">M63 P0</code> / <code class="mono">M62 P0</code>), and <code class="mono">P1</code> (<code class="mono">ExtTrajSyncOut1</code>) fires/extinguishes the torch relay (<code class="mono">M62 P1</code> / <code class="mono">M63 P1</code>). <code class="mono">Arc OK</code> is read directly from CSMIO/IP-M digital input 7 via <code class="mono">check_arc_ok(d)</code>.
            </p>
            <div class="doc-code-block">
              <div class="doc-code-bar">
                <span class="doc-code-title"><span class="dot"></span> m3.py Snippet: Dual Ohmic/Floating IHS, Pierce Height &amp; M62 P1 Fire</span>
                <span class="doc-code-lang">PYTHON (SimCNC)</span>
              </div>
              <pre><code># 1. Ohmic + Floating touch-off on Probe 0 (Input 6 active-LOW, Input 5 = Ohmic)
result = d.executeProbing(CoordMode.Machine, Maximum_position, 0, Probing_velocity)
if not result:
    emergency("Probing did not trigger within Max_probing_distance")

pin5 = mod.getDigitalIO(IOPortDir.InputPort, 5)
Probe_touch_position = d.getProbingPosition(CoordMode.Machine)
if pin5 == DIOPinVal.PinReset:
    surface_z = Probe_touch_position[Axis.Z.value]  # Ohmic hit (0 deflection)
else:
    surface_z = Probe_touch_position[Axis.Z.value] + abs(Sensor_hysteresis)  # Floating head

# 2. Lift to Pierce Height and anchor Program Z
Pierce_height_position[Axis.Z.value] = surface_z + Pierce_height
d.moveToPosition(CoordMode.Machine, Pierce_height_position, Lifting_velocity)
d.setAxisProgPosition(Axis.Z, Pierce_height)

# 3. Pre-fire Arc OK sanity check, then fire via ExtTrajSyncOut1 (M62 P1 + Z micro-wiggle)
if check_arc_ok(d):
    emergency("PRE-FIRE FAULT: Arc OK input already active before firing")

fire_torch_hardware(d, Arc_Sync_Pin, unit)  # M62 P1 + 0.01 mm Z wiggle

max_time = time.time() + (Timeout_Torch_is_on / 1000.0)
while not check_arc_ok(d):
    if max_time &lt; time.time():
        emergency("Wait for Torch on (Arc OK) - Timeout")
    time.sleep(0.005)</code></pre>
            </div>
            <p>
              In <code class="mono">m5.py</code>, if the post already extinguished the arc on the fly with <code class="mono">M63 P1</code> (Zero-Overburn Early Torch-Out), <code class="mono">check_arc_ok(d)</code> is already false. <code class="mono">m5.py</code> skips the Z micro-wiggle and exits cleanly after locking THC:
            </p>
            <div class="doc-code-block">
              <div class="doc-code-bar">
                <span class="doc-code-title"><span class="dot emerald"></span> m5.py Snippet: Fast Extinguish Check &amp; Synced Torch Off</span>
                <span class="doc-code-lang">PYTHON (SimCNC)</span>
              </div>
              <pre><code>if check_arc_ok(d):
    # Arc is still live: run M63 P1 + M63 P0 + 0.01 mm Z micro-wiggle
    extinguish_torch_hardware(d, Arc_Sync_Pin, unit)
    max_time = time.time() + (Timeout_Torch_is_on / 1000.0)
    while check_arc_ok(d):
        if max_time &lt; time.time():
            emergency("Wait for Torch off (Arc OK false) - Timeout")
        time.sleep(0.005)
else:
    # Already extinguished at full speed by M63 P1: fast M5 without motion
    d.executeGCode("M63 " + Arc_Sync_Pin)
    d.executeGCode("M63 " + THC_Sync_Pin)
    d.setThcState(ThcState.Off)</code></pre>
            </div>
            <p>
              For full <code class="mono">ExtTrajSyncOut0/1</code> wiring and <code class="mono">___CONF.py</code> micro-wiggle internals, see <a href="../../simcnc-motion-sync.html" style="color: var(--cyan-400);">Tutorial 07: SimCNC Motion-Synchronized Torch &amp; 3D Ramp Lead-Ins</a> and <a href="../../rotary-and-sheet-feedrates.html" style="color: var(--amber-400);">Tutorial 11: G94, G93 &amp; G20/G21 Feedrates</a>.
            </p>""",
            },
            {
                "id": "3d-ramp-leadin",
                "badge": "3D Ramp",
                "title": "How 3D Ramp Lead-Ins Work (<code class=\"mono\">#1113</code>, <code class=\"mono\">#1110</code> &amp; <code class=\"mono\">m3.py</code>)",
                "body_html": """
            <p>
              Standard plasma plunges drop straight down into the pierce puddle, which splashes molten slag onto your shield and nozzle. With <strong>3D Ramp Lead-In</strong> enabled, the torch pierces at <code class="mono">Pierce_height</code> and then ramps diagonally down to <code class="mono">Cut_height</code> (<code class="mono">Z#3</code>) during the lateral lead-in move while THC stays locked.
            </p>
            <div class="doc-code-block">
              <div class="doc-code-bar">
                <span class="doc-code-title"><span class="dot"></span> G-Code Handshake for 3D Ramp Lead-In</span>
                <span class="doc-code-lang">GCODE (.nc)</span>
              </div>
              <pre><code>#1110 = 3.000   (Material thickness in current units)
#1113 = 1       (Arm 3D ramp lead-in inside m3.py)
M63 P0          (Lock THC before firing and across the ramp)
M3 S1           (Probes, pierces, and returns with Z still at Pierce_height)
G1 X12.500 Y10.000 Z#3 F2800.0  (Diagonal 3D ramp down to Cut_height #3)
M62 P0          (Unlock THC only after reaching Cut_height)</code></pre>
            </div>
            <p>
              Inside <code class="mono">m3.py</code>, <code class="mono">#1113</code> and <code class="mono">#1110</code> control both the pierce dwell and the Z handoff:
            </p>
            <div class="doc-code-block">
              <div class="doc-code-bar">
                <span class="doc-code-title"><span class="dot cyan"></span> m3.py Snippet: Thickness-Aware Dwell &amp; Pierce-Height Handoff</span>
                <span class="doc-code-lang">PYTHON (SimCNC)</span>
              </div>
              <pre><code>ramp_lead_in_enabled = (float(d.getMachineParam(1113)) == 1.0)
Material_thickness = float(d.getMachineParam(1110) or 0.0)

if Pierce_delay &gt; 0:
    thresh_thin = 0.080 if unit == "inch" else 2.0
    if ramp_lead_in_enabled and Material_thickness &lt;= thresh_thin and Pierce_delay &lt; 400.0:
        # Thin sheet (&lt;= 14 GA / 2.0 mm): 60% flying dwell (min 100 ms)
        dwell_ms = max(100, int(Pierce_delay * 0.60))
    else:
        # Plate (&gt; 2.0 mm) or standard pierce: full 100% blowout dwell
        dwell_ms = int(Pierce_delay)

    max_time = time.time() + (dwell_ms / 1000.0)
    while max_time &gt; time.time():
        if not check_arc_ok(d):
            emergency("Torch went out while piercing")
        time.sleep(0.005)

if ramp_lead_in_enabled:
    # Keep Z at Pierce_height so the next G1 ... Z#3 block ramps down smoothly
    d.setMachineParam(1113, 0.0)  # Reset one-shot handoff flag
else:
    if Pierce_height != Cut_height:
        Cut_height_position = d.getPosition(CoordMode.Program)
        Cut_height_position[Axis.Z.value] = Cut_height
        d.moveToPosition(CoordMode.Program, Cut_height_position, Descent_velocity)</code></pre>
            </div>""",
            },
            {
                "id": "tab-cutting",
                "badge": "Tab Cutting",
                "title": "Tab Cutting &amp; Fast Bridge Restarts (<code class=\"mono\">m35.py</code> &amp; <code class=\"mono\">m33.py</code>)",
                "body_html": """
            <p>
              When cutting micro-tabs (uncut bridge joints that hold parts in the skeleton), running a full <code class="mono">M5</code> retract and <code class="mono">M3</code> IHS touch-off on every tab wastes seconds per part. Instead, your G-code calls <code class="mono">M35</code> to pause the arc across the tab and <code class="mono">M33</code> to re-ignite on the other side without re-probing:
            </p>
            <div class="doc-code-block">
              <div class="doc-code-bar">
                <span class="doc-code-title"><span class="dot"></span> G-Code Sequence Across an Uncut Tab Bridge</span>
                <span class="doc-code-lang">GCODE (.nc)</span>
              </div>
              <pre><code>G1 X48.000 Y20.000 F2800.0   (Cut up to tab entry)
M35                          (Lock THC M63 P0, wait zero vel, extinguish M63 P1)
G0 X52.000 Y20.000           (Rapid across 4 mm uncut tab at cut height)
M33                          (Lift to Pierce_height, fire M62 P1, 35% dwell, plunge, M62 P0)
G1 X90.000 Y20.000 F2800.0   (Resume cutting with THC active)</code></pre>
            </div>
            <p>
              <strong><code class="mono">m35.py</code> (Tab Pause):</strong> Locks THC first (<code class="mono">M63 P0</code>) so the head cannot dive as the arc drops, waits for zero velocity, then extinguishes <code class="mono">M63 P1</code> and confirms <code class="mono">Arc OK</code> is false while holding Z at cut height.
            </p>
            <div class="doc-code-block">
              <div class="doc-code-bar">
                <span class="doc-code-title"><span class="dot cyan"></span> m35.py Snippet: Lock THC, Stop Motion &amp; Extinguish Across Tab</span>
                <span class="doc-code-lang">PYTHON (SimCNC)</span>
              </div>
              <pre><code>d.executeGCode("M63 " + THC_Sync_Pin)  # Lock THC immediately
d.setThcState(ThcState.Off)

if not d.waitForZeroVelocity(0.5):
    emergency("M35 Zero Velocity - Timeout")

d.executeGCode("M63 " + Arc_Sync_Pin)  # Extinguish arc
max_time = time.time() + (Timeout_Torch_is_on / 1000.0)
while check_arc_ok(d):
    if max_time &lt; time.time():
        emergency("M35 Arc Extinguish Timeout")
    time.sleep(0.005)</code></pre>
            </div>
            <p>
              <strong><code class="mono">m33.py</code> (Tab Fast Restart):</strong> Skips IHS probing completely, lifts to <code class="mono">Pierce_height</code> to prevent slag blowback, fires <code class="mono">M62 P1</code>, dwells for 35% of normal pierce delay (minimum <code class="mono">50 ms</code>, since the electrode is hot and post-flow is active), plunges to <code class="mono">Cut_height</code>, and re-enables THC via <code class="mono">M62 P0</code>.
            </p>
            <div class="doc-code-block">
              <div class="doc-code-bar">
                <span class="doc-code-title"><span class="dot emerald"></span> m33.py Snippet: No-IHS Lift, 35% Restart Dwell &amp; THC Re-Enable</span>
                <span class="doc-code-lang">PYTHON (SimCNC)</span>
              </div>
              <pre><code>d.executeGCode("M63 " + THC_Sync_Pin)  # Keep THC locked during restart
if not d.waitForZeroVelocity(0.5):
    emergency("M33 Zero Velocity - Timeout")

# 1. Lift to Pierce_height without re-probing IHS
current_pos = d.getPosition(CoordMode.Program)
if Pierce_height &gt; Cut_height and current_pos[Axis.Z.value] &lt; (Pierce_height - 0.1):
    pierce_pos = current_pos.copy()
    pierce_pos[Axis.Z.value] = Pierce_height
    d.moveToPosition(CoordMode.Program, pierce_pos, Lifting_velocity)

# 2. Fire torch (M62 P1) and wait for Arc OK
d.executeGCode("M62 " + Arc_Sync_Pin)
max_time = time.time() + (Timeout_Torch_is_on / 1000.0)
while not check_arc_ok(d):
    if max_time &lt; time.time():
        emergency("M33 Wait for Torch on - Timeout")
    time.sleep(0.005)

# 3. Reduced tab restart dwell (35% of Pierce_delay, min 50 ms)
tab_restart_delay = min(Pierce_delay, max(50.0, Pierce_delay * 0.35))
dwell_end = time.time() + (tab_restart_delay / 1000.0)
while dwell_end &gt; time.time():
    if not check_arc_ok(d):
        emergency("M33 Torch went out while restarting on tab")
    time.sleep(0.005)

# 4. Plunge to Cut_height, unlock THC (M62 P0), and restore feedrate
if Pierce_height != Cut_height:
    cut_pos = d.getPosition(CoordMode.Program)
    cut_pos[Axis.Z.value] = Cut_height
    d.moveToPosition(CoordMode.Program, cut_pos, Descent_velocity)

d.waitForZeroVelocity(0.1)
d.executeGCode("M62 " + THC_Sync_Pin)
d.setFeedrate(Feed_Rate)</code></pre>
            </div>""",
            },
            {
                "id": "xml-links",
                "badge": "config.xml",
                "title": "One-Click <code class=\"mono\">config.xml</code> Import",
                "body_html": """
            <p>
              Upload your SimCNC 3.6 <code class="mono">config.xml</code> in the <strong>Machines</strong> modal (<span class="ui-chip">Import SimCNC Config (config.xml)</span>) to auto-fill base units, XYZA velocity/acceleration/jerk limits, and rotary <code class="mono">rad/s</code> limits. Any axis, IJK, or MotionKit mismatches link straight to the <a href="#import-warnings-faq" style="color: var(--cyan-400);">SimCNC config.xml Import Warnings FAQ</a> below.
            </p>""",
            },
        ],
    },
    {
        "slug": "GenericG94",
        "is_scribing": False,
        "name": "Portable RS-274 (generic_g94)",
        "short_name": "Portable RS-274",
        "ext": ".nc",
        "rotary_mode": "Modal G94 (dL_xyz/dt; deg/min or rad/min)",
        "ihs_summary": "Pre-zeroed Z0 default (or optional G38.2/G31/G28.1)",
        "torch_summary": "M03 / M05 (split 3D ramp; Dry-Run suppress option)",
        "thc_summary": "None default (warning on 3D/4D Z) or M62/M63 / custom M",
        "sync_summary": "Strict ISO 6983 core, uppercase (COMMENT) <= 80 chars, G92 A unwind",
        "card_summary": "Clean ISO 6983 G94 core with configurable G04 dwells, swing-envelope Safe Z, optional THC/IHS, and Dry-Run mode.",
        "badge_label": "Portable ISO 6983 RS-274 &bull; generic_g94 (.nc)",
        "meta_title": "Portable RS-274 (generic_g94) Setup & Cut Cycle | RotaryCAM Docs",
        "meta_description": "Portable RS-274 (generic_g94) setup: ISO 6983 G00-G94/M03-M30 core, pre-zeroed Z0 vs IHS, G04 P/X dwells, THC M62-M63 or Custom, and Dry-Run.",
        "hero_title_html": 'Portable RS-274 <span class="text-gradient-amber">(generic_g94) Setup</span>',
        "subtitle_html": 'Strict ISO 6983 <code class="mono">G94</code> post-processor for open-source, retrofit, and industrial controllers without vendor macros. Zero <code class="mono">;</code>, <code class="mono">%</code>, <code class="mono">G49</code>, or <code class="mono">G92.1</code> rewrites.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Extension:</strong> <code class="mono">.nc</code>'},
            {"style": "", "html": '<strong>Comments:</strong> Uppercase <code class="mono">(COMMENT)</code> &le; 80 chars'},
            {"style": "", "html": '<strong>Modes:</strong> <code class="mono">Dry-Run</code> &bull; <code class="mono">deg/min</code> or <code class="mono">rad/min</code>'},
        ],
        "toc": [
            {"id": "iso-subset", "badge": "01", "label": "Strict ISO 6983 Subset &amp; Hygiene"},
            {"id": "thc-dwells", "badge": "02", "label": "THC Modes, IHS &amp; G04 Dwells"},
            {"id": "rotary-limits", "badge": "03", "label": "Cartesian G94 Feeds &amp; Incompatibilities"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G20|G21 / G90 / G17 / G40 / G94", "desc": "Clean ISO startup (zero G49 or G92.1)"},
                    {"code": "G0 Z<safeZ>", "desc": "Retract above swing envelope before A rapid"},
                    {"code": "G0 X<x> Y<y> A<a>", "desc": "Suppresses A words on 2D flat sheet"},
                ],
                "note": "Always lifts to Safe Z before any rotary A rapid so spinning tube corners clear the torch.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "(Pre-zeroed Z0 default)", "desc": "No controller probe macro required"},
                    {"code": "G38.2 / G31 / G28.1 (opt)", "desc": "Optional explicit surface probe + G92 Z"},
                ],
                "note": "Dry-Run mode skips probing and positions directly at cut height.",
            },
            {
                "num": 3,
                "title": "Pierce & Dwell",
                "codes": [
                    {"code": "G0 Z<pierceZ>", "desc": "Move to pierce height"},
                    {"code": "M63 P<n> | M<lock> (opt)", "desc": "Optional THC lock (None by default)"},
                    {"code": "M03", "desc": "Fire torch (suppressed in Dry-Run)"},
                    {"code": "G04 P0.500 | P500 | X0.500", "desc": "Configurable dwell (>= 10 ms) or off"},
                    {"code": "G1 Z<cutZ> F<plunge>", "desc": "Plunge (3D ramp splits after M03+dwell)"},
                ],
                "note": "If THC=None on 3D/4D Z motion, header prints an explicit warning to disable external THC.",
            },
            {
                "num": 4,
                "title": "Cut & THC Control",
                "codes": [
                    {"code": "G94 F<dL_xyz/dt>", "desc": "Cartesian XYZ speed (<= 2.5 deg rotary steps)"},
                    {"code": "G1 A<a> F<deg/rad>", "desc": "Pure-A feed in deg/min or rad/min"},
                    {"code": "M62/M63 or M<lock/unlock>", "desc": "Optional digital/custom THC modulation"},
                ],
                "note": "Snaps linear jitter below 0.005 mm; outputs explicit Z = currZm + cutHeight.",
            },
            {
                "num": 5,
                "title": "Torch Off & Unlock",
                "codes": [
                    {"code": "M63 P<n> | M<lock> (opt)", "desc": "Optional THC lock before torch off"},
                    {"code": "M05", "desc": "Extinguish torch (suppressed in Dry-Run)"},
                ],
                "note": "Pure M05 shutdown keeps stock RS-274 controllers predictable.",
            },
            {
                "num": 6,
                "title": "Safe Retract & Unwind",
                "codes": [
                    {"code": "G0 Z<safeZ>", "desc": "Retract to Safe Z clearance"},
                    {"code": "G92 A<mod_360>", "desc": "Modulo-360 unwind (no G92.1)"},
                    {"code": "G1 Y0|X0 / M30", "desc": "Optional homing macro, recenter & end"},
                ],
                "note": "Not compatible with Burny, Dynatorch, or FlashCut Stingray controllers.",
            },
        ],
        "sections": [
            {
                "id": "iso-subset",
                "badge": "ISO Core",
                "title": "Strict Portable RS-274 Subset &amp; Comment Hygiene",
                "body_html": """
            <p>
              Use <code class="mono">generic_g94</code> for open-source, retrofit, or industrial <code class="mono">G94</code> controllers that do not use vendor macros. Output stays strictly inside <code class="mono">G00, G01, G02, G03, G04, G17, G20/G21, G40, G90, G92, G94, M03, M05, M30</code>. All comments are uppercase <code class="mono">(COMMENT)</code> blocks capped at <code class="mono">&le; 80</code> chars, with zero <code class="mono">;</code> semicolons, zero <code class="mono">%</code> framing, zero <code class="mono">G49</code>, and zero <code class="mono">G92.1</code> or <code class="mono">G10 L20</code> work-offset rewrites.
            </p>""",
            },
            {
                "id": "thc-dwells",
                "badge": "THC & IHS",
                "title": "THC Mode, Pre-Zeroed <code class=\"mono\">Z0</code>, Dwell Formats &amp; Dry-Run",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>THC Mode (<code class="mono">None</code> Default vs. <code class="mono">M62/M63</code> or Custom M-Codes):</strong> Defaults to zero THC M-codes and prints an explicit header warning on 3D ramps and 4D Z motion so you disable external voltage THC. Enable <code class="mono">M62/M63</code> or custom M-codes if your hardware THC accepts digital hold.</li>
              <li><strong>Pre-Zeroed <code class="mono">Z0</code> &amp; Configurable <code class="mono">G04</code> Dwells:</strong> Assumes pre-zeroed top-surface <code class="mono">Z0</code> by default (or choose <code class="mono">G38.2</code>, <code class="mono">G31</code>, or <code class="mono">G28.1</code>). Format dwells as <code class="mono">G04 P0.500</code>, <code class="mono">G04 P500</code>, <code class="mono">G04 X0.500</code>, or off (<code class="mono">&ge; 10 ms</code> clamp).</li>
              <li><strong>Split 3D Ramps &amp; Dry-Run:</strong> On 3D ramps, <code class="mono">M03</code> and dwell split cleanly before the angled descent. Toggle <strong>Dry-Run</strong> to verify clearances and rotations with <code class="mono">M03</code> suppressed.</li>
            </ul>""",
            },
            {
                "id": "rotary-limits",
                "badge": "Rotary & Warnings",
                "title": "Cartesian <code class=\"mono\">G94</code> Feeds &amp; Incompatible Controllers",
                "body_html": """
            <ul class="doc-bullet-list">
              <li><strong>Combined <code class="mono">G94</code> Feeds:</strong> Mixed moves output <code class="mono">F_G94 = dL_xyz / dt</code>; pure-<code class="mono">A</code> rotations output <code class="mono">deg/min</code> or <code class="mono">rad/min</code>.</li>
              <li><strong>Safe Z &amp; <code class="mono">&le; 2.5&deg;</code> Discretization:</strong> Snaps jitter below <code class="mono">0.005 mm</code>, retracts above the swing envelope before <code class="mono">A</code> rapids, discretizes rotary contours at <code class="mono">&le; 2.5&deg;</code>, suppresses <code class="mono">A</code> on 2D flat sheet, and resets wrap via 360&deg; <code class="mono">G92 A</code>.</li>
            </ul>
            <div class="doc-callout warning">
              <div class="doc-callout-title">&#9888; Incompatible Controllers: Burny, Dynatorch &amp; FlashCut Stingray</div>
              <p>
                Portable RS-274 (<code class="mono">generic_g94</code>) is <strong>NOT compatible with Burny, Dynatorch, or FlashCut Stingray</strong> controllers, which rely on proprietary dialects, word ordering, or non-standard ESSI/torch protocols.
              </p>
            </div>""",
            },
        ],
    },
    {
        "slug": "Scribing",
        "is_scribing": True,
        "name": "Coaxial EasyScribe vs. Pneumatic Air-Scribe",
        "short_name": "Scribing (EasyScribe / Air)",
        "ext": "Multi-Tool",
        "rotary_mode": "All 14 Controllers (Pro Shop)",
        "ihs_summary": "Surface touch-off + spring preload Z_scribe (1.0-1.5 mm)",
        "torch_summary": "EasyScribe: Arc strictly OFF (M0 swap) | Air: M3 $1 / M39 / T111",
        "thc_summary": "THC locked throughout marking strokes",
        "sync_summary": "EasyScribe coaxial (0 wiring) vs Pneumatic (G52 / G54 baked)",
        "card_summary": "Engrave Part IDs, bend lines &amp; weld ticks using coaxial EasyScribe (all controllers, M0 swap) or pneumatic offset air-scribe.",
        "badge_label": "Multi-Tool Marking &bull; Pro Shop ($399)",
        "meta_title": "Coaxial EasyScribe & Air-Scribe Setup | RotaryCAM Docs",
        "meta_description": "Coaxial EasyScribe vs pneumatic offset air-scribe setup across 14 controllers: M0 tool pauses, Z_scribe preload, M3 $1, T111 M6, and G52/G54 shifts.",
        "hero_title_html": 'Scribing: <span class="text-gradient-amber">EasyScribe &amp; Air-Scribe</span>',
        "subtitle_html": 'Engrave Part IDs, chassis bend lines, and weld fit-up witness ticks directly on your parts before cutting, using either a drop-in <strong>Coaxial EasyScribe</strong> or a dedicated <strong>Pneumatic Offset Air-Scribe</strong>.',
        "meta_pills": [
            {"style": "cyan", "html": '<strong>Tier:</strong> Pro Shop ($399)'},
            {"style": "", "html": '<strong>Coaxial EasyScribe:</strong> All 14 Controllers &bull; Auto <code class="mono">M0</code> Swap'},
            {"style": "", "html": '<strong>Pneumatic Air-Scribe:</strong> Native Multi-Tool &bull; Zero Swap Pause'},
        ],
        "toc": [
            {"id": "easyscribe", "badge": "01", "label": "Coaxial Drag Scribing (EasyScribe)"},
            {"id": "pneumatic", "badge": "02", "label": "Pneumatic Offset Air-Scribe"},
        ],
        "stages": [
            {
                "num": 1,
                "title": "Rapid & Rotate",
                "codes": [
                    {"code": "G0 X<x> Y<y> A<a>", "desc": "Coaxial: torch center; Air: + (dx, dy) offset"},
                    {"code": "[M0 Swap Pause]", "desc": "EasyScribe prompts tool swap before/after plasma"},
                ],
                "note": "Pneumatic scribes bake XY offset into G54 on Mach3/Acorn/WinCNC or shift via G52 on Mach4/UCCNC/grblHAL.",
            },
            {
                "num": 2,
                "title": "IHS Touch-Off",
                "codes": [
                    {"code": "G38.2 / G31 / M150", "desc": "Touch-off stock surface (controller dialect)"},
                    {"code": "#<keep-z-motion>=1", "desc": "QTPlasmaC coaxial scribe-only regime"},
                ],
                "note": "Touch-off sets exact surface height before engaging spring preload or air slide.",
            },
            {
                "num": 3,
                "title": "Preload / Slide On",
                "codes": [
                    {"code": "G1 Z-Z_scribe (1.0-1.5 mm)", "desc": "EasyScribe plunges into spring preload"},
                    {"code": "M3 $1 S1 | T111 M6 | M39", "desc": "Pneumatic slide extend + air on"},
                    {"code": "THC Locked (Arc OFF)", "desc": "Zero plasma M3 ignition on EasyScribe"},
                ],
                "note": "Plasma arc is strictly OFF during EasyScribe drag passes.",
            },
            {
                "num": 4,
                "title": "Scribe & Track",
                "codes": [
                    {"code": "G1 / G2 / G3 (G94/G93)", "desc": "Drag or impact-scribe IDs & bend lines"},
                    {"code": "THC Locked", "desc": "Voltage THC disabled across all strokes"},
                ],
                "note": "Uses G93 on 4-axis rotary paths so scribe speed stays uniform around curved tubes.",
            },
            {
                "num": 5,
                "title": "Lift / Slide Off",
                "codes": [
                    {"code": "M5 $1 | M40 | M5", "desc": "Pneumatic air off + retract slide"},
                    {"code": "G0 Z<safeZ>", "desc": "Lift EasyScribe stylus clear between strokes"},
                ],
                "note": "Multi-stroke marks retract to Safe Z between characters and ticks.",
            },
            {
                "num": 6,
                "title": "Tool Swap / Restore",
                "codes": [
                    {"code": "M0 (Swap to Plasma)", "desc": "EasyScribe prompt before plasma cuts"},
                    {"code": "T112 M6 | G52 X0 Y0", "desc": "Pneumatic restores Plasma tool / clears G52"},
                ],
                "note": "Pneumatic air-scribe runs marking and plasma cutting in one hands-off program.",
            },
        ],
        "sections": [
            {
                "id": "easyscribe",
                "badge": "Coaxial Drag",
                "title": "Coaxial Drag Scribing (<code class=\"mono\">EasyScribe</code>)",
                "body_html": """
            <p>
              The EasyScribe tool replaces the shield cup and nozzle directly inside your plasma torch body. It needs zero auxiliary air valves or wiring and works on <strong>every table and controller (including Langmuir FireControl)</strong>:
            </p>
            <ul class="doc-bullet-list">
              <li><strong>Plasma Arc Strictly OFF:</strong> <code class="mono">M3</code> plasma ignition never fires during EasyScribe strokes.</li>
              <li><strong>Spring Preload Depth (<code class="mono">Z_scribe</code>):</strong> Touches off the stock surface, plunges into spring preload (<code class="mono">1.0-1.5 mm</code>), drags the diamond or carbide stylus across the contour, and retracts to Safe Z between strokes.</li>
              <li><strong>Automatic <code class="mono">M0</code> Swap Pause:</strong> When scribing and cutting in the same job, RotaryCAM inserts an <code class="mono">M0</code> pause prompting you to swap between the EasyScribe tool and plasma consumables.</li>
            </ul>""",
            },
            {
                "id": "pneumatic",
                "badge": "Pneumatic Offset",
                "title": "Pneumatic Offset Air-Scribe (Multi-Tool)",
                "body_html": """
            <p>
              For high-production shops with an air-powered stylus mounted alongside the plasma torch. RotaryCAM applies your physical <code class="mono">(X, Y, Z)</code> head offset automatically and runs all marking before switching to plasma in one hands-off run:
            </p>
            <ul class="doc-bullet-list">
              <li><strong>CSLab SimCNC:</strong> Pneumatic offset air-scribe via <code class="mono">G52 X&lt;dx&gt; Y&lt;dy&gt;</code> + <code class="mono">M8</code>/<code class="mono">M9</code> and <code class="mono">G52 X0 Y0</code> cancel (keeping <code class="mono">#1114=3</code> strictly for Coaxial EasyScribe with mandatory <code class="mono">M0</code> swap pause).</li>
              <li><strong>LinuxCNC QTPlasmaC:</strong> <code class="mono">M3 $1 S1</code> (air on + slide drop) / <code class="mono">M5 $1</code> (retract)</li>
              <li><strong>MASSO G3:</strong> <code class="mono">T111 M6</code> (switch to Air Scribe) / <code class="mono">T112 M6</code> (restore Plasma)</li>
              <li><strong>Centroid Acorn:</strong> <code class="mono">M39</code> (extend &amp; offset) / <code class="mono">M40</code> (retract)</li>
              <li><strong>Mach4, UCCNC, FlashCut, EdingCNC, PlanetCNC, grblHAL, Generic RS-274:</strong> Auxiliary M-code pair with automatic <code class="mono">G52 X&lt;dx&gt; Y&lt;dy&gt;</code> shift and <code class="mono">G52 X0 Y0</code> cancel.</li>
              <li><strong>ArtSoft Mach3 &amp; ShopSabre WinCNC:</strong> Auxiliary M-code pair with XY scribe offsets baked directly into <code class="mono">G54</code> coordinates (zero <code class="mono">G52/G92</code> conflict).</li>
              <li><strong>Pneumatic Peck Center-Spotting:</strong> Supported across all 13 third-party controllers for drill-ready bolt center dimples before plasma cutting.</li>
            </ul>""",
            },
        ],
    },
]

XML_IMPORT_WARNINGS = {
    "Mach3": [
        {
            "id": "faq-mach3-units",
            "style": "",
            "title_html": 'Unrecognized or Missing <code class="mono">&lt;Units&gt;</code>',
            "meaning_html": 'Your Mach3 XML did not specify inches or millimeters, so RotaryCAM defaulted Machine Units to <strong>mm</strong>. If your steps/unit in Motor Tuning are calibrated in inches, parts will cut 25.4x the wrong size.',
            "action_html": 'Check <strong>Machine Units</strong> (<code class="mono">mm</code> vs. <code class="mono">in</code>) in the RotaryCAM Machines modal and match your Mach3 Motor Tuning units.',
        },
        {
            "id": "faq-mach3-slaved-a",
            "style": "info",
            "title_html": 'Motor 3 (A-Axis) Slaved to X / Y / Z (<code class="mono">Slave0=0/1/2</code>)',
            "meaning_html": 'Your table uses Motor 3 (A-axis) as the second motor on a dual-drive gantry (common on Bulltear Plasma and HVAC gantry tables) instead of a rotary chuck.',
            "action_html": 'Flat-sheet DXF/SVG cuts work right away with zero changes. To cut round pipe on a dual-drive table, either switch <strong>Rotary Axis Mapping</strong> to <strong>3-Axis Y-Axis Wrap</strong> (and plug your rotary into Y), or unslave Motor 3 in Mach3 (<code class="mono">Config &rarr; Slave Axis</code>) if you move dual-drive slaving to hardware or the B-axis.',
        },
        {
            "id": "faq-mach3-a-angular",
            "style": "",
            "title_html": 'A-Axis Is Set to Linear Mode (<code class="mono">&lt;AAngular&gt;=0</code>)',
            "meaning_html": 'Mach3 treats your A-axis as linear millimeters or inches instead of degrees, so <code class="mono">G93</code> rotary speeds and chuck rotations will be way off.',
            "action_html": 'In Mach3, open <code class="mono">Config &rarr; General Config</code>, check <strong>A-Axis is Angular</strong>, save, and re-import your XML (or type your true A-axis <code class="mono">deg/min</code> limits directly into RotaryCAM).',
        },
        {
            "id": "faq-mach3-a-disabled",
            "style": "info",
            "title_html": '4th Axis Disabled (<code class="mono">&lt;AAxisOn&gt;=0</code>)',
            "meaning_html": 'The A-axis output is turned off in your Mach3 profile.',
            "action_html": 'Flat-sheet cuts work as-is with no changes. For 4-axis pipe cutting, enable Axis A in Mach3 (<code class="mono">Config &rarr; Ports &amp; Pins &rarr; Motor Outputs</code>), or switch RotaryCAM to <strong>3-Axis Y-Axis Wrap</strong>.',
        },
        {
            "id": "faq-mach3-spindle-delay",
            "style": "",
            "title_html": 'Spindle Spin-Up / Spin-Down Delay Active (<code class="mono">SpinDelayCW &gt; 0</code>)',
            "meaning_html": 'Mach3 adds an extra hidden pause after every <code class="mono">M3</code> torch fire on top of RotaryCAM\'s <code class="mono">G04</code> pierce delay, causing blown pierces and arc-loss faults.',
            "action_html": 'Open <code class="mono">Config &rarr; Ports &amp; Pins &rarr; Spindle Setup</code> in Mach3 and set CW and CCW <strong>Delay Spin UP</strong> and <strong>Spin DOWN</strong> to <code class="mono">0</code>.',
        },
        {
            "id": "faq-mach3-screenset",
            "style": "info",
            "title_html": 'Mill / Spindle Screenset Detected',
            "meaning_html": 'Your Mach3 profile loads a router or mill screenset (<code class="mono">.set</code>) instead of a plasma screenset, so on-screen THC controls and Arc OK LEDs may be missing.',
            "action_html": 'Load a plasma screenset in Mach3 (<code class="mono">View &rarr; Load Screens</code>), or verify your <code class="mono">M3/M5</code> torch output and THC pins before cutting.',
        },
        {
            "id": "faq-mach3-dwell-ms",
            "style": "danger",
            "title_html": 'G04 Dwell in Milliseconds (<code class="mono">&lt;DwellinMilli&gt;=1</code>)',
            "meaning_html": 'Mach3 reads <code class="mono">G04 P0.5</code> as 0.5 milliseconds instead of 0.5 seconds, so your torch plunges before piercing through the plate.',
            "action_html": 'Open <code class="mono">Config &rarr; General Config</code> in Mach3 and uncheck <strong>G04 Dwell in ms</strong> so Mach3 reads RotaryCAM\'s <code class="mono">G04 P</code> dwells in seconds.',
        },
        {
            "id": "faq-mach3-plasma-cv",
            "style": "",
            "title_html": 'Plasma Mode or CV Feedrate Active (<code class="mono">&lt;PlasmaMode&gt;=1</code> / <code class="mono">&lt;CVFeedOn&gt;=1</code>)',
            "meaning_html": 'Mach3\'s built-in Plasma Mode, CV Dist Tolerance, and CV Feedrate fight <code class="mono">G93</code> inverse-time rotary blending and cause choppy chuck motion.',
            "action_html": 'In Mach3 <code class="mono">Config &rarr; General Config</code>, uncheck <strong>Plasma Mode</strong> and <strong>CV Dist Tolerance</strong>, then open the <strong>Settings (Alt-6)</strong> tab and turn <strong>CV Feedrate OFF</strong>.',
        },
        {
            "id": "faq-mach3-lookahead",
            "style": "",
            "title_html": 'LookAhead Too High (<code class="mono">&lt;LookAhead&gt; &gt; 200</code>)',
            "meaning_html": 'LookAhead values above <code class="mono">200</code> lines in Mach3 can overflow the motion planner buffer and stutter on dense 4-axis tube saddle toolpaths.',
            "action_html": 'Open <code class="mono">Config &rarr; General Config</code> in Mach3 and set <strong>LookAhead</strong> to <code class="mono">200</code> lines.',
        },
        {
            "id": "faq-mach3-ij-mode",
            "style": "info",
            "title_html": 'Absolute IJ Arc Mode (<code class="mono">&lt;IJMode&gt;=0</code>)',
            "meaning_html": 'Your Mach3 default is Absolute IJ instead of Incremental IJ. RotaryCAM emits <code class="mono">G91.1</code> at the top of every file to force Incremental IJ, so normal runs cut fine, but mid-program restarts can drop back to Absolute IJ and throw crop-circle arcs.',
            "action_html": 'Switch <strong>IJ Mode</strong> to <strong>Inc</strong> in Mach3 <code class="mono">Config &rarr; General Config</code> so mid-program <em>Run From Here</em> restarts stay safe.',
        },
        {
            "id": "faq-mach3-safe-z",
            "style": "",
            "title_html": 'Safe Z Height Zero or Negative (<code class="mono">m_SafeZ &lt;= 0</code>)',
            "meaning_html": 'Mach3 has no positive Safe Z retract height configured, so pausing or stopping mid-cut will not clear clamps or rotating tube corners.',
            "action_html": 'Set a positive Safe Z height in Mach3 (<code class="mono">Config &rarr; Safe_Z Setup</code>) and verify your <strong>Safe Z Clearance</strong> in RotaryCAM clears your biggest tube diagonal.',
        },
        {
            "id": "faq-mach3-ess-g28",
            "style": "",
            "title_html": 'Warp9 ESS + <code class="mono">G28.1</code> Probing Warning',
            "meaning_html": 'Selecting <code class="mono">G28.1</code> touch-off probing with a Warp9 Ethernet SmoothStepper (ESS) often hangs the controller during floating-head probing.',
            "action_html": 'Keep RotaryCAM\'s <strong>Touch-Off Strategy</strong> on <code class="mono">G31 Probe</code> (the Mach3 default) instead of <code class="mono">G28.1</code>.',
        },
    ],
    "FlashCut": [
        {
            "id": "faq-flashcut-units",
            "style": "",
            "title_html": 'Unrecognized or Missing <code class="mono">SystemUnits</code>',
            "meaning_html": 'RotaryCAM could not read <code class="mono">SystemUnits</code> from your FlashCut <code class="mono">Setup.xml</code> and defaulted Machine Units to <strong>mm</strong>.',
            "action_html": 'Check <strong>Machine Units</strong> (<code class="mono">mm</code> vs. <code class="mono">in</code>) in the RotaryCAM Machines modal and match your FlashCut table units.',
        },
        {
            "id": "faq-flashcut-rotary-axis",
            "style": "info",
            "title_html": 'Missing or Unexpected <code class="mono">AxisParallel</code>',
            "meaning_html": 'Your <code class="mono">Setup.xml</code> did not specify which gantry rail your rotary attachment runs along, so RotaryCAM defaulted <strong>Rotary Tube Axis</strong> to <strong>X</strong>.',
            "action_html": 'If your rotary chuck sits parallel to the Y gantry rail, select <strong>Parallel to Y-Axis</strong> in RotaryCAM\'s Machines modal.',
        },
        {
            "id": "faq-flashcut-plasma-head",
            "style": "",
            "title_html": 'Plasma Head ID Not Found in <code class="mono">&lt;Machine&gt;&lt;FabHeads&gt;</code>',
            "meaning_html": 'RotaryCAM could not match your requested Plasma Head ID or found no <code class="mono">*PlasmaHead</code> entries in your FlashCut XML, so head ID, arc transfer, and torch M-codes could not be auto-filled.',
            "action_html": 'Pick your active plasma head from the dropdown in RotaryCAM, or type your <strong>Head ID</strong> (e.g. <code class="mono">Hplasma1</code>), <strong>Arc Transfer Input</strong>, and <code class="mono">M50/M51</code> M-codes manually.',
        },
        {
            "id": "faq-flashcut-zero-lift",
            "style": "",
            "title_html": '<code class="mono">ZeroLiftAxisPositionAfterTouchOff="False"</code>',
            "meaning_html": 'FlashCut is not resetting its Z lift coordinate to zero after <code class="mono">G605</code> touch-off probing. Standard 2D flat-sheet and round-pipe cuts work as-is, but 3D Ramp Lead-Ins and 4D square/angle tubes need a zeroed Z datum.',
            "action_html": 'Enable <strong>Zero Lift Axis Position After Touch Off</strong> inside FlashCut (<code class="mono">Setup &rarr; FabHeads</code>) before running 3D ramps or 4D structural tubing.',
        },
        {
            "id": "faq-flashcut-arc-transfer",
            "style": "",
            "title_html": 'Missing <code class="mono">M101 I&lt;n&gt;</code> Arc Transfer Input',
            "meaning_html": 'RotaryCAM could not find <code class="mono">M101 I&lt;n&gt;</code> in your Cut2D start macro (or had to guess from <code class="mono">InputLines</code>), so it cannot confirm which input waits for Arc OK.',
            "action_html": 'Open FlashCut (<code class="mono">Setup &rarr; I/O &rarr; Inputs</code>), find your Arc Transfer / Arc OK input line number, and enter that number in RotaryCAM\'s FlashCut settings.',
        },
    ],
    "SimCNC": [
        {
            "id": "faq-simcnc-units",
            "style": "",
            "title_html": 'Unrecognized or Missing <code class="mono">&lt;baseUnits&gt;</code>',
            "meaning_html": 'Your SimCNC <code class="mono">config.xml</code> did not list <code class="mono">&lt;baseUnits&gt;</code>, so RotaryCAM defaulted Machine Units to <strong>mm</strong>.',
            "action_html": 'Check <strong>Machine Units</strong> (<code class="mono">mm</code> vs. <code class="mono">in</code>) in RotaryCAM and confirm it matches your SimCNC Configuration units.',
        },
        {
            "id": "faq-simcnc-rotary-a",
            "style": "info",
            "title_html": '<code class="mono">axis_3</code> (A-Axis) Disabled, Unbound, or Set to <code class="mono">linear</code>',
            "meaning_html": 'In SimCNC, <code class="mono">axis_3</code> (A) is turned off, has no MotionKit assigned, or is configured as a <code class="mono">linear</code> axis instead of <code class="mono">angular</code>.',
            "action_html": 'Flat-sheet cuts work as-is. For 4-axis pipe cutting, open SimCNC (<code class="mono">Configuration &rarr; Axes</code>), enable <code class="mono">axis_3</code>, set its type to <strong>angular</strong>, bind a MotionKit, and re-import <code class="mono">config.xml</code>.',
        },
        {
            "id": "faq-simcnc-motionkit",
            "style": "",
            "title_html": 'Missing <code class="mono">&lt;motionKit_N&gt;</code> or Mismatched Dual-Drive Gantry Limits',
            "meaning_html": 'Either a <code class="mono">&lt;motionKit_N&gt;</code> block is missing under <code class="mono">&lt;device&gt;&lt;modules&gt;</code>, or the two motors on a dual-drive gantry have different velocity, acceleration, or jerk limits (which can rack the gantry).',
            "action_html": 'Copy Max Velocity, Accel, and Jerk from SimCNC (<code class="mono">Configuration &rarr; Modules</code>) into RotaryCAM manually, and make sure both dual-drive gantry MotionKits use identical limits in SimCNC.',
        },
        {
            "id": "faq-simcnc-ijk-mode",
            "style": "",
            "title_html": '<code class="mono">&lt;ijkMode&gt;</code> Not Set to <code class="mono">relative</code>',
            "meaning_html": 'SimCNC is expecting Absolute IJK arc centers while RotaryCAM outputs Incremental (Relative) IJK arcs (and does not emit <code class="mono">G90.1</code>/<code class="mono">G91.1</code> on SimCNC), causing huge unwanted arc loops or soft-limit errors.',
            "action_html": 'Open SimCNC (<code class="mono">Configuration &rarr; General</code>) and set <strong>Arc IJK Mode</strong> to <strong>Relative</strong>.',
        },
    ],
}
