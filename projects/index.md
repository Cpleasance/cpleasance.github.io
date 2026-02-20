---
title: "Projects"
description: "Portfolio of data science, machine learning, and systems programming projects by Cory Pleasance."
---

{% include navigation.html %}

# Projects

---

## Hull Tactical Market Prediction
**Python · LightGBM · CatBoost · scikit-learn** · *Dec 2025 – Present*

Building ensemble models for S&P 500 directional forecasting in a Kaggle competition (1,000+ participants), combining gradient-boosted trees with custom feature engineering on macro-economic indicators. Implemented walk-forward and purged cross-validation to prevent lookahead bias, with hyperparameter tuning via Optuna using custom financial evaluation metrics.

[Kaggle](https://www.kaggle.com/cpleasance){: .btn-kaggle target="_blank" rel="noopener noreferrer"}

---

## Real-Time Sentiment Analysis Pipeline
**Python · VADER · pandas · matplotlib** · *Sep 2025*

Modular Python pipeline for monitoring public sentiment from customer feedback, supporting both batch processing and simulated real-time streaming with configurable chunk sizes. Designed independently runnable modules for ingestion, preprocessing, VADER-based analysis, and visualisation, with CLI tooling, structured logging, and automated report generation.

[GitHub](https://github.com/Cpleasance/sentiment-pipeline){: .btn-github target="_blank" rel="noopener noreferrer"}

---

## Custom Bootloader & Minimal OS
**x86 Assembly · C · Bochs** · *Oct 2025*

Built a bootloader and kernel from scratch in x86 Assembly that initialises the CPU, loads the kernel into memory, and outputs to screen, with a FAT filesystem utility written in C. Engineered modular build system with per-component Makefiles, bootable floppy image generation, and emulator-based testing and debugging via Bochs.

[GitHub](https://github.com/Cpleasance/OS-Build){: .btn-github target="_blank" rel="noopener noreferrer"}

---

## University Course Manager
**Java** · *Nov 2025*

Course management system using BSTs for O(log n) student lookups, quicksort for ranked listings, and directed graph traversal with cycle detection for prerequisite validation.

[Private Repo](javascript:void(0)){: .btn-private}

---

## In Progress

**LLM Red Teaming** · Training linear probes across 32 layers of Qwen and Mistral to locate safety-critical decision boundaries; building a PAIR-style multi-model adversarial council where 3+ LLM architectures iteratively generate and refine attacks through cross-model feedback loops

---

{% include footer.html %}
