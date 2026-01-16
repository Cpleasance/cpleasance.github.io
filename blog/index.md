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
*{{ post.date | date: "%B %d, %Y" }}*

{{ post.excerpt }}

---
{% endfor %}

{% if site.posts.size == 0 %}
*No posts yet - check back soon!*
{% endif %}

<p class="nav-footer"><a href="/feed.xml">RSS</a> · <a href="#top">Top</a></p>
