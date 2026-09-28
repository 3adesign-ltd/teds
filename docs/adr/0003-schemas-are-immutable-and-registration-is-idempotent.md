---
status: "accepted"
---
# Schemas are immutable, and registration is idempotent

## Context and Problem Statement

Entities are validated against their schema on every write.
If a schema could change, existing entities could silently stop being valid, and a cached validator could disagree with the stored definition.
TADS forbids editing a Payload Schema's `schema` for the same reasons.
But the core schemas, and schemas that applications ship, must be registered at start-up on every host, every time, without creating duplicates.

## Decision Drivers

* An entity valid today must stay valid against the schema it names
* Services and applications must be able to register their schemas at start-up, repeatedly, on any host
* Identifiers should be the same everywhere, without coordination

## Considered Options

* Immutable definitions, idempotent `PUT /schemas/{id}`, deterministic ids
* Editable definitions, with version history
* Immutable definitions, server-assigned ids only

## Decision Outcome

Chosen option: "Immutable definitions, idempotent `PUT /schemas/{id}`, deterministic ids".

* A schema's `definition` never changes.
  A change is a new version, under a new id.
* `PUT /schemas/{id}` creates the schema if it is absent.
  If the same definition is present, it updates only `label`, `description`, `tags` and `deprecated`, and returns 200.
  If a *different* definition is present, it answers 403.
* Deterministic ids are UUIDv5 under the TEDS namespace `cd261b94-a66a-473f-b491-da5ec582a34b`.
  A schema's id is `v5(NS, "schema:<family>:<version>")`.
  The namespace must never change.
* `(family, version)` is unique.
  `teds.*` families are reserved for the core schemas.
* Uploading version N+1 of a family returns compatibility *warnings* (not errors) when it drops a required role, removes a metadata property, or narrows a type that version N's entities use.
* An entity moves between versions with `POST /entities/{id}/migrate`, which revalidates its metadata and re-evaluates its links.
* A schema that entities use cannot be deleted (409); it can be marked `deprecated`.

### Consequences

* Good, because an application registers its schema at start-up with one idempotent call, and gets the same id on every host
* Good, because a validator compiled from a definition can be cached for ever
* Bad, because fixing a typo in a schema means a new version and a migration

## Pros and Cons of the Options

### Editable definitions, with version history

* Good, because small fixes are easy
* Bad, because entities written under the old definition may no longer validate, and every reader must know which version applied when

### Immutable definitions, server-assigned ids only

* Good, because it is exactly TADS's behaviour
* Bad, because repeated start-up registration creates duplicates, or needs a search-then-create race
