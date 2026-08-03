# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-file, no-build static dashboard (`index.html`) of weekend activity ideas for Joanne, her husband, and their dog Bjarne, filtered for pregnancy-friendly / dog-friendly picks in Oulu, Finland. Deployed via GitHub Pages directly from `main` / root — there is no build, lint, or test step.

## Working with this repo

- Everything (HTML, CSS, JS) lives in `index.html`. There is no bundler, package manager, or dependency file — edits are made directly to this file and take effect on page load.
- To preview changes, just open `index.html` in a browser (or use a local static server) — no build command needed.
- Deployment is automatic: committing and pushing to `main` updates the live GitHub Pages site.

## Architecture

- **`DATA` array** (near the bottom of the `<script type="module">` block): the single source of truth for activity ideas. Each entry is `{name, cat: "now"|"later"|"milestone", tags: [...], note}`. Adding/editing/removing ideas means editing this array directly.
- **Rendering**: vanilla JS, no framework. `render()` filters `DATA` by the active tab/search query and rebuilds the `#content` DOM; `buildGrid()` renders the card grid for a filtered set.
- **Check-off state and sync**: check-off state (`done`, keyed by a slugified activity name) is cached in `localStorage` for instant/offline rendering, then synced live across devices via Firebase Realtime Database (`checkoffs/<slug>` path). The `onValue` listener is the source of truth once Firebase connects; local writes are optimistic and get echoed/reconciled through Firebase. The Firebase config/API key in `index.html` is a public client key for this RTDB instance, not a secret.
- **Featured section**: the "This weekend's picks" block near the top is hand-written HTML, independent of `DATA` — update it manually when picking a new weekend's highlights.
