import csv
import math
from typing import List, Dict, Tuple
from dataclasses import dataclass

# --- Categorical match bonuses added on top of cosine similarity ---
# These keep the continuous cosine signal as the primary driver while
# still rewarding exact genre/mood alignment (max combined score ~1.25).
GENRE_BONUS = 0.15
MOOD_BONUS = 0.10


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_valence: float       # emotional positivity preference [0-1]
    target_danceability: float  # how danceable the user wants tracks [0-1]
    target_acousticness: float  # acoustic vs. produced sound preference [0-1]
    target_tempo_bpm: float     # preferred tempo in raw BPM (normalized internally)


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _normalize_tempo(bpm: float, tempo_min: float, tempo_max: float) -> float:
    """
    Maps raw BPM to [0, 1] using the observed dataset bounds. Clamps outside values.

    Returns 0.5 when all songs share the same BPM (zero range), meaning tempo
    carries no discriminative information and contributes equally to every score.
    """
    if tempo_max == tempo_min:
        return 0.5
    raw = (bpm - tempo_min) / (tempo_max - tempo_min)
    return max(0.0, min(1.0, raw))


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Returns the cosine similarity between two equal-length vectors.

    Cosine similarity measures the angle between two vectors rather than the
    raw distance between them. A score of 1.0 means the vectors point in
    exactly the same direction (perfect taste alignment); 0.0 means they are
    perpendicular (no alignment). With all-positive [0-1] features, the result
    is always in [0, 1].

    Formula: (A · B) / (||A|| * ||B||)
    """
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


def _match_quality(delta: float) -> str:
    """Converts a [0-1] feature delta into a human-readable match label."""
    if delta < 0.05:
        return "near-perfect match"
    if delta < 0.15:
        return "strong match"
    if delta < 0.30:
        return "moderate match"
    return "weak match"


def _valence_label(valence: float) -> str:
    """Returns a semantic description of a song's emotional tone."""
    if valence >= 0.70:
        return "upbeat/positive tone"
    if valence >= 0.40:
        return "neutral/mixed tone"
    return "dark/melancholic tone"


def _acoustic_label(acousticness: float) -> str:
    """Returns a semantic description of a song's production style."""
    if acousticness >= 0.70:
        return "acoustic/organic sound"
    if acousticness >= 0.40:
        return "mixed acoustic and produced"
    return "produced/electronic sound"


def _build_song_vector(song: Song, tempo_min: float, tempo_max: float) -> List[float]:
    """Returns the 5-dimensional feature vector for a song."""
    return [
        song.energy,
        song.valence,
        song.danceability,
        song.acousticness,
        _normalize_tempo(song.tempo_bpm, tempo_min, tempo_max),
    ]


def _build_user_vector(user: UserProfile, tempo_min: float, tempo_max: float) -> List[float]:
    """Returns the 5-dimensional preference vector for a user."""
    return [
        user.target_energy,
        user.target_valence,
        user.target_danceability,
        user.target_acousticness,
        _normalize_tempo(user.target_tempo_bpm, tempo_min, tempo_max),
    ]


