import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


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
    likes_acoustic: bool


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, song: Song, user: UserProfile) -> float:
        """
        Scores a song against a user profile.

        Scoring breakdown (max 4.0):
          +2.0  genre matches user's favorite_genre
          +1.0  mood  matches user's favorite_mood
          +0-1  energy similarity: 1.0 - |song.energy - user.target_energy|
        """
        score = 0.0
        if song.genre == user.favorite_genre:
            score += 2.0
        if song.mood == user.favorite_mood:
            score += 1.0
        score += 1.0 - abs(song.energy - user.target_energy)
        return round(score, 4)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = [(song, self._score(song, user)) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre match '{song.genre}' (+2.0)")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood match '{song.mood}' (+1.0)")
        energy_sim = round(1.0 - abs(song.energy - user.target_energy), 4)
        reasons.append(
            f"energy similarity {energy_sim:.2f} (song {song.energy} vs target {user.target_energy})"
        )
        total = self._score(song, user)
        return f"Score {total:.2f}: " + ", ".join(reasons)


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
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Returns a list of (song_dict, score, explanation) tuples, sorted by score descending.
    """

    def score_and_explain(song: Dict) -> Tuple[float, str]:
        score = 0.0
        reasons = []

        if song["genre"] == user_prefs["favorite_genre"]:
            score += 2.0
            reasons.append(f"genre match '{song['genre']}' (+2.0)")

        if song["mood"] == user_prefs["favorite_mood"]:
            score += 1.0
            reasons.append(f"mood match '{song['mood']}' (+1.0)")

        energy_sim = 1.0 - abs(song["energy"] - user_prefs["target_energy"])
        score += energy_sim
        reasons.append(
            f"energy similarity {energy_sim:.2f} (song {song['energy']} vs target {user_prefs['target_energy']})"
        )

        score = round(score, 4)
        explanation = f"Score {score:.2f}: " + ", ".join(reasons)
        return score, explanation

    results = []
    for song in songs:
        score, explanation = score_and_explain(song)
        results.append((song, score, explanation))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:k]
