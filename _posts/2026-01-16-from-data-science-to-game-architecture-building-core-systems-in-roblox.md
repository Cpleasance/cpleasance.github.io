---
layout: post
title: "From Data Science to Game Architecture: Building Core Systems in Roblox"
date: 2026-01-16 17:37:10
tags: [game-development, roblox, lua, software-engineering, architecture]
---
## Overview

This is my first venture into game development using Lua and Roblox Studio. As a data science and AI student, I decided to branch out and explore a completely different domain, and it's been surprisingly rewarding. Today's session focused on building foundational systems for player input, interactions, and time management. The goal was to create a unified, cross-platform experience that works seamlessly on PC, console, and mobile devices.

---

## 1. Time Management System Enhancement

**Problem:** The existing time system tracked days as numbers (1, 2, 3...) but I needed human-readable day names for UI display.

**Approach:**

- Created a lookup structure mapping day numbers to day names (Monday through Sunday)
- Added time tracking that displays formatted time with day names (e.g., "Monday 14:30")
- Ensured the server maintains the single source of truth for game time

**Architecture Decision:** I chose to store the day name server-side rather than computing it client-side. This ensures consistency across all clients and demonstrates a solid understanding of client-server architecture, something I've been studying in my data systems coursework.

---

## 2. Cross-Platform Input System

**Challenge:** Support three distinct input methods with different interaction paradigms:
- Keyboard: Button press
- Controller: Button press (different button)
- Mobile: Touch/tap

**Implementation Approach:**

Rather than hard-coding input handling, I built an abstraction layer that detects the input device and dynamically adapts the UI accordingly. A player on PC with a controller plugged in will see the UI update in real-time as they switch between keyboard and controller. This kind of adaptive system design mirrors patterns I've studied in my ML and data engineering work.

**Sprint System:**
- Uses state tracking to monitor whether the player is sprinting
- Modifies player speed on input begin/end
- Resets properly on character respawn to prevent edge cases

This highlighted an interesting parallel to my data engineering experience. Handling state transitions cleanly and avoiding cascade failures is critical in both domains.

---

## 3. Custom Proximity Prompt System

**Why Custom?**

The default Roblox UI is functional but visually heavy. I wanted a minimal, clean interface that only shows essential information. This exercise reinforced the importance of thoughtful UI/UX design, something I'm continuing to learn.

**Design Considerations:**

1. **Distance-Based Detection** - Rather than relying on threshold events (which can fire erratically), I implemented smooth distance-checking logic. This mirrors signal processing principles I've studied, avoiding edge-case noise in data.

2. **Dynamic UI Creation** - The interface is created programmatically when a player enters range, positioning it above the target object and adjusting visibility based on context.

3. **Platform-Adaptive UI:**
   - Keyboard: Shows action key
   - Controller: Shows appropriate button
   - Mobile: Shows action text as a tappable button

4. **Real-Time Updates** - The UI reflects server-side changes immediately, demonstrating responsive event-driven architecture.

---

## 4. Tag-Based Interaction Architecture

**Design Philosophy:**

Rather than writing custom scripts for every interactable object, I built a centralised system that determines behaviour based on categorisation tags. This is a practical application of a principle I've explored in my data science work. Abstraction and modularity lead to scalable systems.

**How It Works:**

1. **Client Side:** Detects player interaction and sends a request to the server
2. **Server Side:** Validates the request, checks object properties, and routes to the appropriate handler

**Interaction Types:**

- **Doors** – Toggle state and update UI accordingly
- **Items** – Process pickup and removal

**Why This Matters:** The tag-based system is extensible. Adding new interaction types is straightforward: create a new tag, add a handler, and add a route. This is the kind of scalable architecture I'm practising in my software engineering learning.

---

## 5. Mobile-Specific Considerations

**Touch Input Challenges:**
- No physical buttons to reference
- Limited screen real estate
- Touch targets need to be appropriately sized

**Solutions:**

- **Sprint Button:** Positioned in the bottom-right corner, large enough for reliable tapping
- **Interaction:** Made the floating text itself tappable rather than creating a separate button, more intuitive
- **Device Detection:** Intelligently differentiates between touch-capable and keyboard-capable devices

This segment reinforced how context-specific design is essential. Much like how model architectures must be adapted for different data modalities, interface design requires platform awareness.

---

## 6. Client-Server Security Architecture

**Core Principle:** Never trust the client.

**Validation Strategy:**

- All game state changes happen server-side
- Client only sends "I want to interact with this object"
- Server validates:
  - Does the object exist?
  - Is the player within acceptable range?
  - Is the interaction type recognised?

This prevents exploiters from interacting with objects across the map or triggering unintended interactions. It's a practical lesson in defence-in-depth, a principle equally relevant to API security and data pipeline integrity.

---

## 7. System Architecture Overview

The systems I built today are interconnected but modular:

- **Time Manager** – Handles day/night cycles and time tracking
- **Interaction Handler** – Processes all player interactions server-side
- **Input System** – Abstracts platform-specific input differences
- **Prompt UI** – Renders context-aware interaction prompts
- **Mobile Controls** – Provides touch-specific interface elements

---

## Key Learnings

1. **Abstraction Scales** – Building around abstractions rather than hard-coded logic makes systems more maintainable and extensible
2. **State Management Matters** – Clean state handling prevents cascading bugs
3. **Platform Differences Require Thoughtful Design** – Touch, keyboard, and controller each have different UX constraints
4. **Server Authority is Non-Negotiable** – Always validate on the server; never trust the client
5. **Modularity Over Monoliths** – Centralised handlers and tag-based routing beat dozens of custom scripts

---

## Reflections

Branching into game development has been illuminating. Whilst my background is in data science and AI, this project has reinforced universal software engineering principles. Modularity, abstraction, state management, and security apply across domains. The systems I built today are the foundation for more complex features, and I'm excited to continue exploring this area.

This was a solid foundation-building session. I'm looking forward to seeing how these systems evolve as I add more features.