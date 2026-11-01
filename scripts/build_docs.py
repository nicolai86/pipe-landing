#!/usr/bin/env python3
"""
RotaryCAM / Pipe CAM Documentation Template Builder (`scripts/build_docs.py`)
=============================================================================
Stamps out `docs/index.html` and all `docs/<slug>.html` tutorial pages from
Jinja2 templates in `templates/docs/`, guaranteeing 100% identical headers,
single-line top navigation bars (`.site-header`), left sidebars, pagination
links, `TUTORIAL XX OF YY` badges, footers, and cache-busted `docs.css?v=...`.

Usage:
  python3 scripts/build_docs.py             # Build all docs/*.html pages
  python3 scripts/build_docs.py --verify    # Build and verify all internal links & assets
"""

import os
import re
import sys
from pathlib import Path

# Auto-locate a Python interpreter with Jinja2 installed if the default python3 lacks it
try:
    import jinja2
except ImportError:
    fallback_pythons = [
        "/opt/homebrew/Caskroom/miniconda/base/envs/fovnet_ml/bin/python3",
        "/opt/homebrew/Caskroom/miniconda/base/envs/bricks/bin/python3",
        "/opt/homebrew/Caskroom/miniconda/base/bin/python3",
    ]
    for py in fallback_pythons:
        if os.path.exists(py) and os.path.realpath(py) != os.path.realpath(sys.executable):
            os.execv(py, [py] + sys.argv)
    raise RuntimeError("Jinja2 is required to run scripts/build_docs.py. Install with `pip install jinja2`.")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import version
TEMPLATES_DIR = ROOT_DIR / "templates" / "docs"
PAGES_TEMPLATE_DIR = TEMPLATES_DIR / "pages"
DOCS_OUT_DIR = ROOT_DIR / "docs"

CSS_VERSION = "20261023"
VERSION = version.resolve_version()
BETA_LABEL = version.beta_label(VERSION)
FOOTER_TECH_STRIP = "G93 + G94 • ADLS • ZERO-BEVEL • CUT-AND-BEND • 1D STICK NESTING"

