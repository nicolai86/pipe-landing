# Pipe Landing & Documentation Agent Guide (`pipe-landing`)

This repository (`pipe-landing/`) powers `rotarycam.app` — the main landing page (`index.html`), the open-hardware machine build guide (`build-guide.html`), and the visual operator documentation hub (`docs/*.html`).

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
