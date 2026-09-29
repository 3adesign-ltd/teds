---
status: "accepted"
---
# A link target is checked in its store

## Context and Problem Statement

[ADR 0001](./0001-initial-design-assumptions.md) says TEDS depends on no other service.
Adding a link, however, looks its target up in TAMS or TADS, and refuses one that does not exist or does not satisfy the role's `match`.
Which services must a TEDS server be able to reach, and when?

## Decision Drivers

* A link that points at nothing, or at the wrong kind of flow, is worse than no link: a viewer resolves it and shows the wrong thing
* TEDS must be deployable, and useful for schemas, entities and per-user data, without TAMS or TADS
* A store being briefly unreachable must not be confused with a target being wrong

## Considered Options

* Stores are optional to run; a link is written only after its target has been checked in a configured store
* Stores are required at start-up
* Links are accepted unchecked when a store is not configured

## Decision Outcome

Chosen option: "Stores are optional to run; a link is written only after its target has been checked in a configured store".

* A server starts, and serves everything except links, with no store configured.
  That is what ADR 0001's "depends on no other service" means.
* Adding a link, or accepting a suggestion, fetches the target from the store the link names.
  Changing a link's validity or evidence does not, because the target does not change.
  If a server is configured with several instances of one store, `target.service` names which.
* The outcomes are distinct, so a client can tell a wrong request from a transient failure:
  * no such store configured: **422** `store_not_configured`
  * the target does not exist: **422** `target_missing`
  * the target exists but does not satisfy `match`: **422** `target_mismatch`, saying which property failed
  * the store could not be reached, or answered with a server error: **503** `store_unavailable`, and the link is not written
* TEDS authenticates to a store as itself (a service account), never as the caller.

### Consequences

* Good, because every stored link pointed at a real, matching target when it was written
* Good, because TEDS still runs on its own
* Bad, because adding a link fails while its store is down
* Bad, because a target deleted later leaves a link to nothing until it is closed ([ADR 0004](./0004-links-carry-role-key-validity-and-tier.md))

## Pros and Cons of the Options

### Stores required at start-up

* Good, because a misconfiguration is found immediately
* Bad, because a deployment that uses TEDS only for entities or per-user data must run TAMS and TADS anyway

### Links accepted unchecked

* Good, because links can be written while a store is down
* Bad, because nothing marks which links were checked, so every reader has to distrust all of them
