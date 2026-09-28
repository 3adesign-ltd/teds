---
status: "accepted"
---
# Use Markdown ADRs to record design decisions

## Context and Problem Statement

TEDS is designed in the open, alongside TAMS and TADS, and is expected to be published.
Its decisions need to be understandable by people who were not present when they were made, including why the alternatives were rejected.
How should those decisions be recorded?

## Decision Drivers

* The record must travel with the specification, in the same repository and review process
* It must be possible to see what was considered, not only what was chosen
* It should be familiar to people who already work with TAMS and TADS

## Considered Options

* Markdown Architectural Decision Records (MADR), as TAMS and TADS use
* A single design document, updated as decisions change
* Decisions recorded only in merge request discussions

## Decision Outcome

Chosen option: "Markdown Architectural Decision Records (MADR), as TAMS and TADS use", because it keeps each decision and its alternatives together, reviewable as a merge request, in a format TAMS and TADS contributors already know.

### Consequences

* Good, because each decision can be read, linked and superseded on its own
* Good, because the pipeline can check that every ADR is indexed and none is left "proposed" at merge
* Bad, because a reader has to assemble the current design from several documents; the README and the application notes give the overview

## More Information

TEDS was first designed in a single contract document.
ADRs 0001 to 0010 record the decisions it contained, and the reasons for them, as that document is retired.
