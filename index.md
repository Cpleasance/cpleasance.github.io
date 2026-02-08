---
title: "Home"
description: "Cory Pleasance - Data Science & AI student at University of Stirling. Researching LLM security, mechanistic interpretability, and adversarial testing."
---

{% include navigation.html %}

# Cory Pleasance

**Data Science & AI** · University of Stirling

Researching LLM security and mechanistic interpretability through adversarial testing and red teaming. Background in distributed systems, HPC, and low-level programming.

## Now

- Research assistant studying LLM safety — training linear probes on transformer layer activations and co-authoring a paper on mechanistic interpretability
- Competing in Hull Tactical S&P 500 forecasting challenge on Kaggle
- Year 2 of BSc Data Science & AI, on track for First Class Honours

## Latest Post

{% for post in site.posts limit:1 %}
{% assign words = post.content | number_of_words %}{% assign minutes = words | divided_by: 200 %}{% if minutes < 1 %}{% assign minutes = 1 %}{% endif %}[**{{ post.title }}**]({{ post.url }}) · *{{ post.date | date: "%B %d, %Y" }} · {{ minutes }} min read*

{{ post.excerpt | strip_html | truncatewords: 30 }}
{% endfor %}

## Connect

<div class="social-links">
  <a href="https://github.com/Cpleasance" class="social-link" target="_blank" rel="noopener noreferrer">
    <img src="/assets/images/icons/github.svg" alt="GitHub profile icon" class="social-icon">
    GitHub
  </a>
  <a href="https://www.linkedin.com/in/cory-pleasance-b99b80205/" class="social-link" target="_blank" rel="noopener noreferrer">
    <img src="/assets/images/icons/linkedin.svg" alt="LinkedIn profile icon" class="social-icon">
    LinkedIn
  </a>
  <a href="https://www.kaggle.com/cpleasance" class="social-link" target="_blank" rel="noopener noreferrer">
    <img src="/assets/images/icons/kaggle.svg" alt="Kaggle profile icon" class="social-icon">
    Kaggle
  </a>
  <a href="mailto:corypleasance05@gmail.com" class="social-link">
    <img src="/assets/images/icons/gmail.svg" alt="Email icon" class="social-icon">
    Email
  </a>
</div>
