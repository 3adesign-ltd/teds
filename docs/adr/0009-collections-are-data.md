---
status: "accepted"
---
# Collections are data

## Context and Problem Statement

Channels are naturally grouped: by provider, by territory, by the desk that monitors them.
Those groupings are useful for finding things and for access control alike.
An early design called them groups and tied them to grants.
With rights out of TEDS ([ADR 0006](./0006-teds-decides-no-rights.md)), should TEDS still group entities, and if so what does a group mean?

## Decision Drivers

* Grouping is needed by finders and by access-control services alike
* A new channel should join the right groups without anyone adding it
* A group must not imply a permission

## Considered Options

* Collections: static or rule-based sets of entities, nestable, granting nothing
* No grouping in TEDS; each consumer groups for itself
* Groups as ordinary entities of a "group" schema

## Decision Outcome

Chosen option: "Collections: static or rule-based sets of entities, nestable, granting nothing".

* A **static** collection lists its members.
* A **rule** collection has a rule (a schema family, facet values and tag values, all of which must hold), and an entity joins or leaves as its metadata and tags change.
* Collections nest through `parent_id`, and a cycle is refused.
* `pinned` offers a collection as a shared list, for example in a finder.
* `GET /entities?collection=a,b` lists members, recursively.

A collection is a built-in resource rather than an entity type, because a rule collection's membership is computed by the server.

### Consequences

* Good, because an access-control service can grant by collection, and new channels are covered as they appear
* Good, because a finder can offer "News desk channels" without its own configuration
* Bad, because rule evaluation is server work that must stay fast as entities grow

## Pros and Cons of the Options

### No grouping in TEDS

* Good, because TEDS is smaller
* Bad, because every consumer re-implements the same groupings, and they drift

### Groups as ordinary entities

* Good, because it fits the schema-driven model
* Bad, because rule membership needs server behaviour a plain entity cannot have
