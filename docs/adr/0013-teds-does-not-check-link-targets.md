---
status: "accepted"
---
# TEDS does not check link targets, and does no automatic linking

## Context and Problem Statement

[ADR 0001](./0001-initial-design-assumptions.md) says TEDS depends on no other service.
Two later decisions each made it depend on TAMS and TADS anyway:
[ADR 0012](./0012-a-link-target-is-checked-in-its-store.md) fetched every new link's target from its store and refused one that was missing or did not satisfy the role's `match`,
and [ADR 0005](./0005-automatic-linking.md) had the server watch TAMS and TADS (webhooks and a periodic reconcile) and turn tags and structure into `stamped` and `inferred` links.

In practice this meant a TEDS server could not accept a single link unless it was configured with, could reach, and held credentials for, every TAMS and TADS instance a link might name.
Deploying TEDS meant wiring it to those servers, and a store outage became a TEDS outage for link writes.
Should TEDS reach TAMS or TADS at all?

## Decision Drivers

* TEDS, TAMS and TADS must stay independent: each deployable, and each correct, without the others
* TEDS stores the data it is given; checking that the data describes the world correctly belongs to whoever writes it, which already talks to TAMS or TADS and already knows what it picked and why
* A service that calls other services as itself needs credentials for all of them, and fails when any of them does
* Nothing uses automatic linking: no producer stamps `teds.entity` or `teds.role`, and no linker was ever built

## Considered Options

* TEDS reaches no other service; the client writing a link checks its target
* Keep ADR 0012's check, but make it optional per deployment
* Keep both ADR 0012 and ADR 0005

## Decision Outcome

Chosen option: "TEDS reaches no other service; the client writing a link checks its target".
This supersedes ADR 0012, and the automatic linking of ADR 0005.

* Adding a link validates it only against what TEDS itself holds: the entity, and its schema's role declaration (store, kind, cardinality, key, tier), plus the overlap rule.
  TEDS does not fetch the target, so it does not check that the target exists, or that it satisfies the role's `match`.
* A role's `match` stays in the schema, and keeps its meaning: it is what a target must be to fit the role.
  It is now a statement for the client, which must check a target against it before it writes the link.
* `target.service` is stored and returned, and is not interpreted: it tells a reader which instance of the store the writer meant.
* There is no automatic linking: links are written only through the API, with origin `declared` (by a declaring principal, the system that deployed the entity) or `curated` (by anyone else).
  The `stamped` and `inferred` origins, suggestions and suppression are removed.
* A role's `link` and `tierLink` rules are deprecated and ignored.
  They stay accepted by the meta-schema because schemas are immutable ([ADR 0003](./0003-schemas-are-immutable-and-registration-is-idempotent.md)) and schemas registered before this decision, the core schemas among them, carry them.
  A new schema should leave them out, and a server may warn when one does not.
* The tags of [AppNote 0001](../appnotes/0001-using-teds-with-tams-and-tads.md) are a convention between the producers and clients that want them.
  TEDS reads none of them.

### Consequences

* Good, because a TEDS server needs its database and nothing else, and is configured with no TAMS or TADS address or credential
* Good, because a TAMS or TADS outage no longer stops links being written
* Good, because what TEDS guarantees is exactly what it can check by itself
* Bad, because a stored link may name a target that does not exist, or does not fit its role, if its writer did not check.
  A reader must be ready for that, as it already had to be for a target deleted after its link was written ([ADR 0004](./0004-links-carry-role-key-validity-and-tier.md))
* Bad, because every client that writes links must implement the check itself, rather than relying on one place to do it
* Bad, because nothing links a derived flow or track by itself: whoever creates it, or the system that deploys the entity, writes its link

## Pros and Cons of the Options

### Keep the check, optional per deployment

* Good, because a deployment that wants TEDS to guard its links can have it
* Bad, because a client could no longer tell from TEDS alone whether a link had been checked, so every client would have to check anyway
* Bad, because TEDS would still carry the configuration, credentials and failure modes of every store

### Keep ADR 0012 and ADR 0005

* Good, because every link pointed at a real, matching target when it was written, and derived objects linked themselves
* Bad, because TEDS could not accept a link without TAMS and TADS, and would have had to watch them to do automatic linking
