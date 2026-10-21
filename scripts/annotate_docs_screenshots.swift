#!/usr/bin/env swift
// ============================================================================
// Pipe CAM / RotaryCAM Documentation Screenshot Processor
// ============================================================================
// Standardizes cropping (removing macOS/Chrome browser frame), scaling to
// 2324x1397, and drawing glowing Amber (#f59e0b) & Cyan (#06b6d4) highlight
// boxes with numbered callout pills.
//
// USAGE:
//   1. Generate a coordinate grid on a new raw screenshot to read (x, y, w, h):
//      swift scripts/annotate_docs_screenshots.swift --grid "/path/to/raw.png" "/tmp/grid.png" [x,y,w,h]
//
//   2. Render all documentation screenshots (or filter by output filename substring):
//      swift scripts/annotate_docs_screenshots.swift [filter]
// ============================================================================

import AppKit
import Foundation

enum HighlightStyle {
    case amber
    case cyan

    var strokeColor: NSColor {
        switch self {
        case .amber: return NSColor(calibratedRed: 0.96, green: 0.62, blue: 0.04, alpha: 1.0) // #f59e0b
        case .cyan:  return NSColor(calibratedRed: 0.02, green: 0.71, blue: 0.83, alpha: 1.0) // #06b6d4
        }
    }

    var fillColor: NSColor {
        switch self {
        case .amber: return NSColor(calibratedRed: 0.96, green: 0.62, blue: 0.04, alpha: 0.09)
        case .cyan:  return NSColor(calibratedRed: 0.02, green: 0.71, blue: 0.83, alpha: 0.08)
        }
    }
}

enum LabelPosition {
    case topLeft
    case topRight
    case bottomLeft
    case bottomRight
    case rightCenter
    case leftCenter
}

struct HighlightBox {
    /// Bounding box in top-down coordinates of the cropped source image (e.g. 3470x2094)
    let rect: CGRect
    let style: HighlightStyle
    let label: String?
    let labelPos: LabelPosition

    init(
        x: CGFloat,
        y: CGFloat,
        w: CGFloat,
        h: CGFloat,
        style: HighlightStyle = .amber,
        label: String? = nil,
        labelPos: LabelPosition = .topLeft
    ) {
        self.rect = CGRect(x: x, y: y, width: w, height: h)
        self.style = style
        self.label = label
        self.labelPos = labelPos
    }
}

struct ImageSpec {
    let inputPath: String
    let outputName: String
    let cropRect: CGRect
    let highlights: [HighlightBox]
}

// Standard crop rectangles for 3824x2484 macOS Chrome window captures:
// Removes macOS window shadow, title bar, tab bar, and URL bar so only the
// dark Pipe CAM web app viewport remains.
let defaultCrop = CGRect(x: 224, y: 238, width: 3470, height: 2094)
let legacyCrop  = CGRect(x: 224, y: 238, width: 3486, height: 2096)

// Standard crop rectangles for Autodesk Fusion 360 window captures:
// Strips macOS traffic-light title bar and outer window shadow so only the
// Fusion 360 application bar, DESIGN ribbon, browser tree, viewport, and timeline remain.
let fusionWindowCrop = CGRect(x: 114, y: 140, width: 3596, height: 2194)
let fusionMenuCrop   = CGRect(x: 0,   y: 54,  width: 3584, height: 2194)
let fusionExportCrop = CGRect(x: 2,   y: 60,  width: 3596, height: 2194)

// Standard output dimensions (2/3 downscale of Retina capture, 16:9.6 aspect)
let outWidth = 2324
let outHeight = 1397

