---
status: "accepted"
---
# Links carry role, key, validity and tier

## Context and Problem Statement

An entity is served by several objects in two stores, and which object plays a given part changes over time.
A recorder that restarts may register a new flow; the channel is the same, but "its picture and sound" is now a different flow from that moment on.
Some parts come in several instances (a subtitle track per language), and some tracks are coarse summaries of others (a one-minute loudness rollup of a one-second track).
What does a link need to record for a reader to find the right object at a given time?

## Decision Drivers

* A reader must be able to ask "the object serving role R, key K, at time T" and get exactly one answer
* History must be kept: a channel's loudness before and after a recorder restart must both resolve
* Summary tracks must be found with their base, not declared as separate roles to be kept in step

## Considered Options

* A link carries role, key, store, target, validity timerange and an optional tier
* A link carries role and target only; history and instances are the reader's problem
* A separate role per language, programme and tier

## Decision Outcome

Chosen option: "A link carries role, key, store, target, validity timerange and an optional tier".

* `role`: from the role vocabulary ([AppNote 0002](../appnotes/0002-roles-keys-and-timeline-types.md)), or `x-`-prefixed.
* `key`: `{}` for a role with one instance; `{"lang": "cy"}` for a role declared `cardinality: many`.
* `store` and `target`: a TAMS flow or source, or a TADS track.
* `valid`: a TAMS timerange.
  A link to a live recording is open-ended (`[t_`).
* `tier`: the bucket size, in seconds, of a summary track; absent for the base.
* Links of the same entity, role, key and tier **must not overlap** in validity.
  A server refuses an overlapping link (409), and should enforce this in its database rather than by checking first.
* When a newer member of the same role and key takes over, the older link is **closed** at the newer one's start.
  A link is also closed when its target is deleted.
* `GET /entities/{id}/resolve?role=&key.<name>=&at=` returns the link valid at `at` and its tiers, which is what a viewer calls instead of deriving identifiers.

### Consequences

* Good, because a recorder restart is a new link from a point in time, and history keeps resolving
* Good, because a viewer gets the base track and its whole summary pyramid in one call
* Bad, because every link needs a validity range, including ones that have never changed

## Pros and Cons of the Options

### Role and target only

* Good, because it is simple
* Bad, because a restart breaks the history, and a role with several instances cannot be told apart

### A separate role per language, programme and tier

* Good, because every link is unambiguous without a key
* Bad, because the vocabulary would grow with every language, and a schema could not say "one subtitle track per language the channel carries"
