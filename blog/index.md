---
title: "Blog"
description: "Technical blog posts on machine learning, LLMs, systems programming, and software architecture by Cory Pleasance."
---

{% include navigation.html %}

---

# Blog

---

{% for post in site.posts %}
### [{{ post.title }}]({{ post.url }})
{% assign words = post.content | number_of_words %}{% assign minutes = words | divided_by: 200 %}{% if minutes < 1 %}{% assign minutes = 1 %}{% endif %}*{{ post.date | date: "%B %d, %Y" }} · {{ minutes }} min read*

{{ post.excerpt }}

---
{% endfor %}

{% if site.posts.size == 0 %}
*No posts yet - check back soon!*
{% endif %}

<p class="nav-footer"><a href="/feed.xml">RSS</a> · <a href="#top">Top</a></p>
