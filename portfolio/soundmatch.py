"""Explainable synthetic music discovery; no audio, external metadata or API dependency."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from contextlib import closing
from itertools import combinations

import numpy as np

SEED = 20261117
GENRES = ["ambient", "electronic", "hip-hop", "indie", "jazz", "pop"]
DEFAULT = {"genres": [], "energy": 0.5, "tempo": 110}


def validate_profile(p):
    if not isinstance(p, dict):
        raise ValueError("Preferences must be an object")
    genres = p.get("genres", [])
    if not isinstance(genres, list) or any(g not in GENRES for g in genres):
        raise ValueError("Choose known genres")
    energy = p.get("energy", 0.5)
    tempo = p.get("tempo", 110)
    if (
        isinstance(energy, bool)
        or not isinstance(energy, (float, int))
        or not np.isfinite(energy)
        or not 0 <= energy <= 1
    ):
        raise ValueError("Energy must be 0–1")
    if (
        isinstance(tempo, bool)
        or not isinstance(tempo, (float, int))
        or not np.isfinite(tempo)
        or not 50 <= tempo <= 190
    ):
        raise ValueError("Tempo must be 50–190")
    return {"genres": sorted(set(genres)), "energy": energy, "tempo": tempo}


def catalog(seed=SEED):
    rng = np.random.default_rng(seed)
    tracks = []
    for i in range(480):
        genre = GENRES[i % len(GENRES)]
        tracks.append(
            {
                "id": f"t{i:04}",
                "title": f"{['Soft Signal', 'Blue Hour', 'Night Transit', 'Golden Current', 'Small Orbit', 'Open Window'][i % 6]} {i // 6 + 1:02}",
                "artist": f"Fictional Artist {i % 60 + 1:02}",
                "genre": genre,
                "energy": round(float(rng.uniform(0.05, 0.95)), 3),
                "tempo": int(rng.integers(60, 181)),
                "synthetic": True,
            }
        )
    return tracks


def recommend(tracks, profile, saved=(), skipped=(), k=12):
    if isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= 100:
        raise ValueError("k must be an integer from 1 to 100")
    p = validate_profile(profile)
    by_id = {t["id"]: t for t in tracks}
    saved_tracks = [by_id[i] for i in saved if i in by_id]
    explicit = set(p["genres"])
    learned = Counter(t["genre"] for t in saved_tracks)
    energy = (
        (p["energy"] + np.mean([t["energy"] for t in saved_tracks])) / 2
        if saved_tracks
        else p["energy"]
    )
    tempo = (
        (p["tempo"] + np.mean([t["tempo"] for t in saved_tracks])) / 2
        if saved_tracks
        else p["tempo"]
    )
    cold = not explicit and not saved_tracks
    candidates = []
    for t in tracks:
        if t["id"] in saved or t["id"] in skipped:
            continue
        genre = (
            1.0
            if t["genre"] in explicit
            else (
                0.8 * learned[t["genre"]] / len(saved_tracks)
                if saved_tracks
                else (1 / len(GENRES) if cold else 0)
            )
        )
        components = {
            "genre": 0.5 * genre,
            "energy": 0.3 * (1 - abs(t["energy"] - energy)),
            "tempo": 0.2 * (1 - min(1, abs(t["tempo"] - tempo) / 140)),
        }
        score = sum(components.values())
        candidates.append(
            {
                **t,
                "score": float(score),
                "components": components,
                "why": f"Genre {components['genre']:.3f} + energy {components['energy']:.3f} + tempo {components['tempo']:.3f}. "
                + (
                    "No genre preference yet: neutral discovery."
                    if cold
                    else "Based on selected genres and saved metadata."
                ),
                "cold_start": cold,
            }
        )
    candidates.sort(key=lambda t: (-t["score"], t["id"]))
    # One artist per slate prevents a repetitive top-K; deterministic greedy reranking.
    result = []
    artists = set()
    for t in candidates:
        if t["artist"] in artists:
            continue
        artists.add(t["artist"])
        result.append(t)
        if len(result) >= k:
            break
    return result


def connect(folder):
    folder.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(folder / "state.sqlite")
    con.execute(
        "CREATE TABLE IF NOT EXISTS preferences (id INTEGER PRIMARY KEY, payload TEXT NOT NULL)"
    )
    con.execute("INSERT OR IGNORE INTO preferences VALUES (1,?)", (json.dumps(DEFAULT),))
    con.execute(
        "CREATE TABLE IF NOT EXISTS feedback (track_id TEXT PRIMARY KEY, action TEXT CHECK(action IN ('save','skip')))"
    )
    con.commit()
    return con


def state(folder):
    with closing(connect(folder)) as con, con:
        p = json.loads(con.execute("SELECT payload FROM preferences WHERE id=1").fetchone()[0])
        rows = con.execute("SELECT track_id,action FROM feedback ORDER BY track_id").fetchall()
    return {
        "profile": p,
        "saved": [i for i, a in rows if a == "save"],
        "skipped": [i for i, a in rows if a == "skip"],
    }


def save_profile(folder, profile):
    p = validate_profile(profile)
    with closing(connect(folder)) as con, con:
        con.execute("UPDATE preferences SET payload=? WHERE id=1", (json.dumps(p),))
    return p


def feedback(folder, track_id, action):
    tracks = json.loads((folder / "tracks.json").read_text())
    if not isinstance(track_id, str) or track_id not in {t["id"] for t in tracks}:
        raise ValueError("Unknown track")
    if action not in ["save", "skip", "undo"]:
        raise ValueError("Unknown feedback action")
    with closing(connect(folder)) as con, con:
        if action == "undo":
            con.execute("DELETE FROM feedback WHERE track_id=?", (track_id,))
        else:
            con.execute(
                "INSERT INTO feedback VALUES (?,?) ON CONFLICT(track_id) DO UPDATE SET action=excluded.action",
                (track_id, action),
            )
    return state(folder)


def evaluate(tracks, seed=SEED, k=10):
    rng = np.random.default_rng(seed)
    users = []
    for i in range(160):
        genres = rng.choice(GENRES, 2, replace=False)
        energy = rng.uniform(0.1, 0.9)
        tempo = rng.uniform(70, 170)
        # Noisy latent utility generates positives. The recommender only sees ten training likes.
        utility = np.array(
            [
                1.1 * (t["genre"] in genres)
                - 1.2 * abs(t["energy"] - energy)
                - 0.006 * abs(t["tempo"] - tempo)
                for t in tracks
            ]
        ) + rng.normal(0, 0.25, len(tracks))
        positives = np.argsort(utility)[-30:]
        rng.shuffle(positives)
        users.append(
            {
                "id": f"u{i:03}",
                "train": [tracks[j]["id"] for j in positives[:10]],
                "holdout": [tracks[j]["id"] for j in positives[10:]],
            }
        )
    popularity = Counter(t for u in users for t in u["train"])
    popular = sorted(tracks, key=lambda t: (-popularity[t["id"]], t["id"]))
    precisions = []
    recalls = []
    diversity = []
    baseline = []
    seen: set[str] = set()
    by_id = {t["id"]: t for t in tracks}
    for u in users:
        assert not set(u["train"]) & set(u["holdout"])
        training = [by_id[x] for x in u["train"]]
        profile = {
            "genres": [g for g, _ in Counter(t["genre"] for t in training).most_common(2)],
            "energy": float(np.mean([t["energy"] for t in training])),
            "tempo": float(np.mean([t["tempo"] for t in training])),
        }
        slate = recommend(tracks, profile, saved=u["train"], k=k)
        hits = len({t["id"] for t in slate} & set(u["holdout"]))
        precisions.append(hits / k)
        recalls.append(hits / len(u["holdout"]))
        seen.update(t["id"] for t in slate)
        diversity.append(
            float(np.mean([a["genre"] != b["genre"] for a, b in combinations(slate, 2)]))
        )
        baseline.append(
            len(
                {t["id"] for t in [t for t in popular if t["id"] not in u["train"]][:k]}
                & set(u["holdout"])
            )
            / k
        )
    return {
        "users": len(users),
        "tracks": len(tracks),
        "k": k,
        "train_likes_per_user": 10,
        "holdout_likes_per_user": 20,
        "train_holdout_overlap": 0,
        "precision_at_k": float(np.mean(precisions)),
        "recall_at_k": float(np.mean(recalls)),
        "catalog_coverage": len(seen) / len(tracks),
        "genre_diversity": float(np.mean(diversity)),
        "popularity_baseline_precision_at_k": float(np.mean(baseline)),
        "seed": seed,
        "limitation": "Evaluation measures recovery of synthetic preferences built from similar metadata. It does not measure listening satisfaction. Random per-user interaction holdout, not a temporal live-user trial.",
    }, users


def build(folder):
    folder.mkdir(parents=True, exist_ok=True)
    tracks = catalog()
    metrics, users = evaluate(tracks)
    (folder / "tracks.json").write_text(json.dumps(tracks, indent=2))
    (folder / "evaluation.json").write_text(json.dumps(metrics, indent=2))
    (folder / "evaluation_users.json").write_text(json.dumps(users, indent=2))
    connect(folder).close()
    return metrics
