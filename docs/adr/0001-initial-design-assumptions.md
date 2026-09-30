---
status: "accepted"
---
# Initial design assumptions

## Context and Problem Statement

A continuously recorded broadcast channel is, in TAMS and TADS, many separately registered objects: a transport stream flow, thumbnail and keyframe flows, a proxy, and in TADS tracks for loudness, subtitles per language, the as-run programme timeline and signal events.
The processes that create them do not know about each other, and nothing records that they belong together.
Applications that need a channel end up rebuilding the answer, by listing flows and guessing, by deriving identifiers from conventions, or by keeping private tables.
In the deployment that prompted TEDS, three separate identifier-derivation conventions existed, and one failed silently: a viewer asked for a loudness track that nothing had written, and could not tell "not yet" from "never".

This ADR records the assumptions the rest of the design builds on.

## Decision Drivers

* The things media and data belong to need a stable identity that does not change when a recorder restarts
* Which object plays which part, and when, must be recorded rather than inferred afresh by every reader
* The records should be made automatically wherever the evidence exists
* It must work alongside TAMS and TADS without changing either

## Considered Options

* A separate store of typed, schema-described entities, linked to TAMS and TADS objects (TEDS)
* Conventions within TAMS alone: a multi-essence Source per channel, collections and tags
* Membership recorded as TADS events on a per-channel track

## Decision Outcome

Chosen option: "A separate store of typed, schema-described entities, linked to TAMS and TADS objects (TEDS)".

The assumptions are:

1. TEDS stores **entities**: the things media and data belong to, such as channels, clips and programmes.
2. Every entity is an instance of an uploaded, immutable **entity schema**, and is validated against it ([ADR 0002](./0002-schema-definitions-are-envelopes.md), [ADR 0003](./0003-schemas-are-immutable-and-registration-is-idempotent.md)).
3. An entity is connected to the objects that serve it by **links**: a role, an optional key, a store, a target, and a validity timerange ([ADR 0004](./0004-links-carry-role-key-validity-and-tier.md)).
4. Links are made automatically wherever the evidence allows ([ADR 0005](./0005-automatic-linking.md)).
5. TEDS stores no media and no timed data, decides no rights ([ADR 0006](./0006-teds-decides-no-rights.md)), and depends on no other service: it never calls TAMS or TADS ([ADR 0013](./0013-teds-does-not-check-link-targets.md)).
6. TEDS follows TADS conventions (paging, tags, webhooks, immutable schemas, authentication) unless an ADR records a reason not to.

### Consequences

* Good, because every application asks one place what a channel is and gets the same answer
* Good, because neither TAMS nor TADS has to change: TEDS refers to their objects and reads evidence they already hold
* Bad, because it is another service to deploy and keep consistent with the stores it refers to

## Pros and Cons of the Options

### A separate store of typed, schema-described entities

* Good, because entities can span both stores, and link membership can change over time
* Good, because schemas let customers define new kinds of entity without changing the API
* Bad, because TEDS can disagree with TAMS or TADS if an object is deleted; links must be closed when their targets go

### Conventions within TAMS alone

* Good, because it needs no new service
* Bad, because TADS tracks cannot be members of a TAMS Source or collection
* Bad, because membership cannot be bounded in time, and there is no search beyond tag equality
* Bad, because the curated facts (display name, logo, grouping) would be written onto flows another process owns

### Membership recorded as TADS events

* Good, because TADS already models things that change over time
* Bad, because it uses a published data store for a purpose it was not designed for, and puts the integrity of the registry at the mercy of event editing
