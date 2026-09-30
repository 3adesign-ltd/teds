---
status: "superseded by [ADR-0013](0013-teds-does-not-check-link-targets.md)"
---
# Automatic linking: declared, stamped, inferred, curated

## Context and Problem Statement

If every link had to be written by a person, TEDS would be one more table that falls out of date.
The evidence for most links already exists.
A recorder knows which channel it is recording.
TAMS flow collections say which flow holds a recording's thumbnails.
A TADS track's timeline reference says which flow it annotates.
A derived flow can say which flow it came from.
How should TEDS turn that evidence into links, and what happens when two sources of evidence disagree?

## Decision Drivers

* Nobody should have to register a link that the evidence already establishes
* A process added to a system later should link itself without being told about the entity
* A wrong link must be correctable by a person, and must stay corrected
* A guess must never become a link on its own

## Considered Options

* Rules in each schema, applied by the server to tags and structure, with origins and a precedence order
* Producers call the TEDS API to register what they create
* Links written only by people and by the system that deploys the entity

## Decision Outcome

Chosen option: "Rules in each schema, applied by the server to tags and structure, with origins and a precedence order".

Each role in a schema has an ordered list of **link rules** ([AppNote 0003](../appnotes/0003-registering-a-channel.md)):

| Rule | Matches | Origin |
|---|---|---|
| `declared` | a link written through the API by the entity's owner | `declared` |
| `tags` | a TAMS or TADS object carrying all the given tags | `stamped` |
| `collectionOf` | a member of another role's TAMS flow collection, with a given collection role | `inferred` |
| `derivedFrom` | an object tagged `teds.derived_from` = another role's member | `inferred` |
| `timelineReferenceOf` | a TADS track whose timeline reference is another role's member | `inferred` |

* Producers **stamp** what they create with tags, in the same request that creates it ([AppNote 0001](../appnotes/0001-using-teds-with-tams-and-tads.md)).
  They do not call TEDS: if TEDS is unavailable, recording carries on and the link appears later.
* A process that derives from another object **inherits** its entity tag, so only the first producer is told the entity.
* When origins disagree about the same role, key and time: `curated > declared > stamped > inferred`.
* A heuristic such as label similarity never creates a link.
  It creates a **suggestion**, which becomes a `curated` link only when a person accepts it.
* A removed link that the evidence would recreate is remembered as suppressed, so it stays removed.

### Consequences

* Good, because adding a new extractor to a system links its output with no change to TEDS or to the extractor's configuration beyond copying a tag
* Good, because a person's correction always wins, and does not have to be repeated
* Bad, because the server must watch TAMS and TADS (webhooks, and a periodic reconcile) to see new evidence

## Pros and Cons of the Options

### Producers call the TEDS API

* Good, because every link is explicit
* Bad, because an outage of TEDS becomes a failed recording or a lost link, and every producer must know TEDS

### Links written only by people and the deploying system

* Good, because nothing is automatic, so nothing is surprising
* Bad, because derived and third-party objects would never be linked, and the record would drift from reality
