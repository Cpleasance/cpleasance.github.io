---
title: "Blog"
---

{% include navigation.html %}

<p class="rss-link"><a href="/feed.xml">RSS Feed</a></p>

---

# Blog

Welcome to my blog, where I share insights on machine learning, LLM research, high-performance computing, and my journey through data science and AI.

---

## Topics I Write About

- **Large Language Models** - Prompt engineering, adversarial testing, alignment research, and robustness evaluation
- **High-Performance Computing** - Distributed training, multi-GPU/CPU/TPU setups, and performance optimization
- **Machine Learning Projects** - Kaggle competitions, production pipelines, and practical applications
- **Systems Programming** - Low-level development, operating systems, and embedded systems
- **Research Updates** - Progress on university-led research and academic work

---

## Recent Posts

{% for post in site.posts %}
### [{{ post.title }}]({{ post.url }})
*{{ post.date | date: "%B %d, %Y" }}*

{{ post.excerpt }}

---
{% endfor %}

{% if site.posts.size == 0 %}
*No posts yet - check back soon!*
{% endif %}

---

<p class="nav-footer"><a href="#top">Back to Top</a></p>

