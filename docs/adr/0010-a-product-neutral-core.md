---
status: "accepted"
---
# A product-neutral core

## Context and Problem Statement

TEDS was first designed inside one product's system, and its early drafts named that product in schema families, examples and application settings.
A specification meant to be published and adopted, like TAMS and TADS, cannot carry one vendor's names in its normative parts.
Which parts must be neutral, and how is that kept true?

## Decision Drivers

* Anyone should be able to implement and adopt TEDS without inheriting another product's vocabulary
* Application-specific material still needs somewhere to live
* A rule that is only written down will be broken; it has to be checked

## Considered Options

* The normative files name no product or organisation, and a check enforces it
* Neutrality as a review guideline only
* Keep product names, and replace them at publication

## Decision Outcome

Chosen option: "The normative files name no product or organisation, and a check enforces it".

* The API specification, the API schemas, the core entity schemas and the role vocabulary name no product and no organisation.
  `tools/validate.py` fails if they do (the contact URL is the one exception, until the repository is published).
* TADS payload-schema families used by the core schemas are neutral (`media.*`).
* Application schemas, such as a viewer's per-user settings, are registered by the application ([ADR 0008](./0008-per-user-data-is-ordinary-entities.md)); `entity-schemas/examples/` shows the pattern with fictional names.
* The core schemas are `teds.channel.logging` and `teds.clip`; `teds.*` families are reserved for them.

### Consequences

* Good, because the repository can be published without rewriting its normative content
* Good, because the check found a product name in the specification's contact details the first time it ran
* Bad, because real-world examples have to be fictionalised

## Pros and Cons of the Options

### A review guideline only

* Good, because it costs nothing
* Bad, because names creep back in through examples and descriptions

### Replace names at publication

* Good, because early work is unconstrained
* Bad, because every example, family and identifier derived from a name would change, and deterministic ids with them
