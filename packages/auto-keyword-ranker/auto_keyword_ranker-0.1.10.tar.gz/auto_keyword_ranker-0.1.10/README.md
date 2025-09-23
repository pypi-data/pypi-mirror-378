# auto-keyword-ranker
[![PyPI version](https://img.shields.io/pypi/v/auto-keyword-ranker)](https://pypi.org/project/auto-keyword-ranker)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A lightweight Python library to automatically extract and rank the most relevant keywords and keyphrases from text.

**Goal:** Provide a single-line call to obtain ranked keywords for articles, blog posts, or short documents.
Uses **TF-IDF** by default, with optional re-ranking via **sentence-transformer embeddings**.

---

## Installation

```bash
pip install auto-keyword-ranker
```

With optional embedding-based re-ranking:
```bash
pip install auto-keyword-ranker[embed]
```


---
## Quickstart

```python
from autokeyword import rank_keywords

text = """
Artificial intelligence is transforming industries by enabling new capabilities
such as natural language processing, computer vision, and advanced data analytics.
Companies across healthcare, finance, and manufacturing are investing heavily in AI
to automate decision-making, enhance efficiency, and unlock new insights from
large datasets.
"""

# Simple TF-IDF keyword ranking
keywords = rank_keywords(text, top_n=10)
print(keywords)
```


Output

A list of (keyword, score) pairs, for example:



```python
[('new', 0.25),
 ('vision advanced', 0.12),
 ('unlock new', 0.12),
 ('unlock', 0.12),
 ('transforming industries', 0.12),
 ('vision', 0.12),
 ('transforming', 0.12),
 ('processing computer', 0.12),
 ('new insights', 0.12),
 ('processing', 0.12)]
```

![Example Bar Chart](https://raw.githubusercontent.com/reyaoberoi/auto-keyword-ranker/main/docs/example.png)



---

## API

```python
rank_keywords(
    texts,
    top_n=10,
    method='tfidf',
    ngram_range=(1,2),
    stop_words=True,
    use_embeddings=False,
    embedding_model=None,
    combine_score_alpha=0.6
)
```

See docstrings in
[core.py](https://github.com/reyaoberoi/auto-keyword-ranker/blob/main/autokeyword/core.py)
for full parameter descriptions.


---

## CLI

You can also run the CLI (after installation):
```python
python -m autokeyword.cli --text "Your article text here" --top 10
```


---

## How It Works


TF-IDF scoring formula:

$$
\text{TF-IDF}(t, d) = \text{TF}(t, d) \times \log \frac{N}{1 + \text{DF}(t)}
$$

Where:
- \( t \) = term  
- \( d \) = document  
- \( N \) = total number of documents  


---

## Use Cases
- SEO keyword extraction for blog posts
- Automatic tagging in content management systems
- Quick summarization of research papers
- Preprocessing for search or recommendation engines


---

License


[MIT License](LICENSE) © 2025 Reya Oberoi