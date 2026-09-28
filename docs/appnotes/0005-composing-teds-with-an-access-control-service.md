# 0005: Composing TEDS with an access-control service

## Abstract

TEDS authenticates callers but decides no rights ([ADR 0006](../adr/0006-teds-decides-no-rights.md)).
Where different users may see different entities, an access-control service sits in front of TEDS.
This note describes how the two compose so that listings, paging and single-entity reads stay correct, and what the access-control service is responsible for.

## Content

### What each side holds

| TEDS holds | The access-control service holds |
|---|---|
| entities, links, collections | who may do what to which entity or collection |
| `created_by`, `updated_by` | the audit of its own decisions |
| nothing about users beyond the authenticated identity | users, teams, organisations, as its identity provider defines them |

The access-control service may read TEDS.
TEDS never calls it.

### Granting by collection

Grants should usually name **collections** rather than individual entities.
A rule collection such as "every channel whose provider is Example Broadcaster" admits new channels as they are created, so grants do not have to follow every new entity.
Nested collections let a broad grant cover several narrower groupings.

### Narrowing listings

The access-control service works out which collections (and any individual entities) the user may see, then passes them to TEDS as filters:

```http
GET /entities?type=teds.channel.logging&collection=<a>,<b>&id=<c>
```

The filter runs inside TEDS's query, so the paging headers stay correct.
Filtering a page after it has been returned would give short and empty pages, and a `X-Paging-NextKey` that skipped entities.

### Single entities, and everything else a user reaches

- For an entity the user may not see, the access-control service should answer 404 itself, exactly as for an entity that does not exist, so that identifiers and names do not leak.
  TEDS's own 404 means only "does not exist".
- The same applies to an entity's links, status and resolution, and to per-user entities ([AppNote 0004](./0004-per-user-data.md)): a user is normally allowed only their own.
- Webhook deliveries are not filtered by TEDS.
  A subscriber that serves several users filters them before passing them on.

### Media and data access

Seeing a channel in TEDS does not grant access to its media in TAMS or its data in TADS.
Those stores apply their own authorisation, and an access-control service that governs all three should apply the same grants consistently.
