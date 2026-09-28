# 0003: Registering channels automatically

## Abstract

A recorded channel should become a complete TEDS entity without anyone linking its parts by hand.
This note walks through how that happens for the core `teds.channel.logging` schema: which link rule finds each role, in what order the evidence arrives, and how a person corrects the result.
The rules themselves are recorded in [ADR 0005](../adr/0005-automatic-linking.md).

## Content

### Three layers

1. **Declared.**
   The system that sets up the recording creates the entity, and declares its main flow, through the API.
   It passes the entity id to the recorder.
2. **Stamped.**
   The recorder stamps what it writes with `teds.entity` and `teds.role` ([AppNote 0001](./0001-using-teds-with-tams-and-tads.md)).
   Every process downstream inherits the entity from its input.
3. **Inferred.**
   TEDS reads structure TAMS and TADS already hold (flow collections, derivation tags, timeline references) and applies each schema's link rules.
   This also covers objects nobody stamped: older recordings, and processes TEDS was never told about.

A label-similarity heuristic is a fourth, separate source: it only ever produces **suggestions**, which a person accepts or rejects.

### Worked example: a logging channel

1. A channel entity is created from `teds.channel.logging` with its name, provider, territory, expected subtitle languages (`en`, `cy`) and audio programmes (`main`, `ad`).
2. The recorder registers, in TAMS, a thumbnails flow, a thumbnail-index flow, and the transport stream flow whose `flow_collection` lists the other two with roles `thumbnails` and `thumbnail-index`.
   It stamps the transport stream `teds.entity=<id>`, `teds.role=av`.
   - `av` links by its `tags` rule (origin `stamped`), or by `declared` if the deploying system wrote it.
   - `thumbnails` and `thumbnail-index` link by `collectionOf: av` (origin `inferred`), with no tags needed.
3. A keyframe generator reads the transport stream and writes a keyframes flow.
   It copies `teds.entity`, and sets `teds.derived_from=<av flow>` and `teds.role=keyframes`.
   - `keyframes` links by `derivedFrom: av`.
4. A loudness extractor writes one TADS track per audio programme, with `timeline_reference.entity_id` set to the transport stream, and tags `teds.role=audio.loudness` and `teds.key.programme=main`.
   Its one-minute, one-hour and one-day summary tracks carry `teds.rollup_of` and `teds.tier`.
   - `audio.loudness` links by `timelineReferenceOf: av`, keyed `{programme: main}`, with its tiers attached.
5. `GET /entities/{id}/status` now reports the channel complete except for `audio.loudness` for `ad`, which nothing has produced yet.

### When a recorder restarts

If a recorder registers a new flow for the same channel, the new `av` link starts at the new flow's first segment, and the old one is closed at that moment.
Everything derived from the new flow links to it in turn.
`GET /entities/{id}/resolve?role=av&at=<t>` returns whichever flow served the channel at time `t`.

### Correcting the result

- A wrong inferred or stamped link is replaced by writing a **curated** link, which takes precedence (`curated > declared > stamped > inferred`).
- Removing a link that the evidence would recreate records it as **suppressed**, so it stays removed.
- Accepting a **suggestion** turns it into a curated link; rejecting it stops the same candidate being suggested again.

### What a server has to watch

To see evidence as it arrives, a server subscribes to TAMS and TADS webhooks and also reconciles periodically, since a webhook can be missed.
A server should be able to run the rules over existing objects on demand, and report what it *would* link before writing anything, so that a backfill of an existing system can be reviewed first.
