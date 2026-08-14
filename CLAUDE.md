# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-file, no-build static dashboard (`index.html`) of weekend activity ideas for Joanne, her husband, and their dog Bjarne, filtered for pregnancy-friendly / dog-friendly picks in Oulu, Finland. Deployed via GitHub Pages directly from `main` / root — there is no build, lint, or test step for the page itself. A separate scheduled GitHub Actions pipeline (see "Auto-refreshed data" below) fetches external event/merchant data out-of-band and commits it as JSON, which `index.html` reads at runtime.

## Working with this repo

- Everything (HTML, CSS, JS) lives in `index.html`. There is no bundler, package manager, or dependency file — edits are made directly to this file and take effect on page load.
- To preview changes, just open `index.html` in a browser (or use a local static server) — no build command needed.
- Deployment is automatic: committing and pushing to `main` updates the live GitHub Pages site.

## Architecture

- **`DATA` array** (near the bottom of the `<script type="module">` block): the single source of truth for activity ideas. Each entry is `{name, cat: "now"|"later"|"milestone", tags: [...], note}`. Adding/editing/removing ideas means editing this array directly.
- **Rendering**: vanilla JS, no framework. `render()` filters `DATA` by the active tab/search query and rebuilds the `#content` DOM; `buildGrid()` renders the card grid for a filtered set.
- **Check-off state and sync**: check-off state (`done`, keyed by a slugified activity name) is cached in `localStorage` for instant/offline rendering, then synced live across devices via Firebase Realtime Database (`checkoffs/<slug>` path). The `onValue` listener is the source of truth once Firebase connects; local writes are optimistic and get echoed/reconciled through Firebase. The Firebase config/API key in `index.html` is a public client key for this RTDB instance, not a secret.
- **Featured section**: the "This weekend's picks" block near the top is hand-written HTML, independent of `DATA` — update it manually when picking a new weekend's highlights.
- **Auto-refreshed data (Menox/Edenred)**: `scripts/fetch-menox.py` and `scripts/fetch-edenred.py` are run out-of-band by `.github/workflows/refresh-menox.yml` (weekly) and `refresh-edenred.yml` (monthly), which commit their output to `data/menox.json` / `data/edenred.json` (each with a `fetchedAt` timestamp). `index.html` only ever reads these committed files at runtime — it never scrapes the sources directly (avoids CORS/JS-rendering issues, per JOA-306). Menox events render into their own "This week in Oulu" section, with a staleness banner shown if `fetchedAt` is more than a week old. Edenred merchants that accept the Virike voucher are merged into `DATA` (`tags:["virike"]`) so they flow through the normal card/tab/search rendering. Note: the Menox fetch depends on an undocumented Supabase endpoint reverse-engineered from Menox's own frontend, not a published API — it may break if Menox changes their bundle; the staleness banner is the safety net for that.