# Central single-source-of-truth registry of all documentation tutorials
TUTORIALS = [
    {
        "num": 1,
        "slug": "machine-configuration",
        "filename": "machine-configuration.html",
        "nav_short": "Machine",
        "sidebar_label": "Machine Configuration",
        "footer_label": "Machine Configuration",
        "breadcrumb_title": "Basic Machine Configuration",
        "meta_title": "01. Basic Machine Configuration — RotaryCAM Documentation",
        "meta_description": "Step-by-step guide to configuring 4-axis CNC plasma machine profiles, axis velocity/acceleration limits, G94/G93 controller dialects, synchronous THC corner locking, and zero-bevel defaults in RotaryCAM.",
        "hero_title_html": 'Basic <span class="text-gradient-amber">Machine Configuration</span>',
        "hero_subtitle_html": 'How to configure your 4-axis rotary plasma kinematics, controller G-code dialect (<code class="mono">G94</code> vs. <code class="mono">G93</code> inverse-time), synchronous Torch Height Control (THC) locking, and default cut compensation profiles.',
        "steps_count": 5,
        "steps_label": "5 Steps",
        "meta_pills": [
            {"style": "cyan", "html": "<strong>Persistence:</strong> Multi-Profile Saved Across Restarts"},
            {"style": "", "html": "<strong>Applies To:</strong> Any 4-Axis CNC (G93 / G94) • SimCNC, Mach4, LinuxCNC"},
        ],
        "toc": [
            {"id": "step-1", "badge": "01", "label": "Open Machine Profiles Modal"},
            {"id": "step-2", "badge": "02", "label": "Axis Kinematics &amp; Physical Limits"},
            {"id": "step-3", "badge": "03", "label": "Controller Dialect (G94 vs. G93)"},
            {"id": "step-4", "badge": "04", "label": "THC Lock/Unlock &amp; Hardware"},
            {"id": "step-5", "badge": "05", "label": "Zero-Bevel Defaults &amp; Saving"},
        ],
        "pagination_title": "Basic Machine Configuration",
        "pagination_desc": "Configure axis limits, G94/G93 dialects & synchronous THC locks",
        "hub_thumb": "assets/machine-config-2-limits.png",
        "hub_thumb_alt": "RotaryCAM Machine Profiles & Kinematics Modal",
        "hub_title": "Basic Machine Configuration",
        "hub_desc": "Configure your 4-axis CNC plasma kinematics, controller dialect (G94 vs. G93 inverse-time), synchronous Torch Height Control (THC) locking, and default zero-bevel &amp; corner-loop parameters.",
        "hub_topics": [
            "Velocity, acceleration, jerk &amp; Safe Z clearance limits",
            "SimCNC G94+G93 emulation vs. native G93 inverse-time",
            "Synchronous M62/M63 THC locking during corner slowdowns",
            "Creating, cloning &amp; persisting multiple machine profiles",
        ],
        "hub_cta_right": "5 Annotated Screenshots",
        "has_lightbox": True,
    },
    {
        "num": 2,
        "slug": "cut-path-configuration",
        "filename": "cut-path-configuration.html",
        "nav_short": "Cut Paths",
        "sidebar_label": "UI & Cut Path Config",
        "footer_label": "Cut Path Configuration",
        "breadcrumb_title": "UI Layout & STEP Cut Path Configuration",
        "meta_title": "02. UI Layout & STEP File Cut Path Configuration — RotaryCAM Documentation",
        "meta_description": "Step-by-step visual guide to RotaryCAM's 3D CAD assembly inspector, per-contour lead-in/lead-out settings, Zero-Bevel Dual-Curve saddle compensation, and 4-axis 3D toolpath simulation.",
        "hero_title_html": 'UI Layout &amp; <span class="text-gradient-amber">STEP Cut Path Configuration</span>',
        "hero_subtitle_html": 'Learn how to load a multi-body STEP file, switch between solids in the 3D assembly overview, inspect and customize individual cut contours (<code class="mono">STARTCUT</code>, <code class="mono">ENDCUT</code>, <code class="mono">CUTOUT</code>), apply Zero-Bevel Dual-Curve saddle compensation, and verify the 4-axis toolpath in 3D simulation.',
        "steps_count": 8,
        "steps_label": "8 Steps",
        "meta_pills": [
            {"style": "cyan", "html": "<strong>Fixture Used:</strong> Saddle Joint (Zero-Bevel)"},
            {"style": "", "html": "<strong>Key Feature:</strong> Per-Contour Lead-In / Zero-Bevel &amp; 3D Simulation"},
        ],
        "toc": [
            {"id": "step-1", "badge": "01", "label": "Load Saddle Joint CAD Fixture"},
            {"id": "step-2", "badge": "02", "label": "Entire Model Overview &amp; Solid Selector"},
            {"id": "step-3", "badge": "03", "label": "3D Part Preview &amp; Cut Contours"},
            {"id": "step-4", "badge": "04", "label": "Select the Saddle ENDCUT Contour"},
            {"id": "step-5", "badge": "05", "label": "Open Per-Contour ⚙ Config Drawer"},
            {"id": "step-6", "badge": "06", "label": "Apply 80% Zero-Bevel &amp; Save"},
            {"id": "step-7", "badge": "07", "label": "Start 4-Axis 3D Cut Simulation"},
            {"id": "step-8", "badge": "08", "label": "Verify Completed Saddle Toolpath"},
        ],
        "pagination_title": "UI Layout & STEP Cut Path Configuration",
        "pagination_desc": "Inspect 3D parts, configure per-contour Zero-Bevel & run 3D simulation",
        "hub_thumb": "assets/cut-path-6-zero-bevel.png",
        "hub_thumb_alt": "RotaryCAM Per-Contour Cut Path & Zero-Bevel Configuration",
        "hub_title": "UI Layout &amp; STEP Cut Path Configuration",
        "hub_desc": "Tour the 3D CAD assembly inspector, switch between individual tube solids, inspect lead-in/cut/lead-out contours, apply Zero-Bevel Dual-Curve compensation on a saddle joint, and verify in 3D simulation.",
        "hub_topics": [
            "Entire Model Overview &amp; Active CAD Solid switching",
            "3D part preview &amp; interactive contour selection (`ENDCUT`)",
            "Per-contour Lead-In, Lead-Out, Corner Loop &amp; Zero-Bevel (80%)",
            "Full 4-axis (XYZA) 3D toolpath simulation &amp; live DRO",
        ],
        "hub_cta_right": "8 Annotated Screenshots",
        "has_lightbox": True,
    },
    {
        "num": 3,
        "slug": "nesting",
        "filename": "nesting.html",
        "nav_short": "Nesting",
        "sidebar_label": "Multi-Part Stick Nesting",
        "footer_label": "Multi-Part Nesting",
        "breadcrumb_title": "Multi-Part Stick Nesting",
        "meta_title": "03. Multi-Part Stick Nesting — RotaryCAM Documentation",
        "meta_description": "Step-by-step guide to RotaryCAM's Multi-Part Pack Nesting: load a 37-part STEP assembly, filter by cross-section profile, pack 17 parts across multiple 6000 mm sticks at 99.8% efficiency, and export per-stick G-code.",
        "hero_title_html": 'Multi-Part <span class="text-gradient-amber">Stick Nesting</span>',
        "hero_subtitle_html": 'How to load a complex multi-body STEP weldment, group tubes by cross-section profile, automatically pack 17 parts across multiple <code class="mono">6000 mm</code> raw stock sticks at <code class="mono">99.8%</code> material utilization, and export per-stick G-code programs.',
        "steps_count": 6,
        "steps_label": "6 Steps",
        "meta_pills": [
            {"style": "cyan", "html": "<strong>Fixture Used:</strong> Headache Rack [COMPLEX] (37 Parts)"},
            {"style": "", "html": '<strong>Output:</strong> Multi-Stick 1D Bin Packing (<code class="mono">pack_stick_1.nc</code>, <code class="mono">pack_stick_2.nc</code>)'},
        ],
        "toc": [
            {"id": "step-1", "badge": "01", "label": "Load 37-Part Headache Rack Fixture"},
            {"id": "step-2", "badge": "02", "label": "Open Multi-Part Pack Nesting Tab"},
            {"id": "step-3", "badge": "03", "label": "Open the Cutting Profile Selector"},
            {"id": "step-4", "badge": "04", "label": "Select 25.4×25.4 mm HSS Profile (17 Parts)"},
            {"id": "step-5", "badge": "05", "label": "Review Multi-Stick Layout &amp; Compile G-Code"},
            {"id": "step-6", "badge": "06", "label": "Simulate &amp; Download Per-Stick .nc Files"},
        ],
        "pagination_title": "Multi-Part Stick Nesting",
        "pagination_desc": "Load a 37-part assembly, filter by cross-section & pack across multiple sticks",
        "hub_thumb": "assets/nesting-5-compile.png",
        "hub_thumb_alt": "RotaryCAM Multi-Part Pack Nesting Across Multiple Sticks",
        "hub_title": "Multi-Part Stick Nesting",
        "hub_desc": "Load a complex 37-part Headache Rack assembly, filter parts by detected cross-section profile, interlock miters &amp; copes with 180° flips + A-axis rolls and optional common-line sever cuts across two 6000 mm sticks at 99.8% efficiency, and export per-stick G-code.",
        "hub_topics": [
            "Automatic cross-section profile detection &amp; filtering",
            "Interlocking miter &amp; cope nesting (180° flip + A-axis roll)",
            "Optional single-cut common-line severing (50% fewer cutoff pierces)",
            "Per-stick `.nc` download &amp; 3D multi-stick simulation",
        ],
        "hub_cta_right": "6 Annotated Screenshots",
        "has_lightbox": True,
    },
    {
        "num": 4,
        "slug": "bending",
        "filename": "bending.html",
        "nav_short": "Bending",
        "sidebar_label": "Bending HSS & HSS-O",
        "footer_label": "Bending HSS & HSS-O",
        "breadcrumb_title": "Bending HSS & HSS-O Sticks",
        "meta_title": "04. Bending HSS & HSS-O Sticks — RotaryCAM Documentation",
        "meta_description": "Step-by-step guide to RotaryCAM's Cut-and-Bend unfolding workflow for square/rectangular HSS and round HSS-O sticks: load a bent tube STEP file, expand relief kerf cuts, customize cut counts and living-hinge spine width (Edge Left), preview the unfolded straight stick in 3D, and export G-code.",
        "hero_title_html": 'Bending <span class="text-gradient-amber">HSS &amp; HSS-O Sticks</span>',
        "hero_subtitle_html": 'How to load a 3D bent tube STEP model, automatically unfold its centerline into a straight stick with kerf-bending relief cuts, customize the number of relief cuts (<code class="mono">3 → 5</code>) and the uncut spine bridge width (<code class="mono">Edge Left: 30 mm</code>), preview the unfolded straight stick in 3D simulation, and download shop-ready G-code.',
        "steps_count": 5,
        "steps_label": "5 Steps",
        "meta_pills": [
            {"style": "cyan", "html": "<strong>Fixture Used:</strong> HSS Bending [CUT &amp; BEND] (3 Bends)"},
            {"style": "", "html": "<strong>Profiles Supported:</strong> Square/Rectangular HSS &amp; Round Tube (HSS-O)"},
        ],
        "toc": [
            {"id": "step-1", "badge": "01", "label": "Select HSS Bending Fixture"},
            {"id": "step-2", "badge": "02", "label": "Select Bend #1 &amp; Click 'Cuts (3)'"},
            {"id": "step-3", "badge": "03", "label": "Inspect Expanded Relief Cuts"},
            {"id": "step-4", "badge": "04", "label": "Set Cuts to 5 &amp; Edge Left to 30 mm"},
            {"id": "step-5", "badge": "05", "label": "Preview Cut Simulation &amp; Download"},
        ],
        "pagination_title": "Bending HSS & HSS-O Sticks",
        "pagination_desc": "Unfold 3D bent tubes into straight-stick kerf relief cut patterns",
        "hub_thumb": "assets/bending-4-configure-bend.png",
        "hub_thumb_alt": "RotaryCAM HSS & HSS-O Cut-and-Bend Unfolding",
        "hub_title": "Bending HSS &amp; HSS-O Sticks",
        "hub_desc": "Load a 3D bent tube STEP fixture, automatically unfold its 3 bends into a straight stick with kerf-bending relief slots, customize cut counts (`3 → 5`) and spine bridge width (`Edge Left: 30 mm`), preview in 3D, and download G-code.",
        "hub_topics": [
            "Automatic 3D bent-tube spine detection &amp; unfolding",
            "Collapsible per-bend relief cut inspection (`▸ Cuts (3)`)",
            "Custom relief cut count (`5`) &amp; living-hinge spine (`Edge Left: 30 mm`)",
            "3D straight-stick Cut Preview &amp; one-click `.nc` export",
        ],
        "hub_cta_right": "5 Annotated Screenshots",
        "has_lightbox": True,
    },
    {
        "num": 5,
        "slug": "changelog",
        "filename": "changelog.html",
        "nav_short": "Changelog",
        "sidebar_label": "Build Info & Changelog",
        "footer_label": "Build Info & Changelog",
        "breadcrumb_title": "Build Information & Changelog",
        "meta_title": "05. Build Information & Changelog — RotaryCAM Documentation",
        "meta_description": "How to access RotaryCAM's built-in About modal, verify your version and Git commit hash, locate saved machine profiles and cut charts across macOS, Windows, and Linux, review release notes, and copy diagnostics.",
        "hero_title_html": 'Build Information &amp; <span class="text-gradient-amber">Changelog</span>',
        "hero_subtitle_html": 'How to verify your running RotaryCAM version, Git commit hash, UTC build timestamp, platform architecture, and release changelog directly inside the application—and copy one-click diagnostics when reporting shop-floor feedback.',
        "steps_count": 3,
        "steps_label": "3 Steps • Diagnostics & Storage",
        "meta_pills": [
            {"style": "cyan", "html": "<strong>Location:</strong> Top-Right Header Bar (<code class=\"mono\">ⓘ About</code>)"},
            {"style": "", "html": "<strong>Includes:</strong> System File Locations (macOS / Windows / Linux) &amp; Diagnostics"},
        ],
        "toc": [
            {"id": "step-1", "badge": "01", "label": "Click 'ⓘ About' in Top-Right Header"},
            {"id": "step-2", "badge": "02", "label": "Inspect Build Metadata &amp; Changelog"},
            {"id": "storage-locations", "badge": "03", "label": "System File &amp; Data Locations"},
            {"id": "release-transcript", "badge": "LOG", "label": "Recent Release Highlights"},
        ],
        "pagination_title": "Build Information & Changelog",
        "pagination_desc": "Access version metadata, find local machine profiles & cut charts, and review release highlights",
        "hub_thumb": "assets/changelog-2-modal.png",
        "hub_thumb_alt": "RotaryCAM About Modal with Build Information & Changelog",
        "hub_title": "Build Information &amp; Changelog",
        "hub_desc": "Open the built-in `ⓘ About` modal from the top-right header bar to verify your installed version, Git commit hash, and license status, locate saved machine profiles, cut charts and offline licenses on disk (macOS, Windows, Linux), browse release highlights, and copy system diagnostics.",
        "hub_topics": [
            "Top-right `ⓘ About` quick access from any workspace tab",
            "Version, Git commit hash, platform &amp; license status table",
            "Local file locations: machine profiles, cut charts &amp; offline licenses",
            "One-click `📋 Copy Diagnostics` for support tickets",
        ],
        "hub_cta_right": "2 Annotated Screenshots",
        "has_lightbox": True,
    },
    {
        "num": 6,
        "slug": "ai-autodetection",
        "filename": "ai-autodetection.html",
        "nav_short": "AI CAD",
        "sidebar_label": "Fusion 360 & AI Autodetect",
        "footer_label": "Fusion 360 & AI Autodetect",
        "breadcrumb_title": "Fusion 360 & AI Profile Autodetection",
        "meta_title": "06. Modeling in Fusion 360 for AI Profile Autodetection — RotaryCAM Documentation",
        "meta_description": "Step-by-step guide to modeling tube and pipe assemblies in Autodesk Fusion 360 using the Structural Member (SM) plugin so RotaryCAM automatically detects tube profiles, sizes, and wall thicknesses straight out of CAD.",
        "hero_title_html": 'Fusion 360 &amp; <span class="text-gradient-amber">AI Profile Autodetection</span>',
        "hero_subtitle_html": 'How to model tube and pipe structures in <strong>Autodesk Fusion 360</strong> using the <strong>Structural Member (<code class="mono">SM</code>)</strong> plugin so that RotaryCAM automatically recognizes every tube profile, wall thickness, and bend centerline straight out of CAD.',
        "steps_count": 8,
        "steps_label": "8 Steps • 11 Screenshots",
        "meta_pills": [
            {"style": "cyan", "html": "<strong>Required CAD Stack:</strong> Autodesk Fusion 360 + Structural Member Plugin"},
            {"style": "", "html": "<strong>AI Engine:</strong> Automatic CAD Tube Recognition &amp; Sizing"},
        ],
        "toc": [
            {"id": "step-1", "badge": "01", "label": "Start New Design in Fusion 360"},
            {"id": "step-2", "badge": "02", "label": "Create a 2D Centerline Sketch"},
            {"id": "step-3", "badge": "03", "label": "Draw Centerline Path &amp; Finish Sketch"},
            {"id": "step-4", "badge": "04", "label": "Generate Tubes with Structural Member"},
            {"id": "step-5", "badge": "05", "label": "Combine Bodies (Required for Cut &amp; Bend)"},
            {"id": "step-6", "badge": "06", "label": "Export Full Assembly as STEP (.step)"},
            {"id": "step-7", "badge": "07", "label": "Drop STEP File into RotaryCAM"},
            {"id": "step-8", "badge": "08", "label": "Verify AI Profile Autodetection"},
        ],
        "pagination_title": "Fusion 360 & AI Profile Autodetection",
        "pagination_desc": "Model with Structural Member (SM) so RotaryCAM auto-detects tube profiles out of the box",
        "hub_thumb": "assets/ai-cad-8-autodetect.png",
        "hub_thumb_alt": "RotaryCAM Fusion 360 Structural Member & Automatic Tube Detection",
        "hub_title": "Fusion 360 &amp; AI Profile Autodetection",
        "hub_desc": "Design 2D centerline sketches and 3D tube assemblies in Autodesk Fusion 360 using the Structural Member (`SM`) add-in, combine contiguous bend segments, export a full-design STEP file, and watch RotaryCAM automatically identify every tube size and wall thickness.",
        "hub_topics": [
            "Why Fusion 360 + Structural Member (`SM`) is required today",
            "Drawing 2D centerline sketches &amp; applying ANSI/AISC HSS/Pipe profiles",
            "Using `Modify → Combine` (`Join`) for Cut-and-Bend support",
            "Full-assembly STEP export &amp; zero-click `AI` profile detection",
        ],
        "hub_cta_right": "11 Annotated Screenshots",
        "has_lightbox": True,
    },
    {
        "num": 7,
        "slug": "simcnc-motion-sync",
        "filename": "simcnc-motion-sync.html",
        "nav_short": "SimCNC",
        "sidebar_label": "SimCNC Motion-Sync & 3D Ramp",
        "footer_label": "SimCNC Motion-Sync & Ramp",
        "breadcrumb_title": "SimCNC Motion-Synchronized Torch & 3D Ramp Lead-Ins",
        "meta_title": "07. SimCNC Motion-Synchronized Torch On/Off & 3D Ramp Lead-Ins — RotaryCAM Documentation",
        "meta_description": "Complete technical implementation guide to achieving motion-synchronized torch ignition/extinguish (M62/M63 P1), hardware THC locking (M62/M63 P0), direct CSMIO/IP-M Arc OK polling, and 3D Ramp Lead-Ins in CSLab SimCNC for RotaryCAM.",
        "hero_title_html": 'SimCNC Motion-Synchronized <span class="text-gradient-amber">Torch On/Off &amp; 3D Ramp Lead-Ins</span>',
        "hero_subtitle_html": 'How to configure CSLab SimCNC (<code class="mono">config.xml</code>, <code class="mono">___CONF.py</code>, <code class="mono">m3.py</code>, <code class="mono">m5.py</code>) and the <strong>RotaryCAM Post-Processor</strong> for sub-millisecond <code class="mono">M62/M63</code> trajectory-synchronized torch switching, direct CSMIO/IP-M <code class="mono">Arc OK</code> polling, <strong>Zero-Overburn Early Torch-Out</strong>, and <strong>3D Ramp Lead-Ins</strong>.',
        "steps_count": 12,
        "steps_label": "12 Steps • Technical Guide",
        "meta_pills": [
            {"style": "cyan", "html": "<strong>Required For:</strong> 3D Ramp Lead-Ins &amp; Zero-Overburn Early Extinguish"},
            {"style": "", "html": "<strong>Hardware:</strong> CSLab CSMIO/IP-M + SimCNC (<code class=\"mono\">ExtTrajSyncOut0/1</code>)"},
        ],
        "toc": [
            {"id": "part-1", "badge": "PT I", "label": "Motion-Synchronized Torch On/Off"},
            {"id": "step-1", "badge": "01", "label": "Unassign Spindle &amp; Software THC"},
            {"id": "step-2", "badge": "02", "label": "Assign Outputs to ExternalTrajCtrl"},
            {"id": "step-3", "badge": "03", "label": "Create Helpers in ___CONF.py"},
            {"id": "step-4", "badge": "04", "label": "Update m3.py for Sync Ignition"},
            {"id": "step-5", "badge": "05", "label": "Update m5.py for Dual-Path Stop"},
            {"id": "step-6", "badge": "06", "label": "Emit M62/M63 in RotaryCAM Post"},
            {"id": "part-2", "badge": "PT II", "label": "3D Ramp Lead-Ins in m3.py"},
            {"id": "step-7", "badge": "07", "label": "Define #1113 &amp; #1110 Parameters"},
            {"id": "step-8", "badge": "08", "label": "Anchor Program Z to Pierce Height"},
            {"id": "step-9", "badge": "09", "label": "Read Ramp Flag &amp; Wall Thickness"},
            {"id": "step-10", "badge": "10", "label": "Two-Tier Pierce Dwell Logic"},
            {"id": "step-11", "badge": "11", "label": "Skip Stationary Plunge &amp; Reset #1113"},
            {"id": "step-12", "badge": "12", "label": "Emit 3D Ramp G-Code to Z#3"},
        ],
        "pagination_title": "SimCNC Motion-Synchronized Torch & 3D Ramp",
        "pagination_desc": "Configure ExtTrajSyncOut M62/M63, direct Arc OK & 3D ramp lead-ins in SimCNC",
        "hub_thumb": None,
        "hub_custom_thumb_html": """<div class="docs-hub-code-preview">
              <div>
                <div class="code-line-muted"># ___CONF.py + m3.py + m5.py + RotaryCAM Post</div>
                <div class="code-line-amber">ExtTrajSyncOut0 (P0) → Out 4 (Hardware THC Lock)</div>
                <div class="code-line-cyan">ExtTrajSyncOut1 (P1) → Out 0 (Torch Fire Relay)</div>
              </div>
              <div>
                <div class="code-line-emerald">#1113=1  #1110=0.25  M03  M63 P0</div>
                <div>G01 X1.2500 Y0.8000 Z#3 F120.0  (3D Ramp)</div>
                <div class="code-line-amber">M63 P0  M63 P1  G1 ... (0-Overburn Torch-Out)</div>
              </div>
            </div>""",
        "hub_title": "SimCNC Motion-Sync Torch &amp; 3D Ramp Lead-Ins",
        "hub_desc": "Configure SimCNC's `ExternalTrajCtrl` (`M62/M63 P0/P1`), direct CSMIO/IP-M `Arc OK` polling, and `___CONF.py` / `m3.py` / `m5.py` macros—required for RotaryCAM's 3D Ramp Lead-In and Zero-Overburn Early Extinguish features.",
        "hub_topics": [
            "Reassigning Torch Fire (`P1`) &amp; THC Lock (`P0`) to `ExtTrajSyncOut`",
            "Solving SimCNC's stationary `M62/M63` constraint via `<1.5 ms` Z micro-wiggle",
            "On-the-fly `M63 P1` Zero-Overburn arc extinguish without motion stalls",
            "Parameter `#1113` / `#1110` / `Z#3` handshake for 3D Ramp Lead-Ins",
        ],
        "hub_cta_right": "12-Step Technical Reference",
        "has_lightbox": False,
    },
    {
        "num": 8,
        "slug": "cut-charts-and-features",
        "filename": "cut-charts-and-features.html",
        "nav_short": "Cut Charts",
        "sidebar_label": "Cut Charts & Feature Toggles",
        "footer_label": "Cut Charts & Feature Toggles",
        "breadcrumb_title": "Plasma Cut Charts & Feature Toggling",
        "meta_title": "08. Plasma Cut Charts, Torch Settings & Feature Toggling — RotaryCAM Documentation",
        "meta_description": "Complete guide to RotaryCAM's built-in Hypertherm plasma cut charts, automatic wall-thickness matching, custom cut chart editing, and selective feature omission in 3D tube inspection.",
        "hero_title_html": 'Plasma Cut Charts, Torch Settings &amp; <span class="text-gradient-amber">Feature Toggling</span>',
        "hero_subtitle_html": 'How to utilize RotaryCAM&rsquo;s built-in Hypertherm plasma cut charts (Powermax 45XP/65/85/Sync), match cut parameters automatically to detected STEP wall thickness, create and edit custom shop presets, and selectively toggle holes, slots, or cutouts without touching CAD.',
        "steps_count": 6,
        "steps_label": "6 Steps • Visual Guide",
        "meta_pills": [
            {"style": "cyan", "html": "<strong>Cut Charts:</strong> 145 Factory Hypertherm Presets + Custom Shop Gauges"},
            {"style": "", "html": "<strong>Interactive CAD:</strong> Omit Holes &amp; Slots Without CAD Redraw"},
        ],
        "toc": [
            {"id": "step-1", "badge": "01", "label": "Open Cut Charts Manager"},
            {"id": "step-2", "badge": "02", "label": "Browse &amp; Filter Factory Presets"},
            {"id": "step-3", "badge": "03", "label": "Edit Parameters &amp; Add Custom Presets"},
            {"id": "step-4", "badge": "04", "label": "Inspect Automatic Wall-Thickness Matching"},
            {"id": "step-5", "badge": "05", "label": "Toggle Contours in Single Part Inspection"},
            {"id": "step-6", "badge": "06", "label": "Verify Omitted Toolpaths &amp; Live G-Code"},
        ],
        "pagination_title": "Plasma Cut Charts & Feature Toggles",
        "pagination_desc": "Hypertherm cut presets, wall-thickness auto-matching & selective hole omission",
        "hub_thumb": "assets/cut-charts-2-modal.png",
        "hub_thumb_alt": "RotaryCAM Hypertherm Cut Charts Manager and Parameter Editor",
        "hub_title": "Plasma Cut Charts &amp; Feature Toggles",
        "hub_desc": "Browse 145 factory Hypertherm Powermax cut charts, match feedrates and voltages automatically to your tube's wall thickness, tweak cut parameters on the fly, and omit secondary holes or slots with a single click.",
        "hub_topics": [
            "145 built-in Hypertherm presets (Mild Steel, Stainless, Aluminum)",
            "Automatic STEP wall-thickness matching with manual override",
            "Editing kerf, feedrates, arc voltage, pierce height &amp; cut air",
            "Selective feature toggling (holes/slots/notches) with live G-code updates",
        ],
        "hub_cta_right": "6 Annotated Screenshots",
        "has_lightbox": True,
    },
    {
        "num": 9,
        "slug": "mcp-offline-workflows",
        "filename": "mcp-offline-workflows.html",
        "nav_short": "MCP & AI",
        "sidebar_label": "Offline MCP & AI Automation",
        "footer_label": "Offline MCP & AI Automation",
        "breadcrumb_title": "Offline Model Context Protocol (MCP) & AI Automation",
        "meta_title": "09. Offline Model Context Protocol (MCP) & AI Automation — RotaryCAM Documentation",
        "meta_description": "Step-by-step guide to RotaryCAM's 100% offline Model Context Protocol (MCP) server: connect Claude Desktop, Cursor, or LM Studio, run first-principles drive math, analyze STEP CAD files, apply zero-bevel copes, and emit production G-code air-gapped.",
        "hero_title_html": 'Offline Model Context Protocol (MCP) &amp; <span class="text-gradient-amber">AI Automation</span>',
        "hero_subtitle_html": 'How to connect local AI coding assistants (Claude Desktop, Cursor, LM Studio) to RotaryCAM&rsquo;s 100% offline MCP stdio server (<code class="mono">rotarycam-mcp</code>), calculate drive kinematics with first-principles physics, inspect STEP CAD solids, apply dual-curve zero-bevel compensation, and emit shop-ready G-code without sending a single byte to the cloud.',
        "steps_count": 8,
        "steps_label": "8 Steps • Integration Guide",
        "meta_pills": [
            {"style": "cyan", "html": "<strong>100% Air-Gapped:</strong> Standard JSON-RPC 2.0 over Stdio"},
            {"style": "", "html": "<strong>Supported Clients:</strong> Claude Desktop, Cursor, VS Code, LM Studio"},
        ],
        "toc": [
            {"id": "step-1", "badge": "01", "label": "Locate Binary &amp; Activate License"},
            {"id": "step-2", "badge": "02", "label": "Configure Claude Desktop"},
            {"id": "step-3", "badge": "03", "label": "Configure Cursor &amp; VS Code"},
            {"id": "step-4", "badge": "04", "label": "Air-Gapped Setup with Open LLMs"},
            {"id": "step-5", "badge": "05", "label": "First-Principles Drive Math"},
            {"id": "step-6", "badge": "06", "label": "Headless STEP CAD Analysis"},
            {"id": "step-7", "badge": "07", "label": "Dual-Curve Zero-Bevel Compensation"},
            {"id": "step-8", "badge": "08", "label": "Generate G-Code &amp; 3D Visual Handoff"},
        ],
        "pagination_title": "Offline MCP & AI Automation",
        "pagination_desc": "Connect local AI assistants, run drive math, analyze CAD & emit production G-code",
        "hub_thumb": None,
        "hub_custom_thumb_html": """<div class="docs-hub-code-preview">
              <div>
                <div class="code-line-muted"># rotarycam-mcp stdio (JSON-RPC 2.0)</div>
                <div class="code-line-amber">Claude Desktop / Cursor / LM Studio</div>
                <div class="code-line-cyan">→ analyze_step(path="rollcage.step")</div>
              </div>
              <div>
                <div class="code-line-emerald">→ apply_zero_bevel(intensity=60.0)</div>
                <div>→ generate_gcode(mode="auto")</div>
                <div class="code-line-amber">→ open_in_rotarycam() → WebGL 3D</div>
              </div>
            </div>""",
        "hub_title": "Offline MCP &amp; AI Automation",
        "hub_desc": "Connect Claude Desktop, Cursor, or LM Studio to RotaryCAM's 100% offline `rotarycam-mcp` stdio server. Calculate drive kinematics from pitch and gear ratios, inspect STEP files, apply zero-bevel copes, and generate G-code air-gapped.",
        "hub_topics": [
            "100% offline stdio server for macOS, Linux, and Windows",
            "First-principles drive math (rack-and-pinion, ballscrew, rotary)",
            "STEP CAD feature extraction &amp; dual-curve zero-bevel compensation",
            "Headless G-code generation &amp; interactive 3D WebGL handoff",
        ],
        "hub_cta_right": "8-Step Technical Reference",
        "has_lightbox": False,
    },
]


