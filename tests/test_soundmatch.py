import pytest

from portfolio.soundmatch import (
    DEFAULT,
    build,
    catalog,
    evaluate,
    feedback,
    recommend,
    state,
    validate_profile,
)


def test_cold_start():
    r = recommend(catalog(), DEFAULT)
    assert len(r) == 12 and all(t["cold_start"] for t in r)
    assert len({t["artist"] for t in r}) == 12


def test_genre_and_score():
    r = recommend(catalog(), {"genres": ["jazz"], "energy": 0.4, "tempo": 100})
    assert all(t["genre"] == "jazz" for t in r[:5])
    assert all(abs(t["score"] - sum(t["components"].values())) < 1e-12 for t in r)


def test_feedback_exclusion():
    tracks = catalog()
    first = recommend(tracks, DEFAULT)[0]["id"]
    assert first not in {t["id"] for t in recommend(tracks, DEFAULT, skipped=[first])}
    assert first not in {t["id"] for t in recommend(tracks, DEFAULT, saved=[first])}


def test_reproducible_and_holdout():
    a, users = evaluate(catalog())
    b, _ = evaluate(catalog())
    assert a == b
    assert all(not set(u["train"]) & set(u["holdout"]) for u in users)
    for field in [
        "precision_at_k",
        "recall_at_k",
        "catalog_coverage",
        "genre_diversity",
    ]:
        assert 0 <= a[field] <= 1


def test_persistence_undo(tmp_path):
    build(tmp_path)
    feedback(tmp_path, "t0001", "save")
    assert state(tmp_path)["saved"] == ["t0001"]
    feedback(tmp_path, "t0001", "skip")
    assert state(tmp_path)["skipped"] == ["t0001"] and not state(tmp_path)["saved"]
    feedback(tmp_path, "t0001", "undo")
    assert not state(tmp_path)["skipped"]


@pytest.mark.parametrize(
    "p",
    [
        {"genres": ["bogus"]},
        {"energy": 2},
        {"tempo": -1},
        {"genres": "pop"},
        {"energy": float("nan")},
    ],
)
def test_invalid_preferences(p):
    with pytest.raises(ValueError):
        validate_profile(p)
