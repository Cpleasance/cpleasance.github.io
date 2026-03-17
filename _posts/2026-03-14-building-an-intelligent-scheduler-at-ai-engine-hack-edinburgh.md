---
layout: post
title: "Building an Intelligent Scheduler at AI Engine Hack Edinburgh"
date: 2026-03-14 20:00:00
tags: [hackathon, python, flask, scheduling, algorithms, web-development]
---
## Overview

On March 14th, Danny Macpherson and I competed in AI Engine Hack Edinburgh — a one-day hackathon running from 9am to 8pm, with a £1,000 prize from Tomoro AI on the line. We didn't win, but we shipped something I'm genuinely proud of: a full-stack intelligent workflow scheduling platform built from scratch in under 12 hours.

<!--more-->

The event brought together builders from across Scotland, with OpenAI and Anthropic credits provided, CTO speakers from companies like Owkin and Danu Insights, and partners including JetBrains and Wordsmith. The brief was open-ended — build something useful with AI. We chose to focus on a problem that felt underserved: intelligent task scheduling for appointment-based service businesses.

---

## 1. The Problem We Chose

Most scheduling software for small businesses is either too rigid (fixed time slots, no conflict handling) or too complex to set up. The core insight was that scheduling is fundamentally an optimisation problem — you have employees with different skills and availability, tasks with different priorities and durations, and constraints like buffer time between appointments.

We wanted to build a system that reasons about all of these factors simultaneously, rather than making the user do that work manually.

**The core question:** Given a set of tasks and a set of employees, what's the optimal assignment?

---

## 2. Designing the Priority Engine

**Problem:** How do you decide which task gets assigned first when multiple tasks are competing for the same employee?

**Approach:**

Rather than a simple FIFO queue, we built a multi-factor priority score that weighs:

- Task urgency and deadline proximity
- Employee skill match (proficiency level vs. task requirements)
- Existing schedule density (avoiding overloading one person)
- Time buffer requirements between consecutive appointments

This felt natural to me coming from a data science background — it's essentially a ranking problem. The priority score is a weighted linear combination of normalised features, which is conceptually the same as a simple scoring model. The challenge was getting the weights right under time pressure without the luxury of training data or iteration.

**Architecture Decision:** Priority scoring happens server-side and is recomputed on every scheduling event. This means the system stays consistent even as new tasks arrive mid-session.

---

## 3. Real-Time Conflict Resolution

**Challenge:** What happens when an employee runs over on an appointment and creates a cascade of conflicts downstream?

This was the most technically interesting part of the project. A naive scheduler would just mark the conflict and leave it for the user to resolve. We wanted automatic cascade reassignment.

**Implementation:**

1. Detect the overrun — the appointment end time exceeds the next appointment's start time
2. Identify all downstream appointments for that employee that are now affected
3. Attempt to reassign them in priority order to other available employees with matching skills
4. Where reassignment isn't possible, flag the conflict clearly in the UI

The cascade logic required careful ordering. Reassigning in the wrong order can create new conflicts while resolving old ones. We processed assignments greedily by priority score, which isn't globally optimal but is fast and good enough for real-world workloads.

This problem has a lot in common with job scheduling algorithms I've studied in my systems programming work — the challenge of resource allocation under constraints comes up everywhere from OS process scheduling to ML training job queues.

---

## 4. The Stack and Why We Chose It

**Backend:** Python 3.11 with Flask 3.1 and SQLAlchemy 2.0
**Frontend:** Vanilla JavaScript SPA
**Database:** SQLite (with PostgreSQL-compatible schema)

We made a deliberate choice to avoid heavy frameworks on the frontend. With 12 hours on the clock, the overhead of setting up a React or Vue project — even with Vite — wasn't worth it. Vanilla JS with CSS Grid gave us enough to build a functional, clean interface without configuration overhead.

Flask was the right choice for the same reason: low ceremony, fast to set up, easy to reason about. SQLAlchemy gave us proper ORM-backed transactions, which mattered for the ACID compliance we needed to prevent double-booking.

**ACID-compliant double-booking prevention:** Every scheduling operation wraps the read-check-write sequence in a database transaction. Without this, two concurrent scheduling operations could both read a slot as available and both confirm it — a classic race condition. Locking at the transaction level handles this cleanly.

---

## 5. What We Built vs. What We Planned

We scoped the project reasonably well for a hackathon, but a few things slipped:

**Shipped:**
- Multi-factor priority scheduling engine
- Real-time conflict detection and cascade reassignment
- Employee utilisation analytics dashboard
- Configurable buffer zones between appointments
- ACID-safe transaction handling

**Didn't make it:**
- Demand forecasting (we had a design for it but ran out of time)
- Proper authentication — employees are identified by ID only
- Mobile-responsive UI (functional but not polished on small screens)

The demand forecasting piece was the most interesting idea we didn't finish. The goal was to use historical booking patterns to predict busy periods and proactively flag likely scheduling bottlenecks before they happen. That would have made the system genuinely proactive rather than just reactive — something to return to.

---

## 6. Lessons from Competing

We didn't place, and reflecting on why is more useful than glossing over it.

**What held us back:**

The winning projects leaned heavily into the AI angle — LLM integrations, generative features, demos that were visually immediate and easy to grasp in a 3-minute pitch. Our project was technically solid but hard to demo compellingly. A scheduling dashboard with cascade reassignment logic requires context to appreciate. That's a presentation problem as much as a product problem.

**What I'd do differently:**

- Pick a problem with a more visceral demo — something where the "before and after" is immediately obvious to a judge
- Spend the first hour aligning on what the demo looks like, not just what the system does
- Build the pitch alongside the product, not after it

---

## Key Learnings

1. **Scheduling is a genuine hard problem** — even a simplified version has interesting algorithmic depth once you add real-world constraints
2. **Greedy is often good enough** — globally optimal assignment is NP-hard at scale; a well-ordered greedy approach gets you most of the way there in practice
3. **ACID compliance isn't optional for booking systems** — concurrency bugs in scheduling software cause real damage
4. **Hackathon demos are a different skill** — building something impressive and presenting it impressively are not the same thing
5. **Scope ruthlessly** — the features that didn't ship weren't cut because we were slow, they were cut because we scoped too wide initially

---

## Reflections

Hackathons are a different mode of working to anything in coursework or research. There's no specification, no supervisor, and the feedback loop is a single judging session at the end. I found it genuinely energising, even with the time pressure.

Working with Danny was a strong experience — we divided the work cleanly, with him taking more of the frontend and me anchoring the backend scheduling logic. The project is something I'd like to continue developing. The demand forecasting piece in particular feels worth finishing properly.

If you're curious, the full source is on [GitHub](https://github.com/Cpleasance/Hackathon).
