# Principles

These principles help us judge what is and is not in scope, and how we approach the design of TEDS.
They follow the [TAMS principles](https://github.com/bbc/tams/blob/main/PRINCIPLES.md) and the [TADS principles](https://github.com/bbc/tads/blob/main/PRINCIPLES.md), since TEDS is designed to work alongside both.

## What is TEDS?

1. TEDS is designed as an interoperable registry of the things media and data belong to.
   Supporting TEDS should enable integration with other TEDS solutions, removing or minimising the need for bespoke integrations.
2. TEDS is agnostic to clouds, and is intended to deploy anywhere, including on-premise and at the edge.
3. TEDS is schema-driven.
   Every entity it holds is an instance of a schema anyone can read, and TEDS has no special-purpose resources for particular kinds of entity.
4. TEDS stores no media and no timed data.
   It refers to media and data held elsewhere, primarily in TAMS and TADS.
5. TEDS decides no rights.
   It authenticates callers, but what a caller may see or do is the responsibility of the systems around it.
6. TEDS depends on no other service.
   It can refer to TAMS and TADS, and check what it is told against them, but it runs without them.
7. TEDS will be open source to reduce barriers to entry and maximise adoption.
8. TEDS is a specification and not an implementation or product.
   Its normative documents name no product and no organisation.
9. TEDS will be a living specification, evolving to meet the needs of the community.

## Guiding Principles

1. TEDS is a small sharp tool.
   It does not solve all problems in all ways.
2. TEDS and its API should be as simple as possible, and always strike a balance across complexity, capability and scalability.
3. TEDS servers and clients with compatible versions should interoperate.
   The specification is prescriptive where necessary to enable this.
4. We aim to give users as much flexibility as possible while ensuring interoperability.
   Customers extend TEDS by uploading schemas, not by changing the API.
5. The specification is agnostic to implementation, and we avoid implementation details driving decisions.
6. Records that can be made automatically should be.
   A person should only need to decide what the evidence cannot.
7. We re-use patterns where possible: within TEDS, and from TAMS and TADS in particular.
   Paging, tags, webhooks, immutable schemas and authentication follow TADS unless there is a reason recorded in an ADR not to.
8. Breaking changes are possible, but we strike a balance to minimise impact and maximise benefit, through an open decision process.
9. When a common requirement arises, we standardise an approach either in the API specification or an Application Note, to enable interoperability.
