# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**MusicMatcher 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

The recommender considers every sensible feature, leaving out only `id`, `title`, and `artist` since they are not relevant features to scoring and recommending. Most of the genres are underreprented, such as `jazz` and `r&b`, since the dataset only has 20 songs distributes across many genres. There are also several, though fewer, underrepresented moods, such as `melancholic` and `peaceful`, again suffering from the small dataset size. The recommender places heavy emphasis on genre and mood matching, which sometimes causes songs to be propped up in the top `k` solely due to this, overpowering the numeric (`energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness`), which is especially evident in the edge case taste profiles. The recommender also favors users with "standard" preferences, such as liking `pop`, `happy`, and low `accousticness` together. Users such as those represented by the edge case test profiles may find that the recommender does not work as well for them.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

I tested 6 user profiles, 3 of them standard:

* Happy Pop
* Chill LoFi
* Focused Classical

And 3 of them edge cases:

* Acoustic Dance Floor
* Calm Metal
* High Energy Heartbreak

**Happy Pop and Acoustic Dance Floor**: The Happy Pop profile prefers less acoustic, higher BPM, and slightly higher energy songs than the Acoustic Dance Floor profile. However, the twist is that both prefer high valence and high danceability.

**Chill Lofi and Calm Metal**: Both profiles prefer low energy, medium tempo, and medium valence. The Calm Metal profile prefers higher acousticness than the Chill Lofi profile.

**Focused Classical and High Energy Heartbreak**: These are almost polar opposites. The High Energy Heartbreak profile prefers much higher BPM, lower acousticness, higher danceability, much lower valence, and much higher energy than the Focused Classical profile. 

I'm surprised by the fact that even though the Chill Lofi and Calm Metal profiles have similar preferences, only one song is in both of their top 5 recommended songs. This outlines that the genre and mood heavily distinguishes the makeup of the recommendation lists.

A simple test I can is toggling off mood matching, which caused the song Rooftop Lights to disappear from the Acoustic Dance Floor profile's recommendations, revealing that mood matching alone was propping up the song even if the numeric matching was weak.


---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
