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

## 2. Documentation HTML & Navigation Consistency Rules

When adding a new tutorial page `docs/<slug>.html`:

1. **Identical Single-Line Top Navigation Bar (`.site-header`)**:
   - The top `.site-header` navigation bar across `index.html`, `build-guide.html`, and all `docs/*.html` pages must have the exact same height (`69px`), typography, and single-line layout (`white-space: nowrap`).
   - Every `docs/*.html` file **MUST** include both:
     - The cache-busted stylesheet link `<link rel="stylesheet" href="docs.css?v=YYYYMMDD" />` (bump the `?v=` date whenever `docs.css` changes), **AND**
     - The inlined `<style>` block for `.site-header` in `<head>` so that browser or CDN caching of `docs.css` can never break the header layout.
   - Keep link labels in `.nav-links` concise (`Overview`, `01. Machine`, `02. Cut Paths`, `03. Nesting`, `04. Bending`, `05. Changelog`, etc.) so the navigation bar never wraps onto two lines at desktop widths (`>= 1080px`).

2. **Cross-Linking Checklist when Adding Tutorial `N`**:
   - Create `docs/<slug>.html` following the two-column `.docs-shell` template (sticky `.docs-sidebar` on the left with both "Tutorials & Guides" and "On This Page" TOC + `.docs-main` with `.doc-step-card` articles and `.docs-Lightbox` script).
   - Update `.docs-nav-list` (left sidebar), `.nav-links` (top header), `.docs-meta-pill` (`TUTORIAL XX OF YY`), `.docs-pagination` (prev/next links), and `.footer-links` across **all** `docs/*.html` pages.
   - Add a card for the new tutorial to `docs/index.html` and to the `#documentation` section of `index.html`.
   - Add the new URL to `sitemap.xml`.

3. **Automated Link & Asset Verification**:
   - Before committing, verify that every `href` and `src` across `index.html`, `build-guide.html`, and `docs/*.html` resolves to an existing file on disk, and verify the top navbar layout with headless Chrome at `1202px` width.
