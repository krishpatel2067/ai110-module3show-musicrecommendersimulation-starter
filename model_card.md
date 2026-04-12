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

The recommender is designed to recommend songs to a given user based on their profile. In the real world, these profiles would be updated automatically as the user listens to songs, likes them, etc., but in this project, all of that is abstracted away: the recommender simply expects the user taste profile to be premade.

The recommender generates top several recommendations based on a user's preferences for genre, mood, energy, etc. in a song. The recommender assumes that the user has standard taste profiles. For example, the recommender behaves well when a pop lover also loves high-energy songs, which is a pretty common pairing in the real world. This recommender is simple and is currently only for classroom exploration. It would have to be analyzed even further and improved to address biases and limitations before rolling it out to real users.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

The recommender uses all the features that can connect one song to another: genre, mood, energy, tempo, etc. All user preferences are considered in this version of the recommender: anything from genre and mood to danceability. The model first converts the numeric features into vectors, which are then passed through calculations to produce a similarity score. That similarity score then gets increased if the categorical features, such as mood and genre, match between a song and user's preferences. This is the main change from the starter logic, that did not use vectors and only had three features under consideration.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The dataset contains 20 songs currently after 10 more were generated using AI to extend the original dataset. The dataset represents a diverse range of genres and moods such as pop, synthwave, and lofi for genres and chill, moody, and happy for mood. No data was removed. The only thing I did was add more datapoints. The dataset doesn't contain genres like EDM and moods like inspirational. It also doesn't contain features such as song duration, which may very well impact preferences.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

The recommender gives reasonable results if their preferences are standard and match at least some of the songs in the dataset across multiple features, for example, by associating a chill mood with low energy and high acousticness. The recommender's scoring correctly captures genres correctly many of the times because of having a higher weight than mood as well as a sizeable portion of the numeric similarity score. The recommendations matched my intutitions for profiles like Happy Pop, where the top recommendation was Sunrise City, which I expected.

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

In the future, the recommender can add features like song length, popularity, etc. as well as their respective references (preferred song length, preferred affinity for currently popular songs, etc.). The recommendations can also be given in more natural language, hiding away unnecessary stats that may bore or overwhelm average users. The top results can also be made less rigid by adding some randomness into the mix, allowing users to discover songs outside of their preferences but only occasionally. The recommender can also be improved to gracefully handle nonstandard user preferences, such as one preferring high energy and high acousticness.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

I learned that recommender systems don't have to be complex to begin with (mine is currently very simple). However, they can be refined with iterations over time after identifying limitations from trials. I discovered that no matter how sophisticated a recommender system gets, it is not always foolproof. And it probably does not matter that a recommender is great but not perfect because end users may see its mistakes as serendipity and a means of discovery of other tastes. This project will cause me to look at recommendation in popular streaming services through a more technical and admiring light. Previously, I used to see it as this monolithic "algorithm" in a more-or-less sinister sight. While some of those aspects remain, I will also start to appreciate the engineering and design that went into such systems.