# pipe-landing (`rotarycam.app`)

Landing page, open-hardware machine build guide (`build-guide.html`), and visual operator documentation (`docs/`) for **RotaryCAM / Pipe CAM**.

## Agent & Screenshot Processing Guide

See **[`AGENTS.md`](./AGENTS.md)** for the mandatory workflow for cropping, highlighting, and generating documentation screenshots using [`scripts/annotate_docs_screenshots.swift`](./scripts/annotate_docs_screenshots.swift):

```bash
# 1. Generate a 100px/200px coordinate grid on a raw screenshot to find (x, y, w, h)
swift scripts/annotate_docs_screenshots.swift --grid "/path/to/raw.png" "/tmp/grid.png"

# 2. Render all (or filtered) annotated documentation screenshots into docs/assets/
swift scripts/annotate_docs_screenshots.swift [filter]
```
