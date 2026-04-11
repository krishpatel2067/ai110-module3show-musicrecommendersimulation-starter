---
name: Project Context
description: Module 3 upgrade goals for the music recommender — cosine similarity, full feature use, rich explanations
type: project
---

Phase 1 and 2 are complete. Now upgrading to Phase 3.

**Why:** Course progression requires adding cosine similarity scoring and richer recommendation explanations.

**Current state:**
- Song dataclass: id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness
- UserProfile dataclass: favorite_genre, favorite_mood, target_energy, likes_acoustic (bool, unused in scoring)
- _score method: crude additive (+2 genre, +1 mood, +0-1 energy diff) — max 4.0, not normalized
- Two parallel implementations: Recommender class (OOP) and recommend_songs function (functional, used by main.py)
- 20 songs in data/songs.csv, tempo_bpm range [58-168]
- 6 taste profile JSON files: happy_pop, chill_lofi, intense_rock, late_night_synthwave, focused_classical, party_hiphop
- tests/test_recommender.py imports from src.recommender — tests must remain passing

**Design session outcome (2026-04-11):**
- Designing cosine similarity scoring, feature vector design, and explain_recommendation — student reviewing design before code is written
- Key open questions posed to student: UserProfile expansion approach, backward compat with main.py, likes_acoustic bool vs float

**How to apply:** When writing code, respect both the OOP Recommender class interface AND the functional recommend_songs interface. Tests must not break.
