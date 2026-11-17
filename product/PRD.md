# SoundMatch product requirements and decision record

## User problem and audience
A new discovery user has little history and cannot tell why suggestions fit. Intended users are listeners wanting explicit control over mood/pace/genre and transparent recommendations. No real listener research supports the persona yet.

## Goal and delivered scope
Demonstrate personalization mechanics with legal, fictional metadata. Delivered: 480 generated tracks/60 artists; optional genre onboarding; energy and tempo controls; weighted content scores; neutral cold start; one-per-artist slate; save/skip/undo; SQLite persistence; synthetic holdout evaluation. No audio, external catalog, collaborative filtering, real listening events or Spotify integration exists.

## Acceptance criteria
- Empty genre selection is supported and explicitly labeled neutral discovery.
- The score equals displayed genre/energy/tempo components; it is not a probability.
- Saved/skipped items leave the candidate set. Undo restores eligibility, and state survives reloads.
- One artist appears at most once per slate. Invalid feedback/parameters return useful errors.
- Only training likes construct the evaluation profile. Hidden positives never influence ranking.

## Prioritization
Impact × subjective confidence / relative effort.

| Feature | Impact | Confidence | Effort | Score | Status |
|---|---:|---:|---:|---:|---|
| Cold start and explanations | 3 | .9 | 2 | 1.35 | Delivered |
| Reversible feedback | 3 | .85 | 2 | 1.275 | Delivered |
| Reproducible holdout | 2 | .85 | 2 | .85 | Delivered |
| Licensed catalog/playback | 3 | .4 | 5 | .24 | Unstarted |
| Collaborative ranking | 2 | .3 | 6 | .1 | Unstarted |

## KPIs and evaluation limits
Precision@10 = held-out hits / ten recommendation slots, averaged across 160 synthetic profiles. Recall@10 = hits / twenty hidden likes. Coverage = distinct recommended IDs / 480 tracks. Diversity = different-genre pairs / 45 pairs per ten-track slate. Training and held-out interactions are disjoint; users appear on both sides because this is personalized interaction completion, not unseen-user generalization. It is a random split, not temporal. Unobserved tracks are not proven disliked.

The generator and recommender use related genre/energy/tempo attributes, making this an intentionally favorable synthetic benchmark. A training-popularity baseline is descriptive; it does not use the ranker's identical artist-diversity constraint, so the difference is not a controlled ranking win. No claim of real recommendation quality or uplift follows. For a future licensed-content trial, measure self-reported relevance and voluntary saves among exposed consenting listeners; track skips, repetition and explanation comprehension as guardrails.

## Proposed experiment
Compare explanations visible versus hidden while holding slate contents fixed and counterbalancing order. Primary endpoint: correctly explaining the recommendation mechanism. Secondary: voluntary saves and relevance ratings. Guardrails: perceived repetition, stereotyping, privacy/deletion comprehension. Recruit consenting participants only after licensed content is available; determine quantitative study size from pilot variability.

## Recommendation
Use this build to demonstrate transparent ranking and data separation. Validate with real consented preferences before optimizing for satisfaction. Add licensing/playback and account-level privacy controls before collaborative complexity. Three next improvements: licensed metadata, explicit data deletion/multi-user state, and a temporally separated real-feedback evaluation.

## Planned usability tasks
Start with no genres; choose a genre and explain a changed score; save then reload; skip then undo; distinguish similarity score from satisfaction probability. No human testing has been completed.
