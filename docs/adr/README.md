# Decisions

This directory contains decision records for the TEDS API.
They describe the rationale behind decisions about the API, the other options that were considered, and the implications.
They exist to describe proposals, to support discussion and decision making, and to serve as a concise record of those discussions.
The full list is in [the documentation index](../README.md#adrs).

These records are based on the Markdown Any Decision Record template: see <https://github.com/adr/madr> for the original template, and <https://adr.github.io/> for more on ADRs in general.
The process follows the one [TADS uses](https://github.com/bbc/tads/blob/main/docs/adr/README.md).

ADRs are submitted as merge requests, which provide the tooling for review and approval.
Not every change to the API needs an ADR.
The test, on review of any merge request, is architectural significance.

## Creating a new ADR

0. Look at the existing ADRs, and see whether this has been considered before, or whether it would supersede one
1. Copy the [adr-template.md](../templates/adr-template.md) into this directory
2. Name it with the next number in sequence and a sensible title (e.g. `0011-support-entity-hierarchies.md`)
3. Fill in the template: at least the "Context", "Considered Options" and "Pros and Cons" sections.
   Feel free to choose a preferred option and add it to "Decision Outcome" as well.
4. If making the proposed changes (to the API, schemas or examples) helps to explain the proposal, make them as well
5. Add the ADR to the index in [docs/README.md](../README.md)
6. Open a merge request with the ADR and any other changes

## Reviewing the proposal

During review, use merge request comments to ask questions, make suggestions and discuss the proposal.
If a synchronous discussion takes place (e.g. a meeting), add a description of what was discussed and the outcome to the ADR itself.

## Finishing and merging

Once review has finished and a consensus has been reached:

1. Amend the ADR with relevant points from the review, and changes to the decision if necessary
2. Make these changes with new commits, so the original version stays visible in the history
3. If you added an implementation at the same time, make the required changes there too.
   Remember to bump the API version as described in [the README](../../README.md#api-versioning)
4. Amend the ADR status to "accepted" (the pipeline refuses a merge while any ADR is still "proposed")
5. Merge the merge request
