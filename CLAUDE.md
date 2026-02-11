# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal academic portfolio website for Hang Gao. Static HTML/CSS site hosted on GitHub Pages at hangg7.com. No build system or package manager — everything is hand-written and production-ready as committed.

## Development

- **Local server**: Use `/live-server` skill or `npx live-server --port=8081 --host=0.0.0.0`
- **Mobile testing**: Access via LAN IP on port 8081 (run `ipconfig getifaddr en0` to find IP)
- **Deployment**: Push to `main` branch — GitHub Pages serves automatically

## Architecture

### Layout System
Table-based layout with a max-width 800px centered container. Two-column grid: 25% image / 75% text, with uniform `2.5%` padding across all sections (profile, product, research) for consistent left/right edge alignment.

### Custom HTML Elements
- `<name>` — Profile name (28px)
- `<heading>` — Section headers (22px)
- `<papertitle>` — Paper/project titles (14px, semibold)

### Hover Teaser System
Each project row has a `.one` container (160x160px) with a `.two` overlay. The `.two` div contains the "after" video/image, toggled via inline `onmouseover`/`onmouseout` handlers that set opacity. Each project needs paired JS functions: `{project}_start()` / `{project}_stop()`.

### Content Sections
- **Product**: entries use `class="product-row"`
- **Research**: entries use `class="paper-row"`, optionally with `class="paper-row selected"` for the featured/selected toggle filter

### Responsive Design
- `@media (max-width: 600px)`: Stacks table cells vertically, hides project thumbnails (`.one`), adjusts padding
- `@media (max-width: 380px)`: Hides Chinese name image when it would get too small

## Asset Naming Convention

- Thumbnails: `assets/{project}_before.{png|jpg}` (static) and `assets/{project}_after.{mp4|mov}` (hover video)
- All videos must have `muted autoplay loop playsinline` attributes for iOS compatibility
