---
name: Architecture State
description: Tracks which modules are complete, in design, or planned — updated each session
type: project
---

## Completed (Phase 1 & 2)
- Song dataclass with 10 fields
- UserProfile dataclass (4 fields, likes_acoustic unused)
- Recommender._score: additive scoring (genre +2, mood +1, energy diff +0-1)
- Recommender.recommend: sorts by score, returns top-k
- Recommender.explain_recommendation: string breakdown of additive score
- recommend_songs: functional parallel implementation used by main.py
- load_songs: CSV loader returning List[Dict]
- 20-song dataset (songs.csv), 6 taste profile JSON files

## In Design (Phase 3, session 2026-04-11)
- Cosine similarity scoring using numerical feature vectors
- Feature normalization (tempo_bpm min-max to [0-1])
- Handling of categorical features (genre, mood) — bonus multipliers, not in cosine vector
- UserProfile expansion: adding target_valence, target_danceability, target_acousticness (float), target_tempo_bpm
- explain_recommendation: per-feature breakdown with human-readable language

## Planned (not yet started)
- Update 6 taste profile JSON files with new UserProfile fields
- Possibly update main.py functional path to match new scoring

## Key Design Decisions Made
- tempo_bpm normalization: min-max using dataset range [58-168]
- Categorical features (genre, mood): handled as bonus multipliers on top of cosine score, NOT inside the vector
- likes_acoustic: convert to target_acousticness: float (0.0-1.0), drop bool
- Cosine similarity score [0,1] + categorical bonus — final score can exceed 1.0 (not purely normalized)
- Next: student reviews design before code is written