func renderGrid(inputPath: String, outputPath: String, cropRect: CGRect) {
    guard let nsImage = NSImage(contentsOfFile: inputPath),
          let cgImage = nsImage.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        fputs("ERROR: Could not load \(inputPath)\n", stderr)
        exit(1)
    }
    print("Raw image size: \(cgImage.width)x\(cgImage.height), cropping to \(cropRect)")
    guard let cropped = cgImage.cropping(to: cropRect) else {
        fputs("ERROR: Crop rect \(cropRect) out of bounds for \(cgImage.width)x\(cgImage.height)\n", stderr)
        exit(1)
    }

    let scaleX = CGFloat(outWidth) / cropRect.width
    let scaleY = CGFloat(outHeight) / cropRect.height

    let rep = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: outWidth,
        pixelsHigh: outHeight,
        bitsPerSample: 8,
        samplesPerPixel: 4,
        hasAlpha: true,
        isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0
    )!

    NSGraphicsContext.saveGraphicsState()
    let nsCtx = NSGraphicsContext(bitmapImageRep: rep)!
    nsCtx.imageInterpolation = .high
    NSGraphicsContext.current = nsCtx
    let ctx = nsCtx.cgContext

    ctx.draw(cropped, in: CGRect(x: 0, y: 0, width: outWidth, height: outHeight))

    let font = NSFont.monospacedSystemFont(ofSize: 12, weight: .bold)
    let labelAttrs: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: NSColor.yellow,
        .backgroundColor: NSColor.black.withAlphaComponent(0.75)
    ]

    // Vertical X grid lines every 100px in cropped source space
    for x in stride(from: 0, through: Int(cropRect.width), by: 100) {
        let sx = CGFloat(x) * scaleX
        let path = NSBezierPath()
        path.move(to: NSPoint(x: sx, y: 0))
        path.line(to: NSPoint(x: sx, y: CGFloat(outHeight)))
        if x % 200 == 0 {
            NSColor.yellow.withAlphaComponent(0.45).setStroke()
            path.lineWidth = 1.0
        } else {
            NSColor.yellow.withAlphaComponent(0.18).setStroke()
            path.lineWidth = 0.5
        }
        path.stroke()

        if x % 200 == 0 {
            let str = NSAttributedString(string: "x\(x)", attributes: labelAttrs)
            str.draw(at: NSPoint(x: sx + 2, y: CGFloat(outHeight) - 18))
            str.draw(at: NSPoint(x: sx + 2, y: CGFloat(outHeight) / 2))
        }
    }

    // Horizontal Y grid lines every 100px in top-down cropped source space
    for y in stride(from: 0, through: Int(cropRect.height), by: 100) {
        let sy = CGFloat(outHeight) - (CGFloat(y) * scaleY)
        let path = NSBezierPath()
        path.move(to: NSPoint(x: 0, y: sy))
        path.line(to: NSPoint(x: CGFloat(outWidth), y: sy))
        if y % 200 == 0 {
            NSColor.cyan.withAlphaComponent(0.45).setStroke()
            path.lineWidth = 1.0
        } else {
            NSColor.cyan.withAlphaComponent(0.18).setStroke()
            path.lineWidth = 0.5
        }
        path.stroke()

        if y % 100 == 0 {
            let str = NSAttributedString(string: "y\(y)", attributes: labelAttrs)
            // Draw centered vertically on the horizontal grid line sy
            str.draw(at: NSPoint(x: 6, y: sy - 7))
            str.draw(at: NSPoint(x: CGFloat(outWidth) * 0.36, y: sy - 7))
            str.draw(at: NSPoint(x: CGFloat(outWidth) * 0.72, y: sy - 7))
        }
    }

    NSGraphicsContext.restoreGraphicsState()
    let pngData = rep.representation(using: .png, properties: [:])!
    try! pngData.write(to: URL(fileURLWithPath: outputPath))
    print("Wrote coordinate grid to \(outputPath)")
}

