import csv
import math
from typing import Any, List, Dict, Tuple
from dataclasses import dataclass

# --- Categorical match bonuses added on top of cosine similarity ---
# These keep the continuous cosine signal as the primary driver while
# still rewarding exact genre/mood alignment (max combined score ~1.25).
GENRE_BONUS = 0.15
MOOD_BONUS = 0.10

# --- Decade bonus ---
# Maximum bonus awarded when a song's release decade exactly matches the
# user's target decade. Scales linearly to 0 as the gap widens.
DECADE_BONUS_MAX = 0.10


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
    popularity: int          # 0-100
    release_decade: int      # e.g. 1990, 2010
    liveness: float          # 0-1
    instrumentalness: float  # 0-1
    duration_sec: int        # seconds


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_valence: float          # emotional positivity preference [0-1]
    target_danceability: float     # how danceable the user wants tracks [0-1]
    target_acousticness: float     # acoustic vs. produced sound preference [0-1]
    target_tempo_bpm: float        # preferred tempo in raw BPM (normalized internally)
    target_popularity: float       # 0-1 (e.g. 0.8 = prefers popular tracks)
    target_liveness: float         # 0-1 (0 = studio, 1 = live feel)
    target_instrumentalness: float # 0-1 (0 = vocal, 1 = fully instrumental)
    target_duration_sec: float     # preferred song length in seconds (normalized internally)
    target_decade: int             # preferred release decade e.g. 2010


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


def _normalize_popularity(pop: int) -> float:
    """Maps popularity (0-100) to [0, 1]."""
    return pop / 100.0


def _normalize_duration(sec: float, dur_min: float, dur_max: float) -> float:
    """Maps song length in seconds to [0, 1] using catalog bounds. Same pattern as tempo."""
    if dur_max == dur_min:
        return 0.5
    return max(0.0, min(1.0, (sec - dur_min) / (dur_max - dur_min)))


def _decade_bonus(song_decade: int, target_decade: int, decade_range: int) -> float:
    """
    Linear decay bonus for release decade proximity.

    A song from the exact target decade scores DECADE_BONUS_MAX.
    The score falls linearly to 0 as the gap reaches decade_range years.

    Example with decade_range=40 and DECADE_BONUS_MAX=0.10:
      0 years away  → 0.10
      20 years away → 0.05
      40 years away → 0.00
    """
    if decade_range == 0:
        return DECADE_BONUS_MAX
    return max(0.0, 1.0 - abs(song_decade - target_decade) / decade_range) * DECADE_BONUS_MAX


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


def _build_song_vector(
    song: Song, tempo_min: float, tempo_max: float, dur_min: float, dur_max: float
) -> List[float]:
    """Returns the 9-dimensional feature vector for a song."""
    return [
        song.energy,
        song.valence,
        song.danceability,
        song.acousticness,
        _normalize_tempo(song.tempo_bpm, tempo_min, tempo_max),
        _normalize_popularity(song.popularity),
        song.liveness,
        song.instrumentalness,
        _normalize_duration(song.duration_sec, dur_min, dur_max),
    ]


def _build_user_vector(
    user: UserProfile, tempo_min: float, tempo_max: float, dur_min: float, dur_max: float
) -> List[float]:
    """Returns the 9-dimensional preference vector for a user."""
    return [
        user.target_energy,
        user.target_valence,
        user.target_danceability,
        user.target_acousticness,
        _normalize_tempo(user.target_tempo_bpm, tempo_min, tempo_max),
        user.target_popularity,
        user.target_liveness,
        user.target_instrumentalness,
        _normalize_duration(user.target_duration_sec, dur_min, dur_max),
    ]


