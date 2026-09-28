---
status: "accepted"
---
# Per-user data is ordinary entities

## Context and Problem Statement

Viewers need to keep per-user data that follows a person between devices: which timeline lanes they show, their favourite channels, what they opened recently.
An early design gave TEDS special resources for this: `/me`, `/me/profiles/{app}`, `/me/favourites`, `/me/recent`, and a second kind of schema for settings.
But TEDS is schema-driven, and special-purpose resources are a second mechanism beside the one it already has.
How should per-user data be held?

## Decision Drivers

* One mechanism (schemas and entities) rather than two
* Updates from two devices changing different settings must not overwrite each other
* No resource that depends on who is calling, which is an access-control concern ([ADR 0006](./0006-teds-decides-no-rights.md))

## Considered Options

* Per-user data is an entity of an application-supplied schema, at a deterministic id
* Dedicated profile, favourites and recent resources, keyed by the caller
* Per-user data kept by each application in its own store

## Decision Outcome

Chosen option: "Per-user data is an entity of an application-supplied schema, at a deterministic id".

* An application registers an entity schema for its per-user data, with the settings as `metadata` and no roles.
* Each user's data is one entity, at `v5(NS, "user:<family>:<sub>")`, where `NS` is the TEDS namespace ([ADR 0003](./0003-schemas-are-immutable-and-registration-is-idempotent.md)) and `<sub>` is the caller's identity.
* A client computes the id, and reads, replaces or merge-patches the entity through `/entities`.
  JSON Merge Patch updates one key at a time, so two devices changing different settings do not overwrite each other.
* Defaults are the schema's JSON Schema `default` values, applied by the client.
* There is no `/me` and no profile resource.

See [AppNote 0004](../appnotes/0004-per-user-data.md).

### Consequences

* Good, because TEDS has one kind of schema and one kind of stored thing
* Good, because an application's per-user data is described by a schema anyone can read
* Bad, because "only your own" is not enforced by TEDS; an access-control service must enforce it

## Pros and Cons of the Options

### Dedicated resources keyed by the caller

* Good, because a client does not have to compute an id
* Bad, because it is a second mechanism, and it makes the response depend on the caller, which TEDS otherwise avoids

### Each application keeps its own store

* Good, because TEDS stays out of it
* Bad, because every application re-solves roaming, merging and schema validation, and favourites cannot refer to TEDS entities reliably