func renderImage(_ spec: ImageSpec, outDir: String) {
    guard FileManager.default.fileExists(atPath: spec.inputPath) else {
        print("SKIP (source screenshot not present on disk): \(spec.outputName) <- \(spec.inputPath)")
        return
    }
    guard let nsImage = NSImage(contentsOfFile: spec.inputPath),
          let cgImage = nsImage.cgImage(forProposedRect: nil, context: nil, hints: nil),
          let cropped = cgImage.cropping(to: spec.cropRect) else {
        fputs("ERROR loading or cropping \(spec.inputPath)\n", stderr)
        return
    }

    let scaleX = CGFloat(outWidth) / spec.cropRect.width
    let scaleY = CGFloat(outHeight) / spec.cropRect.height

    let rep = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: outWidth,
        pixelsHigh: outHeight,
        bitsPerSample: 8,
        samplesPerPixel: 4,
        hasAlpha: true,
        isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0
    )!

    NSGraphicsContext.saveGraphicsState()
    let nsCtx = NSGraphicsContext(bitmapImageRep: rep)!
    nsCtx.imageInterpolation = .high
    NSGraphicsContext.current = nsCtx
    let ctx = nsCtx.cgContext

    // 1. Draw cropped web app screenshot scaled to output resolution (2324x1397)
    ctx.draw(cropped, in: CGRect(x: 0, y: 0, width: outWidth, height: outHeight))

    // 2. Draw glowing highlight boxes & numbered callout pills
    for hl in spec.highlights {
        let sx = hl.rect.origin.x * scaleX
        let sw = hl.rect.size.width * scaleX
        let sh = hl.rect.size.height * scaleY
        let sy = CGFloat(outHeight) - (hl.rect.origin.y * scaleY) - sh
        let boxRect = CGRect(x: sx, y: sy, width: sw, height: sh)

        // Outer glow + translucent tint fill
        ctx.saveGState()
        let shadow = NSShadow()
        shadow.shadowColor = hl.style.strokeColor.withAlphaComponent(0.75)
        shadow.shadowBlurRadius = 16.0
        shadow.shadowOffset = .zero
        shadow.set()

        let path = NSBezierPath(roundedRect: boxRect, xRadius: 8, yRadius: 8)
        hl.style.fillColor.setFill()
        path.fill()

        hl.style.strokeColor.setStroke()
        path.lineWidth = 3.5
        path.stroke()
        ctx.restoreGState()

        // Crisp inner stroke
        let innerPath = NSBezierPath(roundedRect: boxRect, xRadius: 8, yRadius: 8)
        hl.style.strokeColor.setStroke()
        innerPath.lineWidth = 3.0
        innerPath.stroke()

        // Callout pill badge
        if let text = hl.label {
            let font = NSFont.systemFont(ofSize: 17, weight: .bold)
            let textAttrs: [NSAttributedString.Key: Any] = [
                .font: font,
                .foregroundColor: NSColor.white
            ]
            let attrStr = NSAttributedString(string: text, attributes: textAttrs)
            let textSize = attrStr.size()
            let padX: CGFloat = 14
            let padY: CGFloat = 7
            let pillW = textSize.width + padX * 2
            let pillH = textSize.height + padY * 2

            var pillX = boxRect.minX
            var pillY = boxRect.maxY + 8

            switch hl.labelPos {
            case .topLeft:
                pillX = boxRect.minX
                pillY = boxRect.maxY + 8
            case .topRight:
                pillX = boxRect.maxX - pillW
                pillY = boxRect.maxY + 8
            case .bottomLeft:
                pillX = boxRect.minX
                pillY = boxRect.minY - pillH - 8
            case .bottomRight:
                pillX = boxRect.maxX - pillW
                pillY = boxRect.minY - pillH - 8
            case .rightCenter:
                pillX = boxRect.maxX + 10
                pillY = boxRect.midY - pillH / 2
            case .leftCenter:
                pillX = boxRect.minX - pillW - 10
                pillY = boxRect.midY - pillH / 2
            }

            // Clamp to viewport bounds
            pillX = max(8, min(CGFloat(outWidth) - pillW - 8, pillX))
            pillY = max(8, min(CGFloat(outHeight) - pillH - 8, pillY))

            let pillRect = CGRect(x: pillX, y: pillY, width: pillW, height: pillH)

            ctx.saveGState()
            let pillShadow = NSShadow()
            pillShadow.shadowColor = NSColor.black.withAlphaComponent(0.7)
            pillShadow.shadowBlurRadius = 10
            pillShadow.shadowOffset = NSSize(width: 0, height: -2)
            pillShadow.set()

            let pillPath = NSBezierPath(roundedRect: pillRect, xRadius: 6, yRadius: 6)
            NSColor(calibratedRed: 0.06, green: 0.08, blue: 0.11, alpha: 0.95).setFill()
            pillPath.fill()
            ctx.restoreGState()

            let pillBorder = NSBezierPath(roundedRect: pillRect, xRadius: 6, yRadius: 6)
            hl.style.strokeColor.setStroke()
            pillBorder.lineWidth = 2.2
            pillBorder.stroke()

            attrStr.draw(at: CGPoint(x: pillX + padX, y: pillY + padY))
        }
    }

    NSGraphicsContext.restoreGraphicsState()

    let outURL = URL(fileURLWithPath: "\(outDir)/\(spec.outputName)")
    let pngData = rep.representation(using: .png, properties: [:])!
    try! pngData.write(to: outURL)
    print("Wrote \(spec.outputName)")
}