def bootstrap_missing_page_templates():
    """Extract `<div class="docs-main">` body from existing docs/*.html files if .html.j2 doesn't exist yet."""
    PAGES_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    for t in TUTORIALS:
        j2_path = PAGES_TEMPLATE_DIR / f"{t['slug']}.html.j2"
        html_path = DOCS_OUT_DIR / t["filename"]
        if j2_path.exists() or not html_path.exists():
            continue
        raw = html_path.read_text(encoding="utf-8")
        # Extract everything between `<div class="docs-main">` and `<!-- Pagination -->`
        m = re.search(
            r'<div class="docs-main">\s*(.*?)\s*<!-- Pagination -->',
            raw,
            flags=re.DOTALL,
        )
        if not m:
            raise RuntimeError(f"Could not extract .docs-main body from {html_path}")
        body = m.group(1).strip()
        template_content = (
            '{% extends "tutorial_base.html.j2" %}\n\n'
            "{% block tutorial_body %}\n"
            f"        {body}\n"
            "{% endblock %}\n"
        )
        j2_path.write_text(template_content, encoding="utf-8")
        print(f"[bootstrap] Created template {j2_path.relative_to(ROOT_DIR)}")


def build_all_docs():
    bootstrap_missing_page_templates()

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader([str(TEMPLATES_DIR), str(PAGES_TEMPLATE_DIR)]),
        autoescape=False,
        keep_trailing_newline=True,
    )

    total_tutorials = len(TUTORIALS)
    total_steps = sum(t["steps_count"] for t in TUTORIALS)

    # 1. Render docs/index.html
    index_page = {
        "slug": "index",
        "meta_title": "Documentation & Workflows — RotaryCAM | 4-Axis Rotary CNC Plasma CAM",
        "meta_description": "Step-by-step visual documentation and shop tutorials for RotaryCAM: 4-axis machine setup, 3D STEP cut-path inspection, zero-bevel saddle compensation, multi-stick nesting, HSS & round pipe Cut-and-Bend unfolding, Fusion 360 modeling, and SimCNC motion-sync torch control.",
        "has_lightbox": False,
    }
    index_tmpl = env.get_template("pages/index.html.j2")
    index_html = index_tmpl.render(
        page=index_page,
        tutorials=TUTORIALS,
        total_tutorials=total_tutorials,
        total_steps=total_steps,
        css_version=CSS_VERSION,
        version=VERSION,
        beta_label=BETA_LABEL,
        footer_tech_strip=FOOTER_TECH_STRIP,
    )
    (DOCS_OUT_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"[build] Rendered docs/index.html ({total_tutorials} workflows, {total_steps} steps)")

    # 2. Render each tutorial page
    for idx, t in enumerate(TUTORIALS):
        prev_t = TUTORIALS[idx - 1] if idx > 0 else None
        next_t = TUTORIALS[idx + 1] if idx + 1 < total_tutorials else None
        tmpl = env.get_template(f"pages/{t['slug']}.html.j2")
        rendered = tmpl.render(
            page=t,
            tutorials=TUTORIALS,
            total_tutorials=total_tutorials,
            total_steps=total_steps,
            prev_tutorial=prev_t,
            next_tutorial=next_t,
            css_version=CSS_VERSION,
            version=VERSION,
            beta_label=BETA_LABEL,
            footer_tech_strip=FOOTER_TECH_STRIP,
        )
        out_path = DOCS_OUT_DIR / t["filename"]
        out_path.write_text(rendered, encoding="utf-8")
        print(f"[build] Rendered docs/{t['filename']} (Tutorial {t['num']:02d} of {total_tutorials:02d})")


def verify_links_and_assets():
    html_files = [
        ROOT_DIR / "index.html",
        ROOT_DIR / "build-guide.html",
        DOCS_OUT_DIR / "index.html",
    ] + [DOCS_OUT_DIR / t["filename"] for t in TUTORIALS]

    missing = []
    checked = 0
    for f in html_files:
        text = f.read_text(encoding="utf-8")
        for attr, val in re.findall(r'(href|src)="([^"]+)"', text):
            if val.startswith(("http://", "https://", "mailto:", "#", "javascript:", "data:")):
                continue
            clean = val.split("#")[0].split("?")[0]
            if not clean:
                continue
            target = (f.parent / clean).resolve()
            checked += 1
            if not target.exists():
                missing.append((f.relative_to(ROOT_DIR), attr, val, target))

    if missing:
        for src_file, attr, val, target in missing:
            print(f"[ERROR] Broken {attr}=\"{val}\" in {src_file} -> {target}", file=sys.stderr)
        sys.exit(1)
    print(f"[verify] Verified {checked} internal href/src references across {len(html_files)} HTML files — 0 broken links!")


if __name__ == "__main__":
    build_all_docs()
    if "--verify" in sys.argv:
        verify_links_and_assets()
