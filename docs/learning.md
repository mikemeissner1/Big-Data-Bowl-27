# Learning notes

One entry per method we use. Goal: understand it well enough to explain it to an NFL GM.

## Template

```
## Method name
- **What it is (plain English):**
- **Why we use it here:**
- **How to read the result:**
- **Watch out for:**
- **How to explain it to a GM:** (1-2 sentences, no jargon)
- **Source:**
```

## Entries

## Binomial standard error of a rate
- **What it is (plain English):** if a player has 250 chances and succeeds 8.4% of the time, pure luck alone would move that percentage by about `sqrt(p(1-p)/n)`, here 1.8 points.
- **Why we use it here:** to judge, before modelling, whether one player's measured rate (pressures allowed, targets per route) can be told apart from luck at realistic snap counts (data audit, section 6).
- **How to read the result:** compare it with how much players really differ. If the gap between a good and a bad player is smaller than the standard error, the rate cannot rank them.
- **Watch out for:** it assumes every snap is an independent coin flip. Opponents, teammates and game situation make real noise larger, so it is a lower bound.
- **How to explain it to a GM:** "How much would his number move if he played the same snaps again? Over 250 snaps, about two points on a pressure rate."
- **Source:** standard result for a proportion (any introductory statistics text).

## Agreement check between two measures of the same thing
- **What it is (plain English):** line up two measurements of the same quantity (sensor 40 time vs official 40 time) and report both the average gap (bias) and how well they move together (correlation).
- **Why we use it here:** to see whether the Combine sensor traces can be trusted as a faithful record of the published results (data audit, section 2).
- **How to read the result:** high correlation (0.91) with a consistent offset (+0.36 s) means the two rank athletes the same way but define the clock differently. A drifting offset (+0.30 to +0.41 s by year) means the definition is not constant.
- **Watch out for:** correlation hides bias, and bias hides drift. Report all three. My start rule was crude, so part of the offset is my method.
- **How to explain it to a GM:** "The sensor and the stopwatch agree on who is fastest, but the sensor clock starts earlier, by about a third of a second."
- **Source:** standard method-comparison practice (Bland and Altman, 1986, Lancet 327:307-310).

