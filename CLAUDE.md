# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`tony-uav-bible` is Tony's personal UAV/drone learning notes site, built with VitePress and deployed to GitHub Pages via GitHub Actions.

- Live site: `https://superman566.github.io/tony-uav-bible/`
- All notes live under `docs/` as Markdown files
- VitePress config: `docs/.vitepress/config.ts`

## Commands

```bash
npm run docs:dev      # Start local dev server (hot reload)
npm run docs:build    # Build to docs/.vitepress/dist/
npm run docs:preview  # Preview the production build locally
```

## Architecture

```
docs/
├── .vitepress/
│   └── config.ts     # Site config: nav, sidebar, theme settings
├── index.md          # Home page (layout: home, hero + features)
└── uav/              # UAV notes section
    └── intro.md

.github/
└── workflows/
    └── deploy.yml    # CI: build → upload artifact → deploy to GitHub Pages
```

**Adding a new note section:** create a folder under `docs/`, add `.md` files, then register the sidebar entries in `docs/.vitepress/config.ts` under `themeConfig.sidebar`.

## Deployment

Pushes to `main` trigger the GitHub Actions workflow automatically. The workflow uses the official `actions/deploy-pages` approach (no `gh-pages` branch needed). Before the first deploy, enable GitHub Pages in the repo settings: **Settings → Pages → Source → GitHub Actions**.
