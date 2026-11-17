# SoundMatch

[Working public demo](https://maramreddyajit-commits.github.io/soundmatch/) · [Product requirements](product/PRD.md)

Explainable music discovery with preference onboarding and save/skip feedback.

All records are fictional/synthetic. No real adoption, revenue or user impact is claimed.

## Run and reproduce

Use Python 3.14.7 (the audited version):

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock.txt
python -m scripts.build_soundmatch
python -m pytest -q
python -m scripts.build_demo
python -m http.server 8000 --directory docs
```

Open http://localhost:8000/. The public demo is served from `docs/` by GitHub Pages. Python source and seed 20261117 reproduce the underlying dataset/evaluation.

## Deployment architecture

The browser implements the same deterministic content ranking as the Python reference. Preferences/save/skip are stored in namespaced localStorage on this browser, not shared across visitors. Clearing site storage clears feedback. Local Python uses SQLite. No audio or external music API is included.

## Evaluation and limits

480 fictional tracks, 60 artists and 160 synthetic profiles. Ten train and twenty held-out likes per user. Precision@10 = 727/1600 = 45.4375%; coverage = 356/480 = 74.1667%. Random per-user interaction split, not temporal/unseen-user validation. Generator and recommender share metadata, so this is favorable synthetic consistency, not listener satisfaction.

See product documentation for KPI definitions, prioritization assumptions and proposed experiments. Proposed research has not been conducted. Implementation was built with AI coding assistance; evidence and limitations are documented explicitly.

## Publication verification — November 17, 2026

10 Python tests passed. `node tests/browser-parity.mjs` passed 163 Python/browser ranking comparisons. Public browser checks passed preference updates, save/reload, skip/undo, mobile layout and isolation between visitors. No uncaught JavaScript errors were observed in these checks.
