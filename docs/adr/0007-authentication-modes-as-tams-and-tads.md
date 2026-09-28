---
status: "accepted"
---
# Authentication modes as TAMS and TADS

## Context and Problem Statement

A client that already talks to TAMS and TADS should be able to talk to TEDS with the same credentials and the same code.
An early design accepted only verified Bearer tokens, on the grounds that TEDS decided rights.
[ADR 0006](./0006-teds-decides-no-rights.md) removed that reason.
Which authentication methods should TEDS specify?

## Decision Drivers

* The same client code and credentials as TAMS and TADS
* Authentication only has to establish who the caller is, for `created_by`/`updated_by` and per-user entity ids
* A deployment must not be able to switch authentication off by accident

## Considered Options

* The TADS security schemes: Bearer token, URL token, and HTTP Basic
* Bearer tokens only
* Leave authentication entirely to the implementation

## Decision Outcome

Chosen option: "The TADS security schemes: Bearer token, URL token, and HTTP Basic".

* `bearer_token_auth`: an HTTP Bearer token, typically an OAuth2 access token.
* `url_token_auth`: the same token as the `access_token` query parameter, used only when the request has no `Authorization` header.
* `basic_auth`: HTTP Basic.
  As in TADS, Bearer tokens are preferred, because a password is long-lived.
* `GET /service` and `GET /service/meta/definition` are unauthenticated, so a client can discover the API version, and validate a schema, before it has a credential.
* Where a token identifies a subject, a server should use its `sub` as the caller's identity, because per-user entity ids are built from it ([ADR 0008](./0008-per-user-data-is-ordinary-entities.md)).

Implementations are expected to verify Bearer token signatures, expiry and issuer.
A known weakness in some store implementations has been accepting tokens that nobody signed.

### Consequences

* Good, because a TAMS/TADS client needs no new authentication code
* Good, because small deployments can use Basic, and large ones an identity provider
* Bad, because URL tokens can appear in access logs; implementations should avoid logging query strings

## Pros and Cons of the Options

### Bearer tokens only

* Good, because it is the strongest option
* Bad, because it differs from TAMS and TADS, and rules out small deployments without an identity provider

### Leave it to the implementation

* Good, because it is flexible
* Bad, because clients could not rely on any method working
