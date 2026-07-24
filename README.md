# Our Weekend Ideas

A shareable dashboard of weekend activity ideas for Joanne & her husband (+ Bjarne the Alaskan Malamute), filtered for pregnancy-friendly / dog-friendly picks in Oulu, Finland.

Live at: `https://<your-github-username>.github.io/<repo-name>/` once GitHub Pages is enabled (Settings → Pages → Deploy from branch → `main` / root).

## What's inside

- `index.html` — the whole dashboard (self-contained, no build step)
- Sourced from our old "Minä olen velho" dating-days list plus Edenred Virike / Menox / web research (last updated 2026-07-24)

## Updating

Just edit the `DATA` array near the bottom of `index.html` — each idea is `{name, cat: "now"|"later"|"milestone", tags: [...], note}`. Commit and push; GitHub Pages picks it up automatically.

Check-off state is saved per-browser (localStorage), so it won't sync between your phone and your husband's.
