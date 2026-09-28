---
status: "accepted"
---
# Schema definitions are envelopes

## Context and Problem Statement

A TADS Payload Schema's `schema` is a plain JSON Schema: it describes a payload and nothing else.
A TEDS entity schema has to say more than what an entity's metadata looks like.
It must also say which roles an entity of this type is linked to, how each is found automatically, which fields are searchable, and how each role is drawn on a timeline.
Where should that information go?

## Decision Drivers

* The linking information has its own structure and must be validated as strictly as the metadata
* The metadata description should remain an ordinary JSON Schema that existing tools can use
* A definition should be readable on its own

## Considered Options

* An envelope: a TEDS document with `metadata` (a JSON Schema) beside `roles`, `facets`, `search` and `display`
* One JSON Schema, with the linking information in `x-` extension keywords
* The metadata JSON Schema in TEDS, and the linking information in a separate resource

## Decision Outcome

Chosen option: "An envelope", because the roles need their own validation and should not be hidden in extension keywords that JSON Schema tools ignore.

The envelope is `{"$teds": "entity-schema/1", "family", "version", "label", "metadata", "roles", "facets", "search", "display", "purposes"}`.
It is validated by the meta-schema [`api/schemas/definition.json`](../../api/schemas/definition.json), which a server also serves at `GET /service/meta/definition`, so a client can validate a definition before uploading it.

The rules the meta-schema cannot express are listed in [AppNote 0002](../appnotes/0002-roles-keys-and-timeline-types.md) and checked by `tools/validate.py`.

### Consequences

* Good, because `metadata` is a plain Draft 2020-12 JSON Schema that editors, form generators and validators accept unchanged
* Good, because a malformed role is a validation error at upload, not a silently ignored keyword
* Bad, because the envelope's own format has to be versioned; `$teds: entity-schema/1` names the version

## Pros and Cons of the Options

### One JSON Schema with `x-` keywords

* Good, because a definition is a single standard document
* Bad, because JSON Schema validators ignore unknown keywords, so mistakes in the most important part would pass unnoticed

### A separate linking resource

* Good, because each part stays small
* Bad, because the two parts can drift, and a schema cannot be read or reviewed as one thing
