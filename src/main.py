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


COL = {"rank": 3, "title": 26, "artist": 18, "score": 6}
DIVIDER_WIDTH = 80


def _print_profile_recommendations(user_prefs: dict, songs: list) -> None:
    name = user_prefs["name"]
    description = user_prefs.get("description", "")
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("=" * DIVIDER_WIDTH)
    print(f"  {name}")
    print(f"  {description}")
    print()
    print(f"  genre={user_prefs['favorite_genre']}  mood={user_prefs['favorite_mood']}  "
          f"energy={user_prefs['target_energy']}  valence={user_prefs['target_valence']}  "
          f"danceability={user_prefs['target_danceability']}  "
          f"acousticness={user_prefs['target_acousticness']}  "
          f"tempo={user_prefs['target_tempo_bpm']:.0f} BPM")
    print("=" * DIVIDER_WIDTH)

    # --- Summary table ---
    header = (
        f"{'#':>{COL['rank']}}  "
        f"{'Title':<{COL['title']}}  "
        f"{'Artist':<{COL['artist']}}  "
        f"{'Score':>{COL['score']}}  Highlights"
    )
    print(header)
    print("─" * DIVIDER_WIDTH)
    for i, (song, score, _) in enumerate(recommendations, 1):
        print(
            f"{i:>{COL['rank']}}  "
            f"{song['title']:<{COL['title']}}  "
            f"{song['artist']:<{COL['artist']}}  "
            f"{score:>{COL['score']}.2f}  "
            f"{_quick_highlights(song, user_prefs)}"
        )

    # --- Detailed explanations ---
    print("\nDetailed explanations:\n")
    for i, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"{i}. {song['title']} by {song['artist']}")
        print(explanation)
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    taste_profiles = load_taste_profiles("taste_profiles")
    print(f"Loaded taste profiles: {', '.join(taste_profiles)}\n")

    for user_prefs in taste_profiles.values():
        _print_profile_recommendations(user_prefs, songs)
        print()


if __name__ == "__main__":
    main()
