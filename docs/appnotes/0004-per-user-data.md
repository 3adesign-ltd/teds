# 0004: Per-user data

## Abstract

Settings, favourites and recently opened lists should follow a person between devices.
In TEDS they are not a special feature: each is an ordinary entity of a schema the application supplies, stored at an identifier any client can compute.
This note shows the pattern.
The decision is recorded in [ADR 0008](../adr/0008-per-user-data-is-ordinary-entities.md).

## Content

### The application registers a schema

The application registers an entity schema for its per-user data, idempotently, at start-up (`PUT /schemas/{id}`, [ADR 0003](../adr/0003-schemas-are-immutable-and-registration-is-idempotent.md)).
The settings are the schema's `metadata`, with JSON Schema `default` values; it has no roles.
[`entity-schemas/examples/example.profile.logging-viewer-v1.json`](../../entity-schemas/examples/example.profile.logging-viewer-v1.json) is an example.

### One entity per user, at a computable id

A user's data is the entity with id `v5(NS, "user:<family>:<sub>")`:

- `NS` is the TEDS namespace, `cd261b94-a66a-473f-b491-da5ec582a34b`
- `<family>` is the application schema's family, for example `example.profile.logging-viewer`
- `<sub>` is the caller's identity, for example the `sub` of their access token

[`entity-schemas/examples/entity-user-logging-viewer-settings.json`](../../entity-schemas/examples/entity-user-logging-viewer-settings.json) is an example; `tools/validate.py` checks that its id is computed correctly.

### Reading and writing

- `GET /entities/{id}`: 404 means the user has saved nothing yet, so every setting takes its default.
- `PATCH /entities/{id}` with `application/merge-patch+json`: changes only the keys sent.
  Two devices changing different settings do not overwrite each other.
- `PUT /entities/{id}`: creates the entity, or replaces it.
  Use `If-Match` to avoid overwriting a change made elsewhere.

A client applies the schema's `default` values to any key the entity does not have.

### Favourites and recent lists

These follow the same pattern: an application schema whose metadata holds entity ids (and, for a recent list, times), one entity per user.
They are application data, not a TEDS feature.

### What is not stored

Settings that belong to a device rather than a person (panel widths, a debug switch, the audio output device) should stay on the device.
An application's schema should say so in its description, so that nobody adds them later by mistake.

### Who may read whose data

TEDS decides no rights ([ADR 0006](../adr/0006-teds-decides-no-rights.md)).
Restricting a user to their own per-user entities is the access-control service's job, as for any other entity ([AppNote 0005](./0005-composing-teds-with-an-access-control-service.md)).
