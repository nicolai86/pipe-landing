# Pipe Landing & Documentation Agent Guide (`pipe-landing`)

This repository (`pipe-landing/`) powers `rotarycam.app` — the main landing page (`index.html`), the hardware THC sales page (`hardware-thc.html`), the open-hardware machine build guide (`build-guide.html`), the changelog (`changelog.html`), and the visual operator documentation hub (`docs/*.html`).

Every documentation tutorial and screenshot added or updated in `docs/` **MUST** follow the exact visual, cropping, annotation, and layout specification below so that all iterations look 100% identical.

---

## 1. Documentation Screenshot Processing Pipeline (MANDATORY)

All tutorial screenshots in `docs/assets/*.png` are generated deterministically by:
- **Script:** [`scripts/annotate_docs_screenshots.swift`](./scripts/annotate_docs_screenshots.swift)

**NEVER** embed raw macOS/Chrome window screenshots directly into `docs/`. Every screenshot must have the macOS window shadow and Chrome browser frame cropped out, be scaled to `2324 × 1397` (`16:9.6` aspect ratio), and use the exact glowing Amber (`#f59e0b`) and Cyan (`#06b6d4`) highlight boxes and callout pills implemented in `scripts/annotate_docs_screenshots.swift`.

### Step-by-Step Workflow for New Screenshots

#### Step 1: Generate a Coordinate Grid Overlay (`--grid` mode)
Before guessing any highlight coordinates, run the script in `--grid` mode on each raw screenshot to produce a cropped image with `100px` / `200px` X/Y grid lines:

```bash
swift scripts/annotate_docs_screenshots.swift --grid "/path/to/Screenshot.png" "/tmp/grid_step1.png"
```

- **Default Crop Rectangle (`3824 × 2484` Retina Chrome Window Capture):**
  - `CGRect(x: 224, y: 238, width: 3470, height: 2094)` (or `width: 3486, height: 2096` for older captures).
  - This strips the macOS window shadow, title bar, Chrome tab bar, and URL bar so `(0, 0)` is the top-left corner of the dark Pipe CAM web app header (`Pipe CAM XYZA`) and `(3470, 2094)` is the bottom-right status bar (`v1.0.0`).
  - If a raw screenshot was captured at a different window size or position, pass a custom `x,y,w,h` as the 4th argument (`swift scripts/annotate_docs_screenshots.swift --grid "/path/to/raw.png" "/tmp/grid.png" "x,y,w,h"`) and verify that zero browser chrome or desktop wallpaper is visible around the edges.

#### Step 2: Inspect the Grid Image & Record Bounding Boxes
Open `/tmp/grid_step1.png` with `read_file` and read the `(x, y, w, h)` coordinates directly from the yellow vertical (`x0, x200, ...`) and cyan horizontal (`y0, y100, y200, ...`) grid lines:
- Coordinates are in **top-down cropped source space** (`3470 × 2094`), where `x` increases left-to-right and `y` increases top-to-bottom.
- The script automatically converts top-down coordinates to AppKit bottom-up coordinates and scales them to the `2324 × 1397` output resolution.

#### Step 3: Add `ImageSpec` & `HighlightBox` Entries to `scripts/annotate_docs_screenshots.swift`
Append your new `ImageSpec` entries to the `specs` array in `scripts/annotate_docs_screenshots.swift`:

```swift
ImageSpec(
    inputPath: "/path/to/raw/Screenshot.png",
    outputName: "<tutorial>-<step>-<slug>.png",
    cropRect: defaultCrop,
    highlights: [
        HighlightBox(
            x: 1525, y: 1076, w: 440, h: 48,
            style: .amber,
            label: "1. Change Cuts from 3 to 5 & Edge Left to 30.0 mm",
            labelPos: .topLeft
        ),
        HighlightBox(
            x: 2580, y: 1078, w: 162, h: 44,
            style: .cyan,
            label: "2. Click Save (Saved ✓)",
            labelPos: .topRight
        )
    ]
)
```

##### Visual Style Constants (Enforced by `scripts/annotate_docs_screenshots.swift` — Do Not Alter)
- **Output Dimensions:** `2324 × 1397` PNG (`docs/assets/<tutorial>-<step>-<slug>.png`).
- **Highlight Styles (`HighlightStyle`):**
  - `.amber` (`#f59e0b`, stroke `alpha: 1.0`, fill `alpha: 0.09`): Use for **primary user actions** (buttons to click, inputs to edit, active selections).
  - `.cyan` (`#06b6d4`, stroke `alpha: 1.0`, fill `alpha: 0.08`): Use for **context regions, secondary panels, 3D viewport inspection areas, or secondary steps**.