def _build_explanation(
    song_vec: List[float],
    user_vec: List[float],
    song_info: Dict,
    user_info: Dict,
) -> str:
    """
    Builds a multi-line explanation of why a song matches a user's taste.

    song_vec / user_vec are the 9-dimensional feature vectors (already normalized),
    with dimensions [energy, valence, danceability, acousticness, tempo_norm,
                     popularity_norm, liveness, instrumentalness, duration_norm].

    song_info expects keys: genre, mood, tempo_bpm, energy, valence, danceability,
                            acousticness, popularity, liveness, instrumentalness,
                            duration_sec, release_decade
    user_info expects keys: favorite_genre, favorite_mood, target_tempo_bpm,
                            target_energy, target_valence, target_danceability,
                            target_acousticness, target_popularity, target_liveness,
                            target_instrumentalness, target_duration_sec,
                            target_decade, decade_range

    Normalized tempo and duration deltas are read directly from vector indices
    4 and 8 respectively, so this function needs no catalog bounds itself.
    """
    cosine = _cosine_similarity(song_vec, user_vec)
    genre_bonus  = GENRE_BONUS if song_info["genre"] == user_info["favorite_genre"] else 0.0
    mood_bonus   = MOOD_BONUS  if song_info["mood"]  == user_info["favorite_mood"]  else 0.0
    dec_bonus    = _decade_bonus(
        song_info["release_decade"], user_info["target_decade"], user_info["decade_range"]
    )
    total = round(cosine + genre_bonus + mood_bonus + dec_bonus, 4)

    header_parts = [f"cosine: {cosine:.3f}"]
    if genre_bonus:
        header_parts.append(f"genre bonus: +{genre_bonus:.2f}")
    if mood_bonus:
        header_parts.append(f"mood bonus: +{mood_bonus:.2f}")
    if dec_bonus:
        header_parts.append(f"decade bonus: +{dec_bonus:.2f}")
    lines = [f"Score {total:.2f} ({' + '.join(header_parts)}):"]

    continuous = [
        ("energy",          song_info["energy"],                           user_info["target_energy"],          None),
        ("valence",         song_info["valence"],                          user_info["target_valence"],         _valence_label(song_info["valence"])),
        ("danceability",    song_info["danceability"],                     user_info["target_danceability"],    None),
        ("acousticness",    song_info["acousticness"],                     user_info["target_acousticness"],    _acoustic_label(song_info["acousticness"])),
        ("popularity",      _normalize_popularity(song_info["popularity"]), user_info["target_popularity"],     None),
        ("liveness",        song_info["liveness"],                         user_info["target_liveness"],        None),
        ("instrumentalness", song_info["instrumentalness"],                user_info["target_instrumentalness"], None),
    ]
    for name, song_val, user_val, label in continuous:
        delta = abs(song_val - user_val)
        quality = _match_quality(delta)
        label_str = f" — {label}" if label else ""
        lines.append(
            f"  {name:<16}: {quality:<20}"
            f" (song has {song_val:.2f}, Δ={delta:.2f}){label_str}"
        )

    # Tempo and duration deltas come from pre-normalized vector indices (4 and 8),
    # so no catalog bounds are needed inside this function.
    tempo_delta_norm = abs(song_vec[4] - user_vec[4])
    lines.append(
        f"  {'tempo':<16}: {_match_quality(tempo_delta_norm):<20}"
        f" (song has {song_info['tempo_bpm']:.0f} BPM)"
    )

    dur_delta_norm = abs(song_vec[8] - user_vec[8])
    lines.append(
        f"  {'duration':<16}: {_match_quality(dur_delta_norm):<20}"
        f" (song has {song_info['duration_sec']}s)"
    )

    if genre_bonus:
        lines.append(f"  {'genre':<16}: exact match ({song_info['genre']}) — your favorite genre")
    else:
        lines.append(f"  {'genre':<16}: no match (song: {song_info['genre']})")

    if mood_bonus:
        lines.append(f"  {'mood':<16}: exact match ({song_info['mood']}) — your favorite mood")
    else:
        lines.append(f"  {'mood':<16}: no match (song: {song_info['mood']})")

    lines.append(
        f"  {'release decade':<16}: +{dec_bonus:.2f} bonus (song: {song_info['release_decade']})"
    )

    return "\n".join(lines)


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(
        self,
        songs: List[Song],
        genre_bonus: float = GENRE_BONUS,
        mood_bonus: float = MOOD_BONUS,
        diversity_penalty: float = 1.0,
    ):
        self.songs = songs
        self._genre_bonus = genre_bonus
        self._mood_bonus = mood_bonus
        self._diversity_penalty = diversity_penalty
        self._tempo_min = min(s.tempo_bpm for s in songs)
        self._tempo_max = max(s.tempo_bpm for s in songs)
        self._dur_min = min(s.duration_sec for s in songs)
        self._dur_max = max(s.duration_sec for s in songs)
        self._decade_range = max(s.release_decade for s in songs) - min(s.release_decade for s in songs)

    def _score(self, song: Song, user: UserProfile) -> float:
        """
        Scores a song against a user profile using cosine similarity on five
        continuous features plus small categorical bonuses for genre/mood matches.

        Scoring breakdown (max ~1.45 at default bonuses):
          cosine similarity on nine features: [energy, valence, danceability, acousticness,
                                               tempo_norm, popularity_norm, liveness,
                                               instrumentalness, duration_norm]
          +genre_bonus  genre matches user's favorite_genre  (default 0.15)
          +mood_bonus   mood  matches user's favorite_mood   (default 0.10)
          +0-0.10  linear decade bonus (full at exact decade match, 0 at catalog extremes)

        genre_bonus and mood_bonus are set at construction time and can be raised or
        lowered to shift how much weight categorical matches carry vs. the cosine signal.

        Why cosine similarity?
          It measures the angle between the song and user preference vectors,
          not the raw distance. Two vectors pointing in the same direction score
          1.0 regardless of their magnitudes — direction (taste alignment) matters
          more than absolute values.
        """
        song_vec = _build_song_vector(song, self._tempo_min, self._tempo_max, self._dur_min, self._dur_max)
        user_vec = _build_user_vector(user, self._tempo_min, self._tempo_max, self._dur_min, self._dur_max)
        score = _cosine_similarity(song_vec, user_vec)
        if song.genre == user.favorite_genre:
            score += self._genre_bonus
        if song.mood == user.favorite_mood:
            score += self._mood_bonus
        score += _decade_bonus(song.release_decade, user.target_decade, self._decade_range)
        return round(score, 4)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Returns the top-k songs for the user, sorted by score descending.

        When diversity_penalty < 1.0, uses a greedy selection loop: after each
        pick, every remaining candidate from the same genre has its effective
        score multiplied by diversity_penalty for the next round. A second song
        from genre X scores base × penalty, a third scores base × penalty², etc.
        This spreads results across genres without discarding any songs entirely.

        When diversity_penalty == 1.0 (default), falls back to a simple sort
        with no greedy overhead.
        """
        if self._diversity_penalty == 1.0:
            return sorted(self.songs, key=lambda song: self._score(song, user), reverse=True)[:k]

        # Pre-compute base scores once so _score isn't called repeatedly per round.
        # Song is a mutable dataclass (not hashable), so remaining is a set of IDs
        # with a lookup dict — set removal is O(1) vs O(n) for a list.
        songs_by_id = {song.id: song for song in self.songs}
        base_scores = {sid: self._score(song, user) for sid, song in songs_by_id.items()}
        remaining: set = set(songs_by_id)
        selected = []
        genre_counts: Dict[str, int] = {}

        for _ in range(min(k, len(remaining))):
            best_song = max(
                (songs_by_id[sid] for sid in remaining),
                key=lambda s: base_scores[s.id] * (self._diversity_penalty ** genre_counts.get(s.genre, 0)),
            )
            selected.append(best_song)
            remaining.remove(best_song.id)
            genre_counts[best_song.genre] = genre_counts.get(best_song.genre, 0) + 1

        return selected

    def explain_recommendation(self, song: Song, user: UserProfile) -> str:
        """
        Returns a multi-line explanation of why a song was recommended.

        Breaks down the cosine similarity contribution per feature and explains
        each categorical bonus. Every line includes the user's target value,
        the song's actual value, and a plain-English match quality label.
        """
        song_vec = _build_song_vector(
            song, self._tempo_min, self._tempo_max, self._dur_min, self._dur_max
        )
        user_vec = _build_user_vector(
            user, self._tempo_min, self._tempo_max, self._dur_min, self._dur_max
        )
        song_info = {
            "genre":             song.genre,
            "mood":              song.mood,
            "tempo_bpm":         song.tempo_bpm,
            "energy":            song.energy,
            "valence":           song.valence,
            "danceability":      song.danceability,
            "acousticness":      song.acousticness,
            "popularity":        song.popularity,
            "liveness":          song.liveness,
            "instrumentalness":  song.instrumentalness,
            "duration_sec":      song.duration_sec,
            "release_decade":    song.release_decade,
        }
        user_info = {
            "favorite_genre":          user.favorite_genre,
            "favorite_mood":           user.favorite_mood,
            "target_tempo_bpm":        user.target_tempo_bpm,
            "target_energy":           user.target_energy,
            "target_valence":          user.target_valence,
            "target_danceability":     user.target_danceability,
            "target_acousticness":     user.target_acousticness,
            "target_popularity":       user.target_popularity,
            "target_liveness":         user.target_liveness,
            "target_instrumentalness": user.target_instrumentalness,
            "target_duration_sec":     user.target_duration_sec,
            "target_decade":           user.target_decade,
            "decade_range":            self._decade_range,
        }
        return _build_explanation(song_vec, user_vec, song_info, user_info)


def load_songs(csv_path: str) -> List[Dict[str, Any]]:
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
                    "popularity": int(row["popularity"]),
                    "release_decade": int(row["release_decade"]),
                    "liveness": float(row["liveness"]),
                    "instrumentalness": float(row["instrumentalness"]),
                    "duration_sec": int(row["duration_sec"]),
                }
            )
    return songs


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    genre_bonus: float = GENRE_BONUS,
    mood_bonus: float = MOOD_BONUS,
) -> List[Tuple[Dict, float, str]]:
    """
    Functional entry point for the recommendation logic, used by main.py.

    Converts the song dicts and user_prefs dict into typed objects, delegates
    all scoring and explanation to the Recommender class, then maps results
    back to the original song dicts.

    Returns a list of (song_dict, score, explanation) tuples, sorted by score descending.

    genre_bonus and mood_bonus control how much weight categorical matches carry
    relative to the cosine signal (see Recommender for defaults and rationale).

    Expected keys in user_prefs:
      favorite_genre, favorite_mood, target_energy, target_valence,
      target_danceability, target_acousticness, target_tempo_bpm,
      target_popularity, target_liveness, target_instrumentalness,
      target_duration_sec, target_decade
    """
    song_objects = [
        Song(
            id=s["id"], title=s["title"], artist=s["artist"],
            genre=s["genre"], mood=s["mood"], energy=s["energy"],
            tempo_bpm=s["tempo_bpm"], valence=s["valence"],
            danceability=s["danceability"], acousticness=s["acousticness"],
            popularity=s["popularity"], release_decade=s["release_decade"],
            liveness=s["liveness"], instrumentalness=s["instrumentalness"],
            duration_sec=s["duration_sec"],
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
        target_popularity=user_prefs["target_popularity"],
        target_liveness=user_prefs["target_liveness"],
        target_instrumentalness=user_prefs["target_instrumentalness"],
        target_duration_sec=user_prefs["target_duration_sec"],
        target_decade=user_prefs["target_decade"],
    )

    rec = Recommender(song_objects, genre_bonus=genre_bonus, mood_bonus=mood_bonus)
    song_dict_by_id = {s["id"]: s for s in songs}

    return [
        (song_dict_by_id[song.id], rec._score(song, user), rec.explain_recommendation(song, user))
        for song in rec.recommend(user, k=k)
    ]
