# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

Real-world recommenders use a hybrid model of content-based filtering and collaborative filtering since either alone isn't enough: both have their tradeoffs, so they need to work together to suggest prefereable songs to users yet also avoid filter bubbles.

My recommender will solely focus on content-based filtering, scoring individual songs based on a vector of attributes, then ranking them not just based on the score, but also based on constraints to avoid boring and redundant rankings (e.g., all in the same genre). The vector of attributes will be a normalized, continuous vector of `[energy, tempo_norm, valence, danceability, acousticness]`, which will be multiplied by the weights of each attribute as well as an average vector representing user preferences. Discrete attributes like `genre` and `mood` will serve as gated weights (2 values controlled by a condition).

### Algorithmic Recipe

The algorithm awards a maximum of 4 points to each song to get ranked. Songs get +2 points for a genre match against a user's taste profile. They get +1 point for a mood match, and they get a continuous additional 0-1 score for energy similarity. Then, the algorithm ranks the songs in descending order by score, returning the top `k` results.

### Potential Biases

This system may be too simple, focusing only on three features. Perhaps it will lead to many songs having the same or very similar scores. Plus, the recommender might recommend very similar songs, sacrificing diversity and freshness.

## Images

### Recommendations with Explanations

![Song recommendations with short explanations](./readme_imgs/focused_classical-1.png)
![Long explanations for song recommendations](./readme_imgs/focused_classical-2.png)

## User Profile: Focused Classical

![Song recommendations with short explanations](./readme_imgs/focused_classical-1.png)
![Long explanations for song recommendations](./readme_imgs/focused_classical-2.png)

## User Profile: Chill Lofi

![Song recommendations with short explanations](./readme_imgs/chill_lofi-1.png)
![Long explanations for song recommendations](./readme_imgs/chill_lofi-2.png)

## User Profile: Happy Pop

![Song recommendations with short explanations](./readme_imgs/happy_pop-1.png)
![Long explanations for song recommendations](./readme_imgs/happy_pop-2.png)

## Edge User Profile: High Energy Heartbreak

![Song recommendations with short explanations](./readme_imgs/high_energy_heartbreak_edge-1.png)
![Long explanations for song recommendations](./readme_imgs/high_energy_heartbreak_edge-2.png)

## Edge User Profile: Acoustic Dance Floor

![Song recommendations with short explanations](./readme_imgs/acoustic_dance_floor_edge-1.png)
![Long explanations for song recommendations](./readme_imgs/acoustic_dance_floor_edge-2.png)

## Edge User Profile: Calm Metal

![Song recommendations with short explanations](./readme_imgs/calm_metal_edge-1.png)
![Long explanations for song recommendations](./readme_imgs/calm_metal_edge-2.png)

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

