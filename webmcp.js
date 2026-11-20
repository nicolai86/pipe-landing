(function () {
  'use strict';

  const mc =
    (typeof navigator !== 'undefined' && navigator.modelContext) ||
    (typeof document !== 'undefined' && document.modelContext);

  if (!mc) {
    return;
  }

  const CONTROLLERS = [
    {
      slug: 'LinuxCNC',
      name: 'LinuxCNC 2.9+ QTPlasmaC',
      shortName: 'LinuxCNC QTPlasmaC',
      extension: '.ngc',
      rotaryMode: 'G94 (2D/HSS Flats) + G93 (Rotary)',
      url: 'https://rotarycam.app/docs/machine-configuration/LinuxCNC/',
      summary: 'Three clean regimes (2D flat, #<tube_cut>=1 rotary/3D, non-M3 scribe) with M62/M63 kerf void protection.',
      aliases: ['linuxcnc', 'qtplasmac', 'plasmac', 'emc2', 'ngc']
    },
    {
      slug: 'FireControl',
      name: 'Langmuir Systems FireControl v1.6+ / v24.1.6',
      shortName: 'Langmuir FireControl',
      extension: '.tap',
      rotaryMode: 'G94 Y-WRAP / X-WRAP (+ L_rev)',
      url: 'https://rotarycam.app/docs/machine-configuration/FireControl/',
      summary: 'Hardened .tap output for CrossFire, PRO & XR with dual G38.2/G38.4 IHS, 0.55s 3D ramp dwell & Y/X-WRAP.',
      aliases: ['firecontrol', 'langmuir', 'crossfire', 'pro', 'xr', 'tap']
    },
    {
      slug: 'Mach4',
      name: 'ArtSoft Mach4 + Warp9 ESS / TMC3in1',
      shortName: 'Mach4 + ESS / TMC3in1',
      extension: '.tap',
      rotaryMode: 'G93 Inverse-Time (strokes only)',
      url: 'https://rotarycam.app/docs/machine-configuration/Mach4/',
      summary: 'Modal G90/G91.1 separation, G31.0-G31.3 + refDistance skip-probe, Output #4 TMC3in1 THC & M62/M63 P3 torch.',
      aliases: ['mach4', 'mach 4', 'ess', 'warp9', 'tmc3in1', 'artsoft']
    },
    {
      slug: 'MASSO',
      name: 'MASSO G3 + DTHC v5.x',
      shortName: 'MASSO G3 + DTHC',
      extension: '.nc',
      rotaryMode: 'G93 Inverse-Time',
      url: 'https://rotarycam.app/docs/machine-configuration/MASSO/',
      summary: 'T112 M6 plasma mode, 3 THC modes, mandatory M667 F<zFeed> anti-dive, Bare G200 vs Hybrid C=P ramps & G28 A0 unwind.',
      aliases: ['masso', 'masso g3', 'g3', 'dthc', 't112']
    },
    {
      slug: 'Mach3',
      name: 'ArtSoft Mach3 R3.043.062',
      shortName: 'ArtSoft Mach3',
      extension: '.tap',
      rotaryMode: 'G93 Inverse-Time (Use Radius OFF)',
      url: 'https://rotarycam.app/docs/machine-configuration/Mach3/',
      summary: '4 THC hardware topologies, ESS G31 vs LPT G28.1 probing, G54-baked scribe offsets, % framing & .xml import.',
      aliases: ['mach3', 'mach 3', 'artsoft', 'g28.1']
    },
    {
      slug: 'Acorn',
      name: 'Centroid Acorn CNC12 v5.4+',
      shortName: 'Centroid Acorn CNC12',
      extension: '.nc',
      rotaryMode: 'G94 (2D) / G93.1 Smoothed (3D/4D)',
      url: 'https://rotarycam.app/docs/machine-configuration/Acorn/',
      summary: 'Dual-regime CNC12 v5.4+ post: canned M61/M62 2D plate vs. M150/M36/G93.1 3D & 4D rotary with semicolon-only comments.',
      aliases: ['acorn', 'centroid', 'cnc12', 'g93.1']
    },
    {
      slug: 'grblHAL',
      name: 'grblHAL 32-Bit Plasma + Rotary',
      shortName: 'grblHAL 32-Bit Plasma',
      extension: '.nc',
      rotaryMode: 'G94 (2D / Y-Wrap) / G93 (4-Axis)',
      url: 'https://rotarycam.app/docs/machine-configuration/grblHAL/',
      summary: 'Standalone-line $674 virtual ports (P2/P3/E3), M190 P-1 explicit Z, Core #1027 G94-before-G38.2 safety & <= 80-char blocks.',
      aliases: ['grblhal', 'grbl', 'iosender', '32-bit']
    },
    {
      slug: 'UCCNC',
      name: 'CNCdrive UCCNC v1.2115+',
      shortName: 'CNCdrive UCCNC',
      extension: '.nc',
      rotaryMode: 'G93 Inverse-Time (strokes only)',
      url: 'https://rotarycam.app/docs/machine-configuration/UCCNC/',
      summary: 'Integrated G31 / Neuron Lite / M31 modes, ArcOK-safe M205-M212 handshake, 0.200 mm check move + M206 & Checkbox 212.',
      aliases: ['uccnc', 'cncdrive', 'uc100', 'uc300eth', 'axbb', 'neuron']
    },
    {
      slug: 'FlashCut',
      name: 'FlashCut CNC Plasma',
      shortName: 'FlashCut CNC',
      extension: '.nc / .gc',
      rotaryMode: 'G93 Inverse-Time (2D/3D/4D)',
      url: 'https://rotarycam.app/docs/machine-configuration/FlashCut/',
      summary: 'Fabrication Head Cut2D (Mode 1) vs Explicit Dynamic-Z G631/G605/M50/M101/G630 (Mode 2), G04 X<sec> & Setup.xml import.',
      aliases: ['flashcut', 'flash cut', 'cut2d']
    },
    {
      slug: 'EdingCNC',
      name: 'EdingCNC Plasma',
      shortName: 'EdingCNC Plasma',
      extension: '.nc',
      rotaryMode: 'G93 Inverse-Time (0.005 mm deadband)',
      url: 'https://rotarycam.app/docs/machine-configuration/EdingCNC/',
      summary: 'CNC720/760 post with #5150 4THMILL guard, #5067 probe miss check, M22/M23 voltage, M56 Arc-OK & M20/M21 THC.',
      aliases: ['edingcnc', 'eding', 'cnc720', 'cnc760']
    },
    {
      slug: 'PlanetCNC',
      name: 'PlanetCNC TNG Plasma',
      shortName: 'PlanetCNC TNG',
      extension: '.nc',
      rotaryMode: 'G93 Inverse-Time (optional G94 lookahead)',
      url: 'https://rotarycam.app/docs/machine-configuration/PlanetCNC/',
      summary: 'G90.2 rotary absolute mode, AL Axis-Lock G91 G01 probe backoff, lookahead M54 P1 Q R1 THC & semicolon comment safety.',
      aliases: ['planetcnc', 'planet cnc', 'tng']
    },
    {
      slug: 'WinCNC',
      name: 'ShopSabre WinCNC + SideKick Rotary',
      shortName: 'ShopSabre WinCNC',
      extension: '.tap',
      rotaryMode: 'G93 Inverse-Time (A / W / B letter)',
      url: 'https://rotarycam.app/docs/machine-configuration/WinCNC/',
      summary: 'G22 mm / G20 in (never G21!), configurable A/W/B SideKick letter, L37.2 D1/D0 inline THC, L38.1 params & M61/L38 patterns.',
      aliases: ['wincnc', 'win cnc', 'shopsabre', 'sidekick']
    },
    {
      slug: 'SimCNC',
      name: 'CSLab SimCNC 3.5 & 3.6+ G93',
      shortName: 'CSLab SimCNC',
      extension: '.nc',
      rotaryMode: '3.5: 4D Spoofed G94 | 3.6+: Hardened G93',
      url: 'https://rotarycam.app/docs/machine-configuration/SimCNC/',
      summary: 'Hardware-verified SimCNC post: config.xml import, G69/G64 P0.3-0.4, 0.002 mm feathering, #1110/#1113 3D ramps & M62/M63 sync.',
      aliases: ['simcnc', 'sim cnc', 'cslab', 'csmio']
    },
    {
      slug: 'GenericG94',
      name: 'Portable RS-274 (generic_g94)',
      shortName: 'Portable RS-274',
      extension: '.nc',
      rotaryMode: 'Modal G94 (dL_xyz/dt; deg/min or rad/min)',
      url: 'https://rotarycam.app/docs/machine-configuration/GenericG94/',
      summary: 'Clean ISO 6983 G94 core with configurable G04 dwells, swing-envelope Safe Z, optional THC/IHS, and Dry-Run mode.',
      aliases: ['generic', 'genericg94', 'generic_g94', 'rs274', 'rs-274', 'iso']
    },
    {
      slug: 'Scribing',
      name: 'Coaxial EasyScribe vs. Pneumatic Air-Scribe',
      shortName: 'Scribing (EasyScribe / Air)',
      extension: 'Multi-Tool',
      rotaryMode: 'All 14 Controllers (Pro Shop)',
      url: 'https://rotarycam.app/docs/machine-configuration/Scribing/',
      summary: 'Engrave Part IDs, bend lines & weld ticks using coaxial EasyScribe (all controllers, M0 swap) or pneumatic offset air-scribe.',
      aliases: ['scribing', 'scribe', 'easyscribe', 'air-scribe', 'marking', 'engraving']
    }
  ];

  const TUTORIALS = [
    {
      num: 1,
      slug: 'machine-configuration',
      title: 'Basic Machine Configuration',
      url: 'https://rotarycam.app/docs/machine-configuration.html',
      description: 'Set up 4-axis plasma kinematics, X/Y/Z/A velocity limits, G94/G93 dialects, synchronous THC locking, and zero-bevel defaults across 14 controllers.'
    },
    {
      num: 2,
      slug: 'cut-path-configuration',
      title: 'UI Layout & STEP Cut Path Configuration',
      url: 'https://rotarycam.app/docs/cut-path-configuration.html',
      description: 'Inspect multi-body STEP assemblies, tune per-contour lead-ins and 80% zero-bevel saddle copes, add weld bevels or tabs, and preview in 3D simulation.'
    },
    {
      num: 3,
      slug: 'nesting',
      title: 'Multi-Part Stick Nesting',
      url: 'https://rotarycam.app/docs/nesting.html',
      description: 'Load multi-body STEP weldments, filter parts by tube profile, interlock miters and copes across 6000 mm sticks at 99.8% yield, and export .nc files.'
    },
    {
      num: 4,
      slug: 'bending',
      title: 'Bending HSS & HSS-O Sticks',
      url: 'https://rotarycam.app/docs/bending.html',
      description: 'Unfold 3D bent square HSS and round pipe STEP models into straight sticks with custom kerf relief cuts and spine widths, then preview and export G-code.'
    },
    {
      num: 5,
      slug: 'changelog',
      title: 'Build Information & Changelog',
      url: 'https://rotarycam.app/docs/changelog.html',
      description: 'Check your RotaryCAM version and Git commit hash, locate saved machine profiles and cut charts on macOS, Windows, and Linux, and copy diagnostics.'
    },
    {
      num: 6,
      slug: 'ai-autodetection',
      title: 'Fusion 360 & AI Profile Autodetection',
      url: 'https://rotarycam.app/docs/ai-autodetection.html',
      description: 'Model tube frames in Fusion 360 with the Structural Member plugin, combine bend bodies, export STEP assemblies, and auto-detect profiles in RotaryCAM.'
    },
    {
      num: 7,
      slug: 'simcnc-motion-sync',
      title: 'SimCNC Motion-Synchronized Torch & 3D Ramp Lead-Ins',
      url: 'https://rotarycam.app/docs/simcnc-motion-sync.html',
      description: 'Wire SimCNC M62/M63 P0/P1 trajectory-sync outputs, direct Arc OK polling, and m3.py/m5.py macros for 3D ramp lead-ins and zero-overburn torch-out.'
    },
    {
      num: 8,
      slug: 'cut-charts-and-features',
      title: 'Plasma Cut Charts & Feature Toggling',
      url: 'https://rotarycam.app/docs/cut-charts-and-features.html',
      description: 'Browse 1,025 plasma cut presets for Hypertherm SYNC, Duramax, and air plasma, import or export CSV charts, auto-match wall thickness, and omit holes.'
    },
    {
      num: 9,
      slug: 'mcp-offline-workflows',
      title: 'Offline Model Context Protocol (MCP) & AI Automation',
      url: 'https://rotarycam.app/docs/mcp-offline-workflows.html',
      description: 'Connect Claude Desktop, Cursor, or LM Studio to rotarycam-mcp over stdio for offline drive math, STEP inspection, zero-bevel copes, and G-code output.'
    },
    {
      num: 10,
      slug: 'dxf-svg-flat-sheet',
      title: 'Multi-File DXF & SVG Flat-Sheet CAM, 2-Point Scaling & Imperial G20 G-Code',
      url: 'https://rotarycam.app/docs/dxf-svg-flat-sheet.html',
      description: 'Drop multi-file DXF, SVG, or ZIP kits, set sheet thickness, fix scale with 2-point snapping, nest parts inside cutouts, and export G20 or G21 G-code.'
    },
    {
      num: 11,
      slug: 'rotary-and-sheet-feedrates',
      title: 'Understanding G94, G93 Inverse-Time & G20/G21 Feedrates',
      url: 'https://rotarycam.app/docs/rotary-and-sheet-feedrates.html',
      description: 'Learn why flat-sheet G94 F drops 25.4x in inches while rotary G93 F stays constant, plus SimCNC 4D vector scaling and G-code checks before cutting.'
    },
    {
      num: 12,
      slug: 'interactive-canvas-controls',
      title: 'Interactive Canvas Controls & Nest Tweaking',
      url: 'https://rotarycam.app/docs/interactive-canvas-controls.html',
      description: 'Drag pierce points into scrap on 3D and 2D contours, place custom micro-joint holding tabs, rotate 2D sheet parts, and flip or roll 1D stick tubes.'
    },
    {
      num: 13,
      slug: 'flat-plate-pro-cutting',
      title: 'Flat-Plate Pro Cutting Primitives & Torch Crash Protection',
      url: 'https://rotarycam.app/docs/flat-plate-pro-cutting.html',
      description: 'Prevent torch dives with Spatial Void THC Auto-Lock, offset open slits Left/Right/Center, pierce thick plate from the edge, crop remnants, and chain.'
    }
  ];

  const LICENSE_TIERS = {
    pricingUrl: 'https://rotarycam.app/#pricing',
    downloadUrl: 'https://rotarycam.app/#download',
    ownershipModel: 'Perpetual air-gapped offline desktop license (rotarycam.lic). No subscriptions, cloud logins, or internet checks.',
    tiers: [
      {
        name: 'Public Beta',
        offerName: 'Public Beta (30-Day Rolling Offline Evaluation)',
        price: 0,
        currency: 'USD',
        cadence: '30-day rolling offline eval',
        computers: 'Evaluation use (macOS, Windows, Linux)',
        updates: 'Beta updates included during evaluation',
        url: 'https://rotarycam.app/#download',
        keyFeatures: [
          'Full 3D STEP assembly inspection & multi-file 2D DXF/SVG flat-sheet cutting with 2-point snap scaling',
          'Round Pipe, Square/Rect HSS & 2D Flat Sheet G-code across 12 controller dialects (16 profiles) in native G20/G21',
          'Zero-Bevel saddle/miter compensation & 60% small-hole speed',
          '1,025 cut charts across 3 torch families + CSV import/export & ERW seam avoidance',
          'Up to 5 parts/stick & 5 bends/file (Cut-and-Bend)'
        ]
      },
      {
        name: 'Maker',
        offerName: 'Maker Perpetual Offline License (Founding Fabricator)',
        price: 199,
        regularPriceAfterV1: 249,
        currency: 'USD',
        cadence: 'One-time purchase, own forever',
        computers: 2,
        computerNote: '2 computers (Office CAD + Shop Table PC)',
        updates: '1 full year of updates included ($59/yr optional thereafter; installed version runs forever at $0)',
        url: 'https://rotarycam.app/#pricing',
        keyFeatures: [
          'Perpetual air-gapped offline license (rotarycam.lic) with 30-day clock removed forever',
          'Everything in Public Beta across all 12 controller dialects (16 profiles) in native Imperial (G20) and Metric (G21)',
          'Round Pipe, Square/Rect HSS & multi-file 2D DXF/SVG flat-sheet cutting',
          '1,025 cut charts + CSV import/export, Zero-Bevel, custom machines & up to 5 parts/stick',
          'Your shop name stamped in every G-code header'
        ]
      },
      {
        name: 'Pro Shop',
        offerName: 'Pro Shop Perpetual Offline License (Founding Fabricator)',
        price: 399,
        regularPriceAfterV1: 499,
        currency: 'USD',
        cadence: 'One-time purchase, own forever',
        computers: 3,
        computerNote: '3 computers (Office CAD + Foreman + Table PC)',
        updates: '1 full year of updates included ($99/yr optional thereafter; Maker to Pro Shop upgrade is $200)',
        url: 'https://rotarycam.app/#pricing',
        keyFeatures: [
          'Commercial perpetual offline license (rotarycam.lic) for 3 computers with everything in Maker included',
          '4-axis round-tube eccentric V-groove weld-prep beveling without a 5-axis bevel head',
          'Angle Iron, C-Channel & I-Beam 4-axis beamline cutting',
          'Recursive part-in-cutout flat-sheet nesting & 2D common-line cutting',
          'Dual coaxial (EasyScribe) & pneumatic air-scribe marking + center-point spotting',
          'Unlimited multi-stick nesting (.zip batch export + common-line sever cuts) & unlimited 3D cut-and-bend unfolding',
          'Kerf-compensated tabbing, part-ID scribing & headless offline MCP automation (rotarycam-mcp)'
        ]
      }
    ]
  };

  const HARDWARE_THC_INFO = {
    name: 'RotaryCAM Smart Z-Axis Hardware THC & Motion Interceptor (Hardware v2)',
    url: 'https://rotarycam.app/hardware-thc.html',
    notifyUrl: 'https://rotarycam.app/hardware-thc.html#notify',
    price: 199,
    currency: 'CAD',
    priceNote: '$199 CAD target price',
    availability: 'PreOrder / Interest List (https://schema.org/PreOrder)',
    shipping: {
      countries: ['CA', 'US'],
      rate: { min: 12, max: 28, currency: 'CAD' },
      handlingDays: { min: 3, max: 7 },
      transitDays: { min: 3, max: 10 }
    },
    returns: {
      applicableCountries: ['CA', 'US'],
      windowDays: 30,
      method: 'Return by mail (https://schema.org/ReturnByMail)',
      fees: 'Buyer pays return shipping (https://schema.org/ReturnFeesCustomerResponsibility)'
    },
    keySpecs: {
      controlLoop: '10,000 Hz (100 µs) fixed TIM6 hardware loop on STM32G431CBT6 (170 MHz Cortex-M4F)',
      stepDirIO: 'RS-422 differential 6-axis Step/Dir pass-through (100-200 µs latency)',
      ohmicCollisionEscape: '2.0 ms active in-cut ohmic tip-up escape (+1.0 mm lift, 150 ms feedhold)',
      antiDive: 'Macro-free XY(A) corner freeze (<80% speed) & 667 V/s kerf void hold',
      trackingModes: 'HYBRID_SAV, wire-free PURE_SAV & PRESET; full Z lifter stroke (no software clamp)',
      rotaryFeedforward: '4-axis rotary tube cam feedforward (Round, Square & Rect HSS)',
      syncBus: 'Passive Hypertherm Powermax SYNC RS-485 bus snooping',
      flightRecorder: '20 KB (1,024-frame) 10 kHz SRAM crash flight recorder'
    }
  };

  function normalize(str) {
    return String(str || '')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, ' ')
      .trim();
  }

  function compact(str) {
    return String(str || '')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '');
  }

  function levenshtein(a, b) {
    if (a === b) return 0;
    if (!a.length) return b.length;
    if (!b.length) return a.length;
    const prev = new Array(b.length + 1);
    const curr = new Array(b.length + 1);
    for (let j = 0; j <= b.length; j += 1) prev[j] = j;
    for (let i = 1; i <= a.length; i += 1) {
      curr[0] = i;
      for (let j = 1; j <= b.length; j += 1) {
        const cost = a[i - 1] === b[j - 1] ? 0 : 1;
        curr[j] = Math.min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost);
      }
      for (let j = 0; j <= b.length; j += 1) prev[j] = curr[j];
    }
    return prev[b.length];
  }

  function scoreController(query, item) {
    const qNorm = normalize(query);
    const qCompact = compact(query);
    if (!qCompact) return 0;

    const candidates = [
      item.slug,
      item.shortName,
      item.name,
      ...item.aliases
    ];

    let best = 0;
    for (const cand of candidates) {
      const cNorm = normalize(cand);
      const cCompact = compact(cand);
      if (!cCompact) continue;

      if (qCompact === cCompact || qNorm === cNorm) {
        best = Math.max(best, 100);
      } else if (cCompact.startsWith(qCompact) || qCompact.startsWith(cCompact)) {
        best = Math.max(best, 85);
      } else if (cCompact.includes(qCompact) || qCompact.includes(cCompact)) {
        best = Math.max(best, 72);
      } else {
        const qTokens = qNorm.split(' ').filter(Boolean);
        const cTokens = cNorm.split(' ').filter(Boolean);
        let tokenHits = 0;
        for (const qt of qTokens) {
          if (cTokens.some((ct) => ct === qt || ct.includes(qt) || qt.includes(ct))) {
            tokenHits += 1;
          }
        }
        if (tokenHits > 0 && qTokens.length > 0) {
          best = Math.max(best, Math.round((tokenHits / qTokens.length) * 65));
        }

        const dist = levenshtein(qCompact, cCompact);
        const maxLen = Math.max(qCompact.length, cCompact.length);
        const sim = maxLen > 0 ? 1 - dist / maxLen : 0;
        if (sim >= 0.55) {
          best = Math.max(best, Math.round(sim * 60));
        }
      }
    }

    const summaryNorm = normalize(item.summary);
    const qTokens = qNorm.split(' ').filter((t) => t.length >= 2);
    for (const qt of qTokens) {
      if (summaryNorm.includes(qt)) {
        best += 4;
      }
    }
    return best;
  }

  function findControllerProfile(args) {
    const query = args && typeof args.controller === 'string' ? args.controller.trim() : '';
    if (!query) {
      throw new Error('Missing required "controller" string parameter.');
    }

    const ranked = CONTROLLERS.map((c) => ({
      item: c,
      score: scoreController(query, c)
    })).sort((a, b) => b.score - a.score);

    const top = ranked[0];
    if (!top || top.score < 20) {
      return {
        query,
        matched: false,
        message: 'No close controller profile match found. Returning available controller docs.',
        availableControllers: CONTROLLERS.map((c) => ({
          slug: c.slug,
          name: c.name,
          url: c.url
        }))
      };
    }

    return {
      query,
      matched: true,
      name: top.item.name,
      shortName: top.item.shortName,
      slug: top.item.slug,
      extension: top.item.extension,
      rotaryMode: top.item.rotaryMode,
      url: top.item.url,
      summary: top.item.summary,
      alternatives: ranked
        .slice(1, 4)
        .filter((r) => r.score >= 20)
        .map((r) => ({
          slug: r.item.slug,
          name: r.item.name,
          url: r.item.url
        }))
    };
  }

  function searchDocs(args) {
    const query = args && typeof args.query === 'string' ? args.query.trim() : '';
    if (!query) {
      throw new Error('Missing required "query" string parameter.');
    }

    const qNorm = normalize(query);
    const tokens = qNorm.split(' ').filter(Boolean);

    const ranked = TUTORIALS.map((doc) => {
      const titleNorm = normalize(doc.title);
      const slugNorm = normalize(doc.slug);
      const descNorm = normalize(doc.description);
      let score = 0;

      if (titleNorm.includes(qNorm) || slugNorm.includes(qNorm)) {
        score += 50;
      }
      if (descNorm.includes(qNorm)) {
        score += 25;
      }

      for (const t of tokens) {
        if (titleNorm.includes(t)) score += 15;
        if (slugNorm.includes(t)) score += 12;
        if (descNorm.includes(t)) score += 6;
      }

      return { doc, score };
    })
      .filter((entry) => entry.score > 0)
      .sort((a, b) => b.score - a.score || a.doc.num - b.doc.num)
      .slice(0, 5);

    return {
      query,
      totalMatches: ranked.length,
      docsHubUrl: 'https://rotarycam.app/docs/',
      results: ranked.map((entry) => ({
        num: entry.doc.num,
        title: entry.doc.title,
        url: entry.doc.url,
        description: entry.doc.description
      }))
    };
  }

  function wrapExecute(name, fn) {
    return async function (args) {
      try {
        const result = await fn(args || {});
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result)
            }
          ]
        };
      } catch (err) {
        console.error('[WebMCP] Tool execution failed (' + name + '):', err);
        const msg = err && err.message ? err.message : String(err);
        return {
          content: [
            {
              type: 'text',
              text: 'Error: ' + msg
            }
          ],
          isError: true
        };
      }
    };
  }

  const tools = [
    {
      name: 'rotarycam_find_controller_profile',
      description: 'Find the matching RotaryCAM CNC controller documentation page, URL, G-code extension, rotary mode, and setup summary by controller name (e.g. "MASSO G3", "mach 4", "linuxcnc", "acorn").',
      inputSchema: {
        type: 'object',
        properties: {
          controller: {
            type: 'string',
            description: 'Controller name or dialect to look up (e.g. "MASSO G3", "mach 4", "linuxcnc", "acorn").'
          }
        },
        required: ['controller']
      },
      annotations: { readOnlyHint: true },
      execute: wrapExecute('rotarycam_find_controller_profile', findControllerProfile)
    },
    {
      name: 'rotarycam_search_docs',
      description: 'Search RotaryCAM shop guides and documentation tutorials by keyword and return the top 5 matching pages with URLs and descriptions.',
      inputSchema: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Search keywords (e.g. "zero-bevel", "nesting", "G93", "simcnc", "dxf", "bending").'
          }
        },
        required: ['query']
      },
      annotations: { readOnlyHint: true },
      execute: wrapExecute('rotarycam_search_docs', searchDocs)
    },
    {
      name: 'rotarycam_compare_licenses',
      description: 'Compare RotaryCAM license tiers (Public Beta, Maker $199, Pro Shop $399) including pricing, computer limits, update terms, and key feature differences.',
      inputSchema: {
        type: 'object',
        properties: {}
      },
      annotations: { readOnlyHint: true },
      execute: wrapExecute('rotarycam_compare_licenses', function () {
        return LICENSE_TIERS;
      })
    },
    {
      name: 'rotarycam_get_hardware_thc_info',
      description: 'Get specs, target price ($199 CAD), pre-order availability, shipping details (CA & US), and 30-day return policy for the RotaryCAM Smart Z-Axis Hardware THC v2.',
      inputSchema: {
        type: 'object',
        properties: {}
      },
      annotations: { readOnlyHint: true },
      execute: wrapExecute('rotarycam_get_hardware_thc_info', function () {
        return HARDWARE_THC_INFO;
      })
    }
  ];

  try {
    if (typeof mc.registerTool === 'function') {
      for (const tool of tools) {
        mc.registerTool(tool);
      }
    } else if (typeof mc.provideContext === 'function') {
      mc.provideContext({ tools });
    }
  } catch (err) {
    console.error('[WebMCP] Failed to register tools:', err);
  }
})();