def _build_explanation(
    song_vec: List[float],
    user_vec: List[float],
    song_info: Dict,
    user_info: Dict,
) -> str:
    """
    Builds a multi-line explanation of why a song matches a user's taste.

    song_vec / user_vec are the 5-dimensional feature vectors (already normalized),
    with dimensions [energy, valence, danceability, acousticness, tempo_norm].

    song_info expects keys: genre, mood, tempo_bpm, energy, valence,
                            danceability, acousticness
    user_info expects keys: favorite_genre, favorite_mood, target_tempo_bpm,
                            target_energy, target_valence, target_danceability,
                            target_acousticness

    The normalized tempo delta is read directly from the vectors (index 4) so
    that this function does not need to know the dataset's tempo bounds.
    """
    cosine = _cosine_similarity(song_vec, user_vec)
    genre_bonus = GENRE_BONUS if song_info["genre"] == user_info["favorite_genre"] else 0.0
    mood_bonus  = MOOD_BONUS  if song_info["mood"]  == user_info["favorite_mood"]  else 0.0
    total = round(cosine + genre_bonus + mood_bonus, 4)

    header_parts = [f"cosine: {cosine:.3f}"]
    if genre_bonus:
        header_parts.append(f"genre bonus: +{genre_bonus:.2f}")
    if mood_bonus:
        header_parts.append(f"mood bonus: +{mood_bonus:.2f}")
    lines = [f"Score {total:.2f} ({' + '.join(header_parts)}):"]

    continuous = [
        ("energy",       song_info["energy"],       user_info["target_energy"],       None),
        ("valence",      song_info["valence"],       user_info["target_valence"],       _valence_label(song_info["valence"])),
        ("danceability", song_info["danceability"],  user_info["target_danceability"],  None),
        ("acousticness", song_info["acousticness"],  user_info["target_acousticness"],  _acoustic_label(song_info["acousticness"])),
    ]
    for name, song_val, user_val, label in continuous:
        delta = abs(song_val - user_val)
        quality = _match_quality(delta)
        label_str = f" — {label}" if label else ""
        lines.append(
            f"  {name:<14}: {quality:<20}"
            f" (song has {song_val:.2f}, Δ={delta:.2f}){label_str}"
        )

    # Tempo delta is derived from the pre-normalized vector entries (index 4),
    # avoiding any need to re-normalize or pass dataset bounds into this function.
    tempo_delta_norm = abs(song_vec[4] - user_vec[4])
    lines.append(
        f"  {'tempo':<14}: {_match_quality(tempo_delta_norm):<20}"
        f" (song has {song_info['tempo_bpm']:.0f} BPM)"
    )

    if genre_bonus:
        lines.append(f"  {'genre':<14}: exact match ({song_info['genre']}) — your favorite genre")
    else:
        lines.append(f"  {'genre':<14}: no match (song: {song_info['genre']})")

    if mood_bonus:
        lines.append(f"  {'mood':<14}: exact match ({song_info['mood']}) — your favorite mood")
    else:
        lines.append(f"  {'mood':<14}: no match (song: {song_info['mood']})")

    return "\n".join(lines)


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs
        self._tempo_min = min(s.tempo_bpm for s in songs)
        self._tempo_max = max(s.tempo_bpm for s in songs)

    def _score(self, song: Song, user: UserProfile) -> float:
        """
        Scores a song against a user profile using cosine similarity on five
        continuous features plus small categorical bonuses for genre/mood matches.

        Scoring breakdown (max ~1.25):
          cosine similarity on [energy, valence, danceability, acousticness, tempo_norm]
          +0.15  genre matches user's favorite_genre
          +0.10  mood  matches user's favorite_mood

        Why cosine similarity?
          It measures the angle between the song and user preference vectors,
          not the raw distance. Two vectors pointing in the same direction score
          1.0 regardless of their magnitudes — direction (taste alignment) matters
          more than absolute values.
        """
        song_vec = _build_song_vector(song, self._tempo_min, self._tempo_max)
        user_vec = _build_user_vector(user, self._tempo_min, self._tempo_max)
        score = _cosine_similarity(song_vec, user_vec)
        if song.genre == user.favorite_genre:
            score += GENRE_BONUS
        if song.mood == user.favorite_mood:
            score += MOOD_BONUS
        return round(score, 4)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        return sorted(self.songs, key=lambda song: self._score(song, user), reverse=True)[:k]

    def explain_recommendation(self, song: Song, user: UserProfile) -> str:
        """
        Returns a multi-line explanation of why a song was recommended.

        Breaks down the cosine similarity contribution per feature and explains
        each categorical bonus. Every line includes the user's target value,
        the song's actual value, and a plain-English match quality label.
        """
        song_vec = _build_song_vector(song, self._tempo_min, self._tempo_max)
        user_vec = _build_user_vector(user, self._tempo_min, self._tempo_max)
        song_info = {
            "genre": song.genre, "mood": song.mood, "tempo_bpm": song.tempo_bpm,
            "energy": song.energy, "valence": song.valence,
            "danceability": song.danceability, "acousticness": song.acousticness,
        }
        user_info = {
            "favorite_genre": user.favorite_genre, "favorite_mood": user.favorite_mood,
            "target_tempo_bpm": user.target_tempo_bpm, "target_energy": user.target_energy,
            "target_valence": user.target_valence, "target_danceability": user.target_danceability,
            "target_acousticness": user.target_acousticness,
        }
        return _build_explanation(song_vec, user_vec, song_info, user_info)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            )
    return songs


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Functional entry point for the recommendation logic, used by main.py.

    Converts the song dicts and user_prefs dict into typed objects, delegates
    all scoring and explanation to the Recommender class, then maps results
    back to the original song dicts.

    Returns a list of (song_dict, score, explanation) tuples, sorted by score descending.

    Expected keys in user_prefs:
      favorite_genre, favorite_mood, target_energy, target_valence,
      target_danceability, target_acousticness, target_tempo_bpm
    """
    song_objects = [
        Song(
            id=s["id"], title=s["title"], artist=s["artist"],
            genre=s["genre"], mood=s["mood"], energy=s["energy"],
            tempo_bpm=s["tempo_bpm"], valence=s["valence"],
            danceability=s["danceability"], acousticness=s["acousticness"],
        )
        for s in songs
    ]
    user = UserProfile(
        favorite_genre=user_prefs["favorite_genre"],
        favorite_mood=user_prefs["favorite_mood"],
        target_energy=user_prefs["target_energy"],
        target_valence=user_prefs["target_valence"],
        target_danceability=user_prefs["target_danceability"],
        target_acousticness=user_prefs["target_acousticness"],
        target_tempo_bpm=user_prefs["target_tempo_bpm"],
    )

    rec = Recommender(song_objects)
    song_dict_by_id = {s["id"]: s for s in songs}

    return [
        (song_dict_by_id[song.id], rec._score(song, user), rec.explain_recommendation(song, user))
        for song in rec.recommend(user, k=k)
    ]
