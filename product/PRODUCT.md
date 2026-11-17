# Mini PRD and experiment plan
Target: listeners who want to steer discovery and understand recommendations. The demo validates product mechanics using fictional metadata; it does not offer music playback.

Requirements delivered: optional genre onboarding, explicit energy/tempo controls, cold-start slate, artist-diverse content ranking, visible weighted explanation, save/skip/undo with local persistence, empty state, and reproducible offline evaluation. No collaborative filtering: sparse synthetic interactions are sufficient for a baseline benchmark but do not justify a production social signal.

Proposed experiment: compare explanations shown versus hidden for consenting real users with appropriately licensed content. Primary measure: correctly explaining why a track was selected after discovery tasks. Secondary measures: voluntary save rate and self-reported relevance. Guardrails: repetition, perceived stereotyping, data deletion comprehension, accessibility. Sample size and duration require a real pilot baseline; no uplift is assumed.

Research status: no listener interviews, live listening sessions or A/B tests completed. Browser tests validate controls, not satisfaction.

Future improvements: authorized/licensed metadata and playback; explicit user/account deletion and multi-user storage; evaluate novelty and serendipity with real consented preferences.