// ============================================================================
// ALL TUTORIAL SCREENSHOT SPECIFICATIONS
// ============================================================================
let specs: [ImageSpec] = [
    // TUTORIAL 01: Basic Machine Configuration
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 19.46.38.png",
        outputName: "machine-config-1-open.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 16, y: 1308, w: 468, h: 256, style: .cyan, label: "CNC Plasma Kinematics Summary", labelPos: .topLeft),
            HighlightBox(x: 374, y: 1324, w: 98, h: 42, style: .amber, label: "1. Click ⚙ Config", labelPos: .rightCenter),
            HighlightBox(x: 2376, y: 6, w: 128, h: 42, style: .cyan, label: "Or Click ⚙ Machines", labelPos: .bottomLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 19.47.10.png",
        outputName: "machine-config-2-limits.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 1418, y: 678, w: 1130, h: 925, style: .amber, label: "1. Configure Accurate Velocity, Acceleration, Jerk & Safe Z Limits", labelPos: .topLeft),
            HighlightBox(x: 924, y: 550, w: 472, h: 1054, style: .cyan, label: "2. Create (+ New) or Clone Profiles — Saved Across Restarts", labelPos: .bottomLeft),
            HighlightBox(x: 2382, y: 598, w: 162, h: 44, style: .amber, label: "3. Save Profile", labelPos: .topRight)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 19.47.35.png",
        outputName: "machine-config-3-dialect.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 1692, y: 678, w: 266, h: 66, style: .cyan, label: "1. Controller & Compensation Tab", labelPos: .topLeft),
            HighlightBox(x: 1418, y: 765, w: 1130, h: 235, style: .amber, label: "2. Select G-Code Dialect — Use Pure G93 ONLY if Natively Supported", labelPos: .topRight),
            HighlightBox(x: 1418, y: 1015, w: 1130, h: 295, style: .cyan, label: "3. Post-Processor Compensation Strategy", labelPos: .bottomLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 19.47.39.png",
        outputName: "machine-config-4-thc.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 1962, y: 678, w: 266, h: 66, style: .cyan, label: "1. THC & Plasma Hardware Tab", labelPos: .topLeft),
            HighlightBox(x: 1418, y: 765, w: 1130, h: 765, style: .amber, label: "2. Critical: Configure How THC Lock/Unlock Is Emitted in G-Code (M62/M63 vs M-Codes)", labelPos: .bottomLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 19.47.46.png",
        outputName: "machine-config-5-defaults.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 2232, y: 678, w: 312, h: 66, style: .cyan, label: "1. Zero-Bevel & Corner Loops Tab", labelPos: .leftCenter),
            HighlightBox(x: 1418, y: 765, w: 1130, h: 410, style: .amber, label: "2. Default Zero-Bevel Compensation & Corner Loop Parameters", labelPos: .bottomLeft),
            HighlightBox(x: 928, y: 1558, w: 464, h: 52, style: .amber, label: "3. Create (+ New), Clone, or Set Active Profile", labelPos: .bottomLeft),
            HighlightBox(x: 2382, y: 598, w: 162, h: 44, style: .cyan, label: "4. Save Profile", labelPos: .topRight)
        ]
    ),

    // TUTORIAL 02: Basic UI Layout & STEP File Cut Path Configuration
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 19.46.38.png",
        outputName: "cut-path-1-fixture.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 16, y: 905, w: 468, h: 375, style: .cyan, label: "1. Quick CAD Fixtures Panel", labelPos: .topLeft),
            HighlightBox(x: 28, y: 1000, w: 444, h: 46, style: .amber, label: "2. Click 'Saddle Joint (Zero-Bevel)'", labelPos: .rightCenter)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 19.52.50.png",
        outputName: "cut-path-2-overview.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 14, y: 140, w: 472, h: 415, style: .amber, label: "1. Entire Model Overview — Click Any Tube in the 3D Assembly", labelPos: .bottomLeft),
            HighlightBox(x: 525, y: 215, w: 2212, h: 58, style: .cyan, label: "2. Active CAD Solid Selector (Switch Parts via Dropdown or Arrows)", labelPos: .topLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_xnQeMR/Screenshot 2026-10-20 at 19.53.15.png",
        outputName: "cut-path-3-preview.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 525, y: 295, w: 2212, h: 650, style: .amber, label: "3D Part Preview & Cutting Contours (Red = Lead-In, Cyan = Cut Contour, Green = Lead-Out)", labelPos: .topLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 19.54.15.png",
        outputName: "cut-path-4-select-endcut.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 525, y: 1168, w: 2212, h: 52, style: .amber, label: "Click 'ENDCUT' Row to Highlight & Inspect This Saddle Contour", labelPos: .topLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 19.54.23.png",
        outputName: "cut-path-5-open-config.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 2536, y: 1170, w: 98, h: 44, style: .amber, label: "1. Click '⚙ Config'", labelPos: .topRight),
            HighlightBox(x: 535, y: 1220, w: 2190, h: 520, style: .cyan, label: "2. Per-Contour Lead-In, Lead-Out, Corner Loop & Zero-Bevel Drawer", labelPos: .bottomLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_UHbpJE/Screenshot 2026-10-20 at 19.54.52.png",
        outputName: "cut-path-6-zero-bevel.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 1632, y: 1220, w: 540, h: 510, style: .amber, label: "1. Check 'Apply Zero-Bevel Compensation' (80%)", labelPos: .bottomLeft),
            HighlightBox(x: 2638, y: 1170, w: 88, h: 44, style: .cyan, label: "2. Click Save", labelPos: .topRight),
            HighlightBox(x: 1456, y: 132, w: 382, h: 58, style: .amber, label: "3. Click '⚡ 3D Cut Simulation' Tab", labelPos: .bottomLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_DY6DSd/Screenshot 2026-10-20 at 19.55.13.png",
        outputName: "cut-path-7-sim-start.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 750, y: 1972, w: 140, h: 46, style: .amber, label: "1. Click '▶ Play' to Start 3D Toolpath Simulation", labelPos: .topLeft),
            HighlightBox(x: 552, y: 318, w: 274, h: 215, style: .cyan, label: "2. Live 4-Axis CNC DRO (X, Y, Z, A)", labelPos: .bottomLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_d7Pf56/Screenshot 2026-10-20 at 19.55.23.png",
        outputName: "cut-path-8-sim-done.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 880, y: 350, w: 1260, h: 1080, style: .cyan, label: "1. Completed 4-Axis Torch Path & Saddle Cut Geometry", labelPos: .topLeft),
            HighlightBox(x: 545, y: 1905, w: 2170, h: 120, style: .amber, label: "2. Simulation Played to Completion (100% — FINISHED)", labelPos: .topLeft)
        ]
    ),

    // TUTORIAL 03: Multi-Part Stick Nesting
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 19.46.38.png",
        outputName: "nesting-1-fixture.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 16, y: 905, w: 468, h: 375, style: .cyan, label: "1. Quick CAD Fixtures Panel", labelPos: .topLeft),
            HighlightBox(x: 28, y: 1162, w: 444, h: 48, style: .amber, label: "2. Click 'Headache Rack [COMPLEX]'", labelPos: .rightCenter)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_7rH0mg/Screenshot 2026-10-20 at 19.56.34.png",
        outputName: "nesting-2-open-pack.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 1005, y: 132, w: 438, h: 58, style: .amber, label: "1. Click 'Multi-Part Pack Nesting (37 PARTS)' Tab", labelPos: .bottomLeft),
            HighlightBox(x: 14, y: 580, w: 472, h: 230, style: .cyan, label: "Or Click 'Open Pack' in Left Sidebar", labelPos: .bottomLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_FRLyxV/Screenshot 2026-10-20 at 19.56.46.png",
        outputName: "nesting-3-profile-selector.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 535, y: 344, w: 750, h: 56, style: .amber, label: "Click 'CUTTING PROFILE' Selector to Choose Stock Cross-Section", labelPos: .bottomLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_9X3fxC/Screenshot 2026-10-20 at 19.57.01.png",
        outputName: "nesting-4-select-profile.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 762, y: 332, w: 476, h: 204, style: .cyan, label: "Detected Tube Profiles in Assembly", labelPos: .topLeft),
            HighlightBox(x: 766, y: 390, w: 468, h: 34, style: .amber, label: "Select 'Profile_HSS_Rect (25.4x25.4mm) (17 parts)'", labelPos: .rightCenter)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_v2vfs2/Screenshot 2026-10-20 at 19.57.11.png",
        outputName: "nesting-5-compile.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 896, y: 284, w: 254, h: 38, style: .amber, label: "1. Click '⚡ Compile Pack G-Code'", labelPos: .rightCenter),
            HighlightBox(x: 535, y: 405, w: 2205, h: 285, style: .cyan, label: "2. 17 Parts Automatically Nested Across 2 Sticks (99.8% Material Efficiency)", labelPos: .bottomLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_ANzHHZ/Screenshot 2026-10-20 at 19.57.33.png",
        outputName: "nesting-6-download.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 2780, y: 120, w: 696, h: 175, style: .amber, label: "1. Select Stick Tab & Click '⬇ Download pack_stick_1.nc'", labelPos: .bottomLeft),
            HighlightBox(x: 1052, y: 224, w: 230, h: 42, style: .cyan, label: "2. Switch Stick 1 / Stick 2 in 3D Simulation", labelPos: .bottomLeft)
        ]
    ),

    // TUTORIAL 04: Bending HSS & HSS-O Sticks
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_BYvioc/Screenshot 2026-10-20 at 21.27.14.png",
        outputName: "bending-1-fixture.png",
        cropRect: defaultCrop,
        highlights: [
            HighlightBox(x: 16, y: 896, w: 466, h: 382, style: .cyan, label: "1. Quick CAD Fixtures Panel", labelPos: .topLeft),
            HighlightBox(x: 26, y: 1218, w: 446, h: 46, style: .amber, label: "2. Select 'HSS Bending [CUT & BEND]'", labelPos: .rightCenter)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_RYO4qQ/Screenshot 2026-10-20 at 21.28.00.png",
        outputName: "bending-2-select-cuts.png",
        cropRect: defaultCrop,
        highlights: [
            HighlightBox(x: 18, y: 964, w: 462, h: 44, style: .cyan, label: "1. Bent Tube Unfolded (3 Bends Detected)", labelPos: .topLeft),
            HighlightBox(x: 524, y: 1068, w: 2216, h: 68, style: .amber, label: "2. Select Bend #1 (BEND 32.5°, R=145.0mm)", labelPos: .topLeft),
            HighlightBox(x: 2425, y: 1080, w: 100, h: 42, style: .amber, label: "3. Click '▸ Cuts (3)' Next to Config", labelPos: .bottomRight)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_LyjhpP/Screenshot 2026-10-20 at 21.28.17.png",
        outputName: "bending-3-expanded-cuts.png",
        cropRect: defaultCrop,
        highlights: [
            HighlightBox(x: 524, y: 1068, w: 2216, h: 257, style: .amber, label: "1. Expanded Kerf-Bending Relief Cuts (Cut 1/3 to 3/3)", labelPos: .bottomLeft),
            HighlightBox(x: 1525, y: 1076, w: 440, h: 48, style: .cyan, label: "2. Relief Cut Count (3) & Spine Edge Left (13.5 mm)", labelPos: .topLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_XQ1eJT/Screenshot 2026-10-20 at 21.29.02.png",
        outputName: "bending-4-configure-bend.png",
        cropRect: defaultCrop,
        highlights: [
            HighlightBox(x: 1525, y: 1076, w: 440, h: 48, style: .amber, label: "1. Change Cuts from 3 to 5 & Edge Left to 30.0 mm", labelPos: .topLeft),
            HighlightBox(x: 2580, y: 1078, w: 162, h: 44, style: .cyan, label: "2. Click Save (Saved ✓)", labelPos: .topRight),
            HighlightBox(x: 1100, y: 300, w: 900, h: 470, style: .cyan, label: "3. 5 Relief Kerf Cuts & 30mm Spine Updated in 3D", labelPos: .bottomLeft),
            HighlightBox(x: 1384, y: 132, w: 356, h: 52, style: .amber, label: "4. Click '⚡ 3D Cut Simulation' (Cut Preview)", labelPos: .bottomLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_DQi9q6/Screenshot 2026-10-20 at 21.29.51.png",
        outputName: "bending-5-simulate-download.png",
        cropRect: defaultCrop,
        highlights: [
            HighlightBox(x: 1250, y: 800, w: 720, h: 490, style: .cyan, label: "1. Unfolded Straight Stick Cut Preview with 5 Relief Kerfs", labelPos: .topLeft),
            HighlightBox(x: 3198, y: 112, w: 157, h: 42, style: .amber, label: "2. Click '⬇ Download' on the Right to Export G-Code", labelPos: .bottomRight)
        ]
    ),

    // TUTORIAL 05: Accessing Build Information & Changelog
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 19.46.38.png",
        outputName: "changelog-1-open-about.png",
        cropRect: legacyCrop,
        highlights: [
            HighlightBox(x: 2515, y: 6, w: 112, h: 42, style: .amber, label: "Click 'ⓘ About' in the Top-Right Header Bar", labelPos: .bottomLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/var/folders/_z/96ry7rgs03lc1p5cz3k1rxth0000gn/T/TemporaryItems/NSIRD_screencaptureui_sxpzvK/Screenshot 2026-10-20 at 21.31.16.png",
        outputName: "changelog-2-modal.png",
        cropRect: defaultCrop,
        highlights: [
            HighlightBox(x: 1235, y: 662, w: 998, h: 285, style: .cyan, label: "1. Build Metadata (Version, Git Commit, Date, Platform & License)", labelPos: .topLeft),
            HighlightBox(x: 1235, y: 995, w: 998, h: 505, style: .amber, label: "2. Release Notes & Recent Highlights Changelog", labelPos: .bottomLeft),
            HighlightBox(x: 1945, y: 1568, w: 215, h: 42, style: .cyan, label: "3. Copy Diagnostics", labelPos: .bottomRight)
        ]
    ),

    // TUTORIAL 06: Fusion 360 Structural Member & AI Profile Autodetection
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 22.50.21.png",
        outputName: "ai-cad-1-fusion.png",
        cropRect: fusionWindowCrop,
        highlights: [
            HighlightBox(x: 778, y: 112, w: 342, h: 74, style: .amber, label: "1. Structural Member (SM) Add-In Installed in Fusion 360", labelPos: .bottomLeft),
            HighlightBox(x: 10, y: 298, w: 454, h: 194, style: .cyan, label: "2. Create New Design (rotarycam-demo)", labelPos: .rightCenter)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 22.50.38.png",
        outputName: "ai-cad-2-sketch.png",
        cropRect: fusionWindowCrop,
        highlights: [
            HighlightBox(x: 266, y: 112, w: 72, h: 74, style: .amber, label: "1. Click Create Sketch", labelPos: .bottomLeft),
            HighlightBox(x: 1760, y: 900, w: 350, h: 380, style: .cyan, label: "2. Select Reference Origin Plane", labelPos: .topRight)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 22.51.35.png",
        outputName: "ai-cad-3-draw.png",
        cropRect: fusionWindowCrop,
        highlights: [
            HighlightBox(x: 1380, y: 495, w: 1060, h: 1365, style: .amber, label: "1. Draw 2D Tube Centerline Sketch (Lines & Tangent Arcs)", labelPos: .topLeft),
            HighlightBox(x: 3328, y: 110, w: 170, h: 92, style: .cyan, label: "2. Click Finish Sketch", labelPos: .bottomLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 22.51.53.png",
        outputName: "ai-cad-4a-sm-menu.png",
        cropRect: fusionMenuCrop,
        highlights: [
            HighlightBox(x: 245, y: 1358, w: 895, h: 377, style: .amber, label: "1. Create → Structural Member Command (Plus Miter / Notch / Trim)", labelPos: .topRight),
            HighlightBox(x: 778, y: 112, w: 342, h: 74, style: .cyan, label: "Toolbar Shortcuts: SM / Miter / Notch / Trim", labelPos: .bottomRight)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 22.52.15.png",
        outputName: "ai-cad-4b-sm-dialog.png",
        cropRect: fusionWindowCrop,
        highlights: [
            HighlightBox(x: 3092, y: 556, w: 500, h: 814, style: .amber, label: "1. Select Standard (ANSI_AISC), Family (HSS), Size & Wall", labelPos: .topLeft),
            HighlightBox(x: 1192, y: 484, w: 482, h: 1364, style: .cyan, label: "2. 3D Structural Member Generated Along Sketch Line", labelPos: .topLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 22.53.01.png",
        outputName: "ai-cad-4c-sm-complete.png",
        cropRect: fusionWindowCrop,
        highlights: [
            HighlightBox(x: 64, y: 636, w: 306, h: 334, style: .amber, label: "1. Structural Member Components (SM0001:1 – SM0007:1)", labelPos: .rightCenter),
            HighlightBox(x: 1192, y: 290, w: 1500, h: 1750, style: .cyan, label: "2. Populated 3D Tube & Pipe Assembly with Trimmed Joints", labelPos: .topLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 22.53.25.png",
        outputName: "ai-cad-5-combine.png",
        cropRect: fusionWindowCrop,
        highlights: [
            HighlightBox(x: 1480, y: 112, w: 68, h: 74, style: .amber, label: "1. Click Modify → Combine", labelPos: .bottomLeft),
            HighlightBox(x: 3092, y: 556, w: 500, h: 438, style: .amber, label: "2. Join Contiguous Straight + Bend Segments & Click OK", labelPos: .topLeft),
            HighlightBox(x: 1480, y: 598, w: 805, h: 405, style: .cyan, label: "3. Merge Into One Solid Body for Cut & Bend Support", labelPos: .bottomLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 22.54.12.png",
        outputName: "ai-cad-6-export.png",
        cropRect: fusionExportCrop,
        highlights: [
            HighlightBox(x: 136, y: 8, w: 48, h: 42, style: .cyan, label: "1. File → Export", labelPos: .bottomRight),
            HighlightBox(x: 1094, y: 658, w: 1408, h: 48, style: .amber, label: "2. Select Type: STEP Files (*.stp *.step)", labelPos: .topRight),
            HighlightBox(x: 2348, y: 1068, w: 146, h: 56, style: .amber, label: "3. Click Export", labelPos: .topLeft)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 22.54.52.png",
        outputName: "ai-cad-7a-drop.png",
        cropRect: defaultCrop,
        highlights: [
            HighlightBox(x: 14, y: 586, w: 468, h: 280, style: .amber, label: "1. Click or Drop Exported .step File into CAD Ingestion", labelPos: .rightCenter)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 22.54.59.png",
        outputName: "ai-cad-7b-load.png",
        cropRect: defaultCrop,
        highlights: [
            HighlightBox(x: 18, y: 748, w: 460, h: 112, style: .amber, label: "1. Click 'Load & Process CAD' (rotarycam-demo.step)", labelPos: .rightCenter),
            HighlightBox(x: 1420, y: 225, w: 480, h: 530, style: .cyan, label: "2. Entire Multi-Body STEP Assembly Previewed", labelPos: .rightCenter)
        ]
    ),
    ImageSpec(
        inputPath: "/Users/nicolai86/Desktop/Screenshot 2026-10-20 at 22.55.37.png",
        outputName: "ai-cad-8-autodetect.png",
        cropRect: defaultCrop,
        highlights: [
            HighlightBox(x: 14, y: 1178, w: 468, h: 262, style: .amber, label: "1. AI Cross-Section Autodetection (Profile_HSS_Rect 38.1×38.1×3.17mm)", labelPos: .rightCenter),
            HighlightBox(x: 525, y: 345, w: 710, h: 90, style: .cyan, label: "2. Both Rect & Round Profiles Autodetected & Grouped for Nesting", labelPos: .rightCenter)
        ]
    )
]

// CLI Entrypoint
let args = CommandLine.arguments
if args.count >= 4 && args[1] == "--grid" {
    let inputPath = args[2]
    let outputPath = args[3]
    var crop = defaultCrop
    if args.count >= 5 {
        let parts = args[4].split(separator: ",").compactMap { Double($0) }
        if parts.count == 4 {
            crop = CGRect(x: parts[0], y: parts[1], width: parts[2], height: parts[3])
        }
    }
    renderGrid(inputPath: inputPath, outputPath: outputPath, cropRect: crop)
    exit(0)
}

let filter = args.count >= 2 ? args[1] : nil
let scriptURL = URL(fileURLWithPath: CommandLine.arguments[0]).standardizedFileURL
let repoRoot = scriptURL.deletingLastPathComponent().deletingLastPathComponent().path
let outDir = "\(repoRoot)/docs/assets"

for spec in specs {
    if let f = filter, !spec.outputName.contains(f) {
        continue
    }
    renderImage(spec, outDir: outDir)
}
