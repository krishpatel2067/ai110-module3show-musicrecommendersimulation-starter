"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import glob
import json

from recommender import load_songs, recommend_songs


def load_taste_profiles(profiles_dir: str) -> dict:
    profiles = {}
    for path in glob.glob(f"{profiles_dir}/*.json"):
        with open(path, encoding="utf-8") as f:
            profile = json.load(f)
            profiles[profile["name"]] = profile
    return profiles


def _quick_highlights(song: dict, user_prefs: dict) -> str:
    """Returns a short summary of the strongest reasons a song was recommended."""
    parts = []
    if song["genre"] == user_prefs["favorite_genre"]:
        parts.append("genre match")
    if song["mood"] == user_prefs["favorite_mood"]:
        parts.append("mood match")
    continuous = [
        ("energy",       song["energy"],       user_prefs["target_energy"]),
        ("valence",      song["valence"],       user_prefs["target_valence"]),
        ("danceability", song["danceability"],  user_prefs["target_danceability"]),
        ("acousticness", song["acousticness"],  user_prefs["target_acousticness"]),
    ]
    parts += [name for name, sv, uv in continuous if abs(sv - uv) < 0.15]
    return " · ".join(parts) if parts else "overall similarity"


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    taste_profiles = load_taste_profiles("taste_profiles")
    print(f"Loaded taste profiles: {', '.join(taste_profiles)}\n")

    user_prefs = taste_profiles["Happy Pop"]

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # --- Summary table ---
    col = {"rank": 3, "title": 26, "artist": 18, "score": 6}
    header = (
        f"{'#':>{col['rank']}}  "
        f"{'Title':<{col['title']}}  "
        f"{'Artist':<{col['artist']}}  "
        f"{'Score':>{col['score']}}  Highlights"
    )
    print(header)
    print("─" * (len(header) + 20))
    for i, (song, score, _) in enumerate(recommendations, 1):
        print(
            f"{i:>{col['rank']}}  "
            f"{song['title']:<{col['title']}}  "
            f"{song['artist']:<{col['artist']}}  "
            f"{score:>{col['score']}.2f}  "
            f"{_quick_highlights(song, user_prefs)}"
        )

    # --- Detailed explanations ---
    print("\n\nDetailed explanations:\n")
    for i, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"{i}. {song['title']} by {song['artist']}")
        print(explanation)
        print()


if __name__ == "__main__":
    main()
