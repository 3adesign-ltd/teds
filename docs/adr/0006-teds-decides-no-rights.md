---
status: "accepted"
---
# TEDS decides no rights

## Context and Problem Statement

Once channels are entities, the obvious next requirement is that only certain people may see certain channels, or groups of them.
An early design put organisations, grants, role bundles and a decision endpoint inside TEDS, because TEDS already knows the channels and their groups.
But TEDS is meant to be a specification and a service that can be published and adopted like TAMS and TADS, and neither of those decides rights: the TADS specification says its authorisation model "is not part of the TADS specification, and is up to individual implementers and organisations".
Where should rights live?

## Decision Drivers

* TEDS must have no dependency on another service
* Rights models differ between organisations, and a specification should not impose one
* Listings must still be narrowable per user without breaking paging

## Considered Options

* TEDS decides no rights; an access-control service in front of it does
* TEDS holds organisations, grants and a decision endpoint
* TEDS holds a generic, pluggable policy engine

## Decision Outcome

Chosen option: "TEDS decides no rights; an access-control service in front of it does".

* TEDS authenticates callers ([ADR 0007](./0007-authentication-modes-as-tams-and-tads.md)) and records who changed what (`created_by`, `updated_by`).
* It has no organisations, grants, bundles, decision endpoint or audit of decisions.
* An access-control service holds its grants against TEDS entity and collection ids, and narrows listings with the `id` and `collection` filters, which run inside TEDS's query so paging stays correct.
  It enforces its own 404 for things its user may not see, and filters webhook deliveries.
  It may read TEDS; TEDS never calls it.
  See [AppNote 0005](../appnotes/0005-composing-teds-with-an-access-control-service.md).

### Consequences

* Good, because TEDS stays small, dependency-free and publishable, like TAMS and TADS
* Good, because each organisation keeps its own rights model
* Bad, because an access-control service must sit in front of TEDS wherever users see different things; a deployment without one shows everything to every authenticated caller

## Pros and Cons of the Options

### TEDS holds organisations and grants

* Good, because a single service answers every question
* Bad, because it imposes one rights model, and ties TEDS to an identity system's notion of organisations and teams

### A pluggable policy engine

* Good, because it is flexible
* Bad, because it is a large feature that belongs to access-control products, not to a small registry