- **Box Stroke & Glow:** Rounded rectangle (`radius: 8px`), outer glow (`shadowBlurRadius: 16.0`, `alpha: 0.75`, `lineWidth: 3.5`), plus crisp inner stroke (`lineWidth: 3.0`).
- **Callout Pill Badges:** `NSFont.systemFont(ofSize: 17, weight: .bold)`, white text, padding `14px × 7px`, dark slate fill `rgba(15, 20, 28, 0.95)`, `6px` corner radius, `2.2px` border matching the highlight color, drop shadow (`blur: 10`, `offset: (0, -2)`), clamped `8px` inside viewport bounds.
- **Label Placement (`LabelPosition`):** Choose `.topLeft`, `.topRight`, `.bottomLeft`, `.bottomRight`, `.rightCenter`, or `.leftCenter` so that the callout pill **never covers the UI control being highlighted** or overlaps another callout pill.

#### Step 4: Render & Visually Verify Every Output Image (MANDATORY)
Run the script (optionally passing a filename filter to render only the new tutorial's images):

```bash
swift scripts/annotate_docs_screenshots.swift bending-
```

Then **visually inspect every single generated PNG** in `docs/assets/` using `read_file`:
- Verify that no browser frame or window border is visible on any edge.
- Verify that every highlight box tightly frames its target button, row, input, or 3D region without cutting through text.
- Verify that callout pills do not overlap each other or obscure critical adjacent controls. If any box is off by even 10–20px, adjust `(x, y, w, h)` or `labelPos` in `scripts/annotate_docs_screenshots.swift` and re-run until pixel-perfect.

---

## 2. Jinja2 Documentation Template Engine & Navigation Consistency Rules

All `docs/*.html` pages (`docs/index.html` and every `docs/<slug>.html` tutorial) are stamped out deterministically from **Jinja2 templates** in `templates/docs/` using [`scripts/build_docs.py`](./scripts/build_docs.py):

- **Master Layout Template:** [`templates/docs/base.html.j2`](./templates/docs/base.html.j2) (shared `<head>`, inlined `.site-header` CSS, single-line top navigation bar, lightbox modal, and footer).
- **Tutorial Shell Template:** [`templates/docs/tutorial_base.html.j2`](./templates/docs/tutorial_base.html.j2) (hero header, `TUTORIAL XX OF YY` badge, sticky left sidebar with "Tutorials & Guides" + "On This Page" TOC, and automatic prev/next `.docs-pagination`).
- **Per-Page Content Templates:** `templates/docs/pages/<slug>.html.j2` (`index.html.j2`, `machine-configuration.html.j2`, `cut-path-configuration.html.j2`, `nesting.html.j2`, `bending.html.j2`, `changelog.html.j2`, `ai-autodetection.html.j2`, `simcnc-motion-sync.html.j2`).

### Workflow when Adding or Updating a Tutorial `N`:
1. Create or edit `templates/docs/pages/<slug>.html.j2` (extending `tutorial_base.html.j2` and filling `{% block tutorial_body %}...{% endblock %}`).
2. Add or update the tutorial's metadata entry in the `TUTORIALS` list in [`scripts/build_docs.py`](./scripts/build_docs.py) (and bump `CSS_VERSION` whenever `docs/docs.css` changes).
3. Run the Jinja2 builder & link verifier:
   ```bash
   python3 scripts/build_docs.py --verify
   ```
   This automatically stamps out `docs/index.html` and all `docs/<slug>.html` pages with synchronized `.nav-links`, `.docs-nav-list`, `TUTORIAL XX OF YY` pills, `.docs-pagination`, and `.footer-links`, and verifies that every `href` and `src` across the entire site resolves on disk.
4. Also add a card for the new tutorial to the `#documentation` section of `index.html` and add the new URL to `sitemap.xml`.
5. Verify with headless Chrome at `1202px` width that `.site-header` remains a single `69px` horizontal bar.

---

## 3. RotaryCAM Golden Rules of Copywriting & `pipe-copywriter` Subagent (MANDATORY)

Every time documentation (`docs/`, `templates/docs/`), the build guide (`build-guide.html`), the hardware THC page (`hardware-thc.html`), the changelog (`changelog.html`), or the homepage (`index.html`) is updated or added, `pipe-landing` **MUST invoke the specialized `pipe-copywriter` subagent** to review and rewrite the content to match the **5 RotaryCAM Golden Rules of Copywriting**.

### The 5 Golden Rules:

#### #1 Be simple & specific
Write plain, direct, human language: no jargon, no buzzwords, no fluff. Swap vague words like "seamless" or "leverage" for concrete details that explain HOW something works and WHAT the outcome is.

#### #2 Write like a human, NOT a corporation
Sound like you're explaining something important to someone you respect: conversational, confident, and direct. Avoid corporate voice. Write the way you'd talk.

#### #3 Focus on the User, not RotaryCam
Put the reader first. Focus on what THEY can achieve, not how great RotaryCam is.

#### #4 Get to the point, quick
Lead with the bottom-line result or number, say it once, and stop talking. Cut throat-clearing intros, repeated claims, stacked parentheticals, and dense multi-sentence walls of text. Aim for ~30-45% fewer words without dropping a single concrete spec, part number, or shop-floor fact: keep feature cards to 1-2 short, punchy sentences and section intros to 1-2 crisp sentences.

#### #5 NEVER use the em-dash (`—` / `&mdash;` / `&#8212;`)
Never use the AI-slop em-dash (`—` or `&mdash;`) anywhere on the site (titles, meta tags, headings, body copy, tables, callouts, or docs). Break clauses into two short sentences with a period, or use a colon, comma, or parentheses where natural. Before finishing any edit, run `rg '—|&mdash;|&#8212;|&#x2014;'` across modified files and `docs/` to verify **0 matches**.

### Fabrication & Welder Voice Guidelines:
- All copy MUST speak **fabrication language, not software engineering language**. Speak directly to fabricators, welders, chassis builders, and CNC plasma table operators.
- Never use software engineering jargon (e.g. "B-Rep topology extraction", "Graph Neural Network", "50-micron chordal deflection", "Euclidean manifold", "Jacobian acceleration", "TorchScript").
- Always translate into real-world welding and fabrication benefits:
  - "No unrolling solid models to flat 2D DXFs"
  - "Drop complete 3D STEP assemblies straight in"
  - "Cuts, fishmouths, copes, miters, and bolt holes detected automatically"
  - "Zero-gap saddle joints ready to weld with no angle-grinder fitting"
  - "Cuts round pipe, square tube, rectangular HSS, angle iron, and channel"
  - "Pack full 20ft/24ft/6m mill sticks with minimal scrap drop"
  - "Corner anti-dive prevents crashing torch nozzles into rectangular tube corners"
  - "Swirl gas direction ensures the clean square edge stays on your part, not the scrap"
  - "100% offline standalone software right at the machine next to the plasma table with zero internet or cloud dependency"
- Preserve all existing HTML elements, Jinja2 template blocks, styling, anchor IDs, and script dependencies.

---

## 4. 3D PCB STEP-to-WebGL Conversion Pipeline (`scripts/convert_pcb_step.py`)

Whenever adding or updating an interactive 3D PCB viewer on `build-guide.html` or `hardware-thc.html`, convert the exported Fusion 360 / Eagle / KiCad `.step` assembly (and optional `.brd` XML for 2D silkscreen text decals) using [`scripts/convert_pcb_step.py`](./scripts/convert_pcb_step.py):

```bash
/opt/homebrew/Caskroom/miniconda/base/envs/fovnet_ml/bin/python scripts/convert_pcb_step.py \
    --step /path/to/board.step \
    --out-mesh assets/<slug>-mesh.json.gz \
    --out-step-gz assets/<slug>.step.gz \
    [--brd /path/to/board.brd --out-silkscreen assets/<slug>-silkscreen.svg]
```

- Automatically preserves XCAF sRGB colors, groups faces into the exact PBR material buckets expected by `initPcbViewer()` (`fr4`, `copper`, `soldermask`, `silkscreen`, `metal`, `plastic`, `ceramic`, `led`, `default`), centers the assembly, rotates CAD Z-up into Three.js Y-up (`Rx(-90°)`), and emits `bounds` + `board` decal metadata.
- Pair with a static isometric preview PNG (`assets/<slug>-preview.png`) in `#thc-cover` so the page renders instantaneously and loads the WebGL mesh only when the user clicks **"Click to Explore"**.
