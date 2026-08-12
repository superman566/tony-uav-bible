# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`tony-uav-bible` is Tony's personal UAV/drone and AI learning notes site, built with VitePress and deployed to GitHub Pages via GitHub Actions.

- Live site: `https://superman566.github.io/tony-uav-bible/`
- All notes live under `docs/` as Markdown files
- VitePress config: `docs/.vitepress/config.ts`

## Commands

```bash
npm run docs:dev      # Start local dev server (hot reload)
npm run docs:build    # Build to docs/.vitepress/dist/
npm run docs:preview  # Preview the production build locally
```

There is no test suite or linter configured — the only real "check" is that `docs:build` completes without errors (broken internal links, bad frontmatter, etc. fail the build).

## Architecture

```
docs/
├── .vitepress/
│   ├── config.ts          # Site config: nav, sidebar, theme settings
│   └── theme/              # Custom theme layer (extends DefaultTheme)
│       ├── index.ts        # Injects SidebarToggle into the 'sidebar-nav-before' slot
│       ├── SidebarToggle.vue  # Collapse/expand button; persists state to localStorage
│       └── custom.css      # Collapse animation, keyed off documentElement's data-sidebar-collapsed
├── index.md                # Home page (layout: home, hero + features)
├── uav/                    # UAV notes section
└── ai-yolo/                 # AI / computer vision (YOLO) notes section

.github/workflows/deploy.yml  # CI: build → upload artifact → deploy to GitHub Pages
```

**Sidebar collapse mechanism** (spans 3 files, not obvious from any single one): `SidebarToggle.vue` toggles `document.documentElement.dataset.sidebarCollapsed` and saves the choice to `localStorage`; `custom.css` has the actual show/hide + width transition rules keyed off that `data-sidebar-collapsed` attribute; `theme/index.ts` is just what mounts the toggle button into the default theme's sidebar slot. If the collapse button stops animating correctly, check all three.

**Adding a new note section:** create a folder under `docs/`, add `.md` files, then register both the `nav` entry and the `sidebar` entries for that path prefix in `docs/.vitepress/config.ts` (`themeConfig.sidebar` is keyed by URL prefix, e.g. `'/ai-yolo/'`) — a page not listed in `sidebar` is reachable but won't show up in navigation.

## Content Style

All note content must be written in simple, easy-to-understand language (通俗易懂) — avoid dense textbook phrasing. Any non-trivial or abstract concept must be paired with a simple, concrete example (a number example, analogy, small diagram, or code snippet) that makes it click immediately, not just a definition. This is the dominant pattern across all existing notes: every "一句话理解" (one-line intuition) is immediately followed by a worked numeric example, and often an everyday analogy on top of that.

Other conventions to follow, observed consistently across the existing notes:

- **Every technical/专业 term must be given in both Chinese and English** on first use, e.g. `监督学习（Supervised Learning）`, `损失函数（Loss Function）`, `过拟合（Overfitting）` — never introduce a term in only one language.
- **No LaTeX/math rendering plugin is installed.** Formulas are written as plain-text/pseudocode inside fenced code blocks (e.g. `∂J/∂w = (1/m) × Σ(...)`), always paired with a fully worked numeric example — not `$$...$$` math syntax, which will render as raw text.
- **Long, dense docs end with a terminology glossary** (`## 术语表` or `## 词条解释`) listing key terms for quick lookup — see `classic-cv-algorithms.md` and `dl-env-setup.md`. Every glossary term heading must be written as `### 术语名 {.ignore-header}` — the `{.ignore-header}` attribute (via the `markdown-it-attrs` plugin VitePress enables by default) excludes it from the page's "本页目录" outline (`themeConfig.outline.level` is `[2, 4]` site-wide, so a `###` heading is normally included) without affecting its rendered text or anchor `id`. Without this, a glossary with a dozen-plus terms floods the outline and drowns out the page's real section structure.
- **Section grouping**: newer/restructured long docs group flat `##` sections under thematic `## Part N：主题` headings (see `dl-basics.md`, `nn-training-optimization.md`); older docs (`classic-cv-algorithms.md`, `dl-env-setup.md`, `math-basics.md`) still use flat `##` sections. Prefer `## Part N` grouping for new long docs.
- Cross-references between notes use relative markdown links with anchor text, e.g. `[逻辑回归](#逻辑回归-...)` or `[图像识别的数学基础](/ai-yolo/math-basics)` — link to the concept the first time it's reused rather than re-explaining it.
- Images live under `docs/public/images/` and are referenced with absolute paths, e.g. `![说明](/images/cost_function_3d.png)`.
- The user's actual working YOLO version is **YOLO26**, not YOLO11 or earlier — default any "how to use YOLO" content (CLI commands, Python API, training/inference behavior, default parameters) to YOLO26. When YOLO26 and YOLO11 differ in a way that changes usage (not just internal architecture), briefly call it out inline rather than silently writing YOLO11-era instructions. Known usage-relevant differences (see the YOLO26 section of `docs/ai-yolo/yolo-architecture.md`): NMS-Free (no separate NMS post-processing step, so `iou=`/NMS-threshold tuning that mattered for YOLO11 is largely moot), no DFL head (box-regression output structure explanations that lean on DFL don't carry over), and the MuSGD optimizer (training defaults differ from YOLO11's SGD/AdamW `optimizer=auto` behavior).

## Deployment

Pushes to `main` trigger the GitHub Actions workflow automatically. The workflow uses the official `actions/deploy-pages` approach (no `gh-pages` branch needed). Before the first deploy, enable GitHub Pages in the repo settings: **Settings → Pages → Source → GitHub Actions**.
