from src.recommender import Song, UserProfile, Recommender


def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
            popularity=75,
            release_decade=2010,
            liveness=0.12,
            instrumentalness=0.05,
            duration_sec=210,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
            popularity=40,
            release_decade=2020,
            liveness=0.08,
            instrumentalness=0.70,
            duration_sec=180,
        ),
    ]
    return Recommender(songs)


def make_pop_user() -> UserProfile:
    return UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_valence=0.85,
        target_danceability=0.80,
        target_acousticness=0.15,
        target_tempo_bpm=120,
        target_popularity=0.75,
        target_liveness=0.10,
        target_instrumentalness=0.05,
        target_duration_sec=210,
        target_decade=2010,
    )


def test_recommend_returns_songs_sorted_by_score():
    user = make_pop_user()
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_genre_and_mood_bonuses_lift_score():
    """Pop song earns both bonuses (+0.25 total) on top of a strong cosine match."""
    user = make_pop_user()
    rec = make_small_recommender()
    pop_score = rec._score(rec.songs[0], user)
    lofi_score = rec._score(rec.songs[1], user)

    assert pop_score > lofi_score
    assert pop_score >= 1.0  # cosine near 1.0 + 0.15 genre + 0.10 mood


def test_explain_recommendation_covers_all_features():
    """Explanation must mention every scored feature and the overall score."""
    user = make_pop_user()
    rec = make_small_recommender()
    explanation = rec.explain_recommendation(rec.songs[0], user)

    assert isinstance(explanation, str)
    for term in (
        "Score", "energy", "valence", "danceability", "acousticness",
        "popularity", "liveness", "instrumentalness", "tempo", "duration",
        "genre", "mood", "release decade",
    ):
        assert term in explanation, f"Expected '{term}' in explanation"


def test_single_song_catalog_does_not_crash():
    """Tempo normalization must handle tempo_min == tempo_max without dividing by zero."""
    song = Song(
        id=1, title="Solo", artist="A", genre="pop", mood="happy",
        energy=0.8, tempo_bpm=120, valence=0.8, danceability=0.8, acousticness=0.2,
        popularity=60, release_decade=2010, liveness=0.10, instrumentalness=0.05,
        duration_sec=200,
    )
    rec = Recommender([song])
    results = rec.recommend(make_pop_user(), k=1)
    assert len(results) == 1
